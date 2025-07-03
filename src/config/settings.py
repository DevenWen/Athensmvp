import os
import logging
from typing import Dict, Any, Optional, TYPE_CHECKING

# 尝试加载dotenv，如果不可用则跳过
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv不可用，继续使用环境变量
    pass

# 尝试导入pydantic，如果不可用则使用基本类
try:
    from pydantic import BaseModel
    PYDANTIC_AVAILABLE = True
except ImportError:
    # 创建一个简单的BaseModel替代
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    PYDANTIC_AVAILABLE = False

if TYPE_CHECKING:
    from .user_config import UserConfigManager

logger = logging.getLogger(__name__)

class Settings(BaseModel):
    # 明确声明Pydantic字段
    openrouter_api_key: Optional[str] = None
    default_model: str = "openai/gpt-3.5-turbo"
    
    # 新的角色配置
    apollo_model: str = "openai/gpt-4-turbo"
    muses_model: str = "anthropic/claude-3-opus"
    
    # 保持向后兼容（废弃但保留）
    logician_model: str = "openai/gpt-4-turbo"
    skeptic_model: str = "anthropic/claude-3-opus"
    
    # 允许额外字段
    class Config:
        extra = "allow"
        arbitrary_types_allowed = True
    
    def __init__(self, user_config_manager: Optional['UserConfigManager'] = None, **kwargs):
        # 从环境变量获取默认值
        env_values = {
            'openrouter_api_key': os.getenv("OPENROUTER_API_KEY"),
            'default_model': os.getenv("DEFAULT_MODEL", "openai/gpt-3.5-turbo"),
            'apollo_model': os.getenv("APOLLO_MODEL", "openai/gpt-4-turbo"),
            'muses_model': os.getenv("MUSES_MODEL", "anthropic/claude-3-opus"),
            'logician_model': os.getenv("LOGICIAN_MODEL", "openai/gpt-4-turbo"),
            'skeptic_model': os.getenv("SKEPTIC_MODEL", "anthropic/claude-3-opus"),
        }
        
        # 合并环境变量值和传入的kwargs
        merged_kwargs = {**env_values, **kwargs}
        
        # 处理pydantic初始化
        if PYDANTIC_AVAILABLE:
            super().__init__(**merged_kwargs)
        else:
            # 简单设置所有参数
            for key, value in merged_kwargs.items():
                setattr(self, key, value)
        
        # 设置用户配置管理器（使用object.__setattr__避免Pydantic验证）
        object.__setattr__(self, '_user_config', user_config_manager)
        if self._user_config is None:
            try:
                from .user_config import DEFAULT_USER_CONFIG
                object.__setattr__(self, '_user_config', DEFAULT_USER_CONFIG)
            except Exception as e:
                logger.warning(f"无法加载用户配置: {e}")
                object.__setattr__(self, '_user_config', None)
    
    @property
    def user_config(self) -> Optional['UserConfigManager']:
        """获取用户配置管理器"""
        return getattr(self, '_user_config', None)
    
    @property
    def apollo_model_config(self) -> str:
        """获取Apollo模型配置，优先使用用户配置"""
        user_config = self.user_config
        if user_config:
            user_model = user_config.get_setting("agent_settings.apollo.model")
            if user_model:
                return user_model
        # 回退到环境变量或默认值
        return os.getenv("APOLLO_MODEL", "openai/gpt-4-turbo")
    
    @property
    def muses_model_config(self) -> str:
        """获取Muses模型配置，优先使用用户配置"""
        user_config = self.user_config
        if user_config:
            user_model = user_config.get_setting("agent_settings.muses.model")
            if user_model:
                return user_model
        # 回退到环境变量或默认值
        return os.getenv("MUSES_MODEL", "anthropic/claude-3-opus")
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """获取指定Agent的完整配置"""
        user_config = self.user_config
        if not user_config:
            # 返回默认配置
            if agent_name == "apollo":
                return {
                    "model": self.apollo_model,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            elif agent_name == "muses":
                return {
                    "model": self.muses_model,
                    "temperature": 0.8,
                    "max_tokens": 2000
                }
            else:
                raise ValueError(f"未知的Agent: {agent_name}")
        
        # 从用户配置获取
        agent_config = user_config.get_setting(f"agent_settings.{agent_name}", {})
        
        # 设置默认值
        defaults = {
            "apollo": {
                "model": "openai/gpt-4-turbo",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "muses": {
                "model": "anthropic/claude-3-opus", 
                "temperature": 0.8,
                "max_tokens": 2000
            }
        }
        
        if agent_name in defaults:
            for key, default_value in defaults[agent_name].items():
                if key not in agent_config:
                    agent_config[key] = default_value
        
        return agent_config
    
    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI配置"""
        user_config = self.user_config
        if not user_config:
            return {
                "theme": "default",
                "show_timestamps": True,
                "show_typing_indicator": True,
                "auto_scroll": True,
                "input_box_style": "bordered"
            }
        
        return user_config.get_setting("ui_settings", {
            "theme": "default",
            "show_timestamps": True,
            "show_typing_indicator": True,
            "auto_scroll": True,
            "input_box_style": "bordered"
        })
    
    def get_debate_config(self) -> Dict[str, Any]:
        """获取辩论配置"""
        user_config = self.user_config
        if not user_config:
            return {
                "max_rounds": 20,
                "auto_end_after_consensus": True,
                "save_summaries": True,
                "summary_format": "markdown"
            }
        
        return user_config.get_setting("debate_settings", {
            "max_rounds": 20,
            "auto_end_after_consensus": True,
            "save_summaries": True,
            "summary_format": "markdown"
        })
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """获取用户偏好设置"""
        user_config = self.user_config
        if not user_config:
            return {
                "theme": "default",
                "language": "zh_CN",
                "auto_save_debates": True,
                "debate_history_limit": 100
            }
        
        return user_config.get_setting("user_preferences", {
            "theme": "default",
            "language": "zh_CN",
            "auto_save_debates": True,
            "debate_history_limit": 100
        })
    
    def update_agent_config(self, agent_name: str, config: Dict[str, Any]) -> None:
        """更新Agent配置"""
        user_config = self.user_config
        if user_config:
            for key, value in config.items():
                user_config.set_setting(f"agent_settings.{agent_name}.{key}", value)
            user_config.save_config()
        else:
            logger.warning("用户配置不可用，无法更新Agent配置")
    
    def update_ui_config(self, config: Dict[str, Any]) -> None:
        """更新UI配置"""
        user_config = self.user_config
        if user_config:
            for key, value in config.items():
                user_config.set_setting(f"ui_settings.{key}", value)
            user_config.save_config()
        else:
            logger.warning("用户配置不可用，无法更新UI配置")
    
    def get_directories(self) -> Dict[str, str]:
        """获取目录配置"""
        user_config = self.user_config
        if not user_config:
            return {
                "logs": "~/.athens/logs",
                "reports": "~/.athens/reports", 
                "exports": "~/.athens/exports"
            }
        
        return user_config.get_setting("directories", {
            "logs": "~/.athens/logs",
            "reports": "~/.athens/reports",
            "exports": "~/.athens/exports"
        })

# 延迟初始化settings实例，避免导入时的初始化问题
def get_settings() -> Settings:
    """获取Settings实例"""
    global _settings_instance
    if '_settings_instance' not in globals():
        globals()['_settings_instance'] = Settings()
    return globals()['_settings_instance']

# 为了向后兼容，保留settings变量但延迟初始化
class _SettingsProxy:
    """Settings代理类，支持延迟初始化"""
    def __getattr__(self, name):
        return getattr(get_settings(), name)
    
    def __setattr__(self, name, value):
        return setattr(get_settings(), name, value)

settings = _SettingsProxy()
