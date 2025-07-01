"""
用户指令处理器
解析和执行用户输入的指令，包括系统指令和@提及
"""

import re
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass

from src.core.message import Message, MessageType


class CommandType(Enum):
    """指令类型枚举"""
    SYSTEM_COMMAND = "system_command"     # 系统指令 (/pause, /resume等)
    MENTION = "mention"                   # @提及 (@logician, @skeptic)
    REGULAR_MESSAGE = "regular_message"   # 普通消息
    INVALID = "invalid"                   # 无效输入


@dataclass
class ParsedCommand:
    """解析后的指令结构"""
    command_type: CommandType
    raw_input: str
    command: Optional[str] = None         # 系统指令名称
    target: Optional[str] = None          # @提及的目标
    content: Optional[str] = None         # 消息内容
    args: List[str] = None                # 指令参数
    is_valid: bool = True
    error_message: Optional[str] = None


class CommandProcessor:
    """
    用户指令处理器
    负责解析用户输入并执行相应的操作
    """
    
    # 支持的系统指令
    SYSTEM_COMMANDS = {
        "pause": {
            "description": "暂停当前辩论",
            "aliases": ["暂停", "p"],
            "usage": "/pause"
        },
        "resume": {
            "description": "继续暂停的辩论",
            "aliases": ["继续", "r"],
            "usage": "/resume"
        },
        "end": {
            "description": "结束当前辩论",
            "aliases": ["结束", "quit", "exit"],
            "usage": "/end"
        },
        "status": {
            "description": "查看辩论状态",
            "aliases": ["状态", "s"],
            "usage": "/status"
        },
        "help": {
            "description": "显示帮助信息",
            "aliases": ["帮助", "h", "?"],
            "usage": "/help"
        },
        "theme": {
            "description": "切换界面主题",
            "aliases": ["主题"],
            "usage": "/theme [主题名]"
        },
        "history": {
            "description": "查看对话历史",
            "aliases": ["历史"],
            "usage": "/history [数量]"
        },
        "clear": {
            "description": "清空屏幕",
            "aliases": ["清屏", "cls"],
            "usage": "/clear"
        }
    }
    
    # 支持的@提及目标
    MENTION_TARGETS = {
        "logician": ["逻辑者", "logic", "l"],
        "skeptic": ["怀疑者", "doubt", "s"],
        "both": ["all", "所有", "全部"],
        "system": ["系统", "sys"]
    }
    
    def __init__(self):
        self.command_handlers: Dict[str, Callable] = {}
        self.mention_handlers: Dict[str, Callable] = {}
        self.input_validators: List[Callable] = []
        
        # 注册默认验证器
        self._register_default_validators()
    
    def parse_command(self, input_text: str) -> ParsedCommand:
        """
        解析用户输入的指令
        
        Args:
            input_text: 用户输入的原始文本
            
        Returns:
            ParsedCommand: 解析后的指令对象
        """
        if not input_text or not input_text.strip():
            return ParsedCommand(
                command_type=CommandType.INVALID,
                raw_input=input_text,
                is_valid=False,
                error_message="输入不能为空"
            )
        
        input_text = input_text.strip()
        
        # 1. 检查是否为系统指令
        if input_text.startswith('/'):
            return self._parse_system_command(input_text)
        
        # 2. 检查是否包含@提及
        if '@' in input_text:
            return self._parse_mention(input_text)
        
        # 3. 普通消息
        return ParsedCommand(
            command_type=CommandType.REGULAR_MESSAGE,
            raw_input=input_text,
            content=input_text,
            is_valid=True
        )
    
    def _parse_system_command(self, input_text: str) -> ParsedCommand:
        """解析系统指令"""
        # 移除开头的 '/'
        command_text = input_text[1:].strip()
        
        if not command_text:
            return ParsedCommand(
                command_type=CommandType.INVALID,
                raw_input=input_text,
                is_valid=False,
                error_message="指令不能为空，使用 /help 查看可用指令"
            )
        
        # 分割指令和参数
        parts = command_text.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # 查找指令（支持别名）
        found_command = None
        for cmd, info in self.SYSTEM_COMMANDS.items():
            if command == cmd or command in info.get("aliases", []):
                found_command = cmd
                break
        
        if not found_command:
            return ParsedCommand(
                command_type=CommandType.INVALID,
                raw_input=input_text,
                is_valid=False,
                error_message=f"未知指令: {command}，使用 /help 查看可用指令"
            )
        
        return ParsedCommand(
            command_type=CommandType.SYSTEM_COMMAND,
            raw_input=input_text,
            command=found_command,
            args=args,
            is_valid=True
        )
    
    def _parse_mention(self, input_text: str) -> ParsedCommand:
        """解析@提及"""
        # 使用正则表达式提取@提及
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, input_text)
        
        if not mentions:
            # 包含@但没有有效提及，当作普通消息处理
            return ParsedCommand(
                command_type=CommandType.REGULAR_MESSAGE,
                raw_input=input_text,
                content=input_text,
                is_valid=True
            )
        
        # 查找第一个有效的@提及
        target = None
        for mention in mentions:
            for target_key, aliases in self.MENTION_TARGETS.items():
                if mention.lower() == target_key or mention.lower() in aliases:
                    target = target_key
                    break
            if target:
                break
        
        if not target:
            return ParsedCommand(
                command_type=CommandType.INVALID,
                raw_input=input_text,
                is_valid=False,
                error_message=f"无效的@提及目标: {mentions[0]}，支持的目标: {list(self.MENTION_TARGETS.keys())}"
            )
        
        # 提取消息内容（移除@提及部分）
        content = re.sub(r'@\w+\s*', '', input_text).strip()
        
        if not content:
            return ParsedCommand(
                command_type=CommandType.INVALID,
                raw_input=input_text,
                is_valid=False,
                error_message="@提及后必须包含消息内容"
            )
        
        return ParsedCommand(
            command_type=CommandType.MENTION,
            raw_input=input_text,
            target=target,
            content=content,
            is_valid=True
        )
    
    def register_command_handler(self, command: str, handler: Callable) -> None:
        """注册系统指令处理器"""
        self.command_handlers[command] = handler
    
    def register_mention_handler(self, target: str, handler: Callable) -> None:
        """注册@提及处理器"""
        self.mention_handlers[target] = handler
    
    def execute_command(self, parsed_command: ParsedCommand) -> Dict[str, Any]:
        """
        执行解析后的指令
        
        Args:
            parsed_command: 解析后的指令对象
            
        Returns:
            Dict: 执行结果
        """
        if not parsed_command.is_valid:
            return {
                "success": False,
                "error": parsed_command.error_message,
                "type": "validation_error"
            }
        
        try:
            if parsed_command.command_type == CommandType.SYSTEM_COMMAND:
                return self._execute_system_command(parsed_command)
            
            elif parsed_command.command_type == CommandType.MENTION:
                return self._execute_mention(parsed_command)
            
            elif parsed_command.command_type == CommandType.REGULAR_MESSAGE:
                return {
                    "success": True,
                    "type": "regular_message",
                    "content": parsed_command.content,
                    "message": "普通消息，可以发送到辩论频道"
                }
            
            else:
                return {
                    "success": False,
                    "error": "未知的指令类型",
                    "type": "execution_error"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"执行指令时发生错误: {str(e)}",
                "type": "execution_error"
            }
    
    def _execute_system_command(self, parsed_command: ParsedCommand) -> Dict[str, Any]:
        """执行系统指令"""
        command = parsed_command.command
        args = parsed_command.args or []
        
        # 查找注册的处理器
        if command in self.command_handlers:
            return self.command_handlers[command](args)
        
        # 内置指令处理
        if command == "help":
            return self._handle_help_command(args)
        
        # 默认响应
        return {
            "success": True,
            "type": "system_command",
            "command": command,
            "args": args,
            "message": f"系统指令 '{command}' 被识别，但尚未实现具体处理逻辑"
        }
    
    def _execute_mention(self, parsed_command: ParsedCommand) -> Dict[str, Any]:
        """执行@提及"""
        target = parsed_command.target
        content = parsed_command.content
        
        # 查找注册的处理器
        if target in self.mention_handlers:
            return self.mention_handlers[target](content)
        
        # 默认响应
        return {
            "success": True,
            "type": "mention",
            "target": target,
            "content": content,
            "message": f"@提及 '{target}' 被识别，消息内容: {content}"
        }
    
    def _handle_help_command(self, args: List[str]) -> Dict[str, Any]:
        """处理帮助指令"""
        if args and args[0] in self.SYSTEM_COMMANDS:
            # 显示特定指令的帮助
            cmd_info = self.SYSTEM_COMMANDS[args[0]]
            help_text = f"指令: {args[0]}\n"
            help_text += f"描述: {cmd_info['description']}\n"
            help_text += f"用法: {cmd_info['usage']}\n"
            if cmd_info.get('aliases'):
                help_text += f"别名: {', '.join(cmd_info['aliases'])}"
        else:
            # 显示所有指令的帮助
            help_text = "🤖 Athens 辩论系统 - 用户指令帮助\n\n"
            help_text += "系统指令:\n"
            for cmd, info in self.SYSTEM_COMMANDS.items():
                help_text += f"  {info['usage']:<15} - {info['description']}\n"
            
            help_text += "\n@提及指令:\n"
            help_text += "  @logician <消息> - 向逻辑者发送消息\n"
            help_text += "  @skeptic <消息>  - 向怀疑者发送消息\n"
            help_text += "  @both <消息>     - 向两个智能体发送消息\n"
            
            help_text += "\n提示:\n"
            help_text += "  - 使用 /help <指令名> 查看特定指令的详细帮助\n"
            help_text += "  - 普通文本将作为一般消息发送\n"
            help_text += "  - 支持Markdown格式的消息内容"
        
        return {
            "success": True,
            "type": "help",
            "content": help_text
        }
    
    def validate_input(self, input_text: str) -> Tuple[bool, Optional[str]]:
        """验证用户输入"""
        for validator in self.input_validators:
            is_valid, error_msg = validator(input_text)
            if not is_valid:
                return False, error_msg
        return True, None
    
    def _register_default_validators(self) -> None:
        """注册默认的输入验证器"""
        
        def length_validator(text: str) -> Tuple[bool, Optional[str]]:
            """长度验证器"""
            if len(text) > 2000:
                return False, "输入内容过长，请限制在2000字符以内"
            return True, None
        
        def content_validator(text: str) -> Tuple[bool, Optional[str]]:
            """内容验证器"""
            # 检查是否包含恶意内容（简单实现）
            forbidden_patterns = [
                r'<script.*?>.*?</script>',  # JavaScript
                r'javascript:',              # JavaScript URL
                r'vbscript:',               # VBScript URL
            ]
            
            for pattern in forbidden_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return False, "输入内容包含不允许的脚本代码"
            
            return True, None
        
        self.input_validators.extend([length_validator, content_validator])
    
    def get_command_suggestions(self, partial_input: str) -> List[str]:
        """获取指令建议（用于自动补全）"""
        suggestions = []
        
        if partial_input.startswith('/'):
            partial_cmd = partial_input[1:].lower()
            for cmd, info in self.SYSTEM_COMMANDS.items():
                if cmd.startswith(partial_cmd):
                    suggestions.append(f"/{cmd}")
                # 检查别名
                for alias in info.get("aliases", []):
                    if alias.startswith(partial_cmd):
                        suggestions.append(f"/{alias}")
        
        elif partial_input.startswith('@'):
            partial_mention = partial_input[1:].lower()
            for target, aliases in self.MENTION_TARGETS.items():
                if target.startswith(partial_mention):
                    suggestions.append(f"@{target}")
                for alias in aliases:
                    if alias.startswith(partial_mention):
                        suggestions.append(f"@{alias}")
        
        return suggestions[:5]  # 限制建议数量