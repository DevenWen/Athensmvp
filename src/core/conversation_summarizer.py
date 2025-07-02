"""
对话整理和总结模块
处理辩论对话的整理、分析和markdown格式输出
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from src.core.conversation import Conversation
from src.core.message import Message, MessageType
from src.core.context_manager import ContextManager

logger = logging.getLogger(__name__)


class ConversationSummarizer:
    """
    对话总结器
    负责整理和总结辩论对话，生成结构化的markdown报告
    """
    
    def __init__(self, conversation: Conversation):
        """
        初始化对话总结器
        
        Args:
            conversation: 对话对象
        """
        self.conversation = conversation
        self.context_manager = ContextManager(conversation)
        
    def summarize_debate(self) -> str:
        """
        生成辩论总结
        
        Returns:
            完整的辩论总结文本
        """
        try:
            # 提取关键信息
            participants = self._extract_participants()
            key_points = self.extract_key_points()
            conclusion = self.generate_conclusion()
            
            # 生成总结
            summary = self._format_summary(participants, key_points, conclusion)
            
            logger.info("Debate summary generated successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating debate summary: {e}")
            return f"生成总结时出现错误: {e}"
    
    def format_as_markdown(self) -> str:
        """
        格式化为markdown格式
        
        Returns:
            markdown格式的完整报告
        """
        try:
            # 获取辩论基本信息
            stats = self.conversation.get_statistics()
            messages = self.conversation.messages
            
            # 提取参与者信息
            participants = self._extract_participants()
            
            # 生成markdown内容
            markdown_content = self._generate_markdown_report(stats, messages, participants)
            
            logger.info("Markdown report generated successfully")
            return markdown_content
            
        except Exception as e:
            logger.error(f"Error generating markdown report: {e}")
            return f"# 报告生成失败\\n\\n错误: {e}"
    
    def extract_key_points(self) -> List[str]:
        """
        提取关键论点
        
        Returns:
            关键论点列表
        """
        try:
            key_points = []
            
            # 按发言者分组消息
            messages_by_sender = self._group_messages_by_sender()
            
            for sender, messages in messages_by_sender.items():
                sender_points = self._extract_sender_key_points(sender, messages)
                key_points.extend(sender_points)
                
            return key_points
            
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return [f"提取关键论点时出现错误: {e}"]
    
    def generate_conclusion(self) -> str:
        """
        生成结论
        
        Returns:
            辩论结论
        """
        try:
            messages = self.conversation.messages
            if not messages:
                return "无对话内容"
                
            # 检查是否达成共识
            last_messages = messages[-3:] if len(messages) >= 3 else messages
            
            for message in reversed(last_messages):
                if self._contains_agreement(message.content):
                    return f"双方达成共识。{message.sender}表示同意对方观点。"
                    
            # 如果没有明确共识，生成基于内容的结论
            return self._generate_content_based_conclusion()
            
        except Exception as e:
            logger.error(f"Error generating conclusion: {e}")
            return f"生成结论时出现错误: {e}"
    
    def _extract_participants(self) -> Dict[str, Dict[str, Any]]:
        """提取参与者信息"""
        participants = {}
        
        for message in self.conversation.messages:
            sender = message.sender
            if sender not in participants:
                participants[sender] = {
                    "name": sender,
                    "message_count": 0,
                    "first_message_time": message.timestamp,
                    "last_message_time": message.timestamp,
                    "message_types": set()
                }
            
            # 更新统计
            participants[sender]["message_count"] += 1
            participants[sender]["last_message_time"] = message.timestamp
            participants[sender]["message_types"].add(message.message_type.value)
            
        # 转换set为list以便序列化
        for participant in participants.values():
            participant["message_types"] = list(participant["message_types"])
            
        return participants
    
    def _group_messages_by_sender(self) -> Dict[str, List[Message]]:
        """按发言者分组消息"""
        grouped = {}
        
        for message in self.conversation.messages:
            sender = message.sender
            if sender not in grouped:
                grouped[sender] = []
            grouped[sender].append(message)
            
        return grouped
    
    def _extract_sender_key_points(self, sender: str, messages: List[Message]) -> List[str]:
        """提取特定发言者的关键论点"""
        key_points = []
        
        for message in messages:
            # 简单的关键论点提取逻辑
            content = message.content.strip()
            if len(content) > 50:  # 只考虑较长的消息
                # 取前100个字符作为关键论点摘要
                summary = content[:100].replace("\\n", " ").strip()
                if summary:
                    key_points.append(f"**{sender}**: {summary}...")
                    
        return key_points[:3]  # 最多返回3个关键论点
    
    def _contains_agreement(self, content: str) -> bool:
        """检查内容是否包含同意表达"""
        agreement_keywords = [
            "同意你的结论", "我同意", "赞同你的观点", "接受你的结论",
            "你说得对", "我认为你是对的", "我接受", "同意这个观点",
            "I agree with your conclusion", "I agree", "you are right", "I accept",
            "I concur", "you make a valid point", "I'm convinced"
        ]
        
        content_lower = content.lower()
        return any(keyword.lower() in content_lower for keyword in agreement_keywords)
    
    def _generate_content_based_conclusion(self) -> str:
        """基于内容生成结论"""
        messages = self.conversation.messages
        if not messages:
            return "无法生成结论：无对话内容"
            
        # 简单的结论生成逻辑
        participants = list(self._extract_participants().keys())
        
        if len(participants) >= 2:
            return f"辩论在{participants[0]}和{participants[1]}之间展开，双方各自提出了观点，但未达成明确共识。"
        else:
            return "辩论内容有限，无法生成明确结论。"
    
    def _format_summary(self, participants: Dict[str, Dict[str, Any]], 
                       key_points: List[str], conclusion: str) -> str:
        """格式化总结"""
        summary_parts = [
            "# 辩论总结\\n",
            f"## 参与者 ({len(participants)}人)",
        ]
        
        # 参与者信息
        for participant_info in participants.values():
            summary_parts.append(
                f"- **{participant_info['name']}**: {participant_info['message_count']}条发言"
            )
        
        # 关键论点
        summary_parts.append("\\n## 关键论点")
        if key_points:
            summary_parts.extend(key_points)
        else:
            summary_parts.append("无关键论点提取")
        
        # 结论
        summary_parts.extend([
            "\\n## 结论",
            conclusion
        ])
        
        return "\\n".join(summary_parts)
    
    def _generate_markdown_report(self, stats: Dict[str, Any], 
                                 messages: List[Message], 
                                 participants: Dict[str, Dict[str, Any]]) -> str:
        """生成完整的markdown报告"""
        
        # 报告头部
        report_parts = [
            "# Athens辩论记录\\n",
            "## 基本信息",
            f"- **对话ID**: {self.conversation.conversation_id}",
            f"- **开始时间**: {stats.get('first_message_time', 'N/A')}",
            f"- **结束时间**: {stats.get('last_message_time', 'N/A')}",
            f"- **总消息数**: {stats.get('total_messages', 0)}",
            f"- **参与者数量**: {len(participants)}",
        ]
        
        # 参与者详情
        if participants:
            report_parts.extend([
                "\\n## 参与者信息"
            ])
            
            for participant_info in participants.values():
                report_parts.extend([
                    f"### {participant_info['name']}",
                    f"- **发言次数**: {participant_info['message_count']}",
                    f"- **首次发言**: {participant_info['first_message_time']}",
                    f"- **最后发言**: {participant_info['last_message_time']}",
                    f"- **消息类型**: {', '.join(participant_info['message_types'])}\\n"
                ])
        
        # 辩论摘要
        report_parts.extend([
            "## 辩论摘要",
            self.summarize_debate()
        ])
        
        # 完整对话记录
        report_parts.extend([
            "\\n## 完整对话记录\\n"
        ])
        
        for i, message in enumerate(messages, 1):
            timestamp = message.timestamp.strftime("%H:%M:%S") if message.timestamp else "N/A"
            report_parts.append(
                f"**{i}. {message.sender}** ({timestamp})\\n"
                f"{message.content}\\n"
            )
        
        # 报告尾部
        report_parts.extend([
            "---",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "*生成工具: Athens MVP v0.0.2*"
        ])
        
        return "\\n".join(report_parts)