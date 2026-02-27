# Prompt 优化策略文档

## 优化目标
- 最小化 token 消耗（降低成本）
- 最大化输出质量（格式正确、内容完整）
- 提高响应速度

## 当前优化措施

### 1. 场景列表压缩 (节省约 60% input token)

**旧格式** (~2000 tokens):
```
1. morning_library: 晨光图书馆 (Morning Library) - keywords: book, read, study, library, literature, knowledge
2. university_hall: 大学礼堂 (University Hall) - keywords: education, student, academic, degree, lecture, professor
...
```

**新格式** (~800 tokens):
```
1:morning_library(book,read,study)|2:university_hall(education,student,academic)|...
```

### 2. 单词列表压缩 (节省约 40% input token)

**旧格式**:
```
- abandon: v. 放弃
- absorb: v. 吸收
```

**新格式**:
```
abandon(v.放弃)
absorb(v.吸收)
```

### 3. 输出格式精简 (节省约 30% output token)

**旧格式**:
```json
{
  "scenes": [{
    "scene_id": 1,
    "words_in_scene": ["word1"],
    "paragraphs": [{
      "zh": "中文",
      "en": "English",
      "zh_pure": "翻译"
    }]
  }]
}
```

**新格式**:
```json
{"scenes":[{"scene_id":1,"words":["word1"],"p":[{"zh":"中文","en":"English","t":"翻译"}]}]}
```

### 4. Prompt 指令精简

**旧版** (~400 tokens):
```
You are a Memory Palace expert. Analyze the vocabulary and create immersive scenes.

## YOUR TASK
1. Analyze all {word_count} words below
2. Select 1-5 DIFFERENT scenes from the 50 available scenes (based on word themes)
...
```

**新版** (~150 tokens):
```
Memory Palace generator. Create scenes for vocabulary memorization.

SCENES(id:name): ...
WORDS({word_count}): ...
OUTPUT JSON: ...
RULES: ...
```

## Token 消耗对比

| 项目 | 旧版 | 新版 | 节省 |
|------|------|------|------|
| 场景列表 | ~2000 | ~800 | 60% |
| 单词列表(100词) | ~1500 | ~900 | 40% |
| Prompt 指令 | ~400 | ~150 | 62% |
| 输出格式 | ~3000 | ~2100 | 30% |
| **总计(100词)** | **~6900** | **~3950** | **43%** |

## 其他优化策略（可选）

### 5. 分批处理
超过 100 词时分批处理，每批 50-80 词：
- 减少单次请求的 token 消耗
- 降低 AI 遗漏单词的概率
- 可并行处理提高速度

### 6. 场景预匹配
根据单词关键词预先匹配场景类别，只传递相关场景：
```python
SCENE_CATEGORIES = {
    "education": [1,2,3,4,5],
    "business": [6,7,8,9,10],
    ...
}
```

### 7. 缓存机制
- 相同单词列表返回缓存结果
- 相似单词列表复用部分场景

### 8. 质量模式切换
- 默认使用精简 prompt（快速、低成本）
- 可选质量模式使用详细 prompt（高质量）

## 参考资料

1. [Token efficiency with structured output](https://medium.com/data-science-at-microsoft/token-efficiency-with-structured-output-from-language-models-be2e51d3d9d5)
2. [Prompt Compression in LLMs](https://medium.com/@sahin.samia/prompt-compression-in-large-language-models-llms-making-every-token-count-078a2d1c7e03)
3. [LLMLingua - Microsoft Research](https://github.com/microsoft/LLMLingua)
4. [Optimizing Prompts to Reduce Token Costs](https://inventivehq.com/blog/optimize-prompts-reduce-token-costs)

## 最佳实践总结

1. **精简指令** - 移除冗余说明，使用简洁命令式语句
2. **压缩格式** - 使用紧凑的数据格式（管道分隔、括号包裹）
3. **减少示例** - Zero-shot 优先，必要时用 One-shot
4. **结构化输出** - 使用 JSON Schema 约束输出格式
5. **分批处理** - 大量数据时分批，避免 "lost in the middle"
6. **缓存复用** - 相同/相似请求复用结果
