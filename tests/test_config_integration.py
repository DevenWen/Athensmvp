"""
配置系统集成测试模块
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.config.user_config import UserConfigManager
from src.config.config_init import ConfigInitializer
from src.config.prompt_loader import PromptLoader
from src.config.prompts import PromptConfig
from src.config.settings import Settings


class TestConfigSystemIntegration:
    """测试配置系统集成"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "config.json")
        self.prompts_dir = os.path.join(self.temp_dir, "prompts")
        
    def teardown_method(self):
        """每个测试方法后的清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_prompt_files(self):
        """创建测试提示词文件"""
        prompt_files = {
            "agents/apollo.txt": "Apollo test prompt",
            "agents/muses.txt": "Muses test prompt",
            "agents/base_agent.txt": "Base agent prompt",
            "debate/rules.txt": "Debate rules",
            "debate/format.txt": "Response format",
            "ui/welcome.txt": "Welcome message",
            "system/error_messages.txt": "Error messages"
        }
        
        for relative_path, content in prompt_files.items():
            file_path = Path(self.prompts_dir) / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
    
    def test_full_system_initialization(self):
        """测试完整系统初始化流程"""
        # 创建测试提示词文件
        self.create_test_prompt_files()
        
        # 初始化配置管理器
        config_manager = UserConfigManager(self.config_path)
        
        # 初始化配置初始化器
        config_init = ConfigInitializer(config_manager)
        
        # 运行初始化
        result = config_init.run_initialization()
        
        assert result["success"] == True
        assert len(result["errors"]) == 0
        
        # 验证配置文件已创建
        assert os.path.exists(self.config_path)
        
        # 验证目录已创建
        directories = config_manager.get_setting("directories", {})
        for dir_path in directories.values():
            expanded_path = Path(dir_path).expanduser()
            assert expanded_path.exists()
    
    def test_prompt_system_integration(self):
        """测试提示词系统集成"""
        # 创建测试提示词文件
        self.create_test_prompt_files()
        
        # 初始化提示词加载器
        prompt_loader = PromptLoader(self.prompts_dir)
        
        # 初始化提示词配置
        prompt_config = PromptConfig(prompt_loader)
        
        # 测试获取提示词
        apollo_prompt = prompt_config.get_prompt("apollo")
        assert apollo_prompt == "Apollo test prompt"
        
        muses_prompt = prompt_config.get_prompt("muses")
        assert muses_prompt == "Muses test prompt"
        
        # 测试向后兼容性
        logician_prompt = prompt_config.get_prompt("logician")
        assert logician_prompt == "Apollo test prompt"  # 应该映射到apollo
    
    def test_settings_integration(self):
        """测试Settings类与用户配置的集成"""
        # 初始化用户配置
        config_manager = UserConfigManager(self.config_path)
        
        # 设置一些用户配置
        config_manager.set_setting("agent_settings.apollo.model", "openai/gpt-4")
        config_manager.set_setting("agent_settings.apollo.temperature", 0.9)
        config_manager.set_setting("ui_settings.theme", "dark")
        
        # 初始化Settings
        settings = Settings(config_manager)
        
        # 测试获取Agent配置
        apollo_config = settings.get_agent_config("apollo")
        assert apollo_config["model"] == "openai/gpt-4"
        assert apollo_config["temperature"] == 0.9
        
        # 测试获取UI配置
        ui_config = settings.get_ui_config()
        assert ui_config["theme"] == "dark"
    
    def test_backward_compatibility(self):
        """测试向后兼容性"""
        # 创建测试提示词文件
        self.create_test_prompt_files()
        
        # 不使用用户配置管理器的Settings（旧方式）
        settings = Settings()
        
        # 应该能正常工作
        apollo_config = settings.get_agent_config("apollo")
        assert "model" in apollo_config
        assert "temperature" in apollo_config
        
        # 测试环境变量回退
        with patch.dict(os.environ, {"APOLLO_MODEL": "test-model"}):
            settings = Settings()
            assert settings.apollo_model == "test-model"
    
    def test_prompt_fallback_mechanism(self):
        """测试提示词回退机制"""
        # 不创建提示词文件，测试回退到硬编码提示词
        prompt_loader = PromptLoader(self.prompts_dir)  # 空目录
        prompt_config = PromptConfig(prompt_loader)
        
        # 应该回退到硬编码提示词
        apollo_prompt = prompt_config.get_prompt("apollo")
        assert len(apollo_prompt) > 0  # 应该有内容
        assert "Apollo" in apollo_prompt  # 应该包含Apollo相关内容
    
    def test_config_validation_integration(self):
        """测试配置验证集成"""
        # 创建不完整的配置
        config_manager = UserConfigManager(self.config_path)
        
        # 删除必要的配置项
        del config_manager.config["agent_settings"]
        
        # 验证应该发现问题
        issues = config_manager.validate_config()
        assert len(issues) > 0
        
        # 测试提示词验证
        prompt_loader = PromptLoader(self.prompts_dir)  # 空目录
        issues = prompt_loader.validate_prompt_files()
        assert len(issues) > 0  # 应该报告文件不存在
    
    def test_settings_update_integration(self):
        """测试设置更新集成"""
        config_manager = UserConfigManager(self.config_path)
        settings = Settings(config_manager)
        
        # 通过Settings更新配置
        new_agent_config = {
            "model": "anthropic/claude-3",
            "temperature": 0.5
        }
        settings.update_agent_config("apollo", new_agent_config)
        
        # 验证配置已更新
        updated_config = settings.get_agent_config("apollo")
        assert updated_config["model"] == "anthropic/claude-3"
        assert updated_config["temperature"] == 0.5
        
        # 验证持久化
        new_manager = UserConfigManager(self.config_path)
        assert new_manager.get_setting("agent_settings.apollo.model") == "anthropic/claude-3"
    
    def test_directory_management_integration(self):
        """测试目录管理集成"""
        config_manager = UserConfigManager(self.config_path)
        config_init = ConfigInitializer(config_manager)
        
        # 设置自定义目录
        custom_dirs = {
            "logs": os.path.join(self.temp_dir, "custom_logs"),
            "reports": os.path.join(self.temp_dir, "custom_reports"),
            "exports": os.path.join(self.temp_dir, "custom_exports")
        }
        
        for key, path in custom_dirs.items():
            config_manager.set_setting(f"directories.{key}", path)
        
        # 运行目录设置
        config_init.setup_directories()
        
        # 验证目录已创建
        for path in custom_dirs.values():
            assert os.path.exists(path)
            assert os.path.isdir(path)
    
    def test_error_recovery_integration(self):
        """测试错误恢复集成"""
        # 测试配置文件损坏的恢复
        with open(self.config_path, 'w') as f:
            f.write("invalid json")
        
        # 应该能够恢复
        config_manager = UserConfigManager(self.config_path)
        assert isinstance(config_manager.config, dict)
        
        # 测试提示词文件缺失的恢复
        prompt_loader = PromptLoader(self.prompts_dir)
        prompt_config = PromptConfig(prompt_loader)
        
        # 应该回退到硬编码提示词
        apollo_prompt = prompt_config.get_prompt("apollo")
        assert len(apollo_prompt) > 0
    
    def test_performance_integration(self):
        """测试性能集成"""
        # 创建大量提示词文件
        self.create_test_prompt_files()
        
        import time
        start_time = time.time()
        
        # 初始化系统
        config_manager = UserConfigManager(self.config_path)
        prompt_loader = PromptLoader(self.prompts_dir)
        prompt_config = PromptConfig(prompt_loader)
        settings = Settings(config_manager)
        
        # 加载所有提示词
        all_prompts = prompt_config.get_all_prompts()
        
        # 获取所有配置
        apollo_config = settings.get_agent_config("apollo")
        ui_config = settings.get_ui_config()
        
        end_time = time.time()
        
        # 验证性能（应该在合理时间内完成）
        assert end_time - start_time < 1.0  # 应该在1秒内完成
        
        # 验证结果正确性
        assert len(all_prompts) > 0
        assert "model" in apollo_config
        assert "theme" in ui_config
    
    def test_concurrent_access(self):
        """测试并发访问"""
        import threading
        import time
        
        config_manager = UserConfigManager(self.config_path)
        errors = []
        
        def config_worker(worker_id):
            try:
                for i in range(10):
                    # 读取配置
                    theme = config_manager.get_setting("user_preferences.theme", "default")
                    
                    # 修改配置
                    config_manager.set_setting(f"test.worker_{worker_id}.iteration", i)
                    
                    time.sleep(0.01)  # 短暂延迟
                    
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")
        
        # 启动多个工作线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=config_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证没有错误
        assert len(errors) == 0, f"Concurrent access errors: {errors}"


if __name__ == "__main__":
    pytest.main([__file__])