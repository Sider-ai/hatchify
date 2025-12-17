#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import cast

from fastapi import APIRouter, HTTPException
from loguru import logger
from opendal import AsyncOperator
from starlette.responses import StreamingResponse

from hatchify.common.domain.enums.storage_type import StorageType
from hatchify.common.extensions.ext_storage import storage_client
from hatchify.common.settings.settings import get_hatchify_settings

opendal_router = APIRouter(prefix="/opendal")
settings = get_hatchify_settings()


@opendal_router.get("/{file_path:path}")
async def get_opendal_file(file_path: str):
    """
    通过 OpenDAL 获取文件

    注意：file_path 已经是完整的存储路径（wrapped），直接使用底层 client 访问
    """
    try:
        if settings.storage.platform != StorageType.LOCAL:
            raise HTTPException(status_code=404, detail=f"File '{file_path}' not found")

        client = cast(AsyncOperator, storage_client.client)

        metadata = await client.stat(path=file_path)
        if not metadata.mode.is_file():
            raise HTTPException(status_code=404, detail=f"File '{file_path}' not found")

        content_type = metadata.content_type or "application/octet-stream"

        async def file_stream():
            async with await client.open(path=file_path, mode="rb") as file:
                while chunk := await file.read(40960):
                    yield chunk

        return StreamingResponse(
            file_stream(),
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=3600",
            }
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{file_path}' not found")
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        logger.error(msg)
        raise HTTPException(status_code=500, detail=msg)
