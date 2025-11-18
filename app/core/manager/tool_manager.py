from app.core.factory.tool_factory import ToolRouter
from app.core.tools.math_tool import math_router

tool_factory = ToolRouter()
tool_factory.include_router(math_router)
