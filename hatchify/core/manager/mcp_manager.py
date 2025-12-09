#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel

from hatchify.common.constants.constants import Constants
from hatchify.common.domain.entity.mcp_card import MCPServerCard


class MCPManager(BaseModel):
    servers: Dict[str, MCPServerCard]

    def model_post_init(self, __context):
        enabled_servers = [s for s in self.servers.values() if s.enabled]
        if not enabled_servers:
            pass

    def get_server(self, name: str) -> Optional[MCPServerCard]:
        server = self.servers.get(name)
        if not server:
            raise KeyError(f"MCP server '{name}' not found")
        return server

    def get_enabled_servers(self) -> List[MCPServerCard]:
        return [server for server in self.servers.values() if server.enabled]

    def get_servers_by_type(
            self, server_type: str, enabled_only: bool = True
    ) -> List[MCPServerCard]:
        servers = [s for s in self.servers.values() if s.transport == server_type]
        if enabled_only:
            servers = [s for s in servers if s.enabled]
        return servers

    @classmethod
    def parse_toml(cls, path: str | Path) -> MCPManager:
        data = tomllib.loads(Path(path).read_text())
        servers_list = data.get("servers", [])
        servers_dict = {server["name"]: server for server in servers_list}

        return cls(servers=servers_dict)


mcp_manager: MCPManager = MCPManager.parse_toml(Constants.Path.McpToml)
