"""
基础智能体抽象类
定义所有AI智能体的共同接口和行为
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.core.ai_client import AIClient


class Message:
    """消息类，用于智能体间的通信"""
    
    def __init__(self, content: str, sender: str, recipient: Optional[str] = None, 
                 message_type: str = "general", timestamp: Optional[datetime] = None):
        self.content = content
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.timestamp = timestamp or datetime.now()
        self.metadata: Dict[str, Any] = {}
    
    def __str__(self) -> str:
        return f"[{self.sender}]: {self.content}"
    
    def to_dict(self) -> Dict[str, Any]:
        """将消息转换为字典格式"""
        return {
            "content": self.content,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class BaseAgent(ABC):
    """
    基础智能体抽象类
    定义所有AI智能体的共同接口和行为
    """
    
    def __init__(self, name: str, role_prompt: str, ai_client: AIClient):
        self.name = name
        self.role_prompt = role_prompt
        self.ai_client = ai_client
        self.conversation_history: List[Message] = []
        self.is_active = True
        self.metadata: Dict[str, Any] = {}
    
    def send_message(self, content: str, recipient: Optional[str] = None, 
                    message_type: str = "general") -> Message:
        """
        发送消息
        
        Args:
            content: 消息内容
            recipient: 接收者（可选）
            message_type: 消息类型
            
        Returns:
            创建的消息对象
        """
        message = Message(
            content=content,
            sender=self.name,
            recipient=recipient,
            message_type=message_type
        )
        
        # 将消息添加到对话历史
        self.conversation_history.append(message)
        
        return message
    
    def receive_message(self, message: Message) -> None:
        """
        接收消息并添加到对话历史
        
        Args:
            message: 接收到的消息
        """
        if message.sender != self.name:  # 避免接收自己的消息
            self.conversation_history.append(message)
    
    @abstractmethod
    def generate_response(self, context: str = "", temperature: float = 0.7) -> str:
        """
        生成回应（抽象方法，子类必须实现）
        
        Args:
            context: 上下文信息
            temperature: 生成温度参数
            
        Returns:
            生成的回应内容
        """
        pass
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Message]:
        """
        获取对话历史
        
        Args:
            limit: 返回消息数量限制
            
        Returns:
            消息列表
        """
        if limit is None:
            return self.conversation_history.copy()
        else:
            return self.conversation_history[-limit:]
    
    def get_conversation_context(self, limit: int = 10) -> str:
        """
        获取对话上下文字符串
        
        Args:
            limit: 包含的消息数量限制
            
        Returns:
            格式化的对话上下文
        """
        recent_messages = self.get_conversation_history(limit)
        context_lines = []
        
        for msg in recent_messages:
            context_lines.append(f"{msg.sender}: {msg.content}")
        
        return "\n".join(context_lines)
    
    def reset_conversation(self) -> None:
        """重置对话历史"""
        self.conversation_history.clear()
    
    def set_active(self, active: bool) -> None:
        """设置智能体激活状态"""
        self.is_active = active
    
    def get_status(self) -> Dict[str, Any]:
        """获取智能体状态信息"""
        return {
            "name": self.name,
            "is_active": self.is_active,
            "message_count": len(self.conversation_history),
            "last_message_time": (
                self.conversation_history[-1].timestamp.isoformat() 
                if self.conversation_history else None
            ),
            "metadata": self.metadata
        }
    
    def _build_prompt(self, context: str = "") -> str:
        """
        构建完整的提示词
        
        Args:
            context: 额外的上下文信息
            
        Returns:
            完整的提示词
        """
        prompt_parts = [self.role_prompt]
        
        # 添加对话历史
        conversation_context = self.get_conversation_context()
        if conversation_context:
            prompt_parts.append(f"\n\n## 对话历史:\n{conversation_context}")
        
        # 添加额外上下文
        if context:
            prompt_parts.append(f"\n\n## 当前上下文:\n{context}")
        
        prompt_parts.append("\n\n请根据你的角色特征生成回应:")
        
        return "".join(prompt_parts)
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', active={self.is_active})"
    
    def __repr__(self) -> str:
        return self.__str__()