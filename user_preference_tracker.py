#!/usr/bin/env python3
"""
用户偏好追踪系统
自动记录用户点击、分析偏好、生成个性化推荐策略
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

PREFERENCES_FILE = "/home/lichangjiang/.openclaw/workspace/user_preferences.json"

class UserPreferenceTracker:
    def __init__(self):
        self.data = self._load_preferences()

    def _load_preferences(self) -> dict:
        """加载用户偏好数据"""
        if os.path.exists(PREFERENCES_FILE):
            with open(PREFERENCES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._create_default_preferences()

    def _create_default_preferences(self) -> dict:
        """创建默认偏好配置"""
        return {
            "profile": {
                "createdAt": datetime.now().isoformat(),
                "lastUpdated": datetime.now().isoformat()
            },
            "preferences": {
                "categories": {
                    "programming": {"weight": 0.5, "clicks": 0, "readCount": 0, "avgReadTime": 0},
                    "ai": {"weight": 0.5, "clicks": 0, "readCount": 0, "avgReadTime": 0},
                    "product": {"weight": 0.2, "clicks": 0, "readCount": 0, "avgReadTime": 0}
                },
                "topics": {
                    "react": 0, "python": 0, "rust": 0, "go": 0,
                    "ai-architecture": 0, "frontend": 0, "backend": 0,
                    "product-design": 0, "devops": 0
                },
                "sources": {
                    "bestblogs": 0, "hackernews": 0, "reddit": 0, "openai": 0
                }
            },
            "clickHistory": [],
            "readingSession": []
        }

    def save_preferences(self):
        """保存偏好数据"""
        self.data["profile"]["lastUpdated"] = datetime.now().isoformat()
        with open(PREFERENCES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def record_click(self, article: Dict[str, Any], category: str, topics: List[str] = None, source: str = None):
        """记录用户点击"""
        click_record = {
            "timestamp": datetime.now().isoformat(),
            "articleTitle": article.get("title", ""),
            "articleUrl": article.get("url", ""),
            "category": category,
            "topics": topics or [],
            "source": source or "bestblogs",
            "aiScore": article.get("aiScore", 0)
        }

        # 添加到点击历史
        self.data["clickHistory"].append(click_record)

        # 更新类别偏好
        if category in self.data["preferences"]["categories"]:
            cat_pref = self.data["preferences"]["categories"][category]
            cat_pref["clicks"] += 1

        # 更新主题偏好
        if topics:
            for topic in topics:
                if topic in self.data["preferences"]["topics"]:
                    self.data["preferences"]["topics"][topic] += 1

        # 更新来源偏好
        if source and source in self.data["preferences"]["sources"]:
            self.data["preferences"]["sources"][source] += 1

        # 保存完整的点击历史（不限制数量）
        # 如果需要归档旧数据，可以定期执行 archive_old_clicks() 方法
        self.save_preferences()

        return click_record

    def analyze_preferences(self) -> Dict[str, Any]:
        """分析用户偏好"""
        prefs = self.data["preferences"]

        # 1. 分析类别偏好
        total_clicks = sum(cat["clicks"] for cat in prefs["categories"].values())
        if total_clicks > 0:
            for cat_name, cat_data in prefs["categories"].items():
                cat_data["weight"] = cat_data["clicks"] / total_clicks
        else:
            # 默认权重
            prefs["categories"]["programming"]["weight"] = 0.5
            prefs["categories"]["ai"]["weight"] = 0.5
            prefs["categories"]["product"]["weight"] = 0.2

        # 2. 分析主题偏好（找出前 5 个）
        topic_scores = [(topic, score) for topic, score in prefs["topics"].items()]
        topic_scores.sort(key=lambda x: x[1], reverse=True)
        top_topics = topic_scores[:5]

        # 3. 分析来源偏好
        total_source_clicks = sum(prefs["sources"].values())
        if total_source_clicks > 0:
            pass  # 已经有实际点击数据

        return {
            "totalClicks": total_clicks,
            "categoryWeights": {k: v["weight"] for k, v in prefs["categories"].items()},
            "topTopics": top_topics,
            "sourcePreferences": prefs["sources"]
        }

    def generate_personalized_ratio(self) -> Dict[str, int]:
        """生成个性化推荐比例"""
        analysis = self.analyze_preferences()

        # 基于点击量计算比例
        prog_weight = self.data["preferences"]["categories"]["programming"]["weight"]
        ai_weight = self.data["preferences"]["categories"]["ai"]["weight"]
        product_weight = self.data["preferences"]["categories"]["product"]["weight"]

        # 转换为整数（每天 10 篇）
        total = 10
        prog_count = int(total * prog_weight)
        ai_count = int(total * ai_weight)
        product_count = total - prog_count - ai_count

        # 确保至少有 1 篇
        prog_count = max(1, min(6, prog_count))
        ai_count = max(1, min(7, ai_count))
        product_count = max(1, min(2, product_count))

        return {
            "programming": prog_count,
            "ai": ai_count,
            "product": product_count,
            "total": total
        }

    def get_personalization_insights(self) -> str:
        """生成个性化洞察报告"""
        analysis = self.analyze_preferences()
        ratio = self.generate_personalized_ratio()

        top_topics = analysis["topTopics"][:3]
        top_topics_str = "、".join([f"{topic}({score}次)" for topic, score in top_topics])

        insights = f"""
## 📊 个性化推荐分析报告

### 🎯 用户偏好画像
- 总点击次数：{analysis['totalClicks']}
- 编程技术：{analysis['categoryWeights']['programming']*100:.1f}%
- AI 前沿：{analysis['categoryWeights']['ai']*100:.1f}%
- 产品设计：{analysis['categoryWeights']['product']*100:.1f}%

### 🔥 热门主题 TOP 5
{top_topics_str}

### 📅 今日推荐比例
- 编程技术：{ratio['programming']} 篇 ({ratio['programming']*10}%)
- AI 前沿：{ratio['ai']} 篇 ({ratio['ai']*10}%)
- 产品设计：{ratio['product']} 篇 ({ratio['product']*10}%)

### 💡 推荐策略
1. 根据你的点击历史，自动调整内容比例
2. 优先推荐你关注的热门主题
3. 从你偏好的来源筛选高质量内容
4. 动态学习：每天更新一次画像
        """

        return insights

    def get_clicks_by_date_range(self, start_date: str, end_date: str) -> List[dict]:
        """获取指定日期范围内的点击记录"""
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        filtered_clicks = []
        for click in self.data["clickHistory"]:
            click_dt = datetime.fromisoformat(click["timestamp"])
            if start_dt <= click_dt <= end_dt:
                filtered_clicks.append(click)

        return filtered_clicks

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_clicks = len(self.data["clickHistory"])

        # 计算最近的点击（最近 30 天）
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_clicks = [
            click for click in self.data["clickHistory"]
            if datetime.fromisoformat(click["timestamp"]) > thirty_days_ago
        ]

        return {
            "totalClicks": total_clicks,
            "recentClicks30Days": len(recent_clicks),
            "totalTopics": len([t for t in self.data["preferences"]["topics"].values() if t > 0]),
            "activeSources": len([s for s in self.data["preferences"]["sources"].values() if s > 0])
        }

    def archive_old_clicks(self, days: int = 365) -> str:
        """归档旧点击记录到单独文件"""
        cutoff_date = datetime.now() - timedelta(days=days)
        archive_file = PREFERENCES_FILE.replace(".json", f"_archive_{cutoff_date.strftime('%Y%m%d')}.json")

        # 分离旧记录和新记录
        old_clicks = []
        new_clicks = []

        for click in self.data["clickHistory"]:
            click_dt = datetime.fromisoformat(click["timestamp"])
            if click_dt < cutoff_date:
                old_clicks.append(click)
            else:
                new_clicks.append(click)

        if not old_clicks:
            return f"没有需要归档的旧数据（{days} 天前）"

        # 创建归档文件
        archive_data = {
            "archiveDate": datetime.now().isoformat(),
            "cutoffDate": cutoff_date.isoformat(),
            "archivedClicks": old_clicks,
            "count": len(old_clicks)
        }

        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(archive_data, f, ensure_ascii=False, indent=2)

        # 更新主文件
        self.data["clickHistory"] = new_clicks
        self.save_preferences()

        return f"✅ 已归档 {len(old_clicks)} 条旧记录到 {archive_file}"

def main():
    """测试代码"""
    tracker = UserPreferenceTracker()

    print("=== 用户偏好追踪系统测试 ===")
    print("\n1. 记录模拟点击...")

    # 模拟一些点击
    tracker.record_click(
        article={"title": "React 19 新特性详解", "url": "https://example.com/react", "aiScore": 9.5},
        category="programming",
        topics=["react", "frontend", "javascript"],
        source="bestblogs"
    )

    tracker.record_click(
        article={"title": "OpenAI o1 模型架构", "url": "https://example.com/openai", "aiScore": 9.8},
        category="ai",
        topics=["ai-architecture", "frontend"],
        source="openai"
    )

    tracker.record_click(
        article={"title": "产品设计中的微交互", "url": "https://example.com/product", "aiScore": 8.5},
        category="product",
        topics=["product-design", "ux"],
        source="bestblogs"
    )

    print("\n2. 分析用户偏好...")
    analysis = tracker.analyze_preferences()

    print("\n3. 生成个性化推荐比例...")
    ratio = tracker.generate_personalized_ratio()

    print("\n4. 生成个性化洞察报告...")
    insights = tracker.get_personalization_insights()
    print(insights)

    print("\n✅ 测试完成！")

if __name__ == "__main__":
    main()
