"""
辩论管理器单元测试
测试DebateManager、DebateStates等辩论相关功能
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.core.debate_manager import DebateManager
from src.core.debate_states import (
    DebateState, TurnType, TerminationReason, DebateConfig,
    DebateRound, DebateMetrics, is_valid_state_transition, get_next_turn_type
)
from src.core.message import Message, MessageType
from src.agents.base_agent import BaseAgent
from src.agents.apollo import Apollo
from src.agents.muses import Muses as Skeptic


class MockAgent(BaseAgent):
    """模拟智能体用于测试"""
    
    def __init__(self, name: str, responses: list = None):
        # 创建Mock AI client
        mock_ai_client = Mock()
        mock_ai_client.generate_response.return_value = "Mock response"
        
        super().__init__(name, f"{name} role prompt", mock_ai_client)
        self.responses = responses or ["测试回应"]
        self.response_index = 0
        
    def generate_response(self, context: str, **kwargs) -> str:
        """生成模拟回应"""
        if self.response_index < len(self.responses):
            response = self.responses[self.response_index]
            self.response_index += 1
            return response
        return "默认回应"


class TestDebateStates:
    """辩论状态相关功能测试"""
    
    def test_debate_state_enum(self):
        """测试辩论状态枚举"""
        assert DebateState.PREPARING.value == "preparing"
        assert DebateState.ACTIVE.value == "active"
        assert DebateState.PAUSED.value == "paused"
        assert DebateState.COMPLETED.value == "completed"
        assert DebateState.ABORTED.value == "aborted"
    
    def test_turn_type_enum(self):
        """测试发言类型枚举"""
        assert TurnType.INITIAL_STATEMENT.value == "initial_statement"
        assert TurnType.COUNTER_ARGUMENT.value == "counter_argument"
        assert TurnType.REBUTTAL.value == "rebuttal"
        assert TurnType.CLARIFICATION.value == "clarification"
        assert TurnType.SUMMARY.value == "summary"
    
    def test_termination_reason_enum(self):
        """测试终止原因枚举"""
        assert TerminationReason.MAX_ROUNDS_REACHED.value == "max_rounds_reached"
        assert TerminationReason.CONSENSUS_REACHED.value == "consensus_reached"
        assert TerminationReason.USER_TERMINATED.value == "user_terminated"
        assert TerminationReason.SYSTEM_ERROR.value == "system_error"
    
    def test_debate_config_constants(self):
        """测试辩论配置常量"""
        assert DebateConfig.DEFAULT_MAX_ROUNDS == 10
        assert DebateConfig.MIN_ROUNDS == 1
        assert DebateConfig.MAX_ROUNDS_LIMIT == 50
        assert DebateConfig.DEFAULT_ROUND_TIMEOUT == 120
        assert DebateConfig.MIN_RESPONSE_LENGTH == 10
    
    def test_valid_state_transitions(self):
        """测试状态转换有效性"""
        # 有效转换
        assert is_valid_state_transition(DebateState.PREPARING, DebateState.ACTIVE)
        assert is_valid_state_transition(DebateState.ACTIVE, DebateState.PAUSED)
        assert is_valid_state_transition(DebateState.PAUSED, DebateState.ACTIVE)
        assert is_valid_state_transition(DebateState.ACTIVE, DebateState.COMPLETED)
        
        # 无效转换
        assert not is_valid_state_transition(DebateState.COMPLETED, DebateState.ACTIVE)
        assert not is_valid_state_transition(DebateState.ABORTED, DebateState.ACTIVE)
        assert not is_valid_state_transition(DebateState.PREPARING, DebateState.PAUSED)
    
    def test_get_next_turn_type(self):
        """测试获取下一个发言类型"""
        # 第一轮
        assert get_next_turn_type(1, TurnType.INITIAL_STATEMENT) == TurnType.COUNTER_ARGUMENT
        assert get_next_turn_type(1, TurnType.COUNTER_ARGUMENT) == TurnType.REBUTTAL
        
        # 后续轮次
        assert get_next_turn_type(2, TurnType.COUNTER_ARGUMENT) == TurnType.REBUTTAL
        assert get_next_turn_type(2, TurnType.REBUTTAL) == TurnType.COUNTER_ARGUMENT


class TestDebateRound:
    """辩论轮次测试"""
    
    def test_debate_round_creation(self):
        """测试辩论轮次创建"""
        round_obj = DebateRound(1, "逻辑者")
        
        assert round_obj.round_number == 1
        assert round_obj.initiator == "逻辑者"
        assert round_obj.completed_at is None
        assert len(round_obj.messages) == 0
        assert round_obj.turn_type == TurnType.INITIAL_STATEMENT
    
    def test_debate_round_completion(self):
        """测试轮次完成"""
        round_obj = DebateRound(1, "逻辑者")
        start_time = round_obj.started_at
        
        # 添加一些延迟
        time.sleep(0.01)
        
        round_obj.complete_round()
        
        assert round_obj.completed_at is not None
        assert round_obj.completed_at > start_time
        
        duration = round_obj.get_duration()
        assert duration is not None
        assert duration.total_seconds() > 0
    
    def test_add_message_to_round(self):
        """测试向轮次添加消息"""
        round_obj = DebateRound(2, "怀疑者")
        
        round_obj.add_message("msg_123")
        round_obj.add_message("msg_456")
        
        assert len(round_obj.messages) == 2
        assert "msg_123" in round_obj.messages
        assert "msg_456" in round_obj.messages
    
    def test_round_to_dict(self):
        """测试轮次序列化"""
        round_obj = DebateRound(1, "逻辑者")  # 第1轮应该是INITIAL_STATEMENT
        round_obj.add_message("msg_789")
        round_obj.complete_round()
        
        data = round_obj.to_dict()
        
        assert data["round_number"] == 1
        assert data["initiator"] == "逻辑者"
        assert "started_at" in data
        assert "completed_at" in data
        assert "duration_seconds" in data
        assert data["messages"] == ["msg_789"]
        assert data["turn_type"] == TurnType.INITIAL_STATEMENT.value


class TestDebateMetrics:
    """辩论度量测试"""
    
    def test_metrics_creation(self):
        """测试度量创建"""
        metrics = DebateMetrics()
        
        assert metrics.total_messages == 0
        assert metrics.total_rounds == 0
        assert len(metrics.participant_message_counts) == 0
        assert metrics.average_response_time == 0.0
        assert len(metrics.content_quality_scores) == 0
    
    def test_add_message_to_metrics(self):
        """测试添加消息到度量"""
        metrics = DebateMetrics()
        
        metrics.add_message("逻辑者", 2.5, 0.8)
        metrics.add_message("怀疑者", 3.0, 0.9)
        metrics.add_message("逻辑者", 1.5, 0.7)
        
        assert metrics.total_messages == 3
        assert metrics.participant_message_counts["逻辑者"] == 2
        assert metrics.participant_message_counts["怀疑者"] == 1
        assert metrics.average_response_time == (2.5 + 3.0 + 1.5) / 3
        assert len(metrics.content_quality_scores) == 3
    
    def test_average_quality_calculation(self):
        """测试平均质量计算"""
        metrics = DebateMetrics()
        
        metrics.add_message("测试者", 1.0, 0.8)
        metrics.add_message("测试者", 1.0, 0.6)
        metrics.add_message("测试者", 1.0, 1.0)
        
        assert metrics.get_average_quality() == (0.8 + 0.6 + 1.0) / 3
    
    def test_metrics_completion(self):
        """测试度量完成"""
        metrics = DebateMetrics()
        start_time = metrics.start_time
        
        time.sleep(0.01)
        metrics.complete_debate()
        
        assert metrics.end_time is not None
        assert metrics.end_time > start_time
        
        duration = metrics.get_duration()
        assert duration is not None
        assert duration.total_seconds() > 0
    
    def test_metrics_to_dict(self):
        """测试度量序列化"""
        metrics = DebateMetrics()
        metrics.add_message("逻辑者", 2.0, 0.8)
        metrics.complete_debate()
        
        data = metrics.to_dict()
        
        assert "start_time" in data
        assert "end_time" in data
        assert "duration_seconds" in data
        assert data["total_messages"] == 1
        assert data["participant_message_counts"]["逻辑者"] == 1
        assert data["average_response_time"] == 2.0
        assert data["average_quality"] == 0.8


class TestDebateManager:
    """辩论管理器测试"""
    
    def test_debate_manager_creation(self):
        """测试辩论管理器创建"""
        logician = MockAgent("逻辑者")
        skeptic = MockAgent("怀疑者")
        
        manager = DebateManager(
            apollo=logician,
            muses=skeptic,
            topic="人工智能的发展前景",
            max_rounds=5
        )
        
        assert manager.logician is logician
        assert manager.skeptic is skeptic
        assert manager.topic == "人工智能的发展前景"
        assert manager.max_rounds == 5
        assert manager.state == DebateState.PREPARING
        assert manager.current_round == 0
        assert manager.current_speaker == logician
    
    def test_debate_manager_with_defaults(self):
        """测试使用默认参数创建辩论管理器"""
        manager = DebateManager(topic="测试话题")
        
        assert isinstance(manager.logician, Apollo)
        assert isinstance(manager.skeptic, Skeptic)
        assert manager.topic == "测试话题"
        assert manager.max_rounds == DebateConfig.DEFAULT_MAX_ROUNDS
    
    def test_start_debate_success(self):
        """测试成功开始辩论"""
        logician = MockAgent("逻辑者", ["我认为AI将改变世界"])
        skeptic = MockAgent("怀疑者")
        
        manager = DebateManager(logician, skeptic, "AI发展")
        
        # 设置回调
        state_changes = []
        round_starts = []
        
        def on_state_changed(old, new):
            state_changes.append((old, new))
            
        def on_round_start(round_num, speaker):
            round_starts.append((round_num, speaker))
        
        manager.on_state_changed = on_state_changed
        manager.on_round_start = on_round_start
        
        # 开始辩论
        result = manager.start_debate("AI将带来巨大变革")
        
        assert result is True
        assert manager.state == DebateState.ACTIVE
        assert manager.current_round == 1
        assert manager.current_speaker == skeptic  # 切换到怀疑者
        assert len(manager.rounds) == 1
        assert len(state_changes) == 1
        assert state_changes[0] == (DebateState.PREPARING, DebateState.ACTIVE)
        assert len(round_starts) == 1
        assert round_starts[0] == (1, "逻辑者")
    
    def test_start_debate_without_topic(self):
        """测试没有话题时开始辩论失败"""
        manager = DebateManager()
        
        result = manager.start_debate()
        
        assert result is False
        assert manager.state == DebateState.PREPARING
    
    def test_start_debate_wrong_state(self):
        """测试错误状态下开始辩论失败"""
        manager = DebateManager(topic="测试")
        manager.state = DebateState.ACTIVE
        
        result = manager.start_debate()
        
        assert result is False
    
    def test_process_round_success(self):
        """测试成功处理轮次"""
        logician = MockAgent("逻辑者", ["这是一个详细的初始论证，包含了充分的理由和支持"])
        skeptic = MockAgent("怀疑者", ["我对这个论证有不同的看法和质疑，需要进一步讨论", "我需要进一步质疑这个观点的合理性"])
        
        manager = DebateManager(logician, skeptic, "测试话题")
        
        # 记录消息
        sent_messages = []
        def on_message_sent(message):
            sent_messages.append(message)
        manager.on_message_sent = on_message_sent
        
        # 开始辩论
        result = manager.start_debate()
        assert result is True
        
        # 应该有初始论证
        assert len(sent_messages) == 1
        assert manager.current_speaker == skeptic  # 切换到怀疑者
        
        # 处理第一轮（怀疑者回应）
        result = manager.process_round()
        
        assert result is True
        assert len(sent_messages) == 2  # 初始论证 + 怀疑者回应
        assert manager.current_speaker == logician  # 切换回逻辑者
    
    def test_process_round_wrong_state(self):
        """测试错误状态下处理轮次"""
        manager = DebateManager(topic="测试")
        
        result = manager.process_round()
        
        assert result is False
    
    def test_max_rounds_termination(self):
        """测试最大轮次终止"""
        logician = MockAgent("逻辑者", ["这是一个完整的论证观点"] * 10)
        skeptic = MockAgent("怀疑者", ["我对此观点有质疑和不同看法"] * 10)
        
        manager = DebateManager(logician, skeptic, "测试话题", max_rounds=2)
        
        # 开始辩论
        manager.start_debate()
        
        # 进行多轮直到终止
        while manager.state == DebateState.ACTIVE:
            manager.process_round()
        
        assert manager.state == DebateState.COMPLETED
        assert manager.termination_reason == TerminationReason.MAX_ROUNDS_REACHED
        assert manager.current_round > manager.max_rounds
    
    def test_pause_and_resume_debate(self):
        """测试暂停和恢复辩论"""
        manager = DebateManager(topic="测试")
        manager._change_state(DebateState.ACTIVE)
        
        # 暂停
        result = manager.pause_debate()
        assert result is True
        assert manager.state == DebateState.PAUSED
        
        # 恢复
        result = manager.resume_debate()
        assert result is True
        assert manager.state == DebateState.ACTIVE
        
        # 测试无效操作 - 创建新的manager来测试PREPARING状态
        new_manager = DebateManager(topic="测试")  # 新manager默认是PREPARING状态
        assert new_manager.pause_debate() is False  # 准备状态不能暂停
        
        # 测试COMPLETED状态不能恢复
        manager._change_state(DebateState.COMPLETED)
        assert manager.resume_debate() is False  # 已完成状态不能恢复
    
    def test_end_debate_manually(self):
        """测试手动结束辩论"""
        manager = DebateManager(topic="测试")
        manager._change_state(DebateState.ACTIVE)
        
        # 记录完成回调
        completion_reasons = []
        def on_debate_complete(reason):
            completion_reasons.append(reason)
        manager.on_debate_complete = on_debate_complete
        
        result = manager.end_debate()
        
        assert result is True
        assert manager.state == DebateState.COMPLETED
        assert manager.termination_reason == TerminationReason.USER_TERMINATED
        assert len(completion_reasons) == 1
        assert completion_reasons[0] == TerminationReason.USER_TERMINATED
    
    def test_get_debate_status(self):
        """测试获取辩论状态"""
        logician = MockAgent("逻辑者")
        skeptic = MockAgent("怀疑者")
        
        manager = DebateManager(logician, skeptic, "AI伦理", max_rounds=8)
        manager.current_round = 3
        
        status = manager.get_debate_status()
        
        assert status["state"] == "preparing"
        assert status["topic"] == "AI伦理"
        assert status["current_round"] == 3
        assert status["max_rounds"] == 8
        assert status["current_speaker"] == "逻辑者"
        assert status["total_messages"] == 0
        assert status["termination_reason"] is None
        assert "started_at" in status
        assert "duration" in status
        assert status["participants"] == ["逻辑者", "怀疑者"]
    
    def test_get_debate_summary(self):
        """测试获取辩论总结"""
        manager = DebateManager(topic="测试话题")
        
        summary = manager.get_debate_summary()
        
        assert "debate_info" in summary
        assert "metrics" in summary
        assert "rounds" in summary
        assert "conversation_stats" in summary
        
        # 验证各部分内容
        assert summary["debate_info"]["topic"] == "测试话题"
        assert isinstance(summary["metrics"], dict)
        assert isinstance(summary["rounds"], list)
        assert isinstance(summary["conversation_stats"], dict)
    
    def test_content_repetition_detection(self):
        """测试内容重复检测"""
        manager = DebateManager(topic="测试")
        
        # 测试有共同词汇的相似度计算
        similarity = manager._calculate_similarity("人工智能技术发展", "人工智能技术应用")
        assert 0 < similarity < 1
        
        # 测试完全相同
        similarity = manager._calculate_similarity("相同内容", "相同内容")
        assert similarity == 1.0
        
        # 测试完全不同
        similarity = manager._calculate_similarity("完全不同的内容", "另外一些文字")
        assert similarity < 0.5
    
    def test_response_validation(self):
        """测试回应验证"""
        manager = DebateManager()
        
        # 有效回应
        assert manager._is_valid_response("这是一个有效的回应，包含足够的内容")
        
        # 无效回应
        assert not manager._is_valid_response("")  # 空回应
        assert not manager._is_valid_response("短")  # 太短
        assert not manager._is_valid_response("   ")  # 空白
        assert not manager._is_valid_response("a" * 3000)  # 太长
    
    def test_response_quality_evaluation(self):
        """测试回应质量评估"""
        manager = DebateManager()
        
        # 高质量回应
        high_quality = "这是一个包含多种不同词汇和观点的高质量回应，展示了深入的思考和分析能力"
        score_high = manager._evaluate_response_quality(high_quality)
        assert 0.5 <= score_high <= 1.0
        
        # 低质量回应
        low_quality = "是的是的是的是的是的"
        score_low = manager._evaluate_response_quality(low_quality)
        assert score_low < score_high
        
        # 空回应
        assert manager._evaluate_response_quality("") == 0.0
    
    @patch('time.sleep')  # Mock sleep to speed up test
    def test_observation_mode(self, mock_sleep):
        """测试观察模式"""
        logician = MockAgent("逻辑者", ["AI将为人类带来巨大的改变和便利", "我坚持认为AI技术会带来积极影响"])
        skeptic = MockAgent("怀疑者", ["但是AI技术也带来了很多风险和挑战", "这些风险确实不容忽视需要谨慎对待"])
        
        manager = DebateManager(logician, skeptic, "AI发展", max_rounds=2)
        
        # 运行观察模式
        summary = manager.run_observation_mode()
        
        # 验证结果
        assert isinstance(summary, dict)
        assert "debate_info" in summary
        assert "metrics" in summary
        assert summary["debate_info"]["state"] in ["completed", "aborted"]
        
        # 验证sleep被调用（模拟思考时间）
        assert mock_sleep.called
    
    def test_error_handling_in_process_round(self):
        """测试轮次处理中的错误处理"""
        # 创建会抛出异常的mock agent
        logician = MockAgent("逻辑者")
        skeptic = Mock()
        skeptic.name = "怀疑者"
        skeptic.generate_response.side_effect = Exception("AI服务异常")
        
        manager = DebateManager(logician, skeptic, "��试话题")
        manager.start_debate()
        
        # 处理轮次应该捕获异常并终止辩论
        result = manager.process_round()
        
        assert result is False
        assert manager.state == DebateState.ABORTED
        assert manager.termination_reason == TerminationReason.SYSTEM_ERROR
    
    def test_quality_degradation_detection(self):
        """测试质量下降检测"""
        manager = DebateManager()
        
        # 添加质量逐渐下降的分数
        manager.metrics.content_quality_scores = [0.9, 0.8, 0.7, 0.2, 0.1, 0.1, 0.1]
        
        # 应该检测到质量下降
        assert manager._detect_quality_degradation() is True
        
        # 测试质量良好的情况
        manager.metrics.content_quality_scores = [0.8, 0.9, 0.8, 0.9]
        assert manager._detect_quality_degradation() is False
    
    def test_callback_system(self):
        """测试回调系统"""
        manager = DebateManager(topic="测试话题")
        
        # 设置各种回调
        events = {
            "state_changes": [],
            "round_starts": [],
            "round_completes": [],
            "messages": [],
            "debate_completes": []
        }
        
        manager.on_state_changed = lambda old, new: events["state_changes"].append((old, new))
        manager.on_round_start = lambda round_num, speaker: events["round_starts"].append((round_num, speaker))
        manager.on_round_complete = lambda round_obj: events["round_completes"].append(round_obj)
        manager.on_message_sent = lambda msg: events["messages"].append(msg)
        manager.on_debate_complete = lambda reason: events["debate_completes"].append(reason)
        
        # 进行一些操作
        manager._change_state(DebateState.ACTIVE)
        manager.end_debate()
        
        # 验证回调被调用
        assert len(events["state_changes"]) >= 1
        assert len(events["debate_completes"]) == 1
        assert events["debate_completes"][0] == TerminationReason.USER_TERMINATED


class TestDebateManagerIntegration:
    """辩论管理器集成测试"""
    
    def test_complete_debate_flow(self):
        """测试完整的辩论流程"""
        # 创建有丰富回应的mock agents
        logician_responses = [
            "AI技术将为人类带来巨大便利",
            "AI可以帮助解决气候变化问题",
            "AI在医疗领域已有重大突破"
        ]
        
        skeptic_responses = [
            "但AI也可能导致大规模失业",
            "AI系统存在偏见和不公平问题",
            "AI技术的发展速度超出了监管能力"
        ]
        
        logician = MockAgent("逻辑者", logician_responses)
        skeptic = MockAgent("怀疑者", skeptic_responses)
        
        manager = DebateManager(logician, skeptic, "AI技术的双面性", max_rounds=2)
        
        # 记录所有事件
        all_events = []
        
        def record_event(event_type, data):
            all_events.append((event_type, data))
        
        manager.on_state_changed = lambda old, new: record_event("state_change", (old, new))
        manager.on_round_start = lambda round_num, speaker: record_event("round_start", (round_num, speaker))
        manager.on_round_complete = lambda round_obj: record_event("round_complete", round_obj.round_number)
        manager.on_message_sent = lambda msg: record_event("message", msg.sender)
        manager.on_debate_complete = lambda reason: record_event("debate_complete", reason)
        
        # 运行完整流程
        success = manager.start_debate()
        assert success
        
        # 自动进行轮次直到结束
        rounds_processed = 0
        while manager.state == DebateState.ACTIVE and rounds_processed < 10:  # 防止无限循环
            if not manager.process_round():
                break
            rounds_processed += 1
        
        # 验证最终状态
        assert manager.state in [DebateState.COMPLETED, DebateState.ABORTED]
        assert len(manager.conversation.messages) > 0
        assert manager.metrics.total_messages > 0
        assert len(manager.rounds) > 0
        
        # 验证事件记录
        state_changes = [e for e in all_events if e[0] == "state_change"]
        messages = [e for e in all_events if e[0] == "message"]
        
        assert len(state_changes) >= 1  # 至少有准备->活跃的转换
        assert len(messages) >= 2  # 至少��初始论证和一次回应
        
        # 验证辩论总结完整性
        summary = manager.get_debate_summary()
        assert summary["debate_info"]["total_messages"] == len(manager.conversation.messages)
        assert summary["metrics"]["total_messages"] == manager.metrics.total_messages
        assert len(summary["rounds"]) == len(manager.rounds)


if __name__ == "__main__":
    pytest.main([__file__])
