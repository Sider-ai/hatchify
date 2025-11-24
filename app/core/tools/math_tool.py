"""Math tools for arithmetic operations.

Demonstrates:
1. How to get tool's input schema as Pydantic Model for Agent structured_output
2. How to auto-generate output schema from tool's return transport
"""

from strands import ToolContext, tool
from strands.tools.decorator import DecoratedFunctionTool

from app.core.factory.tool_factory import ToolRouter

# math_router 只包含 @tool 装饰的函数
math_router = ToolRouter[DecoratedFunctionTool]()


@tool(name="add", description="Add two numbers", context=True)
async def add(a: float, b: float, tool_context: ToolContext) -> float:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number
        tool_context: Tool execution context

    Returns:
        Sum of a and b
    """
    return a + b


math_router.register(add)
