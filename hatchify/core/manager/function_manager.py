from strands.tools.decorator import DecoratedFunctionTool

from hatchify.core.factory.tool_factory import ToolRouter
from hatchify.core.graph.functions.echo_function import echo_function

# 限制 function_router 只接受 DecoratedFunctionTool
# 这确保只有 @tool 装饰的函数可以注册为 Function
# FunctionNodeWrapper 依赖 DecoratedFunctionTool 的特性（如 input_model）
function_router = ToolRouter[DecoratedFunctionTool]()

function_router.register(echo_function)
