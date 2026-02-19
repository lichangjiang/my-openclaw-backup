#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日技术摘要 - BestBlogs 修复版
使用 feedparser 并增加超时时间
"""

import json
import datetime
import feedparser
from typing import List, Dict

# RSS 源配置
RSS_SOURCES = {
    "bestblogs_featured": {
        "url": "https://www.bestblogs.dev/zh/feeds/rss?featured=y",
        "name": "BestBlogs 精选",
        "category": "ai",  # 精选多为 AI 相关
    },
    "bestblogs_programming": {
        "url": "https://www.bestblogs.dev/zh/feeds/rss?category=programming&type=article",
        "name": "BestBlogs 编程技术",
        "category": "programming",
    },
    "bestblogs_product": {
        "url": "https://www.bestblogs.dev/zh/feeds/rss?category=product",
        "name": "BestBlogs 产品设计",
        "category": "product",
    },
}

USER_PREFERENCES_FILE = "/home/lichangjiang/.openclaw/workspace/user_preferences.json"
ARTICLES_PER_DAY = 10
DEFAULT_RATIOS = {"programming": 3, "ai": 5, "product": 2}

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

def calculate_freshness(published) -> int:
    """计算新鲜度（0-10）"""
    if not published:
        return 5
    
    try:
        parsed_date = None
        
        if hasattr(published, 'tm_year'):
            parsed_date = datetime.datetime(*published[:6], tzinfo=datetime.timezone.utc)
        elif isinstance(published, str):
            from email.utils import parsedate_to_datetime
            parsed_date = parsedate_to_datetime(published)
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=datetime.timezone.utc)
        
        if parsed_date is None:
            return 5
        
        delta = (datetime.datetime.now(datetime.timezone.utc) - parsed_date).days
        
        if delta <= 1:
            return 10
        elif delta <= 3:
            return 8
        elif delta <= 7:
            return 6
        elif delta <= 14:
            return 4
        elif delta <= 30:
            return 2
        else:
            return 0
            
    except:
        return 5

def fetch_articles() -> List[Dict]:
    """从 BestBlogs RSS 获取文章"""
    all_articles = []
    
    print("📡 正在获取 BestBlogs RSS 源...")
    print("（这可能需要 10-15 秒，请耐心等待...）\n")
    
    for source_key, source_config in RSS_SOURCES.items():
        try:
            print(f"  → {source_config['name']}")
            
            # 使用 feedparser，增加超时时间到 20 秒
            feed = feedparser.parse(
                source_config['url'],
                request_headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; OpenClaw/1.0)',
                    'Accept': 'application/rss+xml, application/xml, text/xml',
                }
            )
            
            # 获取文章
            articles = []
            for entry in feed.entries[:12]:  # 取前12篇
                title = entry.get('title', '')
                link = entry.get('link', '')
                
                # 只保留有效文章
                if title and link and 'bestblogs.dev' in link:
                    article = {
                        'title': title,
                        'link': link,
                        'published_str': entry.get('published', ''),
                        'source': source_key,
                        'category': source_config['category'],
                    }
                    
                    # 计算新鲜度
                    article['freshness_score'] = calculate_freshness(entry.get('published_parsed'))
                    
                    # 只保留最近7天的文章
                    if article['freshness_score'] >= 6:
                        articles.append(article)
            
            all_articles.extend(articles)
            print(f"     ✅ 获取 {len(articles)} 篇文章（最近7天内）")
            
        except Exception as e:
            print(f"  ⚠️ {source_config['name']} 获取失败: {e}")
    
    print(f"\n✅ 共获取 {len(all_articles)} 篇文章")
    return all_articles

def select_articles(articles: List[Dict]) -> List[Dict]:
    """选择文章"""
    # 按新鲜度排序
    articles.sort(key=lambda x: x.get('freshness_score', 0), reverse=True)
    
    # 取前10篇
    return articles[:ARTICLES_PER_DAY]

def generate_digest(articles: List[Dict]) -> str:
    """生成摘要"""
    now = datetime.datetime.now(datetime.timezone.utc)
    beijing_time = now + datetime.timedelta(hours=8)
    date_str = beijing_time.strftime("%Y年%m月%d日")
    
    digest = f"📅 {date_str} 每日技术摘要\n\n"
    digest += "━━━━━━━━━━━━━━━━\n\n"
    digest += f"🔥 今日精选（{len(articles)} 篇）\n\n"
    
    # 按分类
    categories = [
        ("programming", "💻 编程技术"),
        ("ai", "🤖 AI 前沿"),
        ("product", "🎨 产品设计")
    ]
    
    for cat_key, cat_name in categories:
        cat_articles = [a for a in articles if a.get('category') == cat_key]
        if not cat_articles: continue
        
        digest += f"### {cat_name}（{len(cat_articles)} 篇）\n\n"
        
        for i, article in enumerate(cat_articles, 1):
            title_display = article['title'][:60] + ('...' if len(article['title']) > 60 else '')
            source_name = RSS_SOURCES.get(article['source'], {}).get('name', 'Unknown')
            
            digest += f"{i}. **{title_display}**\n"
            digest += f"   * 来源：{source_name}\n"
            
            # 显示发布时间
            published = article.get('published_str', '')
            if published:
                digest += f"   * 发布：{published[:20]}...\n"
            
            digest += f"   * 链接：{article['link']}\n\n"
    
    digest += "━━━━━━━━━━━━━━━━\n"
    digest += "来源：BestBlogs.dev | 管理订阅：https://www.bestblogs.dev/#subscribe\n"
    digest += "（文章链接均为具体文章页面，可直接跳转）"
    
    return digest

def main():
    """主函数"""
    print("🚀 每日技术摘要（BestBlogs 源）")
    print("=" * 50)
    print()
    
    # 获取文章
    articles = fetch_articles()
    
    if not articles:
        print("\n❌ 没有获取到任何文章")
        print("\n📝 请手动检查以下内容：")
        print("1. 网络连接：ping www.bestblogs.dev")
        print("2. RSS 可访问性：curl -L 'https://www.bestblogs.dev/zh/feeds/rss?featured=y'")
        print("3. DNS 解析：nslookup www.bestblogs.dev")
        return
    
    # 选择文章
    selected_articles = select_articles(articles)
    
    # 生成摘要
    digest = generate_digest(selected_articles)
    
    print("\n📝 摘要生成完成")
    print(digest)

if __name__ == "__main__":
    import os
    main()
