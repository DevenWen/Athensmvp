"""
设置向导模块
负责首次运行时的用户配置向导
"""

import logging
from typing import Dict, Any, List
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from ..config.user_config import UserConfigManager

logger = logging.getLogger(__name__)


class SetupWizard:
    """设置向导"""
    
    def __init__(self, config_manager: UserConfigManager):
        self.config_manager = config_manager
        self.console = Console()
        
    def run_first_time_setup(self) -> None:
        """运行首次设置向导"""
        try:
            self.console.print(Panel.fit(
                "🏛️ 欢迎使用 Athens MVP!\n\n"
                "这是您第一次运行系统，让我们来配置一些基本设置。\n"
                "所有设置稍后都可以在配置文件中修改。",
                title="首次运行设置向导",
                border_style="blue"
            ))
            
            # 收集基础设置
            basic_settings = self.prompt_basic_settings()
            
            # 收集Agent偏好设置
            agent_settings = self.prompt_agent_preferences()
            
            # 收集UI偏好设置
            ui_settings = self.prompt_ui_preferences()
            
            # 收集辩论设置
            debate_settings = self.prompt_debate_preferences()
            
            # 合并所有设置
            all_settings = {
                **basic_settings,
                "agent_settings": agent_settings,
                "ui_settings": ui_settings,
                "debate_settings": debate_settings
            }
            
            # 确认设置
            if self.confirm_settings(all_settings):
                self.apply_settings(all_settings)
                self.console.print("✅ 设置完成！欢迎使用Athens MVP!")
            else:
                self.console.print("❌ 设置已取消，将使用默认配置")
                
        except KeyboardInterrupt:
            self.console.print("\n❌ 设置向导被中断，将使用默认配置")
        except Exception as e:
            logger.error(f"设置向导失败: {e}")
            self.console.print(f"❌ 设置向导失败: {e}")
            self.console.print("将使用默认配置")
    
    def prompt_basic_settings(self) -> Dict[str, Any]:
        """提示基础设置"""
        self.console.print("\n🔧 基础设置")
        
        # 语言设置
        languages = {
            "1": ("zh_CN", "中文 (简体)"),
            "2": ("en_US", "English"),
            "3": ("zh_TW", "中文 (繁體)")
        }
        
        self.console.print("请选择界面语言:")
        for key, (code, name) in languages.items():
            self.console.print(f"  {key}. {name}")
        
        lang_choice = Prompt.ask("选择语言", choices=list(languages.keys()), default="1")
        selected_language = languages[lang_choice][0]
        
        # 自动保存设置
        auto_save = Confirm.ask("是否自动保存辩论记录?", default=True)
        
        # 历史记录限制
        history_limit = int(Prompt.ask("辩论历史记录保留数量", default="100"))
        
        return {
            "user_preferences": {
                "language": selected_language,
                "auto_save_debates": auto_save,
                "debate_history_limit": history_limit
            }
        }
    
    def prompt_agent_preferences(self) -> Dict[str, Any]:
        """提示Agent偏好设置"""
        self.console.print("\n🤖 AI智能体设置")
        
        # 模型选择
        models = {
            "1": "openai/gpt-4-turbo",
            "2": "openai/gpt-3.5-turbo",
            "3": "anthropic/claude-3-opus",
            "4": "anthropic/claude-3-sonnet",
            "5": "meta-llama/llama-3-70b-instruct"
        }
        
        self.console.print("可用的AI模型:")
        for key, model in models.items():
            self.console.print(f"  {key}. {model}")
        
        # Apollo模型选择
        apollo_choice = Prompt.ask("为Apollo选择模型", choices=list(models.keys()), default="1")
        apollo_model = models[apollo_choice]
        
        # Muses模型选择
        muses_choice = Prompt.ask("为Muses选择模型", choices=list(models.keys()), default="3")
        muses_model = models[muses_choice]
        
        # 温度设置
        use_custom_temp = Confirm.ask("是否自定义模型温度参数?", default=False)
        
        apollo_temp = 0.7
        muses_temp = 0.8
        
        if use_custom_temp:
            apollo_temp = float(Prompt.ask("Apollo模型温度 (0.0-1.0)", default="0.7"))
            muses_temp = float(Prompt.ask("Muses模型温度 (0.0-1.0)", default="0.8"))
        
        return {
            "apollo": {
                "model": apollo_model,
                "temperature": apollo_temp,
                "max_tokens": 2000
            },
            "muses": {
                "model": muses_model,
                "temperature": muses_temp,
                "max_tokens": 2000
            }
        }
    
    def prompt_ui_preferences(self) -> Dict[str, Any]:
        """提示UI偏好设置"""
        self.console.print("\n🎨 界面设置")
        
        # 主题选择
        themes = {
            "1": "default",
            "2": "dark", 
            "3": "forest",
            "4": "ocean",
            "5": "sunset",
            "6": "minimal"
        }
        
        self.console.print("选择界面主题:")
        for key, theme in themes.items():
            self.console.print(f"  {key}. {theme}")
        
        theme_choice = Prompt.ask("选择主题", choices=list(themes.keys()), default="4")
        selected_theme = themes[theme_choice]
        
        # 其他UI设置
        show_timestamps = Confirm.ask("是否显示时间戳?", default=True)
        show_typing = Confirm.ask("是否显示打字指示器?", default=True)
        auto_scroll = Confirm.ask("是否自动滚动?", default=True)
        
        return {
            "theme": selected_theme,
            "show_timestamps": show_timestamps,
            "show_typing_indicator": show_typing,
            "auto_scroll": auto_scroll,
            "input_box_style": "bordered"
        }
    
    def prompt_debate_preferences(self) -> Dict[str, Any]:
        """提示辩论偏好设置"""
        self.console.print("\n💭 辩论设置")
        
        # 最大轮数
        max_rounds = int(Prompt.ask("辩论最大轮数", default="20"))
        
        # 共识后自动结束
        auto_end_consensus = Confirm.ask("达成共识后自动结束辩论?", default=True)
        
        # 保存摘要
        save_summaries = Confirm.ask("是否保存辩论摘要?", default=True)
        
        # 摘要格式
        summary_formats = {
            "1": "markdown",
            "2": "json",
            "3": "plain_text"
        }
        
        if save_summaries:
            self.console.print("摘要格式:")
            for key, fmt in summary_formats.items():
                self.console.print(f"  {key}. {fmt}")
            
            format_choice = Prompt.ask("选择格式", choices=list(summary_formats.keys()), default="1")
            summary_format = summary_formats[format_choice]
        else:
            summary_format = "markdown"
        
        return {
            "max_rounds": max_rounds,
            "auto_end_after_consensus": auto_end_consensus,
            "save_summaries": save_summaries,
            "summary_format": summary_format
        }
    
    def confirm_settings(self, settings: Dict[str, Any]) -> bool:
        """确认设置"""
        self.console.print("\n📋 设置确认")
        
        # 创建设置摘要表格
        table = Table(title="您的配置摘要")
        table.add_column("设置项", style="cyan")
        table.add_column("值", style="magenta")
        
        # 基础设置
        user_prefs = settings.get("user_preferences", {})
        table.add_row("语言", user_prefs.get("language", "zh_CN"))
        table.add_row("自动保存", "是" if user_prefs.get("auto_save_debates") else "否")
        table.add_row("历史记录限制", str(user_prefs.get("debate_history_limit", 100)))
        
        # Agent设置
        agent_settings = settings.get("agent_settings", {})
        apollo_settings = agent_settings.get("apollo", {})
        muses_settings = agent_settings.get("muses", {})
        
        table.add_row("Apollo模型", apollo_settings.get("model", ""))
        table.add_row("Apollo温度", str(apollo_settings.get("temperature", 0.7)))
        table.add_row("Muses模型", muses_settings.get("model", ""))
        table.add_row("Muses温度", str(muses_settings.get("temperature", 0.8)))
        
        # UI设置
        ui_settings = settings.get("ui_settings", {})
        table.add_row("界面主题", ui_settings.get("theme", "default"))
        table.add_row("显示时间戳", "是" if ui_settings.get("show_timestamps") else "否")
        
        # 辩论设置
        debate_settings = settings.get("debate_settings", {})
        table.add_row("最大轮数", str(debate_settings.get("max_rounds", 20)))
        table.add_row("摘要格式", debate_settings.get("summary_format", "markdown"))
        
        self.console.print(table)
        
        return Confirm.ask("确认以上设置?", default=True)
    
    def apply_settings(self, settings: Dict[str, Any]) -> None:
        """应用设置"""
        try:
            # 应用基础设置
            user_prefs = settings.get("user_preferences", {})
            for key, value in user_prefs.items():
                self.config_manager.set_setting(f"user_preferences.{key}", value)
            
            # 应用Agent设置
            agent_settings = settings.get("agent_settings", {})
            for agent, config in agent_settings.items():
                for key, value in config.items():
                    self.config_manager.set_setting(f"agent_settings.{agent}.{key}", value)
            
            # 应用UI设置
            ui_settings = settings.get("ui_settings", {})
            for key, value in ui_settings.items():
                self.config_manager.set_setting(f"ui_settings.{key}", value)
            
            # 应用辩论设置
            debate_settings = settings.get("debate_settings", {})
            for key, value in debate_settings.items():
                self.config_manager.set_setting(f"debate_settings.{key}", value)
            
            # 保存配置
            self.config_manager.save_config()
            
            logger.info("设置向导完成，配置已保存")
            
        except Exception as e:
            logger.error(f"应用设置失败: {e}")
            raise
    
    def show_current_config(self) -> None:
        """显示当前配置"""
        self.console.print("\n📋 当前配置")
        
        config_info = self.config_manager.get_config_info()
        
        table = Table(title="配置信息")
        table.add_column("项目", style="cyan")
        table.add_column("值", style="magenta")
        
        table.add_row("配置文件路径", config_info["config_path"])
        table.add_row("版本", config_info["version"])
        table.add_row("创建时间", config_info["created_at"])
        table.add_row("更新时间", config_info["updated_at"])
        table.add_row("文件大小", f"{config_info['file_size']} bytes")
        
        self.console.print(table)
    
    def run_config_update(self) -> None:
        """运行配置更新向导"""
        self.console.print(Panel.fit(
            "🔧 配置更新向导\n\n"
            "选择您想要更新的配置项目",
            title="配置更新",
            border_style="green"
        ))
        
        options = {
            "1": ("基础设置", self.prompt_basic_settings),
            "2": ("AI智能体设置", self.prompt_agent_preferences),
            "3": ("界面设置", self.prompt_ui_preferences),
            "4": ("辩论设置", self.prompt_debate_preferences),
            "5": ("查看当前配置", lambda: None),
            "6": ("重置为默认配置", lambda: None)
        }
        
        while True:
            self.console.print("\n请选择要更新的项目:")
            for key, (name, _) in options.items():
                self.console.print(f"  {key}. {name}")
            self.console.print("  0. 退出")
            
            choice = Prompt.ask("请选择", choices=list(options.keys()) + ["0"])
            
            if choice == "0":
                break
            elif choice == "5":
                self.show_current_config()
            elif choice == "6":
                if Confirm.ask("确认重置为默认配置? 这将丢失所有自定义设置"):
                    self.config_manager.reset_to_defaults()
                    self.console.print("✅ 已重置为默认配置")
            else:
                try:
                    _, update_func = options[choice]
                    new_settings = update_func()
                    
                    if new_settings and self.confirm_settings(new_settings):
                        self.apply_settings(new_settings)
                        self.console.print("✅ 配置已更新")
                    else:
                        self.console.print("❌ 更新已取消")
                        
                except Exception as e:
                    self.console.print(f"❌ 更新失败: {e}")
        
        self.console.print("👋 感谢使用配置更新向导")