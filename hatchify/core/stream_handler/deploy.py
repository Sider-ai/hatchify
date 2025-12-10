import asyncio
import os
from pathlib import Path
from typing import AsyncIterator, Dict, Any

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger
import shutil

from hatchify.common.domain.event.base_event import StreamEvent
from hatchify.common.domain.event.deploy_event import ProgressEvent, LogEvent, DeployResultEvent
from hatchify.core.stream_handler.stream_handler import BaseStreamHandler

# 全局状态：已挂载的项目
MOUNTED_GRAPHS: Dict[str, str] = {}  # {graph_id: dist_path}

# 常量定义
PACKAGE_JSON = "package.json"
NODE_MODULES = "node_modules"
DIST_DIR = "dist"
PREVIEW_PREFIX = "/preview"


class DeployGenerator(BaseStreamHandler):
    """部署流式处理器"""

    def __init__(
            self,
            source_id: str,
            graph_id: str,
            project_path: str,
            redeploy: bool = False,
    ):
        super().__init__(source_id=source_id, ping_interval=5)
        self.graph_id = graph_id
        self.project_path = project_path
        self.redeploy = redeploy

        # 预定义路径常量
        self.package_json_path = os.path.join(project_path, PACKAGE_JSON)
        self.node_modules_path = os.path.join(project_path, NODE_MODULES)
        self.dist_path = os.path.join(project_path, DIST_DIR)
        self.preview_url = f"{PREVIEW_PREFIX}/{graph_id}/"
        self.mount_path = f"{PREVIEW_PREFIX}/{graph_id}"

    async def handle_stream_event(self, event: Any):
        await self.emit_event(event)

    @staticmethod
    async def _run_command_with_logs(
            cmd: list[str],
            cwd: str,
            stage: str
    ) -> AsyncIterator[StreamEvent]:
        """执行命令并实时推送日志"""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        # 实时读取输出
        if process.stdout:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break

                log_line = line.decode().rstrip()
                if log_line:
                    yield StreamEvent(
                        type="log",
                        data=LogEvent(content=f"[{stage}] {log_line}")
                    )

        await process.wait()

        if process.returncode != 0:
            raise RuntimeError(f"{' '.join(cmd)} failed with code {process.returncode}")

    async def build_project(self) -> AsyncIterator[StreamEvent]:
        """构建项目的异步生成器"""

        # === 阶段 1: 检查项目 ===
        yield StreamEvent(
            type="progress",
            data=ProgressEvent(stage="checking", message="检查项目目录...")
        )

        if not os.path.exists(self.project_path):
            raise FileNotFoundError(f"项目目录不存在: {self.project_path}")

        if not os.path.exists(self.package_json_path):
            raise FileNotFoundError(f"{PACKAGE_JSON} 不存在: {self.package_json_path}")

        # === Redeploy: 清理旧构建 ===
        if self.redeploy:
            yield StreamEvent(
                type="progress",
                data=ProgressEvent(stage="checking", message="清理旧构建产物...")
            )

           

            if os.path.exists(self.node_modules_path):
                shutil.rmtree(self.node_modules_path)
                yield StreamEvent(
                    type="log",
                    data=LogEvent(content=f"已删除 {NODE_MODULES}/")
                )

            if os.path.exists(self.dist_path):
                shutil.rmtree(self.dist_path)
                yield StreamEvent(
                    type="log",
                    data=LogEvent(content=f"已删除 {DIST_DIR}/")
                )

            yield StreamEvent(
                type="progress",
                data=ProgressEvent(stage="checking", message="清理完成")
            )

        # === 阶段 2: 安装依赖 ===
        if not os.path.exists(self.node_modules_path):
            yield StreamEvent(
                type="progress",
                data=ProgressEvent(stage="installing", message="安装依赖 (npm install)...")
            )

            async for event in self._run_command_with_logs(
                    ["npm", "install"],
                    self.project_path,
                    "npm install"
            ):
                yield event

            yield StreamEvent(
                type="progress",
                data=ProgressEvent(stage="installing", message="依赖安装完成")
            )
        else:
            yield StreamEvent(
                type="progress",
                data=ProgressEvent(stage="installing", message="依赖已存在，跳过安装")
            )

        # === 阶段 3: 执行构建 ===
        yield StreamEvent(
            type="progress",
            data=ProgressEvent(stage="building", message="开始构建 (npm run build)...")
        )

        async for event in self._run_command_with_logs(
                ["npm", "run", "build"],
                self.project_path,
                "npm run build"
        ):
            yield event

        # 检查构建产物
        if not os.path.exists(self.dist_path):
            raise RuntimeError(f"构建完成但 {DIST_DIR}/ 目录不存在")

        yield StreamEvent(
            type="progress",
            data=ProgressEvent(stage="building", message="构建完成")
        )

        # === 阶段 4: 挂载静态文件 ===
        yield StreamEvent(
            type="progress",
            data=ProgressEvent(stage="deploying", message="部署静态资源...")
        )

        await self._mount_static_files()

        yield StreamEvent(
            type="progress",
            data=ProgressEvent(stage="deploying", message="部署完成")
        )

        # 返回最终结果
        yield StreamEvent(
            type="deploy_result",
            data=DeployResultEvent(
                preview_url=self.preview_url,
                message=f"应用已成功部署到 {self.preview_url}"
            )
        )

    async def _mount_static_files(self):
        from hatchify.launch.launch import app

        global MOUNTED_GRAPHS

        if self.graph_id in MOUNTED_GRAPHS:
            logger.info(f"Graph {self.graph_id} 已挂载，跳过")
            return

        try:
            app.mount(
                self.mount_path,
                StaticFiles(directory=self.dist_path, html=True),
                name=f"preview_{self.graph_id}"
            )

            MOUNTED_GRAPHS[self.graph_id] = self.dist_path
            logger.info(f"✅ 挂载成功: {self.mount_path} -> {self.dist_path}")

        except Exception as e:
            logger.error(f"挂载失败: {type(e).__name__}: {e}")
            raise

    async def submit_task(self):
        """提交部署任务"""
        async_generator = self.build_project()
        await self.run_streamed(async_generator)