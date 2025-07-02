"""
用户界面模块单元测试
测试CLI界面、指令处理器、参与模式和实时显示功能
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import threading
import time

from src.ui.cli_interface import CLIInterface
from src.ui.command_processor import CommandProcessor, CommandType, ParsedCommand
from src.ui.participation_mode import ParticipationMode
from src.ui.realtime_display import RealTimeDisplay
from src.core.message import Message, MessageType


class TestCLIInterface:
    """测试CLI界面功能"""
    
    def test_cli_interface_creation(self):
        """测试CLI界面创建"""
        cli = CLIInterface()
        assert cli.current_theme_name == "default"
        assert cli.theme == cli.THEMES["default"]
        assert cli.console is not None
    
    def test_cli_interface_with_theme(self):
        """测试带主题的CLI界面创建"""
        cli = CLIInterface("dark")
        assert cli.current_theme_name == "dark"
        assert cli.theme == cli.THEMES["dark"]
    
    def test_theme_switching(self):
        """测试主题切换"""
        cli = CLIInterface("default")
        
        # 成功切换到存在的主题
        result = cli.switch_theme("ocean")
        assert result is True
        assert cli.current_theme_name == "ocean"
        assert cli.theme == cli.THEMES["ocean"]
        
        # 尝试切换到不存在的主题
        result = cli.switch_theme("nonexistent")
        assert result is False
        assert cli.current_theme_name == "ocean"  # 保持原主题
    
    def test_available_themes(self):
        """测试所有预设主题都可用"""
        expected_themes = ["default", "dark", "forest", "ocean", "sunset", "minimal"]
        cli = CLIInterface()
        
        for theme_name in expected_themes:
            assert theme_name in cli.THEMES
            assert cli.switch_theme(theme_name) is True
    
    def test_display_message(self):
        """测试消息显示"""
        cli = CLIInterface()
        
        with patch.object(cli, 'console') as mock_console:
            # 创建测试消息
            message = Message(
                content="这是一个测试消息",
                sender="逻辑者",
                message_type=MessageType.ARGUMENT
            )
            
            # 显示消息
            cli.display_message(message)
            
            # 验证console.print被调用
            assert mock_console.print.called
    
    def test_status_messages(self):
        """测试状态消息显示"""
        cli = CLIInterface()
        
        with patch.object(cli, 'console') as mock_console:
            # 测试各种状态消息
            cli.show_success("操作成功")
            cli.show_error("发生错误")
            cli.show_warning("警告信息")
            cli.show_info("提示信息")
            
            # 验证所有状态消息都被调用
            assert mock_console.print.call_count == 4


class TestCommandProcessor:
    """测试指令处理器功能"""
    
    def test_command_processor_creation(self):
        """测试指令处理器创建"""
        processor = CommandProcessor()
        assert processor.command_handlers == {}
        assert processor.mention_handlers == {}
        assert len(processor.input_validators) == 2  # 默认验证器
    
    def test_parse_system_command(self):
        """测试系统指令解析"""
        processor = CommandProcessor()
        
        # 测试有效的系统指令
        result = processor.parse_command("/pause")
        assert result.command_type == CommandType.SYSTEM_COMMAND
        assert result.command == "pause"
        assert result.is_valid is True
        
        # 测试带参数的系统指令
        result = processor.parse_command("/theme dark")
        assert result.command_type == CommandType.SYSTEM_COMMAND
        assert result.command == "theme"
        assert result.args == ["dark"]
        assert result.is_valid is True
        
        # 测试无效的系统指令
        result = processor.parse_command("/invalid")
        assert result.command_type == CommandType.INVALID
        assert result.is_valid is False
        assert "未知指令" in result.error_message
    
    def test_parse_mention(self):
        """测试@提及解析"""
        processor = CommandProcessor()
        
        # 测试有效的@提及
        result = processor.parse_command("@logician 这是给逻辑者的消息")
        assert result.command_type == CommandType.MENTION
        assert result.target == "logician"
        assert result.content == "这是给逻辑者的消息"
        assert result.is_valid is True
        
        # 测试别名@提及
        result = processor.parse_command("@逻辑者 这是中文别名")
        assert result.command_type == CommandType.MENTION
        assert result.target == "logician"
        assert result.content == "这是中文别名"
        assert result.is_valid is True
        
        # 测试无效的@提及
        result = processor.parse_command("@unknown 无效目标")
        assert result.command_type == CommandType.INVALID
        assert result.is_valid is False
        assert "无效的@提及目标" in result.error_message
        
        # 测试@提及但没有内容
        result = processor.parse_command("@logician")
        assert result.command_type == CommandType.INVALID
        assert result.is_valid is False
        assert "@提及后必须包含消息内容" in result.error_message
    
    def test_parse_regular_message(self):
        """测试普通消息解析"""
        processor = CommandProcessor()
        
        result = processor.parse_command("这是一个普通消息")
        assert result.command_type == CommandType.REGULAR_MESSAGE
        assert result.content == "这是一个普通消息"
        assert result.is_valid is True
    
    def test_empty_input(self):
        """测试空输入"""
        processor = CommandProcessor()
        
        result = processor.parse_command("")
        assert result.command_type == CommandType.INVALID
        assert result.is_valid is False
        assert "输入不能为空" in result.error_message
        
        result = processor.parse_command("   ")
        assert result.command_type == CommandType.INVALID
        assert result.is_valid is False
        assert "输入不能为空" in result.error_message
    
    def test_command_aliases(self):
        """测试指令别名"""
        processor = CommandProcessor()
        
        # 测试中文别名
        result = processor.parse_command("/暂停")
        assert result.command_type == CommandType.SYSTEM_COMMAND
        assert result.command == "pause"
        assert result.is_valid is True
        
        # 测试短别名
        result = processor.parse_command("/h")
        assert result.command_type == CommandType.SYSTEM_COMMAND
        assert result.command == "help"
        assert result.is_valid is True
    
    def test_input_validation(self):
        """测试输入验证"""
        processor = CommandProcessor()
        
        # 测试过长输入
        long_input = "a" * 2500
        is_valid, error_msg = processor.validate_input(long_input)
        assert is_valid is False
        assert "过长" in error_msg
        
        # 测试正常输入
        normal_input = "这是正常的输入"
        is_valid, error_msg = processor.validate_input(normal_input)
        assert is_valid is True
        assert error_msg is None
    
    def test_command_suggestions(self):
        """测试指令建议"""
        processor = CommandProcessor()
        
        # 测试系统指令建议
        suggestions = processor.get_command_suggestions("/p")
        assert "/pause" in suggestions
        
        # 测试@提及建议
        suggestions = processor.get_command_suggestions("@l")
        assert "@logician" in suggestions
        
        # 测试空建议
        suggestions = processor.get_command_suggestions("normal text")
        assert len(suggestions) == 0
    
    def test_command_execution(self):
        """测试指令执行"""
        processor = CommandProcessor()
        
        # 测试执行有效指令
        parsed_cmd = processor.parse_command("/help")
        result = processor.execute_command(parsed_cmd)
        assert result["success"] is True
        assert result["type"] == "help"
        assert "content" in result
        
        # 测试执行无效指令
        parsed_cmd = ParsedCommand(
            command_type=CommandType.INVALID,
            raw_input="/invalid",
            is_valid=False,
            error_message="测试错误"
        )
        result = processor.execute_command(parsed_cmd)
        assert result["success"] is False
        assert result["error"] == "测试错误"
    
    def test_handler_registration(self):
        """测试处理器注册"""
        processor = CommandProcessor()
        
        # 注册指令处理器
        mock_handler = Mock()
        processor.register_command_handler("test", mock_handler)
        assert "test" in processor.command_handlers
        assert processor.command_handlers["test"] == mock_handler
        
        # 注册@提及处理器
        mock_mention_handler = Mock()
        processor.register_mention_handler("test_target", mock_mention_handler)
        assert "test_target" in processor.mention_handlers
        assert processor.mention_handlers["test_target"] == mock_mention_handler


class TestParticipationMode:
    """测试参与模式功能"""
    
    def test_participation_mode_creation(self):
        """测试参与模式创建"""
        with patch('src.ui.participation_mode.AIClient'):
            mode = ParticipationMode()
            assert mode.cli is not None
            assert mode.cmd_processor is not None
            assert mode.logician is not None
            assert mode.skeptic is not None
            assert mode.debate_manager is None
    
    def test_participation_mode_with_theme(self):
        """测试带主题的参与模式创建"""
        with patch('src.ui.participation_mode.AIClient'):
            mode = ParticipationMode("ocean")
            assert mode.cli.current_theme_name == "ocean"
    
    @patch('src.ui.participation_mode.AIClient')
    @patch('src.ui.participation_mode.DebateManager')
    def test_start_debate(self, mock_debate_manager, mock_ai_client):
        """测试开始辩论"""
        mode = ParticipationMode()
        
        # 模拟辩论管理器
        mock_debate_instance = Mock()
        mock_debate_instance.start_debate.return_value = True
        mock_debate_manager.return_value = mock_debate_instance
        
        mode._start_debate("测试话题")
        
        assert mode.debate_manager is not None
        mock_debate_manager.assert_called_once()
        mock_debate_instance.start_debate.assert_called_once()
    
    def test_command_handlers_setup(self):
        """测试指令处理器设置"""
        with patch('src.ui.participation_mode.AIClient'):
            mode = ParticipationMode()
            
            # 验证指令处理器已注册
            assert "pause" in mode.cmd_processor.command_handlers
            assert "resume" in mode.cmd_processor.command_handlers
            assert "end" in mode.cmd_processor.command_handlers
            assert "status" in mode.cmd_processor.command_handlers
            
            # 验证@提及处理器已注册
            assert "logician" in mode.cmd_processor.mention_handlers
            assert "skeptic" in mode.cmd_processor.mention_handlers
            assert "both" in mode.cmd_processor.mention_handlers


class TestRealTimeDisplay:
    """测试实时显示功能"""
    
    @patch('src.ui.realtime_display.RealTimeDisplay._setup_layout')
    def test_realtime_display_creation(self, mock_setup):
        """测试实时显示创建"""
        theme = {"panel_title": "blue", "panel_border": {}}
        display = RealTimeDisplay(theme)
        
        assert display.theme == theme
        assert display.messages == []
        assert display.status_info == {}
        assert display.max_displayed_messages == 10
        assert display.is_running is False
        mock_setup.assert_called_once()
    
    @patch('src.ui.realtime_display.RealTimeDisplay._setup_layout')
    def test_message_management(self, mock_setup):
        """测试消息管理"""
        theme = {"panel_title": "blue", "panel_border": {}}
        display = RealTimeDisplay(theme)
        
        # 创建测试消息
        message = Message(
            content="测试消息",
            sender="逻辑者",
            message_type=MessageType.ARGUMENT
        )
        
        # 添加消息
        display.add_message(message)
        
        # 验证消息被添加到队列
        assert not display.update_queue.empty()
    
    @patch('src.ui.realtime_display.RealTimeDisplay._setup_layout')
    def test_status_update(self, mock_setup):
        """测试状态更新"""
        theme = {"panel_title": "blue", "panel_border": {}}
        display = RealTimeDisplay(theme)
        
        status_data = {
            "topic": "测试话题",
            "state": "active",
            "current_round": 1,
            "max_rounds": 5
        }
        
        display.update_status(status_data)
        
        # 验证状态更新被添加到队列
        assert not display.update_queue.empty()
    
    @patch('src.ui.realtime_display.RealTimeDisplay._setup_layout')
    def test_input_hint_setting(self, mock_setup):
        """测试输入提示设置"""
        theme = {"panel_title": "blue", "panel_border": {}}
        display = RealTimeDisplay(theme)
        
        display.set_input_hint("新的输入提示")
        
        # 验证提示更新被添加到队列
        assert not display.update_queue.empty()
    
    @patch('src.ui.realtime_display.RealTimeDisplay._setup_layout')
    def test_clear_messages(self, mock_setup):
        """测试清空消息"""
        theme = {"panel_title": "blue", "panel_border": {}}
        display = RealTimeDisplay(theme)
        
        display.clear_messages()
        
        # 验证清空消息命令被添加到队列
        assert not display.update_queue.empty()
    
    @patch('src.ui.realtime_display.RealTimeDisplay._setup_layout')
    def test_start_stop_display(self, mock_setup):
        """测试启动和停止显示"""
        theme = {"panel_title": "blue", "panel_border": {}}
        display = RealTimeDisplay(theme)
        
        # 测试基本状态变化
        assert display.is_running is False
        
        # 模拟启动过程
        display.is_running = True
        assert display.is_running is True
        
        # 模拟停止过程
        display.stop_display()
        assert display.is_running is False


class TestUIIntegration:
    """测试UI组件集成"""
    
    @patch('src.ui.participation_mode.AIClient')
    def test_cli_and_command_processor_integration(self, mock_ai_client):
        """测试CLI界面和指令处理器集成"""
        mode = ParticipationMode()
        
        # 验证CLI界面和指令处理器已正确集成
        assert mode.cli is not None
        assert mode.cmd_processor is not None
        
        # 测试主题切换集成
        original_theme = mode.cli.current_theme_name
        result = mode._handle_theme(["dark"])
        
        # 根据具体实现验证结果
        assert result["success"] is True
    
    def test_message_type_display_consistency(self):
        """测试消息类型显示一致性"""
        cli = CLIInterface()
        
        # 创建不同类型的消息
        logician_msg = Message("逻辑者消息", "逻辑者", MessageType.ARGUMENT)
        skeptic_msg = Message("怀疑者消息", "怀疑者", MessageType.COUNTER)
        user_msg = Message("用户消息", "用户", MessageType.USER_INPUT)
        
        # 验证消息可以正常显示（不抛出异常）
        try:
            cli.display_message(logician_msg)
            cli.display_message(skeptic_msg)
            cli.display_message(user_msg)
        except Exception as e:
            pytest.fail(f"消息显示失败: {e}")


class TestUIErrorHandling:
    """测试UI错误处理"""
    
    def test_command_processor_malformed_input(self):
        """测试指令处理器对畸形输入的处理"""
        processor = CommandProcessor()
        
        # 测试各种畸形输入
        malformed_inputs = [
            "/",           # 只有斜杠
            "/@",          # 混合符号
            "@",           # 只有@符号
            "@ ",          # @后只有空格
            "/command with very long arguments " + "a" * 100,  # 过长参数
        ]
        
        for malformed_input in malformed_inputs:
            result = processor.parse_command(malformed_input)
            # 畸形输入应该被正确处理，要么解析成功要么返回明确错误
            assert result is not None
            if not result.is_valid:
                assert result.error_message is not None
    
    def test_cli_interface_theme_error_handling(self):
        """测试CLI界面主题错误处理"""
        cli = CLIInterface()
        
        # 测试切换到不存在的主题
        result = cli.switch_theme("nonexistent_theme")
        assert result is False
        # 原主题应该保持不变
        assert cli.current_theme_name == "default"
    
    @patch('src.ui.participation_mode.AIClient')
    def test_participation_mode_error_recovery(self, mock_ai_client):
        """测试参与模式错误恢复"""
        mode = ParticipationMode()
        
        # 测试没有辩论管理器时的状态检查
        result = mode._handle_status([])
        assert result["success"] is True  # 应该优雅处理而不是崩溃
        
        # 测试空参数的主题切换
        result = mode._handle_theme([])
        assert result["success"] is False  # 应该返回错误而不是崩溃


if __name__ == "__main__":
    pytest.main([__file__, "-v"])