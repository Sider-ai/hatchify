"""
GraphExecutor 管理器

用于管理多个 GraphExecutor 实例，支持：
- 创建和注册 executor
- 通过 graph_id 获取 executor
- 清理完成的 executor
"""
import asyncio
from typing import Dict, Optional

from loguru import logger

from app.core.graph.stream_handler import BaseStreamHandler


class StreamManager:
    """
    全局 Stream handler 管理器（单例模式）

    管理所有活跃的 GraphExecutor 实例
    """

    # 类级别存储
    _executors: Dict[str, BaseStreamHandler] = {}
    _lock = asyncio.Lock()

    @classmethod
    async def create(
            cls,
            task_id: str,
            handler: BaseStreamHandler
    ) -> BaseStreamHandler:
        """创建并注册流式 handler"""
        async with cls._lock:
            if task_id in cls._executors:
                raise ValueError(f"Handler with task_id '{task_id}' already exists")

            cls._executors[task_id] = handler
            logger.info(f"Created stream handler: {task_id}")
            return handler

    @classmethod
    async def get(cls, task_id: str) -> Optional[BaseStreamHandler]:
        """获取流式 handler"""
        async with cls._lock:
            return cls._executors.get(task_id)

    @classmethod
    async def get_or_raise(cls, task_id: str) -> BaseStreamHandler:
        """获取流式 handler，不存在抛错"""
        handler = await cls.get(task_id)
        if not handler:
            raise ValueError(f"Handler with task_id '{task_id}' not found")
        return handler

    @classmethod
    async def delete(cls, task_id: str) -> bool:
        """删除流式 handler"""
        async with cls._lock:
            if task_id in cls._executors:
                del cls._executors[task_id]
                logger.info(f"Deleted stream handler: {task_id}")
                return True
            return False

    @classmethod
    async def exists(cls, task_id: str) -> bool:
        """检查 handler 是否存在"""
        async with cls._lock:
            return task_id in cls._executors

    @classmethod
    async def get_all_ids(cls) -> list[str]:
        """获取所有活跃的 task_id"""
        async with cls._lock:
            return list(cls._executors.keys())

    @classmethod
    async def count(cls) -> int:
        """获取活跃的 handler 数量"""
        async with cls._lock:
            return len(cls._executors)

    @classmethod
    async def clear(cls):
        """清空所有 handler（谨慎使用）"""
        async with cls._lock:
            count = len(cls._executors)
            cls._executors.clear()
            logger.warning(f"Cleared all {count} stream handlers")
