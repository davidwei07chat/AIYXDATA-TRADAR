# (C) 2026 AIYXDATA. All rights reserved.
# Project: AIYXDATA-TRADAR

# coding=utf-8
"""
AI 客户端模块

基于 LiteLLM 的统一 AI 模型接口
支持 100+ AI 提供商（OpenAI、DeepSeek、Gemini、Claude、国内模型等）
"""

import os
from typing import Any, Dict, List, Optional

from litellm import completion


class AIClient:
    """统一的 AI 客户端（基于 LiteLLM）"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 AI 客户端

        Args:
            config: AI 配置字典
                - MODEL: 模型标识（格式: provider/model_name）
                - API_KEY: API 密钥
                - API_BASE: API 基础 URL（可选）
                - TEMPERATURE: 采样温度
                - MAX_TOKENS: 最大生成 token 数
                - TIMEOUT: 请求超时时间（秒）
                - NUM_RETRIES: 重试次数（可选）
                - FALLBACK_MODELS: 备用模型列表（可选）
        """
        raw_model = config.get("MODEL", "deepseek/deepseek-chat")
        self.model = self._auto_prefix_model(raw_model)
        self.api_key = config.get("API_KEY") or os.environ.get("AI_API_KEY", "")
        self.api_base = config.get("API_BASE", "")
        self.custom_llm_provider = config.get("CUSTOM_LLM_PROVIDER", "")
        self.temperature = config.get("TEMPERATURE", 1.0)
        self.max_tokens = config.get("MAX_TOKENS", 5000)
        self.timeout = config.get("TIMEOUT", 120)
        self.num_retries = config.get("NUM_RETRIES", 2)
        self.fallback_models = config.get("FALLBACK_MODELS", [])

    def _auto_prefix_model(self, model: str) -> str:
        """
        自动为非原生支持的模型添加 openai/ 前缀

        Args:
            model: 用户填写的模型名称

        Returns:
            str: 处理后的模型名称
        """
        if not model or "/" not in model:
            return model

        try:
            from litellm import provider_list
            # 提取提供商前缀（如 'deepseek', 'anthropic', 'openai'）
            provider = model.split("/")[0].lower()

            # 检查是否在原生支持列表中
            is_supported = False
            for p in provider_list:
                # p 是 LlmProviders 枚举，其 value 是字符串形式的 provider
                val = getattr(p, "value", str(p)).lower()
                # Use exact match or check if provider is part of the value but only at word boundaries
                if val == provider or provider == val.split("_")[0] or provider == val.split("-")[0]:
                    is_supported = True
                    break

            # 兼容 OpenAI 的提供商列表
            openai_compatible_providers = ["openai", "custom_openai", "openai_like", "hosted_vllm", "lm_studio", "ollama", "ollama_chat"]
            if provider in openai_compatible_providers:
                is_supported = True

            # 如果不在原生支持列表中，则默认使用 openai/ 协议
            if not is_supported and not model.startswith("openai/"):
                print(f"[AI] 自动为非原生模型 {model} 添加 openai/ 前缀")
                return f"openai/{model}"

        except ImportError:
            pass

        return model

    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        调用 AI 模型进行对话

        Args:
            messages: 消息列表，格式: [{"role": "system/user/assistant", "content": "..."}]
            **kwargs: 额外参数，会覆盖默认配置

        Returns:
            str: AI 响应内容

        Raises:
            Exception: API 调用失败时抛出异常
        """
        # 构建请求参数
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "timeout": kwargs.get("timeout", self.timeout),
            "num_retries": kwargs.get("num_retries", self.num_retries),
        }

        # 添加自定义提供商（如果配置了）
        custom_llm_provider = kwargs.get("custom_llm_provider", self.custom_llm_provider)
        if custom_llm_provider:
            params["custom_llm_provider"] = custom_llm_provider

        # 添加 API Key
        if self.api_key:
            params["api_key"] = self.api_key

        # 添加 API Base（如果配置了）
        if self.api_base:
            params["api_base"] = self.api_base

        # 添加 max_tokens（如果配置了且不为 0）
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        if max_tokens and max_tokens > 0:
            params["max_tokens"] = max_tokens

        # 添加 fallback 模型（如果配置了）
        if self.fallback_models:
            params["fallbacks"] = self.fallback_models

        # 合并其他额外参数
        for key, value in kwargs.items():
            if key not in params:
                params[key] = value

        # 调用 LiteLLM
        response = completion(**params)

        # 提取响应内容
        return response.choices[0].message.content

    def validate_config(self) -> tuple[bool, str]:
        """
        验证配置是否有效

        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not self.model:
            return False, "未配置 AI 模型（model）"

        if not self.api_key:
            return False, "未配置 AI API Key，请在 config.yaml 或环境变量 AI_API_KEY 中设置"

        # 验证模型格式（应该包含 provider/model）
        if "/" not in self.model:
            return False, f"模型格式错误: {self.model}，应为 'provider/model' 格式（如 'deepseek/deepseek-chat'）"

        return True, ""
