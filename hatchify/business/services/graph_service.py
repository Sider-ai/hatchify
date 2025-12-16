import mimetypes
from typing import Optional, cast, List, get_args, Sequence, Tuple, Any

from sqlalchemy.ext.asyncio import AsyncSession
from strands.types.content import ContentBlock, Messages, Message
from strands.types.media import DocumentFormat, VideoFormat, ImageFormat, DocumentContent, ImageContent, VideoContent

from hatchify.business.db.session import transaction
from hatchify.business.manager.repository_manager import RepositoryManager
from hatchify.business.manager.service_manager import ServiceManager
from hatchify.business.models.graph import GraphTable
from hatchify.business.models.graph_version import GraphVersionTable
from hatchify.business.models.messages import MessageTable
from hatchify.business.models.session import SessionTable
from hatchify.business.repositories.graph_repository import GraphRepository
from hatchify.business.repositories.graph_version_repository import GraphVersionRepository
from hatchify.business.repositories.message_repository import MessageRepository
from hatchify.business.repositories.session_repository import SessionRepository
from hatchify.business.services.base.generic_service import GenericService
from hatchify.business.services.graph_version_service import GraphVersionService
from hatchify.business.services.session_service import SessionService
from hatchify.common.domain.entity.graph_spec import GraphSpec
from hatchify.common.domain.enums.graph_version_type import GraphVersionType
from hatchify.common.domain.enums.session_scene import SessionScene
from hatchify.common.domain.requests.graph_patch import GraphSpecPatchRequest
from hatchify.core.graph.dynamic_graph_builder import DynamicGraphBuilder
from hatchify.core.manager.function_manager import function_router
from hatchify.core.manager.tool_manager import tool_factory

document_formats = get_args(DocumentFormat)
image_formats = get_args(ImageFormat)
video_formats = get_args(VideoFormat)


class GraphService(GenericService[GraphTable]):

    def __init__(self):
        super().__init__(GraphTable, GraphRepository)
        self._repository: GraphRepository = RepositoryManager.get_repository(GraphRepository)
        self._version_repo: GraphVersionRepository = RepositoryManager.get_repository(GraphVersionRepository)
        self._session_repo: SessionRepository = RepositoryManager.get_repository(SessionRepository)
        self._message_repo: MessageRepository = RepositoryManager.get_repository(MessageRepository)
        self._version_service: GraphVersionService = ServiceManager.get_service(GraphVersionService)
        self._session_service: SessionService = ServiceManager.get_service(SessionService)

    @staticmethod
    async def clean_strands_messages(messages: Messages):
        for message in messages:
            contents: List[ContentBlock] = message.get("content", [])
            for content in contents:

                video_content: VideoContent = content.get("video")
                if document_content := cast(DocumentContent, content.get("document")):
                    content_type = mimetypes.guess_type(cast(str, document_content.get("format")))
                if image_content := cast(ImageContent, content.get("image")):
                    content_type = mimetypes.guess_type(cast(str, image_content.get("format")))
                if video_content := cast(VideoContent, content.get("video")):
                    content_type = mimetypes.guess_type(cast(str, video_content.get("format")))

    async def get_recent_messages(
            self,
            session: AsyncSession,
            session_id: str,
            limit: int = 10,
    ) -> Sequence[MessageTable]:
        """
        按条数拉取指定 session 的历史消息（默认最近 20 条），按 created_at 升序。
        """
        limit = max(limit, 1)
        return await self._message_repo.find_by(
            session,
            session_id=session_id,
            limit=limit,
            sort="created_at:asc",
        )

    @staticmethod
    def db_messages_to_messages(db_messages: Sequence[MessageTable]) -> Messages:
        messages: Messages = []
        for msg in db_messages:
            messages.append(Message(
                role=msg.role.value,  # type: ignore
                content=cast(List[ContentBlock], msg.content)
            ))
        return messages

    async def get_graph_spec(
            self,
            session: AsyncSession,
            graph_id: str
    ) -> GraphSpec | None:
        graph_obj = await self.get_by_id(session, graph_id)
        if not graph_obj or graph_obj.current_spec is None:
            return None
        return GraphSpec.model_validate(graph_obj.current_spec)

    async def get_current_session_id(
            self,
            session: AsyncSession,
            graph_id: str
    ) -> str:
        """
        获取 Graph 的当前 Session ID
        """
        graph = await self.get_by_id(session, graph_id)
        if not graph:
            raise ValueError(f"Graph {graph_id} not found")

        if not graph.current_session_id:
            raise ValueError(f"Graph {graph_id} has no current_session_id")

        return graph.current_session_id

    async def create(
            self,
            session: AsyncSession,
            entity_data: dict,
            commit: bool = True
    ) -> GraphTable:
        """
        创建 Graph，自动创建默认 Session
        """
        try:
            # 1. 创建 Graph（不提交）
            graph = await super().create(session, entity_data, commit=False)

            # 2. 通过 SessionService 创建默认 Session（遵守层级原则）
            default_session = await self._session_service.create(
                session,
                {
                    "graph_id": graph.id,
                    "scene": SessionScene.GRAPH_EDIT.value,
                },
                commit=False
            )

            # 3. 设置 current_session_id
            graph.current_session_id = default_session.id

            # 4. 提交或返回
            if commit:
                await session.commit()
                await session.refresh(graph)

            return graph
        except Exception:
            if commit:
                await session.rollback()
            raise

    async def _create_draft_snapshot(
            self,
            session: AsyncSession,
            graph: GraphTable,
            comment: Optional[str] = None,
            parent_version_id: Optional[int] = None,
    ) -> GraphVersionTable:
        """
        为 Graph 创建草稿快照（最多保留 3 条，超出则删除最早的）
        - 自动使用 graph.current_session_id 作为来源会话
        - 复制会话历史，生成分支会话，写入 branch_session_id
        - 删除超出的草稿时，通过 VersionService 批量级联删除关联的 Session 和 Message
        """
        drafts = await self._version_repo.list_drafts_by_graph(session, graph.id)

        # 收集需要删除的草稿 ID
        draft_ids_to_delete = []
        while len(drafts) >= 3:
            oldest = drafts.pop(0)
            draft_ids_to_delete.append(oldest.id)

        # 批量删除超出的草稿（会自动删除 Session 和 Message）
        if draft_ids_to_delete:
            await self._version_service.delete_by_ids(
                session,
                draft_ids_to_delete,
                commit=False  # 不立即提交
            )

        # 使用当前工作区的 session 作为来源
        source_session_id = graph.current_session_id

        # 复制来源会话历史（全部消息）
        branched_session = await self._fork_session_with_messages(
            session=session,
            graph_id=graph.id,
            source_session_id=source_session_id,
        )
        draft = GraphVersionTable(
            graph_id=graph.id,
            type=GraphVersionType.DRAFT,
            version=None,
            spec=graph.current_spec,
            comment=comment or "auto-draft",
            parent_version_id=parent_version_id,
            branch_session_id=branched_session.id if branched_session else None,
        )
        await self._version_repo.save(session, draft)
        await session.flush()
        return draft

    async def _fork_session_with_messages(
            self,
            session: AsyncSession,
            graph_id: str,
            source_session_id: Optional[str],
            source_message_id: Optional[str] = None,
    ) -> Optional[SessionTable]:
        """
        基于来源会话复制消息，生成新的分支会话。
        - 如果未提供 source_session_id，则取该 graph 最新的会话
        - 如果提供 source_message_id，则只复制该消息及之前的消息
        - 通过 SessionService 创建分支会话（遵守层级原则）
        """
        # 1. 解析 source_session_id
        resolved_session_id = source_session_id
        if not resolved_session_id:
            sessions = await self._session_repo.find_by(
                session,
                graph_id=graph_id,
                limit=1,
                sort="created_at:desc",
            )
            resolved_session_id = sessions[0].id if sessions else None

        if not resolved_session_id:
            raise ValueError(f"No source session found for graph {graph_id}")

        # 2. 获取需要复制的消息
        messages = await self._message_repo.find_by(
            session,
            session_id=resolved_session_id,
            sort="created_at:asc",
        )

        messages_to_copy: List[MessageTable] = []
        if source_message_id:
            for msg in messages:
                messages_to_copy.append(msg)
                if msg.id == source_message_id:
                    break
            else:
                raise ValueError(
                    f"Source message {source_message_id} not found in session {resolved_session_id}"
                )
        else:
            messages_to_copy = list(messages)

        # 3. 通过 SessionService 创建分支会话（遵守层级原则）
        new_session = await self._session_service.fork_session_with_messages(
            session,
            new_session_data={
                "graph_id": graph_id,
                "parent_session_id": resolved_session_id,
                "fork_from_message_id": source_message_id,
            },
            messages_to_copy=messages_to_copy,
            commit=False
        )

        return new_session

    async def update_by_id(
            self,
            session: AsyncSession,
            entity_id: str,
            update_data: dict,
            commit: bool = True
    ) -> Optional[GraphTable]:
        """
        更新 Graph
        - 如果更新了 spec，current_version_id 会设为 NULL（标记有未保存修改）
        - 如果只更新 name/description，current_version_id 不变
        """
        try:
            # 如果更新了 spec，则标记为有未保存修改
            if "spec" in update_data:
                validated_spec = self._validate_spec(update_data.pop("spec"))
                update_data["current_spec"] = validated_spec
                update_data["current_version_id"] = None

            result = await self._repository.update_by_id(session, entity_id, update_data)

            if commit:
                await session.commit()
                if result:
                    await session.refresh(result)

            return result
        except Exception:
            if commit:
                await session.rollback()
            raise

    @staticmethod
    def _validate_spec(spec_data: dict) -> dict:
        spec_model = GraphSpec.model_validate(spec_data)
        builder = DynamicGraphBuilder(
            tool_router=tool_factory,
            function_router=function_router,
        )
        builder.build_graph(spec_model)

        return spec_model.model_dump(exclude_none=True)

    async def create_snapshot(
            self,
            session: AsyncSession,
            graph_id: str,
            comment: Optional[str] = None,
    ) -> GraphVersionTable:
        """
        为 Graph 创建快照版本（纯粹保存副本，不改变工作区状态）
        - 自动使用 graph.current_session_id 作为来源会话
        - 复制会话历史，生成分支会话
        - Graph.current_session_id 不变（继续在工作区对话）
        - Graph.current_version_id 不变（打快照不影响 dirty 状态）

        1. 读取 Graph.current_spec（加锁）
        2. 计算新的 version 号（max(version) + 1）
        3. 创建 GraphVersion（保存 spec 和对话历史的副本）

        使用悲观锁防止并发创建相同版本号
        """
        # 1. 获取 Graph（加悲观锁）
        async with transaction(session):

            graph = await self._repository.get_by_id_with_lock(session, graph_id)
            if not graph:
                raise ValueError(f"Graph {graph_id} not found")

            # 1.1 确定 parent_version_id（即将基于哪个版本创建快照）
            # 如果 current_version_id 存在（例如回滚后），则使用它
            # 否则使用最新的 SNAPSHOT（例如一直在工作区修改）
            if graph.current_version_id is not None:
                parent_version = await self._version_repo.find_by_id(
                    session, graph.current_version_id
                )
                parent_id = graph.current_version_id
            else:
                parent_version = await self._version_repo.get_latest_version_by_graph(
                    session, graph_id
                )
                parent_id = parent_version.id if parent_version else None

            # 1.2 检查是否有未保存的变化（和父版本比较）
            if parent_version and parent_version.spec == graph.current_spec:
                raise ValueError(
                    f"当前 spec 与版本 {parent_version.version} 完全相同，无需创建新快照"
                )

            # 1.4 使用当前工作区的 session 作为来源
            source_session_id = graph.current_session_id

            # 2. 计算新的 version 号
            max_version = await self._version_repo.get_max_version_by_graph(
                session, graph_id
            )
            new_version_no = (max_version or 0) + 1

            # 3. 创建分支会话（复制全部历史消息）
            branched_session = await self._fork_session_with_messages(
                session=session,
                graph_id=graph_id,
                source_session_id=source_session_id,
            )
            branch_session_id = branched_session.id if branched_session else None

            # 4. 创建 GraphVersion
            new_graph_version = GraphVersionTable(
                graph_id=graph_id,
                type=GraphVersionType.SNAPSHOT,
                version=new_version_no,
                spec=graph.current_spec,
                parent_version_id=parent_id,
                branch_session_id=branch_session_id,
                comment=comment,
            )
            await self._version_repo.save(session, new_graph_version)
            await session.flush()

            # 5. 不更新 Graph.current_version_id
            # 打快照只是保存副本，不改变工作区状态
            # 如果工作区之前是 dirty，打快照后依然是 dirty

            await session.refresh(new_graph_version)
            return new_graph_version

    async def rollback_to_version(
            self,
            session: AsyncSession,
            graph_id: str,
            version_id: int,
    ) -> GraphTable:
        """
        回滚到指定版本
        - 自动切换到目标版本的 branch_session_id
        - 如果目标版本没有 branch_session_id，创建新会话

        1. 读取指定 version 的 spec
        2. 更新 Graph.current_spec = 该版本的 spec
        3. 更新 Graph.current_version_id = version_id
        4. 更新 Graph.current_session_id = 目标版本的会话
        """
        async with transaction(session):
            graph = await self._repository.get_by_id_with_lock(session, graph_id)
            if not graph:
                raise ValueError(f"Graph {graph_id} not found")

            # 1. 获取指定版本
            target_version = await self._version_repo.find_by_id(session, version_id)
            if not target_version:
                raise ValueError(f"GraphVersion {version_id} not found")

            if target_version.graph_id != graph_id:
                raise ValueError(
                    f"GraphVersion {version_id} does not belong to Graph {graph_id}"
                )

            # 2. 检测当前工作区是否 dirty
            dirty = graph.current_version_id is None
            if not dirty and graph.current_version_id is not None:
                current_version = await self._version_repo.find_by_id(
                    session, graph.current_version_id
                )
                if (not current_version) or graph.current_spec != current_version.spec:
                    dirty = True

            # 3. 如果 dirty，先创建草稿快照
            if dirty:
                await self._create_draft_snapshot(
                    session=session,
                    graph=graph,
                    comment="auto-draft before rollback",
                    parent_version_id=graph.current_version_id,
                )

            # 4. 确定目标会话
            target_session_id = target_version.branch_session_id
            if not target_session_id:
                # 目标版本没有关联会话，通过 SessionService 创建新会话（遵守层级原则）
                new_session = await self._session_service.create(
                    session,
                    {
                        "graph_id": graph_id,
                        "scene": SessionScene.GRAPH_EDIT.value,
                    },
                    commit=False
                )
                target_session_id = new_session.id

            # 5. 更新 Graph（包括切换会话）
            update_data = {
                "current_spec": target_version.spec,
                "current_version_id": version_id,
                "current_session_id": target_session_id,  # 切换会话
            }
            result = await self._repository.update_by_id(session, graph_id, update_data)

            if not result:
                raise ValueError(f"Failed to rollback Graph {graph_id}")

            await session.refresh(result)
            return result

    async def delete_by_id(
            self,
            session: AsyncSession,
            entity_id: Any,
            commit: bool = True
    ) -> bool:
        """
        删除 Graph 时自动级联删除所有关联数据

        删除顺序（层级化）：
        1. 批量删除所有 GraphVersion（会自动删除其 branch_session_id 和 Message）
        2. 删除工作区 current_session_id（会自动删除其 Message）
        3. 删除 Graph 记录
        """
        try:
            # 0. 获取 Graph 记录
            graph = await self._repository.find_by_id(session, entity_id)
            if not graph:
                return False

            # 1. 批量删除所有 GraphVersion（通过 VersionService，会自动删除关联 Session 和 Message）
            versions = await self._version_repo.find_by(
                session,
                graph_id=entity_id,
            )
            if versions:
                version_ids = [v.id for v in versions]
                await self._version_service.delete_by_ids(
                    session,
                    version_ids,
                    commit=False  # 不立即提交
                )

            # 2. 删除工作区会话（通过 SessionService，会自动删除 Message）
            if graph.current_session_id:
                await self._session_service.delete_by_id(
                    session,
                    graph.current_session_id,
                    commit=False  # 不立即提交
                )

            # 3. 删除 Graph 记录
            result = await self._repository.delete_by_id(session, entity_id)

            if result and commit:
                await session.commit()

            return result
        except Exception as e:
            if commit:
                await session.rollback()
            raise

    async def patch_spec(
            self,
            session: AsyncSession,
            graph_id: str,
            patch_request: GraphSpecPatchRequest,
            commit: bool = True
    ) -> Optional[GraphTable]:
        """
        细粒度修改 GraphSpec
        - agents.update: 更新 Agent 配置（model, instruction, tools）
        - 修改后 current_version_id 设为 NULL（标记有未保存修改）
        """
        try:
            graph = await self._repository.find_by_id(session, graph_id)
            if not graph:
                raise ValueError(f"Graph {graph_id} not found")

            if not graph.current_spec:
                raise ValueError(f"Graph {graph_id} has no spec")

            # 解析当前 spec
            spec_dict = dict(graph.current_spec)


            if patch_request.agents and patch_request.agents.update:

                agents_list = spec_dict.get("agents", [])
                agent_index_map = {agent["name"]: i for i, agent in enumerate(agents_list)}

                for agent_name, patch in patch_request.agents.update.items():
                    if agent_name not in agent_index_map:
                        raise ValueError(f"Agent '{agent_name}' not found in spec")

                    idx = agent_index_map[agent_name]
                    patch_data = patch.model_dump(exclude_none=True)

                    # 合并更新
                    for key, value in patch_data.items():
                        agents_list[idx][key] = value

                spec_dict["agents"] = agents_list

            # 验证并更新
            validated_spec = self._validate_spec(spec_dict)
            update_data = {
                "current_spec": validated_spec,
                "current_version_id": None  # 标记有未保存修改
            }

            result = await self._repository.update_by_id(session, graph_id, update_data)

            if commit:
                await session.commit()
                if result:
                    await session.refresh(result)

            return result
        except Exception:
            if commit:
                await session.rollback()
            raise
