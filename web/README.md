# Hatchify Web Frontend

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Node.js](https://img.shields.io/badge/node-%3E%3D20-brightgreen.svg)](https://nodejs.org/)
[![React](https://img.shields.io/badge/react-19-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.7-blue.svg)](https://www.typescriptlang.org/)

English | [简体中文](README_ZH.md)

---

🌐 **Cloud Version**: [https://hatchify.ai/](https://hatchify.ai/) - Try Hatchify instantly without installation!

---

</div>

## 📖 Introduction

**This is the frontend application for Hatchify.** It works in conjunction with the [Hatchify Backend](../README.md) to provide a powerful workflow visualization and AI agent management interface.

⚠️ **Important**: This frontend requires the backend server to be running. Please see the [main README](../README.md) for complete setup instructions.

## 🚀 Quick Start

For detailed installation and configuration instructions, please refer to the [main README](../README.md#-quick-start).

### Quick Commands

```bash
# Install dependencies
pnpm install

# Build icons package (required before first run)
pnpm build:icons

# Development mode
pnpm dev

# Production build
pnpm build
```

### Environment Configuration

Create a `.env` file:

```bash
# Backend API endpoint (default: http://localhost:8000)
VITE_API_TARGET=http://localhost:8000
```

See `.env.example` for all available options.

## 🛠️ Tech Stack

- **React 19** - UI framework
- **TypeScript 5.7** - Type safety
- **Vite 7** - Build tool
- **Tailwind CSS 4** - Styling
- **React Flow** - Workflow visualization
- **Biome** - Code formatting and linting

## 🤝 Contributing

### Code Style

- Use **Biome** for formatting (tab indentation, double quotes)
- Follow TypeScript best practices
- Write meaningful commit messages
- Add comments for complex logic (in English)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Official Website**: [https://hatchify.ai/](https://hatchify.ai/)
- **Backend Repository**: [https://github.com/Sider-ai/hatchify](https://github.com/Sider-ai/hatchify)
- **Main Documentation**: [../README.md](../README.md)

---

Made with ❤️ by [Sider.ai](https://sider.ai/)
