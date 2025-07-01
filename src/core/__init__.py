"""
Core module for Athens MVP
核心模块导出
"""

# AI客户端
from .ai_client import AIClient

# 消息系统
from .message import (
    Message, MessageType, MessageBuilder,
    create_argument_message, create_counter_message,
    create_user_input_message, create_summary_message
)
from .conversation import Conversation
from .communication import Communication, CommunicationChannel, CommunicationStatus, MessageDeliveryStatus
from .context_manager import ContextManager

# 辩论系统
from .debate_states import (
    DebateState, TurnType, TerminationReason, DebateConfig,
    DebateRound, DebateMetrics, is_valid_state_transition, get_next_turn_type
)
from .debate_manager import DebateManager

__all__ = [
    # AI客户端
    'AIClient',
    
    # 消息系统
    'Message', 'MessageType', 'MessageBuilder',
    'create_argument_message', 'create_counter_message',
    'create_user_input_message', 'create_summary_message',
    'Conversation',
    'Communication', 'CommunicationChannel', 'CommunicationStatus', 'MessageDeliveryStatus',
    'ContextManager',
    
    # 辩论系统
    'DebateState', 'TurnType', 'TerminationReason', 'DebateConfig',
    'DebateRound', 'DebateMetrics', 'is_valid_state_transition', 'get_next_turn_type',
    'DebateManager'
]