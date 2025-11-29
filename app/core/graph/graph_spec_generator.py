import json
from typing import Optional, cast, Any, Dict, List, Union, Tuple

from litellm.types.completion import ChatCompletionSystemMessageParam, \
    ChatCompletionUserMessageParam, ChatCompletionMessageParam
from litellm.types.utils import Usage
from loguru import logger
from strands.models.litellm import LiteLLMModel
from strands.tools.decorator import DecoratedFunctionTool
from strands.types.content import ContentBlock, Role

from app.business.db.session import transaction, AsyncSessionLocal
from app.business.manager.repository_manager import RepositoryManager
from app.business.manager.service_manager import ServiceManager
from app.business.models.messages import MessageTable
from app.business.models.session import SessionTable
from app.business.repositories.session_repository import SessionRepository
from app.business.services.graph_service import GraphService
from app.common.domain.entity.agent_node_spec import AgentNode
from app.common.domain.entity.function_node_spec import FunctionNode
from app.common.domain.entity.graph_spec import GraphSpec, Edge
from app.common.domain.enums.conversation_mode import ConversationMode
from app.common.domain.enums.message_role import MessageRole
from app.common.domain.enums.session_scene import SessionScene
from app.common.domain.requests.graph import ConversationRequest
from app.common.domain.structured_output.graph_generation_output import (
    GraphArchitectureOutput,
    SchemaExtractionOutput,
)
from app.common.event.base_event import StreamEvent, ResultEvent
from app.common.event.edit_event import PhaseEvent
from app.common.settings.settings import get_hatchify_settings
from app.core.factory.tool_factory import ToolRouter
from app.core.graph.stream_handler import BaseStreamHandler
from app.core.manager.model_card_manager import ModelCardManager
from app.core.prompts.prompts import (
    GRAPH_GENERATOR_SYSTEM_PROMPT,
    GRAPH_GENERATOR_USER_PROMPT,
    GRAPH_REFINEMENT_SYSTEM_PROMPT,
    GRAPH_REFINEMENT_USER_PROMPT,
    SCHEMA_EXTRACTOR_PROMPT, RESOURCE_MESSAGE,
)
from app.core.utils.json_generator import json_generator
from app.core.utils.schema_utils import generate_output_schema

settings = get_hatchify_settings()


class GraphSpecGenerator(BaseStreamHandler):

    def __init__(
            self,
            source_id: str,
            model_card_manager: ModelCardManager,
            tool_router: ToolRouter,
            function_router: ToolRouter[DecoratedFunctionTool],
    ):
        super().__init__(source_id=source_id)
        self.model_card_manager = model_card_manager
        self.tool_router = tool_router
        self.function_router = function_router

        self.spec_gen_config = settings.models.spec_generator
        self.spec_ext_config = settings.models.spec_generator

    async def _generate_graph_architecture(
            self,
            pre_graph_spec: Dict[str, Any],
            user_messages: List[Dict[str, Any]],
            history_messages: List[Dict[str, Any]]
    ) -> Tuple[GraphArchitectureOutput, Optional[Usage]]:
        """Step 1: 生成 Graph 架构

        使用 structured_output 调用 LLM，返回类型安全的 GraphArchitectureOutput
        """
        resource_message = RESOURCE_MESSAGE.format(
            available_models=self.model_card_manager.format_models_for_prompt(),
            available_tools=self.tool_router.format_for_prompt(),
            available_functions=self.function_router.format_functions_for_prompt(),
        )
        messages: List[Union[ChatCompletionMessageParam, Dict[str, Any]]] = [
            ChatCompletionSystemMessageParam(
                role="system",
                content=GRAPH_GENERATOR_SYSTEM_PROMPT
            ),
            ChatCompletionSystemMessageParam(
                role="system",
                content=resource_message
            ),
        ]
        if pre_graph_spec:
            messages.append(
                ChatCompletionSystemMessageParam(
                    role="system",
                    content=GRAPH_REFINEMENT_SYSTEM_PROMPT
                )
            )
        messages.extend(history_messages)
        messages.append(
            ChatCompletionUserMessageParam(
                role="user",
                content=GRAPH_GENERATOR_USER_PROMPT
            )
        )
        if pre_graph_spec:
            messages.append(
                ChatCompletionUserMessageParam(
                    role="user",
                    content=GRAPH_REFINEMENT_USER_PROMPT.format(
                        current_graph_spec=json.dumps(
                            pre_graph_spec,
                            ensure_ascii=False,
                            indent=2
                        )
                    )
                )
            )
        messages.extend(user_messages)
        result, usage = await json_generator(
            provider_id=self.spec_gen_config.provider,
            model_id=self.spec_gen_config.model,
            messages=messages,
            response_model=GraphArchitectureOutput,
            max_retries=3,
        )

        return result, usage

    async def _extract_schemas(
            self,
            graph_arch: GraphArchitectureOutput,
    ) -> Tuple[SchemaExtractionOutput, List[Usage]]:
        """Step 2: 从 agent instructions 提取 JSON schemas

        Router/Orchestrator 使用预定义 schema，General Agent 通过 LLM 提取。
        """
        usages = []
        agent_schemas = []

        # 分离需要预定义 schema 的 agent 和需要 LLM 提取的 agent
        agents_needing_llm = []

        for agent in graph_arch.agents:
            agents_needing_llm.append(agent)
            # # 尝试获取预定义 schema
            # predefined_schema = get_predefined_schema(agent.category)
            #
            # if predefined_schema:
            #     # 使用预定义 schema
            #     agent_schemas.append(
            #         AgentSchema(
            #             agent_name=agent.name,
            #             structured_output_schema=predefined_schema
            #         )
            #     )
            #     logger.info(
            #         f"Using predefined schema for {agent.category} agent: {agent.name}"
            #     )
            # else:
            #     # 需要 LLM 提取
            #     agents_needing_llm.append(agent)

        # 如果有需要 LLM 提取的 agent，调用 LLM
        if agents_needing_llm:
            # 构建只包含需要提取的 agent 的临时架构
            temp_arch = GraphArchitectureOutput(
                name=graph_arch.name,
                description=graph_arch.description,
                agents=agents_needing_llm,
                functions=graph_arch.functions,
                nodes=graph_arch.nodes,
                edges=graph_arch.edges,
                entry_point=graph_arch.entry_point
            )

            # 构建 user prompt
            user_prompt = SCHEMA_EXTRACTOR_PROMPT.format(
                graph_spec=temp_arch.model_dump_json(indent=2, ensure_ascii=False)
            )

            logger.info(
                f"Calling Schema Extractor LLM for {len(agents_needing_llm)} general agents..."
            )

            # 使用 json_generator - 自动处理 JSON 解析、验证和重试
            llm_result, usage = await json_generator(
                provider_id=self.spec_ext_config.provider,
                model_id=self.spec_ext_config.model,
                messages=[
                    ChatCompletionSystemMessageParam(
                        role="system",
                        content="You are a JSON schema expert. Extract schemas accurately from agent instructions."
                    ),
                    ChatCompletionUserMessageParam(
                        role="user",
                        content=user_prompt
                    )
                ],
                response_model=SchemaExtractionOutput,
                max_retries=3,
            )

            # 合并 LLM 提取的 schemas
            usages.append(usage)
            agent_schemas.extend(llm_result.agent_schemas)

        # 返回完整的 SchemaExtractionOutput
        return SchemaExtractionOutput(agent_schemas=agent_schemas), usages

    def _merge_and_create_spec(
            self,
            graph_arch: GraphArchitectureOutput,
            schemas_output: SchemaExtractionOutput,
    ) -> GraphSpec:
        """Step 3: 合并 schemas 并创建 GraphSpec 对象

        将 LLM 返回的 Pydantic 对象转换为 GraphSpec，
        并自动生成 output_schema（从终端节点提取）。
        """
        # 创建 agent name -> schema 的映射
        schema_map = {
            schema.agent_name: schema.structured_output_schema
            for schema in schemas_output.agent_schemas
        }

        # 解析 agents
        agents = []
        for agent_arch in graph_arch.agents:
            # 从映射中获取对应的 schema
            structured_output_schema = schema_map.get(agent_arch.name)

            # 创建 AgentNode
            agent_node = AgentNode(
                name=agent_arch.name,
                model=agent_arch.model,
                instruction=agent_arch.instruction,
                category=agent_arch.category,
                tools=agent_arch.tools,
                structured_output_schema=structured_output_schema,
            )
            agents.append(agent_node)

        # 解析 functions
        functions = []
        for func_arch in graph_arch.functions:
            function_node = FunctionNode(
                name=func_arch.name,
                function_ref=func_arch.function_ref,
            )
            functions.append(function_node)

        # 解析 edges
        edges = []
        for edge_arch in graph_arch.edges:
            edge = Edge(
                from_node=edge_arch.from_node,
                to_node=edge_arch.to_node,
            )
            edges.append(edge)

        graph_spec = GraphSpec(
            name=graph_arch.name,
            description=graph_arch.description,
            agents=agents,
            functions=functions,
            nodes=graph_arch.nodes,
            edges=edges,
            entry_point=graph_arch.entry_point,
            input_schema=graph_arch.input_schema,
            output_schema=None,
        )

        try:
            output_schema = generate_output_schema(graph_spec, self.function_router)
            graph_spec.output_schema = output_schema
            logger.info(
                f"自动生成 output_schema: {len(output_schema.get('properties', {}))} 个输出字段"
            )
        except Exception as e:
            logger.error(f"生成 output_schema 失败: {e}", exc_info=True)
            raise e

        return graph_spec

    @staticmethod
    def _normalize_role(role: Union[str | Role | MessageRole]) -> MessageRole:
        if isinstance(role, MessageRole):
            return role
        else:
            match role:
                case MessageRole.ASSISTANT.value:
                    return MessageRole.ASSISTANT
                # case MessageRole.SYSTEM.value:
                #     return MessageRole.SYSTEM
                # case MessageRole.TOOL.value:
                #     return MessageRole.TOOL
                case MessageRole.USER.value | _:
                    return MessageRole.USER

    async def handle_stream_event(self, event: Any):
        await self.stream_queue.put(event)

    async def submit_task(
            self,
            session_id: str,
            request: ConversationRequest,
    ):
        async_generator = self.conversation(session_id, request)
        await self.run_streamed(async_generator)

    async def conversation(
            self,
            session_id: str,
            request: ConversationRequest,
    ):
        async with AsyncSessionLocal() as session:

            yield StreamEvent(
                type="phase",
                data=PhaseEvent(phase="prepare", message="Initialization messages"),
            )
            graph_service = ServiceManager.get_service(GraphService)
            session_repo = RepositoryManager.get_repository(SessionRepository)

            # TODO 目前仅支持用户文本，暂不支持其他消息类型和二进制内容
            history_db_messages = await graph_service.get_recent_messages(session, session_id)
            history_messages: List[Dict[str, Any]] = LiteLLMModel.format_request_messages(
                graph_service.db_messages_to_messages(history_db_messages)
            )
            user_messages = LiteLLMModel.format_request_messages(request.messages)

            async with transaction(session):
                yield StreamEvent(
                    type="phase",
                    data=PhaseEvent(phase="prepare", message="Prepare the data table"),
                )
                session_obj = await session_repo.find_by_id(session, session_id)
                # create session and graph table
                if not session_obj:
                    graph_obj = await graph_service.create(
                        session,
                        {
                            "name": f"graph_{session_id}",
                            "description": "Auto generated from conversation",
                            "current_spec": {},
                        },
                        commit=False,
                    )
                    session_obj = SessionTable(
                        id=session_id,
                        graph_id=cast(str, graph_obj.id),
                        scene=SessionScene.GRAPH_EDIT,
                    )
                    await session_repo.save(session, session_obj)
                else:
                    graph_obj = await graph_service.get_by_id(session, cast(str, session_obj.graph_id))
                    if not graph_obj:
                        graph_obj = await graph_service.create(
                            session,
                            {
                                "name": f"graph_{session_obj.graph_id}_recreated",
                                "description": "Recreated for missing graph",
                                "current_spec": {},
                            },
                            commit=False,
                        )
                        await session_repo.update_by_id(
                            session,
                            cast(str, session_obj.id),
                            {"graph_id": cast(str, graph_obj.id)},
                        )

                # generate architecture
                yield StreamEvent(
                    type="phase",
                    data=PhaseEvent(phase="generate", message="Generating graph architecture"),
                )
                graph_arch, _ = await self._generate_graph_architecture(
                    pre_graph_spec=cast(Dict[str, Any], graph_obj.current_spec),
                    user_messages=user_messages,
                    history_messages=history_messages
                )

                # extract schemas
                yield StreamEvent(
                    type="phase",
                    data=PhaseEvent(phase="extract", message="Extracting schemas from instructions"),
                )
                schemas_output, _ = await self._extract_schemas(graph_arch)

                # merge
                yield StreamEvent(
                    type="phase",
                    data=PhaseEvent(phase="merge", message="Merging architecture and schemas"),
                )
                graph_spec = self._merge_and_create_spec(graph_arch, schemas_output)

                # result
                yield StreamEvent(
                    type="result",
                    data=ResultEvent(
                        data={
                            "graph_id": graph_obj.id,
                            "spec": graph_spec.model_dump(exclude_none=True),
                        }
                    ),
                )

                assistant_reply = graph_spec.model_dump_json(indent=2, ensure_ascii=False)

                if request.mode == ConversationMode.EDIT:
                    update_data: Dict[str, Any] = {
                        "name": graph_spec.name,
                        "description": graph_spec.description,
                        "current_spec": graph_spec.model_dump(exclude_none=True),
                    }
                    await graph_service.update_by_id(
                        session,
                        cast(str, graph_obj.id),
                        update_data,
                        commit=False,
                    )

                # write record
                yield StreamEvent(
                    type="phase",
                    data=PhaseEvent(phase="record", message="Persisting conversation messages"),
                )
                for msg in request.messages:
                    role: Role = msg.get("role")
                    normalize_role = self._normalize_role(role)
                    content: List[ContentBlock] = msg.get("content")
                    await session_repo.save(
                        session,
                        MessageTable(
                            session_id=cast(str, session_obj.id),
                            role=normalize_role,
                            content=content
                        ),
                    )
                await session_repo.save(
                    session,
                    MessageTable(
                        session_id=cast(str, session_obj.id),
                        role=MessageRole.ASSISTANT,
                        content=[ContentBlock(text=assistant_reply)],
                    ),
                )

                await session.flush()
