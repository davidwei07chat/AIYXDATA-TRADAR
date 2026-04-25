#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 配置验证脚本
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from aiyxdata_tradar.core import load_config

def test_ai_config():
    """测试 AI 配置加载"""
    try:
        config = load_config("config/config.yaml")

        print("=" * 60)
        print("AI 配置验证结果")
        print("=" * 60)

        ai_config = config.get("AI", {})

        print(f"\n✓ 模型: {ai_config.get('MODEL')}")
        print(f"✓ API Base: {ai_config.get('API_BASE')}")
        print(f"✓ Temperature: {ai_config.get('TEMPERATURE')}")
        print(f"✓ Max Tokens: {ai_config.get('MAX_TOKENS')}")
        print(f"✓ Timeout: {ai_config.get('TIMEOUT')}")
        print(f"✓ Num Retries: {ai_config.get('NUM_RETRIES')}")

        # 验证模型格式
        model = ai_config.get('MODEL', '')
        if model:
            parts = model.split('/')
            print(f"\n模型格式检查:")
            print(f"  - 完整格式: {model}")
            print(f"  - 斜杠数量: {len(parts) - 1}")
            print(f"  - 部分: {parts}")

            if len(parts) == 2:
                print(f"  ✓ 格式正确 (provider/model)")
            else:
                print(f"  ✗ 格式错误 (应为 provider/model，但有 {len(parts) - 1} 个斜杠)")

        # 验证 temperature
        temp = ai_config.get('TEMPERATURE', 0)
        if 0 <= temp <= 2:
            print(f"\n✓ Temperature 在有效范围内: {temp}")
        else:
            print(f"\n✗ Temperature 超出范围: {temp} (应在 0-2 之间)")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_config()
