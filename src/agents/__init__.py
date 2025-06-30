"""
智能体模块
提供Athens辩论平台的AI智能体实现
"""

from .base_agent import BaseAgent, Message
from .logician import Logician
from .skeptic import Skeptic

__all__ = [
    "BaseAgent",
    "Message", 
    "Logician",
    "Skeptic"
]