"""
实时显示管理器
使用Rich的Live显示和Layout管理实时更新的UI界面
"""

import threading
import time
import queue
from typing import List, Optional, Dict, Any
from datetime import datetime

from rich.console import Console, Group
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich import box

from src.core.message import Message
from src.core.debate_states import DebateState


class RealTimeDisplay:
    """
    实时显示管理器
    管理分离的消息显示区域和用户输入区域
    """
    
    def __init__(self, theme: Dict[str, Any]):
        self.console = Console()
        self.theme = theme
        
        # 消息历史和状态
        self.messages: List[Message] = []
        self.status_info: Dict[str, Any] = {}
        self.max_displayed_messages = 10
        
        # 线程安全的更新队列
        self.update_queue = queue.Queue()
        self.is_running = False
        
        # 创建布局
        self.layout = Layout()
        self._setup_layout()
        
        # Live显示对象
        self.live: Optional[Live] = None
        
        # 输入处理
        self.input_prompt = "💬 输入消息或指令"
        self.show_input_hint = True
    
    def _setup_layout(self) -> None:
        """设置UI布局"""
        # 创建主要布局区域
        self.layout.split_column(
            Layout(name="header", size=4),      # 标题和状态栏
            Layout(name="messages", ratio=1),   # 消息显示区域  
            Layout(name="input_area", size=3)   # 输入提示区域
        )
        
        # 初始化各个区域
        self._update_header()
        self._update_messages()
        self._update_input_area()
    
    def _update_header(self) -> None:
        """更新头部区域"""
        if not self.status_info:
            header_content = Panel(
                "🏛️ Athens 思辨广场 - 准备中...",
                style=self.theme.get("panel_title", "blue"),
                box=box.ROUNDED
            )
        else:
            # 创建状态表格
            status_table = Table(show_header=False, box=None, padding=(0, 1))
            status_table.add_column("项目", style="dim white", width=12)
            status_table.add_column("信息", style="white")
            
            status_table.add_row("话题", f"[bold]{self.status_info.get('topic', 'N/A')}[/bold]")
            status_table.add_row("状态", f"[green]{self.status_info.get('state', 'N/A')}[/green]")
            status_table.add_row("轮次", f"{self.status_info.get('current_round', 0)}/{self.status_info.get('max_rounds', 0)}")
            status_table.add_row("参与者", "逻辑者, 怀疑者, [yellow]用户[/yellow]")
            
            header_content = Panel(
                status_table,
                title="🏛️ Athens 思辨广场 - 参与模式",
                border_style=self.theme.get("panel_title", "blue"),
                box=box.ROUNDED
            )
        
        self.layout["header"].update(header_content)
    
    def _update_messages(self) -> None:
        """更新消息显示区域"""
        if not self.messages:
            placeholder = Panel(
                Text("等待消息...", style="dim white", justify="center"),
                title="📝 对话记录",
                border_style=self.theme.get("panel_title", "blue"),
                box=box.ROUNDED
            )
            self.layout["messages"].update(placeholder)
            return
        
        # 获取最近的消息
        recent_messages = self.messages[-self.max_displayed_messages:]
        
        # 创建消息组
        message_panels = []
        for message in recent_messages:
            panel = self._create_message_panel(message)
            message_panels.append(panel)
        
        # 如果消息太多，显示省略提示
        if len(self.messages) > self.max_displayed_messages:
            omitted_count = len(self.messages) - self.max_displayed_messages
            omitted_text = Text(f"... (省略了 {omitted_count} 条更早的消息)", style="dim white", justify="center")
            message_panels.insert(0, omitted_text)
        
        # 创建消息容器
        messages_group = Group(*message_panels)
        
        messages_container = Panel(
            messages_group,
            title="📝 对话记录",
            border_style=self.theme.get("panel_title", "blue"),
            box=box.ROUNDED
        )
        
        self.layout["messages"].update(messages_container)
    
    def _create_message_panel(self, message: Message) -> Panel:
        """创建单个消息面板"""
        # 获取发送者名称（如果是对象，提取其名称或类名）
        sender_name = self._get_sender_display_name(message.sender)
        
        # 根据发送者选择样式
        if sender_name in ["Apollo", "逻辑者", "Logician"] or "apollo" in sender_name.lower() or "logician" in sender_name.lower():
            icon = "🤔"
            border_style = self.theme.get("panel_border", {}).get("apollo", "blue")
            display_name = "Apollo"
        elif sender_name in ["Muses", "怀疑者", "Skeptic"] or "muses" in sender_name.lower() or "skeptic" in sender_name.lower():
            icon = "🤨"
            border_style = self.theme.get("panel_border", {}).get("muses", "red")
            display_name = "Muses"
        elif sender_name in ["用户", "User"] or "user" in sender_name.lower():
            icon = "👤"
            border_style = self.theme.get("panel_border", {}).get("user", "yellow")
            display_name = "用户"
        else:
            icon = "💬"
            border_style = self.theme.get("panel_border", {}).get("system", "white")
            display_name = sender_name
        
        # 格式化时间
        time_str = message.timestamp.strftime("%H:%M:%S")
        title = f"{icon} {display_name} [{time_str}]"
        
        # 使用Markdown渲染内容
        content = Markdown(message.content)
        
        return Panel(
            content,
            title=title,
            title_align="left",
            border_style=border_style,
            box=box.ROUNDED,
            padding=(0, 1)
        )
    
    def _get_sender_display_name(self, sender) -> str:
        """获取发送者的显示名称"""
        if isinstance(sender, str):
            return sender
        elif hasattr(sender, 'name'):
            return sender.name
        elif hasattr(sender, '__class__'):
            class_name = sender.__class__.__name__
            if 'Logician' in class_name:
                return "逻辑者"
            elif 'Skeptic' in class_name:
                return "怀疑者"
            else:
                return class_name
        else:
            return str(sender)
    
    def _update_input_area(self) -> None:
        """更新输入区域"""
        if self.show_input_hint:
            input_text = Text()
            input_text.append("💬 ", style="yellow")
            input_text.append(self.input_prompt, style="dim white")
            input_text.append("\n")
            input_text.append("提示: 使用 @apollo/@muses 提及智能体，/help 查看指令", style="dim cyan")
            
            input_panel = Panel(
                input_text,
                title="输入区域",
                border_style="dim white",
                box=box.SIMPLE
            )
        else:
            input_panel = Panel(
                Text("", style="dim white"),
                title="输入区域", 
                border_style="dim white",
                box=box.SIMPLE
            )
        
        self.layout["input_area"].update(input_panel)
    
    def start_display(self) -> None:
        """启动实时显示"""
        self.is_running = True
        self.live = Live(
            self.layout,
            console=self.console,
            refresh_per_second=10,
            screen=True
        )
        self.live.start()
        
        # 启动更新处理线程
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def stop_display(self) -> None:
        """停止实时显示"""
        self.is_running = False
        if self.live:
            self.live.stop()
    
    def _update_loop(self) -> None:
        """更新循环（在独立线程中运行）"""
        error_count = 0
        max_errors = 10
        
        while self.is_running:
            try:
                # 处理队列中的更新请求
                while not self.update_queue.empty():
                    try:
                        update_type, data = self.update_queue.get_nowait()
                        
                        if update_type == "message":
                            if data and hasattr(data, 'content'):
                                self.messages.append(data)
                                self._update_messages()
                        elif update_type == "status":
                            if isinstance(data, dict):
                                self.status_info.update(data)
                                self._update_header()
                        elif update_type == "input_hint":
                            if isinstance(data, str):
                                self.input_prompt = data
                                self._update_input_area()
                        elif update_type == "clear_messages":
                            self.messages.clear()
                            self._update_messages()
                            
                        error_count = 0  # 重置错误计数
                        
                    except Exception as e:
                        error_count += 1
                        if error_count >= max_errors:
                            # 如果错误过多，停止更新循环
                            self.is_running = False
                            break
                
                time.sleep(0.1)  # 避免过度CPU使用
                
            except Exception as e:
                error_count += 1
                if error_count >= max_errors:
                    self.is_running = False
                    break
                time.sleep(0.5)  # 错误后等待更长时间
    
    def add_message(self, message: Message) -> None:
        """添加新消息"""
        self.update_queue.put(("message", message))
    
    def update_status(self, status_data: Dict[str, Any]) -> None:
        """更新状态信息"""
        self.update_queue.put(("status", status_data))
    
    def set_input_hint(self, hint: str) -> None:
        """设置输入提示"""
        self.update_queue.put(("input_hint", hint))
    
    def clear_messages(self) -> None:
        """清空消息"""
        self.update_queue.put(("clear_messages", None))
    
    def show_thinking(self, agent_name: str) -> None:
        """显示智能体思考状态"""
        thinking_hint = f"{agent_name} 正在思考中..."
        self.set_input_hint(thinking_hint)
        
        # 3秒后恢复正常提示
        def restore_hint():
            time.sleep(3)
            self.set_input_hint("💬 输入消息或指令")
        
        threading.Thread(target=restore_hint, daemon=True).start()
    
    def get_user_input(self, prompt: str = "请输入") -> str:
        """获取用户输入（非阻塞方式）"""
        # 临时停止Live显示以获取输入
        live_was_running = False
        if self.live:
            try:
                self.live.stop()
                live_was_running = True
            except:
                pass
        
        try:
            # 显示输入提示
            self.console.print(f"\n[bold yellow]💬 {prompt}:[/bold yellow] ", end="")
            user_input = input()
            return user_input.strip()
        except (KeyboardInterrupt, EOFError):
            # 用户中断输入
            return ""
        except Exception:
            # 其他输入错误
            return ""
        finally:
            # 重新启动Live显示
            if live_was_running and self.is_running:
                try:
                    if self.live:
                        self.live.start()
                except:
                    pass


class NonBlockingInput:
    """
    非阻塞输入处理器
    使用独立线程处理用户输入，避免阻塞显示更新
    """
    
    def __init__(self, callback_func):
        self.callback_func = callback_func
        self.is_running = False
        self.input_thread: Optional[threading.Thread] = None
    
    def start(self) -> None:
        """启动输入处理"""
        self.is_running = True
        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()
    
    def stop(self) -> None:
        """停止输入处理"""
        self.is_running = False
    
    def _input_loop(self) -> None:
        """输入处理循环"""
        while self.is_running:
            try:
                # 使用标准输入获取用户输入
                user_input = input()
                if user_input.strip() and self.callback_func:
                    self.callback_func(user_input.strip())
            except (EOFError, KeyboardInterrupt):
                break
            except Exception as e:
                # 错误处理
                pass


# 演示函数
def demo_realtime_display():
    """演示实时显示功能"""
    from src.core.message import Message, MessageType
    from src.ui.cli_interface import CLIInterface
    
    # 创建显示管理器
    cli = CLIInterface("ocean")
    display = RealTimeDisplay(cli.theme)
    
    # 设置初始状态
    display.update_status({
        "topic": "人工智能技术对社会的影响",
        "state": "active",
        "current_round": 2,
        "max_rounds": 5
    })
    
    # 启动显示
    display.start_display()
    
    try:
        # 模拟消息流
        messages = [
            Message("AI技术确实在改变我们的生活方式", "逻辑者", MessageType.ARGUMENT),
            Message("但我们需要考虑其负面影响", "Muses", MessageType.COUNTER),
            Message("@apollo 你能提供更多具体例子吗？", "用户", MessageType.USER_INPUT),
            Message("当然，比如在医疗、教育、交通等领域...", "Apollo", MessageType.CLARIFICATION),
        ]
        
        # 逐个添加消息，模拟实时对话
        for i, msg in enumerate(messages):
            time.sleep(2)  # 模拟消息间隔
            display.add_message(msg)
            
            # 更新状态
            display.update_status({
                "topic": "人工智能技术对社会的影响",
                "state": "active", 
                "current_round": i + 1,
                "max_rounds": 5
            })
        
        # 等待用户观察
        time.sleep(10)
        
    finally:
        display.stop_display()
        print("实时显示演示结束")


if __name__ == "__main__":
    demo_realtime_display()