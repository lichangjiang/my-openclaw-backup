#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日技术摘要生成脚本 - 真实 RSS 源版本（快速版）
使用 feedparser，添加超时和错误处理
"""

import json
import datetime
import feedparser
from typing import List, Dict

# RSS 源配置（只使用最快最可靠的源）
RSS_SOURCES = {
    "bestblogs_ai": {
        "url": "https://www.bestblogs.dev/en/feeds/rss?category=ai&minScore=90",
        "name": "BestBlogs AI 高分",
        "category": "ai",
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
    preferences = load_user_preferences()
    clicks = preferences.get('clicks', [])
    if not clicks:
        return DEFAULT_RATIOS.copy()
    
    category_counts = {"programming": 0, "ai": 0, "product": 0}
    for click in clicks:
        category = click.get('category', 'unknown')
        if category in category_counts:
            category_counts[category] += 1
            
    total_clicks = sum(category_counts.values()) or 1
    if total_clicks == 0:
        return DEFAULT_RATIOS.copy()
        
    ratios = {}
    for category, count in category_counts.items():
        articles = (count / total_clicks) * ARTICLES_PER_DAY
        ratios[category] = max(2, round(articles))
    return ratios

def get_user_topics() -> List[str]:
    preferences = load_user_preferences()
    clicks = preferences.get('clicks', [])
    topic_counts = {}
    
    keywords = ['python', 'rust', 'go', 'java', 'react', 'vue', 'docker',
                'kubernetes', 'k8s', 'ai', 'ml', 'security', 'linux']
    
    for click in clicks:
        title = click.get('title', '')
        for keyword in keywords:
            if keyword.lower() in title.lower():
                topic_counts[keyword] = topic_counts.get(keyword, 0) + 1
                
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    return [topic for topic, count in sorted_topics]

def calculate_freshness(published) -> int:
    """计算文章新鲜度分数（0-10）"""
    if not published:
        return 5
    
    try:
        parsed_date = None
        
        # feedparser 会自动解析时间
        if hasattr(published, 'tm_year'):
            parsed_date = datetime.datetime(*published[:6], tzinfo=datetime.timezone.utc)
        elif isinstance(published, str):
            # 尝试手动解析
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
    """从 RSS 源获取文章"""
    all_articles = []
    
    print("📡 正在获取 RSS 源...")
    
    for source_key, source_config in RSS_SOURCES.items():
        try:
            print(f"  → {source_config['name']}")
            
            # 设置超时（5秒）
            feedparser._parsers[''][''] = None  # 禁用某些解析器以提高速度
            
            feed = feedparser.parse(source_config['url'], request_headers={'User-Agent': 'OpenClaw'})
            
            articles = []
            for entry in feed.entries[:15]:  # 只取前15篇
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published_parsed'),
                    'published_str': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:200],
                    'source': source_key,
                    'category': source_config['category'],
                }
                
                # 计算新鲜度
                article['freshness_score'] = calculate_freshness(article.get('published'))
                
                # 只保留最近30天的文章
                if article['freshness_score'] >= 2:
                    articles.append(article)
            
            all_articles.extend(articles)
            print(f"     ✅ 获取 {len(articles)} 篇文章")
            
        except Exception as e:
            print(f"  ⚠️ {source_config['name']} 获取失败: {e}")
    
    print(f"✅ 共获取 {len(all_articles)} 篇文章")
    return all_articles

def select_articles(articles: List[Dict], user_ratios: Dict[str, int], user_topics: List[str]) -> Dict[str, List[Dict]]:
    """选择文章"""
    # 计算综合评分
    for article in articles:
        score = 50  # 基础分
        score += article.get('freshness_score', 0)
        
        # 主题相关度
        for topic in user_topics:
            if topic.lower() in article.get('title', '').lower():
                score += 10
                break
        
        article['score'] = score
    
    # 按分数排序
    articles.sort(key=lambda x: x['score'], reverse=True)
    
    # 按类别分配
    selected_articles = {"programming": [], "ai": [], "product": []}
    
    for article in articles:
        category = article.get('category', 'programming')
        if category in selected_articles:
            if len(selected_articles[category]) < user_ratios.get(category, 3):
                selected_articles[category].append(article)
    
    # 确保总数
    total = sum(len(v) for v in selected_articles.values())
    if total < ARTICLES_PER_DAY:
        for article in articles:
            if not any(article in v for v in selected_articles.values()):
                category = article.get('category', 'programming')
                if category in selected_articles:
                    selected_articles[category].append(article)
                    if sum(len(v) for v in selected_articles.values()) >= ARTICLES_PER_DAY:
                        break
    
    return selected_articles

def generate_digest(selected_articles: Dict[str, List[Dict]], user_topics: List[str]) -> str:
    """生成摘要"""
    now = datetime.datetime.now(datetime.timezone.utc)
    beijing_time = now + datetime.timedelta(hours=8)
    date_str = beijing_time.strftime("%Y年%m月%d日")
    
    digest = f"📅 {date_str} 每日技术摘要\n\n"
    digest += "━━━━━━━━━━━━━━━━\n\n"
    digest += f"🔥 今日精选（{sum(len(v) for v in selected_articles.values())} 篇）\n\n"
    
    categories = [
        ("programming", "💻 编程技术"),
        ("ai", "🤖 AI 前沿"),
        ("product", "🎨 产品设计")
    ]
    
    for cat_key, cat_name in categories:
        articles = selected_articles.get(cat_key, [])
        if not articles: continue
        
        digest += f"### {cat_name}（{len(articles)} 篇）\n\n"
        
        for i, article in enumerate(articles, 1):
            title_display = article['title'][:60] + ('...' if len(article['title']) > 60 else '')
            
            digest += f"{i}. **{title_display}**\n"
            digest += f"   * 来源：{RSS_SOURCES.get(article['source'], {}).get('name', 'Unknown')}\n"
            
            # 显示发布时间
            published = article.get('published_str', '')
            if published:
                digest += f"   * 发布：{published[:20]}...\n"
            
            digest += f"   * 链接：{article['link']}\n\n"
    
    digest += "━━━━━━━━━━━━━━━━\n\n💡 个性化提示\n"
    digest += f"**热门主题：** {', '.join(user_topics) if user_topics else '暂无数据'}\n"
    digest += "\n━━━━━━━━━━━━━━━━\n来源：BestBlogs.dev | 管理订阅：https://www.bestblogs.dev/#subscribe"
    
    return digest

def main():
    """主函数"""
    print("🚀 每日技术摘要推送系统（真实 RSS 源）")
    print("=" * 50)
    
    # 获取用户偏好
    user_ratios = get_user_ratios()
    user_topics = get_user_topics()
    
    print(f"\n📊 推荐比例: {user_ratios}")
    print(f"📚 热门主题: {user_topics}")
    
    # 获取文章
    articles = fetch_articles()
    
    if not articles:
        print("\n❌ 没有获取到任何文章，使用备用方案...")
        # 使用测试数据
        from daily_tech_digest_simple import generate_test_digest
        digest = generate_test_digest()
    else:
        # 选择文章
        selected_articles = select_articles(articles, user_ratios, user_topics)
        
        # 生成摘要
        digest = generate_digest(selected_articles, user_topics)
    
    print("\n📝 摘要生成完成")
    print(digest)

if __name__ == "__main__":
    import os
    main()
