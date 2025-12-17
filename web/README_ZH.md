# Hatchify

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Node.js](https://img.shields.io/badge/node-%3E%3D20-brightgreen.svg)](https://nodejs.org/)
[![React](https://img.shields.io/badge/react-19-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.7-blue.svg)](https://www.typescriptlang.org/)

[English](README.md) | 简体中文

---

🌐 **云端版本**: [https://hatchify.ai/](https://hatchify.ai/) - 无需安装，立即试用 Hatchify！

---

</div>

## 📖 简介

**这是前端应用程序。** 它需要配合 [Hatchify 后端](https://github.com/Sider-ai/hatchify) 使用，后端提供 API 服务。

Hatchify 是一个强大的工作流可视化和 AI 智能体管理平台，采用现代 Web 技术构建。它提供直观的界面，用于实时创建、管理和监控 AI 智能体工作流。

## 🚀 快速开始

### 环境要求

**前端：**

- Node.js 20+
- pnpm 9+

**后端（必需）：**

- [Hatchify 后端](https://github.com/Sider-ai/hatchify) 运行在 <http://localhost:8000>（或自定义 URL）

### 安装

```bash
# 克隆仓库
git clone https://github.com/Sider-ai/hatchify-web.git
cd hatchify-web

# 安装依赖
pnpm install

# 构建图标包（首次运行前必需）
pnpm build:icons
```

**注意**：在启动开发服务器之前必须构建图标包，因为主应用依赖 `@hatchify/icons`。

### 配置

**⚠️ 重要提示**：这是前端应用程序。使用前需要先运行后端项目。

1. **启动后端项目**

   从 [https://github.com/Sider-ai/hatchify](https://github.com/Sider-ai/hatchify) 克隆并启动后端项目：

   ```bash
   # 克隆后端仓库
   git clone https://github.com/Sider-ai/hatchify.git
   cd hatchify

   # 按照后端设置说明操作
   # 后端默认运行在 http://localhost:8000
   ```

2. **配置前端环境**

   在前端根目录创建 `.env` 文件：

   ```bash
   # API 端点配置
   # 使用后端服务器 URL（默认：http://localhost:8000）
   VITE_API_TARGET=http://localhost:8000
   ```

   查看 `.env.example` 了解所有可用的环境变量。

### 启动

```bash
# 开发模式（热重载）
pnpm dev

```

### 构建

```bash
# 生产构建
pnpm build

# 预览生产构建
pnpm preview
```

## 🐳 Docker 部署

### 1. 构建镜像

```bash
docker build -t hatchify-web .
```

### 2. 启动容器

```bash
# 后台运行并映射端口
docker run -d \
  --name hatchify-web \
  -p 3000:80 \
  hatchify-web
```

**参数说明：**

- `-p 3000:80`：将容器的 80 端口映射到主机的 3000 端口
- `-d`：后台运行（分离模式）
- `--name`：容器名称，便于管理

### 3. 查看日志

```bash
# 实时查看日志
docker logs -f hatchify-web

# 查看最后 100 行
docker logs --tail 100 hatchify-web
```

### 4. 后端 API 配置

要连接到不同的后端 API，在构建前编辑 `docker/nginx.conf`：

```nginx
location /api/ {
  proxy_pass http://your-backend-url;
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection 'upgrade';
  proxy_set_header Host $host;
  # ... 其他代理配置
}
```

然后重新构建镜像：

```bash
docker build -t hatchify-web .
```

**重要提示：**

- ⚠️ 确保后端 API 可从 Docker 容器访问
- 生产部署时，请使用正确的域名和 HTTPS

## 🤝 参与贡献

我们欢迎各种形式的贡献！欢迎提交 Pull Request。

### 开发流程

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 代码规范

- 使用 **Biome** 进行格式化（Tab 缩进，双引号）
- 遵循 TypeScript 最佳实践
- 编写有意义的提交信息
- 为复杂逻辑添加注释（使用英文）

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🔗 链接

- **官方网站**: [https://hatchify.ai/](https://hatchify.ai/)
- **后端仓库**: [https://github.com/Sider-ai/hatchify](https://github.com/Sider-ai/hatchify)

## 💬 社区与支持

- 🐛 [报告 Bug](https://github.com/Sider-ai/hatchify-web/issues)
- 💡 [功能请求](https://github.com/Sider-ai/hatchify-web/issues)

---

Made with ❤️ by [Sider.ai](https://sider.ai/)
