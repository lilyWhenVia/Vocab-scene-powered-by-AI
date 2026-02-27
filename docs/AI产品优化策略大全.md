# AI 产品优化策略大全

除了 Prompt 优化，还有以下 6 大类策略可以显著降低成本、提升性能。

---

## 1. 缓存策略 (Caching)

### 1.1 精确缓存 (Exact Match Cache)
相同输入直接返回缓存结果。

```python
import hashlib
import json

class ExactCache:
    def __init__(self):
        self.cache = {}
    
    def get_key(self, words):
        # 对单词列表排序后生成哈希
        sorted_words = sorted([w['word'] for w in words])
        return hashlib.md5(json.dumps(sorted_words).encode()).hexdigest()
    
    def get(self, words):
        key = self.get_key(words)
        return self.cache.get(key)
    
    def set(self, words, result):
        key = self.get_key(words)
        self.cache[key] = result
```

### 1.2 语义缓存 (Semantic Cache)
相似输入返回缓存结果，使用向量相似度匹配。

```python
# 使用 Redis + 向量搜索
from redis import Redis
from sentence_transformers import SentenceTransformer

class SemanticCache:
    def __init__(self):
        self.redis = Redis()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.threshold = 0.95  # 相似度阈值
    
    def find_similar(self, query):
        embedding = self.model.encode(query)
        # 在 Redis 中搜索相似向量
        results = self.redis.ft().search(
            Query(f"*=>[KNN 1 @embedding $vec AS score]")
            .return_fields("response", "score")
            .dialect(2),
            {"vec": embedding.tobytes()}
        )
        if results and results[0].score > self.threshold:
            return results[0].response
        return None
```

**效果**: 减少 30-70% 重复请求

---

## 2. 批处理策略 (Batching)

### 2.1 请求批处理
收集多个请求，一次性发送给 AI。

```python
import asyncio
from collections import deque

class BatchProcessor:
    def __init__(self, batch_size=10, wait_time=0.5):
        self.queue = deque()
        self.batch_size = batch_size
        self.wait_time = wait_time
    
    async def add_request(self, request):
        future = asyncio.Future()
        self.queue.append((request, future))
        
        if len(self.queue) >= self.batch_size:
            await self._process_batch()
        else:
            asyncio.create_task(self._delayed_process())
        
        return await future
    
    async def _process_batch(self):
        batch = [self.queue.popleft() for _ in range(min(len(self.queue), self.batch_size))]
        # 合并请求，一次调用 AI
        combined_prompt = self._merge_prompts([r[0] for r in batch])
        result = await self.call_ai(combined_prompt)
        # 分发结果
        for (req, future), res in zip(batch, self._split_results(result)):
            future.set_result(res)
```

### 2.2 单词分批处理
大量单词时分批生成，避免 "lost in the middle"。

```python
def generate_in_batches(words, batch_size=80):
    """分批处理单词，每批 80 词"""
    all_scenes = []
    for i in range(0, len(words), batch_size):
        batch = words[i:i+batch_size]
        result = ai_service.generate_scene(batch)
        all_scenes.extend(result['scenes'])
    return {"scenes": all_scenes}
```

**效果**: 提升 2-6x 吞吐量，降低 50% 成本

---

## 3. 模型路由策略 (Model Routing)

### 3.1 复杂度路由
简单任务用小模型，复杂任务用大模型。

```python
class ModelRouter:
    def __init__(self):
        self.models = {
            "simple": "gpt-3.5-turbo",      # $0.0005/1K tokens
            "medium": "gpt-4o-mini",         # $0.00015/1K tokens
            "complex": "gpt-4o"              # $0.0025/1K tokens
        }
    
    def route(self, words):
        word_count = len(words)
        
        if word_count <= 20:
            return self.models["simple"]
        elif word_count <= 100:
            return self.models["medium"]
        else:
            return self.models["complex"]
```

### 3.2 级联策略 (Cascading)
先用小模型，失败时升级到大模型。

```python
async def cascade_generate(words):
    """级联生成：小模型 → 中模型 → 大模型"""
    models = ["minimax", "zhipu", "deepseek"]
    
    for model in models:
        try:
            result = await generate_with_model(words, model)
            if validate_result(result):
                return result
        except Exception as e:
            print(f"{model} failed: {e}")
            continue
    
    raise Exception("All models failed")
```

**效果**: 降低 40-70% 成本

---

## 4. 流式输出策略 (Streaming)

### 4.1 流式响应
边生成边返回，提升用户体验。

```python
from fastapi.responses import StreamingResponse

@app.post("/generate-stream")
async def generate_stream(req: GenerateRequest):
    async def stream_generator():
        async for chunk in ai_service.generate_stream(req.words):
            yield f"data: {json.dumps(chunk)}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream"
    )
```

### 4.2 前端流式接收

```javascript
const response = await fetch('/generate-stream', {
  method: 'POST',
  body: JSON.stringify({ words }),
});

const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = new TextDecoder().decode(value);
  // 实时更新 UI
  updateScene(JSON.parse(chunk));
}
```

**效果**: 首字节时间 (TTFB) 降低 80%

---

## 5. 预计算策略 (Pre-computation)

### 5.1 场景模板预生成
预先生成常见场景的故事模板。

```python
SCENE_TEMPLATES = {
    1: {  # 图书馆场景
        "intro": "清晨的阳光透过高窗洒入图书馆，{word1}的书籍整齐排列...",
        "body": "一位学者正在{word2}地研究{word3}的理论...",
        "outro": "图书馆的钟声响起，提醒着{word4}的重要性..."
    }
}

def generate_with_template(scene_id, words):
    """使用模板 + 单词填充，减少 AI 生成量"""
    template = SCENE_TEMPLATES[scene_id]
    # AI 只需要选择单词位置，不需要生成完整故事
    return fill_template(template, words)
```

### 5.2 热门词库预缓存
预先生成四六级、考研等热门词库的场景。

```python
POPULAR_WORDLISTS = {
    "cet4": [...],  # 四级词汇
    "cet6": [...],  # 六级词汇
    "kaoyan": [...] # 考研词汇
}

# 启动时预生成
for name, words in POPULAR_WORDLISTS.items():
    result = ai_service.generate_scene(words)
    cache.set(f"preset:{name}", result)
```

**效果**: 热门请求 0 延迟，0 成本

---

## 6. 质量保障策略 (Quality Assurance)

### 6.1 输出验证
验证 AI 输出格式和内容完整性。

```python
def validate_result(result, expected_words):
    """验证生成结果"""
    errors = []
    
    # 检查场景数量
    scenes = result.get('scenes', [])
    if not scenes:
        errors.append("No scenes generated")
    
    # 检查单词覆盖率
    all_words_used = set()
    for scene in scenes:
        all_words_used.update(scene.get('words', []))
    
    missing = set(expected_words) - all_words_used
    if missing:
        errors.append(f"Missing words: {missing}")
    
    # 检查 [[word]] 标记
    for scene in scenes:
        content = scene.get('zh', {}).get('content', '')
        markers = re.findall(r'\[\[([^\]]+)\]\]', content)
        if not markers:
            errors.append(f"Scene {scene['id']} has no word markers")
    
    return len(errors) == 0, errors
```

### 6.2 自动重试
失败时自动重试，使用不同策略。

```python
async def generate_with_retry(words, max_retries=3):
    """带重试的生成"""
    for attempt in range(max_retries):
        try:
            result = await ai_service.generate_scene(words)
            valid, errors = validate_result(result, [w['word'] for w in words])
            
            if valid:
                return result
            
            print(f"Attempt {attempt+1} validation failed: {errors}")
            
            # 调整策略重试
            if attempt == 1:
                # 第二次尝试：使用质量模式
                result = await ai_service.generate_scene(words, quality_mode=True)
            elif attempt == 2:
                # 第三次尝试：分批处理
                result = await generate_in_batches(words, batch_size=50)
                
        except Exception as e:
            print(f"Attempt {attempt+1} error: {e}")
    
    raise Exception("All retries failed")
```

---

## 策略组合推荐

### 低成本方案 (节省 70%+)
1. 精确缓存 + 语义缓存
2. 模型路由（小模型优先）
3. 批处理
4. Prompt 压缩

### 高性能方案 (延迟降低 80%+)
1. 流式输出
2. 预计算热门词库
3. 边缘缓存
4. 并行处理

### 平衡方案 (推荐)
1. 语义缓存（相似请求复用）
2. 级联路由（小模型 → 大模型）
3. 流式输出（提升体验）
4. 输出验证 + 自动重试

---

## 成本对比

| 策略 | 成本降低 | 延迟降低 | 实现难度 |
|------|----------|----------|----------|
| Prompt 压缩 | 40-60% | 20% | ⭐ |
| 精确缓存 | 30-50% | 90% | ⭐ |
| 语义缓存 | 50-70% | 85% | ⭐⭐⭐ |
| 批处理 | 30-50% | -20% | ⭐⭐ |
| 模型路由 | 40-70% | 30% | ⭐⭐ |
| 流式输出 | 0% | 80% | ⭐⭐ |
| 预计算 | 100% | 100% | ⭐⭐⭐ |

---

## 参考资料

1. [Redis LangCache - Semantic Caching](https://redis.io/langcache/)
2. [LLM Routing and Cascading](https://arxiv.org/html/2410.10347v3)
3. [Tribe AI - Reducing Latency and Cost](https://www.tribe.ai/applied-ai/reducing-latency-and-cost-at-scale-llm-performance)
4. [LLM Cost Trap Escape Playbook](https://cloudurable.com/blog/llm-cost-trap-escape-playbook/)
