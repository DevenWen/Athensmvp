"""
智能体间通信机制
处理消息路由、分发和通信状态管理
"""

from typing import Dict, List, Optional, Callable, Any, Set
from datetime import datetime
from enum import Enum
import asyncio
from collections import defaultdict, deque

from .message import Message, MessageType
from .conversation import Conversation


class CommunicationStatus(Enum):
    """通信状态枚举"""
    ACTIVE = "active"           # 活跃通信
    PAUSED = "paused"          # 暂停通信
    SUSPENDED = "suspended"     # 挂起通信
    TERMINATED = "terminated"   # 终止通信


class MessageDeliveryStatus(Enum):
    """消息投递状态枚举"""
    PENDING = "pending"         # 等待投递
    DELIVERED = "delivered"     # 已投递
    ACKNOWLEDGED = "acknowledged" # 已确认
    FAILED = "failed"          # 投递失败


class CommunicationChannel:
    """
    通信通道
    管理两个或多个智能体之间的通信
    """
    
    def __init__(self, channel_id: str, participants: List[str]):
        self.channel_id = channel_id
        self.participants = set(participants)
        self.conversation = Conversation(f"channel_{channel_id}")
        self.status = CommunicationStatus.ACTIVE
        self.message_queue: deque = deque()
        self.delivery_status: Dict[str, MessageDeliveryStatus] = {}
        self.created_at = datetime.now()
        self.metadata: Dict[str, Any] = {}
        
        # 消息监听器
        self.message_listeners: List[Callable[[Message], None]] = []
        
        # 通信统计
        self.stats = {
            "messages_sent": 0,
            "messages_delivered": 0,
            "messages_acknowledged": 0,
            "last_activity": datetime.now()
        }
    
    def add_participant(self, participant: str) -> None:
        """添加参与者"""
        self.participants.add(participant)
    
    def remove_participant(self, participant: str) -> None:
        """移除参与者"""
        self.participants.discard(participant)
    
    def is_participant(self, agent: str) -> bool:
        """检查是否为参与者"""
        return agent in self.participants
    
    def send_message(self, message: Message) -> bool:
        """发送消息到通道"""
        if self.status != CommunicationStatus.ACTIVE:
            return False
        
        # 广播通道允许任何人发送消息
        if self.channel_id != "broadcast" and message.sender not in self.participants:
            return False
        
        # 如果指定了接收者，检查是否为参与者
        if message.recipient and message.recipient not in self.participants:
            return False
        
        # 添加到对话历史
        self.conversation.add_message(message)
        
        # 添加到消息队列
        self.message_queue.append(message)
        
        # 设置投递状态
        self.delivery_status[message.id] = MessageDeliveryStatus.PENDING
        
        # 更新统计
        self.stats["messages_sent"] += 1
        self.stats["last_activity"] = datetime.now()
        
        # 通知监听器
        for listener in self.message_listeners:
            try:
                listener(message)
            except Exception as e:
                print(f"消息监听器错误: {e}")
        
        return True
    
    def get_pending_messages(self, recipient: str = None) -> List[Message]:
        """获取待处理的消息"""
        pending = []
        for message in self.message_queue:
            if self.delivery_status.get(message.id) == MessageDeliveryStatus.PENDING:
                if recipient is None or message.recipient == recipient or message.recipient is None:
                    pending.append(message)
        return pending
    
    def mark_delivered(self, message_id: str) -> bool:
        """标记消息已投递"""
        if message_id in self.delivery_status:
            self.delivery_status[message_id] = MessageDeliveryStatus.DELIVERED
            self.stats["messages_delivered"] += 1
            return True
        return False
    
    def mark_acknowledged(self, message_id: str) -> bool:
        """标记消息已确认"""
        if message_id in self.delivery_status:
            self.delivery_status[message_id] = MessageDeliveryStatus.ACKNOWLEDGED
            self.stats["messages_acknowledged"] += 1
            return True
        return False
    
    def mark_failed(self, message_id: str) -> bool:
        """标记消息投递失败"""
        if message_id in self.delivery_status:
            self.delivery_status[message_id] = MessageDeliveryStatus.FAILED
            return True
        return False
    
    def add_message_listener(self, listener: Callable[[Message], None]) -> None:
        """添加消息监听器"""
        self.message_listeners.append(listener)
    
    def remove_message_listener(self, listener: Callable[[Message], None]) -> None:
        """移除消息监听器"""
        if listener in self.message_listeners:
            self.message_listeners.remove(listener)
    
    def pause(self) -> None:
        """暂停通信"""
        self.status = CommunicationStatus.PAUSED
    
    def resume(self) -> None:
        """恢复通信"""
        if self.status == CommunicationStatus.PAUSED:
            self.status = CommunicationStatus.ACTIVE
    
    def terminate(self) -> None:
        """终止通信"""
        self.status = CommunicationStatus.TERMINATED
        self.message_queue.clear()
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Message]:
        """获取对话历史"""
        if limit:
            return self.conversation.get_recent_messages(limit)
        return self.conversation.messages.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取通信统计"""
        stats = self.stats.copy()
        stats.update({
            "channel_id": self.channel_id,
            "participants": list(self.participants),
            "status": self.status.value,
            "total_messages": len(self.conversation.messages),
            "pending_messages": len([m for m in self.delivery_status.values() 
                                   if m == MessageDeliveryStatus.PENDING]),
            "conversation_stats": self.conversation.get_statistics()
        })
        return stats


class Communication:
    """
    通信管理器
    负责管理所有智能体间的通信，包括消息路由和通道管理
    """
    
    def __init__(self):
        self.channels: Dict[str, CommunicationChannel] = {}
        self.agent_channels: Dict[str, Set[str]] = defaultdict(set)  # 智能体到通道的映射
        self.global_listeners: List[Callable[[Message, str], None]] = []  # 全局消息监听器
        self.routing_rules: List[Callable[[Message], Optional[str]]] = []  # 路由规则
        
        # 广播通道
        self.broadcast_channel_id = "broadcast"
        self.create_channel(self.broadcast_channel_id, [])
    
    def create_channel(self, channel_id: str, participants: List[str]) -> CommunicationChannel:
        """创建通信通道"""
        if channel_id in self.channels:
            raise ValueError(f"通道 {channel_id} 已存在")
        
        channel = CommunicationChannel(channel_id, participants)
        self.channels[channel_id] = channel
        
        # 更新智能体通道映射
        for participant in participants:
            self.agent_channels[participant].add(channel_id)
        
        # 添加全局监听器
        channel.add_message_listener(lambda msg: self._on_message_sent(msg, channel_id))
        
        return channel
    
    def get_channel(self, channel_id: str) -> Optional[CommunicationChannel]:
        """获取通信通道"""
        return self.channels.get(channel_id)
    
    def delete_channel(self, channel_id: str) -> bool:
        """删除通信通道"""
        if channel_id not in self.channels:
            return False
        
        channel = self.channels[channel_id]
        
        # 从智能体通道映射中移除
        for participant in channel.participants:
            self.agent_channels[participant].discard(channel_id)
        
        # 终止并删除通道
        channel.terminate()
        del self.channels[channel_id]
        
        return True
    
    def join_channel(self, channel_id: str, agent: str) -> bool:
        """加入通信通道"""
        channel = self.get_channel(channel_id)
        if not channel:
            return False
        
        channel.add_participant(agent)
        self.agent_channels[agent].add(channel_id)
        return True
    
    def leave_channel(self, channel_id: str, agent: str) -> bool:
        """离开通信通道"""
        channel = self.get_channel(channel_id)
        if not channel:
            return False
        
        channel.remove_participant(agent)
        self.agent_channels[agent].discard(channel_id)
        return True
    
    def send_message(self, message: Message, channel_id: str = None) -> bool:
        """发送消息"""
        # 如果没有指定通道，尝试自动路由
        if channel_id is None:
            channel_id = self._route_message(message)
        
        if channel_id is None:
            return False
        
        channel = self.get_channel(channel_id)
        if not channel:
            return False
        
        return channel.send_message(message)
    
    def send_direct_message(self, sender: str, recipient: str, content: str, 
                          message_type: MessageType = MessageType.GENERAL) -> bool:
        """发送点对点消息"""
        # 查找或创建直接通信通道
        channel_id = f"direct_{min(sender, recipient)}_{max(sender, recipient)}"
        
        if channel_id not in self.channels:
            self.create_channel(channel_id, [sender, recipient])
        
        message = Message(
            content=content,
            sender=sender,
            recipient=recipient,
            message_type=message_type
        )
        
        return self.send_message(message, channel_id)
    
    def broadcast_message(self, sender: str, content: str, 
                         message_type: MessageType = MessageType.GENERAL) -> bool:
        """广播消息"""
        message = Message(
            content=content,
            sender=sender,
            message_type=message_type
        )
        
        return self.send_message(message, self.broadcast_channel_id)
    
    def get_pending_messages_for_agent(self, agent: str) -> List[tuple[Message, str]]:
        """获取智能体的待处理消息"""
        pending_messages = []
        
        for channel_id in self.agent_channels[agent]:
            channel = self.get_channel(channel_id)
            if channel:
                messages = channel.get_pending_messages(agent)
                for message in messages:
                    pending_messages.append((message, channel_id))
        
        # 也检查广播通道
        broadcast_channel = self.get_channel(self.broadcast_channel_id)
        if broadcast_channel:
            messages = broadcast_channel.get_pending_messages()
            for message in messages:
                if message.sender != agent:  # 不包括自己发送的广播消息
                    pending_messages.append((message, self.broadcast_channel_id))
        
        return pending_messages
    
    def acknowledge_message(self, message_id: str, channel_id: str) -> bool:
        """确认收到消息"""
        channel = self.get_channel(channel_id)
        if channel:
            return channel.mark_acknowledged(message_id)
        return False
    
    def add_routing_rule(self, rule: Callable[[Message], Optional[str]]) -> None:
        """添加路由规则"""
        self.routing_rules.append(rule)
    
    def add_global_listener(self, listener: Callable[[Message, str], None]) -> None:
        """添加全局消息监听器"""
        self.global_listeners.append(listener)
    
    def get_agent_channels(self, agent: str) -> List[str]:
        """获取智能体参与的所有通道"""
        return list(self.agent_channels[agent])
    
    def get_conversation_between_agents(self, agent1: str, agent2: str) -> Optional[Conversation]:
        """获取两个智能体之间的对话"""
        channel_id = f"direct_{min(agent1, agent2)}_{max(agent1, agent2)}"
        channel = self.get_channel(channel_id)
        return channel.conversation if channel else None
    
    def get_communication_statistics(self) -> Dict[str, Any]:
        """获取通信统计信息"""
        total_channels = len(self.channels)
        total_messages = sum(len(ch.conversation.messages) for ch in self.channels.values())
        active_channels = sum(1 for ch in self.channels.values() 
                            if ch.status == CommunicationStatus.ACTIVE)
        
        channel_stats = {ch_id: ch.get_statistics() 
                        for ch_id, ch in self.channels.items()}
        
        return {
            "total_channels": total_channels,
            "active_channels": active_channels,
            "total_messages": total_messages,
            "total_agents": len(self.agent_channels),
            "channel_statistics": channel_stats
        }
    
    def pause_all_communication(self) -> None:
        """暂停所有通信"""
        for channel in self.channels.values():
            channel.pause()
    
    def resume_all_communication(self) -> None:
        """恢复所有通信"""
        for channel in self.channels.values():
            channel.resume()
    
    def _route_message(self, message: Message) -> Optional[str]:
        """消息路由逻辑"""
        # 应用自定义路由规则
        for rule in self.routing_rules:
            try:
                channel_id = rule(message)
                if channel_id:
                    return channel_id
            except Exception as e:
                print(f"路由规则错误: {e}")
        
        # 默认路由逻辑
        if message.recipient:
            # 点对点消息
            channel_id = f"direct_{min(message.sender, message.recipient)}_{max(message.sender, message.recipient)}"
            if channel_id in self.channels:
                return channel_id
            # 如果直接通道不存在，创建一个
            self.create_channel(channel_id, [message.sender, message.recipient])
            return channel_id
        else:
            # 广播消息
            return self.broadcast_channel_id
    
    def _on_message_sent(self, message: Message, channel_id: str) -> None:
        """消息发送事件处理"""
        # 调用全局监听器
        for listener in self.global_listeners:
            try:
                listener(message, channel_id)
            except Exception as e:
                print(f"全局消息监听器错误: {e}")
    
    def __repr__(self) -> str:
        """调试用字符串表示"""
        return (f"Communication(channels={len(self.channels)}, "
                f"agents={len(self.agent_channels)})")