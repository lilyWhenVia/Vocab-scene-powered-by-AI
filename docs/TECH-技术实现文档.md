# 记忆宫殿单词系统 - 技术实现文档

> 本文档详细说明代码的技术实现细节，便于后期维护和改造。

## 一、文件结构

```
项目根目录/
├── memory-palace-356.html      # 主页面（单文件应用）
├── PROMPT-记忆宫殿单词系统.md   # 需求文档
├── WORKFLOW-单词记忆宫殿化.md   # 工作流指南
├── CHANGELOG-功能改造记录.md    # 改动记录
└── TECH-技术实现文档.md         # 本文档
```

## 二、代码架构概览

### 2.1 整体结构（单HTML文件）

```
memory-palace-356.html
├── <head>
│   ├── Tailwind CSS CDN
│   ├── Font Awesome CDN
│   └── <style> 自定义CSS工具类
├── <body>
│   ├── <header> 顶部导航栏
│   ├── <main> 场景容器
│   ├── 语言切换按钮
│   └── 展开箭头
└── <script>
    ├── CONFIG 配置对象
    ├── SCENES_DATA 场景数据数组
    ├── State 状态管理
    ├── DOM 引用模块
    ├── SceneRenderer 渲染模块
    ├── SceneController 控制模块
    ├── LanguageController 语言模块
    ├── TTSController 语音模块
    └── EventBinder 事件模块
```

### 2.2 模块依赖关系

```
EventBinder
    ├── SceneController.prev/next
    ├── LanguageController.toggle
    ├── TTSController.speak
    └── collapseCurrentCard/expandCurrentCard

SceneController
    ├── State (读写)
    ├── DOM (操作)
    └── SceneRenderer (调用)

SceneRenderer
    ├── SCENES_DATA (读取)
    └── DOM.container (写入)
```

---

## 三、核心数据结构

### 3.1 SCENES_DATA 场景数据

```javascript
const SCENES_DATA = [
    {
        id: 1,                    // 场景ID
        icon: 'fa-book',          // Font Awesome图标
        bgImage: 'https://...',   // 背景图URL
        isSpecial: false,         // 是否特殊页（完成页/祝福页）
        
        zh: {
            title: '晨光图书馆',
            anchors: '阅览桌→书架走廊→天文角',
            content: `<p class="mb-3">段落1内容...</p>
                      <p class="mb-3">段落2内容...</p>`,
            translation: '完整翻译（用于整体展示）',
            translationParagraphs: [
                '段落1的完整中文翻译',
                '段落2的完整中文翻译'
            ]
        },
        
        en: {
            title: 'Morning Library',
            anchors: 'Reading Table → Bookshelf → Astronomy Corner',
            content: `<p class="mb-3">Paragraph 1...</p>
                      <p class="mb-3">Paragraph 2...</p>`
        }
    },
    // ... 更多场景
];
```

### 3.2 translationParagraphs 详解

**用途**：支持点击段落时显示对应的独立中文翻译

**数据格式**：
```javascript
translationParagraphs: [
    // 索引0对应content中的第1个<p>
    `走进现代化的医学中心，消毒水的气味弥漫。`,
    
    // 索引1对应content中的第2个<p>
    `【候诊厅】<span class="word-highlight">理论上<span class="tooltip">theoretically: adv. 理论上</span></span>来说...`,
    
    // ... 依此类推
]
```

**关键规则**：
1. 数组长度 = content中`<p>`标签数量
2. 每个元素是完整中文句子
3. 关键词必须翻译成中文并带高亮
4. 段落标记（如【候诊厅】）保留在对应翻译中

---

## 四、核心模块实现

### 4.1 SceneRenderer - 场景渲染

**位置**：`<script>` 标签内，约第500行

**核心方法**：`createSceneHTML(sceneData, lang)`

```javascript
const SceneRenderer = {
    createSceneHTML(sceneData, lang) {
        const data = sceneData[lang];
        
        // 1. 解析content中的段落
        const paragraphs = data.content.match(/<p[^>]*>[\s\S]*?<\/p>/g) || [];
        
        // 2. 获取英文段落（用于EN翻译）
        const enParagraphs = sceneData.en.content.match(/<p[^>]*>[\s\S]*?<\/p>/g) || [];
        
        // 3. 获取中文翻译段落
        const cnParagraphs = sceneData.zh.translationParagraphs || [];
        const hasParagraphTrans = cnParagraphs.length > 0;
        
        // 4. 为每个段落生成HTML
        let contentWithTranslations = '';
        paragraphs.forEach((p, idx) => {
            const enContent = (enParagraphs[idx] || '').replace(/<\/?p[^>]*>/g, '');
            
            // 优先使用translationParagraphs
            let cnContent = '';
            if (hasParagraphTrans) {
                cnContent = cnParagraphs[idx] || '';
            } else if (idx === 0) {
                cnContent = sceneData.zh.translation || '';
            } else {
                cnContent = '<span class="text-gray-400 text-xs">（完整翻译见第一段）</span>';
            }
            
            contentWithTranslations += `
                <div class="para-wrapper" data-para-idx="${idx}">
                    <div class="para-main">${p.replace(/<\/?p[^>]*>/g, '')}</div>
                    <div class="para-trans">
                        <div class="trans-en"><span class="trans-label">EN:</span> ${enContent}</div>
                        <div class="trans-cn"><span class="trans-label">CN:</span> ${cnContent}</div>
                    </div>
                </div>`;
        });
        
        // 5. 返回完整场景HTML
        return `<div class="scene" data-scene="${sceneData.id}" data-lang="${lang}">
            <img src="${sceneData.bgImage}" class="scene-bg">
            <div class="card-center-container">
                <div class="card-content">
                    ${contentWithTranslations}
                </div>
            </div>
        </div>`;
    }
};
```

### 4.2 EventBinder - 事件绑定

**段落点击处理**：

```javascript
const EventBinder = {
    lastTapTime: 0,
    
    initParagraphClick() {
        document.addEventListener('click', (e) => {
            const wrapper = e.target.closest('.para-wrapper');
            if (!wrapper) return;
            if (e.target.closest('.tooltip')) return; // 忽略tooltip点击
            
            const isMobile = 'ontouchstart' in window;
            
            if (isMobile) {
                // 移动端双击
                const now = Date.now();
                if (now - this.lastTapTime < 300) {
                    this.toggleTranslation(wrapper);
                }
                this.lastTapTime = now;
            } else {
                // 桌面端单击
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

**卡片收起/展开**：

```javascript
const EventBinder = {
    collapseCurrentCard() {
        const card = document.querySelector('.scene.opacity-100 .card-content');
        if (card) {
            card.classList.add('card-collapsed');
            DOM.expandNotch.classList.add('visible');
        }
    },
    
    expandCurrentCard() {
        const card = document.querySelector('.scene.opacity-100 .card-content');
        if (card) {
            card.classList.remove('card-collapsed');
            DOM.expandNotch.classList.remove('visible');
        }
    },
    
    toggleCurrentCard() {
        const card = document.querySelector('.scene.opacity-100 .card-content');
        if (card?.classList.contains('card-collapsed')) {
            this.expandCurrentCard();
        } else {
            this.collapseCurrentCard();
        }
    }
};
```

---

## 五、CSS关键样式

### 5.1 段落翻译样式

```css
/* 段落包装器 */
.para-wrapper {
    @apply cursor-pointer select-none transition-all duration-200 rounded mb-3;
}
.para-wrapper:hover {
    @apply bg-gray-50;
}
.para-wrapper.expanded {
    @apply bg-blue-50 p-2 -mx-2;
}

/* 翻译区域（默认隐藏） */
.para-trans { 
    @apply text-sm overflow-hidden;
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

/* EN翻译（蓝色边框） */
.trans-en {
    @apply text-accent border-l-2 border-accent pl-2;
}

/* CN翻译（红色边框） */
.trans-cn {
    @apply text-primary border-l-2 border-primary pl-2 mt-2;
}
```

### 5.2 卡片收起样式

```css
/* 卡片完全隐藏 */
.card-collapsed { 
    transform: translateY(-100%) !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

/* 顶部展开箭头 */
.expand-notch {
    @apply fixed top-16 left-1/2 -translate-x-1/2 w-8 h-6 
           flex items-center justify-center cursor-pointer z-50;
    opacity: 0;
    pointer-events: none;
}
.expand-notch.visible {
    opacity: 1;
    pointer-events: auto;
}
.expand-notch i {
    @apply text-primary text-xl;
}
```

### 5.3 单词高亮样式

```css
.word-highlight {
    @apply relative cursor-help font-semibold text-primary 
           hover:bg-primary/10 px-0.5 rounded inline;
}

.tooltip {
    @apply absolute left-1/2 -translate-x-1/2 bottom-full mb-2 
           w-max max-w-xs bg-neutral text-white text-xs 
           rounded p-2 shadow-lg z-50 hidden whitespace-nowrap;
}
.word-highlight:hover .tooltip {
    display: block;
}
```

---

## 六、常见维护场景

### 6.1 添加新场景

1. 在 `SCENES_DATA` 数组末尾添加新对象
2. 确保 `id` 递增
3. 填写 `zh.content` 和 `en.content`
4. **必须**添加 `zh.translationParagraphs` 数组
5. 数组长度 = content中`<p>`标签数量

### 6.2 修改段落翻译

1. 找到对应场景的 `translationParagraphs` 数组
2. 修改对应索引的字符串
3. 确保关键词高亮格式正确：
   ```html
   <span class="word-highlight">中文词<span class="tooltip">英文: 词性. 释义</span></span>
   ```

### 6.3 添加新单词

1. 在 `content` 中添加高亮：
   ```html
   <span class="word-highlight">newWord<span class="tooltip">newWord: n. 新词</span></span>
   ```
2. 在对应的 `translationParagraphs` 元素中添加中文高亮：
   ```html
   <span class="word-highlight">新词<span class="tooltip">newWord: n. 新词</span></span>
   ```

### 6.4 调整翻译显示顺序

修改 `SceneRenderer.createSceneHTML` 中的HTML模板：
```javascript
// 当前顺序：EN在前，CN在后
contentWithTranslations += `
    <div class="para-trans">
        <div class="trans-en">...</div>  // 先EN
        <div class="trans-cn">...</div>  // 后CN
    </div>`;

// 如需调整为CN在前：
contentWithTranslations += `
    <div class="para-trans">
        <div class="trans-cn">...</div>  // 先CN
        <div class="trans-en">...</div>  // 后EN
    </div>`;
```

---

## 七、调试技巧

### 7.1 检查段落数量匹配

```javascript
// 在浏览器控制台执行
SCENES_DATA.forEach((scene, i) => {
    const contentParagraphs = (scene.zh.content.match(/<p[^>]*>/g) || []).length;
    const transParagraphs = (scene.zh.translationParagraphs || []).length;
    if (contentParagraphs !== transParagraphs) {
        console.warn(`场景${i+1}: content有${contentParagraphs}段，translationParagraphs有${transParagraphs}段`);
    }
});
```

### 7.2 检查高亮单词数量

```javascript
// 统计所有高亮单词
document.querySelectorAll('.word-highlight').length

// 检查某个场景的单词
document.querySelectorAll('[data-scene="1"] .word-highlight').length
```

### 7.3 测试段落点击

```javascript
// 模拟点击第一个段落
document.querySelector('.para-wrapper').click();

// 检查展开状态
document.querySelector('.para-wrapper').classList.contains('expanded');
```

---

## 八、性能注意事项

1. **避免频繁DOM操作**：场景切换使用CSS类切换，不重新渲染
2. **图片懒加载**：背景图使用 `loading="lazy"` 属性
3. **动画使用GPU加速**：transition属性使用transform/opacity
4. **事件委托**：段落点击使用document级别事件委托

---

## 九、版本历史

| 版本 | 日期 | 主要改动 |
|-----|------|---------|
| v1.0 | 2026-02-24 | 初始版本，8场景+完成页+祝福页 |
| v1.1 | 2026-02-24 | 添加段落点击翻译功能 |
| v1.2 | 2026-02-24 | 添加卡片收起/展开功能 |
| v1.3 | 2026-02-24 | 添加translationParagraphs支持，场景1-8全部完成 |

---

*文档维护：每次代码改动后同步更新本文档*
