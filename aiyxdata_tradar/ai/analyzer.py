# (C) 2026 AIYXDATA. All rights reserved.
# Project: AIYXDATA-TRADAR

# coding=utf-8
"""
AI 分析器模块

调用 AI 大模型对热点新闻进行深度分析
基于 LiteLLM 统一接口，支持 100+ AI 提供商
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from aiyxdata_tradar.ai.client import AIClient


@dataclass
class AIAnalysisResult:
    """AI 分析结果"""
    # 新版 5 核心板块
    core_trends: str = ""                # 核心热点与舆情态势
    sentiment_controversy: str = ""      # 舆论风向与争议
    signals: str = ""                    # 异动与弱信号
    rss_insights: str = ""               # RSS 深度洞察
    outlook_strategy: str = ""           # 研判与策略建议
    standalone_summaries: Dict[str, str] = field(default_factory=dict)  # 独立展示区概括 {源ID: 概括}

    # 基础元数据
    raw_response: str = ""               # 原始响应
    success: bool = False                # 是否成功
    error: str = ""                      # 错误信息

    # 新闻数量统计
    total_news: int = 0                  # 总新闻数（热榜+RSS）
    analyzed_news: int = 0               # 实际分析的新闻数
    max_news_limit: int = 0              # 分析上限配置值
    hotlist_count: int = 0               # 热榜新闻数
    rss_count: int = 0                   # RSS 新闻数
    ai_mode: str = ""                    # AI 分析使用的模式 (daily/current/incremental)
    metadata: Dict[str, Any] = field(default_factory=dict)  # 分析元数据 (模型名称、时长等)


class AIAnalyzer:
    """AI 分析器"""

    def __init__(
        self,
        ai_config: Dict[str, Any],
        analysis_config: Dict[str, Any],
        get_time_func: Callable,
        debug: bool = False,
    ):
        """
        初始化 AI 分析器

        Args:
            ai_config: AI 模型配置（LiteLLM 格式）
            analysis_config: AI 分析功能配置（language, prompt_file 等）
            get_time_func: 获取当前时间的函数
            debug: 是否开启调试模式
        """
        self.ai_config = ai_config
        self.analysis_config = analysis_config
        self.get_time_func = get_time_func
        self.debug = debug

        # 创建 AI 客户端（基于 LiteLLM）
        self.client = AIClient(ai_config)

        # 验证配置
        valid, error = self.client.validate_config()
        if not valid:
            print(f"[AI] 配置警告: {error}")

        # 从分析配置获取功能参数
        self.max_news = analysis_config.get("MAX_NEWS_FOR_ANALYSIS", 50)
        self.include_rss = analysis_config.get("INCLUDE_RSS", True)
        self.include_rank_timeline = analysis_config.get("INCLUDE_RANK_TIMELINE", False)
        self.include_standalone = analysis_config.get("INCLUDE_STANDALONE", False)
        self.language = analysis_config.get("LANGUAGE", "Chinese")

        # 加载提示词模板
        self.prompt_template_error = ""
        self.prompt_file = analysis_config.get("PROMPT_FILE", "ai_analysis_prompt.txt")
        self.system_prompt, self.user_prompt_template = self._load_prompt_template(
            self.prompt_file
        )

    def _load_prompt_template(self, prompt_file: str) -> tuple:
        """加载提示词模板"""
        config_dir = Path(__file__).parent.parent.parent / "config"
        prompt_path = config_dir / prompt_file

        if not prompt_path.exists():
            self.prompt_template_error = f"提示词文件不存在: {prompt_path}"
            print(f"[AI] {self.prompt_template_error}")
            return "", ""

        content = prompt_path.read_text(encoding="utf-8")

        # 解析 [system] 和 [user] 部分
        system_prompt = ""
        user_prompt = ""

        if "[user]" in content:
            system_part, user_part = content.split("[user]", 1)
            if "[system]" in system_part:
                system_prompt = system_part.split("[system]", 1)[1].strip()
            user_prompt = user_part.strip()
        else:
            if "[system]" in content:
                system_prompt = content.split("[system]", 1)[1].strip()
                self.prompt_template_error = (
                    f"提示词文件 {prompt_file} 缺少 [user] 段，"
                    "已停止 AI 分析，避免把整份提示词配置当作待分析内容发送给模型"
                )
                print(f"[AI] {self.prompt_template_error}")
            else:
                # 兼容纯 user prompt 模板，但仍会在下方检查数据占位符。
                user_prompt = content.strip()

        if not self.prompt_template_error and not user_prompt.strip():
            self.prompt_template_error = f"提示词文件 {prompt_file} 的 [user] 段为空"
            print(f"[AI] {self.prompt_template_error}")

        data_placeholders = ("{news_content}", "{rss_content}", "{standalone_content}")
        if (
            not self.prompt_template_error
            and not any(placeholder in user_prompt for placeholder in data_placeholders)
        ):
            self.prompt_template_error = (
                f"提示词文件 {prompt_file} 缺少新闻数据占位符 "
                "{news_content}/{rss_content}/{standalone_content}"
            )
            print(f"[AI] {self.prompt_template_error}")

        return system_prompt, user_prompt

    def analyze(
        self,
        stats: List[Dict],
        rss_stats: Optional[List[Dict]] = None,
        report_mode: str = "daily",
        report_type: str = "当日汇总",
        platforms: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        standalone_data: Optional[Dict] = None,
    ) -> AIAnalysisResult:
        """
        执行 AI 分析

        Args:
            stats: 热榜统计数据
            rss_stats: RSS 统计数据
            report_mode: 报告模式
            report_type: 报告类型
            platforms: 平台列表
            keywords: 关键词列表

        Returns:
            AIAnalysisResult: 分析结果
        """
        
        # 打印配置信息方便调试
        model = self.ai_config.get("MODEL", "unknown")
        api_key = self.client.api_key or ""
        api_base = self.ai_config.get("API_BASE", "")
        masked_key = f"{api_key[:5]}******" if len(api_key) >= 5 else "******"
        model_display = model.replace("/", "/\u200b") if model else "unknown"

        print(f"[AI] 模型: {model_display}")
        print(f"[AI] Key : {masked_key}")

        if api_base:
            print(f"[AI] 接口: 存在自定义 API 端点")

        custom_provider = self.ai_config.get("CUSTOM_LLM_PROVIDER", "")
        if custom_provider:
            print(f"[AI] 提供商: {custom_provider}")

        timeout = self.ai_config.get("TIMEOUT", 120)
        max_tokens = self.ai_config.get("MAX_TOKENS", 5000)
        print(f"[AI] 参数: timeout={timeout}, max_tokens={max_tokens}")

        if not self.client.api_key:
            print("[AI] 错误: 未配置 API Key")
            return AIAnalysisResult(
                success=False,
                error="未配置 AI API Key，请在 config.yaml 或环境变量 AI_API_KEY 中设置"
            )

        if self.prompt_template_error:
            return AIAnalysisResult(success=False, error=self.prompt_template_error)

        # 准备新闻内容并获取统计数据
        news_content, rss_content, hotlist_total, rss_total, analyzed_count = self._prepare_news_content(stats, rss_stats)
        total_news = hotlist_total + rss_total

        if not news_content and not rss_content:
            return AIAnalysisResult(
                success=False,
                error="没有可分析的新闻内容",
                total_news=total_news,
                hotlist_count=hotlist_total,
                rss_count=rss_total,
                analyzed_news=0,
                max_news_limit=self.max_news
            )

        # 构建提示词
        current_time = self.get_time_func().strftime("%Y-%m-%d %H:%M:%S")

        # 提取关键词
        if not keywords:
            keywords = [s.get("word", "") for s in stats if s.get("word")] if stats else []

        # 使用安全的字符串替换，避免模板中其他花括号（如 JSON 示例）被误解析
        user_prompt = self.user_prompt_template
        user_prompt = user_prompt.replace("{report_mode}", report_mode)
        user_prompt = user_prompt.replace("{report_type}", report_type)
        user_prompt = user_prompt.replace("{current_time}", current_time)
        user_prompt = user_prompt.replace("{news_count}", str(hotlist_total))
        user_prompt = user_prompt.replace("{rss_count}", str(rss_total))
        user_prompt = user_prompt.replace("{platforms}", ", ".join(platforms) if platforms else "多平台")
        user_prompt = user_prompt.replace("{keywords}", ", ".join(keywords[:20]) if keywords else "无")
        user_prompt = user_prompt.replace("{news_content}", news_content)
        user_prompt = user_prompt.replace("{rss_content}", rss_content)
        user_prompt = user_prompt.replace("{language}", self.language)

        # 构建独立展示区内容
        standalone_content = ""
        if self.include_standalone and standalone_data:
            standalone_content = self._prepare_standalone_content(standalone_data)
        user_prompt = user_prompt.replace("{standalone_content}", standalone_content)

        if self.debug:
            print("\n" + "=" * 80)
            print("[AI 调试] 发送给 AI 的完整提示词")
            print("=" * 80)
            if self.system_prompt:
                print("\n--- System Prompt ---")
                print(self.system_prompt)
            print("\n--- User Prompt ---")
            print(user_prompt)
            print("=" * 80 + "\n")

        # 调用 AI API（使用 LiteLLM）
        try:
            print(f"[AI] 正在发送请求到 {model_display}...")
            response = self._call_ai(user_prompt)
            print(f"[AI] 收到响应，长度: {len(response)} 字符")
            result = self._parse_response(response)

            # 如果配置未启用 RSS 分析，强制清空 AI 返回的 RSS 洞察
            if not self.include_rss:
                result.rss_insights = ""

            # 如果配置未启用 standalone 分析，强制清空
            if not self.include_standalone:
                result.standalone_summaries = {}

            # 填充统计数据
            result.total_news = total_news
            result.hotlist_count = hotlist_total
            result.rss_count = rss_total
            result.analyzed_news = analyzed_count
            result.max_news_limit = self.max_news
            result.metadata = {"model": model}
            return result
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)

            # 截断过长的错误消息
            if len(error_msg) > 200:
                error_msg = error_msg[:200] + "..."
            friendly_msg = f"AI 分析失败 ({error_type}): {error_msg}"

            return AIAnalysisResult(
                success=False,
                error=friendly_msg
            )

    def _prepare_news_content(
        self,
        stats: List[Dict],
        rss_stats: Optional[List[Dict]] = None,
    ) -> tuple:
        """
        准备新闻内容文本（增强版）

        热榜新闻包含：来源、标题、排名范围、时间范围、出现次数
        RSS 包含：来源、标题、发布时间

        Returns:
            tuple: (news_content, rss_content, hotlist_total, rss_total, analyzed_count)
        """
        news_lines = []
        rss_lines = []
        news_count = 0
        rss_count = 0

        # 计算总新闻数
        hotlist_total = sum(len(s.get("titles", [])) for s in stats) if stats else 0
        rss_total = sum(len(s.get("titles", [])) for s in rss_stats) if rss_stats else 0

        # 热榜内容
        if stats:
            for stat in stats:
                word = stat.get("word", "")
                titles = stat.get("titles", [])
                if word and titles:
                    news_lines.append(f"\n**{word}** ({len(titles)}条)")
                    for t in titles:
                        if not isinstance(t, dict):
                            continue
                        title = t.get("title", "")
                        if not title:
                            continue

                        # 来源
                        source = t.get("source_name", t.get("source", ""))

                        # 构建行
                        if source:
                            line = f"- [{source}] {title}"
                        else:
                            line = f"- {title}"

                        # 始终显示简化格式：排名范围 + 时间范围 + 出现次数
                        ranks = t.get("ranks", [])
                        if ranks:
                            min_rank = min(ranks)
                            max_rank = max(ranks)
                            rank_str = f"{min_rank}" if min_rank == max_rank else f"{min_rank}-{max_rank}"
                        else:
                            rank_str = "-"

                        first_time = t.get("first_time", "")
                        last_time = t.get("last_time", "")
                        time_str = self._format_time_range(first_time, last_time)

                        appear_count = t.get("count", 1)

                        line += f" | 排名:{rank_str} | 时间:{time_str} | 出现:{appear_count}次"

                        # 开启完整时间线时，额外添加轨迹
                        if self.include_rank_timeline:
                            rank_timeline = t.get("rank_timeline", [])
                            timeline_str = self._format_rank_timeline(rank_timeline)
                            line += f" | 轨迹:{timeline_str}"

                        news_lines.append(line)

                        news_count += 1
                        if news_count >= self.max_news:
                            break
                if news_count >= self.max_news:
                    break

        # RSS 内容（仅在启用时构建）
        if self.include_rss and rss_stats:
            remaining = self.max_news - news_count
            for stat in rss_stats:
                if rss_count >= remaining:
                    break
                word = stat.get("word", "")
                titles = stat.get("titles", [])
                if word and titles:
                    rss_lines.append(f"\n**{word}** ({len(titles)}条)")
                    for t in titles:
                        if not isinstance(t, dict):
                            continue
                        title = t.get("title", "")
                        if not title:
                            continue

                        # 来源
                        source = t.get("source_name", t.get("feed_name", ""))

                        # 发布时间
                        time_display = t.get("time_display", "")

                        # 构建行：[来源] 标题 | 发布时间
                        if source:
                            line = f"- [{source}] {title}"
                        else:
                            line = f"- {title}"
                        if time_display:
                            line += f" | {time_display}"
                        rss_lines.append(line)

                        rss_count += 1
                        if rss_count >= remaining:
                            break

        news_content = "\n".join(news_lines) if news_lines else ""
        rss_content = "\n".join(rss_lines) if rss_lines else ""
        total_count = news_count + rss_count

        return news_content, rss_content, hotlist_total, rss_total, total_count

    def _call_ai(self, user_prompt: str) -> str:
        """调用 AI API（使用 LiteLLM）"""
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        # 传递 max_tokens 参数以确保完整响应
        max_tokens = self.ai_config.get("MAX_TOKENS", 5000)
        return self.client.chat(messages, max_tokens=max_tokens)

    def _format_time_range(self, first_time: str, last_time: str) -> str:
        """格式化时间范围（简化显示，只保留时分）"""
        def extract_time(time_str: str) -> str:
            if not time_str:
                return "-"
            # 尝试提取 HH:MM 部分
            if " " in time_str:
                parts = time_str.split(" ")
                if len(parts) >= 2:
                    time_part = parts[1]
                    if ":" in time_part:
                        return time_part[:5]  # HH:MM
            elif ":" in time_str:
                return time_str[:5]
            # 处理 HH-MM 格式
            result = time_str[:5] if len(time_str) >= 5 else time_str
            if len(result) == 5 and result[2] == '-':
                result = result.replace('-', ':')
            return result

        first = extract_time(first_time)
        last = extract_time(last_time)

        if first == last or last == "-":
            return first
        return f"{first}~{last}"

    def _format_rank_timeline(self, rank_timeline: List[Dict]) -> str:
        """格式化排名时间线"""
        if not rank_timeline:
            return "-"

        parts = []
        for item in rank_timeline:
            time_str = item.get("time", "")
            if len(time_str) == 5 and time_str[2] == '-':
                time_str = time_str.replace('-', ':')
            rank = item.get("rank")
            if rank is None:
                parts.append(f"0({time_str})")
            else:
                parts.append(f"{rank}({time_str})")

        return "→".join(parts)

    def _prepare_standalone_content(self, standalone_data: Dict) -> str:
        """
        将独立展示区数据转为文本，注入 AI 分析 prompt

        Args:
            standalone_data: 独立展示区数据 {"platforms": [...], "rss_feeds": [...]}

        Returns:
            格式化的文本内容
        """
        lines = []

        # 热榜平台
        for platform in standalone_data.get("platforms", []):
            platform_id = platform.get("id", "")
            platform_name = platform.get("name", platform_id)
            items = platform.get("items", [])
            if not items:
                continue

            lines.append(f"### [{platform_name}]")
            for item in items:
                title = item.get("title", "")
                if not title:
                    continue

                line = f"- {title}"

                # 排名信息
                ranks = item.get("ranks", [])
                if ranks:
                    min_rank = min(ranks)
                    max_rank = max(ranks)
                    rank_str = f"{min_rank}" if min_rank == max_rank else f"{min_rank}-{max_rank}"
                    line += f" | 排名:{rank_str}"

                # 时间范围
                first_time = item.get("first_time", "")
                last_time = item.get("last_time", "")
                if first_time:
                    time_str = self._format_time_range(first_time, last_time)
                    line += f" | 时间:{time_str}"

                # 出现次数
                count = item.get("count", 1)
                if count > 1:
                    line += f" | 出现:{count}次"

                # 排名轨迹（如果启用）
                if self.include_rank_timeline:
                    rank_timeline = item.get("rank_timeline", [])
                    if rank_timeline:
                        timeline_str = self._format_rank_timeline(rank_timeline)
                        line += f" | 轨迹:{timeline_str}"

                lines.append(line)
            lines.append("")

        # RSS 源
        for feed in standalone_data.get("rss_feeds", []):
            feed_id = feed.get("id", "")
            feed_name = feed.get("name", feed_id)
            items = feed.get("items", [])
            if not items:
                continue

            lines.append(f"### [{feed_name}]")
            for item in items:
                title = item.get("title", "")
                if not title:
                    continue

                line = f"- {title}"
                published_at = item.get("published_at", "")
                if published_at:
                    line += f" | {published_at}"

                lines.append(line)
            lines.append("")

        return "\n".join(lines)

    def _parse_response(self, response: str) -> AIAnalysisResult:
        """解析 AI 响应"""
        import re

        result = AIAnalysisResult(raw_response=response)

        if not response or not response.strip():
            result.error = "AI 返回空响应"
            return result

        json_str = None
        try:
            # 第一步：提取 JSON 代码块
            if "```json" in response:
                parts = response.split("```json", 1)
                if len(parts) > 1:
                    code_block = parts[1]
                    end_idx = code_block.find("```")
                    if end_idx != -1:
                        json_str = code_block[:end_idx].strip()
                    else:
                        json_str = code_block.strip()
            elif "```" in response:
                parts = response.split("```", 2)
                if len(parts) >= 2:
                    json_str = parts[1].strip()

            # 如果没有找到代码块，尝试直接解析
            if not json_str:
                json_str = response.strip()

            if not json_str:
                raise ValueError("提取的 JSON 内容为空")

            # 第二步：尝试解析 JSON
            # 注意：中文引号在 JSON 字符串内容里是合法字符，不能全局替换成英文引号。
            # 否则模型输出的正文引用会被误变成未转义的 JSON 定界符，导致字段被截断。
            data = json.loads(json_str)

            def as_text(value: Any) -> str:
                if value is None:
                    return ""
                if isinstance(value, str):
                    return value
                if isinstance(value, (dict, list)):
                    return json.dumps(value, ensure_ascii=False)
                return str(value)

            # 新版字段解析
            result.core_trends = as_text(data.get("core_trends", ""))
            result.sentiment_controversy = as_text(data.get("sentiment_controversy", ""))
            result.signals = as_text(data.get("signals", ""))
            result.rss_insights = as_text(data.get("rss_insights", ""))
            result.outlook_strategy = as_text(data.get("outlook_strategy", ""))

            # 解析独立展示区概括
            summaries = data.get("standalone_summaries", {})
            if isinstance(summaries, dict):
                result.standalone_summaries = {
                    str(k): str(v) for k, v in summaries.items()
                }

            has_content = any(
                getattr(result, field_name, "").strip()
                for field_name in (
                    "core_trends",
                    "sentiment_controversy",
                    "signals",
                    "rss_insights",
                    "outlook_strategy",
                )
            ) or any(str(v).strip() for v in result.standalone_summaries.values())
            combined_content = "\n".join(
                value for value in (
                    result.core_trends,
                    result.sentiment_controversy,
                    result.signals,
                    result.rss_insights,
                    result.outlook_strategy,
                    "\n".join(str(v) for v in result.standalone_summaries.values()),
                ) if value
            )
            prompt_markers = (
                "提示词配置文件",
                "用于指导AI分析",
                "用于指导 AI 分析",
                "我已理解你的需求",
            )
            if any(marker in combined_content for marker in prompt_markers):
                result.error = "AI 响应疑似提示词说明文本，已拒绝作为分析报告展示"
                return result

            if not has_content:
                result.error = "AI 响应 JSON 中没有可展示的分析内容"
                return result

            result.success = True
            return result

        except json.JSONDecodeError as e:
            # JSON 解析失败，尝试使用正则表达式提取字段
            if json_str:
                try:
                    # 使用相邻字段边界提取每个字段的值。
                    # 这比“遇到第一个英文引号就停止”更稳，可以容忍正文里出现未转义引号。
                    extracted = {}
                    field_order = [
                        "core_trends",
                        "sentiment_controversy",
                        "signals",
                        "rss_insights",
                        "outlook_strategy",
                        "standalone_summaries",
                    ]

                    def decode_jsonish_string(value: str) -> str:
                        value = value.strip()
                        try:
                            return json.loads(f'"{value}"')
                        except Exception:
                            return (
                                value
                                .replace("\\n", "\n")
                                .replace("\\t", "\t")
                                .replace('\\"', '"')
                                .replace("\\/", "/")
                            )

                    def extract_string_field(source: str, field: str, following_fields: List[str]) -> str:
                        key_pattern = rf'["“]{re.escape(field)}["”]\s*:\s*["“]'
                        key_match = re.search(key_pattern, source, re.DOTALL)
                        if not key_match:
                            return ""

                        start = key_match.end()
                        end_candidates = []
                        for following_field in following_fields:
                            boundary_pattern = (
                                rf'["”]\s*,\s*["“]{re.escape(following_field)}["”]\s*:'
                            )
                            boundary_match = re.search(boundary_pattern, source[start:], re.DOTALL)
                            if boundary_match:
                                end_candidates.append(start + boundary_match.start())

                        if not end_candidates:
                            tail_match = re.search(r'["”]\s*}\s*$', source[start:], re.DOTALL)
                            if tail_match:
                                end_candidates.append(start + tail_match.start())

                        if not end_candidates:
                            return ""

                        return decode_jsonish_string(source[start:min(end_candidates)])

                    for index, field_name in enumerate(field_order[:-1]):
                        value = extract_string_field(
                            json_str,
                            field_name,
                            field_order[index + 1:],
                        )
                        if value:
                            extracted[field_name] = value

                    # 如果至少提取了一个非空字段，使用提取的数据
                    if any(value.strip() for value in extracted.values()):
                        result.core_trends = extracted.get('core_trends', '')
                        result.sentiment_controversy = extracted.get('sentiment_controversy', '')
                        result.signals = extracted.get('signals', '')
                        result.rss_insights = extracted.get('rss_insights', '')
                        result.outlook_strategy = extracted.get('outlook_strategy', '')

                        # 尝试提取 standalone_summaries
                        try:
                            match = re.search(r'"standalone_summaries"\s*:\s*({.*?})\s*}', json_str, re.DOTALL)
                            if match:
                                summaries_str = match.group(1)
                                summaries = json.loads(summaries_str)
                                if isinstance(summaries, dict):
                                    result.standalone_summaries = {str(k): str(v) for k, v in summaries.items()}
                        except Exception:
                            pass

                        if any(
                            getattr(result, field_name, "").strip()
                            for field_name in (
                                "core_trends",
                                "sentiment_controversy",
                                "signals",
                                "rss_insights",
                                "outlook_strategy",
                            )
                        ) or any(str(v).strip() for v in result.standalone_summaries.values()):
                            combined_content = "\n".join(
                                value for value in (
                                    result.core_trends,
                                    result.sentiment_controversy,
                                    result.signals,
                                    result.rss_insights,
                                    result.outlook_strategy,
                                    "\n".join(str(v) for v in result.standalone_summaries.values()),
                                ) if value
                            )
                            prompt_markers = (
                                "提示词配置文件",
                                "用于指导AI分析",
                                "用于指导 AI 分析",
                                "我已理解你的需求",
                            )
                            if any(marker in combined_content for marker in prompt_markers):
                                result.error = "AI 响应疑似提示词说明文本，已拒绝作为分析报告展示"
                                return result

                            result.success = True
                            return result

                except Exception as regex_error:
                    pass

            # 如果正则表达式也失败了，尝试从 markdown 代码块中再次提取 JSON
            if "```json" in json_str:
                try:
                    parts = json_str.split("```json", 1)
                    if len(parts) > 1:
                        nested_block = parts[1]
                        end_idx = nested_block.find("```")
                        if end_idx != -1:
                            nested_json = nested_block[:end_idx].strip()
                        else:
                            nested_json = nested_block.strip()

                        # 再次尝试用正则表达式提取
                        extracted = {}

                        match = re.search(r'"core_trends"\s*:\s*"((?:[^"\\]|\\.)*)"', nested_json, re.DOTALL)
                        if match:
                            extracted['core_trends'] = match.group(1)

                        match = re.search(r'"sentiment_controversy"\s*:\s*"((?:[^"\\]|\\.)*)"', nested_json, re.DOTALL)
                        if match:
                            extracted['sentiment_controversy'] = match.group(1)

                        match = re.search(r'"signals"\s*:\s*"((?:[^"\\]|\\.)*)"', nested_json, re.DOTALL)
                        if match:
                            extracted['signals'] = match.group(1)

                        match = re.search(r'"rss_insights"\s*:\s*"((?:[^"\\]|\\.)*)"', nested_json, re.DOTALL)
                        if match:
                            extracted['rss_insights'] = match.group(1)

                        match = re.search(r'"outlook_strategy"\s*:\s*"((?:[^"\\]|\\.)*)"', nested_json, re.DOTALL)
                        if match:
                            extracted['outlook_strategy'] = match.group(1)

                        if any(value.strip() for value in extracted.values()):
                            result.core_trends = extracted.get('core_trends', '')
                            result.sentiment_controversy = extracted.get('sentiment_controversy', '')
                            result.signals = extracted.get('signals', '')
                            result.rss_insights = extracted.get('rss_insights', '')
                            result.outlook_strategy = extracted.get('outlook_strategy', '')

                            result.success = True
                            return result
                except Exception:
                    pass

            # 所有方法都失败了，记录错误
            error_context = json_str[max(0, e.pos - 30):e.pos + 30] if json_str and hasattr(e, 'pos') and e.pos else ""
            result.error = f"JSON 解析错误: {e.msg if hasattr(e, 'msg') else str(e)}"
            if error_context:
                result.error += f"，上下文: ...{error_context}..."
            result.error += "。AI 原始回复不是有效 JSON，已拒绝将其作为分析报告展示"
            return result

        except (IndexError, KeyError, TypeError, ValueError) as e:
            result.error = f"响应解析错误: {type(e).__name__}: {str(e)}"

        except Exception as e:
            result.error = f"解析时发生未知错误: {type(e).__name__}: {str(e)}"

        return result
