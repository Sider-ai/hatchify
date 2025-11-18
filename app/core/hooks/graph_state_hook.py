from typing import Any

from strands.experimental.hooks.multiagent import BeforeMultiAgentInvocationEvent, \
    AfterNodeCallEvent, BeforeNodeCallEvent
from strands.hooks import HookProvider, HookRegistry


class GraphStateHook(HookProvider):

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        registry.add_callback(BeforeNodeCallEvent, self.before_node_call)
        registry.add_callback(AfterNodeCallEvent, self.after_node_call)

    @staticmethod
    def before_node_call(event: BeforeNodeCallEvent):
        print(f"before before {event.invocation_state}")
        event.invocation_state.update({
            "source_graph": event.source
        })
        print(f"after before {event.invocation_state}")

    @staticmethod
    def after_node_call(event: AfterNodeCallEvent):
        print(f"before after {event.invocation_state}")
        event.invocation_state.pop("source_graph", None)
        print(f"after after {event.invocation_state}")
