#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/7/1
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : launch
# @Software: PyCharm
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.common.domain.result.result import Result
from app.common.settings.settings import get_hatchify_settings

hatchify_settings = get_hatchify_settings()


async def initialize_extensions():
    ...


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
    title="We0 API",
    description="API for We0",
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
    error = Result.failed(code=500, message=f"{type(exc).__name__}: {exc}")
    return JSONResponse(content=jsonable_encoder(error))


@app.get("/")
async def home():
    return JSONResponse(content={"msg": "welcome to Hatchify"})


@app.get("/health")
async def health():
    return JSONResponse(content={"status": "ok"})
