import sys
import os
import logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.ai_client import AIClient
from src.core.debate_manager import DebateManager
from src.agents.apollo import Apollo
from src.agents.muses import Muses
from src.config.settings import Settings
from src.config.user_config import UserConfigManager
from src.config.config_init import ConfigInitializer
from src.config.prompt_loader import PromptLoader
from src.config.prompts import PromptConfig
from src.ui.cli_interface import CLIInterface
from src.ui.participation_mode import ParticipationMode
from src.ui.setup_wizard import SetupWizard

logger = logging.getLogger(__name__)

def run_demo_debate(settings=None):
    """运行演示辩论"""
    print("\n🎯 运行演示辩论...")
    
    try:
        # 使用传入的settings或创建默认的
        if settings is None:
            settings = Settings()
        
        # 初始化AI客户端
        ai_client = AIClient()
        
        # 创建智能体
        apollo = Apollo(ai_client=ai_client)
        muses = Muses(ai_client=ai_client)
        
        # 获取辩论配置
        debate_config = settings.get_debate_config()
        
        # 创建辩论管理器
        manager = DebateManager(
            apollo=apollo,
            muses=muses,
            topic="人工智能技术的发展前景",
            max_rounds=debate_config.get("max_rounds", 2)
        )
        
        print("📍 开始观察模式辩论...")
        
        # 运行观察模式
        summary = manager.run_observation_mode()
        
        print("\n📊 辩论结果:")
        print(f"状态: {summary['debate_info']['state']}")
        print(f"轮次: {summary['debate_info']['current_round']}")
        print(f"消息数: {summary['metrics']['total_messages']}")
        print(f"持续时间: {summary['debate_info']['duration']:.1f}秒")
        
        print("\n💬 对话摘要:")
        for i, message in enumerate(manager.get_conversation_history()[-4:], 1):  # 显示最后4条消息
            print(f"{i}. {message.sender}: {message.content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 演示辩论失败: {e}")
        print("可能的原因:")
        print("- 缺少OPENROUTER_API_KEY环境变量")
        print("- 网络连接问题")
        print("- API配额不足")
        return False

def show_main_menu(settings=None):
    """显示主菜单并获取用户选择"""
    if settings is None:
        settings = Settings()
    
    cli = CLIInterface()
    cli.show_welcome()
    cli.show_menu()
    
    choice = cli.get_user_choice()
    return choice, cli

def run_observation_mode(settings=None):
    """运行观察模式（AI自动辩论）"""
    print("\n🔍 启动观察模式...")
    return run_demo_debate(settings)

def run_participation_mode(settings=None):
    """运行参与模式（用户交互辩论）"""
    print("\n👤 启动参与模式...")
    
    if settings is None:
        settings = Settings()
    
    # 主题选择
    cli = CLIInterface()
    ui_config = settings.get_ui_config()
    saved_theme = ui_config.get("theme", "ocean")
    
    themes = ["default", "dark", "forest", "ocean", "sunset", "minimal"]
    
    cli.console.print("🎨 选择界面主题：")
    for i, theme in enumerate(themes, 1):
        indicator = " (已保存)" if theme == saved_theme else ""
        cli.console.print(f"  {i}. {theme}{indicator}")
    
    choice = cli.get_user_input(f"请选择主题（1-6，默认使用已保存的: {saved_theme}）")
    try:
        if choice:
            theme_index = int(choice) - 1
            if 0 <= theme_index < len(themes):
                selected_theme = themes[theme_index]
            else:
                selected_theme = saved_theme
        else:
            selected_theme = saved_theme
    except ValueError:
        selected_theme = saved_theme
    
    # 保存用户选择的主题
    if selected_theme != saved_theme:
        settings.update_ui_config({"theme": selected_theme})
        cli.show_info(f"主题偏好已保存: {selected_theme}")
    
    cli.show_success(f"已选择主题: {selected_theme}")
    
    try:
        # 启动参与模式
        mode = ParticipationMode(selected_theme)
        mode.start_participation_mode()
        return True
        
    except KeyboardInterrupt:
        cli.show_info("用户中断，退出参与模式")
        return True
    except Exception as e:
        cli.show_error(f"参与模式运行出错: {e}")
        return False

def run_example_debates():
    """运行预设话题的示例辩论"""
    cli = CLIInterface()
    
    example_topics = [
        "人工智能技术对社会的影响",
        "Elixir具有很强的容错性",
        "远程工作是否比办公室工作更高效",
        "加密货币是否是未来货币的发展方向"
    ]
    
    cli.console.print("📝 选择示例话题：")
    for i, topic in enumerate(example_topics, 1):
        cli.console.print(f"  {i}. {topic}")
    
    choice = cli.get_user_input("请选择话题（1-4，默认1）")
    try:
        topic_index = int(choice) - 1 if choice else 0
        if 0 <= topic_index < len(example_topics):
            selected_topic = example_topics[topic_index]
        else:
            selected_topic = example_topics[0]
    except ValueError:
        selected_topic = example_topics[0]
    
    cli.show_info(f"选择的话题: {selected_topic}")
    
    try:
        # 创建专门的示例辩论
        ai_client = AIClient()
        apollo = Apollo(ai_client=ai_client)
        muses = Muses(ai_client=ai_client)
        
        manager = DebateManager(
            apollo=apollo,
            muses=muses,
            topic=selected_topic,
            max_rounds=3  # 示例用较少轮次
        )
        
        cli.show_info("📍 开始示例辩论...")
        summary = manager.run_observation_mode()
        
        cli.show_success("🎉 示例辩论完成！")
        cli.console.print(f"\n📊 辩论结果:")
        cli.console.print(f"状态: {summary['debate_info']['state']}")
        cli.console.print(f"轮次: {summary['debate_info']['current_round']}")
        cli.console.print(f"消息数: {summary['metrics']['total_messages']}")
        cli.console.print(f"持续时间: {summary['debate_info']['duration']:.1f}秒")
        
        cli.console.print(f"\n💬 对话摘要:")
        for i, message in enumerate(manager.get_conversation_history()[-4:], 1):
            cli.console.print(f"{i}. {message.sender}: {message.content[:80]}...")
        
        return True
        
    except Exception as e:
        cli.show_error(f"示例辩论失败: {e}")
        return False

def show_help_info():
    """显示帮助信息"""
    cli = CLIInterface()
    
    help_content = """
🏛️ Athens MVP - AI辩论系统帮助

## 系统功能
• **观察模式**: 观看AI智能体自动辩论
• **参与模式**: 在辩论中实时参与互动
• **示例辩论**: 运行预设话题的演示

## 参与模式指令
• `/pause` - 暂停当前辩论
• `/resume` - 继续暂停的辩论
• `/end` - 结束当前辩论
• `/status` - 查看辩论状态
• `/help` - 显示帮助信息
• `/theme <主题名>` - 切换界面主题
• `/clear` - 清空屏幕

## @提及功能
• `@apollo <消息>` - 向Apollo发送消息
• `@muses <消息>` - 向Muses发送消息
• `@both <消息>` - 向两个智能体发送消息

## 可用主题
• default - 默认主题
• dark - 深色主题
• forest - 森林主题
• ocean - 海洋主题
• sunset - 日落主题
• minimal - 极简主题

## 技术信息
• 基于OpenRouter API的AI模型
• 使用Rich库的美化CLI界面
• 支持Markdown格式的消息显示
• 实时状态监控和更新
"""
    
    cli.console.print(help_content)
    input("\n按回车键返回主菜单...")

def initialize_system():
    """初始化系统配置"""
    try:
        # 初始化配置系统
        config_manager = UserConfigManager()
        config_init = ConfigInitializer(config_manager)
        
        # 确保配置目录存在
        config_init.ensure_config_directory()
        
        # 检查是否为首次运行
        if config_manager.is_first_run():
            print("🏛️ 欢迎首次使用 Athens MVP!")
            wizard = SetupWizard(config_manager)
            wizard.run_first_time_setup()
        
        # 初始化配置系统
        init_result = config_init.run_initialization()
        
        if not init_result["success"]:
            print("⚠️ 配置初始化出现问题:")
            for error in init_result["errors"]:
                print(f"  ❌ {error}")
            for warning in init_result["warnings"]:
                print(f"  ⚠️ {warning}")
        
        # 加载配置
        settings = Settings(config_manager)
        
        # 初始化提示词配置
        prompt_loader = PromptLoader()
        prompt_config = PromptConfig(prompt_loader)
        
        # 验证配置
        validation_issues = prompt_config.validate_prompts()
        if validation_issues:
            logger.warning("提示词验证发现问题:")
            for issue in validation_issues:
                logger.warning(f"  - {issue}")
        
        return settings, config_manager, prompt_config
        
    except Exception as e:
        logger.error(f"系统初始化失败: {e}")
        print(f"❌ 系统初始化失败: {e}")
        print("将使用默认配置继续运行...")
        return Settings(), None, None

def main():
    """
    Main function to initialize and run the Athens MVP application.
    """
    try:
        # 初始化系统
        settings, config_manager, prompt_config = initialize_system()
        
        # 主循环
        while True:
            choice, cli = show_main_menu(settings)
            
            if choice == "0":
                cli.show_info("感谢使用 Athens MVP！")
                break
            elif choice == "1":
                if not run_observation_mode(settings):
                    cli.show_warning("观察模式未能完成")
                input("\n按回车键返回主菜单...")
            elif choice == "2":
                if not run_participation_mode(settings):
                    cli.show_warning("参与模式未能完成")
                input("\n按回车键返回主菜单...")
            elif choice == "3":
                if not run_example_debates():
                    cli.show_warning("示例辩论未能完成")
                input("\n按回车键返回主菜单...")
            elif choice == "4":
                show_help_info()
            elif choice == "5":
                # 隐藏的配置管理选项
                if config_manager:
                    wizard = SetupWizard(config_manager)
                    wizard.run_config_update()
                else:
                    cli.show_error("配置管理不可用")
            else:
                cli.show_error("无效选择，请重试")
                
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，退出系统")
    except Exception as e:
        logger.error(f"系统运行出错: {e}")
        print(f"\n❌ 系统运行出错: {e}")
        
    print("\n🏛️ Athens MVP系统已退出！")

if __name__ == "__main__":
    main()
