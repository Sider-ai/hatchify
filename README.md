# Hatchify

<div align="center">

**基于 AWS Strands SDK 的多智能体图执行平台**

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[English](README_EN.md) | 简体中文

---

🌐 **在线体验**: [https://hatchify.ai/](https://hatchify.ai/) - 无需安装，立即尝试 Vibe Graph！

---

</div>

## 📖 简介

Hatchify 是一个强大的多智能体工作流平台，通过动态图执行引擎实现复杂的 AI Agent 协作。它基于 FastAPI + AWS Strands SDK 构建，支持通过 JSON 配置动态创建和执行 Agent 工作流。

### 核心特性

- 🤖 **动态多智能体编排**: 通过 JSON 配置动态构建和执行 Agent 工作流
- 🔄 **智能路由系统**: 支持 Rules、JSONLogic、Router Agent、Orchestrator 等多种路由策略
- 🔌 **MCP 协议集成**: 原生支持 Model Context Protocol，轻松扩展工具能力
- 💬 **Web Builder**: 对话式 Web 应用生成，支持实时预览和部署（完善中）
- 📊 **事件驱动架构**: 基于 SSE 的实时事件流，完整追踪执行过程
- 🗄️ **版本管理**: Graph 规范的版本快照与回滚支持
- 🎯 **多模型支持**: 统一的 LLM 接口，支持 OpenAI、Gemini、Claude 等主流模型
- 🔐 **企业级架构**: 分层设计（API/Business/Repository），易于扩展和维护

## 🚀 快速开始

### 环境要求

- Python 3.13+
- SQLite / PostgreSQL (可选)
- Node.js 18+ (用于 Web Builder 功能)

### 安装

```bash
# 克隆仓库
git clone https://github.com/Sider-ai/hatchify.git
cd hatchify

# 安装依赖（推荐使用 uv）
uv sync
```

### 配置

1. **复制配置文件**
```bash
cp resources/example.mcp.toml resources/mcp.toml
cp resources/example.models.toml resources/models.toml
```

2. **编辑模型配置** (`resources/models.toml`)
```toml
[[models]]
name = "gpt-4o"
provider = "openai"
api_key = "your-api-key-here"
api_base = "https://api.openai.com/v1"
```

3. **编辑 MCP 服务器配置** (`resources/mcp.toml`)（可选）
```toml
[[servers]]
name = "filesystem"
transport = "stdio"
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/workspace"]
```

### 启动

```bash
# 开发模式
uvicorn hatchify.launch.launch:app --reload --host 0.0.0.0 --port 8000

# 或使用 main.py
python main.py
```

访问 http://localhost:8000/docs 查看 API 文档。

### Docker 部署

#### 1. 构建镜像

```bash
docker build -t hatchify .
```

#### 2. 启动容器

```bash
# 后台运行，映射端口并挂载数据目录
docker run -itd \
  --name=hatchify \
  -p 8000:8000 \
  -v ./data:/app/data \
  -v ./resources:/app/resources \
  hatchify
```

**参数说明：**
- `-p 8000:8000`: 将容器的 8000 端口映射到主机的 8000 端口
- `-v ./data:/app/data`: 挂载数据目录（包含数据库、存储、会话等）
- `-v ./resources:/app/resources`: 挂载配置文件目录（`mcp.toml`、`models.toml`、`development.yaml`）

#### 3. 查看日志

```bash
# 实时查看日志
docker logs -f hatchify

# 查看最近 100 行日志
docker logs --tail 100 hatchify
```

#### 4. 容器管理

```bash
# 停止容器
docker stop hatchify

# 启动容器
docker start hatchify

# 重启容器
docker restart hatchify

# 删除容器
docker rm -f hatchify
```

#### 5. 环境变量配置

可以通过环境变量覆盖配置：

```bash
docker run -itd \
  --name=hatchify \
  -p 8000:8000 \
  -e HATCHIFY__SERVER__BASE_URL=https://your-domain.com \
  -e HATCHIFY__SERVER__PORT=8000 \
  -v ./data:/app/data \
  -v ./resources:/app/resources \
  hatchify
```

**注意事项：**
- ⚠️ 生产部署时务必修改 `HATCHIFY__SERVER__BASE_URL` 为实际的外网地址
- 确保 `./data` 和 `./resources` 目录存在且有正确的权限
- 首次启动前需要先配置 `resources/mcp.toml` 和 `resources/models.toml`

## 📁 项目结构

```
Hatchify/
├── hatchify/                      # 主应用包
│   ├── business/                  # 业务层
│   │   ├── api/v1/               # RESTful API 路由
│   │   ├── db/                   # 数据库配置
│   │   ├── models/               # ORM 模型
│   │   ├── repositories/         # 数据访问层
│   │   └── services/             # 业务逻辑层
│   ├── common/                    # 共享层
│   │   ├── domain/               # 领域模型（Entity、Event）
│   │   ├── extensions/           # 扩展模块
│   │   └── settings/             # 配置管理
│   ├── core/                      # 核心引擎
│   │   ├── factory/              # 工厂模式（Agent、LLM、Tool）
│   │   ├── graph/                # 动态图构建系统
│   │   ├── manager/              # 管理器（MCP、Model、Tool）
│   │   ├── mcp/                  # MCP 协议集成
│   │   └── stream_handler/       # 事件流处理
│   └── launch/                    # 应用启动入口
├── resources/                     # 配置文件目录
│   ├── development.yaml          # 环境配置
│   ├── mcp.toml                  # MCP 服务器配置
│   └── models.toml               # 模型配置
└── main.py                        # 程序入口
```

## 🔥 核心功能

### 1. 💬 Vibe Graph - 自然语言驱动的工作流生成

通过自然语言交互，利用 LLM 的语义理解能力自动生成 GraphSpec 规范，实现从需求描述到可执行工作流的端到端转换。系统采用结构化输出机制，将用户意图解析为包含 Agent 节点、工具配置和路由策略的完整图定义。

**核心能力：**
- 🗣️ **语义解析**：基于 LLM 的意图理解，将自然语言需求映射为 GraphSpec 结构
- 🧠 **智能推断**：自动推断 Agent 角色定位、工具依赖关系和节点间路由逻辑
- 🔄 **对话式迭代**：支持多轮对话优化工作流结构，动态调整节点配置
- 📊 **自动编排**：根据任务特征自动选择 LLM 模型、分配工具集和配置路由策略

### 2. 🏗️ 灵活的 Graph 构建系统

Graph 由节点（Node）和边（Edge）组成，支持声明式定义复杂的多智能体协作流程。

**节点类型：**

**Agent 节点** - 基于 LLM 的智能节点
- **General Agent**：通用型 Agent，执行具体任务（如数据分析、内容生成）
- **Router Agent**：路由型 Agent，根据上游输出的结构化字段决定工作流跳转
- **Orchestrator Agent**：编排型 Agent，中心化协调所有节点，支持 `COMPLETE` 信号终止流程

每个 Agent 可配置：
- 动态模型选择（支持 OpenAI、Gemini、Claude 等）
- 工具集注册（MCP 工具、自定义本地工具）
- 结构化输出 Schema（用于路由决策和数据传递）

**Function 节点** - 确定性函数节点
- 使用 `@tool` 装饰器定义，作为 Graph 中的独立节点
- 接收上游 Agent 的结构化输出作为输入
- 执行确定性操作（如数据转换、格式化、计算）
- 必须返回 Pydantic BaseModel 类型，确保类型安全的数据传递
- 通过 `function_ref` 引用预注册的函数名

**工具与自定义扩展：**

**1. Agent 工具（供 Agent 调用）**
- **MCP 工具**：支持 Model Context Protocol 标准，动态加载外部工具服务器
  - 文件系统操作（`@modelcontextprotocol/server-filesystem`）
  - Git 操作（`@modelcontextprotocol/server-github`）
  - 数据库查询等
- **自定义本地工具**：使用 `@tool` 装饰器定义并注册到 `ToolRouter`
  ```python
  from strands import tool, ToolContext
  from hatchify.core.factory.tool_factory import ToolRouter

  tool_router = ToolRouter()

  @tool(name="add", description="Add two numbers", context=True)
  async def add(a: float, b: float, tool_context: ToolContext) -> float:
      return a + b

  tool_router.register(add)
  ```

**2. Function 节点（作为 Graph 节点）**
- 使用相同的 `@tool` 装饰器，但注册到 Function Router
- 必须定义 Pydantic 输出模型
  ```python
  from pydantic import BaseModel
  from strands import tool

  class EchoResult(BaseModel):
      text: str

  @tool(name="echo_function", description="Echo input")
  async def echo_function(text: str) -> EchoResult:
      return EchoResult(text=f"[ECHO] {text}")
  ```

### 3. ⚙️ 统一的配置管理

通过声明式配置文件管理模型和工具，支持多 Provider 和多传输协议。

**模型配置（`resources/models.toml`）**

支持多 Provider 配置，统一管理不同 LLM 服务商的模型：

```toml
default_provider = "openai-like"

[providers.openai]
id = "openai"
name = "OpenAI"
family = "openai"
base_url = "https://api.openai.com/v1"
api_key = "sk-xxx"
enabled = true
priority = 3  # 优先级，数字越小优先级越高

[[providers.openai.models]]
id = "gpt-4o"
name = "gpt-4o"
max_tokens = 16384
context_window = 128000
description = "..."

[providers.anthropic]
id = "anthropic"
family = "anthropic"
base_url = "https://api.anthropic.com"
api_key = "sk-ant-xxx"
enabled = true
priority = 4

[[providers.anthropic.models]]
id = "claude-sonnet-4-5-20250929"
max_tokens = 64000
context_window = 200000
```

**配置特性：**
- 支持多 Provider 同时配置（OpenAI、Anthropic、DeepSeek 等）
- `priority` 字段控制 Provider 回退顺序（数字越小优先级越高）
- 支持单独禁用某个模型（`enabled = false`）
- 兼容 OpenAI-Like 接口（适配第三方代理服务）

**MCP 工具配置（`resources/mcp.toml`）**

支持三种传输协议，动态加载外部工具服务器：

**1. Stdio 传输（本地进程）**
```toml
[[servers]]
name = "filesystem"
transport = "stdio"
enabled = true
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
prefix = "fs"  # 工具名前缀

# 可选配置
cwd = "/tmp"
encoding = "utf-8"

[servers.env]
NODE_ENV = "production"

[servers.tool_filters]
allowed = ["read_file", "write_file"]  # 白名单
```

**2. SSE 传输（Server-Sent Events）**
```toml
[[servers]]
name = "calculator-sse"
transport = "sse"
enabled = true
url = "http://localhost:8000/sse"
prefix = "calc"
timeout = 5
sse_read_timeout = 300

[servers.headers]
Authorization = "Bearer your-token"
```

**3. StreamableHTTP 传输**
```toml
[[servers]]
name = "weather-api"
transport = "streamablehttp"
enabled = true
url = "http://localhost:8001/mcp/"
prefix = "weather"
timeout = 30
terminate_on_close = true
```

**MCP 配置特性：**
- 支持三种传输协议（stdio / sse / streamablehttp）
- 工具过滤器（白名单 `allowed` / 黑名单 `rejected`）
- 工具名前缀（避免命名冲突）
- 动态启用/禁用服务器（`enabled` 字段）

### 4. 🎨 Web Builder - Vibe 建站 🚧

> **状态：正在实现中**
> 该功能目前处于开发阶段，部分功能可能尚未完善。

通过自然语言对话，让 AI 自动生成和定制 Web 应用，从需求描述到部署上线一站式完成。

**技术栈：**
- React 19 + TypeScript
- Vite 7（构建工具）
- Tailwind CSS 4（样式框架）
- React JSON Schema Form（动态表单生成）

**工作流程：**

1. **项目初始化**
   - 基于 Graph 的 `input_schema` 和 `output_schema` 自动生成 Web 项目
   - 生成表单页面（用于输入数据并触发 Webhook）
   - 生成结果展示页面（智能渲染 Graph 输出）

2. **对话式定制**
   - Agent 可调用工具对项目进行修改：
     - `file_read`：读取项目文件
     - `editor`：编辑代码文件
     - `file_write`：创建新文件
     - `shell`：Bash工具实现
   - 支持多轮对话，迭代优化界面设计和功能

3. **智能内容渲染**
   - 自动识别输出数据类型（图片、URL、结构化数据、列表等）
   - 防御性编程，兼容实际数据与 Schema 不一致的情况
   - 响应式设计，自适应各种设备尺寸

4. **一键部署**
   - 自动执行 `npm install` 和 `npm run build`
   - 将构建产物挂载到 `/preview/{graph_id}` 路径
   - 实时推送构建日志和进度
   - 支持热更新，修改后自动重新构建

**使用场景：**
- 为 Graph 工作流快速生成 Web 界面
- 无需前端开发经验，通过对话式交互定制界面
- 自动生成基于 JSON Schema 的动态表单
- 智能渲染各种类型的 Graph 输出结果

### 5. 🔧 环境配置系统

通过 `resources/development.yaml` 集中管理应用的所有运行时配置。

**核心配置项：**

**1. 服务器配置**
```yaml
hatchify:
  server:
    host: 0.0.0.0
    port: 8000
    base_url: http://localhost:8000  # ⚠️ 生产环境必须改为外网地址
```

⚠️ **重要提示**：`base_url` 是最关键的配置项
- 本地开发：`http://localhost:8000`
- 生产部署：必须修改为实际的外网地址（如 `https://your-domain.com`）
- 影响范围：Webhook 回调、Web Builder 项目的 API 地址、预览页面的资源加载

**2. 模型配置**
```yaml
models:
  spec_generator:      # Vibe Graph 生成器使用的模型
    model: claude-sonnet-4-5-20250929
    provider: anthropic
  schema_extractor:    # Schema 提取器使用的模型
    model: claude-sonnet-4-5-20250929
    provider: anthropic
  web_builder:         # Web Builder 使用的模型
    model: claude-sonnet-4-5-20250929
    provider: anthropic
```

**3. 数据库配置**
```yaml
db:
  platform: sqlite  # 当前仅支持: sqlite
  sqlite:
    driver: sqlite+aiosqlite
    file: ./data/dev.db
    echo: False
    pool_pre_ping: True
```

⚠️ **注意**：当前版本仅支持 SQLite，PostgreSQL 和 MySQL 支持将在未来版本中添加。

**4. 存储配置**
```yaml
storage:
  platform: opendal  # 当前仅支持: opendal
  opendal:
    schema: fs  # 支持: fs / s3 / oss 等（基于 OpenDAL）
    bucket: hatchify
    folder: dev
    root: ./data/storage
```

**5. 会话管理配置**
```yaml
session_manager:
  manager: file  # 当前仅支持: file
  file:
    folder: dev
    root: ./data/session
```

**6. Web Builder 配置**
```yaml
web_app_builder:
  repo_url: https://github.com/Sider-ai/hatchify-web-app-template.git
  branch: master
  workspace: ./data/workspace

  # 项目初始化时的环境变量注入
  init_steps:
    - type: env
      file: .env
      vars:
        VITE_API_BASE_URL: "{{base_url}}"  # 自动使用 server.base_url
        VITE_GRAPH_ID: "{{graph_id}}"
        VITE_BASE_PATH: "/preview/{{graph_id}}"

  # 安全配置
  security:
    allowed_directories:  # 白名单：允许 Agent 访问的目录
      - ./data/workspace
      - /tmp
    sensitive_paths:      # 黑名单：禁止访问的敏感路径
      - ~/.ssh
      - ~/.aws
      - /etc/passwd
      - /root
```

**环境变量覆盖：**

支持通过环境变量覆盖配置，使用 `HATCHIFY__` 前缀：

```bash
# 覆盖服务器端口
export HATCHIFY__SERVER__PORT=8080

# 覆盖 base_url（生产部署时使用）
export HATCHIFY__SERVER__BASE_URL=https://your-domain.com

# 覆盖数据库平台
export HATCHIFY__DB__PLATFORM=postgresql
```

**配置优先级：** 环境变量 > YAML 配置文件 > 默认值

### 6. 🏛️ 企业级分层架构

采用经典的三层架构设计（API → Service → Repository），通过泛型和依赖注入实现高内聚低耦合。

**架构层次：**

```
┌─────────────────────────────────────────────┐
│         API 层 (FastAPI Router)             │
│  - 路由定义、请求验证、响应序列化             │
│  - Depends 依赖注入                         │
└─────────────────┬───────────────────────────┘
                  │ 调用
┌─────────────────▼───────────────────────────┐
│         Service 层 (GenericService[T])      │
│  - 业务逻辑编排、事务管理                    │
│  - 跨 Repository 协调                       │
└─────────────────┬───────────────────────────┘
                  │ 使用
┌─────────────────▼───────────────────────────┐
│       Repository 层 (BaseRepository[T])     │
│  - 数据访问抽象、CRUD 操作                   │
│  - 查询构建、分页封装                        │
└─────────────────┬───────────────────────────┘
                  │ 操作
┌─────────────────▼───────────────────────────┐
│         数据库层 (SQLAlchemy ORM)           │
│  - ORM 模型、数据库连接                      │
└─────────────────────────────────────────────┘
```

**1. Repository 层 - 数据访问抽象**

**核心特性：**
- 泛型设计，类型安全
- 异步操作，高性能
- 统一的分页接口（基于 `fastapi-pagination`）
- 灵活的查询过滤（`find_by(**filters)`）

**2. Service 层 - 业务逻辑编排**

**核心特性：**
- 事务管理（自动 commit/rollback）
- 数据验证（基于 Pydantic）
- 跨 Repository 协调
- 业务逻辑复用

**3. API 层 - 路由与依赖注入**

**核心特性：**
- 依赖注入（`ServiceManager`、`RepositoryManager`）
- 统一响应格式（`Result[T]`）
- 自动参数验证（Pydantic）
- 统一异常处理


**架构优势：**
- 📦 **关注点分离**：每层职责清晰，易于维护
- 🔄 **可测试性**：每层可独立单元测试
- 🔌 **可扩展性**：通过泛型基类快速扩展新实体
- 🎯 **类型安全**：泛型 + Pydantic 保证类型正确性
- 🚀 **开发效率**：通用 CRUD 操作开箱即用


