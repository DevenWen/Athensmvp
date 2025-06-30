"""
上下文管理器
智能地维护对话上下文，控制上下文长度和相关性，为AI模型准备输入。
"""

from typing import List, Dict, Any, Optional
from .message import Message, MessageType
from .conversation import Conversation

class ContextManager:
    """
    上下文管理器
    负责为AI智能体构建和维护一个相关的、有界的对话上下文。
    """
    
    def __init__(self, conversation: Conversation, max_tokens: int = 4096, 
                 user_input_weight: float = 2.0, referenced_message_weight: float = 1.5):
        """
        初始化上下文管理器
        
        :param conversation: 对话历史对象
        :param max_tokens: 上下文允许的最大token数
        :param user_input_weight: 用户输入消息的权重
        :param referenced_message_weight: 被引用消息的权重
        """
        self.conversation = conversation
        self.max_tokens = max_tokens
        self.user_input_weight = user_input_weight
        self.referenced_message_weight = referenced_message_weight
        
        # 简单的token计算函数（可替换为更精确的实现）
        self._token_estimator = lambda text: len(text) // 4

    def _calculate_message_score(self, message: Message, all_messages: List[Message]) -> float:
        """
        计算消息的重要性得分
        - 用户输入的消息得分更高
        - 被其他消息引用的消息得分更高
        - 最近的消息得分更高
        """
        score = 1.0
        
        # 用户输入权重
        if message.message_type == MessageType.USER_INPUT:
            score *= self.user_input_weight
            
        # 被引用权重
        is_referenced = any(message.id in m.references for m in all_messages if m.references)
        if is_referenced:
            score *= self.referenced_message_weight
            
        # 时间衰减（越近的消息得分越高）
        # 这里简化处理，在选择时直接优先选择最近的
        
        return score

    def build_context(self, for_agent: str, max_messages: Optional[int] = None) -> List[Message]:
        """
        为特定智能体构建上下文
        
        策略：
        1. 获取所有消息。
        2. 计算每条消息的重要性得分。
        3. 按得分和时间倒序排序。
        4. 从高分到低分选择消息，直到达到token或数量限制。
        5. 最终结果按时间正序排列。
        
        :param for_agent: 需要上下文的智能体ID
        :param max_messages: 上下文包含的最大消息数
        :return: 构建好的上下文消息列表
        """
        all_messages = self.conversation.get_messages()
        
        # 计算所有消息的得分
        scored_messages = []
        for i, msg in enumerate(all_messages):
            score = self._calculate_message_score(msg, all_messages)
            # 添加时间因素，越新的消息得分越高
            score += i / len(all_messages)
            scored_messages.append((score, msg))
            
        # 按得分降序排序
        scored_messages.sort(key=lambda x: x[0], reverse=True)
        
        # 选择消息构建上下文
        context_messages = []
        current_tokens = 0
        
        for score, message in scored_messages:
            message_tokens = self._token_estimator(message.content)
            
            if current_tokens + message_tokens > self.max_tokens:
                continue
            
            context_messages.append(message)
            current_tokens += message_tokens
            
            if max_messages and len(context_messages) >= max_messages:
                break
        
        # 按时间戳升序排序，确保对话顺序正确
        context_messages.sort(key=lambda m: m.timestamp)
        
        return context_messages

    def get_formatted_context(self, for_agent: str, max_messages: Optional[int] = None) -> str:
        """
        获取格式化为字符串的上下文，可以直接作为AI模型的输入
        
        :param for_agent: 需要上下文的智能体ID
        :param max_messages: 上下文包含的最大消息数
        :return: 格式化的上下文字符串
        """
        context_messages = self.build_context(for_agent, max_messages)
        
        formatted_context = []
        for msg in context_messages:
            # 格式: "Sender (MessageType): Content"
            line = f"{msg.sender} ({msg.message_type.value}): {msg.content}"
            formatted_context.append(line)
            
        return "\n".join(formatted_context)

    def summarize_and_compress(self, messages: List[Message]) -> Message:
        """
        (待实现)
        使用AI模型对一组消息进行摘要和压缩，生成一条新的摘要消息。
        这对于处理非常长的对话历史非常有用。
        """
        # TODO: 调用AI客户端进行摘要
        raise NotImplementedError("上下文摘要功能尚未实现")

    def set_max_tokens(self, max_tokens: int):
        """更新最大token限制"""
        self.max_tokens = max_tokens

    def __repr__(self) -> str:
        return (f"ContextManager(conversation_id='{self.conversation.conversation_id}', "
                f"max_tokens={self.max_tokens})")
