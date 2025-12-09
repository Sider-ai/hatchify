from typing import Any

from loguru import logger
from strands import Agent
from strands.types.content import Messages
import json
from hatchify.common.domain.event.base_event import StreamEvent
from hatchify.common.domain.event.edit_event import PhaseEvent
from hatchify.common.domain.requests.web_builder import WebBuilderConversationRequest
from hatchify.core.stream_handler.stream_handler import BaseStreamHandler


class WebBuilderGenerator(BaseStreamHandler):
    """
    Web Builder Generator - 处理 Web Builder 对话的流式生成器

    功能：
    - 管理与 Web Builder Agent 的对话
    - 处理流式事件
    - 利用 Strands SDK 的会话管理
    """

    def __init__(
            self,
            source_id: str,
            agent: Agent,
    ):
        super().__init__(source_id=source_id)
        self.agent = agent

    async def handle_stream_event(self, event: Any):
        try:
            if isinstance(event, dict):
                with open("web_builder_events.jsonl", "a", encoding="utf-8") as f:
                    f.write(json.dumps(event, ensure_ascii=False) + "\n")
            else:
                logger.warning(f"unhandled event type: {type(event).__name__}: {event}")
        except Exception as e:
            logger.exception(f"{type(e).__name__}: {e}")

    async def submit_task(
            self,
            request: WebBuilderConversationRequest,
    ):
        """
        提交任务并开始流式处理

        Args:
            request: Web Builder 对话请求
        """
        messages: Messages = request.messages
        async_generator=self.agent.stream_async(messages)
        await self.run_streamed(async_generator)