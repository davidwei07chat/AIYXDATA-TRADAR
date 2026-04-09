# (C) 2026 AIYXDATA. All rights reserved.
# Project: AIYXDATA-TRADAR

# coding=utf-8
"""
核心模块 - 配置管理和核心工具
"""

from aiyxdata_tradar.core.config import (
    parse_multi_account_config,
    validate_paired_configs,
    limit_accounts,
    get_account_at_index,
)
from aiyxdata_tradar.core.loader import load_config
from aiyxdata_tradar.core.frequency import load_frequency_words, matches_word_groups
from aiyxdata_tradar.core.scheduler import Scheduler, ResolvedSchedule
from aiyxdata_tradar.core.data import (
    read_all_today_titles_from_storage,
    read_all_today_titles,
    detect_latest_new_titles_from_storage,
    detect_latest_new_titles,
)
from aiyxdata_tradar.core.analyzer import (
    calculate_news_weight,
    format_time_display,
    count_word_frequency,
    count_rss_frequency,
)

__all__ = [
    "parse_multi_account_config",
    "validate_paired_configs",
    "limit_accounts",
    "get_account_at_index",
    "load_config",
    "load_frequency_words",
    "matches_word_groups",
    # 数据处理
    "read_all_today_titles_from_storage",
    "read_all_today_titles",
    "detect_latest_new_titles_from_storage",
    "detect_latest_new_titles",
    # 统计分析
    "calculate_news_weight",
    "format_time_display",
    "count_word_frequency",
    "count_rss_frequency",
    # 调度器
    "Scheduler",
    "ResolvedSchedule",
]
