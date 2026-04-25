#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 分析功能完整测试脚本
测试 AI 客户端和分析器的实际调用
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from aiyxdata_tradar.core import load_config
from aiyxdata_tradar.ai import AIAnalyzer

def test_ai_analysis():
    """测试 AI 分析功能"""

    print("=" * 80)
    print("AI 分析功能完整测试")
    print("=" * 80)

    # 加载配置
    print("\n[1] 加载配置...")
    try:
        config = load_config("config/config.yaml")
        ai_config = config.get("AI", {})
        ai_analysis_config = config.get("AI_ANALYSIS", {})
        print(f"✓ 配置加载成功")
        print(f"  - AI 模型: {ai_config.get('MODEL')}")
        print(f"  - AI 分析启用: {ai_analysis_config.get('ENABLED')}")
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return False

    # 创建 AI 分析器
    print("\n[2] 创建 AI 分析器...")
    try:
        analyzer = AIAnalyzer(
            ai_config=ai_config,
            analysis_config=ai_analysis_config,
            get_time_func=datetime.now,
            debug=True
        )
        print(f"✓ AI 分析器创建成功")
    except Exception as e:
        print(f"✗ AI 分析器创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 准备测试数据
    print("\n[3] 准备测试数据...")
    test_stats = [
        {
            "word": "AI技术",
            "titles": [
                {
                    "title": "OpenAI 发布新的 GPT 模型",
                    "source": "科技新闻",
                    "source_name": "TechNews",
                    "ranks": [1, 2, 1],
                    "count": 3,
                    "first_time": "09:00",
                    "last_time": "12:00"
                },
                {
                    "title": "谷歌 AI 研究新进展",
                    "source": "科技新闻",
                    "source_name": "TechNews",
                    "ranks": [3, 4, 5],
                    "count": 3,
                    "first_time": "10:00",
                    "last_time": "11:00"
                }
            ]
        },
        {
            "word": "科技动态",
            "titles": [
                {
                    "title": "苹果发布新产品",
                    "source": "科技新闻",
                    "source_name": "TechNews",
                    "ranks": [2, 3],
                    "count": 2,
                    "first_time": "08:00",
                    "last_time": "13:00"
                }
            ]
        }
    ]

    print(f"✓ 测试数据准备完成")
    print(f"  - 关键词数: {len(test_stats)}")
    print(f"  - 新闻总数: {sum(len(s['titles']) for s in test_stats)}")

    # 执行 AI 分析
    print("\n[4] 执行 AI 分析...")
    try:
        result = analyzer.analyze(
            stats=test_stats,
            rss_stats=None,
            report_mode="daily",
            report_type="当日汇总",
            platforms=["TechNews"],
            keywords=["AI技术", "科技动态"]
        )

        print(f"\n✓ AI 分析完成")
        print(f"  - 成功: {result.success}")
        print(f"  - 分析新闻数: {result.analyzed_news}")
        print(f"  - 总新闻数: {result.total_news}")

        if result.error:
            print(f"  - 错误: {result.error}")

        if result.core_trends:
            print(f"\n核心热点分析（前 300 字）:")
            print(f"  {result.core_trends[:300]}...")

        return result.success

    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"✗ AI 分析失败 ({error_type}): {error_msg}")

        # 详细错误分析
        if "401" in error_msg or "Unauthorized" in error_msg or "Invalid token" in error_msg:
            print("\n⚠️  认证错误诊断:")
            print("  1. API Key 无效或已过期")
            print("  2. API Key 格式不正确")
            print("  3. API Base 与 API Key 不匹配")
            print("  4. 模型名称与 API 提供商不匹配")
        elif "404" in error_msg or "Not found" in error_msg:
            print("\n⚠️  模型不存在诊断:")
            print("  1. 模型名称错误")
            print("  2. API Base 不支持该模型")
            print("  3. SiliconFlow 不支持该模型")
        elif "timeout" in error_msg.lower():
            print("\n⚠️  请求超时诊断:")
            print("  1. 网络连接问题")
            print("  2. API 服务响应缓慢")
            print("  3. 请求超时时间设置过短")

        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n")
    success = test_ai_analysis()
    print("\n" + "=" * 80)
    if success:
        print("✓ AI 分析测试完成 - 功能正常")
        sys.exit(0)
    else:
        print("✗ AI 分析测试失败 - 请检查配置和错误信息")
        sys.exit(1)
