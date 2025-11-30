from typing import List, cast

from fastapi import APIRouter, Depends, Path
from fastapi_pagination import Page
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.business.db.session import get_db
from app.business.manager.service_manager import ServiceManager
from app.business.models.messages import MessageTable
from app.business.services.message_service import MessageService
from app.business.utils.pagination_utils import CustomParams
from app.common.domain.requests.message import (
    PageMessageRequest,
)
from app.common.domain.responses.message_response import MessageResponse
from app.common.domain.responses.pagination import PaginationInfo
from app.common.domain.result.result import Result

messages_router = APIRouter(prefix="/messages")


@messages_router.get("/get_by_id/{id}", response_model=Result[MessageResponse])
async def get_by_id(
        _id: str = Path(default=..., alias="id"),
        session: AsyncSession = Depends(get_db),
        service: MessageService = Depends(ServiceManager.get_service_dependency(MessageService)),
):
    try:
        obj_tb: MessageTable = await service.get_by_id(session, _id)
        if not obj_tb:
            return Result.failed(
                code=404,
                message="Message Not Found",
            )
        response = MessageResponse.model_validate(obj_tb)
        return Result.ok(data=response)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.failed(code=500, message=msg)


@messages_router.get("/history/{session_id}", response_model=Result[List[MessageResponse]])
async def history(
        session_id: str = Path(default=..., description="会话 ID"),
        session: AsyncSession = Depends(get_db),
        service: MessageService = Depends(ServiceManager.get_service_dependency(MessageService)),
):
    try:
        history_list: List[MessageTable] = cast(List[MessageTable], await service.get_list(
            session,
            sort="created_at:asc",
            session_id=session_id,
        ))
        data = [MessageResponse.model_validate(item) for item in history_list]
        return Result.ok(data=data)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.failed(code=500, message=msg)


@messages_router.get("/page", response_model=Result[PaginationInfo[List[MessageResponse]]])
async def page(
        list_request: PageMessageRequest = Depends(),
        session: AsyncSession = Depends(get_db),
        service: MessageService = Depends(ServiceManager.get_service_dependency(MessageService)),
):
    try:
        params = CustomParams(page=list_request.page, size=list_request.size)

        # 构建过滤条件
        filters = {}
        if list_request.session_id:
            filters["session_id"] = list_request.session_id
        if list_request.role:
            filters["role"] = list_request.role

        pages: Page[MessageTable] = await service.get_paginated_list(
            session, params, sort=list_request.sort, **filters
        )
        data = [MessageResponse.model_validate(item) for item in pages.items]
        page_info = PaginationInfo.from_fastapi_page(data=data, page_result=pages)
        return Result.ok(data=page_info)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.failed(code=500, message=msg)
