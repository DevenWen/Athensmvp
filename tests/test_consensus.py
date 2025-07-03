"""
共识检测功能的单元测试
测试AI协商机制和对话整理功能
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from src.core.debate_manager import DebateManager
from src.core.debate_states import ConsensusState, TerminationReason, DebateState
from src.core.conversation_summarizer import ConversationSummarizer
from src.core.message import Message, MessageType
from src.core.conversation import Conversation


class TestConsensusDetection(unittest.TestCase):
    """测试共识检测功能"""
    
    def setUp(self):
        """测试前的设置"""
        # 创建Mock的智能体
        self.mock_logician = Mock()
        self.mock_logician.name = "Logician"
        self.mock_skeptic = Mock()
        self.mock_skeptic.name = "Skeptic"
        
        # 创建辩论管理器
        self.debate_manager = DebateManager(
            apollo=self.mock_logician,
            muses=self.mock_skeptic,
            topic="测试话题",
            max_rounds=5
        )
    
    def test_detect_agreement_keywords_chinese(self):
        """测试中文同意关键词检测"""
        test_cases = [
            ("我同意你的结论", True),
            ("同意你的观点", True),
            ("我赞同你的观点", True),
            ("你说得对", True),
            ("我认为你是对的", True),
            ("我接受", True),
            ("我不同意", False),
            ("这个观点有问题", False),
            ("普通的对话内容", False),
            ("", False)
        ]
        
        for content, expected in test_cases:
            with self.subTest(content=content):
                result = self.debate_manager.detect_agreement_keywords(content)
                self.assertEqual(result, expected, f"Failed for content: '{content}'")
    
    def test_detect_agreement_keywords_english(self):
        """测试英文同意关键词检测"""
        test_cases = [
            ("I agree with your conclusion", True),
            ("I agree", True),
            ("You are right", True),
            ("I accept your argument", True),
            ("I concur", True),
            ("You make a valid point", True),
            ("I'm convinced", True),
            ("I disagree", False),
            ("This is wrong", False),
            ("Regular conversation", False),
            ("", False)
        ]
        
        for content, expected in test_cases:
            with self.subTest(content=content):
                result = self.debate_manager.detect_agreement_keywords(content)
                self.assertEqual(result, expected, f"Failed for content: '{content}'")
    
    def test_consensus_state_management(self):
        """测试协商状态管理"""
        # 初始状态应该��ONGOING
        self.assertEqual(self.debate_manager.get_consensus_status(), ConsensusState.ONGOING)
        
        # 更新状态
        self.debate_manager.update_consensus_state(ConsensusState.NEGOTIATING)
        self.assertEqual(self.debate_manager.get_consensus_status(), ConsensusState.NEGOTIATING)
        
        # 更新到共识达成
        self.debate_manager.update_consensus_state(ConsensusState.CONSENSUS_REACHED)
        self.assertEqual(self.debate_manager.get_consensus_status(), ConsensusState.CONSENSUS_REACHED)
    
    def test_check_consensus_with_agreement_message(self):
        """测试包含同意消息时的共识检测"""
        # 添加一些消息到对话中
        message1 = Message(
            content="这是第一条消息",
            sender="Logician",
            recipient="Skeptic",
            message_type=MessageType.ARGUMENT
        )
        message2 = Message(
            content="我同意你的结论",
            sender="Skeptic", 
            recipient="Logician",
            message_type=MessageType.COUNTER
        )
        
        self.debate_manager.conversation.add_message(message1)
        self.debate_manager.conversation.add_message(message2)
        
        # 检查共识
        result = self.debate_manager.check_consensus()
        self.assertTrue(result)
        self.assertEqual(self.debate_manager.get_consensus_status(), ConsensusState.CONSENSUS_REACHED)
    
    def test_check_consensus_without_agreement(self):
        """测试不包含同意消息时的共识检测"""
        # 添加不包含同意的消息
        message1 = Message(
            content="这是第一条消息",
            sender="Logician",
            recipient="Skeptic",
            message_type=MessageType.ARGUMENT
        )
        message2 = Message(
            content="我觉得这个观点有问题",
            sender="Skeptic",
            recipient="Logician", 
            message_type=MessageType.COUNTER
        )
        
        self.debate_manager.conversation.add_message(message1)
        self.debate_manager.conversation.add_message(message2)
        
        # 检查共识
        result = self.debate_manager.check_consensus()
        self.assertFalse(result)
        self.assertEqual(self.debate_manager.get_consensus_status(), ConsensusState.ONGOING)
    
    def test_check_consensus_with_empty_conversation(self):
        """测试空对话的共识检测"""
        result = self.debate_manager.check_consensus()
        self.assertFalse(result)
    
    @patch('src.core.debate_manager.logger')
    def test_consensus_detection_logging(self, mock_logger):
        """测试共识检测的日志记录"""
        # 先添加一条普通消息
        self.debate_manager.conversation.add_message(Message(
            content="这是一个初始论点",
            sender="Logician",
            recipient="Skeptic",
            message_type=MessageType.ARGUMENT
        ))
        # 再添加包含同意的消息
        message = Message(
            content="我同意你的结论",
            sender="Skeptic",
            recipient="Logician",
            message_type=MessageType.COUNTER
        )
        self.debate_manager.conversation.add_message(message)
        
        # 检查共识
        self.debate_manager.check_consensus()
        
        # 验证日志调用
        mock_logger.info.assert_called()
    
    def test_debate_status_includes_consensus(self):
        """测试辩论状态包含共识信息"""
        status = self.debate_manager.get_debate_status()
        self.assertIn("consensus_state", status)
        self.assertEqual(status["consensus_state"], ConsensusState.ONGOING.value)
        
        # 更新共识状态后再检查
        self.debate_manager.update_consensus_state(ConsensusState.CONSENSUS_REACHED)
        status = self.debate_manager.get_debate_status()
        self.assertEqual(status["consensus_state"], ConsensusState.CONSENSUS_REACHED.value)


class TestConversationSummarizer(unittest.TestCase):
    """测试对话整理功能"""
    
    def setUp(self):
        """测试前的设置"""
        self.conversation = Conversation("test_conversation")
        self.summarizer = ConversationSummarizer(self.conversation)
        
        # 添加一些测试消息
        self._add_test_messages()
    
    def _add_test_messages(self):
        """添加测试消息"""
        messages = [
            Message(
                content="人工智能的发展无疑将对���会结构、就业市场和伦理观念带来前所未有的巨大变革。",
                sender="Logician",
                recipient="Skeptic",
                message_type=MessageType.ARGUMENT
            ),
            Message(
                content="然而，我们绝不能忽视AI技术滥用可能带来的严重风险，例如大规模失业、算法偏见以及对个人隐私的侵犯等。",
                sender="Skeptic", 
                recipient="Logician",
                message_type=MessageType.COUNTER
            ),
            Message(
                content="你提出的这些风险确实非常关键，我完全同意我们必须在推动AI发展的同时，建立强有力的监管框架和伦理准则来应对这些挑战。",
                sender="Logician",
                recipient="Skeptic", 
                message_type=MessageType.CLARIFICATION
            )
        ]
        
        for message in messages:
            self.conversation.add_message(message)
    
    def test_extract_participants(self):
        """测试参与者信息提取"""
        participants = self.summarizer._extract_participants()
        
        self.assertEqual(len(participants), 2)
        self.assertIn("Logician", participants)
        self.assertIn("Skeptic", participants)
        
        # 检查统计信息
        logician_info = participants["Logician"]
        self.assertEqual(logician_info["message_count"], 2)
        self.assertEqual(logician_info["name"], "Logician")
    
    def test_extract_key_points(self):
        """测试关键论点提取"""
        # 在一个空的 conversation 中，应该返回空列表
        empty_conversation = Conversation("empty")
        empty_summarizer = ConversationSummarizer(empty_conversation)
        self.assertEqual(empty_summarizer.extract_key_points(), [])

        # 在有内容的 conversation 中，应该返回非空列表
        key_points = self.summarizer.extract_key_points()
        
        self.assertIsInstance(key_points, list)
        self.assertGreater(len(key_points), 0)
        
        # 检查关键论点格式
        for point in key_points:
            self.assertIsInstance(point, str)
            self.assertIn("**", point)  # 应该包含markdown格式
    
    def test_generate_conclusion_with_agreement(self):
        """测试包含同意表达的结论生成"""
        conclusion = self.summarizer.generate_conclusion()
        
        self.assertIsInstance(conclusion, str)
        self.assertGreater(len(conclusion), 0)
        # 由于最后一条消息包含"我同意"，应该检测到共识
        self.assertIn("共识", conclusion)
    
    def test_generate_conclusion_without_agreement(self):
        """测试不包含同意表达的结论生成"""
        # 创建新的对话，不包含同意表达
        conversation = Conversation("test_no_agreement")
        conversation.add_message(Message(
            content="这是一个非常复杂的论证，需要我们从多个角度进行深入的探讨和分析。",
            sender="Logician",
            recipient="Skeptic",
            message_type=MessageType.ARGUMENT
        ))
        conversation.add_message(Message(
            content="我承认这个问题的复杂性，但我认为你的论证中存在一些逻辑上的跳跃，需要进一步澄清。",
            sender="Skeptic",
            recipient="Logician", 
            message_type=MessageType.COUNTER
        ))
        
        summarizer = ConversationSummarizer(conversation)
        conclusion = summarizer.generate_conclusion()
        
        self.assertIsInstance(conclusion, str)
        self.assertGreater(len(conclusion), 0)
    
    def test_summarize_debate(self):
        """测试辩论总结生成"""
        summary = self.summarizer.summarize_debate()
        
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)
        self.assertIn("# 辩论总结", summary)
        self.assertIn("参与者", summary)
        self.assertIn("关键论点", summary)
        self.assertIn("结论", summary)
    
    def test_format_as_markdown(self):
        """测试markdown格式化"""
        markdown = self.summarizer.format_as_markdown()
        
        self.assertIsInstance(markdown, str)
        self.assertGreater(len(markdown), 0)
        
        # 检查markdown格式元素
        self.assertIn("# Athens辩论记录", markdown)
        self.assertIn("## 基本信息", markdown)
        self.assertIn("## 参与者信息", markdown)
        self.assertIn("## 完整对话记录", markdown)
    
    def test_empty_conversation_handling(self):
        """测试空对话的处理"""
        empty_conversation = Conversation("empty")
        empty_summarizer = ConversationSummarizer(empty_conversation)
        
        # 应该能够处理空对话而不出错
        summary = empty_summarizer.summarize_debate()
        self.assertIsInstance(summary, str)
        
        markdown = empty_summarizer.format_as_markdown() 
        self.assertIsInstance(markdown, str)
        
        conclusion = empty_summarizer.generate_conclusion()
        self.assertEqual(conclusion, "无对话内容")


class TestConsensusIntegration(unittest.TestCase):
    """测试共识检测的集成功能"""
    
    def setUp(self):
        """测试前的设置"""
        self.mock_logician = Mock()
        self.mock_logician.name = "Logician"
        self.mock_skeptic = Mock()
        self.mock_skeptic.name = "Skeptic"
        
        self.debate_manager = DebateManager(
            apollo=self.mock_logician,
            muses=self.mock_skeptic,
            topic="集成测试话题"
        )
    
    @patch('src.core.debate_manager.logger')
    def test_consensus_triggers_termination(self, mock_logger):
        """测试共识检测触发辩论终止"""
        # 设置辩论状态为ACTIVE
        self.debate_manager._change_state(DebateState.ACTIVE)
        
        # 先添加一条普通消息
        self.debate_manager.conversation.add_message(Message(
            content="这是一个初始论点",
            sender="Logician",
            recipient="Skeptic",
            message_type=MessageType.ARGUMENT
        ))
        # 再添加包含同意的消息
        message = Message(
            content="经过深入思考，我同意你的结论",
            sender="Skeptic",
            recipient="Logician",
            message_type=MessageType.COUNTER
        )
        self.debate_manager.conversation.add_message(message)
        
        # 调用检查终止条件的方法
        should_continue = self.debate_manager._check_continuation_conditions()
        
        # 应该不继续（因为达成共识）
        self.assertFalse(should_continue)
        
        # 辩论应该已完成
        self.assertEqual(self.debate_manager.state, DebateState.COMPLETED)
        self.assertEqual(self.debate_manager.termination_reason, TerminationReason.CONSENSUS_REACHED)
    
    def test_no_false_positive_consensus(self):
        """测试不应该误判共识"""
        # 设置辩论状态为ACTIVE
        self.debate_manager._change_state(DebateState.ACTIVE)
        
        # 添加不包含同意的消息
        message = Message(
            content="我觉得这个论点还需要更多证据支持",
            sender="Skeptic",
            recipient="Logician",
            message_type=MessageType.COUNTER
        )
        self.debate_manager.conversation.add_message(message)
        
        # 调用检查终止条件的方法
        should_continue = self.debate_manager._check_continuation_conditions()
        
        # 应该继续（没有达成共识）
        self.assertTrue(should_continue)
        
        # 辩论状态应该保持ACTIVE
        self.assertEqual(self.debate_manager.state, DebateState.ACTIVE)
        self.assertIsNone(self.debate_manager.termination_reason)


if __name__ == '__main__':
    unittest.main()
