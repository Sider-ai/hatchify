import abc
import asyncio
import time
from typing import Optional, Literal, AsyncIterator, Any

from loguru import logger

from app.common.event.base_event import StreamEvent, PingEvent, DoneEvent, ErrorEvent, StartEvent, CancelEvent
from app.core.manager.event_manager import EventStore


class BaseStreamHandler(metaclass=abc.ABCMeta):
    def __init__(
            self,
            source_id: str,
            ping_interval: int = 15,
            enable_reconnect: bool = True,
            event_ttl: int = 3600
    ):
        self.source_id: str = source_id
        self.ping_task: Optional[asyncio.Task] = None
        self.ping_interval = ping_interval
        self.ping_running = False
        self.enable_reconnect = enable_reconnect
        self.stream_task: Optional[asyncio.Task] = None
        self.stream_queue: asyncio.Queue[StreamEvent] = asyncio.Queue()
        self.event_ttl = event_ttl
        self.event_store: Optional[EventStore] = None
        self.stored_exception: Optional[Exception] = None

    async def ping_loop(self):
        try:
            while self.ping_running:
                await asyncio.sleep(self.ping_interval)
                if self.ping_running:
                    await self.stream_queue.put(
                        StreamEvent(
                            type="ping",
                            data=PingEvent(
                                timestamp=int(time.time())
                            )
                        )
                    )
        except asyncio.CancelledError:
            logger.debug(f"Ping task cancelled for graph: {self.source_id}")
        except Exception as e:
            logger.error(f"Ping task error: {type(e).__name__}: {e}")

    async def start_ping(self):
        if not self.ping_running:
            self.ping_running = True
            self.ping_task = asyncio.create_task(self.ping_loop())

    async def stop_ping(self):
        if not self.ping_running:
            return

        self.ping_running = False
        if self.ping_task:
            self.cancel_tasks(self.ping_task)
            await self.await_task_safely(self.ping_task)

    @staticmethod
    def cancel_tasks(asyncio_task: asyncio.Task) -> None:
        if not asyncio_task:
            return
        if asyncio_task is asyncio.current_task():
            return
        if not asyncio_task.done():
            asyncio_task.cancel()

    @staticmethod
    async def await_task_safely(asyncio_task: asyncio.Task) -> None:
        if not asyncio_task:
            return
        if asyncio_task is asyncio.current_task():
            return

        try:
            if not asyncio_task.done():
                await asyncio_task
            else:
                asyncio_task.result()
        except (asyncio.CancelledError, Exception) as e:
            logger.debug(f"{asyncio_task.get_name()} completed: {type(e).__name__}")

    @staticmethod
    def format_sse(event: StreamEvent) -> str:
        return "\n".join([
            f"id: {event.id}",
            f"event: {event.type}",
            f"data: {event.data.model_dump_json(exclude_none=True)}",
            "",
            ""
        ])

    async def stream_events(self):
        is_complete: bool = False
        try:
            while True:
                if is_complete and self.stream_queue.empty():
                    break

                try:
                    event = await self.stream_queue.get()
                except asyncio.CancelledError:
                    break

                yield event
                self.stream_queue.task_done()

                if isinstance(event.data, DoneEvent):
                    is_complete = True

        finally:
            if self.stored_exception:
                raise self.stored_exception

    async def worker(self, last_event_id: Optional[str] = None):
        try:
            if self.enable_reconnect:
                self.event_store = await EventStore.get_or_create(
                    self.source_id,
                    ttl_seconds=self.event_ttl
                )

                if last_event_id:
                    logger.info(f"Reconnect request with last_event_id: {last_event_id}")
                    historical_events = self.event_store.get_after(last_event_id)

                    for event in historical_events:
                        yield self.format_sse(event)

                    if self.event_store.is_completed():
                        return

            await self.start_ping()
            async for event in self.stream_events():
                if self.enable_reconnect and self.event_store:
                    self.event_store.append(event)

                yield self.format_sse(event)

        except asyncio.CancelledError as e:
            logger.debug(f"worker cancelled: {self.source_id}")
            raise e
        except Exception as e:
            logger.exception(f"{type(e).__name__}: {e}")
        finally:
            await self.stop_ping()

            if self.stream_task:
                self.cancel_tasks(self.stream_task)
                await self.await_task_safely(self.stream_task)

    async def send_terminal_events(
            self,
            terminal_type: Literal["error"],
            message: str,
            reason: Literal["error"]
    ):
        await self.stream_queue.put(
            StreamEvent(
                type="start",
                data=StartEvent(
                    task_id=self.source_id,
                ),
            )
        )

        if terminal_type == "error":  # error
            await self.stream_queue.put(
                StreamEvent(
                    type="error",
                    data=ErrorEvent(reason=message),
                )
            )
        else:
            raise TypeError(f"Unknown terminal type: {terminal_type}")

        # 在发送 DoneEvent 之前停止 ping
        await self.stop_ping()

        await self.stream_queue.put(
            StreamEvent(
                type="done",
                data=DoneEvent(
                    task_id=self.source_id,
                    reason=reason
                ),
            )
        )

    async def start_streaming(
            self,
            async_generator: AsyncIterator[Any],
    ):
        done_reason: Literal["completed", "cancel", "error"] = "completed"

        try:
            await self.stream_queue.put(
                StreamEvent(
                    type="start",
                    data=StartEvent(
                        task_id=self.source_id,
                    )
                )
            )
            async for event in async_generator:
                await self.handle_stream_event(event)
        except asyncio.CancelledError as e:
            # 客户端断开连接是正常行为，使用 info 级别
            msg = f"Stream cancelled (client disconnected or task stopped)"
            logger.info(f"{msg} - source: {self.source_id}")
            await self.stream_queue.put(
                StreamEvent(
                    type="cancel",
                    data=CancelEvent(
                        reason=msg
                    ),
                )
            )
            done_reason = "cancel"
            self.stored_exception = e
        except Exception as e:
            msg = f"{type(e).__name__}: {e}"
            logger.error(msg)
            await self.stream_queue.put(
                StreamEvent(
                    type="error",
                    data=ErrorEvent(
                        reason=msg
                    ),
                )
            )
            done_reason = "error"
            self.stored_exception = e
        finally:
            await self.stop_ping()

            await self.stream_queue.put(
                StreamEvent(
                    type="done",
                    data=DoneEvent(
                        task_id=self.source_id,
                        reason=done_reason
                    ),
                )
            )

    async def run_streamed(self, async_generator: AsyncIterator[Any], ):
        try:
            self.stream_task = asyncio.create_task(self.start_streaming(async_generator))
        except Exception as e:
            logger.error(f"Initialization failed: {type(e).__name__}: {e}")
            try:
                await self.send_terminal_events("error", f"{type(e).__name__}: {e}", "error")
            except Exception as inner_e:
                logger.error(f"Failed to send error events: {inner_e}")

    @abc.abstractmethod
    async def handle_stream_event(self, event: Any):
        ...
