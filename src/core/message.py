"""
消息结构定义模块
定义Athens系统的标准化消息格式和类型
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Union
import json


class MessageType(Enum):
    """消息类型枚举"""
    ARGUMENT = "argument"          # 论证陈述
    COUNTER = "counter"            # 反驳质疑  
    CLARIFICATION = "clarification" # 澄清说明
    SUMMARY = "summary"            # 总结概述
    USER_INPUT = "user_input"      # 用户输入
    SYSTEM = "system"              # 系统消息
    GENERAL = "general"            # 一般消息


@dataclass
class Message:
    """
    标准化消息结构
    支持智能体间的结构化通信和上下文管理
    """
    
    # 核心字段
    content: str
    sender: str
    message_type: MessageType
    
    # 可选字段（有默认值）
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    recipient: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    references: List[str] = field(default_factory=list)  # 引用的消息ID
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """后初始化处理"""
        # 确保message_type是MessageType枚举
        if isinstance(self.message_type, str):
            try:
                self.message_type = MessageType(self.message_type)
            except ValueError:
                self.message_type = MessageType.GENERAL
    
    def add_reference(self, message_id: str) -> None:
        """添加消息引用"""
        if message_id not in self.references:
            self.references.append(message_id)
    
    def remove_reference(self, message_id: str) -> None:
        """移除消息引用"""
        if message_id in self.references:
            self.references.remove(message_id)
    
    def set_context(self, key: str, value: Any) -> None:
        """设置上下文信息"""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """获取上下文信息"""
        return self.context.get(key, default)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """设置元数据"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取元数据"""
        return self.metadata.get(key, default)
    
    def is_reply_to(self, message_id: str) -> bool:
        """检查是否是对某条消息的回复"""
        return message_id in self.references
    
    def has_references(self) -> bool:
        """检查是否有引用其他消息"""
        return len(self.references) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于序列化）"""
        return {
            "id": self.id,
            "content": self.content,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "references": self.references,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """从字典创建消息对象（用于反序列化）"""
        # 处理时间戳
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        
        # 处理消息类型
        if isinstance(data.get("message_type"), str):
            data["message_type"] = MessageType(data["message_type"])
        
        # 确保字段存在
        data.setdefault("context", {})
        data.setdefault("references", [])
        data.setdefault("metadata", {})
        
        return cls(**data)
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """从JSON字符串创建消息对象"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def clone(self, **overrides) -> "Message":
        """克隆消息对象，可选择性覆盖字段"""
        data = self.to_dict()
        data.update(overrides)
        # 为克隆的消息生成新ID（除非明确指定）
        if "id" not in overrides:
            data["id"] = str(uuid.uuid4())
        return self.from_dict(data)
    
    def get_display_preview(self, max_length: int = 50) -> str:
        """获取用于显示的消息预览"""
        preview = self.content
        if len(preview) > max_length:
            preview = preview[:max_length-3] + "..."
        return f"[{self.sender}][{self.message_type.value}]: {preview}"
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"[{self.sender}]: {self.content}"
    
    def __repr__(self) -> str:
        """调试用字符串表示"""
        return (f"Message(id='{self.id[:8]}...', sender='{self.sender}', "
                f"type={self.message_type.value}, content='{self.content[:30]}...')")
    
    def format_as_letter(self, recipient: str = None) -> str:
        """
        将消息格式化为书信格式
        
        Args:
            recipient: 接收者名称，如果为None则使用消息中的recipient
            
        Returns:
            书信格式的消息内容
        """
        if recipient is None:
            recipient = self.recipient
        
        if not recipient:
            # 如果没有指定接收者，返回原始内容
            return self.content
        
        # 生成书信格式
        greeting = self.get_letter_greeting(recipient)
        signature = self.get_letter_signature()
        
        formatted_content = f"{greeting}\n\n{self.content}\n\n{signature}"
        return formatted_content
    
    def get_letter_greeting(self, recipient: str) -> str:
        """
        获取书信问候语
        
        Args:
            recipient: 接收者名称
            
        Returns:
            书信问候语
        """
        # 根据发送者和接收者确定问候语
        if self.sender == "Apollo" and recipient == "Muses":
            return "致 Muses，"
        elif self.sender == "Muses" and recipient == "Apollo":
            return "致 Apollo，"
        elif self.sender in ["用户", "User"]:
            if recipient in ["Apollo", "Muses"]:
                return f"致 {recipient}，"
            else:
                return "致各位，"
        else:
            # 通用格式
            return f"致 {recipient}，"
    
    def get_letter_signature(self) -> str:
        """
        获取书信签名
        
        Returns:
            书信签名
        """
        return f"此致\n{self.sender}"
    
    def add_letter_header(self, sender: str = None, recipient: str = None) -> str:
        """
        添加书信头部格式
        
        Args:
            sender: 发送者，如果为None则使用消息中的sender
            recipient: 接收者，如果为None则使用消息中的recipient
            
        Returns:
            带有书信头部的消息内容
        """
        actual_sender = sender or self.sender
        actual_recipient = recipient or self.recipient
        
        if not actual_recipient:
            return self.content
        
        # 生成头部
        greeting = f"致 {actual_recipient}，" if actual_sender != actual_recipient else ""
        
        if greeting:
            return f"{greeting}\n\n{self.content}\n\n此致\n{actual_sender}"
        else:
            return self.content


class MessageBuilder:
    """消息构建器，提供便捷的消息创建方法"""
    
    def __init__(self, sender: str):
        self.sender = sender
        self.reset()
    
    def reset(self) -> "MessageBuilder":
        """重置构建器"""
        self._content = ""
        self._recipient = None
        self._message_type = MessageType.GENERAL
        self._context = {}
        self._references = []
        self._metadata = {}
        return self
    
    def content(self, content: str) -> "MessageBuilder":
        """设置消息内容"""
        self._content = content
        return self
    
    def to(self, recipient: str) -> "MessageBuilder":
        """设置接收者"""
        self._recipient = recipient
        return self
    
    def type(self, message_type: Union[MessageType, str]) -> "MessageBuilder":
        """设置消息类型"""
        if isinstance(message_type, str):
            message_type = MessageType(message_type)
        self._message_type = message_type
        return self
    
    def reply_to(self, message_id: str) -> "MessageBuilder":
        """设置为回复某条消息"""
        if message_id not in self._references:
            self._references.append(message_id)
        return self
    
    def with_context(self, key: str, value: Any) -> "MessageBuilder":
        """添加上下文信息"""
        self._context[key] = value
        return self
    
    def with_metadata(self, key: str, value: Any) -> "MessageBuilder":
        """添加元数据"""
        self._metadata[key] = value
        return self
    
    def build(self) -> Message:
        """构建消息对象"""
        return Message(
            content=self._content,
            sender=self.sender,
            recipient=self._recipient,
            message_type=self._message_type,
            context=self._context.copy(),
            references=self._references.copy(),
            metadata=self._metadata.copy()
        )


# 便捷的消息创建函数
def create_argument_message(sender: str, content: str, recipient: str = None) -> Message:
    """创建论证消息"""
    return Message(content=content, sender=sender, recipient=recipient, 
                  message_type=MessageType.ARGUMENT)

def create_counter_message(sender: str, content: str, reply_to_id: str, recipient: str = None) -> Message:
    """创建反驳消息"""
    msg = Message(content=content, sender=sender, recipient=recipient, 
                 message_type=MessageType.COUNTER)
    msg.add_reference(reply_to_id)
    return msg

def create_user_input_message(content: str, sender: str = "用户") -> Message:
    """创建用户输入消息"""
    return Message(content=content, sender=sender, message_type=MessageType.USER_INPUT)

def create_summary_message(sender: str, content: str, referenced_messages: List[str] = None) -> Message:
    """创建总结消息"""
    msg = Message(content=content, sender=sender, message_type=MessageType.SUMMARY)
    if referenced_messages:
        for ref_id in referenced_messages:
            msg.add_reference(ref_id)
    return msg