from typing import Optional

from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from hatchify.core.manager.stream_manager import StreamManager


async def create_sse_response(
        execution_id: str,
        last_event_id: Optional[str] = None,
        latest_event_id: Optional[str] = None,
) -> StreamingResponse:
    """
    创建 SSE 流式响应

    Args:
        execution_id: 执行 ID
        last_event_id: SSE 重连时的最后一个事件 ID（从 Header）
        latest_event_id: SSE 重连时的最后一个事件 ID（从 Query，优先级更高）

    Returns:
        StreamingResponse: SSE 流式响应

    Raises:
        HTTPException: 如果 execution 不存在或流式处理出错
    """
    # 获取 executor
    executor = await StreamManager.get(execution_id)
    if not executor:
        raise HTTPException(
            status_code=404,
            detail=f"Execution '{execution_id}' not found. It may have expired or been cleaned up."
        )

    # 确定有效的 last_event_id（优先使用 query 参数）
    effective_last_id = latest_event_id or last_event_id

    # 创建 SSE 响应
    try:
        return StreamingResponse(
            executor.worker(last_event_id=effective_last_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        logger.error(f"Stream error for execution {execution_id}: {msg}")
        raise HTTPException(status_code=500, detail=msg)