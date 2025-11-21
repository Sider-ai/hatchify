from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ToolFilterConfig(BaseModel):
    allowed: Optional[List[str]] = Field(
        default=None, description="白名单: 只加载这些工具 (支持正则表达式,以 'regex:' 开头)"
    )
    rejected: Optional[List[str]] = Field(
        default=None, description="黑名单: 排除这些工具 (支持正则表达式,以 'regex:' 开头)"
    )

    @field_validator("allowed", "rejected")
    @classmethod
    def validate_filters(cls, v):
        """验证不能同时使用 allowed 和 rejected"""
        return v


class MCPServerCard(BaseModel):
    """MCP 服务器配置卡片"""

    name: str = Field(..., description="服务器唯一标识")
    transport: Literal["stdio", "sse", "streamablehttp"] = Field(
        ..., description="连接类型"
    )
    startup_timeout: Optional[int] = Field(default=None, description="启动时间")
    enabled: bool = Field(default=True, description="是否启用")
    prefix: Optional[str] = Field(default=None, description="工具名称前缀")
    description: Optional[str] = Field(default=None, description="服务器描述")

    # Stdio 类型参数
    command: Optional[str] = Field(default=None, description="启动命令 (stdio)")
    args: Optional[List[str]] = Field(default=None, description="命令参数 (stdio)")
    env: Optional[Dict[str, str]] = Field(default=None, description="环境变量 (stdio)")
    cwd: Optional[str] = Field(default=None, description="工作目录 (stdio)")
    encoding: Optional[str] = Field(default=None, description="编码格式 (stdio)")
    encoding_error_handler: Optional[Literal["strict", "ignore", "replace"]] = Field(
        default=None, description="编码错误处理 (stdio)"
    )

    # SSE 和 StreamableHTTP 类型参数
    url: Optional[str] = Field(default=None, description="服务器地址 (sse/streamablehttp)")
    headers: Optional[Dict[str, str]] = Field(
        default=None, description="HTTP headers (sse/streamablehttp)"
    )
    timeout: Optional[float] = Field(default=None, description="连接超时秒数")
    sse_read_timeout: Optional[float] = Field(
        default=None, description="SSE 读取超时秒数"
    )

    # StreamableHTTP 专用参数
    terminate_on_close: Optional[bool] = Field(
        default=None, description="关闭时终止连接 (streamablehttp)"
    )

    # 工具过滤器
    tool_filters: Optional[ToolFilterConfig] = Field(
        default=None, description="工具过滤配置"
    )

    def model_post_init(self, __context):
        if self.transport == "stdio":
            if not self.command:
                raise ValueError(
                    f"Server '{self.name}': stdio type requires 'command' parameter"
                )

        elif self.transport in ["sse", "streamablehttp"]:
            if not self.url:
                raise ValueError(
                    f"Server '{self.name}': {self.transport} type requires 'url' parameter"
                )
        if self.tool_filters:
            if self.tool_filters.allowed and self.tool_filters.rejected:
                raise ValueError(
                    f"Server '{self.name}': tool_filters cannot have both 'allowed' and 'rejected'"
                )
