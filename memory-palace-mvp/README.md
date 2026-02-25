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

# 配置环境变量（可选，也可在 Admin 页面配置）
copy .env.example .env
# 编辑 .env，填入你的 API Key

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 2. 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 3. 访问

- 主页: http://localhost:5173
- Admin: http://localhost:5173/admin（密钥：admin123）
- API 文档: http://localhost:8000/docs

## 环境变量

在 `backend/.env` 中配置（任选一个）：

```bash
MINIMAX_API_KEY=xxx      # 推荐，性价比最高
ZHIPU_API_KEY=xxx        # 智谱 GLM
DEEPSEEK_API_KEY=xxx     # DeepSeek
OPENAI_API_KEY=sk-xxx    # OpenAI
ANTHROPIC_API_KEY=sk-ant-xxx  # Anthropic
```

或者在 Admin 页面动态配置。

## 核心架构

### AI 场景生成流程

```
输入: 200个单词
    ↓
AI 分析 → 选择 1-5 个场景 (scene_id 1-50)
    ↓
AI 返回: {scenes: [{scene_id, words_in_scene, paragraphs}]}
    ↓
后端: SCENES[scene_id] → 获取图片URL、标题
后端: [[word]] → <span class='word-highlight'>...</span>
    ↓
输出: 5个场景，每个有唯一图片、故事、单词
```

### 50个预设场景

场景库定义在 `backend/app/ai_service.py` 的 `SCENE_LIBRARY` 中：

| ID | 场景 | 关键词 |
|----|------|--------|
| 1 | 晨光图书馆 | book, read, study, library |
| 2 | 大学礼堂 | education, student, academic |
| 3 | 科学实验室 | science, experiment, research |
| ... | ... | ... |
| 50 | 火山口 | volcano, lava, eruption |

AI 根据单词主题自动选择最匹配的场景。

### 单词高亮机制

AI 在故事中使用 `[[word]]` 标记单词，后端转换为 HTML：

```
AI 输出: "他决定 [[abandon]] 这个计划"
    ↓
后端转换: "他决定 <span class='word-highlight'>abandon<span class='tooltip'>abandon: v. 放弃</span></span> 这个计划"
```

## API 示例

### 生成场景

```bash
POST /generate
Content-Type: application/json

{
  "name": "四级词汇",
  "words": [
    {"word": "abandon", "pos": "v.", "meaning": "放弃"},
    {"word": "absorb", "pos": "v.", "meaning": "吸收"},
    ...
  ]
}
```

响应：
```json
{
  "message": "成功生成 3 个记忆场景",
  "scenes": [
    {
      "id": 1,
      "scene_id": 1,
      "bgImage": "https://images.unsplash.com/...",
      "zh": {
        "title": "晨光图书馆",
        "content": "<p>清晨的阳光透过高窗...<span class='word-highlight'>abandon</span>...</p>"
      },
      "en": {
        "title": "Morning Library",
        "content": "<p>Morning sunlight streams...</p>"
      }
    }
  ]
}
```

### 上传文件解析

```bash
POST /parse-file
Content-Type: multipart/form-data

file: vocabulary.pdf
```

## 调试日志

后端会输出详细日志，帮助调试：

```
============================================================
[AI] ===== 开始生成场景 =====
[AI] 总单词数: 50, 提供商: minimax
[AI] 单词字典大小: 100
[AI] Prompt长度: 12345 字符

[AI] ===== AI原始返回 =====
[AI] 场景数: 3
[AI] 场景1: scene_id=1, words_in_scene=20

[AI] --- 处理场景1: 晨光图书馆 (id=1) ---
[AI] 段落数: 4, 单词数: 20
[AI]   段落1: zh标记5→高亮5, en标记5→高亮5
[AI] 场景1完成: zh高亮=20, en高亮=20

[AI] ===== 生成完成 =====
[AI] 生成场景数: 3, 覆盖单词数: 50/50
============================================================
```

如果有问题，日志会显示 `⚠️ 警告` 标记。

## 技术栈

- **前端**: React 18 + Vite + Tailwind CSS
- **后端**: Python FastAPI + SQLite
- **AI**: MiniMax / 智谱 / DeepSeek / OpenAI / Anthropic

## 功能清单

- [x] 用户注册/登录 (JWT)
- [x] 创建单词列表
- [x] AI 生成记忆宫殿场景
- [x] 50个预设场景库
- [x] 场景展示 (中英双语)
- [x] 段落点击翻译
- [x] 单词高亮 + 悬浮释义
- [x] 键盘快捷键 (← → L Esc)
- [x] Admin 配置面板
- [ ] 学习进度追踪
- [ ] 复习算法
