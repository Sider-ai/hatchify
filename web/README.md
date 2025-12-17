# Hatchify

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

**This is the frontend application.** It works in conjunction with the [Hatchify Backend](https://github.com/Sider-ai/hatchify), which provides the API server.

Hatchify is a powerful workflow visualization and AI agent management platform built with modern web technologies. It provides an intuitive interface for creating, managing, and monitoring AI agent workflows in real-time.

## 🚀 Quick Start

### Requirements

**Frontend:**

- Node.js 20+
- pnpm 9+

**Backend (Required):**

- [Hatchify Backend](https://github.com/Sider-ai/hatchify) running on <http://localhost:8000> (or custom URL)

### Installation

```bash
# Clone repository
git clone https://github.com/Sider-ai/hatchify-web.git
cd hatchify-web

# Install dependencies
pnpm install

# Build icons package (required before first run)
pnpm build:icons
```

**Note**: The icons package must be built before starting the development server, as the main application depends on `@hatchify/icons`.

### Configuration

**⚠️ Important**: This is the frontend application. You need to run the backend project first to use this application.

1. **Start the backend project**

   Clone and start the backend project from [https://github.com/Sider-ai/hatchify](https://github.com/Sider-ai/hatchify):

   ```bash
   # Clone backend repository
   git clone https://github.com/Sider-ai/hatchify.git
   cd hatchify

   # Follow backend setup instructions
   # Backend will run on http://localhost:8000 by default
   ```

2. **Configure frontend environment**

   Create a `.env` file in the frontend root directory:

   ```bash
   # API endpoint configuration
   # Use the backend server URL (default: http://localhost:8000)
   VITE_API_TARGET=http://localhost:8000
   ```

   See `.env.example` for all available environment variables.

### Launch

```bash
# Development mode (with hot reload)
pnpm dev

```

### Build

```bash
# Production build
pnpm build

# Preview production build
pnpm preview
```

## 🐳 Docker Deployment

### 1. Build Image

```bash
docker build -t hatchify-web .
```

### 2. Start Container

```bash
# Run in background with port mapping
docker run -d \
  --name hatchify-web \
  -p 3000:80 \
  hatchify-web
```

**Parameter Explanation:**

- `-p 3000:80`: Map container port 80 to host port 3000
- `-d`: Run in detached mode (background)
- `--name`: Container name for easy management

### 3. View Logs

```bash
# Real-time log viewing
docker logs -f hatchify-web

# View last 100 lines
docker logs --tail 100 hatchify-web
```

### 4. Backend API Configuration

To connect to a different backend API, edit `docker/nginx.conf` before building:

```nginx
location /api/ {
  proxy_pass http://your-backend-url;
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection 'upgrade';
  proxy_set_header Host $host;
  # ... rest of proxy configuration
}
```

Then rebuild the image:

```bash
docker build -t hatchify-web .
```

**Important Notes:**

- ⚠️ Ensure backend API is accessible from the Docker container
- For production deployment, use proper domain names and HTTPS

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

### Development Workflow

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

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

## 💬 Community & Support

- 🐛 [Report a Bug](https://github.com/Sider-ai/hatchify-web/issues)
- 💡 [Request a Feature](https://github.com/Sider-ai/hatchify-web/issues)

---

Made with ❤️ by [Sider.ai](https://sider.ai/)
