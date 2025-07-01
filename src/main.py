import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.ai_client import AIClient
from src.core.debate_manager import DebateManager
from src.agents.logician import Logician
from src.agents.skeptic import Skeptic
from src.config.settings import settings

def run_demo_debate():
    """运行演示辩论"""
    print("\n🎯 运行演示辩论...")
    
    try:
        # 初始化AI客户端
        ai_client = AIClient()
        
        # 创建智能体
        logician = Logician(ai_client=ai_client)
        skeptic = Skeptic(ai_client=ai_client)
        
        # 创建辩论管理器
        manager = DebateManager(
            logician=logician,
            skeptic=skeptic,
            topic="人工智能技术的发展前景",
            max_rounds=2
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

def main():
    """
    Main function to initialize and run the Athens MVP application.
    """
    print("🏛️ Athens MVP - AI辩论系统")
    print("="*50)
    print(f"默认模型: {settings.default_model}")

    # Initialize the AI Client
    try:
        ai_client = AIClient()
        print("✅ AI客户端初始化成功")
        
        # 简单测试连接
        print("🔍 测试AI客户端连接...")
        test_response = ai_client.generate_response("简单测试：请回复'连接成功'")
        if test_response and len(test_response) > 0:
            print("✅ AI客户端连接测试成功")
            
            # 运行演示辩论
            if run_demo_debate():
                print("\n🎉 Athens MVP演示完成！")
            else:
                print("\n⚠️ 演示辩论未能完成，但系统初始化正常")
        else:
            print("⚠️ AI客户端连接测试失败，但客户端已初始化")
            print("提示：检查API密钥和网络连接")
            
    except Exception as e:
        print(f"❌ AI客户端初始化失败: {e}")
        print("📝 请确保:")
        print("  1. .env文件中设置了OPENROUTER_API_KEY")
        print("  2. API密钥有效且有足够配额")
        print("  3. 网络连接正常")
        print("\n💡 你仍然可以使用:")
        print("  - 运行单元测试: pytest tests/")
        print("  - 查看示例代码: examples/simple_debate.py")

    print("\n🔧 系统组件状态:")
    print("  ✅ 智能体系统 (逻辑者、怀疑者)")
    print("  ✅ 消息系统 (通信、对话、上下文)")
    print("  ✅ 辩论管理器 (状态控制、轮次管理)")
    print("  🔲 用户界面 (待开发)")
    
    print("\n📖 使用指南:")
    print("  - 运行示例: python examples/simple_debate.py")
    print("  - 运行测试: pytest tests/")
    print("  - 查看文档: docs/")
    
    print("\n🏛️ Athens MVP核心系统就绪!")

if __name__ == "__main__":
    main()
