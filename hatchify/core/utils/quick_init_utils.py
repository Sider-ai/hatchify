import asyncio
import json
from pathlib import Path
from typing import Dict, Any

import aiofiles

from hatchify.common.domain.entity.init_context import InitContext
from hatchify.common.settings.settings import get_hatchify_settings

settings = get_hatchify_settings()


def replace_placeholders(text: str, placeholders: Dict[str, Any]) -> str:
    """替换文本中的 {{placeholder}} 占位符"""
    result = text
    for key, value in placeholders.items():
        pattern = f"{{{{{key}}}}}"
        result = result.replace(pattern, str(value))
    return result


def get_repository_path(graph_id: str) -> Path:
    return Path(settings.web_app_builder.workspace) / graph_id


async def quick_clone_repository(graph_id: str) -> Path:
    """克隆仓库到 workspace/graph_id 目录"""
    target_dir = get_repository_path(graph_id)
    process = await asyncio.subprocess.create_subprocess_exec(
        "git", "clone", "-b",
        settings.web_app_builder.branch,
        settings.web_app_builder.repo_url,
        target_dir,
        stderr=asyncio.subprocess.PIPE,
    )

    _, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"Git clone failed: {stderr.decode().strip()}")

    return target_dir


async def quick_init(project_path: Path, ctx: InitContext):
    """
    根据配置初始化项目
    
    Args:
        project_path: 项目根目录（克隆后的目录）
        ctx: 初始化上下文，包含占位符值和 schemas
    """

    for step in settings.web_app_builder.init_steps:
        target_file = project_path / step.file if step.file else None

        match step.type:
            case "env":
                placeholders = {
                    "base_url": ctx.base_url,
                    "graph_id": ctx.graph_id,
                    "graph_input_format": ctx.graph_input_format,
                }
                env_content = "\n".join(
                    f"{key}={replace_placeholders(str(value), placeholders)}"
                    for key, value in step.vars.items()
                )
                async with aiofiles.open(target_file, mode="w") as f:
                    await f.write(env_content)

            case "write_input_schema":
                async with aiofiles.open(target_file, mode="w") as f:
                    await f.write(json.dumps(ctx.input_schema, indent=2))

            case "write_output_schema":
                async with aiofiles.open(target_file, mode="w") as f:
                    await f.write(json.dumps(ctx.output_schema, indent=2))

            case _:
                raise TypeError(f"Unknown step type: {step.type}")


async def sync_web_project(graph_id: str, ctx: InitContext) -> Path:
    """
    同步 Web 项目：
    - 如果不存在，克隆并初始化
    - 如果存在，只更新配置文件（不覆盖 LLM 修改的代码）

    Args:
        graph_id: Graph ID
        ctx: 初始化上下文

    Returns:
        项目路径
    """
    project_path = get_repository_path(graph_id)

    if not project_path.exists():
        # 首次创建：克隆模板
        await quick_clone_repository(graph_id)

    # 更新配置文件（.env, schemas）
    await quick_init(project_path, ctx)

    return project_path


async def main():
    graph_id = "test"
    init_ctx = InitContext(
        base_url=settings.server.base_url,
        repo_url=settings.web_app_builder.repo_url,
        graph_id=graph_id,
        graph_input_format="multipart/form-data",
        input_schema={
            "type": "object",
            "properties": {
                "paper_pdf": {
                    "type": "string",
                    "format": "data-url",
                    "description": "The academic paper in PDF format to be analyzed."
                }
            },
            "required": [
                "paper_pdf"
            ]
        },
        output_schema={
            "type": "object",
            "properties": {
                "Report_Generator": {
                    "type": "object",
                    "properties": {
                        "final_report": {
                            "type": "string",
                            "description": "The complete, comprehensive analysis report in well-structured Markdown format, in Chinese."
                        }
                    },
                    "required": [
                        "final_report"
                    ]
                }
            },
            "required": [
                "Report_Generator"
            ],
            "description": "Workflow output from 1 terminal node(s)"
        }
    )
    path = await quick_clone_repository(graph_id)
    await quick_init(path, init_ctx)


if __name__ == '__main__':
    asyncio.run(main())
