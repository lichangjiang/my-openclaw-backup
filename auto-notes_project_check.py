#!/usr/bin/env python3
"""
检查 OneDrive auto-notes 目录中的代码项目
"""

import os
from pathlib import Path

BASE_DIR = "/home/lichangjiang/onedrive/auto-notes"

# 代码项目特征标识符
CODE_PROJECT_INDICATORS = {
    # 项目配置文件
    'config_files': [
        'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
        'requirements.txt', 'setup.py', 'pyproject.toml', 'poetry.lock',
        'pom.xml', 'build.gradle', 'gradle.properties',
        'go.mod', 'go.sum',
        'Cargo.toml', 'Cargo.lock',
        'composer.json',
        'Gemfile', 'Gemfile.lock',
        '*.csproj', '*.sln',
        'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
    ],
    # 源代码目录
    'source_dirs': [
        'src', 'lib', 'app', 'apps', 'packages',
        'main', 'cmd', 'internal', 'pkg',
    ],
    # 其他标识
    'other_indicators': [
        '.git', '.vscode', '.idea',
        'README.md', 'LICENSE', 'CONTRIBUTING.md',
        'Makefile', 'CMakeLists.txt', 'setup.cfg',
    ],
}

# 代码文件扩展名
CODE_FILE_EXTENSIONS = [
    '.py', '.js', '.ts', '.jsx', '.tsx',
    '.java', '.kt', '.scala', '.groovy',
    '.go', '.rs', '.c', '.cpp', '.h', '.hpp',
    '.cs', '.vb', '.fs',
    '.php', '.rb', '.swift', '.dart',
    '.sh', '.bat', '.ps1',
    '.yml', '.yaml', '.json', '.xml', '.toml', 'ini', 'cfg',
]

def is_code_project(directory):
    """判断目录是否是代码项目"""
    dir_path = Path(directory)

    # 检查配置文件
    for config in CODE_PROJECT_INDICATORS['config_files']:
        if any(dir_path.glob(config)):
            return True, f"包含配置文件: {config}"

    # 检查源代码目录
    for src_dir in CODE_PROJECT_INDICATORS['source_dirs']:
        src_path = dir_path / src_dir
        if src_path.is_dir():
            # 检查源代码目录下是否有代码文件
            for ext in CODE_FILE_EXTENSIONS:
                if list(src_path.glob(f'*{ext}')):
                    return True, f"包含源代码目录: {src_dir}"

    # 检查其他标识
    for indicator in CODE_PROJECT_INDICATORS['other_indicators']:
        if any(dir_path.glob(indicator)):
            # 排除 node_modules 中的 .vscode
            if indicator in ['.vscode', '.idea']:
                if 'node_modules' not in str(directory):
                    return True, f"包含项目标识: {indicator}"
            else:
                return True, f"包含项目标识: {indicator}"

    # 检查是否有代码文件（在根目录）
    for ext in CODE_FILE_EXTENSIONS[:10]:  # 检查主要代码文件扩展名
        code_files = list(dir_path.glob(f'*{ext}'))
        if code_files and len(code_files) > 2:  # 至少有 3 个代码文件
            return True, f"包含代码文件: {len(code_files)} 个"

    # 检查是否有 node_modules（Node.js 项目）
    node_modules = dir_path / 'node_modules'
    if node_modules.is_dir() and any(dir_path.glob('package.json')):
        return True, "Node.js 项目（包含 node_modules 和 package.json）"

    return False, None

def check_directory_structure():
    """检查目录结构并识别代码项目"""

    print("=" * 80)
    print("OneDrive auto-notes 目录结构分析")
    print("=" * 80)
    print()

    base_path = Path(BASE_DIR)

    # 统计
    total_dirs = 0
    code_projects = []
    empty_dirs = []
    note_dirs = []

    # 递归遍历所有目录
    for root, dirs, files in os.walk(BASE_DIR):
        root_path = Path(root)

        # 跳过 node_modules
        if 'node_modules' in root:
            continue

        total_dirs += 1

        # 检查是否是代码项目
        is_project, reason = is_code_project(root)

        if is_project:
            code_projects.append({
                'path': root,
                'reason': reason,
                'files': len(files),
            })
        elif len(files) == 0 and len(dirs) == 0:
            empty_dirs.append(root)
        else:
            note_dirs.append({
                'path': root,
                'files': len(files),
                'dirs': len(dirs),
            })

    # 输出统计
    print(f"📊 统计信息:")
    print(f"  总目录数: {total_dirs}")
    print(f"  代码项目: {len(code_projects)}")
    print(f"  笔记目录: {len(note_dirs)}")
    print(f"  空目录: {len(empty_dirs)}")
    print()

    # 输出代码项目
    if code_projects:
        print("=" * 80)
        print("🔧 代码项目目录")
        print("=" * 80)
        for project in sorted(code_projects, key=lambda x: x['path']):
            rel_path = project['path'].replace(BASE_DIR + '/', '')
            print(f"\n📁 {rel_path}")
            print(f"   原因: {project['reason']}")
            print(f"   文件数: {project['files']}")
        print()

    # 输出笔记目录
    if note_dirs:
        print("=" * 80)
        print(f"📝 笔记目录（前 20 个）")
        print("=" * 80)
        sorted_notes = sorted(note_dirs, key=lambda x: x['path'])
        for note in sorted_notes[:20]:
            rel_path = note['path'].replace(BASE_DIR + '/', '')
            if note['files'] > 0 or note['dirs'] > 0:
                print(f"\n📁 {rel_path}")
                print(f"   文件: {note['files']}, 子目录: {note['dirs']}")
        print()

    # 输出空目录
    if empty_dirs:
        print("=" * 80)
        print(f"📂 空目录（前 20 个）")
        print("=" * 80)
        for empty_dir in sorted(empty_dirs)[:20]:
            rel_path = empty_dir.replace(BASE_DIR + '/', '')
            print(f"📁 {rel_path}")
        print()

    # 保存到文件
    output_file = "/home/lichangjiang/.openclaw/workspace/auto_notes_project_check_report.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("OneDrive auto-notes 目录结构分析报告\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"总目录数: {total_dirs}\n")
        f.write(f"代码项目: {len(code_projects)}\n")
        f.write(f"笔记目录: {len(note_dirs)}\n")
        f.write(f"空目录: {len(empty_dirs)}\n\n")

        if code_projects:
            f.write("=" * 80 + "\n")
            f.write("代码项目目录\n")
            f.write("=" * 80 + "\n\n")
            for project in sorted(code_projects, key=lambda x: x['path']):
                rel_path = project['path'].replace(BASE_DIR + '/', '')
                f.write(f"{rel_path}\n")
                f.write(f"  原因: {project['reason']}\n")
                f.write(f"  文件数: {project['files']}\n\n")

    print(f"✅ 报告已保存到: {output_file}")

if __name__ == '__main__':
    check_directory_structure()
