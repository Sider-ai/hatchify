from typing import List

from fastapi import APIRouter

from hatchify.common.domain.responses.model_response import ModelResponse
from hatchify.common.domain.result.result import Result
from hatchify.core.manager.model_card_manager import model_card_manager

model_router = APIRouter(prefix="/models")


@model_router.get("/all")
async def all_tools() -> Result[List[ModelResponse]]:
    try:
        return Result.ok(
            data=[
                ModelResponse(id=model.id, name=model.name, description=model.description)
                for model in model_card_manager.get_all_models()
            ]
        )
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        return Result.error(message=msg)
