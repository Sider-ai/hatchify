from pydantic import BaseModel, Field


class ProcessorNode(BaseModel):
    """Graph 中的 Processor 节点定义（确定性函数节点）

    Processor 对应 Strands 的 FunctionNode，执行确定性的 Python 函数。
    与 YAgents 不同，Hatchify 的 FunctionNode 会自动处理输入映射，
    因此不需要 input_mapping 字段。
    """
    name: str = Field(
        ...,
        description="节点唯一名称（在 Graph 中的 ID，可以自定义）"
    )
    processor_ref: str = Field(
        ...,
        description="Processor 类型（从 processor_manager 查找对应的 @tool 函数名）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "echo_step_1",
                "processor_ref": "echo"
            }
        }