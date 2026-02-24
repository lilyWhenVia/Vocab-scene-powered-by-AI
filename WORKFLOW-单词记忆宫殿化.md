# 单词记忆宫殿化工作流

## 概述
将用户提供的单词文件（PDF/Word/Excel）转换为记忆宫殿HTML页面的标准工作流程。

---

## 输入文件支持
| 格式 | 读取方式 |
|-----|---------|
| PDF | pypdf / pdfplumber 提取文本 |
| Word (.docx) | python-docx 读取 |
| Excel (.xlsx) | openpyxl / pandas 读取 |
| 纯文本 (.txt) | 直接读取 |

---

## 工作流步骤

### Step 1: 提取单词列表
```
输入: 用户提供的单词文件
输出: 结构化单词列表
```

**操作**:
1. 识别文件格式，选择对应解析库
2. 提取所有单词，保留词性和释义（如有）
3. 去重、排序，统计总数
4. 输出格式：
   ```
   序号 | 单词 | 词性 | 释义
   1    | flap | v.  | 拍打翅膀
   2    | ranger | n. | 护林员
   ...
   ```

**校验点**: 
- [ ] 单词总数确认
- [ ] 无重复/遗漏

---

### Step 2: 规划场景分配
```
输入: 单词列表 + 总数
输出: 场景规划表
```

**分配原则**:
- 每场景 40-50 个单词（视总数调整）
- 按主题/词性/首字母分组
- 场景数 = ceil(总数 / 45)

**场景规划表模板**:
| 场景ID | 场景名称 | 锚点路径 | 单词范围 | 单词数 |
|-------|---------|---------|---------|-------|
| 1 | 晨光图书馆 | 阅览桌→书架走廊→天文角 | 1-45 | 45 |
| 2 | 自然博物馆 | 生物展厅→海洋馆→矿石角 | 46-90 | 45 |
| ... | ... | ... | ... | ... |
| N | 完成页 | - | - | 0 |
| N+1 | 祝福页 | - | - | 0 |

**场景命名参考**:
- 图书馆、博物馆、大学、医院、广场、公园
- 科技园、会议中心、艺术馆、体育馆
- 咖啡厅、餐厅、商场、机场、火车站

---

### Step 3: 编写场景叙事
```
输入: 场景规划表 + 分配的单词
输出: 英文叙事 → 中英夹杂版 → 纯中文翻译
```

**⚠️ 核心原则：英文优先！**

内容创作必须按以下顺序进行：
1. **先写纯英文叙事** - 确保表达地道、专业、符合母语者习惯
2. **再生成中英夹杂版** - 将英文单词嵌入中文语境
3. **最后写纯中文翻译** - 完整翻译，关键词也是中文

**英文叙事写作规范**:

1. **语言要求**:
   - 使用正式但自然的英语
   - 避免中式英语（Chinglish）
   - 句子结构多样化，避免重复句式
   - 逻辑连贯，段落之间有过渡
   - 无废话、无口水话

2. **风格参考**:
   ```
   ❌ 错误示例（生硬、不自然）:
   "You ultimately walk to the reading table. This is your ultimate goal."
   
   ✅ 正确示例（自然、流畅）:
   "You ultimately find a seat—your ultimate goal for the morning."
   ```

3. **单词嵌入技巧**:
   - 动词：用于描述动作（"A bird flaps its wings"）
   - 名词：用于场景物品（"The counsellor at the entrance"）
   - 形容词：用于修饰（"an unconventional lecturer"）
   - 副词：用于强调（"People conventionally believe..."）

**叙事结构**:
```
段落1: 场景入口（2-3个单词）
段落2: 锚点1详细描写（8-10个单词）
段落3: 锚点1补充（4-6个单词）
段落4: 锚点2详细描写（8-10个单词）
段落5: 锚点2补充（4-6个单词）
段落6: 锚点3详细描写（8-10个单词）
段落7: 场景收尾（4-6个单词）
```

**高亮格式**:
```html
<!-- 英文版 -->
<span class="word-highlight">word<span class="tooltip">word: n. 释义</span></span>

<!-- 中英夹杂版（zh.content） -->
你<span class="word-highlight">ultimately<span class="tooltip">ultimately: adv. 最终</span></span>找到了座位

<!-- 纯中文翻译（zh.translationParagraphs） -->
你<span class="word-highlight">最终<span class="tooltip">ultimately: adv. 最终</span></span>找到了座位
```

---

### Step 4: 准备背景图片
```
输入: 场景名称列表
输出: 背景图片URL列表
```

**图片要求**:
- 展示场景整体环境（非特定物体）
- 16:9 横版构图
- 高清质量（1920px宽度）

**推荐图源**: Unsplash（免费商用）

**URL格式**:
```
https://images.unsplash.com/photo-{ID}?w=1920&q=80
```

**场景-图片对照表**:
| 场景 | 搜索关键词 | 示例URL |
|-----|-----------|---------|
| 图书馆 | library interior | photo-1481627834876-b7833e8f5570 |
| 博物馆 | museum hall | photo-1574068468668-a05a11f871da |
| 大学 | university campus | photo-1562774053-701939374585 |
| 医院 | hospital lobby | photo-1519494026892-80bbd2d6fd0d |
| 广场 | city square | photo-1517732306149-e8f829eb588a |
| 公园 | park landscape | photo-1496442226666-8d4d0e62e6e9 |

---

### Step 5: 组装SCENES_DATA
```
输入: 叙事文本 + 背景图片
输出: JavaScript数据结构
```

**数据结构模板**:
```javascript
{
    id: 1,
    icon: 'fa-book',  // Font Awesome 4.7 图标
    bgImage: 'https://images.unsplash.com/...',
    zh: {
        title: '场景中文名',
        anchors: '锚点1→锚点2→锚点3',
        content: `<p class="mb-3">中文叙事段落1...</p>
                  <p class="mb-3">【锚点1】中文叙事段落2...</p>
                  ...`,
        translation: `完整的英文翻译，包含高亮...`
    },
    en: {
        title: 'Scene English Name',
        anchors: 'Anchor1 → Anchor2 → Anchor3',
        content: `<p class="mb-3">English narrative paragraph 1...</p>
                  <p class="mb-3">[Anchor1] English narrative paragraph 2...</p>
                  ...`
    }
}
```

**图标参考**:
| 场景类型 | 图标 |
|---------|------|
| 图书馆/学习 | fa-book |
| 博物馆/自然 | fa-leaf |
| 大学/研究 | fa-university |
| 医院/健康 | fa-heartbeat |
| 广场/城市 | fa-building |
| 公园/户外 | fa-tree |
| 科技/创新 | fa-rocket |
| 会议/商务 | fa-briefcase |
| 完成页 | fa-check-circle |
| 祝福页 | fa-star |

---

### Step 6: 生成HTML页面
```
输入: SCENES_DATA + 模板代码
输出: 完整HTML文件
```

**基于模板文件**: `memory-palace-356.html`

**需要修改的部分**:
1. `<title>` 标签 - 更新标题
2. `CONFIG.app.title` - 中英文标题
3. `SCENES_DATA` 数组 - 替换为新数据
4. `State.totalScenes` - 更新场景总数

**命名规范**:
```
memory-palace-{单词数}.html
示例: memory-palace-200.html
```

---

### Step 7: 质量校验
```
输入: 生成的HTML文件
输出: 校验报告
```

**自动校验**:
```javascript
// 统计高亮单词数
document.querySelectorAll('.word-highlight').length

// 检查tooltip完整性
document.querySelectorAll('.word-highlight .tooltip').length
```

**人工校验清单**:
- [ ] 单词总数与源文件一致
- [ ] 所有场景可正常切换
- [ ] 中英文切换正常（无动画）
- [ ] 段落点击展开翻译正常
- [ ] 语音朗读功能正常
- [ ] 移动端显示正常
- [ ] 背景图片加载正常

---

### Step 8: 更新记录
```
输入: 完成的工作
输出: 更新CHANGELOG
```

在 `CHANGELOG-功能改造记录.md` 追加：
```markdown
## {日期}

### 新增: {文件名}
**来源**: {源文件名}
**单词数**: {N}
**场景数**: {M}
**特殊处理**: {如有}
```

---

## 快速参考

### 文件清单
| 文件 | 用途 |
|-----|------|
| `PROMPT-记忆宫殿单词系统.md` | 完整开发规范 |
| `WORKFLOW-单词记忆宫殿化.md` | 本工作流文件 |
| `CHANGELOG-功能改造记录.md` | 改动记录 |
| `memory-palace-*.html` | 生成的页面 |

### 常用命令
```python
# PDF提取
from pypdf import PdfReader
reader = PdfReader("file.pdf")
text = "".join(page.extract_text() for page in reader.pages)

# Word提取
from docx import Document
doc = Document("file.docx")
text = "\n".join(p.text for p in doc.paragraphs)

# Excel提取
import pandas as pd
df = pd.read_excel("file.xlsx")
words = df['单词'].tolist()
```

### 单词高亮模板
```html
<span class="word-highlight">word<span class="tooltip">word: n. 释义</span></span>
```

---

## 注意事项

1. **单词完整性是核心** - 必须100%覆盖，不可遗漏
2. **叙事自然流畅** - 单词嵌入不能生硬
3. **中英对应** - 段落数量和单词位置要匹配
4. **翻译完整** - 中文翻译不能用省略号
5. **图片场景化** - 背景图展示整体环境

---

*工作流版本: v1.0*
*创建日期: 2026-02-24*
