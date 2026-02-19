#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日技术摘要生成脚本 - 可靠版
使用 Hacker News 和其他可靠 RSS 源
"""

import json
import datetime
import feedparser
from typing import List, Dict

# 使用可靠的 RSS 源
RSS_SOURCES = {
    "hacker_news": {
        "url": "https://hnrss.org/frontpage",
        "name": "Hacker News",
        "category": "programming",
    },
    "github_trending": {
        "url": "https://github.com/trending/developers.atom",
        "name": "GitHub Trending Developers",
        "category": "programming",
    },
}

USER_PREFERENCES_FILE = "/home/lichangjiang/.openclaw/workspace/user_preferences.json"
ARTICLES_PER_DAY = 10
DEFAULT_RATIOS = {"programming": 5, "ai": 5, "product": 0}

def load_user_preferences() -> Dict:
    try:
        if os.path.exists(USER_PREFERENCES_FILE):
            with open(USER_PREFERENCES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except:
        return {}

def get_user_ratios() -> Dict[str, int]:
    return DEFAULT_RATIOS.copy()

def get_user_topics() -> List[str]:
    return []

def fetch_articles() -> List[Dict]:
    """从 RSS 源获取文章"""
    all_articles = []
    
    print("📡 正在获取 RSS 源...")
    
    for source_key, source_config in RSS_SOURCES.items():
        try:
            print(f"  → {source_config['name']}")
            
            # 使用 feedparser（不使用私有 API）
            feed = feedparser.parse(source_config['url'])
            
            articles = []
            for entry in feed.entries[:10]:  # 取前10篇
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published_str': entry.get('published', ''),
                    'source': source_key,
                    'category': source_config['category'],
                }
                
                articles.append(article)
            
            all_articles.extend(articles)
            print(f"     ✅ 获取 {len(articles)} 篇文章")
            
        except Exception as e:
            print(f"  ⚠️ {source_config['name']} 获取失败: {e}")
    
    print(f"✅ 共获取 {len(all_articles)} 篇文章")
    return all_articles

def generate_digest(articles: List[Dict]) -> str:
    """生成摘要"""
    now = datetime.datetime.now(datetime.timezone.utc)
    beijing_time = now + datetime.timedelta(hours=8)
    date_str = beijing_time.strftime("%Y年%m月%d日")
    
    digest = f"📅 {date_str} 每日技术摘要\n\n"
    digest += "━━━━━━━━━━━━━━━━\n\n"
    digest += f"🔥 今日精选（{len(articles)} 篇）\n\n"
    
    digest += f"### 💻 编程技术（{len(articles)} 篇）\n\n"
    
    for i, article in enumerate(articles, 1):
        title_display = article['title'][:60] + ('...' if len(article['title']) > 60 else '')
        source_name = RSS_SOURCES.get(article['source'], {}).get('name', 'Unknown')
        
        digest += f"{i}. **{title_display}**\n"
        digest += f"   * 来源：{source_name}\n"
        
        # 显示发布时间
        published = article.get('published_str', '')
        if published:
            digest += f"   * 发布：{published[:20]}...\n"
        
        digest += f"   * 链接：{article['link']}\n\n"
    
    digest += "━━━━━━━━━━━━━━━━\n\n💡 个性化提示\n"
    digest += "**热门主题：** 暂无数据（需要多点击积累数据）\n"
    digest += "\n━━━━━━━━━━━━━━━━\n来源：Hacker News + GitHub | 实时更新"
    
    return digest

def main():
    """主函数"""
    print("🚀 每日技术摘要推送系统（可靠版）")
    print("=" * 50)
    
    # 获取文章
    articles = fetch_articles()
    
    if not articles:
        print("\n❌ 没有获取到任何文章")
        return
    
    # 生成摘要
    digest = generate_digest(articles)
    
    print("\n📝 摘要生成完成")
    print(digest)

if __name__ == "__main__":
    import os
    main()
