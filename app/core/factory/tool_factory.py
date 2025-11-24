from copy import deepcopy

from strands.tools.decorator import DecoratedFunctionTool
from strands.types.tools import AgentTool


class ToolRouter[T: AgentTool = AgentTool]:
    """泛型工具路由器，可以限制接受的工具类型

    默认接受所有 AgentTool 类型，也可以限制为特定子类（如 DecoratedFunctionTool）。

    Examples:
        ```python
        # 默认行为：接受所有 AgentTool（向后兼容）
        tool_router = ToolRouter()

        # 限制为 DecoratedFunctionTool（用于 FunctionNodeWrapper）
        from strands.tools.decorator import DecoratedFunctionTool
        function_router = ToolRouter[DecoratedFunctionTool]()
        ```
    """

    def __init__(self) -> None:
        self._tools: dict[str, T] = {}

    def register(self, _tool: T) -> None:
        """注册工具

        Args:
            _tool: 工具实例，类型由泛型参数 T 限制
        """
        self._tools[_tool.tool_name] = _tool  # type: ignore

    def include_router(
            self,
            router: "ToolRouter[T]",
            *,
            prefix: str | None = None,
            overwrite: bool = False,
    ) -> None:
        """包含另一个相同类型的路由器

        Args:
            router: 另一个 ToolRouter 实例，必须是相同的泛型类型
            prefix: 可选的工具名称前缀
            overwrite: 是否覆盖已存在的工具
        """
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
                cloned: T = deepcopy(item)
                cloned._tool_name = new_name
                self._tools[new_name] = cloned

    def get_tool(self, name: str) -> T:
        """获取工具

        Args:
            name: 工具名称

        Returns:
            工具实例，类型由泛型参数 T 决定
        """
        return self._tools[name]

    def get_all_tools(self) -> dict[str, T]:
        """获取所有工具

        Returns:
            工具字典，值类型由泛型参数 T 决定
        """
        return dict(self._tools)

    def get_descriptions(self) -> dict[str, str]:
        """获取所有工具/函数的名称和描述（用于 LLM 提示词）

        Returns:
            名称 -> 描述的字典
        """
        descriptions = {}
        for name, tool in self._tools.items():
            desc = tool.tool_spec.get('description', 'No description available')
            descriptions[name] = desc
        return descriptions

    def format_for_prompt(self) -> str:
        """格式化为 LLM 提示词

        Returns:
            格式化的列表字符串，格式：
            - name: description
            - another: another description
        """
        descriptions = self.get_descriptions()
        if not descriptions:
            return "None available"

        lines = [f"- {name}: {desc}" for name, desc in descriptions.items()]
        return "\n".join(lines)

    @staticmethod
    def _get_function_output_model(tool: DecoratedFunctionTool):
        """从 DecoratedFunctionTool 获取 output model

        Args:
            tool: DecoratedFunctionTool 实例

        Returns:
            返回类型的 BaseModel 类，如果没有则返回 None
        """
        if not isinstance(tool, DecoratedFunctionTool):
            raise TypeError("tool expects a DecoratedFunctionTool instance.")
        return tool._metadata.type_hints.get('return')

    def format_functions_for_prompt(self) -> str:
        """格式化 DecoratedFunctionTool 为 LLM 提示词（包含 input/output schema）

        仅适用于 function_router，会包含每个 function 的输入输出 schema，
        以便 LLM 设计 Agent 时能匹配 Function 的接口。

        Returns:
            格式化的字符串，包含 function 名称、描述和 schema
        """

        if not self._tools:
            return "None available"

        lines = []
        for name, tool in self._tools.items():
            if not isinstance(tool, DecoratedFunctionTool):
                continue

            desc = tool.tool_spec.get('description', 'No description available')
            line = f"- {name}: {desc}"

            # Input schema
            input_schema = tool._metadata.input_model.model_json_schema()
            line += f"\n  Input Schema: {input_schema}"

            # Output schema
            output_model = self._get_function_output_model(tool)
            if output_model:
                output_schema = output_model.model_json_schema()
                line += f"\n  Output Schema: {output_schema}"

            lines.append(line)

        return "\n".join(lines) if lines else "None available"
