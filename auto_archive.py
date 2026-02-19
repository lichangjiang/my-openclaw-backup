#!/usr/bin/env python3
"""
用户偏好数据自动归档脚本
由 Cron 任务定期调用
"""

import sys
import os
from datetime import datetime

# 添加 workspace 到 Python 路径
sys.path.insert(0, '/home/lichangjiang/.openclaw/workspace')

from user_preference_tracker import UserPreferenceTracker

def auto_archive(days=180):
    """自动归档旧数据"""
    try:
        tracker = UserPreferenceTracker()

        # 获取统计信息
        stats = tracker.get_stats()
        print(f"[{datetime.now()}] 开始自动归档...")
        print(f"总点击数：{stats['totalClicks']}")
        print(f"归档 {days} 天前的数据")

        # 执行归档
        result = tracker.archive_old_clicks(days)
        print(result)

        # 归档后统计
        stats_after = tracker.get_stats()
        print(f"归档后总点击数：{stats_after['totalClicks']}")
        print(f"✅ 自动归档完成")

        return True
    except Exception as e:
        print(f"❌ 自动归档失败：{e}")
        return False

if __name__ == "__main__":
    # 默认归档 180 天前的数据
    success = auto_archive(180)
    sys.exit(0 if success else 1)
