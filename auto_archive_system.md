# 用户偏好数据自动归档系统

## 概述

系统会每 6 个月自动归档 180 天前的点击记录，防止主文件过大。

## Cron 任务配置

**任务 ID：** 612fedfc-4e45-497d-a3a1-28fbf8cb34a2
**任务名称：** 用户偏好数据自动归档（每 6 个月）
**归档周期：** 每 180 天（约 6 个月）
**会话类型：** isolated（独立会话执行）

## 归档流程

1. **触发时机：** 每 180 天自动执行
2. **归档内容：** 180 天前的所有点击记录
3. **归档文件：** `user_preferences_archive_YYYYMMDD.json`
4. **执行脚本：** `/home/lichangjiang/.openclaw/workspace/auto_archive.py`

## 归档文件格式

归档文件包含以下信息：
```json
{
  "archiveDate": "归档日期",
  "cutoffDate": "截止日期（180天前）",
  "archivedClicks": [
    {
      "timestamp": "点击时间",
      "articleTitle": "文章标题",
      "articleUrl": "文章链接",
      "category": "类别",
      "topics": ["主题列表"],
      "source": "来源",
      "aiScore": 评分
    }
  ],
  "count": 归档记录数
}
```

## 手动归档

如果需要手动归档，可以使用 CLI 工具：

```bash
# 归档 1 年前的数据
python3 preferences_cli.py archive 365

# 归档 6 个月前的数据
python3 preferences_cli.py archive 180

# 归档前预览（不实际归档）
python3 preferences_cli.py archive 365 --dry-run
```

## 查看归档文件

```bash
# 列出所有归档文件
ls -lh /home/lichangjiang/.openclaw/workspace/user_preferences_archive_*.json

# 查看特定归档文件
cat /home/lichangjiang/.openclaw/workspace/user_preferences_archive_20260101.json
```

## 数据恢复

如果需要将归档的数据重新导入到主文件，可以：

1. 读取归档文件
2. 将 `archivedClicks` 数组追加到主文件的 `clickHistory`
3. 使用 `user_preference_tracker.py` 的 `save_preferences()` 保存

## 注意事项

- 归档后，旧数据不会用于个性化推荐
- 归档文件应定期备份
- 建议每年检查一次归档文件数量
- 可以使用 `preferences_cli.py stats` 查看当前数据量
