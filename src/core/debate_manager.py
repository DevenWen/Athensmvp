"""
辩论管理器
协调和控制Athens系统中逻辑者和怀疑者之间的辩论流程
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable, Any, Tuple
from datetime import datetime, timedelta
import logging

from src.core.debate_states import (
    DebateState, TurnType, TerminationReason, DebateConfig, 
    DebateRound, DebateMetrics, is_valid_state_transition, get_next_turn_type
)
from src.core.message import Message, MessageType, create_argument_message, create_counter_message
from src.core.conversation import Conversation
from src.core.communication import Communication
from src.core.context_manager import ContextManager
# 延迟导入避免循环依赖
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.agents.base_agent import BaseAgent
    from src.agents.logician import Logician
    from src.agents.skeptic import Skeptic

logger = logging.getLogger(__name__)


class DebateManager:
    """
    辩论管理器
    负责协调逻辑者和怀疑者之间的辩论，管理轮次、状态和终止条件
    """
    
    def __init__(self, 
                 logician: Optional['BaseAgent'] = None,
                 skeptic: Optional['BaseAgent'] = None,
                 topic: str = "",
                 max_rounds: int = DebateConfig.DEFAULT_MAX_ROUNDS,
                 round_timeout: int = DebateConfig.DEFAULT_ROUND_TIMEOUT):
        """
        初始化辩论管理器
        
        Args:
            logician: 逻辑者智能体
            skeptic: 怀疑者智能体
            topic: 辩论话题
            max_rounds: 最大轮次数
            round_timeout: 每轮超时时间（秒）
        """
        # 运行时导入避免循环依赖
        if logician is None or skeptic is None:
            from src.agents.logician import Logician
            from src.agents.skeptic import Skeptic
        
        # 智能体
        self.logician = logician or Logician()
        self.skeptic = skeptic or Skeptic()
        
        # 辩论配置
        self.topic = topic
        self.max_rounds = max_rounds
        self.round_timeout = round_timeout
        
        # 状态管理
        self.state = DebateState.PREPARING
        self.current_round = 0
        self.current_speaker = self.logician  # 逻辑者先发言
        self.termination_reason: Optional[TerminationReason] = None
        
        # 通信系统
        self.communication = Communication()
        self.debate_channel_id = "debate_main"
        self.conversation = Conversation(f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.context_manager = ContextManager(self.conversation)
        
        # 轮次和统计
        self.rounds: List[DebateRound] = []
        self.metrics = DebateMetrics()
        
        # 事件回调
        self.on_round_start: Optional[Callable[[int, str], None]] = None
        self.on_round_complete: Optional[Callable[[DebateRound], None]] = None
        self.on_message_sent: Optional[Callable[[Message], None]] = None
        self.on_state_changed: Optional[Callable[[DebateState, DebateState], None]] = None
        self.on_debate_complete: Optional[Callable[[TerminationReason], None]] = None
        
        # 初始化通信通道
        self._setup_communication()
        
    def _setup_communication(self):
        """设置通信通道"""
        participants = [self.logician.name, self.skeptic.name]
        self.communication.create_channel(self.debate_channel_id, participants)
        
        # 添加消息监听器
        self.communication.add_global_listener(self._on_message_received)
        
    def _on_message_received(self, message: Message, channel_id: str):
        """处理接收到的消息"""
        if channel_id == self.debate_channel_id:
            self.conversation.add_message(message)
            if self.on_message_sent:
                self.on_message_sent(message)
                
    def _change_state(self, new_state: DebateState) -> bool:
        """
        改变辩论状态
        
        Args:
            new_state: 新状态
            
        Returns:
            是否成功改变状态
        """
        if not is_valid_state_transition(self.state, new_state):
            logger.warning(f"Invalid state transition: {self.state} -> {new_state}")
            return False
            
        old_state = self.state
        self.state = new_state
        
        logger.info(f"Debate state changed: {old_state} -> {new_state}")
        
        if self.on_state_changed:
            self.on_state_changed(old_state, new_state)
            
        return True
        
    def start_debate(self, initial_statement: str = "") -> bool:
        """
        开始辩论
        
        Args:
            initial_statement: 初始论证（可选，如果为空则让逻辑者自动生成）
            
        Returns:
            是否成功开始
        """
        if self.state != DebateState.PREPARING:
            logger.error(f"Cannot start debate in state: {self.state}")
            return False
            
        if not self.topic:
            logger.error("Cannot start debate without topic")
            return False
            
        # 改变状态
        if not self._change_state(DebateState.ACTIVE):
            return False
            
        # 开始第一轮
        self.current_round = 1
        self.current_speaker = self.logician
        
        # 创建第一轮
        round_obj = DebateRound(self.current_round, self.logician.name)
        self.rounds.append(round_obj)
        
        if self.on_round_start:
            self.on_round_start(self.current_round, self.logician.name)
            
        # 发送初始论证
        try:
            if initial_statement:
                # 使用提供的初始论证
                message = create_argument_message(
                    self.logician.name, 
                    initial_statement, 
                    self.skeptic.name
                )
            else:
                # 让逻辑者生成初始论证
                context = f"话题: {self.topic}\n请提出你的初始论证。"
                response = self.logician.generate_response(context)
                message = create_argument_message(
                    self.logician.name,
                    response,
                    self.skeptic.name
                )
                
            # 发送消息
            success = self.communication.send_message(message, self.debate_channel_id)
            if success:
                round_obj.add_message(message.id)
                self.metrics.add_message(self.logician.name)
                
                # 切换到怀疑者
                self.current_speaker = self.skeptic
                
                logger.info(f"Debate started with initial statement from {self.logician.name}")
                return True
            else:
                logger.error("Failed to send initial statement")
                self._change_state(DebateState.ABORTED)
                return False
                
        except Exception as e:
            logger.error(f"Error starting debate: {e}")
            self._change_state(DebateState.ABORTED)
            return False
            
    def process_round(self) -> bool:
        """
        处理当前轮次的发言
        
        Returns:
            是否应该继续辩论
        """
        if self.state != DebateState.ACTIVE:
            logger.warning(f"Cannot process round in state: {self.state}")
            return False
            
        try:
            start_time = time.time()
            
            # 获取当前发言者的上下文
            context_messages = self.context_manager.build_context(self.current_speaker.name)
            context_text = self.context_manager.get_formatted_context(self.current_speaker.name)
            
            # 添加话题和角色信息
            full_context = f"话题: {self.topic}\n\n{context_text}\n\n请根据以上对话历史，提出你的观点。"
            
            # 生成回应
            response = self.current_speaker.generate_response(full_context)
            
            # 检查回应质量
            if not self._is_valid_response(response):
                logger.warning(f"Invalid response from {self.current_speaker.name}: {response}")
                return self._handle_invalid_response()
                
            # 创建消息
            message = create_counter_message(
                self.current_speaker.name,
                response,
                context_messages[-1].id if context_messages else "",
                self._get_other_speaker().name
            )
            
            # 发送消息
            success = self.communication.send_message(message, self.debate_channel_id)
            if not success:
                logger.error(f"Failed to send message from {self.current_speaker.name}")
                return False
                
            # 更新统计
            response_time = time.time() - start_time
            quality_score = self._evaluate_response_quality(response)
            self.metrics.add_message(self.current_speaker.name, response_time, quality_score)
            
            # 添加到当前轮次
            current_round_obj = self.rounds[-1]
            current_round_obj.add_message(message.id)
            
            # 切换发言者
            self.current_speaker = self._get_other_speaker()
            
            # 检查是否需要开始新轮次
            if self._should_start_new_round():
                self._complete_current_round()
                if not self._start_next_round():
                    return False
                    
            # 检查终止条件
            return self._check_continuation_conditions()
            
        except Exception as e:
            logger.error(f"Error processing round: {e}")
            self._terminate_debate(TerminationReason.SYSTEM_ERROR)
            return False
            
    def _get_other_speaker(self) -> 'BaseAgent':
        """获取另一个发言者"""
        return self.skeptic if self.current_speaker == self.logician else self.logician
        
    def _should_start_new_round(self) -> bool:
        """判断是否应该开始新轮次"""
        current_round_obj = self.rounds[-1]
        # 每轮包含两个发言：逻辑者和怀疑者各一次
        return len(current_round_obj.messages) >= 2
        
    def _complete_current_round(self):
        """完成当前轮次"""
        if self.rounds:
            current_round_obj = self.rounds[-1]
            current_round_obj.complete_round()
            self.metrics.total_rounds += 1
            
            if self.on_round_complete:
                self.on_round_complete(current_round_obj)
                
    def _start_next_round(self) -> bool:
        """开始下一轮"""
        self.current_round += 1
        
        # 检查是否超过最大轮次
        if self.current_round > self.max_rounds:
            self._terminate_debate(TerminationReason.MAX_ROUNDS_REACHED)
            return False
            
        # 创建新轮次
        round_obj = DebateRound(self.current_round, self.current_speaker.name)
        self.rounds.append(round_obj)
        
        if self.on_round_start:
            self.on_round_start(self.current_round, self.current_speaker.name)
            
        return True
        
    def _check_continuation_conditions(self) -> bool:
        """检查是否应该继续辩论"""
        # 检查内容重复
        if self._detect_content_repetition():
            self._terminate_debate(TerminationReason.CONTENT_REPETITION)
            return False
            
        # 检查质量下降
        if self._detect_quality_degradation():
            self._terminate_debate(TerminationReason.QUALITY_DEGRADATION)
            return False
            
        # 检查共识达成（可以在后续版本中实现更复杂的逻辑）
        # if self._detect_consensus():
        #     self._terminate_debate(TerminationReason.CONSENSUS_REACHED)
        #     return False
            
        return True
        
    def _detect_content_repetition(self) -> bool:
        """检测内容重复"""
        if len(self.conversation.messages) < DebateConfig.REPETITION_CHECK_WINDOW * 2:
            return False
            
        recent_messages = self.conversation.get_recent_messages(
            DebateConfig.REPETITION_CHECK_WINDOW * 2
        )
        
        # 简单的重复检测：检查最近的消息是否有高度相似的内容
        for i in range(len(recent_messages) - 1):
            for j in range(i + 1, len(recent_messages)):
                if self._calculate_similarity(recent_messages[i].content, recent_messages[j].content) > DebateConfig.SIMILARITY_THRESHOLD:
                    return True
                    
        return False
        
    def _detect_quality_degradation(self) -> bool:
        """检测质量下降"""
        if len(self.metrics.content_quality_scores) < 4:
            return False
            
        # 检查最近几个回应的质量是否显著下降
        recent_scores = self.metrics.content_quality_scores[-4:]
        average_recent = sum(recent_scores) / len(recent_scores)
        
        return average_recent < DebateConfig.QUALITY_DEGRADATION_THRESHOLD
        
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简单实现）"""
        # 对于中文，按字符进行比较
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
            
        # 转换为字符集合
        chars1 = set(text1.lower())
        chars2 = set(text2.lower())
        
        intersection = chars1 & chars2
        union = chars1 | chars2
        
        if not union:
            return 0.0
            
        return len(intersection) / len(union)
        
    def _is_valid_response(self, response: str) -> bool:
        """检查回应是否有效"""
        if not response or not response.strip():
            return False
        if len(response) < DebateConfig.MIN_RESPONSE_LENGTH:
            return False
        if len(response) > DebateConfig.MAX_RESPONSE_LENGTH:
            return False
        return True
        
    def _evaluate_response_quality(self, response: str) -> float:
        """评估回应质量（简单实现）"""
        # 基于长度、多样性等简单指标
        if not response:
            return 0.0
            
        # 长度得分（适中长度得分更高）
        length_score = min(len(response) / 200, 1.0)
        
        # 词汇多样性得分
        words = response.split()
        unique_words = set(words)
        diversity_score = len(unique_words) / len(words) if words else 0
        
        # 简单的质量评分
        quality = (length_score * 0.3 + diversity_score * 0.7)
        return min(quality, 1.0)
        
    def _handle_invalid_response(self) -> bool:
        """处理无效回应"""
        # 简单处理：记录警告并继续
        logger.warning(f"Invalid response from {self.current_speaker.name}, continuing...")
        return True
        
    def _terminate_debate(self, reason: TerminationReason):
        """终止辩论"""
        self.termination_reason = reason
        
        # 完成当前轮次
        if self.rounds and not self.rounds[-1].completed_at:
            self._complete_current_round()
            
        # 完成统计
        self.metrics.complete_debate()
        
        # 改变状态
        if reason == TerminationReason.SYSTEM_ERROR:
            self._change_state(DebateState.ABORTED)
        else:
            self._change_state(DebateState.COMPLETED)
            
        logger.info(f"Debate terminated: {reason}")
        
        if self.on_debate_complete:
            self.on_debate_complete(reason)
            
    def pause_debate(self) -> bool:
        """暂停辩论"""
        if self.state != DebateState.ACTIVE:
            return False
        return self._change_state(DebateState.PAUSED)
        
    def resume_debate(self) -> bool:
        """恢复辩论"""
        if self.state != DebateState.PAUSED:
            return False
        return self._change_state(DebateState.ACTIVE)
        
    def end_debate(self) -> bool:
        """手动结束辩论"""
        if self.state not in [DebateState.ACTIVE, DebateState.PAUSED]:
            return False
        self._terminate_debate(TerminationReason.USER_TERMINATED)
        return True
        
    def get_debate_status(self) -> Dict[str, Any]:
        """获取辩论状态信息"""
        return {
            "state": self.state.value,
            "topic": self.topic,
            "current_round": self.current_round,
            "max_rounds": self.max_rounds,
            "current_speaker": self.current_speaker.name if self.current_speaker else None,
            "total_messages": len(self.conversation.messages),
            "termination_reason": self.termination_reason.value if self.termination_reason else None,
            "started_at": self.metrics.start_time.isoformat(),
            "duration": self.metrics.get_duration().total_seconds(),
            "participants": [self.logician.name, self.skeptic.name]
        }
        
    def get_conversation_history(self) -> List[Message]:
        """获取对话历史"""
        return self.conversation.messages.copy()
        
    def get_debate_summary(self) -> Dict[str, Any]:
        """获取辩论总结"""
        return {
            "debate_info": self.get_debate_status(),
            "metrics": self.metrics.to_dict(),
            "rounds": [round_obj.to_dict() for round_obj in self.rounds],
            "conversation_stats": self.conversation.get_statistics()
        }
        
    def run_observation_mode(self) -> Dict[str, Any]:
        """
        运行观察模式（自动化辩论）
        
        Returns:
            辩论结果总结
        """
        logger.info(f"Starting observation mode debate on topic: {self.topic}")
        
        # 开始辩论
        if not self.start_debate():
            logger.error("Failed to start debate")
            return self.get_debate_summary()
            
        # 自动进行轮次
        while self.state == DebateState.ACTIVE:
            if not self.process_round():
                break
                
            # 短暂延迟（模拟思考时间）
            time.sleep(1)
            
        logger.info(f"Observation mode completed. Final state: {self.state}")
        return self.get_debate_summary()