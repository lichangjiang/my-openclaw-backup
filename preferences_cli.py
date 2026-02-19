#!/usr/bin/env python3
"""
用户偏好数据管理工具
支持归档、查询、统计等功能
"""

import argparse
import sys
import json
from datetime import datetime, timedelta
from user_preference_tracker import UserPreferenceTracker

def main():
    parser = argparse.ArgumentParser(description='用户偏好数据管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 归档命令
    archive_parser = subparsers.add_parser('archive', help='归档旧数据')
    archive_parser.add_argument('days', type=int, help='归档 N 天前的数据')
    archive_parser.add_argument('--dry-run', action='store_true', help='仅显示将要归档的数据')

    # 统计命令
    stats_parser = subparsers.add_parser('stats', help='显示统计信息')

    # 查询命令
    query_parser = subparsers.add_parser('query', help='查询点击记录')
    query_parser.add_argument('--start-date', required=True, help='开始日期 (YYYY-MM-DD)')
    query_parser.add_argument('--end-date', help='结束日期 (YYYY-MM-DD)，默认为今天')
    query_parser.add_argument('--category', help='按类别过滤')
    query_parser.add_argument('--limit', type=int, default=50, help='限制返回数量')

    # 偏好分析命令
    analyze_parser = subparsers.add_parser('analyze', help='分析用户偏好')
    analyze_parser.add_argument('--detailed', action='store_true', help='显示详细分析')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    tracker = UserPreferenceTracker()

    try:
        if args.command == 'archive':
            # 归档旧数据
            if args.dry_run:
                # 显示将要归档的数据
                cutoff_date = datetime.now() - timedelta(days=args.days)
                clicks_to_archive = [
                    click for click in tracker.data["clickHistory"]
                    if datetime.fromisoformat(click["timestamp"]) < cutoff_date
                ]
                print(f"将归档 {len(clicks_to_archive)} 条记录（{args.days} 天前）")
                for click in clicks_to_archive[:10]:
                    print(f"  - {click['timestamp']}: {click['articleTitle'][:50]}")
                if len(clicks_to_archive) > 10:
                    print(f"  ... 还有 {len(clicks_to_archive) - 10} 条")
            else:
                # 执行归档
                result = tracker.archive_old_clicks(args.days)
                print(result)

        elif args.command == 'stats':
            # 显示统计信息
            stats = tracker.get_stats()
            print("=== 系统统计信息 ===")
            print(f"总点击次数：{stats['totalClicks']}")
            print(f"最近 30 天点击：{stats['recentClicks30Days']}")
            print(f"总主题数：{stats['totalTopics']}")
            print(f"活跃来源数：{stats['activeSources']}")

        elif args.command == 'query':
            # 查询点击记录
            start_date = args.start_date
            end_date = args.end_date or datetime.now().strftime("%Y-%m-%d")

            clicks = tracker.get_clicks_by_date_range(start_date, end_date)

            if args.category:
                clicks = [c for c in clicks if c['category'] == args.category]

            clicks = clicks[:args.limit]

            print(f"=== 查询结果：{start_date} 至 {end_date} ===")
            print(f"找到 {len(clicks)} 条记录\n")

            for i, click in enumerate(clicks, 1):
                print(f"{i}. [{click['timestamp']}] {click['articleTitle']}")
                print(f"   类别：{click['category']} | 主题：{', '.join(click['topics'])} | 来源：{click['source']}")
                print(f"   AI 评分：{click['aiScore']}")
                print()

        elif args.command == 'analyze':
            # 分析用户偏好
            analysis = tracker.analyze_preferences()
            ratio = tracker.generate_personalized_ratio()

            print("=== 用户偏好分析 ===")
            print(f"\n总点击次数：{analysis['totalClicks']}")
            print(f"\n类别权重：")
            for cat_name, weight in analysis['categoryWeights'].items():
                clicks = tracker.data["preferences"]["categories"][cat_name]["clicks"]
                print(f"  {cat_name}: {weight*100:.1f}% ({clicks} 次)")

            print(f"\n热门主题 TOP 5：")
            for i, (topic, score) in enumerate(analysis['topTopics'][:5], 1):
                print(f"  {i}. {topic}: {score} 次")

            print(f"\n今日推荐比例：")
            print(f"  编程技术：{ratio['programming']} 篇")
            print(f"  AI 前沿：{ratio['ai']} 篇")
            print(f"  产品设计：{ratio['product']} 篇")

            if args.detailed:
                print(f"\n来源偏好：")
                for source, count in analysis['sourcePreferences'].items():
                    print(f"  {source}: {count} 次")

                print("\n详细报告：")
                insights = tracker.get_personalization_insights()
                print(insights)

    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
