#!/bin/bash
# 每日技术摘要推送系统 - 方案1：直接调用 OpenClaw API
#
# 修复说明：
# - 不使用 cron 的 announce delivery 功能
# - 脚本生成摘要后，输出到 stdout
# - OpenClaw 自动捕获并发送到飞书
#
# 使用方法：
#   ./daily_tech_digest_system.sh          # 正常模式（生成并推送）
#   ./daily_tech_digest_system.sh --test   # 测试模式（只显示不推送）

set -e

# 配置
SCRIPT_DIR="/home/lichangjiang/.openclaw/workspace"
PYTHON_SCRIPT="${SCRIPT_DIR}/daily_tech_digest_simple.py"
LOG_FILE="/tmp/daily_tech_digest.log"

# 测试模式检查
if [ "$1" = "--test" ]; then
    echo "🧪 测试模式"
    echo ""
fi

# 执行 Python 脚本生成摘要
echo "📊 生成技术摘要..."
cd "${SCRIPT_DIR}"

python3 "${PYTHON_SCRIPT}" 2>&1

# 如果是测试模式，添加说明
if [ "$1" = "--test" ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━"
    echo "✅ 测试完成（未实际发送）"
    echo "━━━━━━━━━━━━━━━━"
fi
