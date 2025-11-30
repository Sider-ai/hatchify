import mimetypes
from typing import Optional, cast, List, get_args, Sequence, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from strands.types.content import ContentBlock, Messages, Message
from strands.types.media import DocumentFormat, VideoFormat, ImageFormat, DocumentContent, ImageContent, VideoContent

from app.business.db.session import transaction
from app.business.manager.repository_manager import RepositoryManager
from app.business.models.graph import GraphTable
from app.business.models.graph_version import GraphVersionTable
from app.business.models.messages import MessageTable
from app.business.models.session import SessionTable
from app.business.repositories.graph_repository import GraphRepository
from app.business.repositories.graph_version_repository import GraphVersionRepository
from app.business.repositories.message_repository import MessageRepository
from app.business.repositories.session_repository import SessionRepository
from app.business.services.base.generic_service import GenericService
from app.common.domain.entity.graph_spec import GraphSpec
from app.common.domain.enums.graph_version_type import GraphVersionType
from app.core.graph.dynamic_graph_builder import DynamicGraphBuilder
from app.core.manager.function_manager import function_router
from app.core.manager.tool_manager import tool_factory

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
        if not graph_obj or not graph_obj.current_spec:
            return None
        return GraphSpec.model_validate(graph_obj.current_spec)

    async def _create_draft_snapshot(
            self,
            session: AsyncSession,
            graph: GraphTable,
            comment: Optional[str] = None,
            session_id: Optional[str] = None,
            message_id: Optional[str] = None,
            parent_version_id: Optional[int] = None,
    ) -> GraphVersionTable:
        """
        为 Graph 创建草稿快照（最多保留 3 条，超出则删除最早的）
        - 可选复制来源会话历史，生成分支会话，写入 branch_session_id
        """
        drafts = await self._version_repo.list_drafts_by_graph(session, graph.id)
        while len(drafts) >= 3:
            oldest = drafts.pop(0)
            await self._version_repo.delete_by_id(session, oldest.id)

        # 复制来源会话历史（如果有）
        branched_session = await self._fork_session_with_messages(
            session=session,
            graph_id=graph.id,
            source_session_id=session_id,
            source_message_id=message_id,
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
            source_message_id: Optional[str],
    ) -> Optional[SessionTable]:
        """
        基于来源会话复制消息，生成新的分支会话。
        - 如果未提供 source_session_id，则取该 graph 最新的会话
        - 如果提供 source_message_id，则只复制该消息及之前的消息
        """
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

        new_session = SessionTable(
            graph_id=graph_id,
            parent_session_id=resolved_session_id,
            fork_from_message_id=source_message_id,
        )
        await self._session_repo.save(session, new_session)
        await session.flush()

        if messages_to_copy:
            clones = [
                MessageTable(
                    session_id=new_session.id,
                    role=msg.role,
                    content=msg.content,
                    token_usage=msg.token_usage,
                    meta_data=msg.meta_data,
                )
                for msg in messages_to_copy
            ]
            await self._message_repo.save_all(session, clones)
            await session.flush()

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
            session_id: Optional[str] = None,
            message_id: Optional[str] = None,
            comment: Optional[str] = None,
            parent_version_id: Optional[int] = None,
    ) -> GraphVersionTable:
        """
        为 Graph 创建快照版本
        1. 读取 Graph.current_spec（加锁）
        2. 计算新的 version 号（max(version) + 1）
        3. 创建 GraphVersion
        4. 更新 Graph.current_version_id

        使用悲观锁防止并发创建相同版本号
        """
        # 1. 获取 Graph（加悲观锁）
        async with transaction(session):

            graph = await self._repository.get_by_id_with_lock(session, graph_id)
            if not graph:
                raise ValueError(f"Graph {graph_id} not found")

            # 1.1 确定来源 session（若未传入则取最新会话）
            source_session_id = session_id
            if not source_session_id:
                sessions = await self._session_repo.find_by(
                    session,
                    graph_id=graph_id,
                    limit=1,
                    sort="created_at:desc",
                )
                source_session_id = sessions[0].id if sessions else None

            # 2. 计算新的 version 号
            max_version = await self._version_repo.get_max_version_by_graph(
                session, graph_id
            )
            new_version_no = (max_version or 0) + 1

            # 3. 创建分支会话（复制来源历史）
            branched_session = await self._fork_session_with_messages(
                session=session,
                graph_id=graph_id,
                source_session_id=source_session_id,
                source_message_id=message_id,
            )
            branch_session_id = branched_session.id if branched_session else None

            # 4. 创建 GraphVersion
            new_graph_version = GraphVersionTable(
                graph_id=graph_id,
                type=GraphVersionType.SNAPSHOT,
                version=new_version_no,
                spec=graph.current_spec,
                parent_version_id=parent_version_id,
                branch_session_id=branch_session_id,
                comment=comment,
            )
            await self._version_repo.save(session, new_graph_version)
            await session.flush()

            # 5. 更新 Graph.current_version_id
            await self._repository.update_by_id(
                session,
                graph_id,
                {"current_version_id": new_graph_version.id}
            )
            await session.refresh(new_graph_version)
            return new_graph_version

    async def rollback_to_version(
            self,
            session: AsyncSession,
            graph_id: str,
            version_id: int,
    ) -> Tuple[GraphTable, Optional[str]]:
        """
        回滚到指定版本
        1. 读取指定 version 的 spec
        2. 更新 Graph.current_spec = 该版本的 spec
        3. 更新 Graph.current_version_id = version_id
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

            # 2. 更新 Graph
            update_data = {
                "current_spec": target_version.spec,
                "current_version_id": version_id,
            }
            result = await self._repository.update_by_id(session, graph_id, update_data)

            if not result:
                raise ValueError(f"Failed to rollback Graph {graph_id}")

            await session.refresh(result)
            return result, target_version.branch_session_id
