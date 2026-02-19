#!/usr/bin/env python3
"""
检查 SRS Word 数据库中所有单词和句子的拼写和翻译
通过 API 获取数据
"""

import json
import urllib.request
from datetime import datetime
import re

API_BASE_URL = "http://10.0.0.23:30080/api/knowledge_items"

def fetch_all_items():
    """分页获取所有数据"""
    all_items = []
    page = 1
    limit = 100
    total = None

    print("📡 正在从 API 获取数据...")

    while True:
        url = f"{API_BASE_URL}?page={page}&limit={limit}"
        print(f"  获取第 {page} 页...", end=" ")

        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode('utf-8'))

                if total is None:
                    total = data.get('total', 0)
                    print(f"(总计: {total} 条)")

                items = data.get('items', [])
                all_items.extend(items)
                print(f"已获取 {len(items)} 条, 累计 {len(all_items)} 条")

                if len(all_items) >= total:
                    break

                page += 1
        except Exception as e:
            print(f"❌ 获取数据失败: {e}")
            break

    return all_items

def check_spelling_basic(word):
    """基本的拼写检查"""
    issues = []

    # 检查是否为空
    if not word or word.strip() == '':
        issues.append("单词为空")
        return issues

    # 检查是否包含非字母字符（不包括常见的连字符、撇号等）
    if word and not re.match(r"^[a-zA-Z\s\-']+$", word):
        # 检查是否有明显的拼写错误（多个连续相同字母）
        if re.search(r"(.)\1\1+", word):
            issues.append("包含连续重复的字母")

    return issues

def check_sentence(sentence):
    """检查句子"""
    issues = []

    if not sentence or sentence.strip() == '':
        issues.append("句子为空")
        return issues

    # 检查大小写
    if sentence and not sentence[0].isupper():
        issues.append("首字母未大写")

    # 检查标点符号
    if sentence and not sentence.endswith(('.', '!', '?')):
        issues.append("句末缺少标点符号")

    return issues

def check_translation(translation):
    """检查翻译"""
    issues = []

    if not translation or translation.strip() == '':
        issues.append("翻译为空")
        return issues

    # 检查是否包含乱码字符（非中文、英文、常用标点）
    if translation:
        # 常用字符集：中文、英文、数字、常用标点
        allowed = re.compile(r'^[\u4e00-\u9fff\u3400-\u4dbf\w\s\-\'.,:;?!""''()、，。；：？！（）]+$')
        if not allowed.match(translation):
            issues.append("翻译包含异常字符")

    return issues

def main():
    print("=" * 80)
    print("SRS Word 拼写和翻译检查报告")
    print("=" * 80)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # 获取所有数据
    items = fetch_all_items()

    if not items:
        print("❌ 未能获取任何数据！")
        return

    print(f"✅ 成功获取 {len(items)} 条数据")
    print()

    # 统计
    word_count = 0
    sentence_count = 0
    word_issues = []
    sentence_issues = []

    # 分析数据
    for item in items:
        item_type = item.get('item_type')
        content = item.get('content', '')
        phonetic = item.get('phonetic_symbol')
        definition = item.get('definition')
        translation = item.get('translation')
        item_id = item.get('id')

        if item_type == 'word':
            word_count += 1

            # 检查单词
            issues = check_spelling_basic(content)
            if not definition:
                issues.append("缺少定义")

            if issues:
                word_issues.append({
                    'id': item_id,
                    'content': content,
                    'phonetic': phonetic,
                    'definition': definition,
                    'issues': issues
                })

        elif item_type == 'sentence':
            sentence_count += 1

            # 检查句子
            issues = check_sentence(content)
            trans_issues = check_translation(translation)
            issues.extend(trans_issues)

            if issues:
                sentence_issues.append({
                    'id': item_id,
                    'content': content,
                    'translation': translation,
                    'issues': issues
                })

    # 输出统计
    print("=" * 80)
    print("📊 统计信息")
    print("=" * 80)
    print(f"单词总数: {word_count}")
    print(f"句子总数: {sentence_count}")
    print(f"有问题的单词: {len(word_issues)}")
    print(f"有问题的句子: {len(sentence_issues)}")
    print()

    # 输出有问题的单词
    if word_issues:
        print("=" * 80)
        print("⚠️  有问题的单词")
        print("=" * 80)
        for item in word_issues:
            print(f"\nID: {item['id']}")
            print(f"单词: {item['content']}")
            if item['phonetic']:
                print(f"音标: {item['phonetic']}")
            if item['definition']:
                print(f"定义: {item['definition']}")
            print("问题:")
            for issue in item['issues']:
                print(f"  - {issue}")
            print("-" * 80)
        print()

    # 输出有问题的句子
    if sentence_issues:
        print("=" * 80)
        print("⚠️  有问题的句子")
        print("=" * 80)
        for item in sentence_issues:
            print(f"\nID: {item['id']}")
            print(f"句子: {item['content']}")
            if item['translation']:
                print(f"翻译: {item['translation']}")
            print("问题:")
            for issue in item['issues']:
                print(f"  - {issue}")
            print("-" * 80)
        print()

    # 生成报告文件
    output_file = f"/home/lichangjiang/.openclaw/workspace/srs_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("SRS Word 拼写和翻译检查报告\n")
        f.write("=" * 80 + "\n")
        f.write(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"单词总数: {word_count}\n")
        f.write(f"句子总数: {sentence_count}\n")
        f.write(f"有问题的单词: {len(word_issues)}\n")
        f.write(f"有问题的句子: {len(sentence_issues)}\n\n")

        if word_issues:
            f.write("=" * 80 + "\n")
            f.write("有问题的单词\n")
            f.write("=" * 80 + "\n\n")
            for item in word_issues:
                f.write(f"\nID: {item['id']}\n")
                f.write(f"单词: {item['content']}\n")
                if item['phonetic']:
                    f.write(f"音标: {item['phonetic']}\n")
                if item['definition']:
                    f.write(f"定义: {item['definition']}\n")
                f.write("问题:\n")
                for issue in item['issues']:
                    f.write(f"  - {issue}\n")
                f.write("-" * 80 + "\n")

        if sentence_issues:
            f.write("\n" + "=" * 80 + "\n")
            f.write("有问题的句子\n")
            f.write("=" * 80 + "\n\n")
            for item in sentence_issues:
                f.write(f"\nID: {item['id']}\n")
                f.write(f"句子: {item['content']}\n")
                if item['translation']:
                    f.write(f"翻译: {item['translation']}\n")
                f.write("问题:\n")
                for issue in item['issues']:
                    f.write(f"  - {issue}\n")
                f.write("-" * 80 + "\n")

    print(f"✅ 检查报告已保存到: {output_file}")

    # 如果没有问题，输出成功信息
    if not word_issues and not sentence_issues:
        print()
        print("=" * 80)
        print("🎉 检查完成！没有发现明显的拼写或翻译问题！")
        print("=" * 80)

if __name__ == '__main__':
    main()
