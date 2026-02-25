# 🌿 记了么 | AI Memory Palace

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **AI 自动生成沉浸式记忆场景**
> 
> 上传词库，AI 自动生成记忆宫殿场景，让单词在故事中自然生长

## ✨ 功能特点

- 🤖 **AI 场景生成** - 上传单词，AI 自动生成沉浸式记忆场景
- 📄 **多格式支持** - 支持 PDF、Word、TXT 词库上传
- 🌐 **中英双语** - 一键切换中英文叙事
- 💡 **单词高亮** - 悬浮查看词义，自然融入故事
- 📱 **响应式设计** - 支持桌面端和移动端
- 💾 **本地缓存** - 历史词库自动保存，随时回顾

## 🚀 快速开始

### 后端

```bash
cd memory-palace-mvp/backend

# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd memory-palace-mvp/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173 开始使用。

### 配置 AI

访问 http://localhost:5173/admin（密钥：admin123）配置 AI API Key。

支持的 AI 提供商：
- MiniMax（推荐，性价比最高）
- 智谱 GLM
- DeepSeek
- 通义千问
- OpenAI
- Anthropic

## 📁 项目结构

```
.
├── memory-palace-mvp/     # 项目代码
│   ├── backend/           # FastAPI 后端
│   │   └── app/
│   │       ├── main.py        # API 路由
│   │       ├── ai_service.py  # AI 场景生成
│   │       └── ...
│   └── frontend/          # React 前端
│       └── src/
│           ├── pages/         # 页面组件
│           └── ...
├── docs/                  # 文档
├── templates/             # HTML 模板参考
└── samples/               # 示例文件
```

## 🛠️ 技术栈

- **后端**: FastAPI, Python
- **前端**: React, Vite, Tailwind CSS
- **AI**: MiniMax / 智谱 / DeepSeek / OpenAI / Anthropic

## 📄 License

MIT License

---

**🌿 在场景中记忆，让单词自然生长**
