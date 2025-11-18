from typing import Any, AsyncIterator, cast

from strands.multiagent.base import MultiAgentBase, MultiAgentResult, Status
from strands.multiagent.graph import Graph
from strands.tools.decorator import DecoratedFunctionTool
from strands.types.content import ContentBlock
from strands.types.event_loop import Usage, Metrics


class FunctionNode(MultiAgentBase):
    """Execute deterministic Python functions as graph nodes.

    This node wraps a DecoratedFunctionTool and executes it as part of a multi-agent graph.
    It handles both streaming and non-streaming execution.
    """

    def __init__(self, tool: DecoratedFunctionTool, name: str | None = None):
        """Initialize the function node.

        Args:
            tool: A DecoratedFunctionTool instance from strands
            name: Optional custom name for the node (defaults to tool's name)
        """
        super().__init__()
        self.tool = tool
        self.name = name or tool.tool_name

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
        graph: Graph = invocation_state.get('source_graph')
        print(graph.state.results)
        yield {
            "result": MultiAgentResult(
                status=Status.COMPLETED,
                results={},
                accumulated_usage=Usage(inputTokens=0, outputTokens=0, totalTokens=0),
                accumulated_metrics=Metrics(latencyMs=0),
                execution_count=1,
                execution_time=0,
            )
        }
