import asyncio
import inspect
import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, cast, Optional

from opentelemetry import trace as trace_api
from pydantic import BaseModel
from strands._async import run_async
from strands.agent import AgentResult
from strands.experimental.hooks.multiagent import MultiAgentInitializedEvent, AfterMultiAgentInvocationEvent, \
    BeforeMultiAgentInvocationEvent, BeforeNodeCallEvent, AfterNodeCallEvent
from strands.hooks import HookProvider, HookRegistry
from strands.multiagent.base import MultiAgentBase, MultiAgentResult, Status, NodeResult
from strands.multiagent.graph import Graph
from strands.telemetry import get_tracer, EventLoopMetrics
from strands.tools.decorator import DecoratedFunctionTool
from strands.types._events import MultiAgentResultEvent, MultiAgentNodeStartEvent, MultiAgentNodeStopEvent
from strands.types.content import ContentBlock, Message
from strands.types.event_loop import Usage, Metrics
from strands.types.tools import ToolUse, ToolResult, ToolResultContent

logger = logging.getLogger(__name__)
_DEFAULT_FUNCTION_ID = "default_function"


@dataclass
class FunctionResult(MultiAgentResult):
    ...


@dataclass
class FunctionState:
    task: str | list[ContentBlock] = ""
    status: Status = Status.PENDING
    start_time: float = field(default_factory=time.time)
    result: Optional[NodeResult] = field(default=None)


class FunctionNodeWrapper(MultiAgentBase):
    """Execute deterministic Python functions as graph nodes.

    This node wraps a DecoratedFunctionTool and executes it as part of a multi-agent graph.
    It handles both streaming and non-streaming execution.

    Can get structured outputs from dependency nodes via graph edges to build tool inputs.
    """

    def __init__(
            self,
            tool: DecoratedFunctionTool,
            hooks: Optional[list[HookProvider]] = None,
            _id: str = _DEFAULT_FUNCTION_ID
    ) -> None:
        super().__init__()
        self.id = _id
        self.tool = tool
        self.name = tool.tool_name
        self.state = FunctionState()
        self.tracer = get_tracer()
        self.hooks = HookRegistry()
        if hooks:
            for hook in hooks:
                self.hooks.add_hook(hook)
        self._resume_from_session = False

        # Validate tool return transport - MUST be BaseModel for transport-safe output
        self._validate_tool_return_type()

        run_async(lambda: self.hooks.invoke_callbacks_async(MultiAgentInitializedEvent(self)))

    def _validate_tool_return_type(self) -> None:
        """Validate that tool returns a BaseModel for transport-safe structured output.

        Raises:
            ValueError: If tool return transport is not a BaseModel subclass
        """
        return_type = self.tool._metadata.type_hints.get('return')

        if not return_type or return_type is type(None):
            raise ValueError(
                f"Tool '{self.tool.tool_name}' has no return transport annotation. "
                f"FunctionNodeWrapper requires tools to have a BaseModel return transport for transport-safe output. "
                f"Example: async def {self.tool.tool_name}(...) -> YourOutputModel:"
            )

        # Check if return transport is BaseModel
        if not (isinstance(return_type, type) and issubclass(return_type, BaseModel)):
            raise ValueError(
                f"Tool '{self.tool.tool_name}' return transport must be a Pydantic BaseModel, "
                f"but got '{return_type.__name__}'. "
                f"This ensures transport-safe structured output for downstream agents. "
                f"Define an output model: class {self.tool.tool_name.capitalize()}Output(BaseModel): ..."
            )

    async def invoke_async(
            self, task: str | list[ContentBlock], invocation_state: dict[str, Any] | None = None, **kwargs: Any
    ) -> MultiAgentResult:
        """Execute the tool and return the final result.

        Args:
            task: The input task (string or content blocks)
            invocation_state: Optional state dictionary passed between nodes
            **kwargs: Additional keyword arguments (should include 'tool_input')

        Returns:
            MultiAgentResult containing the function execution result
        """
        events = self.stream_async(task, invocation_state, **kwargs)
        final_event = None
        async for event in events:
            final_event = event

        if final_event is None or "result" not in final_event:
            raise ValueError("Graph streaming completed without producing a result event")

        return cast(MultiAgentResult, final_event["result"])

    async def stream_async(
            self, task: str | list[ContentBlock], invocation_state: dict[str, Any] | None = None, **kwargs: Any
    ) -> AsyncIterator[dict[str, Any]]:

        if invocation_state is None:
            invocation_state = {}

        await self.hooks.invoke_callbacks_async(BeforeMultiAgentInvocationEvent(self, invocation_state))

        start_time = time.time()
        if not self._resume_from_session:
            # Initialize state
            self.state = FunctionState(
                status=Status.EXECUTING,
                task=task,
                start_time=start_time,
            )
        else:
            self.state.status = Status.EXECUTING
            self.state.start_time = start_time

        span = self.tracer.start_multiagent_span(task, "function")
        with trace_api.use_span(span, end_on_exit=True):
            try:

                async for event in self._execute_function(invocation_state):
                    yield event.as_dict()

                self.state.status = Status.COMPLETED

                result = self._build_result()

                yield MultiAgentResultEvent(result=result).as_dict()

            except Exception:
                logger.exception("function execution failed")
                self.state.status = Status.FAILED
                raise
            finally:
                self.state.execution_time = round((time.time() - start_time) * 1000)
                await self.hooks.invoke_callbacks_async(AfterMultiAgentInvocationEvent(self))
                self._resume_from_session = False

    def _build_node_input(self, invocation_state: dict[str, Any]) -> dict[str, Any]:
        """Build tool input from dependency node's structured output.

        Gets the structured output from the single dependency node and converts it
        to the tool's expected input format.

        Args:
            invocation_state: State dict containing source_graph

        Returns:
            Dict with tool input parameters extracted from dependency's structured output

        Example:
            Dependency outputs: {"text": "hello"}
            Tool expects: def echo(text: str)
            Returns: {"text": "hello"}
        """
        graph: Optional[Graph] = invocation_state.get('source_graph')

        # Get structured output from dependency node
        if graph is None:
            raise ValueError("FunctionNodeWrapper must run in a Graph, but source_graph not found")

        # Find current node
        current_node = None
        for node_id, node in graph.nodes.items():
            if node.executor == self:
                current_node = node
                break

        if not current_node:
            raise ValueError(f"Cannot find FunctionNodeWrapper in Graph (id={self.id})")

        # Find incoming edges (dependency nodes)
        incoming_edges = [edge for edge in graph.edges if edge.to_node == current_node]

        # Validate single dependency
        if len(incoming_edges) == 0:
            raise ValueError(
                f"FunctionNodeWrapper '{self.id}' has no dependency nodes. "
                f"FunctionNodeWrapper must have exactly one input node."
            )

        if len(incoming_edges) > 1:
            dependency_ids = [edge.from_node.node_id for edge in incoming_edges]
            raise ValueError(
                f"FunctionNodeWrapper '{self.id}' has multiple dependencies: {dependency_ids}. "
                f"FunctionNodeWrapper can only accept one input. Ensure only one node connects to this FunctionNodeWrapper."
            )

        # Get the single dependency node
        edge = incoming_edges[0]
        from_node = edge.from_node
        from_node_id = from_node.node_id

        # Get dependency node result from GraphState
        if from_node_id not in graph.state.results:
            raise ValueError(
                f"Dependency node '{from_node_id}' has not executed yet or produced no result. "
                f"FunctionNodeWrapper can only run after its dependency completes."
            )

        node_result = graph.state.results[from_node_id]

        # Validate result transport
        if not isinstance(node_result.result, AgentResult):
            raise ValueError(
                f"Dependency node '{from_node_id}' must be an Agent node, "
                f"but result transport is '{type(node_result.result).__name__}'. "
                f"FunctionNodeWrapper can only receive Agent structured outputs."
            )
        if not node_result.result.structured_output:
            raise ValueError(
                f"Dependency node '{from_node_id}' has no structured output. "
                f"Ensure the Agent is configured with 'structured_output_model' parameter."
            )
        return node_result.result.structured_output.model_dump()

    async def _execute_function(self, invocation_state: dict[str, Any]) -> AsyncIterator[Any]:
        await self.hooks.invoke_callbacks_async(BeforeNodeCallEvent(self, self.id, invocation_state))

        start_event = MultiAgentNodeStartEvent(
            node_id=self.id, node_type="multiagent"
        )
        yield start_event

        start_time = time.time()
        try:
            tool_input = self._build_node_input(invocation_state)
            tool_use_id = f"tooluse_{self.tool.tool_name}_{random.randint(100000000, 999999999)}"
            tool_use = ToolUse(
                input=tool_input,
                toolUseId=tool_use_id,
                name=self.tool.tool_name
            )

            validated_input = self.tool._metadata.validate_input(tool_input)
            self.tool._metadata.inject_special_parameters(validated_input, tool_use, invocation_state)

            if inspect.iscoroutinefunction(self.tool._tool_func):
                result = await self.tool._tool_func(**validated_input)  # transport: ignore
            else:
                result = await asyncio.to_thread(self.tool._tool_func, **validated_input)  # transport: ignore

            execution_time = round((time.time() - start_time) * 1000)
            node_result = NodeResult(
                result=AgentResult(
                    stop_reason="tool_use",
                    message=Message(
                        role="assistant",
                        content=[
                            ContentBlock(text=result.model_dump_json(), toolUse=tool_use, toolResult=ToolResult(
                                content=[
                                    ToolResultContent(json=result.model_dump_json())
                                ],
                                status="success",
                                toolUseId=tool_use_id,
                            ))
                        ]
                    ),
                    metrics=EventLoopMetrics(),
                    state=Status.COMPLETED.value,
                    structured_output=result
                ),
                execution_time=execution_time,
                status=Status.COMPLETED,
                accumulated_usage=Usage(inputTokens=0, outputTokens=0, totalTokens=0),
                accumulated_metrics=Metrics(latencyMs=execution_time),
                execution_count=1,
            )
            self.state.result = node_result

            complete_event = MultiAgentNodeStopEvent(
                node_id=self.id,
                node_result=node_result,
            )
            yield complete_event

        except Exception as e:

            execution_time = round((time.time() - start_time) * 1000)

            node_result = NodeResult(
                result=e,
                execution_time=execution_time,
                status=Status.FAILED,
                accumulated_usage=Usage(inputTokens=0, outputTokens=0, totalTokens=0),
                accumulated_metrics=Metrics(latencyMs=execution_time),
                execution_count=1,
            )
            self.state.result = node_result

            raise
        finally:
            await self.hooks.invoke_callbacks_async(AfterNodeCallEvent(self, self.id, invocation_state))

    def _build_result(self) -> FunctionResult:
        return FunctionResult(
            results={
                self.id: self.state.result
            },
            status=self.state.status
        )
