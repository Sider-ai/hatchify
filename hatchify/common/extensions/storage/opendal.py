#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/12
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : opendal_storage
# @Software: PyCharm
from pathlib import Path
from typing import AsyncGenerator

import aiofiles
import opendal
from loguru import logger

from hatchify.common.extensions.storage.base_storage import BaseStorage
from hatchify.common.settings.settings import get_hatchify_settings

settings = get_hatchify_settings()


class OpenDalStorage(BaseStorage):

    def __init__(self):
        self.bucket_name = settings.storage.opendal.bucket
        self.folder = settings.storage.opendal.folder
        self.client = self.get_client()

    def get_client(self, **kwargs):
        if settings.storage.opendal.opendal_schema == "fs":
            root = settings.storage.opendal.root or 'global_storage'
            Path(root).mkdir(parents=True, exist_ok=True)
            kwargs.update({
                "root": root
            })
        op = opendal.AsyncOperator(scheme=settings.storage.opendal.opendal_schema, **kwargs)

        retry_layer = opendal.layers.RetryLayer(max_times=3, factor=2.0, jitter=True)
        mime_layer = opendal.layers.MimeGuessLayer()
        return op.layer(retry_layer).layer(mime_layer)

    async def save(self, key, data, mimetype='application/octet-stream'):
        oss_key = self.__wrapper_folder_key(key)
        async with await self.client.open(path=oss_key, mode="wb", content_type=mimetype) as file:
            await file.write(data)

    async def upload_file(self, key, path, mimetype='application/octet-stream'):
        async with aiofiles.open(path, mode='rb') as f:
            await self.save(key, await f.read(), mimetype=mimetype)

    async def load_once(self, key: str) -> bytes:
        oss_key = self.__wrapper_folder_key(key)
        if not await self.exists(key):
            raise FileNotFoundError("File not found")
        content: bytes = await self.client.read(path=oss_key)
        return content

    async def load_stream(self, key: str, chunk_size: int = 40960) -> AsyncGenerator[bytes, None]:
        oss_key = self.__wrapper_folder_key(key)
        if not await self.exists(key):
            raise FileNotFoundError("File not found")

        async def generate() -> AsyncGenerator[bytes, None]:
            async with await self.client.open(path=oss_key, mode="rb") as file:
                while chunk := await file.read(chunk_size):
                    yield chunk

        return generate()

    async def download(self, key, target_filepath):
        oss_key = self.__wrapper_folder_key(key)
        if not await self.exists(key):
            raise FileNotFoundError("File not found")
        async with aiofiles.open(target_filepath, 'wb') as f:
            await f.write(await self.client.read(path=oss_key))

    async def exists(self, key):
        oss_key = self.__wrapper_folder_key(key)
        try:
            metadata = await self.client.stat(path=oss_key)
            return metadata.mode.is_file()
        except Exception as e:
            logger.error(e)
            return False

    async def delete(self, key):
        oss_key = self.__wrapper_folder_key(key)
        if await self.exists(key):
            await self.client.delete(path=oss_key)
            return True
        else:
            return False

    async def get_pre_signed_url(self, key: str, expires_in: int = 3600) -> str:
        oss_key = self.__wrapper_folder_key(key)
        logger.warning(
            "OpenDAL backend lacks pre-sign capability. "
            "Falling back to public URL construction. (Recommended for Dev Only)"
        )
        return f"{settings.server.base_url.rstrip('/')}/opendal/{oss_key.lstrip('/')}"

    async def stat(self, key: str):
        """获取文件元数据"""
        oss_key = self.__wrapper_folder_key(key)
        try:
            return await self.client.stat(path=oss_key)
        except Exception as e:
            logger.error(e)
            raise FileNotFoundError("File not found")

    def __wrapper_folder_key(self, key: str) -> str:
        wrapper_bucket_key = f'{self.bucket_name}/{key}'
        return f"{self.folder.strip('/')}/{wrapper_bucket_key.strip('/')}" if self.folder else wrapper_bucket_key
