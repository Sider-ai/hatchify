from strands.tools.decorator import DecoratedFunctionTool

from app.core.factory.tool_factory import ToolRouter
from app.core.functions.echo_function import echo_function

# 限制 function_router 只接受 DecoratedFunctionTool
# 这确保只有 @tool 装饰的函数可以注册为 Function
# FunctionNodeWrapper 依赖 DecoratedFunctionTool 的特性（如 input_model）
function_router = ToolRouter[DecoratedFunctionTool]()

function_router.register(echo_function)
