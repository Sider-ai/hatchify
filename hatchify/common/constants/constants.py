import os


class Constants:
    class Path:
        RootPath: str = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        AppPath: str = os.path.join(RootPath, "app")
        ResourcesPath: str = os.path.join(RootPath, "resources")
        ModelPath: str = os.path.join(ResourcesPath, "models.toml")
        McpToml: str = os.path.join(ResourcesPath, "mcp.toml")
        ToolsToml: str = os.path.join(ResourcesPath, "tools.toml")
        EnvPath: str = os.path.join(ResourcesPath, ".env")

        @classmethod
        def get_yaml_path(cls, environment: str) -> str:
            return os.path.join(cls.ResourcesPath, f"{environment}.yaml")

    class WebBuilder:
        """Web Builder 相关常量"""
        PACKAGE_JSON = "package.json"
        NODE_MODULES = "node_modules"
        DIST_DIR = "dist"
        PREVIEW_PREFIX = "/preview"
