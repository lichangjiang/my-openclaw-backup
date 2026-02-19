#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日技术摘要 - 修复 BestBlogs 访问
使用 urllib 直接访问，添加超时和重试
"""

import json
import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict
import time

# RSS 源配置
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
}

ARTICLES_PER_DAY = 10
DEFAULT_RATIOS = {"programming": 3, "ai": 5, "product": 2}

def fetch_rss(url: str, timeout: int = 15, retries: int = 3) -> str:
    """获取 RSS 内容，带超时和重试"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; OpenClaw/1.0)',
        'Accept': 'application/rss+xml, application/xml, text/xml',
    }
    
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(request, timeout=timeout) as response:
                content = response.read().decode('utf-8')
                print(f"     ✅ 成功获取（{len(content)} bytes）")
                return content
                
        except urllib.error.URLError as e:
            print(f"     ⚠️ 尝试 {attempt+1}/{retries} 失败: {e}")
            if attempt < retries - 1:
                time.sleep(1)  # 等待1秒后重试
        except Exception as e:
            print(f"     ⚠️ 尝试 {attempt+1}/{retries} 失败: {e}")
            if attempt < retries - 1:
                time.sleep(1)
    
    return None

def parse_rss(xml_content: str, source_key: str, category: str) -> List[Dict]:
    """解析 RSS XML"""
    if not xml_content:
        return []
    
    articles = []
    
    try:
        root = ET.fromstring(xml_content)
        
        # 处理命名空间
        if root.tag.startswith('{'):
            ns = root.tag.split('{')[1].split('}')[0]
            ET.register_namespace('', ns)
            root = ET.fromstring(xml_content)
        
        # RSS 2.0 格式
        if root.tag.endswith('rss') or root.tag == 'rss':
            channel = root.find('channel')
            if channel is None:
                channel = root
            
            items = channel.findall('item')
            
            for item in items[:15]:  # 取前15篇
                title_elem = item.find('title')
                link_elem = item.find('link')
                pub_date_elem = item.find('pubDate')
                desc_elem = item.find('description')
                
                if title_elem is not None and title_elem.text and link_elem is not None:
                    article = {
                        'title': title_elem.text.strip(),
                        'link': link_elem.text.strip() if link_elem.text else '',
                        'published': pub_date_elem.text if pub_date_elem is not None else '',
                        'summary': (desc_elem.text[:150] if desc_elem.text else '') if desc_elem is not None else '',
                        'source': source_key,
                        'category': category,
                    }
                    
                    # 计算新鲜度
                    article['freshness_score'] = calculate_freshness(article.get('published', ''))
                    
                    # 只保留最近7天的文章
                    if article['freshness_score'] >= 6:
                        articles.append(article)
                    
    except Exception as e:
        print(f"     ⚠️ 解析失败: {e}")
    
    return articles

def calculate_freshness(published_date: str) -> int:
    """计算新鲜度（0-10）"""
    if not published_date:
        return 5
    
    try:
        from email.utils import parsedate_to_datetime
        parsed_date = parsedate_to_datetime(published_date)
        
        if parsed_date.tzinfo is None:
            parsed_date = parsed_date.replace(tzinfo=datetime.timezone.utc)
        
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
    """获取所有文章"""
    all_articles = []
    
    print("📡 正在获取 BestBlogs RSS 源...")
    
    for source_key, source_config in RSS_SOURCES.items():
        try:
            print(f"  → {source_config['name']}")
            
            # 获取 RSS
            xml_content = fetch_rss(source_config['url'], timeout=15, retries=2)
            
            if xml_content:
                # 解析
                articles = parse_rss(xml_content, source_key, source_config['category'])
                
                print(f"     📊 解析到 {len(articles)} 篇文章（最近7天内）")
                all_articles.extend(articles)
            else:
                print(f"     ❌ 获取失败")
                
        except Exception as e:
            print(f"  ⚠️ {source_config['name']} 处理失败: {e}")
    
    print(f"✅ 共获取 {len(all_articles)} 篇文章")
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
            published = article.get('published', '')
            if published:
                digest += f"   * 发布：{published[:20]}...\n"
            
            digest += f"   * 链接：{article['link']}\n\n"
    
    digest += "━━━━━━━━━━━━━━━━\n"
    digest += "来源：BestBlogs.dev | 管理订阅：https://www.bestblogs.dev/#subscribe"
    
    return digest

def main():
    """主函数"""
    print("🚀 每日技术摘要（BestBlogs 源）")
    print("=" * 50)
    
    # 获取文章
    articles = fetch_articles()
    
    if not articles:
        print("\n❌ 没有获取到任何文章")
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
