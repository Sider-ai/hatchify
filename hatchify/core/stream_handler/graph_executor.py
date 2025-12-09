import json
import mimetypes
from typing import Dict, Any, List, get_args, Optional, Union

from strands.agent import AgentResult
from strands.multiagent.base import NodeResult, MultiAgentResult
from strands.types.content import ContentBlock
from strands.types.media import DocumentFormat, ImageFormat, VideoFormat, DocumentContent, DocumentSource, ImageContent, \
    ImageSource, VideoContent, VideoSource

from hatchify.common.domain.entity.graph_execute_data import GraphExecuteData
from hatchify.common.domain.entity.graph_spec import GraphSpec
from hatchify.common.domain.event.base_event import StreamEvent
from hatchify.common.domain.event.execute_event import NodeStartEvent, NodeStopEvent, NodeHandoffEvent, ResultEvent
from hatchify.common.extensions.ext_storage import storage_client
from hatchify.core.graph.graph_wrapper import GraphWrapper
from hatchify.core.stream_handler.stream_handler import BaseStreamHandler

document_formats = get_args(DocumentFormat)
image_formats = get_args(ImageFormat)
video_formats = get_args(VideoFormat)


class GraphExecutor(BaseStreamHandler):

    def __init__(
            self,
            graph_id: str,
            graph: GraphWrapper,
            graph_spec: GraphSpec,
    ):
        super().__init__(
            source_id=graph_id,
        )
        self.graph = graph
        self.graph_spec = graph_spec

    @staticmethod
    async def build_messages(
            task: GraphExecuteData,
    ) -> List[ContentBlock]:
        messages: List[ContentBlock] = []
        for field, sub_files in task.files.items():
            for index, sub_file in enumerate(sub_files):

                ext_with_dot: Optional[str] = mimetypes.guess_extension(sub_file.mime)
                if ext_with_dot is None:
                    raise RuntimeError(f"Unsupported file format: {sub_file.name}")
                ext = ext_with_dot.split(".")[-1]
                bytes_data: bytes = await storage_client.load(sub_file.key)

                if ext in document_formats:
                    messages.append(
                        ContentBlock(
                            text=f"User’s Document data. {sub_file.name}",
                            document=DocumentContent(
                                format=ext,  # type: ignore
                                name=sub_file.name,
                                source=DocumentSource(bytes=bytes_data)

                            ),
                            source_key=sub_file.key  # type: ignore 自定义额外字段，用于配合重写后的 FileSessionManager
                        )
                    )
                elif ext in image_formats:
                    messages.append(
                        ContentBlock(
                            text=f"User’s Image data. {sub_file.name}",
                            image=ImageContent(
                                format=ext,  # type: ignore
                                source=ImageSource(bytes=bytes_data)
                            ),
                            source_key=sub_file.key  # type: ignore 自定义额外字段，用于配合重写后的 FileSessionManager
                        )
                    )
                elif ext in video_formats:
                    messages.append(
                        ContentBlock(
                            text=f"User’s video data. {sub_file.name}",
                            video=VideoContent(
                                format=ext,  # type: ignore
                                source=VideoSource(bytes=bytes_data)
                            ),
                            source_key=sub_file.key  # type: ignore 自定义额外字段，用于配合重写后的 FileSessionManager
                        )
                    )
                else:
                    raise TypeError(f"Unsupported file format: {ext}")
        if task.jsons:
            messages.append(
                ContentBlock(text=f"User’s input: {json.dumps(task.jsons, indent=2, ensure_ascii=False)})")
            )
        return messages

    async def handle_stream_event(self, event: Dict[str, Any]):
        event_type = event.get("type")
        if event_type in ["multiagent_node_stream"]:
            return
        match event_type:
            case "multiagent_node_start":
                await self.emit_event(
                    StreamEvent(
                        type="node_start",
                        data=NodeStartEvent(
                            node_id=event.get("node_id"),
                        )
                    )
                )
            case "multiagent_node_stop":
                node_result: NodeResult = event.get("node_result")
                result = node_result.result
                if isinstance(result, AgentResult):
                    await self.emit_event(
                        StreamEvent(
                            type="node_stop",
                            data=NodeStopEvent(
                                node_id=event.get("node_id"),
                                status=node_result.status,
                                result=result.structured_output.model_dump() or str(result)
                            )
                        )
                    )
            case "multiagent_handoff":
                await self.emit_event(
                    StreamEvent(
                        type="node_handoff",
                        data=NodeHandoffEvent(
                            to_node_ids=event.get("to_node_ids", []),
                            from_node_ids=event.get("from_node_ids", []),
                        )
                    )
                )
            case "multiagent_result":
                result_dict: Dict[str, Union[str, Dict[str, Any]]] = {}
                output_required = self.graph_spec.output_schema.get("required")
                multi_agent_result: MultiAgentResult = event.get("result")
                for node_id, node_result in multi_agent_result.results.items():
                    if node_id not in output_required:
                        continue
                    result = node_result.result
                    if isinstance(result, AgentResult):
                        result_dict[node_id] = result.structured_output.model_dump() or str(result)
                await self.emit_event(
                    StreamEvent(
                        type="result",
                        data=ResultEvent(
                            data={
                                "status": multi_agent_result.status,
                                "results": result_dict
                            },
                        )
                    )
                )
            case _:
                raise TypeError(f"Unsupported event type: {event_type}")

    async def submit_task(
            self,
            task: GraphExecuteData,
            invocation_state: Dict[str, Any] | None = None,
            **kwargs: Any
    ):
        messages = await self.build_messages(task)
        async_generator = self.graph.stream_async(messages, invocation_state, **kwargs)
        await self.run_streamed(async_generator)

    async def invoke_async(
            self,
            task: GraphExecuteData,
            invocation_state: Dict[str, Any] | None = None,
            **kwargs: Any
    ):
        messages = await self.build_messages(task)

        result = await self.graph.invoke_async(messages, invocation_state, **kwargs)
        return result
