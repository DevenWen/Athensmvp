"""
参与模式控制器
负责协调CLI界面、指令处理器和辩论管理器，实现用户参与的完整流程
"""

import threading
from typing import Optional

from src.core.ai_client import AIClient
from src.core.debate_manager import DebateManager
from src.core.debate_states import DebateState
from src.agents.apollo import Apollo
from src.agents.muses import Muses
from src.core.message import Message, MessageType
from src.ui.cli_interface import CLIInterface
from src.ui.command_processor import CommandProcessor, ParsedCommand, CommandType

class ParticipationMode:
    """
    参与模式控制器
    """
    def __init__(self, theme_name: str = "default"):
        self.cli = CLIInterface(theme_name=theme_name)
        self.cmd_processor = CommandProcessor()
        self.ai_client = AIClient()
        
        self.apollo = Apollo(self.ai_client)
        self.muses = Muses(self.ai_client)
        
        # 向后兼容的别名
        self.logician = self.apollo
        self.skeptic = self.muses
        
        self.debate_manager: Optional[DebateManager] = None
        self.debate_thread: Optional[threading.Thread] = None
        self.displayed_message_count = 0  # 追踪已显示的消息数量
        
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
        
        self.cmd_processor.register_mention_handler("apollo", self._handle_mention)
        self.cmd_processor.register_mention_handler("muses", self._handle_mention)
        # 向后兼容
        self.cmd_processor.register_mention_handler("logician", self._handle_mention)
        self.cmd_processor.register_mention_handler("skeptic", self._handle_mention)
        self.cmd_processor.register_mention_handler("both", self._handle_mention)

    def run(self):
        """启动参与模式"""
        try:
            self.cli.show_welcome()
            
            # 输入验证循环
            topic = None
            while not topic:
                try:
                    topic = self.cli.get_user_input("请输入辩论主题")
                    if not topic or not topic.strip():
                        self.cli.show_error("辩论主题不能为空，请重新输入！")
                        topic = None
                        continue
                    topic = topic.strip()
                except (KeyboardInterrupt, EOFError):
                    self.cli.show_info("用户取消输入，退出参与模式")
                    return
                except Exception as e:
                    self.cli.show_error(f"输入错误: {e}")
                    continue
                
            if not self._start_debate(topic):
                self.cli.show_error("辩论启动失败，请检查系统配置")
                return
            
            # 主循环，处理用户输入
            consecutive_errors = 0
            max_consecutive_errors = 3
            
            while self.debate_manager and self._is_debate_active():
                try:
                    # 处理一轮辩论
                    if self.debate_manager.state == DebateState.ACTIVE:
                        try:
                            # 处理辩论轮次 - AI回复会通过回调自动显示
                            self.debate_manager.process_round()
                            consecutive_errors = 0  # 重置错误计数
                        except Exception as e:
                            self.cli.show_error(f"辩论处理出错: {e}")
                            consecutive_errors += 1
                            if consecutive_errors >= max_consecutive_errors:
                                self.cli.show_error("连续错误过多，辩论将被终止")
                                break
                    
                    try:
                        user_input = self.cli.get_user_input("您的指令或消息")
                        if not user_input:
                            continue
                            
                        parsed_command = self.cmd_processor.parse_command(user_input)
                        
                        if not parsed_command.is_valid:
                            self.cli.show_error(parsed_command.error_message)
                            # 提供帮助提示
                            self.cli.show_info("输入 /help 查看可用指令")
                            continue
                        
                        result = self.cmd_processor.execute_command(parsed_command)
                        if not result.get("success", True):
                            self.cli.show_error(result.get("error", "指令执行失败"))
                            
                    except (KeyboardInterrupt, EOFError):
                        self.cli.show_info("检测到用户中断信号")
                        if self._confirm_exit():
                            break
                    except Exception as e:
                        self.cli.show_error(f"指令处理出错: {e}")
                        consecutive_errors += 1
                        if consecutive_errors >= max_consecutive_errors:
                            self.cli.show_error("系统错误过多，将退出参与模式")
                            break

                except Exception as e:
                    self.cli.show_error(f"主循环出错: {e}")
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        self.cli.show_error("系统不稳定，强制退出")
                        break
                    
        except Exception as e:
            self.cli.show_error(f"参与模式严重错误: {e}")
        finally:
            # 确保清理资源
            try:
                if self.debate_manager:
                    self.debate_manager.end_debate()
            except:
                pass
            self.cli.show_info("辩论已结束。")

    def start_participation_mode(self):
        """启动参与模式（别名方法）"""
        self.run()

    def _start_debate(self, topic: str):
        """初始化并启动辩论"""
        try:
            self.debate_manager = DebateManager(
                apollo=self.apollo,
                muses=self.muses,
                topic=topic,
                max_rounds=10
            )
            
            # 设置消息回调，确保AI回复能实时显示
            self.debate_manager.on_message_sent = self._handle_debate_message
            
            # 启动辩论（这里我们需要手动开始辩论而不是在后台线程中运行）
            if self.debate_manager.start_debate():
                self.cli.show_success(f"辩论开始！主题: {topic}")
                # 显示初始消息
                self._display_latest_messages()
                return True
            else:
                self.cli.show_error("无法启动辩论")
                return False
        except Exception as e:
            self.cli.show_error(f"启动辩论时出错: {e}")
            return False
    
    def _confirm_exit(self):
        """确认是否退出"""
        try:
            choice = self.cli.get_user_input("确定要退出参与模式吗？(y/N)")
            return choice.lower() in ['y', 'yes', '是', '确定']
        except:
            return True  # 如果无法获取输入，默认退出

    def _is_debate_active(self) -> bool:
        """检查辩论是否仍在进行中"""
        if not self.debate_manager:
            return False
        return self.debate_manager.state in [DebateState.ACTIVE, DebateState.PAUSED]
    
    def _display_latest_messages(self):
        """显示最新的辩论消息"""
        if not self.debate_manager:
            return
        
        # 获取对话历史并显示新消息
        history = self.debate_manager.get_conversation_history()
        new_messages = history[self.displayed_message_count:]
        
        for message in new_messages:
            self.cli.display_message(message)
        
        self.displayed_message_count = len(history)
    
    def _handle_debate_message(self, message: Message):
        """处理来自辩论管理器的消息"""
        # 立即显示AI生成的消息
        self.cli.display_message(message)
        # 更新显示计数器
        self.displayed_message_count = len(self.debate_manager.get_conversation_history())

    # --- 指令处理函数 ---

    def _handle_pause(self, args):
        try:
            if self.debate_manager:
                self.debate_manager.pause_debate()
                self.cli.show_success("辩论已暂停")
            else:
                self.cli.show_warning("没有进行中的辩论")
            return {"success": True}
        except Exception as e:
            self.cli.show_error(f"暂停辩论失败: {e}")
            return {"success": False, "error": str(e)}

    def _handle_resume(self, args):
        try:
            if self.debate_manager:
                self.debate_manager.resume_debate()
                self.cli.show_success("辩论已继续")
            else:
                self.cli.show_warning("没有进行中的辩论")
            return {"success": True}
        except Exception as e:
            self.cli.show_error(f"继续辩论失败: {e}")
            return {"success": False, "error": str(e)}

    def _handle_end(self, args):
        try:
            if self.debate_manager:
                self.debate_manager.end_debate()
                self.cli.show_success("辩论已结束")
            else:
                self.cli.show_warning("没有进行中的辩论")
            return {"success": True}
        except Exception as e:
            self.cli.show_error(f"结束辩论失败: {e}")
            return {"success": False, "error": str(e)}

    def _handle_status(self, args):
        try:
            if self.debate_manager:
                status = self.debate_manager.get_debate_status()
                self.cli.show_info(f"状态: {status['state']}, 轮次: {status['current_round']}/{status['max_rounds']}")
            else:
                self.cli.show_info("当前没有进行中的辩论")
            return {"success": True}
        except Exception as e:
            self.cli.show_error(f"获取状态失败: {e}")
            return {"success": False, "error": str(e)}

    def _handle_help(self, args):
        try:
            help_text = self.cmd_processor._handle_help_command(args)['content']
            self.cli.show_info(help_text)
            return {"success": True}
        except Exception as e:
            self.cli.show_error(f"显示帮助失败: {e}")
            return {"success": False, "error": str(e)}

    def _handle_theme(self, args):
        try:
            if not args:
                available_themes = list(self.cli.THEMES.keys())
                self.cli.show_error(f"请提供主题名称，可用主题: {', '.join(available_themes)}")
                return {"success": False, "error": "缺少主题名称"}
            
            theme_name = args[0]
            if self.cli.switch_theme(theme_name):
                self.cli.show_success(f"主题已切换到 {theme_name}")
            else:
                available_themes = list(self.cli.THEMES.keys())
                self.cli.show_error(f"未知主题: {theme_name}，可用主题: {', '.join(available_themes)}")
                return {"success": False, "error": f"未知主题: {theme_name}"}
            return {"success": True}
        except Exception as e:
            self.cli.show_error(f"切换主题失败: {e}")
            return {"success": False, "error": str(e)}

    def _handle_clear(self, args):
        try:
            self.cli.console.clear()
            self.cli.show_success("屏幕已清空")
            return {"success": True}
        except Exception as e:
            self.cli.show_error(f"清空屏幕失败: {e}")
            return {"success": False, "error": str(e)}

    def _handle_mention(self, target: str, content: str):
        try:
            if not self.debate_manager:
                self.cli.show_warning("没有进行中的辩论，消息未发送")
                return {"success": False, "error": "没有进行中的辩论"}
                
            user_message = Message(
                content=content,
                sender="用户",
                message_type=MessageType.USER_INPUT,
                metadata={"target": target}
            )
            # 将用户消息添加到对话历史中
            self.debate_manager.conversation.add_message(user_message)
            self.cli.display_message(user_message)
            self.cli.show_success(f"消息已发送给 {target}")
            return {"success": True}
        except Exception as e:
            self.cli.show_error(f"发送消息失败: {e}")
            return {"success": False, "error": str(e)}
