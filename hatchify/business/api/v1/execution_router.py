from typing import List

from fastapi import APIRouter, Depends, Path
from fastapi_pagination import Page
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from hatchify.business.db.session import get_db
from hatchify.business.manager.service_manager import ServiceManager
from hatchify.business.models.execution import ExecutionTable
from hatchify.business.services.execution_service import ExecutionService
from hatchify.business.utils.pagination_utils import CustomParams
from hatchify.common.domain.requests.execution import PageExecutionRequest
from hatchify.common.domain.responses.execution_response import ExecutionResponse
from hatchify.common.domain.responses.pagination import PaginationInfo
from hatchify.common.domain.result.result import Result

executions_router = APIRouter(prefix="/executions")


@executions_router.get("/get_by_id/{id}", response_model=Result[ExecutionResponse])
async def get_by_id(
        _id: str = Path(default=..., alias="id"),
        session: AsyncSession = Depends(get_db),
        service: ExecutionService = Depends(ServiceManager.get_service_dependency(ExecutionService)),
):
    """根据 ID 查询执行记录"""
    try:
        execution: ExecutionTable = await service.get_by_id(session, _id)
        if not execution:
            return Result.error(code=404, message="Execution Not Found")
        response = ExecutionResponse.model_validate(execution)
        return Result.ok(data=response)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.error(code=500, message=msg)


@executions_router.get("/page", response_model=Result[PaginationInfo[List[ExecutionResponse]]])
async def page(
        list_request: PageExecutionRequest = Depends(),
        session: AsyncSession = Depends(get_db),
        service: ExecutionService = Depends(ServiceManager.get_service_dependency(ExecutionService)),
):
    """分页查询执行记录"""
    try:
        params = CustomParams(page=list_request.page, size=list_request.size)

        pages: Page[ExecutionTable] = await service.get_paginated_list(
            session,
            params,
            sort=list_request.sort
        )
        data = [ExecutionResponse.model_validate(item) for item in pages.items]
        page_info = PaginationInfo.from_fastapi_page(data=data, page_result=pages)
        return Result.ok(data=page_info)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.error(code=500, message=msg)