from pydantic import BaseModel, Field


class FunctionNode(BaseModel):
    """Graph 中的 Function 节点定义（确定性函数节点）

    Function 对应 Strands 的 FunctionNodeWrapper，执行确定性的 Python 函数。
    与 YAgents 不同，Hatchify 的 FunctionNodeWrapper 会自动处理输入映射，
    因此不需要 input_mapping 字段。
    """
    name: str = Field(
        ...,
        description="节点唯一名称（在 Graph 中的 ID，可以自定义）"
    )
    function_ref: str = Field(
        ...,
        description="Function 类型（从 function_manager 查找对应的 @tool 函数名）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "echo_step_1",
                "function_ref": "echo"
            }
        }