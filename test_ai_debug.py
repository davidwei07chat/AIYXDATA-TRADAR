#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendRadar AI 分析调试脚本 - 检查完整响应
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from aiyxdata_tradar.ai import AIAnalyzer

def create_test_data():
    """创建测试数据"""
    stats = [
        {
            "word": "AI大模型突破",
            "titles": [
                {
                    "title": "OpenAI 发布 GPT-5 重大更新",
                    "source_name": "微博",
                    "ranks": [1, 2, 1],
                    "first_time": "09:30",
                    "last_time": "12:45",
                    "count": 3,
                    "rank_timeline": [
                        {"time": "09:30", "rank": 1},
                        {"time": "10:30", "rank": 2},
                        {"time": "11:30", "rank": 1}
                    ]
                },
                {
                    "title": "国内大模型厂商加速追赶",
                    "source_name": "知乎",
                    "ranks": [5, 4, 3],
                    "first_time": "10:00",
                    "last_time": "13:00",
                    "count": 2,
                    "rank_timeline": [
                        {"time": "10:00", "rank": 5},
                        {"time": "11:30", "rank": 4},
                        {"time": "13:00", "rank": 3}
                    ]
                }
            ]
        },
        {
            "word": "科技政策调整",
            "titles": [
                {
                    "title": "新规出台：AI 企业需加强数据安全",
                    "source_name": "36氪",
                    "ranks": [8, 6, 4],
                    "first_time": "11:00",
                    "last_time": "14:00",
                    "count": 2,
                    "rank_timeline": [
                        {"time": "11:00", "rank": 8},
                        {"time": "12:30", "rank": 6},
                        {"time": "14:00", "rank": 4}
                    ]
                }
            ]
        }
    ]

    rss_stats = [
        {
            "word": "AI 行业深度分析",
            "titles": [
                {
                    "title": "2026年AI投资趋势报告：从通用到垂直",
                    "feed_name": "TechCrunch",
                    "time_display": "2026-05-12 08:00"
                },
                {
                    "title": "大模型成本下降 50%，创业公司迎来机遇",
                    "feed_name": "VentureBeat",
                    "time_display": "2026-05-12 09:30"
                }
            ]
        }
    ]

    return stats, rss_stats

def main():
    print("=" * 80)
    print("TrendRadar AI 分析调试 - 检查完整响应")
    print("=" * 80)
    print()

    # 读取配置
    config_path = Path(__file__).parent / "config" / "config.yaml"
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    ai_config = config.get("ai", {})
    analysis_config = config.get("ai_analysis", {})

    # 转换配置键名为大写
    ai_config_upper = {k.upper(): v for k, v in ai_config.items()}

    get_time = lambda: datetime.now()
    analyzer = AIAnalyzer(ai_config_upper, analysis_config, get_time, debug=False)

    # 创建测试数据
    stats, rss_stats = create_test_data()

    print("执行 AI 分析...")
    result = analyzer.analyze(
        stats=stats,
        rss_stats=rss_stats,
        report_mode="daily",
        report_type="当日汇总",
        platforms=["微博", "知乎", "36氪"],
        keywords=["AI大模型", "科技政策"]
    )

    print()
    print("=" * 80)
    print("原始响应（前 2000 字）")
    print("=" * 80)
    print(result.raw_response[:2000])
    print()
    print("=" * 80)
    print("解析结果")
    print("=" * 80)
    print(f"success: {result.success}")
    print(f"error: {result.error}")
    print()
    print("=" * 80)
    print("各字段内容长度")
    print("=" * 80)
    print(f"core_trends: {len(result.core_trends)} 字")
    print(f"sentiment_controversy: {len(result.sentiment_controversy)} 字")
    print(f"signals: {len(result.signals)} 字")
    print(f"rss_insights: {len(result.rss_insights)} 字")
    print(f"outlook_strategy: {len(result.outlook_strategy)} 字")
    print()

    if result.core_trends:
        print("=" * 80)
        print("core_trends 内容（前 500 字）")
        print("=" * 80)
        print(result.core_trends[:500])
        print()

    if result.sentiment_controversy:
        print("=" * 80)
        print("sentiment_controversy 内容（前 500 字）")
        print("=" * 80)
        print(result.sentiment_controversy[:500])
        print()

    if result.signals:
        print("=" * 80)
        print("signals 内容（前 500 字）")
        print("=" * 80)
        print(result.signals[:500])
        print()

    if result.rss_insights:
        print("=" * 80)
        print("rss_insights 内容（前 500 字）")
        print("=" * 80)
        print(result.rss_insights[:500])
        print()

    if result.outlook_strategy:
        print("=" * 80)
        print("outlook_strategy 内容（前 500 字）")
        print("=" * 80)
        print(result.outlook_strategy[:500])
        print()

if __name__ == "__main__":
    main()
