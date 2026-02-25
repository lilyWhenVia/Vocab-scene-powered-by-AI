# 记忆宫殿 MVP

AI 驱动的单词记忆系统 - 最小可行产品版本

## 快速开始

### 1. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env，填入你的 API Key

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 2. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 3. 访问

打开浏览器访问 http://localhost:5173

## 环境变量

在 `backend/.env` 中配置：

```
# 二选一
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
```

## API 文档

启动后端后访问 http://localhost:8000/docs 查看 Swagger 文档

## 技术栈

- 前端: React + Vite + Tailwind CSS
- 后端: Python FastAPI + SQLite
- AI: OpenAI GPT-4 / Anthropic Claude

## 功能

- [x] 用户注册/登录 (JWT)
- [x] 创建单词列表
- [x] AI 生成记忆宫殿场景
- [x] 场景展示 (中英双语)
- [x] 段落点击翻译
- [ ] 学习进度追踪
- [ ] 复习算法
