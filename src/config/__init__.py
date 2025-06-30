"""
配置模块
提供Athens辩论平台的配置管理
"""

from .settings import settings
from .prompts import (
    PromptConfig,
    DEFAULT_PROMPTS,
    get_logician_prompt,
    get_skeptic_prompt,
    get_debate_rules,
    get_response_format
)

__all__ = [
    "settings",
    "PromptConfig",
    "DEFAULT_PROMPTS",
    "get_logician_prompt", 
    "get_skeptic_prompt",
    "get_debate_rules",
    "get_response_format"
]