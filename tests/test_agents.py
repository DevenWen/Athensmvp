"""
智能体模块单元测试
测试BaseAgent、Logician和Skeptic的核心功能
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.agents.base_agent import BaseAgent
from src.agents.apollo import Apollo
from src.agents.muses import Muses
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


class TestApollo:
    """测试Apollo角色"""
    
    @pytest.fixture
    def mock_ai_client(self):
        """模拟AI客户端"""
        client = Mock(spec=AIClient)
        client.generate_response.return_value = "逻辑性回应"
        return client
    
    @pytest.fixture
    def apollo(self, mock_ai_client):
        """创建Apollo实例"""
        return Apollo("测试Apollo", mock_ai_client)
    
    def test_apollo_initialization(self, apollo):
        """测试Apollo初始化"""
        assert apollo.name == "测试Apollo"
        assert apollo.role_name == "Apollo"
        assert apollo.display_name == "Apollo"
        assert apollo.description == "Logic and reason focused AI agent"
        assert apollo.metadata["role"] == "apollo"
        assert apollo.metadata["focus"] == "logical_reasoning"
        assert apollo.metadata["approach"] == "supportive_argumentation"
    
    def test_apollo_generate_response(self, apollo, mock_ai_client):
        """测试Apollo生成回应"""
        response = apollo.generate_response("测试上下文")
        
        assert response == "逻辑性回应"
        mock_ai_client.generate_response.assert_called_once()
        
        # 检查温度参数
        call_args = mock_ai_client.generate_response.call_args
        assert call_args[1]["temperature"] <= 0.6
    
    def test_apollo_analyze_argument(self, apollo, mock_ai_client):
        """测试Apollo论证分析"""
        mock_ai_client.generate_response.return_value = "论证分析结果"
        
        result = apollo.analyze_argument("测试论证")
        assert result == "论证分析结果"
        mock_ai_client.generate_response.assert_called()
    
    def test_apollo_build_supporting_argument(self, apollo, mock_ai_client):
        """测试Apollo构建支持性论证"""
        mock_ai_client.generate_response.return_value = "支持性论证"
        
        result = apollo.build_supporting_argument("话题", "立场")
        assert result == "支持性论证"
        
        # 检查是否发送了消息
        assert len(apollo.conversation_history) == 1
        assert apollo.conversation_history[0].message_type == MessageType.ARGUMENT
    
    def test_apollo_respond_to_skepticism(self, apollo, mock_ai_client):
        """测试Apollo回应质疑"""
        mock_ai_client.generate_response.return_value = "理性回应"
        
        result = apollo.respond_to_skepticism("Muses的质疑")
        assert result == "理性回应"


class TestMuses:
    """测试Muses角色"""
    
    @pytest.fixture
    def mock_ai_client(self):
        """模拟AI客户端"""
        client = Mock(spec=AIClient)
        client.generate_response.return_value = "质疑性回应"
        return client
    
    @pytest.fixture
    def muses(self, mock_ai_client):
        """创建Muses实例"""
        return Muses("测试Muses", mock_ai_client)
    
    def test_muses_initialization(self, muses):
        """测试Muses初始化"""
        assert muses.name == "测试Muses"
        assert muses.role_name == "Muses"
        assert muses.display_name == "Muses"
        assert muses.description == "Creative and challenging AI agent"
        assert muses.metadata["role"] == "muses"
        assert muses.metadata["focus"] == "critical_thinking"
        assert muses.metadata["approach"] == "questioning_challenging"
    
    def test_muses_generate_response(self, muses, mock_ai_client):
        """测试Muses生成回应"""
        response = muses.generate_response("测试上下文")
        
        assert response == "质疑性回应"
        mock_ai_client.generate_response.assert_called_once()
        
        # 检查温度参数范围
        call_args = mock_ai_client.generate_response.call_args
        temperature = call_args[1]["temperature"]
        assert 0.6 <= temperature <= 0.8
    
    def test_muses_challenge_argument(self, muses, mock_ai_client):
        """测试Muses质疑论证"""
        mock_ai_client.generate_response.return_value = "质疑内容"
        
        result = muses.challenge_argument("论证内容")
        assert result == "质疑内容"
        
        # 检查是否发送了消息
        assert len(muses.conversation_history) == 1
        assert muses.conversation_history[0].message_type == MessageType.COUNTER
    
    def test_muses_find_contradictions(self, muses, mock_ai_client):
        """测试Muses寻找矛盾"""
        mock_ai_client.generate_response.return_value = "矛盾分析"
        
        statements = ["陈述1", "陈述2", "陈述3"]
        result = muses.find_contradictions(statements)
        assert result == "矛盾分析"
    
    def test_muses_propose_counterexamples(self, muses, mock_ai_client):
        """测试Muses提出反例"""
        mock_ai_client.generate_response.return_value = "反例分析"
        
        result = muses.propose_counterexamples("一般性声明")
        assert result == "反例分析"
        
        # 检查是否发送了消息
        assert len(muses.conversation_history) == 1
        assert muses.conversation_history[0].message_type == MessageType.COUNTER
    
    def test_muses_respond_to_logic(self, muses, mock_ai_client):
        """测试Muses回应逻辑论证"""
        mock_ai_client.generate_response.return_value = "批判性回应"
        
        result = muses.respond_to_logic("Apollo的论证")
        assert result == "批判性回应"


class TestApolloMusesInteraction:
    """测试Apollo和Muses之间的交互"""
    
    @pytest.fixture
    def mock_ai_client(self):
        """模拟AI客户端"""
        client = Mock(spec=AIClient)
        return client
    
    @pytest.fixture
    def new_agents(self, mock_ai_client):
        """创建新的测试智能体对"""
        apollo = Apollo("Apollo", mock_ai_client)
        muses = Muses("Muses", mock_ai_client)
        return apollo, muses
    
    def test_new_message_exchange(self, new_agents):
        """测试Apollo和Muses的消息交换"""
        apollo, muses = new_agents
        
        # Apollo发送消息
        msg1 = apollo.send_message("逻辑论证", "Muses")
        
        # Muses接收消息
        muses.receive_message(msg1)
        
        # Muses回应
        msg2 = muses.send_message("质疑回应", "Apollo")
        
        # Apollo接收回应
        apollo.receive_message(msg2)
        
        # 验证对话历史
        assert len(apollo.conversation_history) == 2
        assert len(muses.conversation_history) == 2
        
        # 验证消息内容
        assert apollo.conversation_history[0].content == "逻辑论证"
        assert apollo.conversation_history[1].content == "质疑回应"
        assert muses.conversation_history[0].content == "逻辑论证"
        assert muses.conversation_history[1].content == "质疑回应"


class TestLetterFormat:
    """测试书信格式功能"""
    
    def test_message_letter_format(self):
        """测试消息书信格式化"""
        msg = Message(
            content="这是一条测试消息",
            sender="Apollo",
            recipient="Muses",
            message_type=MessageType.ARGUMENT
        )
        
        letter_format = msg.format_as_letter()
        
        assert "致 Muses，" in letter_format
        assert "这是一条测试消息" in letter_format
        assert "此致\nApollo" in letter_format
    
    def test_letter_greeting_apollo_to_muses(self):
        """测试Apollo给Muses的问候语"""
        msg = Message(content="测试", sender="Apollo", message_type=MessageType.ARGUMENT)
        greeting = msg.get_letter_greeting("Muses")
        assert greeting == "致 Muses，"
    
    def test_letter_greeting_muses_to_apollo(self):
        """测试Muses给Apollo的问候语"""
        msg = Message(content="测试", sender="Muses", message_type=MessageType.COUNTER)
        greeting = msg.get_letter_greeting("Apollo")
        assert greeting == "致 Apollo，"
    
    def test_letter_greeting_user(self):
        """测试用户的问候语"""
        msg = Message(content="测试", sender="用户", message_type=MessageType.USER_INPUT)
        greeting = msg.get_letter_greeting("Apollo")
        assert greeting == "致 Apollo，"
    
    def test_letter_signature(self):
        """测试书信签名"""
        msg = Message(content="测试", sender="Apollo", message_type=MessageType.ARGUMENT)
        signature = msg.get_letter_signature()
        assert signature == "此致\nApollo"
