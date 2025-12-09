from typing import Any

from strands.experimental.hooks.multiagent import AfterNodeCallEvent, BeforeNodeCallEvent
from strands.hooks import HookProvider, HookRegistry


class GraphStateHook(HookProvider):

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:  # type: ignore
        registry.add_callback(BeforeNodeCallEvent, self.before_node_call)
        registry.add_callback(AfterNodeCallEvent, self.after_node_call)

    @staticmethod
    def before_node_call(event: BeforeNodeCallEvent):
        event.invocation_state.update({
            "source_graph": event.source
        })

    @staticmethod
    def after_node_call(event: AfterNodeCallEvent):
        event.invocation_state.pop("source_graph", None)
