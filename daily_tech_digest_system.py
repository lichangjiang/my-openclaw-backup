#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import datetime
import feedparser
import subprocess
import signal
from typing import List, Dict
import time
from datetime import timezone, timedelta
from email.utils import parsedate_to_datetime

# 配置
RSS_SOURCES = {
    "bestblogs_featured": {
        "url": "https://www.bestblogs.dev/zh/feeds/rss?featured=y",
        "name": "BestBlogs 精选",
        "category": "programming",
    },
    "bestblogs_programming": {
        "url": "https://www.bestblogs.dev/zh/feeds/rss?category=programming&type=article",
        "name": "BestBlogs 编程技术",
        "category": "programming",
    },
    "bestblogs_ai": {
        "url": "https://www.bestblogs.dev/en/feeds/rss?category=ai&minScore=90",
        "name": "BestBlogs AI 高分",
        "category": "ai",
    },
    "bestblogs_product": {
        "url": "https://www.bestblogs.dev/zh/feeds/rss?category=product",
        "name": "BestBlogs 产品设计",
        "category": "product",
    },
    "hacker_news": {
        "url": "https://hnrss.org/frontpage",
        "name": "Hacker News",
        "category": "programming",
    },
    "reddit_programming": {
        "url": "https://www.reddit.com/r/programming/.rss",
        "name": "Reddit r/programming",
        "category": "programming",
    },
    "openai_blog": {
        "url": "https://openai.com/blog/rss.xml",
        "name": "OpenAI Blog",
        "category": "ai",
    },
}

USER_PREFERENCES_FILE = "/home/lichangjiang/.openclaw/workspace/user_preferences.json"
ARTICLES_PER_DAY = 10
DEFAULT_RATIOS = {"programming": 3, "ai": 5, "product": 2}
TEST_MODE = "--test" in sys.argv

def load_user_preferences() -> Dict:
    try:
        if os.path.exists(USER_PREFERENCES_FILE):
            with open(USER_PREFERENCES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"⚠️ 加载用户偏好失败: {e}")
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

def parse_pub_time(pub_date: str) -> datetime.datetime:
    """解析发布时间"""
    try:
        # 使用 email.utils.parsedate_to_datetime 解析 RFC 2822 格式
        dt = parsedate_to_datetime(pub_date)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception as e:
        # 如果解析失败，尝试手动解析
        for fmt in [
            '%a, %d %b %Y %H:%M:%S %Z',
            '%a, %d %b %Y %H:%M:%S %z',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S%z',
        ]:
            try:
                dt = datetime.datetime.strptime(pub_date, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except:
                continue
    return None

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

def calculate_score(article: Dict, user_topics: List[str]) -> int:
    score = 50  # 基础分
    
    # 时间新鲜度（越新越好）
    pub_time = article.get('pub_time')
    if pub_time:
        now = datetime.datetime.now(timezone.utc)
        hours_old = (now - pub_time).total_seconds() / 3600
        if hours_old < 24:
            score += 20  # 24小时内
        elif hours_old < 48:
            score += 15  # 48小时内
        elif hours_old < 72:
            score += 10  # 72小时内
    
    # 主题相关度
    for topic in user_topics:
        if topic.lower() in article.get('title', '').lower():
            score += 20
            
    # 来源优先级
    source = article.get('source', '')
    if 'featured' in source:
        score += 15
    elif 'ai' in source:
        score += 10
    elif 'hacker' in source:
        score += 8
        
    return score

def fetch_articles() -> List[Dict]:
    all_articles = []
    print("📡 正在获取 RSS 源...")
    
    # 只获取最近 3 天的文章
    now = datetime.datetime.now(timezone.utc)
    cutoff_time = now - timedelta(days=3)
    
    for source_key, source_config in RSS_SOURCES.items():
        try:
            print(f"  → {source_config['name']}")
            feed = feedparser.parse(source_config['url'])
            
            fresh_count = 0
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': source_key,
                    'category': source_config['category'],
                }
                
                # 解析发布时间
                pub_time = parse_pub_time(article['published'])
                article['pub_time'] = pub_time
                
                # 只保留最近 3 天的文章
                if pub_time and pub_time > cutoff_time:
                    all_articles.append(article)
                    fresh_count += 1
                elif not pub_time:
                    # 如果无法解析时间，也保留（但不计入新鲜度）
                    all_articles.append(article)
                
            print(f"     ✓ 获取 {len(feed.entries)} 篇，新鲜 {fresh_count} 篇")
                
        except Exception as e:
            print(f"  ⚠️ {source_config['name']} 获取失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"✅ 共获取 {len(all_articles)} 篇文章（最近 3 天）")
    return all_articles

def select_articles(articles: List[Dict], user_ratios: Dict[str, int], user_topics: List[str]) -> Dict[str, List[Dict]]:
    for article in articles:
        article['score'] = calculate_score(article, user_topics)
    
    articles.sort(key=lambda x: x['score'], reverse=True)
    
    selected_articles = {"programming": [], "ai": [], "product": []}
    
    for article in articles:
        category = article.get('category', 'programming')
        if category in selected_articles:
            if len(selected_articles[category]) < user_ratios.get(category, 3):
                selected_articles[category].append(article)
                
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
        for i, article in enumerate(articles[:5], 1):
            digest += f"{i}. **{article['title'][:60]}...**\n"
            digest += f"   * 来源：{RSS_SOURCES.get(article['source'], {}).get('name', 'Unknown')}\n"
            
            # 显示发布时间
            pub_time = article.get('pub_time')
            if pub_time:
                beijing_pub = pub_time + datetime.timedelta(hours=8)
                time_str = beijing_pub.strftime("%m月%d日 %H:%M")
                hours_old = int((now - pub_time).total_seconds() / 3600)
                if hours_old < 1:
                    time_str += " (刚刚)"
                elif hours_old < 24:
                    time_str += f" ({hours_old}小时前)"
                else:
                    time_str += f" ({hours_old//24}天前)"
                digest += f"   * 发布：{time_str}\n"
            else:
                digest += f"   * 发布：{article.get('published', 'N/A')[:20]}...\n"
            
            digest += f"   * 链接：{article['link']}\n\n"
    
    digest += "━━━━━━━━━━━━━━━━\n\n💡 个性化提示\n"
    digest += f"**热门主题：** {', '.join(user_topics) if user_topics else '暂无数据'}\n"
    digest += "\n━━━━━━━━━━━━━━━━\n来源：BestBlogs.dev + 其他精选源"
    
    return digest

def trigger_openglaw_send(digest: str) -> bool:
    """触发 OpenClaw 发送消息（方案1：直接调用 API）"""
    try:
        # 将摘要写入临时文件
        temp_file = "/tmp/daily_tech_digest_content.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(digest)
        
        print(f"✅ 摘要已保存到: {temp_file}")
        print(f"📤 摘要内容已输出，等待 OpenClaw 自动发送...")
        
        # 输出特定标记，让 OpenClaw 捕获并发送
        print(f"\n【OpenClaw_SEND_START】")
        print(digest)
        print(f"【OpenClaw_SEND_END】\n")
        
        return True
        
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

def main():
    print("🚀 每日技术摘要推送系统启动")
    print("=" * 50)
    
    user_ratios = get_user_ratios()
    user_topics = get_user_topics()
    
    print(f"\n📊 推荐比例: {user_ratios}")
    print(f"📚 热门主题: {user_topics}")
    
    articles = fetch_articles()
    selected_articles = select_articles(articles, user_ratios, user_topics)
    digest = generate_digest(selected_articles, user_topics)
    
    if TEST_MODE:
        print("\n🧪 测试模式:\n")
        print(digest)
        return
    
    print("\n📝 生成摘要完成，准备发送...")
    
    # 触发 OpenClaw 发送
    success = trigger_openglaw_send(digest)
    
    if success:
        print("\n✅ 推送任务已完成")
    else:
        print("\n❌ 推送任务失败")

if __name__ == "__main__":
    main()
