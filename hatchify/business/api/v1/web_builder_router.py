import uuid
from typing import Optional

from fastapi import APIRouter, Path, Depends, HTTPException, Header, Query
from fastapi.responses import StreamingResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from strands.agent import SlidingWindowConversationManager

from hatchify.business.db.session import get_db
from hatchify.business.manager.service_manager import ServiceManager
from hatchify.business.services.graph_service import GraphService
from hatchify.business.utils.sse_helper import create_sse_response
from hatchify.common.domain.entity.agent_card import AgentCard
from hatchify.common.domain.entity.init_context import InitContext
from hatchify.common.domain.requests.web_builder import WebBuilderConversationRequest
from hatchify.common.domain.responses.web_hook import ExecutionResponse
from hatchify.common.domain.result.result import Result
from hatchify.common.settings.settings import get_hatchify_settings
from hatchify.core.factory.agent_factory import create_agent_by_agent_card
from hatchify.core.factory.session_manager_factory import create_session_manager
from hatchify.core.graph.hooks.security_file_hook import SecurityFileHook
from hatchify.core.manager.stream_manager import StreamManager
from hatchify.core.prompts.prompts import WEB_BUILDER_SYSTEM_PROMPT
from hatchify.core.stream_handler.web_builder import WebBuilderGenerator
from hatchify.core.utils.quick_init_utils import sync_web_project
from hatchify.core.utils.webhook_utils import infer_webhook_spec_from_schema

settings = get_hatchify_settings()
web_builder_router = APIRouter(prefix="/web-builder")


def create_web_builder_agent_card(
        project_path: str,
        graph_id: str,
        input_type: str,
        description: str
) -> AgentCard:
    """创建 Web Builder Agent 的 AgentCard"""
    return AgentCard(
        name="web-builder",
        model=settings.models.web_builder.model,
        provider=settings.models.web_builder.provider,
        instruction=WEB_BUILDER_SYSTEM_PROMPT.format(
            project_path=project_path,
            graph_id=graph_id,
            input_type=input_type,
            description=description
        ),
        description="Web application customization assistant",
        tools=["file_read", "image_reader", "editor", "file_write", "shell"],
    )


@web_builder_router.post("/stream", response_model=Result[ExecutionResponse])
async def submit_stream_conversation(
        request: WebBuilderConversationRequest,
        session_id: Optional[str] = Query(default=uuid.uuid4().hex),
        session: AsyncSession = Depends(get_db),
        service: GraphService = Depends(ServiceManager.get_service_dependency(GraphService)),
):
    """
    提交 Web Builder 流式对话任务

    通过自然语言与 LLM 对话，修改 Web 应用代码使其更符合 Graph 主题。

    流程：
    1. 获取 Graph 当前 spec
    2. 同步 Web 项目（如不存在则创建，更新配置文件）
    3. 创建 Agent 和 Generator
    4. 提交流式任务并返回 execution_id
    """
    execution_id = uuid.uuid4().hex
    try:
        # 1. 获取当前 Graph spec
        graph_spec = await service.get_graph_spec(session, request.graph_id)
        if not graph_spec:
            raise HTTPException(status_code=404, detail=f"Graph '{request.graph_id}' not found")

        # 2. 推断 webhook 配置
        webhook_spec = infer_webhook_spec_from_schema(graph_spec.input_schema)

        # 3. 构建初始化上下文
        init_ctx = InitContext(
            base_url=settings.server.base_url,
            repo_url=settings.web_app_builder.repo_url,
            graph_id=request.graph_id,
            graph_input_format=webhook_spec.input_type,
            input_schema=graph_spec.input_schema or {},
            output_schema=graph_spec.output_schema or {},
        )

        # 4. 同步 Web 项目（确保存在 + 配置最新）
        project_path = await sync_web_project(request.graph_id, init_ctx)
        project_absolute_path =  project_path.absolute().as_posix()
        # 5. 创建 Agent Card
        agent_card = create_web_builder_agent_card(
            project_path=project_absolute_path,
            graph_id=request.graph_id,
            input_type=webhook_spec.input_type,
            description=graph_spec.description
        )
        # 6. 创建 Agent
        agent = create_agent_by_agent_card(
            agent_card=agent_card,
            conversation_manager=SlidingWindowConversationManager(),
            session_manager=create_session_manager(session_id=session_id),
            hooks=[SecurityFileHook(project_absolute_path)]
        )

        # 7. 创建 Generator 并提交任务
        generator = WebBuilderGenerator(
            source_id=execution_id,
            agent=agent,
        )
        await StreamManager.create(execution_id, generator)
        await generator.submit_task(request=request)

        # 8. 返回 execution_id
        return Result.ok(data=ExecutionResponse(session_id=session_id, execution_id=execution_id))

    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        logger.error(msg)
        return Result.error(message=msg)


@web_builder_router.get("/stream/{execution_id}")
async def stream_conversation(
        execution_id: str = Path(...),
        last_event_id: Optional[str] = Header(default=None, alias="Last-Event-ID"),
        latest_event_id: Optional[str] = Query(default=None),
):
    """
    获取 Web Builder 对话的流式响应

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
