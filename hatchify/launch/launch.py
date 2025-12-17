#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/7/1
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : launch
# @Software: PyCharm
import asyncio
from contextlib import asynccontextmanager

import litellm
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from hatchify.business.api.v1.execution_router import executions_router
from hatchify.business.api.v1.graph_router import graphs_router
from hatchify.business.api.v1.graph_version_router import graph_versions_router
from hatchify.business.api.v1.message_router import messages_router
from hatchify.business.api.v1.models_router import model_router
from hatchify.business.api.v1.opendal_router import opendal_router
from hatchify.business.api.v1.session_router import sessions_router
from hatchify.business.api.v1.tool_router import tool_router
from hatchify.business.api.v1.web_builder_router import web_builder_router
from hatchify.business.api.v1.web_hook_router import web_hook_router
from hatchify.business.db.session import init_db
from hatchify.business.middleware.preview_middleware import PreviewMiddleware
from hatchify.common.domain.enums.storage_type import StorageType
from hatchify.common.domain.result.result import Result
from hatchify.common.extensions.ext_storage import init_storage
from hatchify.common.settings.settings import get_hatchify_settings
from hatchify.core.manager.tool_manager import async_load_mcp_server, async_load_strands_tools, \
    async_load_pre_defined_tools

hatchify_settings = get_hatchify_settings()


async def initialize_extensions():
    litellm.modify_params = True

    await init_db()
    await asyncio.gather(
        async_load_mcp_server(),
        async_load_strands_tools(),
        async_load_pre_defined_tools(),
        init_storage(),
    )


async def close_extensions():
    ...


@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    try:
        await initialize_extensions()
        yield
    finally:
        await close_extensions()


app = FastAPI(
    title="Hatchify API",
    description="API for Hatchify",
    version="0.0.1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加预览中间件 - 在请求到达路由前处理挂载
app.add_middleware(PreviewMiddleware)


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    error = Result.error(code=500, message=f"{type(exc).__name__}: {exc}")
    return JSONResponse(content=jsonable_encoder(error))


@app.get("/")
async def home():
    return JSONResponse(content={"msg": "welcome to Hatchify"})


@app.get("/health")
async def health():
    return JSONResponse(content={"status": "ok"})


# 所有 API 路由都挂载到 /api 前缀下
app.include_router(web_hook_router, prefix="/api", tags=["webhooks"])
app.include_router(graphs_router, prefix="/api", tags=["graphs"])
app.include_router(graph_versions_router, prefix="/api", tags=["graph_versions"])
app.include_router(messages_router, prefix="/api", tags=["messages"])
app.include_router(sessions_router, prefix="/api", tags=["sessions"])
app.include_router(web_builder_router, prefix="/api", tags=["web_builder"])
app.include_router(tool_router, prefix="/api", tags=["tools"])
app.include_router(model_router, prefix="/api", tags=["models"])
app.include_router(executions_router, prefix="/api", tags=["executions"])

# 挂载 OpenDAL 文件访问路由（用于提供存储文件的 HTTP 访问）
if hatchify_settings.storage.platform == StorageType.LOCAL:
    app.include_router(opendal_router, tags=["opendal"])
