#!/usr/bin/env python3
"""
检查 SRS Word 数据库中的所有单词和句子的拼写和翻译
"""

import psycopg2
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'dbname': 'srs-db',
    'user': 'jolin',
    'password': 'lcj890712',
    'host': '127.0.0.1',
    'port': '5432',
}

def check_database_data():
    """连接数据库并检查所有数据"""

    try:
        # 连接数据库
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("=" * 80)
        print("SRS Word 数据检查报告")
        print("=" * 80)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()

        # 查询所有数据
        query = """
        SELECT
            id,
            item_type,
            content,
            phonetic_symbol,
            definition,
            translation,
            created_at
        FROM knowledge_items
        ORDER BY item_type, content
        """

        cursor.execute(query)
        items = cursor.fetchall()

        if not items:
            print("⚠️  数据库中没有任何数据！")
            return

        print(f"📊 总条目数: {len(items)}")
        print()

        # 统计
        word_count = 0
        sentence_count = 0

        # 检查数据
        print("=" * 80)
        print("📝 详细内容")
        print("=" * 80)
        print()

        for item in items:
            (item_id, item_type, content, phonetic_symbol, definition, translation, created_at) = item

            if item_type == 'word':
                word_count += 1
                print(f"【单词 {word_count}】")
                print(f"  ID: {item_id}")
                print(f"  单词: {content}")
                if phonetic_symbol:
                    print(f"  音标: {phonetic_symbol}")
                if definition:
                    print(f"  定义: {definition}")
                else:
                    print(f"  ⚠️  定义缺失！")
                print(f"  创建时间: {created_at}")
                print()

                # 基本拼写检查
                if not content.isalpha() and '-' not in content and "'" not in content:
                    print(f"  ⚠️  可能包含非字母字符: {content}")

            elif item_type == 'sentence':
                sentence_count += 1
                print(f"【句子 {sentence_count}】")
                print(f"  ID: {item_id}")
                print(f"  句子: {content}")
                if translation:
                    print(f"  翻译: {translation}")
                else:
                    print(f"  ⚠️  翻译缺失！")
                print(f"  创建时间: {created_at}")
                print()

                # 基本检查
                if not translation:
                    print(f"  ⚠️  翻译缺失！")

            print("-" * 80)
            print()

        # 输出统计
        print("=" * 80)
        print("📈 统计信息")
        print("=" * 80)
        print(f"单词总数: {word_count}")
        print(f"句子总数: {sentence_count}")
        print(f"总计: {len(items)}")
        print()

        # 输出到文件
        output_file = f"/home/lichangjiang/.openclaw/workspace/srs_data_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("SRS Word 数据检查报告\n")
            f.write("=" * 80 + "\n")
            f.write(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"总条目数: {len(items)}\n")
            f.write(f"单词总数: {word_count}\n")
            f.write(f"句子总数: {sentence_count}\n\n")

            for item in items:
                (item_id, item_type, content, phonetic_symbol, definition, translation, created_at) = item

                if item_type == 'word':
                    f.write(f"【单词】\n")
                    f.write(f"  ID: {item_id}\n")
                    f.write(f"  单词: {content}\n")
                    if phonetic_symbol:
                        f.write(f"  音标: {phonetic_symbol}\n")
                    if definition:
                        f.write(f"  定义: {definition}\n")
                    else:
                        f.write(f"  ⚠️ 定义缺失！\n")
                    f.write(f"  创建时间: {created_at}\n\n")
                elif item_type == 'sentence':
                    f.write(f"【句子】\n")
                    f.write(f"  ID: {item_id}\n")
                    f.write(f"  句子: {content}\n")
                    if translation:
                        f.write(f"  翻译: {translation}\n")
                    else:
                        f.write(f"  ⚠️ 翻译缺失！\n")
                    f.write(f"  创建时间: {created_at}\n\n")

        print(f"✅ 检查报告已保存到: {output_file}")

        # 关闭连接
        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"❌ 数据库错误: {e}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == '__main__':
    check_database_data()
