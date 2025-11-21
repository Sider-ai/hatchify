from copy import deepcopy
from typing import Dict, Self, Union

from strands.types.tools import AgentTool


class ToolRouter:
    def __init__(self) -> None:
        self._tools: Dict[str, Union[AgentTool]] = {}

    def register(self, _tool: AgentTool) -> None:
        self._tools[_tool.tool_name] = _tool

    def include_router(
            self,
            router: Self,
            *,
            prefix: str | None = None,
            overwrite: bool = False,
    ) -> None:
        if not isinstance(router, ToolRouter):
            raise TypeError("include_router() expects a ToolRouter instance.")

        for name, item in router.get_all_tools().items():
            new_name = f"{prefix}/{name}" if prefix else name

            if not overwrite and new_name in self._tools:
                raise ValueError(f"Tool '{new_name}' already exists in ToolRouter.")

            if new_name == name:
                self._tools[new_name] = item
            else:
                if not isinstance(item, AgentTool):
                    raise ValueError(
                        "Cannot prefix a 'factory' tool; please instantiate first."
                    )
                cloned: AgentTool = deepcopy(item)
                cloned._tool_name = new_name
                self._tools[new_name] = cloned

    def get_tool(self, name: str) -> AgentTool:
        return self._tools[name]

    def get_all_tools(
            self,
    ) -> Dict[str, AgentTool]:
        return dict(self._tools)
