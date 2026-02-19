#!/usr/bin/env python3
"""
SQLite 版本的偏好追踪系统
性能更好的长期方案
"""
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional

DATABASE_FILE = "/home/lichangjiang/.openclaw/workspace/user_preferences.db"

class SQLitePreferenceTracker:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_FILE)
        self._create_tables()
        self.conn.row_factory = sqlite3.Row  # 返回字典而非元组

    def _create_tables(self):
        """创建数据库表"""
        cursor = self.conn.cursor()
        
        # 点击记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                article_title TEXT NOT NULL,
                article_url TEXT NOT NULL,
                category TEXT NOT NULL,
                source TEXT NOT NULL,
                ai_score REAL DEFAULT 0
            )
        ''')
        
        # 主题表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_name TEXT UNIQUE NOT NULL,
                click_count INTEGER DEFAULT 0,
                last_clicked_at TIMESTAMP
            )
        ''')
        
        # 类别表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT UNIQUE NOT NULL,
                click_count INTEGER DEFAULT 0,
                weight REAL DEFAULT 0.5
            )
        ''')
        
        # 点击-主题关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS click_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                click_id INTEGER NOT NULL,
                topic_id INTEGER NOT NULL,
                FOREIGN KEY (click_id) REFERENCES clicks (id),
                FOREIGN KEY (topic_id) REFERENCES topics (id)
            )
        ''')
        
        self.conn.commit()
    
    def record_click(self, article: Dict[str, Any], category: str, 
                    topics: List[str] = None, source: str = "bestblogs"):
        """记录用户点击"""
        cursor = self.conn.cursor()
        
        # 插入点击记录（不包含 created_at，让它使用默认值）
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO clicks (timestamp, article_title, article_url, category, source, ai_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (current_time, article.get("title", ""),
              article.get("url", ""), category, source, article.get("aiScore", 0)))
        
        click_id = cursor.lastrowid
        
        # 更新类别
        cursor.execute('''
            INSERT INTO categories (category_name, click_count)
            VALUES (?, 1)
            ON CONFLICT(category_name) DO UPDATE SET
                click_count = click_count + 1
        ''', (category,))
        
        # 更新主题
        if topics:
            for topic in topics:
                # 插入或更新主题
                cursor.execute('''
                    INSERT INTO topics (topic_name, click_count, last_clicked_at)
                    VALUES (?, 1, ?)
                    ON CONFLICT(topic_name) DO UPDATE SET
                        click_count = click_count + 1,
                        last_clicked_at = ?
                ''', (topic, current_time))
                
                # 关联点击和主题
                cursor.execute('''
                    INSERT INTO click_topics (click_id, topic_id)
                    VALUES (?, (SELECT id FROM topics WHERE topic_name = ?))
                ''', (click_id, topic))
        
        self.conn.commit()
        return click_id
    
    def get_category_stats(self) -> Dict[str, Any]:
        """获取类别统计"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT SUM(click_count) FROM categories')
        total = cursor.fetchone()[0] if cursor.fetchone() else 0
        
        if total == 0:
            return {
                "programming": {"weight": 0.5, "clicks": 0},
                "ai": {"weight": 0.5, "clicks": 0},
                "product": {"weight": 0.2, "clicks": 0}
            }
        
        cursor.execute('SELECT category_name, click_count FROM categories')
        categories = {row[0]: {"clicks": row[1], "weight": 0} for row in cursor.fetchall()}
        
        # 重新计算权重
        for cat_name, cat_data in categories.items():
            categories[cat_name]["weight"] = cat_data["clicks"] / total
        
        return categories
    
    def get_top_topics(self, limit: int = 5) -> List[tuple]:
        """获取热门主题"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT topic_name, click_count
            FROM topics
            ORDER BY click_count DESC
            LIMIT ?
        ''', (limit,))
        
        return cursor.fetchall()
    
    def analyze_preferences(self) -> Dict[str, Any]:
        """分析用户偏好"""
        category_stats = self.get_category_stats()
        top_topics = self.get_top_topics(5)
        
        return {
            "categories": category_stats,
            "topTopics": top_topics,
            "totalClicks": sum(cat["clicks"] for cat in category_stats.values())
        }
    
    def cleanup_old_clicks(self, days: int = 90):
        """清理旧数据"""
        cursor = self.conn.cursor()
        # SQLite 的日期比较
        cutoff_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(f'''
            DELETE FROM clicks
            WHERE timestamp < datetime('{cutoff_date}', '-{days} days')
        ''')
        self.conn.commit()
        return cursor.rowcount
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM clicks')
        total_clicks = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT topic_name) FROM topics')
        total_topics = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM categories WHERE click_count > 0')
        active_categories = cursor.fetchone()[0]
        
        return {
            "totalClicks": total_clicks,
            "totalTopics": total_topics,
            "activeCategories": active_categories
        }
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()

def main():
    """测试 SQLite 版本"""
    tracker = SQLitePreferenceTracker()
    
    print("=== SQLite 版偏好追踪系统测试 ===")
    
    # 记录一些点击
    print("\n1. 记录模拟点击...")
    tracker.record_click(
        article={"title": "React 19 新特性", "url": "https://example.com", "aiScore": 9.5},
        category="programming",
        topics=["react", "frontend"],
        source="bestblogs"
    )
    
    tracker.record_click(
        article={"title": "OpenAI o1 模型", "url": "https://openai.com", "aiScore": 9.8},
        category="ai",
        topics=["ai-architecture"],
        source="openai"
    )
    
    tracker.record_click(
        article={"title": "产品微交互", "url": "https://example.com", "aiScore": 8.5},
        category="product",
        topics=["product-design", "ux"],
        source="bestblogs"
    )
    
    # 分析偏好
    print("\n2. 分析用户偏好...")
    analysis = tracker.analyze_preferences()
    print(f"总点击次数：{analysis['totalClicks']}")
    print(f"类别权重：")
    for cat_name, cat_data in analysis['categories'].items():
        print(f"  {cat_name}: {cat_data['clicks']} 次 ({cat_data['weight']*100:.1f}%)")
    print(f"热门主题：")
    for topic, count in analysis['topTopics'][:5]:
        print(f"  {topic} ({count} 次)")
    
    # 查看统计
    print("\n3. 数据库统计...")
    stats = tracker.get_stats()
    print(f"总点击记录：{stats['totalClicks']}")
    print(f"总主题数：{stats['totalTopics']}")
    print(f"活跃类别数：{stats['activeCategories']}")
    
    tracker.close()
    print("\n✅ 测试完成！")

if __name__ == "__main__":
    main()
