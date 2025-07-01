"""
辩论状态管理
定义辩论流程中的各种状态和相关常量
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class DebateState(Enum):
    """辩论状态枚举"""
    PREPARING = "preparing"        # 准备阶段 - 初始化参与者和话题
    ACTIVE = "active"             # 进行中 - 正在进行辩论
    PAUSED = "paused"             # 暂停 - 用户主动暂停
    COMPLETED = "completed"       # 已完成 - 正常结束
    ABORTED = "aborted"          # 已中止 - 异常终止


class TurnType(Enum):
    """发言轮次类型"""
    INITIAL_STATEMENT = "initial_statement"    # 初始论证
    COUNTER_ARGUMENT = "counter_argument"      # 反驳论证  
    REBUTTAL = "rebuttal"                     # 再次回应
    CLARIFICATION = "clarification"           # 澄清说明
    SUMMARY = "summary"                       # 总结发言


class TerminationReason(Enum):
    """辩论终止原因"""
    MAX_ROUNDS_REACHED = "max_rounds_reached"      # 达到最大轮次
    CONSENSUS_REACHED = "consensus_reached"         # 达成共识
    USER_TERMINATED = "user_terminated"             # 用户主动终止
    SYSTEM_ERROR = "system_error"                   # 系统错误
    CONTENT_REPETITION = "content_repetition"      # 内容重复
    QUALITY_DEGRADATION = "quality_degradation"    # 质量下降
    TIMEOUT = "timeout"                             # 超时
    AI_SERVICE_UNAVAILABLE = "ai_service_unavailable"  # AI服务不可用


class DebateConfig:
    """辩论配置常量"""
    
    # 默认轮次限制
    DEFAULT_MAX_ROUNDS = 10
    MIN_ROUNDS = 1
    MAX_ROUNDS_LIMIT = 50
    
    # 时间限制（秒）
    DEFAULT_ROUND_TIMEOUT = 120  # 每轮最大时间
    DEFAULT_DEBATE_TIMEOUT = 3600  # 整场辩论最大时间
    
    # 内容质量检测
    MIN_RESPONSE_LENGTH = 10  # 最小回应长度
    MAX_RESPONSE_LENGTH = 2000  # 最大回应长度
    SIMILARITY_THRESHOLD = 0.8  # 内容相似度阈值
    
    # 重试配置
    MAX_RETRY_ATTEMPTS = 3  # 最大重试次数
    RETRY_DELAY = 5  # 重试延迟（秒）
    
    # 智能终止检测
    REPETITION_CHECK_WINDOW = 3  # 检查重复的消息窗口
    QUALITY_DEGRADATION_THRESHOLD = 0.3  # 质量下降阈值


class DebateRound:
    """辩论轮次信息"""
    
    def __init__(self, round_number: int, initiator: str):
        self.round_number = round_number
        self.initiator = initiator  # 本轮发起者
        self.started_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.messages: List[str] = []  # 本轮产生的消息ID列表
        self.turn_type = TurnType.INITIAL_STATEMENT if round_number == 1 else TurnType.COUNTER_ARGUMENT
        
    def complete_round(self):
        """标记轮次完成"""
        self.completed_at = datetime.now()
        
    def get_duration(self) -> Optional[timedelta]:
        """获取轮次持续时间"""
        if self.completed_at:
            return self.completed_at - self.started_at
        return datetime.now() - self.started_at
        
    def add_message(self, message_id: str):
        """添加消息到本轮"""
        self.messages.append(message_id)
        
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "round_number": self.round_number,
            "initiator": self.initiator,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.get_duration().total_seconds() if self.completed_at else None,
            "messages": self.messages,
            "turn_type": self.turn_type.value
        }


class DebateMetrics:
    """辩论度量指标"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.total_rounds = 0
        self.total_messages = 0
        self.participant_message_counts: Dict[str, int] = {}
        self.average_response_time = 0.0
        self.content_quality_scores: List[float] = []
        
    def add_message(self, sender: str, response_time: float = 0.0, quality_score: float = 1.0):
        """添加消息统计"""
        self.total_messages += 1
        self.participant_message_counts[sender] = self.participant_message_counts.get(sender, 0) + 1
        
        # 更新平均响应时间
        total_time = self.average_response_time * (self.total_messages - 1) + response_time
        self.average_response_time = total_time / self.total_messages
        
        # 记录质量分数
        self.content_quality_scores.append(quality_score)
        
    def complete_debate(self):
        """完成辩论统计"""
        self.end_time = datetime.now()
        
    def get_duration(self) -> Optional[timedelta]:
        """获取辩论总时长"""
        end = self.end_time or datetime.now()
        return end - self.start_time
        
    def get_average_quality(self) -> float:
        """获取平均内容质量"""
        if not self.content_quality_scores:
            return 0.0
        return sum(self.content_quality_scores) / len(self.content_quality_scores)
        
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.get_duration().total_seconds(),
            "total_rounds": self.total_rounds,
            "total_messages": self.total_messages,
            "participant_message_counts": self.participant_message_counts,
            "average_response_time": self.average_response_time,
            "average_quality": self.get_average_quality(),
            "quality_scores": self.content_quality_scores
        }


# 状态转换规则
VALID_STATE_TRANSITIONS: Dict[DebateState, List[DebateState]] = {
    DebateState.PREPARING: [DebateState.ACTIVE, DebateState.ABORTED],
    DebateState.ACTIVE: [DebateState.PAUSED, DebateState.COMPLETED, DebateState.ABORTED],
    DebateState.PAUSED: [DebateState.ACTIVE, DebateState.ABORTED],
    DebateState.COMPLETED: [],  # 终态
    DebateState.ABORTED: []     # 终态
}


def is_valid_state_transition(from_state: DebateState, to_state: DebateState) -> bool:
    """检查状态转换是否有效"""
    return to_state in VALID_STATE_TRANSITIONS.get(from_state, [])


def get_next_turn_type(current_round: int, current_turn: TurnType) -> TurnType:
    """获取下一个发言类型"""
    if current_round == 1:
        if current_turn == TurnType.INITIAL_STATEMENT:
            return TurnType.COUNTER_ARGUMENT
        else:
            return TurnType.REBUTTAL
    else:
        # 后续轮次在反驳和回应之间交替
        if current_turn == TurnType.COUNTER_ARGUMENT:
            return TurnType.REBUTTAL
        else:
            return TurnType.COUNTER_ARGUMENT