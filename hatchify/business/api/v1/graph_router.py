import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Header, Query
from fastapi_pagination import Page
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from hatchify.business.db.session import get_db
from hatchify.business.manager.service_manager import ServiceManager
from hatchify.business.models.execution import ExecutionTable
from hatchify.business.models.graph import GraphTable
from hatchify.business.services.execution_service import ExecutionService
from hatchify.business.services.graph_service import GraphService
from hatchify.business.utils.pagination_utils import CustomParams
from hatchify.business.utils.sse_helper import create_sse_response
from hatchify.common.domain.enums.execution_type import ExecutionType
from hatchify.common.domain.requests.graph import (
    PageGraphRequest,
    UpdateGraphRequest,
    GraphConversationRequest,
)
from hatchify.common.domain.responses.graph_response import GraphResponse
from hatchify.common.domain.responses.graph_version_response import GraphVersionResponse
from hatchify.common.domain.responses.pagination import PaginationInfo
from hatchify.common.domain.responses.web_hook import ExecutionResponse
from hatchify.common.domain.result.result import Result
from hatchify.core.manager.function_manager import function_router
from hatchify.core.manager.model_card_manager import model_card_manager
from hatchify.core.manager.stream_manager import StreamManager
from hatchify.core.manager.tool_manager import tool_factory
from hatchify.core.stream_handler.event_listener.execution_tracker_listener import ExecutionTrackerListener
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
        comment: Optional[str] = Query(default=None, description="快照备注"),
        session: AsyncSession = Depends(get_db),
        service: GraphService = Depends(ServiceManager.get_service_dependency(GraphService)),
):
    """
    为 Graph 创建快照版本
    - 自动使用 graph.current_session_id 作为来源会话
    - 复制会话历史，生成分支会话
    - Graph.current_session_id 不变（继续在工作区对话）
    """
    try:
        version = await service.create_snapshot(session, _id, comment=comment)
        response = GraphVersionResponse.model_validate(version)
        return Result.ok(data=response)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.error(code=500, message=msg)


@graphs_router.post("/{id}/rollback/{version_id}", response_model=Result[GraphResponse])
async def rollback_to_version(
        _id: str = Path(default=..., alias="id"),
        version_id: int = Path(default=...),
        session: AsyncSession = Depends(get_db),
        service: GraphService = Depends(ServiceManager.get_service_dependency(GraphService)),
):
    """
    回滚到指定版本
    - 自动切换到该版本的 branch_session_id
    - 返回的 GraphResponse 包含更新后的 current_session_id
    """
    try:
        graph = await service.rollback_to_version(session, _id, version_id)
        response = GraphResponse.model_validate(graph)
        return Result.ok(data=response)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)}"
        logger.error(msg)
        return Result.error(code=500, message=msg)


@graphs_router.post("/stream/{graph_id}", response_model=Result[ExecutionResponse])
async def submit_stream_conversation(
        request: GraphConversationRequest,
        session: AsyncSession = Depends(get_db),
        graph_service: GraphService = Depends(ServiceManager.get_service_dependency(GraphService)),
        execution_service: ExecutionService = Depends(ServiceManager.get_service_dependency(ExecutionService)),
):
    """
    Graph 对话接口（通过对话生成/修改 Graph spec）

    - 如果提供 graph_id：使用该 Graph 的 current_session_id，对话历史会累积
    - 如果不提供 graph_id：自动创建新的 Graph 和 Session
    """
    try:
        if request.graph_id:
            graph_id = request.graph_id
        else:
            graph_id = uuid.uuid4().hex

        # 1. 获取或创建 Graph
        graph = await graph_service.get_by_id(session, graph_id)

        if graph:
            # 场景 1: Graph 已存在，使用其 current_session_id（对话历史会累积）
            current_session_id = graph.current_session_id
        else:
            # 场景 2: Graph 不存在，创建新 Graph（使用传入的 graph_id 或生成的 UUID）
            graph = await graph_service.create(
                session,
                {
                    "id": graph_id,  # 使用指定的 graph_id
                    "name": "Untitled Graph",
                    "current_spec": None,  # None 表示尚未生成 spec，首次对话时会自动更新 name 和 spec
                }
            )
            current_session_id = graph.current_session_id

        # 2. 创建执行记录
        execution_obj: ExecutionTable = await execution_service.create_execution(
            session=session,
            execution_type=ExecutionType.GRAPH_BUILDER,
            graph_id=graph_id,
            session_id=current_session_id,
        )

        # 3. 创建 Generator（会自动通过 Hook 更新状态）
        generator = GraphSpecGenerator(
            source_id=execution_obj.id,
            model_card_manager=model_card_manager,
            tool_router=tool_factory,
            function_router=function_router,
            listeners=[ExecutionTrackerListener()]
        )
        await StreamManager.create(execution_obj.id, generator)
        await generator.submit_task(session_id=current_session_id, request=request)

        return Result.ok(data=ExecutionResponse(
            session_id=current_session_id,
            execution_id=execution_obj.id,
            graph_id=graph_id
        ))
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        logger.error(msg)
        return Result.error(message=msg)


@graphs_router.get("/stream/{execution_id}")
async def stream_conversation(
        execution_id: str = Path(...),
        last_event_id: Optional[str] = Header(default=None, alias="Last-Event-ID"),
        latest_event_id: Optional[str] = Query(default=None),
        replay: bool = Query(default=False),
):
    """
    获取 Graph 对话的流式响应

    Args:
        execution_id: 执行 ID（从 submit_stream_conversation 返回）
        last_event_id: SSE 重连时的最后一个事件 ID（从 Header）
        latest_event_id: SSE 重连时的最后一个事件 ID（从 Query，优先级更高）
        replay: 是否强制从头重播所有事件（即使任务已完成）

    Returns:
        StreamingResponse: SSE 流式响应
    """
    return await create_sse_response(
        execution_id=execution_id,
        last_event_id=last_event_id,
        latest_event_id=latest_event_id,
        replay=replay
    )
