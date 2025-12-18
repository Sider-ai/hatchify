# Hatchify Web 前端

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

**这是 Hatchify 的前端应用程序。** 它需要配合 [Hatchify 后端](../README_ZH.md) 使用，提供强大的工作流可视化和 AI 智能体管理界面。

⚠️ **重要提示**：此前端需要后端服务器运行。请查看[主 README](../README_ZH.md) 获取完整的设置说明。

## 🚀 快速开始

有关详细的安装和配置说明，请参阅[主 README](../README_ZH.md#-快速开始)。

### 快速命令

```bash
# 安装依赖
pnpm install

# 构建图标包（首次运行前必需）
pnpm build:icons

# 开发模式
pnpm dev

# 生产构建
pnpm build
```

### 环境配置

创建 `.env` 文件：

```bash
# 后端 API 端点（默认：http://localhost:8000）
VITE_API_TARGET=http://localhost:8000
```

查看 `.env.example` 了解所有可用选项。

## 🛠️ 技术栈

- **React 19** - UI 框架
- **TypeScript 5.7** - 类型安全
- **Vite 7** - 构建工具
- **Tailwind CSS 4** - 样式框架
- **React Flow** - 工作流可视化
- **Biome** - 代码格式化和检查

## 🤝 参与贡献

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
- **主文档**: [../README_ZH.md](../README_ZH.md)

---

Made with ❤️ by [Sider.ai](https://sider.ai/)
