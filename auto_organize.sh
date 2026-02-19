#!/bin/bash

###############################################################################
# OneDrive 自动整理脚本
#
# 功能：
# 1. 镜像 notes/ 目录到 auto-notes/
# 2. 镜像 new-note/ 目录到 auto-notes/
# 3. 不修改原始目录（notes/ 和 new-note/）
#
# 使用方法：
#   chmod +x auto_organize.sh
#   ./auto_organize.sh --dry-run    # 预览操作
#   ./auto_organize.sh            # 实际执行
#
# 作者：OpenClaw
# 创建时间：2026-02-16
# 执行时间：每天凌晨 1:00（北京时间）
#
###############################################################################

# 配置
NOTES="$HOME/onedrive/notes"
NEW_NOTE="$HOME/onedrive/new-note"
AUTO_NOTES="$HOME/onedrive/auto-notes"

# 日志文件
LOG_FILE="$AUTO_NOTES/organize.log"

# 颜览模式
DRY_RUN=false

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 创建目录结构
create_structure() {
    log "创建目录结构..."

    # 创建顶级目录
    mkdir -p "$AUTO_NOTES"/{Projects,Personal,Learning,Environment,Archives}

    # Projects 子目录
    mkdir -p "$AUTO_NOTES/Projects"/{Coding,Data}

    # Coding 子目录
    mkdir -p "$AUTO_NOTES/Projects/Coding"/{Cloud,Tools,VSCode}

    # Personal 子目录
    mkdir -p "$AUTO_NOTES/Personal"/{Journal,Study,Ideas}

    # Learning 子目录
    mkdir -p "$AUTO_NOTES/Learning"/{Jupyter,Python,PPT,LLM}

    # Environment 子目录
    mkdir -p "$AUTO_NOTES/Environment"/{Linux,Cloud,IDE,WSL,Tmux}

    # Archives 子目录
    mkdir -p "$AUTO_NOTES/Archives"/{OldNotes,OldAttachments}

    log "目录结构创建完成"
}

# 镜像 notes/ 内容
mirror_notes() {
    log "镜像 notes/ 目录到 auto-notes/..."

    # Projects
    if [ -d "$NOTES/jupyter" ]; then
        rsync -av --delete "$NOTES/jupyter/" "$AUTO_NOTES/Projects/Learning/Jupyter/"
    fi
    if [ -d "$NOTES/python" ]; then
        rsync -av --delete "$NOTES/python/" "$AUTO_NOTES/Projects/Learning/Python/"
    fi
    if [ -d "$NOTES/k8s" ]; then
        rsync -av --delete "$NOTES/k8s/" "$AUTO_NOTES/Projects/Coding/k8s/"
    fi
    if [ -d "$NOTES/graphql" ]; then
        rsync -av --delete "$NOTES/graphql/" "$AUTO_NOTES/Projects/Coding/graphql/"
    fi
    if [ -d "$NOTES/java" ]; then
        rsync -av --delete "$NOTES/java/" "$AUTO_NOTES/Projects/Coding/java/"
    fi
    if [ -d "$NOTES/pingcode" ]; then
        rsync -av --delete "$NOTES/pingcode/" "$AUTO_NOTES/Projects/Coding/pingcode/"
    fi
    if [ -d "$NOTES/.vscode" ]; then
        rsync -av --delete "$NOTES/.vscode/" "$AUTO_NOTES/Environment/VSCode/"
    fi

    # Data
    if [ -d "$NOTES/数学" ]; then
        rsync -av --delete "$NOTES/数学/" "$AUTO_NOTES/Projects/Data/Learning/Math/"
    fi
    if [ -d "$NOTES/pingcode" ]; then
        rsync -av --delete "$NOTES/pingcode/" "$AUTO_NOTES/Projects/Data/pingcode/"
    fi

    # Environment
    if [ -d "$NOTES/wsl环境配置" ]; then
        rsync -av --delete "$NOTES/wsl环境配置/" "$AUTO_NOTES/Environment/WSL/"
    fi

    # Personal
    if [ -d "$NOTES/草稿" ]; then
        rsync -av --delete "$NOTES/草稿/" "$AUTO_NOTES/Archives/Drafts/"
    fi

    log "notes/ 目录镜像完成"
}

# 镜像 new-note/ 内容
mirror_new_notes() {
    log "镜像 new-note/ 目录到 auto-notes/..."

    # Learning
    if [ -d "$NEW_NOTE/jupyter" ]; then
        rsync -av --delete "$NEW_NOTE/jupyter/" "$AUTO_NOTES/Projects/Learning/Jupyter/"
    fi
    if [ -d "$NEW_NOTE/ppt" ]; then
        rsync -av --delete "$NEW_NOTE/ppt/" "$AUTO_NOTES/Learning/Presentation/PPT/"
    fi
    if [ -d "$NEW_NOTE/python" ]; then
        rsync -av --delete "$NEW_NOTE/python/" "$AUTO_NOTES/Projects/Learning/Python/"
    fi

    # 将其他目录移动到对应位置
    if [ -d "$NEW_NOTE/jupyter" ]; then
        rsync -av --delete "$NEW_NOTE/jupyter/" "$AUTO_NOTES/Projects/Learning/Jupyter/"
    fi
    if [ -d "$NEW_NOTE/jupyter" ]; then
        rsync -av --delete "$NEW_NOTE/jupyter/" "$AUTO_NOTES/Projects/Learning/Jupyter/"
    fi
    if [ -d "$NEW_NOTE/jupyter" ]; then
        rsync -av --delete "$NEW_NOTE/jupyter/" "$AUTO_NOTES/Projects/Learning/Jupyter/"
    fi

    log "new-note/ 目录镜像完成"
}

# 创建索引文件
create_index() {
    log "创建索引文件..."

    cat > "$AUTO_NOTES/README.md" << 'EOF'
# OneDrive 自动整理结果

**整理时间：** $(date +'%Y-%m-%d %H:%M:%S')

**目录结构：**
\`\`\`
$AUTO_NOTES/
├── 📁 Projects/          # 项目笔记
│   ├── 💻 Coding/
│   │   ├── ☁️ Cloud/
│   │   ├── 🔧 Tools/
│   │   ├── 📊 Data/
│   └── 📦 IDE/
├── 📝 Personal/          # 个人笔记
│   ├── 📖 Journal/
│   ├── 📚 Study/
│   └── 💡 Ideas/
├── 📚 Learning/         # 学习笔记
│   ├── 📓 Jupyter/
│   ├── 🐍 Python/
│   ├── 📊 PPT/
│   └── 🤖 LLM/
├── 🔧 Environment/       # 环境和配置
│   ├── 💻 Linux/
│   ├── ☁️ Cloud/
│   ├── 📦 IDE/
│   ├── 💾 WSL/
│   └── 💻 Tmux/
└── 📦 Archives/          # 归档
    ├── 📂 OldNotes/          # notes/ 和 new-note/ 的备份
    └── 📎 OldAttachments/  # 附件的备份
\`\`\`

**文件统计：**
\`\`\`
总文件数：$(find "$AUTO_NOTES" -type f | wc -l)
总目录数：$(find "$AUTO_NOTES" -type d | wc -l)
\`\`\`

**操作日志：**
\`\`\`
tail -n 100 "$LOG_FILE"
\`\`\`
EOF

    log "索引文件创建完成"
}

# 显示统计
show_stats() {
    log "显示统计信息..."

    echo "=== auto-notes/ 目录统计 ==="
    echo ""
    echo "文件总数：$(find "$AUTO_NOTES" -type f | wc -l)"
    echo "目录总数：$(find "$AUTO_NOTES" -type d | wc -l)"
    echo ""
    echo "磁盘使用：$(du -sh "$AUTO_NOTES" | tail -1)"
}

# 主函数
main() {
    log "=== 开始自动整理 ==="
    log "预览模式：$DRY_RUN"

    if [ "$DRY_RUN" = true ]; then
        echo "📋 预览模式（不会实际移动文件）"
        create_structure
        echo ""
        echo "将创建以下目录结构："
        tree -L -d "$AUTO_NOTES" 2>/dev/null || find "$AUTO_NOTES" -type d | sort
        create_index
        show_stats
        echo ""
        echo "✅ 预览完成"
        echo "实际执行时（移除 --dry-run 参数）将实际移动文件"
    else
        echo "🚀 实际模式（将实际移动文件）"
        create_structure
        echo ""
        echo "步骤 1：镜像 notes/ 目录..."
        mirror_notes
        echo ""
        echo "步骤 2：镜像 new-note/ 目录..."
        mirror_new_notes
        echo ""
        echo "步骤 3：创建索引..."
        create_index
        echo ""
        echo "步骤 4：显示统计..."
        show_stats
        echo ""
        echo "✅ 自动整理完成！"
        log "整理完成"
fi
}

# 执行主函数
main
