"""
对话历史管理系统
管理完整的对话历史记录，支持消息检索、过滤和组织
"""

from typing import List, Dict, Any, Optional, Callable, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json

from .message import Message, MessageType


class Conversation:
    """
    对话历史管理器
    负责存储、检索和组织对话中的所有消息
    """
    
    def __init__(self, conversation_id: str = None):
        self.conversation_id = conversation_id or f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.messages: List[Message] = []
        self.message_index: Dict[str, Message] = {}  # 消息ID到消息的映射
        self.sender_index: Dict[str, List[str]] = defaultdict(list)  # 发送者到消息ID列表的映射
        self.type_index: Dict[MessageType, List[str]] = defaultdict(list)  # 消息类型到消息ID列表的映射
        self.reference_index: Dict[str, List[str]] = defaultdict(list)  # 被引用消息ID到引用它的消息ID列表
        self.created_at = datetime.now()
        self.metadata: Dict[str, Any] = {}
    
    def add_message(self, message: Message) -> None:
        """添加消息到对话历史"""
        # 检查消息ID是否已存在
        if message.id in self.message_index:
            raise ValueError(f"消息ID {message.id} 已存在")
        
        # 添加到主列表
        self.messages.append(message)
        
        # 更新索引
        self.message_index[message.id] = message
        self.sender_index[message.sender].append(message.id)
        self.type_index[message.message_type].append(message.id)
        
        # 更新引用索引
        for ref_id in message.references:
            self.reference_index[ref_id].append(message.id)
    
    def get_message_by_id(self, message_id: str) -> Optional[Message]:
        """根据ID获取消息"""
        return self.message_index.get(message_id)
    
    def get_messages_by_sender(self, sender: str, limit: Optional[int] = None) -> List[Message]:
        """获取指定发送者的所有消息"""
        message_ids = self.sender_index.get(sender, [])
        if limit:
            message_ids = message_ids[-limit:]
        return [self.message_index[msg_id] for msg_id in message_ids]
    
    def get_messages_by_type(self, message_type: MessageType, limit: Optional[int] = None) -> List[Message]:
        """获取指定类型的所有消息"""
        message_ids = self.type_index.get(message_type, [])
        if limit:
            message_ids = message_ids[-limit:]
        return [self.message_index[msg_id] for msg_id in message_ids]
    
    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """获取最近的N条消息"""
        return self.messages[-count:] if count <= len(self.messages) else self.messages
    
    def get_messages_in_timeframe(self, start_time: datetime, end_time: datetime) -> List[Message]:
        """获取指定时间范围内的消息"""
        return [msg for msg in self.messages 
                if start_time <= msg.timestamp <= end_time]
    
    def get_messages_since(self, since: datetime) -> List[Message]:
        """获取指定时间之后的消息"""
        return [msg for msg in self.messages if msg.timestamp > since]
    
    def get_context_for_agent(self, agent: str, depth: int = 10) -> List[Message]:
        """
        为指定智能体获取相关的上下文消息
        包括最近的消息和与该智能体相关的消息
        """
        # 获取最近的消息
        recent_messages = self.get_recent_messages(depth)
        
        # 获取该智能体的消息
        agent_messages = self.get_messages_by_sender(agent)
        
        # 获取提到该智能体的消息
        mentioned_messages = [msg for msg in self.messages 
                            if msg.recipient == agent or agent in msg.content]
        
        # 合并并去重
        context_messages = []
        seen_ids = set()
        
        for msg_list in [recent_messages, agent_messages[-depth:], mentioned_messages[-depth:]]:
            for msg in msg_list:
                if msg.id not in seen_ids:
                    context_messages.append(msg)
                    seen_ids.add(msg.id)
        
        # 按时间戳排序
        context_messages.sort(key=lambda x: x.timestamp)
        return context_messages
    
    def get_recent_exchanges(self, count: int = 5) -> List[Tuple[Message, List[Message]]]:
        """
        获取最近的消息交换
        返回原始消息和对它的回复列表
        """
        exchanges = []
        processed_ids = set()
        
        # 从最新消息开始查找
        for message in reversed(self.messages):
            if message.id in processed_ids:
                continue
            
            # 查找对此消息的回复
            replies = self.find_replies_to_message(message.id)
            if replies or not message.has_references():
                exchanges.append((message, replies))
                processed_ids.add(message.id)
                for reply in replies:
                    processed_ids.add(reply.id)
            
            if len(exchanges) >= count:
                break
        
        return list(reversed(exchanges))
    
    def find_referenced_messages(self, message_id: str) -> List[Message]:
        """查找被指定消息引用的消息"""
        message = self.get_message_by_id(message_id)
        if not message:
            return []
        
        referenced = []
        for ref_id in message.references:
            ref_message = self.get_message_by_id(ref_id)
            if ref_message:
                referenced.append(ref_message)
        
        return referenced
    
    def find_replies_to_message(self, message_id: str) -> List[Message]:
        """查找对指定消息的回复"""
        reply_ids = self.reference_index.get(message_id, [])
        return [self.message_index[reply_id] for reply_id in reply_ids]
    
    def get_conversation_thread(self, message_id: str) -> List[Message]:
        """
        获取包含指定消息的对话线程
        追踪消息的引用链形成完整的对话线程
        """
        visited = set()
        thread = []
        
        def collect_thread(msg_id: str):
            if msg_id in visited or msg_id not in self.message_index:
                return
            
            visited.add(msg_id)
            message = self.message_index[msg_id]
            thread.append(message)
            
            # 递归收集引用的消息
            for ref_id in message.references:
                collect_thread(ref_id)
            
            # 递归收集回复消息
            for reply_id in self.reference_index.get(msg_id, []):
                collect_thread(reply_id)
        
        collect_thread(message_id)
        
        # 按时间戳排序
        thread.sort(key=lambda x: x.timestamp)
        return thread
    
    def search_messages(self, query: str, case_sensitive: bool = False) -> List[Message]:
        """在消息内容中搜索"""
        if not case_sensitive:
            query = query.lower()
        
        results = []
        for message in self.messages:
            content = message.content if case_sensitive else message.content.lower()
            if query in content:
                results.append(message)
        
        return results
    
    def filter_messages(self, filter_func: Callable[[Message], bool]) -> List[Message]:
        """使用自定义过滤函数过滤消息"""
        return [msg for msg in self.messages if filter_func(msg)]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取对话统计信息"""
        total_messages = len(self.messages)
        if total_messages == 0:
            return {"total_messages": 0}
        
        # 按发送者统计
        sender_stats = {sender: len(msg_ids) 
                       for sender, msg_ids in self.sender_index.items()}
        
        # 按类型统计
        type_stats = {msg_type.value: len(msg_ids) 
                     for msg_type, msg_ids in self.type_index.items()}
        
        # 时间范围
        first_message = self.messages[0]
        last_message = self.messages[-1]
        duration = last_message.timestamp - first_message.timestamp
        
        # 回复统计
        messages_with_refs = sum(1 for msg in self.messages if msg.has_references())
        
        return {
            "total_messages": total_messages,
            "sender_statistics": sender_stats,
            "type_statistics": type_stats,
            "conversation_duration": duration.total_seconds(),
            "messages_with_references": messages_with_refs,
            "reply_rate": messages_with_refs / total_messages if total_messages > 0 else 0,
            "average_messages_per_hour": total_messages / (duration.total_seconds() / 3600) if duration.total_seconds() > 0 else 0,
            "first_message_time": first_message.timestamp.isoformat(),
            "last_message_time": last_message.timestamp.isoformat()
        }
    
    def export_to_dict(self) -> Dict[str, Any]:
        """导出对话为字典格式"""
        return {
            "conversation_id": self.conversation_id,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
            "messages": [msg.to_dict() for msg in self.messages],
            "statistics": self.get_statistics()
        }
    
    def export_to_json(self, indent: int = 2) -> str:
        """导出对话为JSON格式"""
        return json.dumps(self.export_to_dict(), ensure_ascii=False, indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """从字典导入对话"""
        conv = cls(data.get("conversation_id"))
        
        if "created_at" in data:
            conv.created_at = datetime.fromisoformat(data["created_at"])
        
        conv.metadata = data.get("metadata", {})
        
        # 导入消息
        for msg_data in data.get("messages", []):
            message = Message.from_dict(msg_data)
            conv.add_message(message)
        
        return conv
    
    @classmethod
    def from_json(cls, json_str: str) -> "Conversation":
        """从JSON导入对话"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def clear(self) -> None:
        """清空对话历史"""
        self.messages.clear()
        self.message_index.clear()
        self.sender_index.clear()
        self.type_index.clear()
        self.reference_index.clear()
    
    def remove_message(self, message_id: str) -> bool:
        """删除指定消息"""
        message = self.message_index.get(message_id)
        if not message:
            return False
        
        # 从主列表删除
        self.messages.remove(message)
        
        # 从索引删除
        del self.message_index[message_id]
        self.sender_index[message.sender].remove(message_id)
        self.type_index[message.message_type].remove(message_id)
        
        # 清理引用索引
        for ref_id in message.references:
            if message_id in self.reference_index[ref_id]:
                self.reference_index[ref_id].remove(message_id)
        
        # 清理对此消息的引用
        if message_id in self.reference_index:
            del self.reference_index[message_id]
        
        return True
    
    def get_message_count(self) -> int:
        """获取消息总数"""
        return len(self.messages)
    
    def is_empty(self) -> bool:
        """检查对话是否为空"""
        return len(self.messages) == 0
    
    def __len__(self) -> int:
        """返回消息数量"""
        return len(self.messages)
    
    def __iter__(self):
        """迭代所有消息"""
        return iter(self.messages)
    
    def __repr__(self) -> str:
        """调试用字符串表示"""
        return (f"Conversation(id='{self.conversation_id}', "
                f"messages={len(self.messages)}, "
                f"created_at='{self.created_at.strftime('%Y-%m-%d %H:%M')}')")