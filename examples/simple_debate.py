#!/usr/bin/env python3
"""
简单辩论示例
演示Athens系统的观察模式，两个AI智能体就指定话题进行自动辩论
"""

import sys
import os
import logging
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.debate_manager import DebateManager
from src.core.debate_states import DebateState, TerminationReason
from src.agents.logician import Logician
from src.agents.skeptic import Skeptic
from src.core.ai_client import AIClient
from src.config.settings import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'debate_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)


def print_separator(title: str = ""):
    """打印分割线"""
    if title:
        print(f"\n{'='*20} {title} {'='*20}")
    else:
        print("="*60)


def print_message_info(message):
    """打印消息信息"""
    timestamp = message.timestamp.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message.sender}: {message.content}")


def print_debate_status(manager: DebateManager):
    """打印辩论状态"""
    status = manager.get_debate_status()
    print(f"状态: {status['state']}")
    print(f"轮次: {status['current_round']}/{status['max_rounds']}")
    print(f"当前发言者: {status['current_speaker']}")
    print(f"消息总数: {status['total_messages']}")
    print(f"持续时间: {status['duration']:.1f}秒")


def run_simple_debate(topic: str, max_rounds: int = 5):
    """运行简单辩论"""
    print_separator("Athens 辩论系统示例")
    print(f"话题: {topic}")
    print(f"最大轮次: {max_rounds}")
    
    try:
        # 创建AI客户端（如果有API密钥）
        ai_client = None
        try:
            ai_client = AIClient()
            print("✓ AI客户端初始化成功")
        except Exception as e:
            print(f"⚠ AI客户端初始化失败: {e}")
            print("使用模拟模式继续演示...")
        
        # 创建智能体
        if ai_client:
            logician = Logician(ai_client=ai_client)
            skeptic = Skeptic(ai_client=ai_client)
            print("✓ 使用真实AI智能体")
        else:
            # 使用模拟智能体
            from tests.test_debate_manager import MockAgent
            logician = MockAgent("逻辑者", [
                "我认为人工智能技术将为人类社会带来革命性的进步和便利",
                "AI可以帮助我们解决气候变化、疾病治疗等重大挑战",
                "历史证明，每一次技术革命都最终提升了人类的生活质量",
                "我们应该拥抱AI技术，同时建立合适的监管框架"
            ])
            skeptic = MockAgent("怀疑者", [
                "但是AI技术的快速发展也带来了前所未有的风险和挑战",
                "大规模失业、隐私侵犯、算法偏见等问题需要认真对待",
                "我们不能盲目乐观，必须谨慎评估AI对社会的深层影响",
                "技术发展的速度可能超出了人类社会的适应能力"
            ])
            print("✓ 使用模拟智能体进行演示")
        
        # 创建辩论管理器
        manager = DebateManager(
            logician=logician,
            skeptic=skeptic,
            topic=topic,
            max_rounds=max_rounds
        )
        
        # 设置事件监听器
        def on_state_changed(old_state, new_state):
            print(f"\n📍 状态变化: {old_state.value} → {new_state.value}")
        
        def on_round_start(round_num, speaker):
            print_separator(f"第 {round_num} 轮开始")
            print(f"发言者: {speaker}")
        
        def on_round_complete(round_obj):
            duration = round_obj.get_duration()
            print(f"第 {round_obj.round_number} 轮完成 (耗时: {duration.total_seconds():.1f}秒)")
        
        def on_message_sent(message):
            print_message_info(message)
        
        def on_debate_complete(reason):
            print_separator("辩论结束")
            print(f"终止原因: {reason.value}")
        
        # 注册回调
        manager.on_state_changed = on_state_changed
        manager.on_round_start = on_round_start
        manager.on_round_complete = on_round_complete
        manager.on_message_sent = on_message_sent
        manager.on_debate_complete = on_debate_complete
        
        print_separator("开始辩论")
        
        # 运行观察模式
        summary = manager.run_observation_mode()
        
        print_separator("辩论总结")
        
        # 显示最终状态
        print_debate_status(manager)
        
        # 显示详细统计
        print(f"\n📊 辩论统计:")
        metrics = summary['metrics']
        print(f"总消息数: {metrics['total_messages']}")
        print(f"总轮次数: {metrics['total_rounds']}")
        print(f"平均回应时间: {metrics['average_response_time']:.2f}秒")
        print(f"平均内容质量: {metrics['average_quality']:.2f}")
        
        # 显示参与者统计
        print(f"\n👥 参与者统计:")
        for participant, count in metrics['participant_message_counts'].items():
            print(f"{participant}: {count}条消息")
        
        # 显示对话历史
        print_separator("对话历史")
        for i, message in enumerate(manager.get_conversation_history(), 1):
            print(f"{i:2d}. {message.sender}: {message.content}")
        
        # 保存报告
        report_filename = f"debate_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            import json
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
            print(f"\n💾 辩论报告已保存: {report_filename}")
        except Exception as e:
            print(f"⚠ 保存报告失败: {e}")
        
        print_separator("示例完成")
        return summary
        
    except Exception as e:
        logger.error(f"辩论过程中发生错误: {e}")
        print(f"❌ 错误: {e}")
        return None


def run_interactive_example():
    """运行交互式示例"""
    print("🎯 Athens 辩论系统交互式示例")
    print("请输入辩论话题，或使用默认话题")
    
    # 获取用户输入
    default_topic = "人工智能技术对人类社会的影响"
    topic = input(f"辩论话题 (默认: {default_topic}): ").strip()
    if not topic:
        topic = default_topic
    
    # 获取轮次数
    try:
        max_rounds = int(input("最大轮次数 (默认: 3): ") or "3")
        max_rounds = max(1, min(max_rounds, 10))  # 限制在1-10之间
    except ValueError:
        max_rounds = 3
    
    print(f"\n开始辩论...")
    return run_simple_debate(topic, max_rounds)


def main():
    """主函数"""
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
        max_rounds = 3
        print(f"命令行模式: {topic}")
        return run_simple_debate(topic, max_rounds)
    else:
        return run_interactive_example()


if __name__ == "__main__":
    try:
        result = main()
        if result:
            print("\n✅ 示例运行成功!")
        else:
            print("\n❌ 示例运行失败!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹ 用户中断，退出示例")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 未处理的异常: {e}")
        logger.exception("未处理的异常")
        sys.exit(1)