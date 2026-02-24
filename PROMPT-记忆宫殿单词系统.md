# 记忆宫殿单词记忆卡片系统 - 完整开发需求文档

## 〇、记忆宫殿（Method of Loci）核心原理

### 什么是记忆宫殿？

记忆宫殿（Memory Palace），又称「位置记忆法」（Method of Loci），是一种源自古希腊的助记技术。"Loci"在拉丁语中意为"地点/位置"。该方法利用人类大脑天生擅长的**空间记忆能力**，将抽象信息与熟悉场所中的具体位置关联，从而实现高效记忆。

### 核心原理

1. **空间记忆优势**：人脑对空间位置的记忆远强于对抽象信息的记忆
2. **关联编码**：将新信息与已有的空间记忆建立联系，形成记忆锚点
3. **视觉化强化**：通过生动、夸张的画面感增强记忆深度
4. **路径串联**：按固定路线依次访问各个位置，实现有序回忆

### 记忆宫殿五步法

| 步骤 | 操作 | 示例 |
|-----|------|------|
| 1. 选择熟悉场所 | 选择你非常熟悉的地点（家、学校、常走的路） | 选择「办公室」作为记忆宫殿 |
| 2. 规划行走路线 | 确定场所内的固定行走顺序 | 门口→办公桌→文件柜→咖啡机→窗边 |
| 3. 设定空间锚点 | 在路线上选取3-5个显著位置作为记忆锚点 | 锚点1:办公桌、锚点2:文件柜、锚点3:咖啡机 |
| 4. 创建视觉联想 | 将要记忆的信息与锚点位置创建生动画面 | 在办公桌上"identify识别"文件，用红笔"determine确定"优先级 |
| 5. 心理漫步回忆 | 在脑海中沿路线行走，依次回忆各锚点信息 | 闭眼想象走进办公室，看到桌上的文件... |

### 本系统的记忆宫殿应用

本系统将记忆宫殿原理应用于单词记忆：
- **场景即宫殿**：每个场景（办公室/广场/客厅）是一个独立的记忆宫殿
- **锚点即位置**：每个场景设置3个空间锚点，形成记忆路径
- **单词即联想**：将目标单词自然嵌入场景叙事，与锚点位置建立视觉联想
- **故事即路径**：通过连贯的故事情节串联所有单词，形成记忆链条

---

## 一、核心功能目标

开发一个**沉浸式语境化单词记忆卡片系统**，核心特性：
- 多场景切换（记忆宫殿空间锚点）
- 中英双语切换
- 单词 hover 释义
- 语音朗读（TTS）
- 键盘/按钮双控导航
- 移动端+桌面端响应式适配

### ⚠️ 核心质量要求：单词串联的完整性与准确性

**这是本系统最重要的质量标准！**

1. **完整性要求**
   - 所有目标单词必须100%覆盖，不得遗漏
   - 每个单词必须在场景叙事中自然出现至少1次
   - 单词列表需在开发前明确，开发后需逐一核对

2. **准确性要求**
   - 单词拼写必须正确无误
   - 词性标注必须准确（n./v./adj./adv.等）
   - 释义必须符合语境，优先使用常用义项
   - 固定搭配/短语需完整呈现（如 keep track of）

3. **语境自然性要求**
   - 单词必须自然融入叙事，不能生硬堆砌
   - 单词出现位置应与空间锚点逻辑关联
   - 前后文语义连贯，符合场景设定

4. **校验清单**
   ```
   □ 单词总数是否与目标一致？
   □ 每个单词是否都有高亮标记？
   □ 每个高亮单词是否都有tooltip释义？
   □ 释义格式是否统一（单词: 词性. 释义）？
   □ 中英文版本单词是否一一对应？
   ```

---

## 二、功能模块详解

### 1. 场景管理模块

#### 1.1 数据结构
```javascript
{
    id: Number,           // 场景编号 1-N
    icon: String,         // Font Awesome 图标类名
    bgImage: String,      // 背景图片URL
    isSpecial: Boolean,   // 是否为特殊页（完成页/祝福页）
    zh: {
        title: String,        // 中文标题
        desc: String,         // 场景描述
        anchors: String,      // 空间锚点路径
        content: String,      // HTML内容（含单词高亮）
        translation: String,  // 中文翻译（完整版，用于整体展示）
        translationParagraphs: Array<String>, // 按段落分的中文翻译数组（用于点击展开）
        specialContent: String // 特殊页内容（仅isSpecial时）
    },
    en: { /* 同上英文版本，translation可为null */ }
}
```

**⚠️ translationParagraphs 字段说明**：
- 这是一个字符串数组，每个元素对应 `content` 中的一个 `<p>` 段落
- 数组长度必须与 `content` 中的段落数量一致
- 每个翻译必须是**完整的中文**，包括关键词也要翻译成中文
- 关键词使用 `<span class="word-highlight">中文词<span class="tooltip">英文: 词性. 释义</span></span>` 格式
- 如果没有此字段，系统会回退到使用 `translation` 字段（但会显示"见第一段"提示）

#### 1.2 场景切换逻辑
| 触发方式 | 操作 |
|---------|------|
| 按钮点击 | 「上一场景」「下一场景」按钮 |
| 键盘快捷键 | ← → 方向键 |
| 边界处理 | 首/尾场景按钮置灰 + cursor-not-allowed |

#### 1.3 过渡动画
```css
.scene-transition {
    transition: transform 1s ease-in-out, opacity 1s ease-in-out;
}
/* 当前场景 */
.opacity-100.translate-x-0
/* 左侧隐藏 */
.opacity-0.-translate-x-full
/* 右侧隐藏 */
.opacity-0.translate-x-full
```

### 2. 中英双语切换模块

#### 2.1 UI元素
- **位置**：右下角固定悬浮按钮
- **尺寸**：w-14 h-14 圆形
- **样式**：bg-primary 红色背景，hover 缩放效果

#### 2.2 交互逻辑
| 操作 | 效果 |
|-----|------|
| 点击按钮 | zh ↔ en 切换 |
| Ctrl+L | 快捷键切换 |
| 图标变化 | 中文: fa-language / 英文: fa-globe |

#### 2.3 切换行为
- 保持当前场景编号不变
- 仅切换同一场景的语言版本
- 同步更新：指示器文本、按钮文本、标题
- **⚠️ 语言切换时不使用过渡动画**（因为背景图片相同，只有卡片内容变化）

#### 2.4 动画控制
```javascript
// 语言切换时禁用动画
const LanguageController = {
    toggle() {
        State.currentLang = State.currentLang === 'zh' ? 'en' : 'zh';
        SceneController.update(true); // skipAnimation = true
        this.updateIcon();
    }
};

// SceneController.update 支持跳过动画
update(skipAnimation = false) {
    if (skipAnimation) {
        scene.classList.add('no-transition');
    }
    // ... 更新场景显示
    if (skipAnimation) {
        setTimeout(() => scene.classList.remove('no-transition'), 50);
    }
}
```

```css
/* 禁用动画的工具类 */
.no-transition {
    transition: none !important;
}
```

---

### 3. 单词卡片交互模块

#### 3.1 单词高亮样式
```css
.word-highlight {
    position: relative;
    cursor: help;
    font-weight: 600;
    color: #E53E3E;           /* primary红色 */
    padding: 0 0.25rem;
    border-radius: 0.25rem;
    display: inline-block;
}
.word-highlight:hover {
    background-color: rgba(229, 62, 62, 0.1);  /* 浅红背景 */
}
```

#### 3.2 Tooltip 释义
```css
.tooltip {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    bottom: 100%;
    margin-bottom: 0.5rem;
    width: max-content;
    max-width: 28rem;
    background-color: #2D3748;  /* neutral深灰 */
    color: white;
    font-size: 0.75rem;
    border-radius: 0.25rem;
    padding: 0.5rem;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    z-index: 50;
    display: none;
}
.word-highlight:hover .tooltip {
    display: block;
}
```

#### 3.3 释义内容格式
```
单词: 词性. 中文释义
示例：identify: v. 识别，确定
短语：keep track of: 跟踪，了解
标注：polished: adj. 抛光的，精致的（补充词）
```

### 3.4 卡片收起/展开功能（刘海式）

#### 功能说明
用户可以收起卡片，卡片吸顶只露出类似iPhone刘海的下拉区域，方便欣赏背景图片。

#### 交互逻辑
| 操作 | 效果 |
|-----|------|
| 点击收起按钮（↑） | 卡片吸顶，只露出刘海下拉区 |
| 点击刘海区域（↓） | 卡片展开 |
| ESC 键 | 切换当前卡片收起/展开 |

#### CSS样式
```css
/* 收起状态 - 吸顶露出刘海 */
.card-collapsed { 
    transform: translateY(calc(-100% + 40px)) !important;
}
.card-collapsed .card-inner { 
    opacity: 0; 
    pointer-events: none; 
}

/* 刘海下拉区 */
.card-notch {
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 8rem;
    height: 2.5rem;
    background: rgba(255,255,255,0.9);
    border-radius: 0 0 1rem 1rem;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    cursor: pointer;
}
```

#### HTML结构
```html
<div class="card-content">
    <div class="card-inner">
        <!-- 卡片内容 -->
    </div>
    <div class="card-notch">
        <i class="fa fa-chevron-down"></i>
    </div>
</div>
```

---

### 3.5 段落点击展开翻译功能

#### 功能说明
用户可以点击任意段落，展开该段落的中英双语翻译对照。两种语言同时显示，方便对照学习。

#### 数据结构要求
每个场景的 `zh` 对象中需要包含 `translationParagraphs` 数组：
```javascript
zh: {
    content: `<p>段落1...</p><p>段落2...</p>`,
    translationParagraphs: [
        `段落1的完整中文翻译，关键词<span class="word-highlight">高亮<span class="tooltip">highlight: v. 高亮</span></span>`,
        `段落2的完整中文翻译...`
    ]
}
```

**⚠️ 重要规范**：
- 数组长度必须与 `content` 中的 `<p>` 段落数量一致
- 每个翻译必须是**完整的中文句子**，不能出现英文单词
- 关键词必须翻译成中文并带高亮，如：`rise` → `<span class="word-highlight">上涨<span class="tooltip">rise: v. 上升</span></span>`
- 不允许出现"见第一段"等回退提示

#### 交互逻辑
| 设备 | 操作 | 效果 |
|-----|------|------|
| 桌面端 | 单击段落 | 展开/收起 EN + CN 双语翻译 |
| 移动端 | 双击段落 | 展开/收起 EN + CN 双语翻译（300ms内双击） |

#### 视觉反馈
- 展开时：段落背景变为浅蓝色（bg-blue-50），增加内边距
- EN翻译：蓝色左边框（accent色），带"EN:"标签，显示在前
- CN翻译：红色左边框（primary色），带"CN:"标签，显示在后
- 动画：max-height + opacity 过渡动画，平滑展开/收起

#### CSS样式
```css
/* 段落包装器 */
.para-wrapper {
    cursor: pointer;
    user-select: none;
    transition: all 0.2s;
    border-radius: 0.25rem;
    margin-bottom: 0.75rem;
}
.para-wrapper:hover {
    background-color: #f9fafb; /* gray-50 */
}
.para-wrapper.expanded {
    background-color: #eff6ff; /* blue-50 */
    padding: 0.5rem;
    margin-left: -0.5rem;
    margin-right: -0.5rem;
}

/* 翻译区域 */
.para-trans {
    font-size: 0.875rem;
    overflow: hidden;
    max-height: 0;
    opacity: 0;
    transition: max-height 0.3s ease, opacity 0.3s ease;
}
.para-trans.expanded {
    max-height: 1000px;
    opacity: 1;
    padding-top: 0.5rem;
    margin-top: 0.5rem;
}

/* 中英文翻译样式 */
.trans-zh {
    color: #E53E3E; /* primary红色 */
    border-left: 2px solid #E53E3E;
    padding-left: 0.5rem;
    margin-bottom: 0.5rem;
}
.trans-en {
    color: #4299E1; /* accent蓝色 */
    border-left: 2px solid #4299E1;
    padding-left: 0.5rem;
}
.trans-label {
    font-weight: bold;
    font-size: 0.75rem;
    opacity: 0.7;
    margin-right: 0.25rem;
}
```

#### HTML结构
```html
<div class="para-wrapper" data-para-idx="0">
    <div class="para-main">
        <!-- 当前语言的段落内容，含单词高亮 -->
        清晨的阳光透过高窗洒入图书馆...
    </div>
    <div class="para-trans">
        <div class="trans-zh">
            <span class="trans-label">中:</span>
            清晨的阳光透过高窗洒入图书馆，你看见一只鸟
            <span class="word-highlight">拍打翅膀<span class="tooltip">flap: v. 拍打翅膀</span></span>
            飞过...
        </div>
        <div class="trans-en">
            <span class="trans-label">EN:</span>
            Morning sunlight streams through tall windows. You see a bird 
            <span class="word-highlight">flap<span class="tooltip">flap: v. 拍打翅膀</span></span>
            its wings...
        </div>
    </div>
</div>
```

#### JavaScript实现
```javascript
const EventBinder = {
    lastTapTime: 0,
    
    initParagraphClick() {
        document.addEventListener('click', (e) => {
            const wrapper = e.target.closest('.para-wrapper');
            if (!wrapper) return;
            
            // 忽略tooltip内的点击
            if (e.target.closest('.tooltip')) return;
            
            // 检测移动设备
            const isMobile = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
            
            if (isMobile) {
                // 移动端：双击展开
                const now = Date.now();
                if (now - this.lastTapTime < 300) {
                    this.toggleTranslation(wrapper);
                }
                this.lastTapTime = now;
            } else {
                // 桌面端：单击展开
                this.toggleTranslation(wrapper);
            }
        });
    },
    
    toggleTranslation(wrapper) {
        const trans = wrapper.querySelector('.para-trans');
        if (!trans) return;
        
        const isExpanded = wrapper.classList.contains('expanded');
        wrapper.classList.toggle('expanded', !isExpanded);
        trans.classList.toggle('expanded', !isExpanded);
    }
};
```

#### 提示文字
在卡片内容顶部显示操作提示：
- 中文界面：`💡 点击段落查看英文`
- 英文界面：`💡 Click paragraph for Chinese`

---

### 4. 语音朗读模块（TTS）

#### 4.1 功能要求
| 特性 | 说明 |
|-----|------|
| 触发方式 | 点击音量按钮 |
| 语言检测 | 根据 currentLang 选择 zh-CN / en-US |
| 朗读速率 | 0.85倍速（适配记忆节奏） |
| 内容过滤 | 正则过滤 tooltip 内容 |
| 状态反馈 | 朗读中图标切换 |

#### 4.2 实现逻辑
```javascript
// 1. 检测浏览器支持
if (!('speechSynthesis' in window)) { alert('不支持'); return; }

// 2. 获取朗读文本
const text = currentScene.querySelector('.text-gray-700')?.textContent;

// 3. 过滤tooltip内容
text = text.replace(/[a-zA-Z]+:\s.*?（[^）]*）/g, '');

// 4. 创建朗读实例
const utterance = new SpeechSynthesisUtterance(text);
utterance.lang = currentLang === 'zh' ? 'zh-CN' : 'en-US';
utterance.rate = 0.85;

// 5. 事件处理
utterance.onstart = () => { /* 切换图标 */ };
utterance.onend = () => { /* 恢复图标 */ };

// 6. 开始朗读
speechSynthesis.speak(utterance);
```

#### 4.3 特殊场景处理
- 完成页/祝福页无文本内容时，弹窗提示「当前场景无朗读内容」

---

### 5. 视觉设计规范

#### 5.1 主题配色
```javascript
colors: {
    primary: '#E53E3E',    // 马年红 - 主色调
    secondary: '#ED8936',  // 金秋橙 - 渐变辅助
    accent: '#4299E1',     // 宁静蓝 - 强调色
    neutral: '#2D3748',    // 深灰 - 文字/tooltip背景
}
```

#### 5.2 页面布局
```
┌─────────────────────────────────────────┐
│  Header (sticky top-0 z-40)             │
│  ┌─────────────────────────────────────┐│
│  │ Logo + Title    [←][→] 场景X/N [🔊] ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  Main (h-[calc(100vh-64px)])            │
│  ┌─────────────────────────────────────┐│
│  │     ┌───────────────────┐           ││
│  │     │   Scene Card      │           ││
│  │     │   (w-[70%])       │           ││
│  │     │   bg-white/80     │           ││
│  │     │   backdrop-blur   │           ││
│  │     └───────────────────┘           ││
│  │         (Background Image)          ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│                              [🌐] Lang  │ ← fixed bottom-6 right-6
└─────────────────────────────────────────┘
```

#### 5.3 卡片样式
```css
/* 卡片容器 */
.card-center-container {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
}

/* 卡片主体 */
.card-content {
    width: 70%;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(4px);
    border-radius: 0.75rem;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    padding: 1rem 1.5rem;
    max-height: 90%;
    overflow-y: auto;
}

/* Hover效果 */
.hover-scale {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.hover-scale:hover {
    transform: scale(1.05);
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
}
```

#### 5.4 响应式断点
| 断点 | 卡片宽度 | 字体大小 | 内边距 |
|-----|---------|---------|--------|
| 移动端 (<768px) | 90% | text-sm | p-4 |
| 桌面端 (≥768px) | 70% | text-base | p-6 |

---

### 6. 记忆宫殿内容设计

#### 6.1 场景锚点结构
每个场景设置 **3个空间锚点**，形成记忆路径：
```
场景1: 办公桌 → 文件柜 → 咖啡机
场景2: 喷泉 → 长椅 → 花店
场景3: 沙发 → 书桌 → 阳台
```

#### 6.2 内容层次
```html
<!-- 场景标题 -->
<h3>
    <i class="fa fa-briefcase"></i>
    晨光办公室（锚点：办公桌→文件柜→咖啡机）
</h3>

<!-- 英文语境段落（单词高亮） -->
<div class="text-gray-700">
    推开玻璃门，晨光斜铺在
    <span class="word-highlight">polished
        <span class="tooltip">polished: adj. 抛光的</span>
    </span>
    木质办公桌上...
</div>

<!-- 中文翻译（必须完整且高亮） -->
<div class="text-gray-600 border-t pt-2">
    推开玻璃门，晨光斜铺在<span class="word-highlight">光亮的<span class="tooltip">polished: adj. 抛光的</span></span>木质办公桌上...
</div>
```

**⚠️ 中文翻译要求**：
- 翻译必须**完整覆盖**整个场景的所有内容，不能只写开头加省略号
- 翻译是对英文叙事的完整中文对照，帮助用户理解语境
- **每个高亮单词在翻译中都必须有对应的中文高亮**，格式与英文相同
- 中文高亮的tooltip显示英文单词和释义，方便用户对照学习
- 翻译文字流畅自然，不是逐词直译

**中文翻译高亮示例**：
```html
<!-- 英文原文 -->
<span class="word-highlight">polished<span class="tooltip">polished: adj. 抛光的</span></span>

<!-- 对应的中文翻译 -->
<span class="word-highlight">光亮的<span class="tooltip">polished: adj. 抛光的</span></span>
```

#### 6.3 特殊场景类型
| 类型 | 用途 | 内容 |
|-----|------|------|
| 完成页 | 学习汇总 | 锚点回顾、统计信息 |
| 祝福页 | 主题收尾 | 祝福语、品牌信息 |

#### 6.4 背景图片生成规范

**⚠️ 核心原则：背景图片必须展示场景的整体环境，而非特定物体！**

背景图片应该是场景名称所描述的完整空间，让用户有身临其境的感觉。

**正确做法 ✅**：
- 场景名"晨光图书馆" → 生成阳光洒满书架的图书馆全景
- 场景名"自然博物馆" → 生成博物馆大厅或展厅的整体环境
- 场景名"城市广场" → 生成城市广场的全景视角

**错误做法 ❌**：
- 只拍摄一本书、一个展品、一个喷泉等特定物体
- 过于抽象或艺术化的图片
- 与场景名称不符的图片

| 场景名称 | 背景图片要求 | 推荐关键词 |
|---------|-------------|-----------|
| 晨光图书馆 | 图书馆内景全貌，书架林立，阳光透过窗户洒入 | library interior, sunlight, bookshelves, reading room |
| 自然博物馆 | 博物馆展厅，恐龙骨架或动物标本，高挑空间 | natural history museum, dinosaur skeleton, exhibition hall |
| 大学研究所 | 大学建筑或实验室走廊，学术氛围 | university campus, research lab, academic building |
| 医学中心 | 现代医院大厅或走廊，明亮整洁 | hospital lobby, medical center, healthcare facility |
| 城市广场 | 城市广场全景，喷泉、行人、建筑 | city square, plaza, fountain, urban landscape |
| 科技园区 | 现代办公园区，玻璃幕墙，科技感 | tech park, modern office, glass building |
| 国际会议中心 | 会议中心大厅，宏伟空间 | convention center, conference hall, grand lobby |
| 历史博物馆 | 博物馆内部，古典建筑，展品陈列 | history museum, classical architecture, exhibition |

**图片生成Prompt模板**：
```
场景：[场景名称]
画面：[场景名称]的整体内景/全景
风格：写实摄影风格，高清4K，16:9横版构图
要求：
- 展示完整的空间环境，不是特定物体的特写
- 有纵深感，让人感觉可以走进去
- 光线自然，氛围符合场景特点
- 无人物面部，无文字水印
视角：广角镜头，展示空间全貌
```

**示例Prompt**：
```
场景：晨光图书馆
画面：大型图书馆内景全貌，高大的书架排列整齐，晨光从高窗洒入，照亮木质阅读桌和地板
风格：写实摄影风格，高清4K，16:9横版构图
要求：展示图书馆的整体空间，有书架、阅读区、走廊的纵深感
视角：广角镜头，站在入口处向内看的视角
```

---

## 三、技术实现规范

### 1. 技术栈
| 类别 | 选型 |
|-----|------|
| 样式框架 | Tailwind CSS (CDN) |
| 图标库 | Font Awesome 4.7.0 |
| 交互逻辑 | 原生 JavaScript (ES6+) |
| 语音合成 | Web Speech API |

### 2. 模块化代码架构
```javascript
// ========== 配置模块 ==========
const CONFIG = { app: {}, i18n: {} };
const SCENES_DATA = [ /* 场景数据数组 */ ];

// ========== 状态管理模块 ==========
const State = {
    currentScene: 1,
    currentLang: 'zh',
    totalScenes: N,
    isSpeaking: false
};

// ========== DOM引用模块 ==========
const DOM = {
    container, prevBtn, nextBtn, audioBtn, 
    sceneIndicator, langToggleBtn, appTitle,
    init() { /* 初始化DOM引用 */ }
};

// ========== 场景渲染模块 ==========
const SceneRenderer = {
    createSceneHTML(sceneData, lang) { /* 生成单场景HTML */ },
    renderAll() { /* 渲染所有场景 */ }
};

// ========== 场景控制模块 ==========
const SceneController = {
    update() { /* 更新场景显示 */ },
    updateUI() { /* 更新UI状态 */ },
    prev() { /* 上一场景 */ },
    next() { /* 下一场景 */ }
};

// ========== 语言切换模块 ==========
const LanguageController = {
    toggle() { /* 切换语言 */ },
    updateIcon() { /* 更新图标 */ }
};

// ========== 语音朗读模块 ==========
const TTSController = {
    speak() { /* 朗读当前场景 */ },
    setActiveIcon() { /* 设置朗读中图标 */ },
    resetIcon() { /* 恢复默认图标 */ }
};

// ========== 事件绑定模块 ==========
const EventBinder = {
    init() { /* 绑定所有事件 */ }
};

// ========== 应用初始化 ==========
document.addEventListener('DOMContentLoaded', () => {
    DOM.init();
    SceneRenderer.renderAll();
    SceneController.update();
    EventBinder.init();
});
```

### 3. 自定义CSS工具类清单
```css
/* 必需工具类 */
.scene-transition    /* 场景过渡动画 */
.hover-scale         /* 卡片悬浮效果 */
.word-highlight      /* 单词高亮 */
.tooltip             /* 释义提示框 */
.card-center-container /* 卡片居中容器 */
.fixed-lang-btn      /* 语言切换按钮 */
.scene-bg            /* 场景背景图 */

/* 可选装饰动画 */
.animate-float       /* 漂浮动画 */
.animate-float-slow  /* 慢速漂浮 */
.animate-bounce-slow /* 慢速弹跳 */
.animate-spin-slow   /* 慢速旋转 */
```

### 4. 兼容性要求
- ✅ Chrome 80+
- ✅ Edge 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ 移动端触屏操作
- ⚠️ TTS功能需浏览器支持（降级处理）

### 5. 性能优化建议
- 动画使用 CSS3 transition/animation（GPU加速）
- 避免频繁 DOM 操作，批量更新
- 图片可考虑懒加载
- 场景切换使用 CSS 类切换而非 JS 动画

---

## 四、扩展功能建议

### 1. 数据外置
将 `SCENES_DATA` 抽离为独立 JSON 文件，支持动态加载不同词库

### 2. 进度保存
使用 localStorage 保存学习进度（当前场景、语言偏好）

### 3. 单词收藏
点击单词可收藏到本地，支持导出复习列表

### 4. 测验模式
隐藏释义，点击单词显示，增加主动回忆

### 5. 主题切换
支持多套配色主题（马年红/龙年金/虎年橙等）

---

## 六、内容创作规范

### 1. 单词串联写作流程

```
步骤1: 明确单词列表
    ↓ 列出所有目标单词，标注词性和核心释义
步骤2: 规划场景分配
    ↓ 按主题/词性将单词分配到不同场景
步骤3: 设计空间锚点
    ↓ 每个场景设置3个锚点，规划行走路线
步骤4: 编写叙事文本
    ↓ 围绕锚点编写故事，自然嵌入单词
步骤5: 校验完整性
    ↓ 逐一核对单词是否全部覆盖
步骤6: 添加高亮标记
    ↓ 为每个单词添加word-highlight和tooltip
步骤7: 创建英文版本
    ↓ 翻译叙事文本，保持单词位置对应
步骤8: 最终审核
    检查拼写、释义、格式一致性
```

### 2. 叙事文本写作原则

| 原则 | 说明 | 示例 |
|-----|------|------|
| 第二人称视角 | 使用"你"作为主语，增强代入感 | "你坐下来，指尖先identify识别..." |
| 动作串联 | 用动作连接各个锚点 | "推开门→坐下→转身走向→走到窗边" |
| 五感描写 | 加入视觉/触觉/听觉等感官细节 | "指尖划过冰凉的金属柜门" |
| 情感共鸣 | 融入职场/生活中的真实情感 | "绝不流露negative情绪，始终保持positive态度" |
| 逻辑连贯 | 单词出现要符合场景逻辑 | 在文件柜旁出现access/track/account |

### 2.1 ⚠️ 叙事连贯性核心规范（重要！）

**问题诊断**：以下是典型的"单词堆砌"式写法，必须避免：
```
❌ 错误示例（生硬、断裂）：
河床silt样本放在架上。研究方法要inclusive。团队有些disagreement。
导师cosset着优秀学生，但大家disagree这种做法。每个研究都是unique的。
```
这种写法的问题：
- 句子之间没有逻辑关联，像是随机拼凑
- 单词突兀出现，没有上下文铺垫
- 读起来像"单词清单"而非"故事"

**正确做法**：每个句子必须与前后句有因果、递进、转折或时间关系：
```
✅ 正确示例（流畅、连贯）：
你走到样本架前，发现河床silt样本整齐排列——这是团队inclusive研究方法的体现，
力求涵盖所有地质类型。然而，关于样本分类标准，团队内部存在disagreement。
导师倾向于cosset那些支持他观点的学生，但你和其他成员disagree这种偏袒做法。
毕竟，每个研究课题都是unique的，不应受人情因素影响。
```

**连贯性写作技巧**：

| 技巧 | 说明 | 连接词/句式 |
|-----|------|------------|
| 因果链接 | 前句是原因，后句是结果 | 因此、所以、于是、这导致了、正因如此 |
| 递进深入 | 后句在前句基础上更进一步 | 不仅如此、更重要的是、进一步地、甚至 |
| 转折对比 | 后句与前句形成对比或转折 | 然而、但是、不过、相反、尽管如此 |
| 时间顺序 | 按时间先后组织叙事 | 随后、接着、这时、片刻后、与此同时 |
| 空间移动 | 用移动动作串联不同位置 | 走向、转身看到、目光移到、穿过...来到 |
| 观察发现 | 用"发现/注意到/看见"引出新元素 | 你注意到、映入眼帘的是、仔细一看 |

**段落结构模板**：
```
[空间定位] + [观察/动作] + [单词1自然出现] + [逻辑连接] + [单词2承接] + [情感/评价收尾]

示例：
[走到样本架前]，[你发现]河床[silt]样本整齐排列——[这正是]团队[inclusive]研究方法的体现。
[然而]，关于分类标准，团队存在[disagreement]。[你心想]，科学研究应该客观[unique]，不受偏见影响。
```

**单词嵌入的自然度检查**：
每写完一个单词，问自己：
1. 这个单词为什么会在这里出现？（场景逻辑）
2. 它与前一句有什么关系？（句间逻辑）
3. 它如何引出下一句？（承上启下）

如果答不上来，说明嵌入不够自然，需要重写。

### 3. 单词高亮格式规范

```html
<!-- 标准格式 -->
<span class="word-highlight">单词<span class="tooltip">单词: 词性. 释义</span></span>

<!-- 示例 -->
<span class="word-highlight">identify<span class="tooltip">identify: v. 识别，确定</span></span>

<!-- 短语格式 -->
<span class="word-highlight">keep track of<span class="tooltip">keep track of: 跟踪，了解</span></span>

<!-- 补充词标注 -->
<span class="word-highlight">desk<span class="tooltip">desk: n. 办公桌（补充词）</span></span>
```

### 4. 场景背景图片Prompt模板

为确保背景图片与场景第一画面匹配，使用以下模板生成：

```
【场景背景图片生成Prompt】

场景名称：{场景中文名}
第一画面：{场景叙事的第一句话}

图片要求：
- 风格：写实摄影风格，高清4K，16:9横版构图
- 视角：第一人称视角，仿佛刚走进/来到这个空间
- 光线：{根据场景时间：晨光柔和/午后温暖/傍晚暖黄}
- 氛围：{场景情感基调}
- 主体：{第一个锚点物体}必须在画面中清晰可见
- 细节：{场景特有的环境细节}

负面提示：
- 无人物面部
- 无文字水印
- 无过度后期处理
```

**各场景Prompt示例**：

**场景1：晨光办公室**
```
场景名称：晨光办公室
第一画面：推开玻璃门，晨光斜铺在polished木质desk上

图片要求：
- 风格：写实摄影风格，高清4K，16:9横版构图
- 视角：第一人称视角，仿佛刚推开玻璃门走进办公室
- 光线：清晨柔和的自然光，金色调，光线从左侧窗户斜射入
- 氛围：专业、宁静、充满希望的工作日开始
- 主体：木质办公桌必须在画面中央，桌面光亮反光
- 细节：玻璃门、散落的文件、红笔、现代办公室装修
```

**场景2：午后城市广场**
```
场景名称：午后城市广场
第一画面：午后的阳光穿过梧桐叶，落在广场中央的fountain上

图片要求：
- 风格：写实摄影风格，高清4K，16:9横版构图
- 视角：第一人称视角，仿佛刚走进广场
- 光线：午后温暖的阳光，树叶间的斑驳光影
- 氛围：悠闲、宁静、生活气息
- 主体：广场中央的喷泉必须清晰可见，水珠在阳光下闪烁
- 细节：梧桐树、石质长椅、远处的花店、下棋的老人（背影）
```

**场景3：暖光客厅**
```
场景名称：暖光客厅
第一画面：傍晚回到家，你窝进柔软的sofa里

图片要求：
- 风格：写实摄影风格，高清4K，16:9横版构图
- 视角：第一人称视角，仿佛刚走进家门
- 光线：傍晚暖黄色的夕阳光，透过窗帘洒入
- 氛围：温馨、放松、归属感
- 主体：柔软的布艺沙发必须在画面中央，看起来很舒适
- 细节：茶几、坚果、窗帘、地毯、原木书桌（远景）、阳台门
```

---

## 七、文件结构建议

```
project/
├── index.html          # 主页面
├── css/
│   └── custom.css      # 自定义样式（可选，也可内联）
├── js/
│   ├── config.js       # 配置与数据
│   ├── state.js        # 状态管理
│   ├── renderer.js     # 场景渲染
│   ├── controller.js   # 场景/语言控制
│   ├── tts.js          # 语音朗读
│   └── main.js         # 初始化入口
├── data/
│   └── scenes.json     # 场景数据（可选外置）
└── images/
    ├── scene1-office.jpg      # 场景1背景图
    ├── scene2-square.jpg      # 场景2背景图
    └── scene3-livingroom.jpg  # 场景3背景图
```

---

## 八、质量检查清单

### 开发完成后必须逐项检查：

#### A. 单词完整性检查
- [ ] 统计页面中所有 `.word-highlight` 元素数量
- [ ] 与目标单词列表逐一比对，确认无遗漏
- [ ] 检查是否有重复高亮（同一单词多次出现是否都需要高亮）

#### B. 单词准确性检查
- [ ] 所有单词拼写正确
- [ ] 所有词性标注正确
- [ ] 所有释义准确且符合语境
- [ ] 短语/搭配完整（如 keep track of, figure out）

#### C. 中英对应检查
- [ ] 中文版和英文版场景数量一致
- [ ] 同一场景的中英版单词完全对应
- [ ] 单词在中英版中的位置逻辑一致

#### D. 交互功能检查
- [ ] 所有单词 hover 时 tooltip 正常显示
- [ ] tooltip 位置正确（单词正上方居中）
- [ ] tooltip 内容格式统一
- [ ] 场景切换动画流畅
- [ ] 语言切换功能正常
- [ ] 语音朗读功能正常（中英文）
- [ ] 键盘快捷键响应正常

#### E. 视觉一致性检查
- [ ] 背景图片与场景第一画面匹配
- [ ] 卡片样式在各场景保持一致
- [ ] 响应式布局在移动端正常显示
- [ ] 颜色主题统一

---

## 九、参考资料

### 记忆宫殿相关
- Method of Loci（位置记忆法）- 源自古希腊的助记技术
- 核心原理：利用空间记忆优势，将信息与熟悉场所的具体位置关联
- 关键要素：熟悉场所 + 固定路线 + 空间锚点 + 视觉联想 + 心理漫步

### 技术参考
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [Font Awesome 4.7.0 图标](https://fontawesome.com/v4/icons/)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)

---

*文档版本：v2.0*
*更新日期：2026-02-24*
*核心强调：单词串联的完整性与准确性是本系统的生命线*