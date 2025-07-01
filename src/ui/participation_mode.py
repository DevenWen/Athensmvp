"""
参与模式控制器
负责协调CLI界面、指令处理器和辩论管理器，实现用户参与的完整流程
"""

import threading
from typing import Optional

from src.core.ai_client import AIClient
from src.core.debate_manager import DebateManager
from src.agents.logician import Logician
from src.agents.skeptic import Skeptic
from src.core.message import Message, MessageType
from src.ui.cli_interface import CLIInterface
from src.ui.command_processor import CommandProcessor, ParsedCommand, CommandType

class ParticipationMode:
    """
    参与模式控制器
    """
    def __init__(self):
        self.cli = CLIInterface(theme_name="default")
        self.cmd_processor = CommandProcessor()
        self.ai_client = AIClient()
        
        self.logician = Logician(self.ai_client)
        self.skeptic = Skeptic(self.ai_client)
        
        self.debate_manager: Optional[DebateManager] = None
        self.debate_thread: Optional[threading.Thread] = None
        
        self._setup_command_handlers()

    def _setup_command_handlers(self):
        """注册指令处理器"""
        self.cmd_processor.register_command_handler("pause", self._handle_pause)
        self.cmd_processor.register_command_handler("resume", self._handle_resume)
        self.cmd_processor.register_command_handler("end", self._handle_end)
        self.cmd_processor.register_command_handler("status", self._handle_status)
        self.cmd_processor.register_command_handler("help", self._handle_help)
        self.cmd_processor.register_command_handler("theme", self._handle_theme)
        self.cmd_processor.register_command_handler("clear", self._handle_clear)
        
        self.cmd_processor.register_mention_handler("logician", self._handle_mention)
        self.cmd_processor.register_mention_handler("skeptic", self._handle_mention)
        self.cmd_processor.register_mention_handler("both", self._handle_mention)

    def run(self):
        """启动参与模式"""
        self.cli.show_welcome()
        
        topic = self.cli.get_user_input("请输入辩论主题")
        if not topic:
            self.cli.show_error("辩论主题不能为空！")
            return
            
        self._start_debate(topic)
        
        # 主循环，处理用户输入
        while self.debate_manager and self.debate_manager.is_running():
            try:
                user_input = self.cli.get_user_input("您的指令或消息")
                parsed_command = self.cmd_processor.parse_command(user_input)
                
                if not parsed_command.is_valid:
                    self.cli.show_error(parsed_command.error_message)
                    continue
                
                self.cmd_processor.execute_command(parsed_command)

            except (KeyboardInterrupt, EOFError):
                self._handle_end([])
                break
        
        self.cli.show_info("辩论已结束。")

    def _start_debate(self, topic: str):
        """初始化并启动辩论"""
        self.debate_manager = DebateManager(
            logician=self.logician,
            skeptic=self.skeptic,
            topic=topic,
            max_rounds=10,
            message_callback=self._handle_debate_message
        )
        
        self.debate_thread = threading.Thread(
            target=self.debate_manager.run_participation_mode,
            daemon=True
        )
        self.debate_thread.start()
        self.cli.show_success(f"辩论开始！主题: {topic}")

    def _handle_debate_message(self, message: Message):
        """处理来自辩论管理器的消息"""
        self.cli.display_message(message)

    # --- 指令处理函数 ---

    def _handle_pause(self, args):
        if self.debate_manager:
            self.debate_manager.pause_debate()
        return {"success": True}

    def _handle_resume(self, args):
        if self.debate_manager:
            self.debate_manager.resume_debate()
        return {"success": True}

    def _handle_end(self, args):
        if self.debate_manager:
            self.debate_manager.end_debate()
        return {"success": True}

    def _handle_status(self, args):
        if self.debate_manager:
            status = self.debate_manager.get_status()
            self.cli.show_info(f"状态: {status['state']}, 轮次: {status['current_round']}/{status['max_rounds']}")
        return {"success": True}

    def _handle_help(self, args):
        help_text = self.cmd_processor._handle_help_command(args)['content']
        self.cli.show_info(help_text)
        return {"success": True}

    def _handle_theme(self, args):
        if not args:
            self.cli.show_error("请提供主题名称, e.g., /theme dark")
            return {"success": False}
        
        theme_name = args[0]
        if self.cli.switch_theme(theme_name):
            self.cli.show_success(f"主题已切换到 {theme_name}")
        else:
            self.cli.show_error(f"未知主题: {theme_name}")
        return {"success": True}

    def _handle_clear(self, args):
        self.cli.console.clear()
        return {"success": True}

    def _handle_mention(self, target: str, content: str):
        if self.debate_manager:
            user_message = Message(
                content=content,
                sender="User",
                message_type=MessageType.USER_INPUT,
                metadata={"target": target}
            )
            self.debate_manager.add_user_message(user_message)
        return {"success": True}
