from copy import deepcopy
from typing import Dict, Self

from strands.tools.decorator import DecoratedFunctionTool


class ToolRouter:
    def __init__(self) -> None:
        self._tools: Dict[str, DecoratedFunctionTool] = {}

    def register(self, _tool: DecoratedFunctionTool) -> None:
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
                if not isinstance(item, DecoratedFunctionTool):
                    raise ValueError(
                        "Cannot prefix a 'factory' tool; please instantiate first."
                    )
                cloned: DecoratedFunctionTool = deepcopy(item)
                cloned._tool_name = new_name
                self._tools[new_name] = cloned

    def get_tool(self, name: str) -> DecoratedFunctionTool:
        return self._tools[name]

    def get_all_tools(
            self,
    ) -> Dict[str, DecoratedFunctionTool]:
        return dict(self._tools)
