#!/bin/bash
# 每日技术摘要推送系统 - 自动化版本（BestBlogs 源）
# 方案1：直接生成摘要并输出，由 OpenClaw 捕获并自动发送

set -e

SCRIPT_DIR="/home/lichangjiang/.openclaw/workspace"
PYTHON_SCRIPT="${SCRIPT_DIR}/daily_tech_digest_final.py"

echo "📊 每日技术摘要推送系统（BestBlogs 源）"
echo "━━━━━━━━━━━━━━━━"
echo ""

# 生成摘要（超时 45 秒）
cd "${SCRIPT_DIR}"
timeout 45 python3 "${PYTHON_SCRIPT}" 2>&1 || {
    echo ""
    echo "⚠️ 获取 BestBlogs 源超时或失败"
    echo "📝 如果持续失败，请手动检查："
    echo "  1. ping www.bestblogs.dev"
    echo "  2. curl -L 'https://www.bestblogs.dev/zh/feeds/rss?featured=y'"
    echo "  3. nslookup www.bestblogs.dev"
}

echo ""
echo "━━━━━━━━━━━━━━━━"
echo "✅ 摘要生成完成，由 OpenClaw 自动捕获并发送"
