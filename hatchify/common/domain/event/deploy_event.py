from typing import Literal

from pydantic import BaseModel, Field


class ProgressEvent(BaseModel):
    """部署进度事件"""
    type: Literal["progress"] = Field(default="progress", exclude=True)
    stage: Literal["checking", "installing", "building", "deploying"]
    message: str


class LogEvent(BaseModel):
    """构建日志事件"""
    type: Literal["log"] = Field(default="log", exclude=True)
    content: str


class DeployResultEvent(BaseModel):
    """部署完成事件"""
    type: Literal["deploy_result"] = Field(default="deploy_result", exclude=True)
    preview_url: str
    message: str