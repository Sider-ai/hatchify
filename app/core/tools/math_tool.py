from strands import ToolContext, tool

from app.core.factory.tool_factory import ToolRouter

math_router = ToolRouter()


@tool(name="add", description="Add two numbers", context=True)
async def add(a: float, b: float, tool_context: ToolContext) -> float:
    return a + b


math_router.register(add)
