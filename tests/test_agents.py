"""
智能体模块单元测试
测试BaseAgent、Logician和Skeptic的核心功能
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.agents.base_agent import BaseAgent
from src.agents.logician import Logician
from src.agents.skeptic import Skeptic
from src.core.ai_client import AIClient
from src.core.message import Message, MessageType


class TestMessage:
    """测试Message类"""
    
    def test_message_creation(self):
        """测试消息创建"""
        msg = Message(content="测试内容", sender="发送者", recipient="接收者", message_type=MessageType.GENERAL)
        
        assert msg.content == "测试内容"
        assert msg.sender == "发送者"
        assert msg.recipient == "接收者"
        assert msg.message_type == MessageType.GENERAL
        assert isinstance(msg.timestamp, datetime)
        assert isinstance(msg.metadata, dict)
    
    def test_message_str(self):
        """测试消息字符串表示"""
        msg = Message(content="Hello", sender="Alice", message_type=MessageType.GENERAL)
        assert str(msg) == "[Alice]: Hello"
    
    def test_message_to_dict(self):
        """测试消息转换为字典"""
        msg = Message(content="测试", sender="用户", recipient="AI", message_type=MessageType.GENERAL)
        msg_dict = msg.to_dict()
        
        assert msg_dict["content"] == "测试"
        assert msg_dict["sender"] == "用户"
        assert msg_dict["recipient"] == "AI"
        assert msg_dict["message_type"] == "general"
        assert "timestamp" in msg_dict
        assert "metadata" in msg_dict


class TestBaseAgent:
    """测试BaseAgent基础功能"""
    
    @pytest.fixture
    def mock_ai_client(self):
        """模拟AI客户端"""
        client = Mock(spec=AIClient)
        client.generate_response.return_value = "模拟回应"
        return client
    
    @pytest.fixture
    def base_agent(self, mock_ai_client):
        """创建测试用的基础智能体"""
        class TestAgent(BaseAgent):
            def generate_response(self, context="", temperature=0.7):
                prompt = self._build_prompt(context)
                return self.ai_client.generate_response(prompt, temperature)
        
        return TestAgent("测试智能体", "测试提示词", mock_ai_client)
    
    def test_agent_initialization(self, base_agent):
        """测试智能体初始化"""
        assert base_agent.name == "测试智能体"
        assert base_agent.role_prompt == "测试提示词"
        assert base_agent.is_active is True
        assert len(base_agent.conversation_history) == 0
        assert isinstance(base_agent.metadata, dict)
    
    def test_send_message(self, base_agent):
        """测试发送消息"""
        message = base_agent.send_message("测试消息", "接收者", MessageType.GENERAL)
        
        assert isinstance(message, Message)
        assert message.content == "测试消息"
        assert message.sender == "测试智能体"
        assert message.recipient == "接收者"
        assert message.message_type == MessageType.GENERAL
        assert len(base_agent.conversation_history) == 1
    
    def test_receive_message(self, base_agent):
        """测试接收消息"""
        msg = Message(content="收到的消息", sender="其他人", message_type=MessageType.GENERAL)
        base_agent.receive_message(msg)
        
        assert len(base_agent.conversation_history) == 1
        assert base_agent.conversation_history[0] == msg
    
    def test_receive_own_message(self, base_agent):
        """测试不会接收自己的消息"""
        msg = Message(content="自己的消息", sender="测试智能体", message_type=MessageType.GENERAL)
        base_agent.receive_message(msg)
        
        assert len(base_agent.conversation_history) == 0
    
    def test_conversation_history(self, base_agent):
        """测试对话历史管理"""
        # 发送消息
        base_agent.send_message("消息1")
        base_agent.send_message("消息2")
        
        # 接收消息
        msg = Message(content="收到的消息", sender="其他人", message_type=MessageType.GENERAL)
        base_agent.receive_message(msg)
        
        history = base_agent.get_conversation_history()
        assert len(history) == 3
        
        # 测试限制数量
        recent = base_agent.get_conversation_history(limit=2)
        assert len(recent) == 2
    
    def test_conversation_context(self, base_agent):
        """测试对话上下文生成"""
        base_agent.send_message("你好")
        msg = Message(content="回复", sender="其他人", message_type=MessageType.GENERAL)
        base_agent.receive_message(msg)
        
        context = base_agent.get_conversation_context()
        assert "测试智能体: 你好" in context
        assert "其他人: 回复" in context
    
    def test_reset_conversation(self, base_agent):
        """测试重置对话"""
        base_agent.send_message("测试")
        assert len(base_agent.conversation_history) == 1
        
        base_agent.reset_conversation()
        assert len(base_agent.conversation_history) == 0
    
    def test_agent_status(self, base_agent):
        """测试智能体状态"""
        base_agent.send_message("状态测试")
        status = base_agent.get_status()
        
        assert status["name"] == "测试智能体"
        assert status["is_active"] is True
        assert status["message_count"] == 1
        assert "last_message_time" in status
        assert "metadata" in status
    
    def test_set_active(self, base_agent):
        """测试设置激活状态"""
        base_agent.set_active(False)
        assert base_agent.is_active is False
        
        base_agent.set_active(True)
        assert base_agent.is_active is True


class TestLogician:
    """测试Logician逻辑者角色"""
    
    @pytest.fixture
    def mock_ai_client(self):
        """模拟AI客户端"""
        client = Mock(spec=AIClient)
        client.generate_response.return_value = "逻辑性回应"
        return client
    
    @pytest.fixture
    def logician(self, mock_ai_client):
        """创建逻辑者实例"""
        return Logician("测试逻辑者", mock_ai_client)
    
    def test_logician_initialization(self, logician):
        """测试逻辑者初始化"""
        assert logician.name == "测试逻辑者"
        assert logician.metadata["role"] == "logician"
        assert logician.metadata["focus"] == "logical_reasoning"
        assert logician.metadata["approach"] == "supportive_argumentation"
    
    def test_generate_response(self, logician, mock_ai_client):
        """测试生成回应"""
        response = logician.generate_response("测试上下文")
        
        assert response == "逻辑性回应"
        mock_ai_client.generate_response.assert_called_once()
        
        # 检查温度参数
        call_args = mock_ai_client.generate_response.call_args
        assert call_args[1]["temperature"] <= 0.6
    
    def test_analyze_argument(self, logician, mock_ai_client):
        """测试论证分析"""
        mock_ai_client.generate_response.return_value = "论证分析结果"
        
        result = logician.analyze_argument("测试论证")
        assert result == "论证分析结果"
        mock_ai_client.generate_response.assert_called()
    
    def test_build_supporting_argument(self, logician, mock_ai_client):
        """测试构建支持性论证"""
        mock_ai_client.generate_response.return_value = "支持性论证"
        
        result = logician.build_supporting_argument("话题", "立场")
        assert result == "支持性论证"
        
        # 检查是否发送了消息
        assert len(logician.conversation_history) == 1
        assert logician.conversation_history[0].message_type == MessageType.ARGUMENT
    
    def test_respond_to_skepticism(self, logician, mock_ai_client):
        """测试回应怀疑"""
        mock_ai_client.generate_response.return_value = "理性回应"
        
        result = logician.respond_to_skepticism("怀疑质疑")
        assert result == "理性回应"


class TestSkeptic:
    """测试Skeptic怀疑者角色"""
    
    @pytest.fixture
    def mock_ai_client(self):
        """模拟AI客户端"""
        client = Mock(spec=AIClient)
        client.generate_response.return_value = "质疑性回应"
        return client
    
    @pytest.fixture
    def skeptic(self, mock_ai_client):
        """创建怀疑者实例"""
        return Skeptic("测试怀疑者", mock_ai_client)
    
    def test_skeptic_initialization(self, skeptic):
        """测试怀疑者初始化"""
        assert skeptic.name == "测试怀疑者"
        assert skeptic.metadata["role"] == "skeptic"
        assert skeptic.metadata["focus"] == "critical_thinking"
        assert skeptic.metadata["approach"] == "questioning_challenging"
    
    def test_generate_response(self, skeptic, mock_ai_client):
        """测试生成回应"""
        response = skeptic.generate_response("测试上下文")
        
        assert response == "质疑性回应"
        mock_ai_client.generate_response.assert_called_once()
        
        # 检查温度参数范围
        call_args = mock_ai_client.generate_response.call_args
        temperature = call_args[1]["temperature"]
        assert 0.6 <= temperature <= 0.8
    
    def test_challenge_argument(self, skeptic, mock_ai_client):
        """测试质疑论证"""
        mock_ai_client.generate_response.return_value = "质疑内容"
        
        result = skeptic.challenge_argument("论证内容")
        assert result == "质疑内容"
        
        # 检查是否发送了消息
        assert len(skeptic.conversation_history) == 1
        assert skeptic.conversation_history[0].message_type == MessageType.COUNTER
    
    def test_find_contradictions(self, skeptic, mock_ai_client):
        """测试寻找矛盾"""
        mock_ai_client.generate_response.return_value = "矛盾分析"
        
        statements = ["陈述1", "陈述2", "陈述3"]
        result = skeptic.find_contradictions(statements)
        assert result == "矛盾分析"
    
    def test_propose_counterexamples(self, skeptic, mock_ai_client):
        """测试提出反例"""
        mock_ai_client.generate_response.return_value = "反例分析"
        
        result = skeptic.propose_counterexamples("一般性声明")
        assert result == "反例分析"
        
        # 检查是否发送了消息
        assert len(skeptic.conversation_history) == 1
        assert skeptic.conversation_history[0].message_type == MessageType.COUNTER
    
    def test_respond_to_logic(self, skeptic, mock_ai_client):
        """测试回应逻辑论证"""
        mock_ai_client.generate_response.return_value = "批判性回应"
        
        result = skeptic.respond_to_logic("逻辑论证")
        assert result == "批判性回应"


class TestAgentInteraction:
    """测试智能体间的交互"""
    
    @pytest.fixture
    def mock_ai_client(self):
        """模拟AI客户端"""
        client = Mock(spec=AIClient)
        return client
    
    @pytest.fixture
    def agents(self, mock_ai_client):
        """创建测试智能体对"""
        logician = Logician("逻辑者", mock_ai_client)
        skeptic = Skeptic("怀疑者", mock_ai_client)
        return logician, skeptic
    
    def test_message_exchange(self, agents):
        """测试消息交换"""
        logician, skeptic = agents
        
        # 逻辑者发送消息
        msg1 = logician.send_message("逻辑论证", "怀疑者")
        
        # 怀疑者接收消息
        skeptic.receive_message(msg1)
        
        # 怀疑者回应
        msg2 = skeptic.send_message("质疑回应", "逻辑者")
        
        # 逻辑者接收回应
        logician.receive_message(msg2)
        
        # 验证对话历史
        assert len(logician.conversation_history) == 2
        assert len(skeptic.conversation_history) == 2
        
        # 验证消息内容
        assert logician.conversation_history[0].content == "逻辑论证"
        assert logician.conversation_history[1].content == "质疑回应"
        assert skeptic.conversation_history[0].content == "逻辑论证"
        assert skeptic.conversation_history[1].content == "质疑回应"