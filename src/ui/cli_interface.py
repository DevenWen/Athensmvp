"""
CLI用户界面
提供Athens系统的命令行交互界面，使用Rich库美化显示
"""

from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.layout import Layout
from rich.prompt import Prompt
from rich.style import Style
from rich.markdown import Markdown
from rich import box
from datetime import datetime

from src.core.message import Message
from src.core.debate_states import DebateState


class CLIInterface:
    """
    命令行界面控制器
    负责显示界面、处理用户输入和美化输出
    """
    
    # 预设主题配色方案
    THEMES = {
        "default": {
            "name": "默认主题",
            "title": "bold blue",
            "header": "bold green", 
            "apollo": "blue",
            "muses": "red",
            "user": "yellow",
            "system": "dim white",
            "success": "green",
            "error": "red",
            "warning": "yellow",
            "info": "cyan",
            "panel_title": "blue",
            "panel_border": {"apollo": "blue", "muses": "red", "user": "yellow", "system": "white"}
        },
        "dark": {
            "name": "深色主题",
            "title": "bold bright_white",
            "header": "bold bright_green", 
            "apollo": "bright_cyan",
            "muses": "bright_magenta",
            "user": "bright_yellow",
            "system": "dim bright_white",
            "success": "bright_green",
            "error": "bright_red",
            "warning": "bright_yellow",
            "info": "bright_blue",
            "panel_title": "bright_white",
            "panel_border": {"apollo": "bright_cyan", "muses": "bright_magenta", "user": "bright_yellow", "system": "bright_white"}
        },
        "forest": {
            "name": "森林主题",
            "title": "bold green",
            "header": "bold dark_green", 
            "apollo": "dark_green",
            "muses": "dark_orange3",
            "user": "gold1",
            "system": "dim grey70",
            "success": "green",
            "error": "red3",
            "warning": "orange3",
            "info": "dark_turquoise",
            "panel_title": "green",
            "panel_border": {"apollo": "dark_green", "muses": "dark_orange3", "user": "gold1", "system": "grey70"}
        },
        "ocean": {
            "name": "海洋主题",
            "title": "bold deep_sky_blue1",
            "header": "bold blue", 
            "apollo": "deep_sky_blue1",
            "muses": "medium_purple",
            "user": "turquoise2",
            "system": "dim slate_blue1",
            "success": "sea_green2",
            "error": "red",
            "warning": "orange1",
            "info": "cornflower_blue",
            "panel_title": "deep_sky_blue1",
            "panel_border": {"apollo": "deep_sky_blue1", "muses": "medium_purple", "user": "turquoise2", "system": "slate_blue1"}
        },
        "sunset": {
            "name": "日落主题",
            "title": "bold orange1",
            "header": "bold red", 
            "apollo": "orange1",
            "muses": "red3",
            "user": "yellow",
            "system": "dim grey70",
            "success": "green",
            "error": "red",
            "warning": "orange3",
            "info": "magenta",
            "panel_title": "orange1",
            "panel_border": {"apollo": "orange1", "muses": "red3", "user": "yellow", "system": "grey70"}
        },
        "minimal": {
            "name": "极简主题",
            "title": "bold white",
            "header": "bold white", 
            "apollo": "white",
            "muses": "grey70",
            "user": "bright_white",
            "system": "dim grey50",
            "success": "white",
            "error": "bright_white",
            "warning": "white",
            "info": "grey70",
            "panel_title": "white",
            "panel_border": {"apollo": "white", "muses": "grey70", "user": "bright_white", "system": "grey50"}
        }
    }
    
    def __init__(self, theme_name: str = "default"):
        self.console = Console()
        self.current_theme_name = theme_name
        self.theme = self.THEMES[theme_name]
    
    def show_welcome(self) -> None:
        """显示欢迎界面"""
        self.console.clear()
        
        # 创建标题面板
        title_text = Text("Athens 思辨广场 MVP", style="bold blue")
        title_text.append("\n智能辩论系统", style="dim white")
        
        title_panel = Panel(
            title_text,
            title="🏛️ 欢迎使用",
            title_align="center",
            box=box.DOUBLE,
            style="blue",
            padding=(1, 2)
        )
        
        self.console.print(title_panel)
        self.console.print()
        
        # 显示系统信息
        info_table = Table(show_header=False, box=box.SIMPLE)
        info_table.add_column("项目", style="dim white", no_wrap=True)
        info_table.add_column("描述", style="white")
        
        info_table.add_row("🤖 智能体", "逻辑者 & 怀疑者")
        info_table.add_row("💬 消息系统", "实时通信与上下文管理")
        info_table.add_row("🎯 辩论管理", "状态控制与轮次管理")
        info_table.add_row("👤 用户参与", "观察模式 & 参与模式")
        
        self.console.print(Panel(info_table, title="系统组件", border_style="green"))
        self.console.print()
    
    def show_menu(self) -> None:
        """显示主菜单"""
        menu_table = Table(show_header=False, box=box.ROUNDED)
        menu_table.add_column("选项", style="bold", width=8)
        menu_table.add_column("描述", style="white")
        menu_table.add_column("说明", style="dim white")
        
        menu_table.add_row(
            "[1]", 
            "观察模式", 
            "观看AI智能体自动辩论"
        )
        menu_table.add_row(
            "[2]", 
            "参与模式", 
            "在辩论中实时参与互动"
        )
        menu_table.add_row(
            "[3]", 
            "查看示例", 
            "运行预设话题的示例辩论"
        )
        menu_table.add_row(
            "[4]", 
            "帮助信息", 
            "了解使用方法和指令"
        )
        menu_table.add_row(
            "[0]", 
            "退出系统", 
            "结束程序"
        )
        
        self.console.print(Panel(menu_table, title="🎯 请选择模式", border_style="cyan"))
        self.console.print()
    
    def get_user_choice(self) -> str:
        """获取用户选择"""
        choice = Prompt.ask(
            "[bold cyan]请输入选项[/bold cyan]",
            choices=["0", "1", "2", "3", "4"],
            default="1"
        )
        return choice
    
    def get_user_input(self, prompt: str = "请输入") -> str:
        """获取用户输入"""
        return Prompt.ask(f"[bold yellow]{prompt}[/bold yellow]")
    
    def display_message(self, message: Message) -> None:
        """显示单条消息（带边框的富文本格式）"""
        # 获取发送者名称（如果是对象，提取其名称或类名）
        sender_name = self._get_sender_display_name(message.sender)
        
        # 根据发送者选择样式
        if sender_name in ["Apollo", "逻辑者", "Logician"] or "apollo" in sender_name.lower() or "logician" in sender_name.lower():
            style = self.theme["apollo"]
            icon = "🤔"
            border_style = self.theme["panel_border"]["apollo"]
            display_name = "Apollo"
        elif sender_name in ["Muses", "怀疑者", "Skeptic"] or "muses" in sender_name.lower() or "skeptic" in sender_name.lower():
            style = self.theme["muses"] 
            icon = "🤨"
            border_style = self.theme["panel_border"]["muses"]
            display_name = "Muses"
        elif sender_name in ["用户", "User"] or "user" in sender_name.lower():
            style = self.theme["user"]
            icon = "👤"
            border_style = self.theme["panel_border"]["user"]
            display_name = "用户"
        else:
            style = self.theme["system"]
            icon = "💬"
            border_style = self.theme["panel_border"]["system"]
            display_name = sender_name
        
        # 格式化时间
        time_str = message.timestamp.strftime("%H:%M:%S")
        
        # 创建标题（发送者和时间）
        title = f"{icon} {display_name} [{time_str}]"
        
        # 使用Markdown渲染消息内容
        markdown_content = Markdown(message.content)
        
        # 创建带边框的消息面板
        message_panel = Panel(
            markdown_content,
            title=title,
            title_align="left",
            border_style=border_style,
            box=box.ROUNDED,
            padding=(0, 1),
            width=80  # 固定宽度确保一致性
        )
        
        self.console.print(message_panel)
    
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
    
    def switch_theme(self, theme_name: str) -> bool:
        """切换主题"""
        if theme_name in self.THEMES:
            self.current_theme_name = theme_name
            self.theme = self.THEMES[theme_name]
            return True
        return False
    
    def show_theme_selector(self) -> str:
        """显示主题选择器"""
        self.console.print(Panel("🎨 主题选择器", border_style=self.theme["panel_title"]))
        
        theme_table = Table(show_header=False, box=box.ROUNDED)
        theme_table.add_column("编号", style="bold", width=6)
        theme_table.add_column("主题名", style="white", width=15)
        theme_table.add_column("描述", style="dim white")
        theme_table.add_column("当前", style="green", width=6)
        
        for i, (key, config) in enumerate(self.THEMES.items(), 1):
            current = "✅" if key == self.current_theme_name else ""
            theme_table.add_row(
                f"[{i}]",
                config["name"],
                f"智能体: {config['apollo']}, {config['muses']}, {config['user']}",
                current
            )
        
        self.console.print(theme_table)
        
        choice = Prompt.ask(
            "[bold cyan]请选择主题[/bold cyan]",
            choices=["1", "2", "3", "4", "5", "6"],
            default="1"
        )
        
        theme_keys = list(self.THEMES.keys())
        selected_theme = theme_keys[int(choice) - 1]
        
        return selected_theme
    
    def demo_all_themes(self) -> None:
        """演示所有主题效果"""
        from src.core.message import Message, MessageType
        
        # 创建示例消息
        sample_msg = Message(
            "# 主题演示\n\n这是一个**示例消息**，用来展示*不同主题*的效果。\n\n- 列表项1\n- `代码示例`\n\n> 引用文本示例",
            "逻辑者",
            MessageType.ARGUMENT
        )
        
        for theme_name, theme_config in self.THEMES.items():
            self.console.print(f"\n[bold white]🎨 {theme_config['name']} ({theme_name})[/bold white]")
            self.console.print("─" * 60)
            
            # 临时切换主题
            old_theme = self.current_theme_name
            self.switch_theme(theme_name)
            
            # 显示示例消息
            self.display_message(sample_msg)
            
            # 恢复原主题
            self.switch_theme(old_theme)
    
    def show_success(self, message: str) -> None:
        """显示成功消息"""
        self.console.print(f"[green]✅ {message}[/green]")
    
    def show_error(self, message: str) -> None:
        """显示错误消息"""
        self.console.print(f"[red]❌ {message}[/red]")
    
    def show_warning(self, message: str) -> None:
        """显示警告消息"""
        self.console.print(f"[yellow]⚠️ {message}[/yellow]")
    
    def show_info(self, message: str) -> None:
        """显示信息消息"""
        self.console.print(f"[cyan]ℹ️ {message}[/cyan]")


# 简单的测试函数
def demo_cli():
    """演示CLI界面效果"""
    cli = CLIInterface()
    
    # 显示欢迎界面
    cli.show_welcome()
    
    # 显示菜单
    cli.show_menu()
    
    # 主题选择
    print("\n是否要切换主题？(y/n): ", end="")
    if input().lower() == 'y':
        selected_theme = cli.show_theme_selector()
        cli.switch_theme(selected_theme)
        cli.show_success(f"已切换到 {cli.theme['name']}")
        
        # 重新显示欢迎界面展示新主题
        cli.show_welcome()
    
    # 演示消息显示
    from src.core.message import Message, MessageType
    
    cli.console.print(Panel("消息显示效果演示", title="📝 Demo", border_style=cli.theme["panel_title"]))
    
    # 创建示例消息（标准Markdown格式）
    apollo_msg = Message(
        """# Elixir容错性分析

基于**Actor模型**，Elixir确实具有*出色的容错性*和并发处理能力。

## 关键特性

1. **Let it crash哲学**
   - 进程隔离确保错误不会传播
   - 失败快速，恢复迅速

2. **轻量级进程**
   - 可以创建数百万个独立进程
   - 内存占用极小（~2KB）

3. **监督树机制**
   - 自动重启失败的进程
   - 层次化的错误处理

> 这些特性使得Elixir在构建**高可用系统**方面具有天然优势。

```elixir
# 示例代码
{:ok, pid} = GenServer.start_link(MyServer, [])
GenServer.call(pid, :get_state)
```""",
        "Apollo",
        MessageType.ARGUMENT
    )
    
    muses_msg = Message(
        """## 对Actor模型的质疑

虽然**Actor模型**确实有优势，但这种说法过于*绝对*。

### 需要考虑的问题

- **性能开销**
  - 消息传递比共享内存慢
  - 序列化/反序列化成本
  
- **瓶颈问题**
  - `GenServer`单点可能成为瓶颈
  - 热点进程处理能力有限

- **学习曲线**
  - 函数式编程思维转换困难
  - OTP设计模式复杂

### 结论

在某些场景下，传统的**多线程模型**可能更适合：

| 场景 | Elixir | 传统多线程 |
|------|--------|------------|
| CPU密集 | ❌ | ✅ |
| I/O密集 | ✅ | ❌ |
| 高并发 | ✅ | ❌ |""",
        "Muses", 
        MessageType.COUNTER
    )
    
    user_msg = Message(
        """@muses 关于性能开销的问题很有意思！

> 能否提供一个**具体的基准测试**数据来支撑你的观点？

特别想了解：
- `消息传递 vs 共享内存`的*性能对比*
- 不同并发量下的表现差异
- 实际生产环境的案例

期待你的详细分析！""",
        "用户",
        MessageType.USER_INPUT
    )
    
    system_msg = Message(
        """### 系统通知

**状态更新**：检测到用户提及 `@muses`

- ✅ 已通知Muses智能体
- 📊 当前辩论状态：*活跃中*
- ⏱️ 响应时间：< 100ms""",
        "系统",
        MessageType.GENERAL
    )
    
    # 显示消息
    cli.display_message(apollo_msg)
    cli.display_message(muses_msg)
    cli.display_message(user_msg)
    cli.display_message(system_msg)
    
    # 显示各种状态消息
    cli.show_success("CLI界面基础功能完成")
    cli.show_info("这是一个信息提示")
    cli.show_warning("这是一个警告提示")
    cli.show_error("这是一个错误提示")


if __name__ == "__main__":
    demo_cli()