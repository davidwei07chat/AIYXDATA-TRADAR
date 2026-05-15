#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendRadar AI 分析验证脚本 - 强制生成新的分析文章
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目路径
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
    print("TrendRadar AI 分析验证 - 强制生成新的分析文章")
    print("=" * 80)
    print()

    # 读取配置
    config_path = Path(__file__).parent / "config" / "config.yaml"
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        return False

    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    ai_config = config.get("ai", {})
    analysis_config = config.get("ai_analysis", {})

    print(f"✓ 配置加载成功")
    print(f"  - 模型: {ai_config.get('model', 'unknown')}")
    print(f"  - 分析启用: {analysis_config.get('enabled', False)}")
    print()

    # 检查 API Key
    if not ai_config.get("api_key"):
        print("❌ 错误: 未配置 AI API Key")
        print("   请在 config.yaml 中设置 AI.API_KEY 或环境变量 AI_API_KEY")
        return False

    print("✓ API Key 已配置")
    print()

    # 创建分析器
    print("正在初始化 AI 分析器...")
    from datetime import datetime
    get_time = lambda: datetime.now()

    try:
        # 转换配置键名为大写（AIClient 期望大写）
        ai_config_upper = {k.upper(): v for k, v in ai_config.items()}
        analyzer = AIAnalyzer(ai_config_upper, analysis_config, get_time, debug=True)
        print("✓ AI 分析器初始化成功")
        print()
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False

    # 创建测试数据
    print("准备测试数据...")
    stats, rss_stats = create_test_data()
    print(f"✓ 测试数据准备完成")
    print(f"  - 热榜数据: {len(stats)} 个关键词")
    print(f"  - RSS 数据: {len(rss_stats)} 个关键词")
    print()

    # 执行分析
    print("=" * 80)
    print("执行 AI 分析...")
    print("=" * 80)
    print()

    try:
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
        print("分析结果")
        print("=" * 80)
        print()

        if result.success:
            print("✅ 分析成功！")
            print()
            print(f"核心热点与舆情态势:")
            print(result.core_trends[:500] if result.core_trends else "(空)")
            print()
            print(f"舆论风向与争议:")
            print(result.sentiment_controversy[:500] if result.sentiment_controversy else "(空)")
            print()
            print(f"异动与弱信号:")
            print(result.signals[:500] if result.signals else "(空)")
            print()
            print(f"RSS 深度洞察:")
            print(result.rss_insights[:500] if result.rss_insights else "(空)")
            print()
            print(f"研判与策略建议:")
            print(result.outlook_strategy[:500] if result.outlook_strategy else "(空)")
            print()

            # 保存完整结果
            output_file = Path(__file__).parent / "test_ai_analysis_result.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "success": result.success,
                    "core_trends": result.core_trends,
                    "sentiment_controversy": result.sentiment_controversy,
                    "signals": result.signals,
                    "rss_insights": result.rss_insights,
                    "outlook_strategy": result.outlook_strategy,
                    "standalone_summaries": result.standalone_summaries,
                    "metadata": {
                        "total_news": result.total_news,
                        "analyzed_news": result.analyzed_news,
                        "hotlist_count": result.hotlist_count,
                        "rss_count": result.rss_count,
                        "ai_mode": result.ai_mode
                    }
                }, f, ensure_ascii=False, indent=2)

            print(f"✓ 完整结果已保存到: {output_file}")
            return True
        else:
            print(f"❌ 分析失败: {result.error}")
            print()
            print(f"原始响应 (前500字):")
            print(result.raw_response[:500] if result.raw_response else "(空)")
            return False

    except Exception as e:
        print(f"❌ 执行分析时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
