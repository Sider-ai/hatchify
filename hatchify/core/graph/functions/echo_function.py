from pydantic import BaseModel
from strands import tool


class EchoResult(BaseModel):
    text: str


@tool(name="echo_function", description="Echo the input text")
async def echo_function(text: str) -> EchoResult:
    """简单的 echo function，用于测试"""
    return EchoResult(text=f"[ECHO] {text}")
