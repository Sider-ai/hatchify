import uuid
from typing import Any, Optional, List, Dict

from fastapi import APIRouter, Request, HTTPException, UploadFile, Header, Query, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import FormData
from starlette.responses import StreamingResponse

from hatchify.business.utils.sse_helper import create_sse_response
from hatchify.business.db.session import get_db
from hatchify.business.manager.service_manager import ServiceManager
from hatchify.business.services.graph_service import GraphService
from hatchify.common.domain.entity.graph_execute_data import FileData, GraphExecuteData
from hatchify.common.domain.entity.graph_spec import GraphSpec
from hatchify.common.domain.responses.web_hook import WebHookInfoResponse, ExecutionResponse
from hatchify.common.domain.result.result import Result
from hatchify.common.extensions.ext_storage import storage_client
from hatchify.common.settings.settings import get_hatchify_settings
from hatchify.core.factory.session_manager_factory import create_session_manager
from hatchify.core.graph.dynamic_graph_builder import DynamicGraphBuilder

from hatchify.core.graph.hooks.graph_state_hook import GraphStateHook
from hatchify.core.manager.stream_manager import StreamManager
from hatchify.core.manager.function_manager import function_router
from hatchify.core.manager.tool_manager import tool_factory
from hatchify.core.stream_handler.graph_executor import GraphExecutor
from hatchify.core.utils.webhook_utils import infer_webhook_spec_from_schema

settings = get_hatchify_settings()
web_hook_router = APIRouter(prefix="/web-hooks")


async def prepare_data(graph_id: str, graph_spec: GraphSpec, request: Request):
    files: Dict[str, List[FileData]] = {}
    json_data: Dict[str, Any] = {}
    webhook_spec = infer_webhook_spec_from_schema(graph_spec.input_schema)
    if webhook_spec.input_type == "multipart/form-data":

        form: FormData = await request.form()

        for field_name in webhook_spec.file_fields:
            if field_name in form:
                uploaded_file: UploadFile = form[field_name]
                key = f"{graph_id}/hatchify__{uploaded_file.filename}"
                await storage_client.save(key=key, data=await uploaded_file.read(), mimetype=uploaded_file.content_type)
                files[field_name] = [FileData(
                    key=key,
                    mime=uploaded_file.content_type or "application/octet-stream",
                    name=uploaded_file.filename,
                    source=settings.storage.platform
                )]
        for field_name in webhook_spec.data_fields:
            if field_name in form:
                json_data[field_name] = form[field_name]

    else:
        json_data = await request.json()

    execute_data = GraphExecuteData(jsons=json_data, files=files)
    return execute_data


@web_hook_router.get("/webhook-info/{graph_id}", response_model=Result[WebHookInfoResponse])
async def get_webhook_info(
        graph_id: str,
        session: AsyncSession = Depends(get_db),
        service: GraphService = Depends(ServiceManager.get_service_dependency(GraphService)),
):
    try:
        graph_spec = await service.get_graph_spec(session, graph_id)
        if not graph_spec:
            raise HTTPException(status_code=404, detail=f"Graph '{graph_id}' not found")

        webhook_spec = infer_webhook_spec_from_schema(graph_spec.input_schema)
        return Result.ok(data=WebHookInfoResponse(
            graph_id=graph_id,
            input_type=webhook_spec.input_type,
            data_fields=webhook_spec.data_fields,
            file_fields=webhook_spec.file_fields,
            input_schema=webhook_spec.input_schema,
            output_schema=graph_spec.output_schema,
        ))
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        logger.error(msg)
        return Result.error(message=msg)


@web_hook_router.post("/invoke/{graph_id}", response_model=Result[Dict[str, Any]])
async def invoke(
        graph_id: str,
        request: Request,
        session: AsyncSession = Depends(get_db),
        service: GraphService = Depends(ServiceManager.get_service_dependency(GraphService)),
):
    result_dict = {}
    session_id = uuid.uuid4().hex
    graph_spec = await service.get_graph_spec(session, graph_id)
    if not graph_spec:
        return Result.error(code=404, message=f"Graph '{graph_id}' not found")

    output_required = graph_spec.output_schema.get("required", [])
    execute_data = await prepare_data(graph_id, graph_spec, request)

    builder = DynamicGraphBuilder(
        tool_router=tool_factory,
        function_router=function_router,
        hooks=[GraphStateHook()],
        session_manager=create_session_manager(session_id=session_id)
    )

    graph = builder.build_graph(graph_spec)

    executor = GraphExecutor(graph_id, graph, graph_spec)

    try:
        graph_result = await executor.invoke_async(execute_data)

        for node, node_result in graph_result.results.items():
            if node in output_required:
                result_dict[node] = node_result.result.structured_output.model_dump()

        return Result.ok(data=result_dict)

    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        logger.error(msg)
        return Result.error(message=msg)


@web_hook_router.post("/stream/{graph_id}", response_model=Result[ExecutionResponse])
async def submit(
        graph_id: str,
        request: Request,
        session: AsyncSession = Depends(get_db),
        service: GraphService = Depends(ServiceManager.get_service_dependency(GraphService)),
):
    graph_spec = await service.get_graph_spec(session, graph_id)
    if not graph_spec:
        return Result.error(code=404, message=f"Graph '{graph_id}' not found")

    execution_id = uuid.uuid4().hex

    try:
        execute_data = await prepare_data(graph_id, graph_spec, request)

        builder = DynamicGraphBuilder(
            tool_router=tool_factory,
            function_router=function_router,
            hooks=[GraphStateHook()],
            session_manager=create_session_manager(session_id=execution_id)
        )
        graph = builder.build_graph(graph_spec)

        executor = GraphExecutor(execution_id, graph, graph_spec)

        await StreamManager.create(execution_id, executor)

        await executor.submit_task(execute_data)

        return Result.ok(data=ExecutionResponse(execution_id=execution_id))

    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        logger.error(msg)
        return Result.error(message=msg)


@web_hook_router.get("/stream/{execution_id}")
async def stream(
        execution_id: str,
        last_event_id: Optional[str] = Header(default=None, alias="Last-Event-ID"),
        latest_event_id: Optional[str] = Query(default=None),
        replay: bool = Query(default=False),
):
    """
    获取 Webhook 执行的流式响应

    Args:
        execution_id: 执行 ID（从 submit 返回）
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
