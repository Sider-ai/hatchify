from typing import List

from fastapi import APIRouter, Depends, Path
from fastapi_pagination import Page
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from hatchify.business.db.session import get_db
from hatchify.business.manager.service_manager import ServiceManager
from hatchify.business.models.graph_version import GraphVersionTable
from hatchify.business.services.graph_version_service import GraphVersionService
from hatchify.business.utils.pagination_utils import CustomParams
from hatchify.common.domain.requests.graph_version import (
    PageGraphVersionRequest
)
from hatchify.common.domain.responses.graph_version_response import GraphVersionResponse
from hatchify.common.domain.responses.pagination import PaginationInfo
from hatchify.common.domain.result.result import Result

graph_versions_router = APIRouter(prefix="/graph-versions")


@graph_versions_router.get("/get_by_id/{id}", response_model=Result[GraphVersionResponse])
async def get_by_id(
        _id: int = Path(default=..., alias="id"),
        session: AsyncSession = Depends(get_db),
        service: GraphVersionService = Depends(ServiceManager.get_service_dependency(GraphVersionService)),
):
    try:
        obj_tb: GraphVersionTable = await service.get_by_id(session, _id)
        if not obj_tb:
            return Result.error(code=404, message="GraphVersion Not Found")
        response = GraphVersionResponse.model_validate(obj_tb)
        return Result.ok(data=response)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.error(code=500, message=msg)


@graph_versions_router.get("/page", response_model=Result[PaginationInfo[List[GraphVersionResponse]]])
async def page(
        list_request: PageGraphVersionRequest = Depends(),
        session: AsyncSession = Depends(get_db),
        service: GraphVersionService = Depends(ServiceManager.get_service_dependency(GraphVersionService)),
):
    try:
        params = CustomParams(page=list_request.page, size=list_request.size)

        # 构建过滤条件
        filters = {}
        if list_request.graph_id:
            filters["graph_id"] = list_request.graph_id

        pages: Page[GraphVersionTable] = await service.get_paginated_list(
            session, params, sort=list_request.sort, **filters
        )
        data = [GraphVersionResponse.model_validate(item) for item in pages.items]
        page_info = PaginationInfo.from_fastapi_page(data=data, page_result=pages)
        return Result.ok(data=page_info)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.error(code=500, message=msg)


@graph_versions_router.delete("/delete_by_id/{id}", response_model=Result[bool])
async def delete_by_id(
        _id: int = Path(default=..., alias="id"),
        session: AsyncSession = Depends(get_db),
        service: GraphVersionService = Depends(ServiceManager.get_service_dependency(GraphVersionService)),
):
    try:
        is_deleted: bool = await service.delete_by_id(session, _id)
        if not is_deleted:
            return Result.error(code=500, message="Delete GraphVersion Failed")
        return Result.ok(data=is_deleted)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.error(code=500, message=msg)
