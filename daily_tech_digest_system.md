# 每日技术摘要推送系统 - 完整方案

## 🎯 系统概述

基于 BestBlogs.dev 和多个优质 RSS 源，提供个性化的每日技术内容推送。

### 核心特性

1. ✅ **多源内容聚合** - BestBlogs + Hacker News + Reddit + OpenAI
2. ✅ **智能内容筛选** - AI 评分 + 主题相关 + 时间新鲜
3. ✅ **个性化推荐** - 自动学习用户偏好，动态调整内容比例
4. ✅ **每日定时推送** - 每天 22:30（北京时间）自动推送
5. ✅ **智能摘要生成** - AI 生成每篇文章的推荐理由

---

## 📊 个性化推荐系统

### 1. 用户偏好追踪

**数据文件：** `/home/lichangjiang/.openclaw/workspace/user_preferences.json`

**记录内容：**
- 类别偏好（编程/AI/产品）
- 主题偏好（React/Python/Rust/Go 等）
- 来源偏好（BestBlogs/HackerNews/Reddit/OpenAI）
- 点击历史（最近 100 条）

**点击记录方法：**
```bash
# 用户点击时自动触发，或手动记录
python3 record_click.py <category> "<title>" "<url>" <ai_score> <topic1 topic2 ...>

# 示例
python3 record_click.py programming "React 19 新特性" "https://example.com" 9.5 react frontend javascript
python3 record_click.py ai "OpenAI o1 模型" "https://openai.com" 9.8 ai-architecture
```

**当前偏好：**
```json
{
  "categories": {
    "programming": {"weight": 0.5, "clicks": 3, "readCount": 0},
    "ai": {"weight": 0.5, "clicks": 0, "readCount": 0},
    "product": {"weight": 0.2, "clicks": 0, "readCount": 0}
  },
  "topics": {
    "react": 3, "frontend": 2, "python": 1, "ai-architecture": 1
  },
  "sources": {
    "bestblogs": 2, "hackernews": 0, "reddit": 0, "openai": 1
  }
}
```

### 2. 动态比例调整

**初始比例（默认）：**
- 编程：3 篇（30%）
- AI：5 篇（50%）
- 产品：2 篇（20%）

**个性化调整：**
```python
# 读取用户偏好
prog_weight = 0.5  # 偏好权重
ai_weight = 0.5
product_weight = 0.2

# 动态调整比例（共 10 篇）
total = 10
prog_count = max(1, min(6, int(total * prog_weight)))    # 1-6 篇
ai_count = max(1, min(7, int(total * ai_weight)))       # 1-7 篇
product_count = total - prog_count - ai_count                # 1-2 篇
```

### 3. 主题个性化

**热门主题优先：**
- 分析用户最近点击的主题
- 优先推荐 Top 5 主题的相关文章
- 在推荐理由中明确标注："根据你最近关注的 [主题]..."

**主题映射：**
| 类别 | 主题标签 |
|------|----------|
| 编程 | React, Python, Rust, Go, JavaScript, TypeScript, Frontend, Backend, DevOps |
| AI | AI Architecture, GPT, Claude, Anthropic, LLM, RAG, Agents |
| 产品 | Product Design, UX/UI, Figma, Prototyping, User Research |

---

## 🔄 用户反馈机制

### 1. 点击自动记录

**方案 A：自动集成（推荐）**
- 在 Feishu 消息中添加点击链接
- 用户点击后自动触发记录脚本
- 无需用户手动操作

**方案 B：手动反馈**
- 用户点击文章后，回复文章标题或链接
- 系统识别并记录

### 2. 手动调整偏好

用户可以通过回复关键词调整：

| 关键词 | 效果 |
|--------|------|
| "编程更多" | 增加编程文章比例（+10%） |
| "AI 更多" | 增加 AI 文章比例（+10%） |
| "产品更多" | 增加产品文章比例（+10%） |
| "编程更少" | 减少编程文章比例（-10%） |
| "重置偏好" | 恢复默认配置 |
| "偏好分析" | 查看当前的偏好分析报告 |

### 3. 偏好分析报告

每周生成一次个性化洞察报告，包含：
- 用户偏好画像（类别比例）
- 热门主题 TOP 5
- 阅读趋势分析
- 推荐策略说明

---

## 📅 推送计划

### 推送时间

**每天 22:30（北京时间）**
- Cron 表达式：`30 14 * * *`
- 时区：UTC

### 推送内容

每日包含 10 篇文章，按类别分组：

```markdown
📅 [日期] 每日技术摘要

━━━━━━━━━━━━━━━━━━

🔥 个性化洞察
- 你的偏好画像：编程 66.7%、AI 33.3%
- 热门主题：React(3)、Frontend(2)
- 今日比例已根据你的习惯调整

━━━━━━━━━━━━━━━━━━

🔥 今日精选 (10篇)

### 💻 编程技术 (6篇)
1. React 19 新特性深度解析
   * AI 评分：9.2/10
   * 相关度：高（匹配你的 React 偏好）
   * 推荐理由：根据你最近对 React 和前端技术的持续关注...
   * 预计阅读时间：8 分钟

### 🤖 AI 前沿 (3篇)
1. OpenAI o1 模型架构解析
   * AI 评分：9.5/10
   * 相关度：高（AI Architecture）
   * 推荐理由：基于你最近对 AI 架构类文章的兴趣...
   * 预计阅读时间：10 分钟

### 🎨 产品设计 (1篇)
1. 产品设计中的微交互
   * AI 评分：8.8/10
   * 相关度：中
   * 推荐理由：这篇产品设计文章包含实用的 UX 方法...

━━━━━━━━━━━━━━━━━━

💡 个性化推荐

基于你最近 30 天的阅读记录：

你主要关注：
• React 和前端开发（12 篇）
• AI 架构和 LLM（8 篇）
• Python 后端开发（3 篇）

━━━━━━━━━━━━━━━━━━

📚 学习资源（可选）
- 今日推荐课程/文档

━━━━━━━━━━━━━━━━━━

🔄 反馈

你对今天的推荐满意吗？
- 回复 "编程更多" / "AI 更多" / "产品更多" 来调整明日比例
- 回复 "偏好分析" 查看你的阅读习惯分析
- 回复 "重置偏好" 恢复默认配置

来源：BestBlogs.dev + 其他精选源 | 管理订阅：https://www.bestblogs.dev/#subscribe
```

---

## 📊 数据源

### 主要源（BestBlogs 精选）

```
1. 精选内容（高质量）
   https://www.bestblogs.dev/zh/feeds/rss?featured=y

2. 编程技术（编程专题）
   https://www.bestblogs.dev/zh/feeds/rss?category=programming&type=article

3. AI 高分内容（AI 专题，评分 > 90）
   https://www.bestblogs.dev/en/feeds/rss?category=ai&minScore=90

4. 产品设计（产品专题）
   https://www.bestblogs.dev/zh/feeds/rss?category=product
```

### 补充源（扩展覆盖面）

```
1. Hacker News（技术新闻）
   https://hnrss.org/frontpage

2. Reddit r/programming（编程社区）
   https://www.reddit.com/r/programming/.rss

3. OpenAI Blog（官方更新）
   https://openai.com/blog/rss.xml
```

---

## 🔧 技术实现

### 文件结构

```
/home/lichangjiang/.openclaw/workspace/
├── user_preferences.json          # 用户偏好数据
├── user_preference_tracker.py      # 偏好追踪系统
└── record_click.py                 # 点击记录接口
```

### Cron 任务

**任务 ID：** `40c0b192-29af-4a9c-827a-d1a32e1e5edf`
**任务名称：** 每日技术摘要推送
**会话类型：** isolated（独立会话执行）

---

## 🎯 使用指南

### 测试推送

```bash
# 立即运行一次测试推送（可选）
# 系统会在今晚 22:30 自动推送
```

### 记录用户点击

```bash
# 方法 1：手动记录（用于测试）
python3 record_click.py programming "React 19 新特性" "https://example.com" 9.5 react frontend

# 方法 2：自动集成（推荐）
# 在 Feishu 消息中添加文章链接
# 格式：[文章标题](url) [记录点击]
# 用户点击后自动触发记录
```

### 查看用户偏好

```bash
# 查看当前偏好配置
cat /home/lichangjiang/.openclaw/workspace/user_preferences.json

# 查看偏好分析报告
python3 user_preference_tracker.py
```

### 调整推荐策略

通过 Feishu 回复关键词：
- "编程更多" → 增加编程比例
- "AI 更多" → 增加 AI 比例
- "产品更多" → 增加产品比例
- "重置偏好" → 恢复默认配置

---

## ✅ 系统状态

**配置完成：** ✅
**Cron 任务：** ✅ 已创建并启用
**推送时间：** 每天 22:30（北京时间）
**个性化系统：** ✅ 已实现

---

## 📝 下一步

1. **等待首次推送** - 今晚 22:30（北京时间）自动推送
2. **测试点击记录** - 查看收到的推送，测试点击记录功能
3. **观察推荐质量** - 根据实际阅读体验调整偏好
4. **持续优化** - 系统会每天自动学习你的偏好

---

**文档版本：** 1.0
**更新时间：** 2026-02-16
**创建者：** mirrorLee
