from pydantic import BaseModel, Field


class FunctionNode(BaseModel):
    name: str = Field(
        ...,
        description="节点唯一名称（在 Graph 中的 ID，可以自定义）"
    )
    function_ref: str = Field(
        ...,
        description="Function 类型（从 function_manager 查找对应的 @tool 函数名）"
    )
