#!/usr/bin/env python3
"""
记录用户点击的简单接口
"""
import sys
import json

PREFERENCES_FILE = "/home/lichangjiang/.openclaw/workspace/user_preferences.json"

def record_click(category: str, article_title: str, article_url: str, ai_score: float = 0, topics: list = None, source: str = "bestblogs"):
    """
    记录用户点击
    用法：python3 record_click.py <category> "<title>" "<url>" [ai_score] [topics...]
    示例：
        python3 record_click.py programming "React 19 新特性" "https://example.com" 9.5 react frontend javascript
        python3 record_click.py ai "OpenAI o1 模型" "https://openai.com" 9.8 ai-architecture
        python3 record_click.py product "产品设计中的微交互" "https://example.com" 8.5 product-design ux
    """
    try:
        # 读取现有数据
        with open(PREFERENCES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 创建点击记录
        click_record = {
            "timestamp": "2026-02-16T00:00:00Z",
            "articleTitle": article_title,
            "articleUrl": article_url,
            "category": category,
            "topics": topics or [],
            "source": source,
            "aiScore": ai_score
        }

        # 添加到点击历史
        data["clickHistory"].append(click_record)

        # 更新类别偏好
        if category in data["preferences"]["categories"]:
            cat_pref = data["preferences"]["categories"][category]
            cat_pref["clicks"] += 1

        # 更新主题偏好
        if topics:
            for topic in topics:
                if topic in data["preferences"]["topics"]:
                    data["preferences"]["topics"][topic] += 1

        # 更新来源偏好
        if source in data["preferences"]["sources"]:
            data["preferences"]["sources"][source] += 1

        # 只保留最近 100 条点击记录
        if len(data["clickHistory"]) > 100:
            data["clickHistory"] = data["clickHistory"][-100:]

        # 保存
        data["profile"]["lastUpdated"] = "2026-02-16T00:00:00Z"
        with open(PREFERENCES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ 已记录点击：{article_title}")
        print(f"   类别：{category}")
        if topics:
            print(f"   主题：{', '.join(topics)}")
        print(f"   AI 评分：{ai_score}")

    except Exception as e:
        print(f"❌ 记录失败：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法：python3 record_click.py <category> <title> <url> [ai_score] [topic1 topic2 ...]")
        print("")
        print("参数说明：")
        print("  category   - 类别（programming/ai/product）")
        print("  title      - 文章标题")
        print("  url        - 文章链接")
        print("  ai_score   - AI 评分（可选，默认 0）")
        print("  topics     - 主题标签列表（可选）")
        print("")
        print("示例：")
        print("  python3 record_click.py programming 'React 19 新特性' 'https://example.com' 9.5 react frontend")
        print("  python3 record_click.py ai 'OpenAI o1 模型' 'https://openai.com' 9.8 ai-architecture")
        sys.exit(1)

    category = sys.argv[1]
    title = sys.argv[2]
    url = sys.argv[3]
    ai_score = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
    topics = sys.argv[5:] if len(sys.argv) > 5 else []

    record_click(category, title, url, ai_score, topics)
