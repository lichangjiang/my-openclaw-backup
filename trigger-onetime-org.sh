#!/bin/bash

# OneDrive 一次性整理任务
# 触发时间：2026-02-17 01:00 UTC（北京时间 09:00）

# 创建定时器
# 使用 transient timer 在指定时间执行一次
systemd-run --on-calendar=2026-02-17T01:00:00 --user --unit=onedrive-auto-organize-onetime --timer-property=Persistent=false /home/lichangjiang/.openclaw/workspace/auto_organize.sh

echo "✅ 已创建一次性定时器：明天凌晨 1 点（北京时间 9 点）"