# Hatchify

<div align="center">

**Multi-Agent Graph Execution Platform Based on AWS Strands SDK**

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

English | [简体中文](README.md)

---

🌐 **Live Demo**: [https://hatchify.ai/](https://hatchify.ai/) - Try Vibe Graph instantly without installation!

---

</div>

## 📖 Introduction

Hatchify is a powerful multi-agent workflow platform that enables complex AI Agent collaboration through a dynamic graph execution engine. Built on FastAPI + AWS Strands SDK, it supports dynamic creation and execution of Agent workflows via JSON configuration.

### Core Features

- 🤖 **Dynamic Multi-Agent Orchestration**: Build and execute Agent workflows dynamically through JSON configuration
- 🔄 **Intelligent Routing System**: Support for multiple routing strategies including Rules, JSONLogic, Router Agent, and Orchestrator
- 🔌 **MCP Protocol Integration**: Native support for Model Context Protocol, easily extend tool capabilities
- 💬 **Web Builder**: Conversational web application generation with real-time preview and deployment (in progress)
- 📊 **Event-Driven Architecture**: Real-time event streaming based on SSE, complete execution tracking
- 🗄️ **Version Management**: Version snapshots and rollback support for Graph specifications
- 🎯 **Multi-Model Support**: Unified LLM interface supporting OpenAI, Gemini, Claude, and other mainstream models
- 🔐 **Enterprise Architecture**: Layered design (API/Business/Repository), easy to extend and maintain

## 🚀 Quick Start

### Requirements

- Python 3.13+
- SQLite / PostgreSQL (optional)
- Node.js 18+ (for Web Builder functionality)

### Installation

```bash
# Clone repository
git clone https://github.com/Sider-ai/hatchify.git
cd hatchify

# Install dependencies (recommended using uv)
uv sync
```

### Configuration

1. **Copy configuration files**
```bash
cp resources/example.mcp.toml resources/mcp.toml
cp resources/example.models.toml resources/models.toml
```

2. **Edit model configuration** (`resources/models.toml`)
```toml
[[models]]
name = "gpt-4o"
provider = "openai"
api_key = "your-api-key-here"
api_base = "https://api.openai.com/v1"
```

3. **Edit MCP server configuration** (`resources/mcp.toml`) (optional)
```toml
[[servers]]
name = "filesystem"
transport = "stdio"
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/workspace"]
```

### Launch

```bash
# Development mode
uvicorn hatchify.launch.launch:app --reload --host 0.0.0.0 --port 8000

# Or use main.py
python main.py
```

Visit http://localhost:8000/docs to view API documentation.

### Docker Deployment

#### 1. Build Image

```bash
docker build -t hatchify .
```

#### 2. Start Container

```bash
# Run in background with port mapping and volume mounting
docker run -itd \
  --name=hatchify \
  -p 8000:8000 \
  -v ./data:/app/data \
  -v ./resources:/app/resources \
  hatchify
```

**Parameter Explanation:**
- `-p 8000:8000`: Map container port 8000 to host port 8000
- `-v ./data:/app/data`: Mount data directory (including database, storage, sessions, etc.)
- `-v ./resources:/app/resources`: Mount configuration directory (`mcp.toml`, `models.toml`, `development.yaml`)

#### 3. View Logs

```bash
# Real-time log viewing
docker logs -f hatchify

# View last 100 lines
docker logs --tail 100 hatchify
```

#### 4. Container Management

```bash
# Stop container
docker stop hatchify

# Start container
docker start hatchify

# Restart container
docker restart hatchify

# Remove container
docker rm -f hatchify
```

#### 5. Environment Variable Configuration

Override configuration with environment variables:

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

**Important Notes:**
- ⚠️ For production deployment, make sure to modify `HATCHIFY__SERVER__BASE_URL` to the actual public URL
- Ensure `./data` and `./resources` directories exist with proper permissions
- Configure `resources/mcp.toml` and `resources/models.toml` before first startup

## 📁 Project Structure

```
Hatchify/
├── hatchify/                      # Main application package
│   ├── business/                  # Business layer
│   │   ├── api/v1/               # RESTful API routes
│   │   ├── db/                   # Database configuration
│   │   ├── models/               # ORM models
│   │   ├── repositories/         # Data access layer
│   │   └── services/             # Business logic layer
│   ├── common/                    # Shared layer
│   │   ├── domain/               # Domain models (Entity, Event)
│   │   ├── extensions/           # Extension modules
│   │   └── settings/             # Configuration management
│   ├── core/                      # Core engine
│   │   ├── factory/              # Factory pattern (Agent, LLM, Tool)
│   │   ├── graph/                # Dynamic graph building system
│   │   ├── manager/              # Managers (MCP, Model, Tool)
│   │   ├── mcp/                  # MCP protocol integration
│   │   └── stream_handler/       # Event stream processing
│   └── launch/                    # Application entry point
├── resources/                     # Configuration directory
│   ├── development.yaml          # Environment configuration
│   ├── mcp.toml                  # MCP server configuration
│   └── models.toml               # Model configuration
└── main.py                        # Program entry point
```

## 🔥 Core Features

### 1. 💬 Vibe Graph - Natural Language-Driven Workflow Generation

Through natural language interaction, leveraging LLM's semantic understanding to automatically generate GraphSpec specifications, enabling end-to-end conversion from requirement descriptions to executable workflows. The system uses structured output mechanisms to parse user intent into complete graph definitions containing Agent nodes, tool configurations, and routing strategies.

**Core Capabilities:**
- 🗣️ **Semantic Parsing**: LLM-based intent understanding, mapping natural language requirements to GraphSpec structure
- 🧠 **Intelligent Inference**: Auto-infer Agent role positioning, tool dependencies, and inter-node routing logic
- 🔄 **Conversational Iteration**: Support multi-turn dialogue for workflow structure optimization and dynamic node configuration
- 📊 **Auto-Orchestration**: Automatically select LLM models, assign tool sets, and configure routing strategies based on task characteristics

### 2. 🏗️ Flexible Graph Building System

Graphs consist of nodes and edges, supporting declarative definition of complex multi-agent collaboration processes.

**Node Types:**

**Agent Nodes** - LLM-based intelligent nodes
- **General Agent**: General-purpose Agent executing specific tasks (e.g., data analysis, content generation)
- **Router Agent**: Routing Agent determining workflow jumps based on upstream structured output fields
- **Orchestrator Agent**: Orchestration Agent centrally coordinating all nodes, supporting `COMPLETE` signal for process termination

Each Agent can be configured with:
- Dynamic model selection (supporting OpenAI, Gemini, Claude, etc.)
- Tool set registration (MCP tools, custom local tools)
- Structured output Schema (for routing decisions and data passing)

**Function Nodes** - Deterministic function nodes
- Defined using `@tool` decorator as independent nodes in Graph
- Receive structured output from upstream Agents as input
- Execute deterministic operations (e.g., data transformation, formatting, computation)
- Must return Pydantic BaseModel type for type-safe data passing
- Referenced via `function_ref` to pre-registered function names

**Tools and Custom Extensions:**

**1. Agent Tools (Called by Agents)**
- **MCP Tools**: Support Model Context Protocol standard, dynamically load external tool servers
  - File system operations (`@modelcontextprotocol/server-filesystem`)
  - Git operations (`@modelcontextprotocol/server-github`)
  - Database queries, etc.
- **Custom Local Tools**: Define using `@tool` decorator and register to `ToolRouter`
  ```python
  from strands import tool, ToolContext
  from hatchify.core.factory.tool_factory import ToolRouter

  tool_router = ToolRouter()

  @tool(name="add", description="Add two numbers", context=True)
  async def add(a: float, b: float, tool_context: ToolContext) -> float:
      return a + b

  tool_router.register(add)
  ```

**2. Function Nodes (As Graph Nodes)**
- Use same `@tool` decorator but register to Function Router
- Must define Pydantic output model
  ```python
  from pydantic import BaseModel
  from strands import tool

  class EchoResult(BaseModel):
      text: str

  @tool(name="echo_function", description="Echo input")
  async def echo_function(text: str) -> EchoResult:
      return EchoResult(text=f"[ECHO] {text}")
  ```

### 3. ⚙️ Unified Configuration Management

Manage models and tools through declarative configuration files, supporting multiple Providers and transport protocols.

**Model Configuration (`resources/models.toml`)**

Support multiple Provider configurations for unified management of different LLM service providers:

```toml
default_provider = "openai-like"

[providers.openai]
id = "openai"
name = "OpenAI"
family = "openai"
base_url = "https://api.openai.com/v1"
api_key = "sk-xxx"
enabled = true
priority = 3  # Priority, lower number = higher priority

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

**Configuration Features:**
- Support multiple Provider configurations simultaneously (OpenAI, Anthropic, DeepSeek, etc.)
- `priority` field controls Provider fallback order (lower number = higher priority)
- Support individually disabling models (`enabled = false`)
- Compatible with OpenAI-Like interfaces (adapt third-party proxy services)

**MCP Tool Configuration (`resources/mcp.toml`)**

Support three transport protocols for dynamically loading external tool servers:

**1. Stdio Transport (Local Process)**
```toml
[[servers]]
name = "filesystem"
transport = "stdio"
enabled = true
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
prefix = "fs"  # Tool name prefix

# Optional configuration
cwd = "/tmp"
encoding = "utf-8"

[servers.env]
NODE_ENV = "production"

[servers.tool_filters]
allowed = ["read_file", "write_file"]  # Whitelist
```

**2. SSE Transport (Server-Sent Events)**
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

**3. StreamableHTTP Transport**
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

**MCP Configuration Features:**
- Support three transport protocols (stdio / sse / streamablehttp)
- Tool filters (whitelist `allowed` / blacklist `rejected`)
- Tool name prefixes (avoid naming conflicts)
- Dynamic enable/disable servers (`enabled` field)

### 4. 🎨 Web Builder - Vibe Website Builder 🚧

> **Status: In Development**
> This feature is currently under development, some functions may not be fully implemented.

Through natural language conversation, let AI automatically generate and customize web applications, from requirement description to deployment in one stop.

**Tech Stack:**
- React 19 + TypeScript
- Vite 7 (Build tool)
- Tailwind CSS 4 (Styling framework)
- React JSON Schema Form (Dynamic form generation)

**Workflow:**

1. **Project Initialization**
   - Auto-generate web project based on Graph's `input_schema` and `output_schema`
   - Generate form page (for inputting data and triggering Webhook)
   - Generate result display page (intelligently render Graph output)

2. **Conversational Customization**
   - Agent can call tools to modify the project:
     - `file_read`: Read project files
     - `editor`: Edit code files
     - `file_write`: Create new files
     - `shell`: Bash tool implementation
   - Support multi-turn dialogue for iterative interface design and functionality optimization

3. **Intelligent Content Rendering**
   - Auto-identify output data types (images, URLs, structured data, lists, etc.)
   - Defensive programming, compatible with data-schema mismatches
   - Responsive design, adapts to various device sizes

4. **One-Click Deployment**
   - Auto-execute `npm install` and `npm run build`
   - Mount build artifacts to `/preview/{graph_id}` path
   - Real-time push build logs and progress
   - Support hot updates, auto-rebuild after modifications

**Use Cases:**
- Quickly generate web interfaces for Graph workflows
- No frontend development experience needed, customize interfaces through conversational interaction
- Auto-generate dynamic forms based on JSON Schema
- Intelligently render various types of Graph output results

### 5. 🔧 Environment Configuration System

Centrally manage all runtime configurations through `resources/development.yaml`.

**Core Configuration Items:**

**1. Server Configuration**
```yaml
hatchify:
  server:
    host: 0.0.0.0
    port: 8000
    base_url: http://localhost:8000  # ⚠️ Must change to public URL in production
```

⚠️ **Important Note**: `base_url` is the most critical configuration item
- Local development: `http://localhost:8000`
- Production deployment: Must modify to actual public URL (e.g., `https://your-domain.com`)
- Impact scope: Webhook callbacks, Web Builder project API addresses, preview page resource loading

**2. Model Configuration**
```yaml
models:
  spec_generator:      # Model used by Vibe Graph generator
    model: claude-sonnet-4-5-20250929
    provider: anthropic
  schema_extractor:    # Model used by Schema extractor
    model: claude-sonnet-4-5-20250929
    provider: anthropic
  web_builder:         # Model used by Web Builder
    model: claude-sonnet-4-5-20250929
    provider: anthropic
```

**3. Database Configuration**
```yaml
db:
  platform: sqlite  # Currently only supports: sqlite
  sqlite:
    driver: sqlite+aiosqlite
    file: ./data/dev.db
    echo: False
    pool_pre_ping: True
```

⚠️ **Note**: Current version only supports SQLite. PostgreSQL and MySQL support will be added in future releases.

**4. Storage Configuration**
```yaml
storage:
  platform: opendal  # Currently only supports: opendal
  opendal:
    schema: fs  # Supports: fs / s3 / oss, etc. (based on OpenDAL)
    bucket: hatchify
    folder: dev
    root: ./data/storage
```

**5. Session Management Configuration**
```yaml
session_manager:
  manager: file  # Currently only supports: file
  file:
    folder: dev
    root: ./data/session
```

**6. Web Builder Configuration**
```yaml
web_app_builder:
  repo_url: https://github.com/Sider-ai/hatchify-web-app-template.git
  branch: master
  workspace: ./data/workspace

  # Environment variable injection during project initialization
  init_steps:
    - type: env
      file: .env
      vars:
        VITE_API_BASE_URL: "{{base_url}}"  # Auto-use server.base_url
        VITE_GRAPH_ID: "{{graph_id}}"
        VITE_BASE_PATH: "/preview/{{graph_id}}"

  # Security configuration
  security:
    allowed_directories:  # Whitelist: directories Agent can access
      - ./data/workspace
      - /tmp
    sensitive_paths:      # Blacklist: sensitive paths forbidden to access
      - ~/.ssh
      - ~/.aws
      - /etc/passwd
      - /root
```

**Environment Variable Override:**

Support overriding configuration via environment variables using `HATCHIFY__` prefix:

```bash
# Override server port
export HATCHIFY__SERVER__PORT=8080

# Override base_url (use in production deployment)
export HATCHIFY__SERVER__BASE_URL=https://your-domain.com

# Override database platform
export HATCHIFY__DB__PLATFORM=postgresql
```

**Configuration Priority:** Environment Variables > YAML Configuration File > Default Values

### 6. 🏛️ Enterprise-Grade Layered Architecture

Adopting classic three-tier architecture design (API → Service → Repository), achieving high cohesion and low coupling through generics and dependency injection.

**Architecture Layers:**

```
┌─────────────────────────────────────────────┐
│         API Layer (FastAPI Router)          │
│  - Route definition, request validation,    │
│    response serialization                   │
│  - Dependency injection via Depends         │
└─────────────────┬───────────────────────────┘
                  │ Calls
┌─────────────────▼───────────────────────────┐
│       Service Layer (GenericService[T])     │
│  - Business logic orchestration,            │
│    transaction management                   │
│  - Cross-Repository coordination            │
└─────────────────┬───────────────────────────┘
                  │ Uses
┌─────────────────▼───────────────────────────┐
│      Repository Layer (BaseRepository[T])   │
│  - Data access abstraction, CRUD operations │
│  - Query building, pagination encapsulation │
└─────────────────┬───────────────────────────┘
                  │ Operates
┌─────────────────▼───────────────────────────┐
│       Database Layer (SQLAlchemy ORM)       │
│  - ORM models, database connections         │
└─────────────────────────────────────────────┘
```

**1. Repository Layer - Data Access Abstraction**

**Core Features:**
- Generic design, type-safe
- Asynchronous operations, high performance
- Unified pagination interface (based on `fastapi-pagination`)
- Flexible query filtering (`find_by(**filters)`)

**2. Service Layer - Business Logic Orchestration**

**Core Features:**
- Transaction management (auto commit/rollback)
- Data validation (based on Pydantic)
- Cross-Repository coordination
- Business logic reuse

**3. API Layer - Routing and Dependency Injection**

**Core Features:**
- Dependency injection (`ServiceManager`, `RepositoryManager`)
- Unified response format (`Result[T]`)
- Automatic parameter validation (Pydantic)
- Unified exception handling

**Architecture Advantages:**
- 📦 **Separation of Concerns**: Clear responsibilities per layer, easy to maintain
- 🔄 **Testability**: Each layer can be unit tested independently
- 🔌 **Extensibility**: Quickly extend new entities through generic base classes
- 🎯 **Type Safety**: Generics + Pydantic ensure type correctness
- 🚀 **Development Efficiency**: Common CRUD operations out-of-the-box

## 🛠️ API Endpoints Overview

### Graph Management
- `GET /api/graphs` - List all Graphs
- `POST /api/graphs` - Create new Graph
- `GET /api/graphs/{graph_id}` - Get Graph details
- `PUT /api/graphs/{graph_id}` - Update Graph
- `DELETE /api/graphs/{graph_id}` - Delete Graph

### Execution
- `POST /api/webhooks/{graph_id}` - Execute Graph (Webhook)
- `GET /api/executions` - Query execution records

### Web Builder
- `POST /api/web_builder/create` - Create Web Builder session
- `POST /api/web_builder/chat` - Conversational building
- `POST /api/web_builder/deploy` - Deploy generated web application

### Version Management
- `GET /api/graph_versions` - List version history
- `POST /api/graph_versions` - Create version snapshot

### Sessions and Messages
- `GET /api/sessions` - List sessions
- `POST /api/sessions` - Create session
- `GET /api/messages` - Query message history

### System
- `GET /api/tools` - List available tools
- `GET /api/models` - List available models

## 📝 Common Tasks

### Adding New Agent Type
1. Define configuration in `AgentCard`
2. Add to `GraphSpec.agents`
3. `AgentFactory` automatically handles creation

### Adding New Function Node
1. Implement function in `core/graph/functions/`
2. Register in `FunctionManager`
3. Reference in `GraphSpec.functions`

### Adding New Tool
1. **Strands Tools**: Implement in `core/graph/tools/`
2. **MCP Tools**: Configure MCP server in `resources/mcp.toml`

### Adding New Event Type
1. Define event class in `common/domain/event/` (inherit from `StreamEvent`)
2. Trigger in corresponding stream processor (e.g., `GraphExecutor`)
3. Frontend receives via SSE

### Custom Routing Logic
Extend routing types in `DynamicGraphBuilder._create_edge_condition()`.

## 📚 Development Guide

### Database
- **Supported Databases**: SQLite (default), PostgreSQL (planned), MySQL (planned)
- **Connection Configuration**: Via `resources/development.yaml`
- **Initialization**: Database tables auto-created on app startup (`init_db()` in `business/db/session.py`)

### Storage System
- **Abstraction Layer**: OpenDAL
- **Supported Schemas**: fs, s3, oss, etc.
- **Configuration**: Via `resources/development.yaml`

## ⚠️ Important Notes

- **Async First**: All database and I/O operations use `async/await`
- **Dependency Injection**: Services and Repositories obtained through Manager singletons
- **Version Management**: Graph's `current_spec` is single source of truth, version table for snapshots
- **Security**: Web Builder file operations restricted by `security.allowed_directories` (see `development.yaml`)
- **Configuration Priority**: Environment Variables > YAML > .env file

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Official Website**: [https://hatchify.ai/](https://hatchify.ai/)
- **Documentation**: Coming soon
- **GitHub**: [https://github.com/Sider-ai/hatchify](https://github.com/Sider-ai/hatchify)

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

Made with ❤️ by Sider.ai