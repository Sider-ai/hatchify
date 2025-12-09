import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Header, Query
from fastapi_pagination import Page
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from hatchify.business.db.session import get_db
from hatchify.business.manager.service_manager import ServiceManager
from hatchify.business.models.graph import GraphTable
from hatchify.business.services.graph_service import GraphService
from hatchify.business.services.session_service import SessionService
from hatchify.business.utils.pagination_utils import CustomParams
from hatchify.business.utils.sse_helper import create_sse_response
from hatchify.common.domain.requests.graph import (
    PageGraphRequest,
    UpdateGraphRequest,
    GraphConversationRequest,
)
from hatchify.common.domain.responses.graph_response import GraphResponse
from hatchify.common.domain.responses.graph_rollback_response import GraphRollbackResponse
from hatchify.common.domain.responses.graph_version_response import GraphVersionResponse
from hatchify.common.domain.responses.pagination import PaginationInfo
from hatchify.common.domain.responses.web_hook import ExecutionResponse
from hatchify.common.domain.result.result import Result
from hatchify.core.manager.function_manager import function_router
from hatchify.core.manager.model_card_manager import model_card_manager
from hatchify.core.manager.stream_manager import StreamManager
from hatchify.core.manager.tool_manager import tool_factory
from hatchify.core.stream_handler.graph_spec_generator import GraphSpecGenerator

graphs_router = APIRouter(prefix="/graphs")


@graphs_router.get("/get_by_id/{id}", response_model=Result[GraphResponse])
async def get_by_id(
        _id: str = Path(default=..., alias="id"),
        session: AsyncSession = Depends(get_db),
        service: GraphService = Depends(ServiceManager.get_service_dependency(GraphService)),
):
    try:
        obj_tb: GraphTable = await service.get_by_id(session, _id)
        if not obj_tb:
            return Result.error(code=404, message="Source Not Found")
        response = GraphResponse.model_validate(obj_tb)
        return Result.ok(data=response)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.error(code=500, message=msg)

@graphs_router.get("/get_by_session_id/{session_id}", response_model=Result[GraphResponse])
async def get_by_id(
        session_id: str = Path(default=...),
        session: AsyncSession = Depends(get_db),
        service: GraphService = Depends(ServiceManager.get_service_dependency(GraphService)),
        session_service: SessionService = Depends(ServiceManager.get_service_dependency(SessionService)),
):
    try:
        session_obj = await session_service.get_by_id(session, session_id)
        if not session_obj:
            return Result.error(code=404, message="Source Not Found")
        obj_tb: GraphTable = await service.get_by_id(session, session_obj.graph_id)
        if not obj_tb:
            return Result.error(code=404, message="Source Not Found")
        response = GraphResponse.model_validate(obj_tb)
        return Result.ok(data=response)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.error(code=500, message=msg)


@graphs_router.get("/page", response_model=Result[PaginationInfo[List[GraphResponse]]])
async def page(
        list_request: PageGraphRequest = Depends(),
        session: AsyncSession = Depends(get_db),
        service: GraphService = Depends(ServiceManager.get_service_dependency(GraphService)),
):
    try:
        params = CustomParams(page=list_request.page, size=list_request.size)

        pages: Page[GraphTable] = await service.get_paginated_list(
            session, params, sort=list_request.sort
        )
        data = [GraphResponse.model_validate(item) for item in pages.items]
        page_info = PaginationInfo.from_fastapi_page(data=data, page_result=pages)
        return Result.ok(data=page_info)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.error(code=500, message=msg)


@graphs_router.delete("/delete_by_id/{id}", response_model=Result[bool])
async def delete_by_id(
        _id: str = Path(default=..., alias="id"),
        session: AsyncSession = Depends(get_db),
        service: GraphService = Depends(ServiceManager.get_service_dependency(GraphService)),
):
    try:
        is_deleted: bool = await service.delete_by_id(session, _id)
        if not is_deleted:
            return Result.error(code=500, message="Delete Source Failed")
        return Result.ok(data=is_deleted)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.error(code=500, message=msg)


@graphs_router.put("/update_by_id/{id}", response_model=Result[GraphResponse])
async def update_by_id(
        update_request: UpdateGraphRequest,
        _id: str = Path(default=..., alias="id"),
        session: AsyncSession = Depends(get_db),
        service: GraphService = Depends(ServiceManager.get_service_dependency(GraphService)),
):
    """
    更新 Graph
    - 可以更新 name, description, spec
    - 如果更新了 spec，current_version_id 会设为 NULL（标记有未保存修改）
    - 如果只更新 name/description，current_version_id 不变
    """
    try:
        update_data = update_request.model_dump(exclude_defaults=True, exclude_none=True)
        obj_tb: GraphTable = await service.update_by_id(session, _id, update_data)
        if not obj_tb:
            return Result.error(code=500, message="Update Graph Failed")
        response = GraphResponse.model_validate(obj_tb)
        return Result.ok(data=response)
    except ValueError as e:
        msg = str(e)
        logger.error(msg)
        return Result.error(code=400, message=msg)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.error(code=500, message=msg)


@graphs_router.post("/{id}/snapshot", response_model=Result[GraphVersionResponse])
async def create_snapshot(
        _id: str = Path(default=..., alias="id"),
        session: AsyncSession = Depends(get_db),
        service: GraphService = Depends(ServiceManager.get_service_dependency(GraphService)),
):
    """为 Graph 创建快照版本"""
    try:
        version = await service.create_snapshot(session, _id)
        response = GraphVersionResponse.model_validate(version)
        return Result.ok(data=response)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.error(code=500, message=msg)


@graphs_router.post("/{id}/rollback/{version_id}", response_model=Result[GraphRollbackResponse])
async def rollback_to_version(
        _id: str = Path(default=..., alias="id"),
        version_id: int = Path(default=...),
        session: AsyncSession = Depends(get_db),
        service: GraphService = Depends(ServiceManager.get_service_dependency(GraphService)),
):
    """回滚到指定版本"""
    try:
        graph, branch_session_id = await service.rollback_to_version(session, _id, version_id)
        response = GraphRollbackResponse(
            graph=GraphResponse.model_validate(graph),
            branch_session_id=branch_session_id,
        )
        return Result.ok(data=response)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.error(code=500, message=msg)


@graphs_router.post("/stream", response_model=Result[ExecutionResponse])
async def submit_stream_conversation(
        request: GraphConversationRequest,
        session_id: Optional[str] = Query(default=uuid.uuid4().hex)
):
    execution_id = uuid.uuid4().hex
    try:
        generator = GraphSpecGenerator(
            source_id=execution_id,
            model_card_manager=model_card_manager,
            tool_router=tool_factory,
            function_router=function_router,
        )
        await StreamManager.create(execution_id, generator)
        await generator.submit_task(session_id=session_id, request=request)
        return Result.ok(data=ExecutionResponse(session_id=session_id, execution_id=execution_id))
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        logger.error(msg)
        return Result.error(message=msg)


@graphs_router.get("/stream/{execution_id}")
async def stream_conversation(
        execution_id: str = Path(...),
        last_event_id: Optional[str] = Header(default=None, alias="Last-Event-ID"),
        latest_event_id: Optional[str] = Query(default=None),
):
    """
    获取 Graph 对话的流式响应

    Args:
        execution_id: 执行 ID（从 submit_stream_conversation 返回）
        last_event_id: SSE 重连时的最后一个事件 ID（从 Header）
        latest_event_id: SSE 重连时的最后一个事件 ID（从 Query，优先级更高）

    Returns:
        StreamingResponse: SSE 流式响应
    """
    return await create_sse_response(
        execution_id=execution_id,
        last_event_id=last_event_id,
        latest_event_id=latest_event_id
    )
