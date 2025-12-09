from typing import List

from fastapi import APIRouter

from hatchify.common.domain.responses.tool_response import ToolResponse
from hatchify.common.domain.result.result import Result
from hatchify.core.manager.tool_manager import tool_factory

tool_router = APIRouter(prefix="/tools")


@tool_router.get("/all")
async def all_tools() -> Result[List[ToolResponse]]:
    try:
        return Result.ok(
            data=[
                ToolResponse(
                    name=tool.tool_name,
                    description=tool.tool_spec.get("description", ""),
                    input_schema=tool.tool_spec.get("inputSchema", {}),
                    output_schema=tool.tool_spec.get("outputSchema", None),
                )
                for tool in tool_factory.get_all_tools().values()
            ]
        )
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        return Result.error(message=msg)
