#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/7/1
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : launch
# @Software: PyCharm
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from hatchify.business.api.v1.graph_router import graphs_router
from hatchify.business.api.v1.graph_version_router import graph_versions_router
from hatchify.business.api.v1.message_router import messages_router
from hatchify.business.api.v1.session_router import sessions_router
from hatchify.business.api.v1.tool_router import tool_router
from hatchify.business.api.v1.web_builder_router import web_builder_router
from hatchify.business.api.v1.web_hook_router import web_hook_router
from hatchify.business.db.session import init_db
from hatchify.common.domain.result.result import Result
from hatchify.common.extensions.ext_storage import init_storage
from hatchify.common.settings.settings import get_hatchify_settings
from hatchify.core.manager.tool_manager import async_load_mcp_server, async_load_strands_tools

hatchify_settings = get_hatchify_settings()


async def initialize_extensions():
    await init_db()

    await asyncio.gather(
        async_load_mcp_server(),
        async_load_strands_tools(),
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
    root_path="/api",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


app.include_router(web_hook_router, tags=["webhooks"])
app.include_router(graphs_router, tags=["graphs"])
app.include_router(graph_versions_router, tags=["graph_versions"])
app.include_router(messages_router, tags=["messages"])
app.include_router(sessions_router, tags=["graphs"])
app.include_router(web_builder_router, tags=["web_builder"])
app.include_router(tool_router, tags=["tools"])
