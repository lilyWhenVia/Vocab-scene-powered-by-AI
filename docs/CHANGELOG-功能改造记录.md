# 记忆宫殿单词系统 - 功能改造记录

## 2026-02-24

### 9. 场景叙事连贯性改写（进行中）
**需求**: 段落之间缺乏逻辑连接，单词出现突兀，不便于串联理解和记忆

**问题诊断**:
- 原文示例："河床silt样本放在架上。研究方法要inclusive。团队有些disagreement。"
- 问题：句子之间没有因果/递进/转折/时间顺序等逻辑衔接

**改写原则**:
- 使用空间移动（"转身走向..."、"穿过走廊来到..."）
- 使用观察发现（"你注意到..."、"你发现..."）
- 使用因果链接（"正因如此..."、"因为...所以..."）
- 使用递进深入（"不仅...更..."、"进一步..."）
- 使用转折对比（"然而..."、"尽管...但..."）

**已完成场景**:
- ✅ 场景2（自然博物馆）：完整改写 zh.content, zh.translation, zh.translationParagraphs, en.content
- ✅ 场景4（医学中心）：完整改写 zh.content, zh.translation

**待改写场景**:
- 场景4（医学中心）：translationParagraphs, en.content
- 场景5（城市广场）
- 场景6（科技园区）
- 场景7（国际会议中心）
- 场景8（历史博物馆）

**Prompt同步**: ✅ 已在 PROMPT-记忆宫殿单词系统.md 添加 "2.1 ⚠️ 叙事连贯性核心规范" 章节

---

### 8. 场景4-8添加translationParagraphs数组
**需求**: 每个段落必须有独立的完整中文翻译，不能出现"见第一段"

**代码改动**:
- 场景4(医学中心): 添加 `translationParagraphs` 数组，9个段落
- 场景5(城市广场): 添加 `translationParagraphs` 数组，8个段落
- 场景6(科技园区): 添加 `translationParagraphs` 数组，8个段落
- 场景7(国际会议中心): 添加 `translationParagraphs` 数组，8个段落
- 场景8(历史博物馆): 添加 `translationParagraphs` 数组，9个段落

**翻译规范**:
- 每段翻译完全独立，包含该段所有关键词的中文翻译
- 关键词使用 `<span class="word-highlight">中文<span class="tooltip">英文: 词性. 释义</span></span>` 格式
- 段落标记（如【候诊厅】）保留在对应翻译段落中

**Prompt同步**: ✅ 已完成

---

### 6. 卡片收起/展开功能（红色箭头）
**需求**: 卡片收起时完全隐藏，顶部显示红色下拉箭头

**代码改动**:
- CSS: `.card-collapsed`(完全隐藏) `.expand-notch`(顶部红色箭头)
- HTML: 新增 `<div id="expand-notch">` 固定顶部箭头
- DOM: 添加 `expandNotch` 引用
- EventBinder: `collapseCurrentCard()` / `expandCurrentCard()` / `toggleCurrentCard()`

**交互**:
- 点击收起按钮(↑)：卡片完全隐藏，顶部显示红色下拉箭头
- 点击红色箭头(↓)：卡片展开
- ESC键：切换收起/展开

**Prompt同步**: ✅ 已更新

---

### 7. 段落点击显示EN+CN双语翻译（完整中文）
**需求**: 点击段落显示 EN: 英文 + CN: 完整中文翻译（关键词也是中文）

**代码改动**:
- 数据结构: 新增 `zh.translationParagraphs` 数组（按段落分的完整中文翻译）
- SceneRenderer: 使用 `translationParagraphs` 或回退到 `translation`
- CSS: `.trans-cn`(红色左边框) `.trans-en`(蓝色左边框)
- 顺序: 先EN后CN

**Prompt同步**: ✅ 已更新

---

### 5. 段落点击显示中英双语翻译
**需求**: 点击段落同时显示中文和英文翻译，关键词高亮

**代码改动**:
- CSS: `.trans-zh`(红色左边框) `.trans-en`(蓝色左边框) `.trans-label` 样式
- SceneRenderer: 修改 `createSceneHTML()` 同时提取zh/en段落，生成双语结构
- HTML结构: `<div class="para-trans"><div class="trans-zh">...</div><div class="trans-en">...</div></div>`

**Prompt同步**: ✅ 已更新 3.4 段落点击展开翻译功能 章节

---

### 1. 段落点击展开翻译功能
**需求**: 点击段落展开对应翻译，桌面单击/移动端双击

**代码改动**:
- CSS: 新增 `.para-wrapper`, `.para-trans`, `.expanded` 样式类
- SceneRenderer: `createSceneHTML()` 解析段落并生成配对结构
- EventBinder: 新增 `initParagraphClick()` 和 `toggleTranslation()` 方法

**Prompt同步**: ✅ 已添加 3.4 段落点击展开翻译功能 章节

---

### 2. 语言切换禁用动画
**需求**: 中英切换时不使用过渡动画（仅卡片内容变化）

**代码改动**:
- CSS: 新增 `.no-transition` 工具类
- SceneController: `update(skipAnimation)` 支持跳过动画参数
- LanguageController: `toggle()` 调用 `update(true)`

**Prompt同步**: ✅ 已添加 2.4 动画控制 章节

---

### 3. 中文翻译完整性+高亮
**需求**: 翻译必须完整（不能省略号），且包含单词高亮

**代码改动**:
- SCENES_DATA: 所有场景的 `translation` 字段补全完整内容
- 翻译中添加 `<span class="word-highlight">中文词<span class="tooltip">...</span></span>`

**Prompt同步**: ✅ 已在 6.2 内容层次 章节强调

---

### 4. 背景图片整体场景化
**需求**: 背景图展示整体环境，非特定物体

**代码改动**:
- SCENES_DATA: 更新所有 `bgImage` URL 为场景全景图

**Prompt同步**: ✅ 已添加 6.4 背景图片生成规范 章节

---

## 文件对应关系
| 文件 | 用途 |
|-----|------|
| `memory-palace-356.html` | 主页面代码 |
| `PROMPT-记忆宫殿单词系统.md` | 开发需求文档 |
| `WORKFLOW-单词记忆宫殿化.md` | 工作流指南 |
| `CHANGELOG-功能改造记录.md` | 本文件，改造记录 |
| `TECH-技术实现文档.md` | 技术实现细节，维护指南 |
