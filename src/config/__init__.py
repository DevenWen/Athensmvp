"""
配置模块
提供Athens辩论平台的配置管理
"""

# 延迟导入以避免循环依赖和依赖问题
def get_settings():
    """获取settings实例"""
    from .settings import settings
    return settings

def get_prompt_config():
    """获取提示词配置实例"""
    from .prompts import DEFAULT_PROMPTS
    return DEFAULT_PROMPTS

# 便捷函数
def get_logician_prompt():
    """获取逻辑者提示词"""
    from .prompts import get_logician_prompt
    return get_logician_prompt()

def get_skeptic_prompt():
    """获取怀疑者提示词"""
    from .prompts import get_skeptic_prompt
    return get_skeptic_prompt()

def get_apollo_prompt():
    """获取Apollo提示词"""
    from .prompts import get_apollo_prompt
    return get_apollo_prompt()

def get_muses_prompt():
    """获取Muses提示词"""
    from .prompts import get_muses_prompt
    return get_muses_prompt()

def get_debate_rules():
    """获取辩论规则"""
    from .prompts import get_debate_rules
    return get_debate_rules()

def get_response_format():
    """获取回应格式规范"""
    from .prompts import get_response_format
    return get_response_format()

__all__ = [
    "get_settings",
    "get_prompt_config",
    "get_logician_prompt", 
    "get_skeptic_prompt",
    "get_apollo_prompt",
    "get_muses_prompt",
    "get_debate_rules",
    "get_response_format"
]