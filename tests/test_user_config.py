"""
用户配置管理测试模块
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.config.user_config import UserConfigManager


class TestUserConfigManager:
    """测试UserConfigManager类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "config.json")
        self.config_manager = UserConfigManager(self.config_path)
        
    def teardown_method(self):
        """每个测试方法后的清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_new_config(self):
        """测试使用新配置文件初始化"""
        assert self.config_manager.config_path == self.config_path
        assert isinstance(self.config_manager.config, dict)
        
        # 应该创建默认配置
        assert "version" in self.config_manager.config
        assert "user_preferences" in self.config_manager.config
        assert "agent_settings" in self.config_manager.config
    
    def test_init_with_existing_config(self):
        """测试使用现有配置文件初始化"""
        # 创建测试配置文件
        test_config = {
            "version": "0.0.3",
            "user_preferences": {
                "theme": "dark",
                "language": "en_US"
            }
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(test_config, f)
        
        # 重新初始化
        manager = UserConfigManager(self.config_path)
        
        assert manager.config["user_preferences"]["theme"] == "dark"
        assert manager.config["user_preferences"]["language"] == "en_US"
    
    def test_get_setting(self):
        """测试获取配置项"""
        # 测试获取存在的设置
        theme = self.config_manager.get_setting("user_preferences.theme")
        assert theme is not None
        
        # 测试获取不存在的设置
        nonexistent = self.config_manager.get_setting("nonexistent.setting", "default")
        assert nonexistent == "default"
        
        # 测试嵌套路径
        model = self.config_manager.get_setting("agent_settings.apollo.model")
        assert model is not None
    
    def test_set_setting(self):
        """测试设置配置项"""
        # 设置新值
        self.config_manager.set_setting("user_preferences.theme", "dark")
        assert self.config_manager.get_setting("user_preferences.theme") == "dark"
        
        # 设置嵌套路径
        self.config_manager.set_setting("agent_settings.apollo.temperature", 0.9)
        assert self.config_manager.get_setting("agent_settings.apollo.temperature") == 0.9
        
        # 设置新的嵌套结构
        self.config_manager.set_setting("new_section.new_key", "new_value")
        assert self.config_manager.get_setting("new_section.new_key") == "new_value"
    
    def test_save_and_load_config(self):
        """测试配置保存和加载"""
        # 修改配置
        self.config_manager.set_setting("user_preferences.theme", "forest")
        self.config_manager.save_config()
        
        # 创建新的管理器实例来验证持久化
        new_manager = UserConfigManager(self.config_path)
        assert new_manager.get_setting("user_preferences.theme") == "forest"
    
    def test_reset_to_defaults(self):
        """测试重置为默认配置"""
        # 修改配置
        self.config_manager.set_setting("user_preferences.theme", "custom")
        
        # 重置
        self.config_manager.reset_to_defaults()
        
        # 验证已重置
        theme = self.config_manager.get_setting("user_preferences.theme")
        assert theme == "default"  # 默认主题
    
    def test_validate_config(self):
        """测试配置验证"""
        # 有效配置应该没有问题
        issues = self.config_manager.validate_config()
        assert isinstance(issues, list)
        
        # 删除必要的配置节来测试验证
        del self.config_manager.config["agent_settings"]
        issues = self.config_manager.validate_config()
        assert len(issues) > 0
        assert any("agent_settings" in issue for issue in issues)
    
    def test_migrate_from_old_config(self):
        """测试配置迁移"""
        # 创建旧版本配置
        old_config = {
            "version": "0.0.1",
            "user_preferences": {
                "theme": "dark"
            }
            # 缺少一些新的配置节
        }
        
        self.config_manager.config = old_config
        self.config_manager.migrate_from_old_config()
        
        # 验证迁移后包含所有必要的配置节
        assert "agent_settings" in self.config_manager.config
        assert "ui_settings" in self.config_manager.config
        assert "debate_settings" in self.config_manager.config
        
        # 验证原有设置保持不变
        assert self.config_manager.config["user_preferences"]["theme"] == "dark"
    
    def test_is_first_run(self):
        """测试首次运行检测"""
        # 删除配置文件
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        
        # 创建新的管理器
        manager = UserConfigManager(self.config_path)
        
        # 在配置文件被创建之前，应该检测为首次运行
        # 注意：实际上配置文件在初始化时就会被创建
        # 所以我们需要在文件被创建之前检查
        temp_path = os.path.join(self.temp_dir, "nonexistent.json")
        temp_manager = UserConfigManager(temp_path)
        
        # 手动删除配置文件来模拟首次运行
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        assert temp_manager.is_first_run()
    
    def test_get_config_info(self):
        """测试获取配置信息"""
        info = self.config_manager.get_config_info()
        
        assert isinstance(info, dict)
        assert "config_path" in info
        assert "version" in info
        assert "file_exists" in info
        assert "file_size" in info
        
        assert info["config_path"] == self.config_path
        assert info["file_exists"] == True
    
    def test_export_import_config(self):
        """测试配置导出和导入"""
        # 修改配置
        self.config_manager.set_setting("user_preferences.theme", "exported")
        
        # 导出配置
        export_path = os.path.join(self.temp_dir, "exported_config.json")
        self.config_manager.export_config(export_path)
        
        # 验证导出文件存在
        assert os.path.exists(export_path)
        
        # 修改当前配置
        self.config_manager.set_setting("user_preferences.theme", "modified")
        
        # 导入配置
        self.config_manager.import_config(export_path)
        
        # 验证配置已恢复
        assert self.config_manager.get_setting("user_preferences.theme") == "exported"
    
    def test_backup_creation(self):
        """测试备份创建"""
        # 保存配置以触发备份
        self.config_manager.save_config()
        
        backup_path = self.config_path + ".backup"
        assert os.path.exists(backup_path)
    
    def test_config_with_unicode(self):
        """测试Unicode字符处理"""
        chinese_text = "中文主题"
        self.config_manager.set_setting("user_preferences.theme", chinese_text)
        
        # 保存和重新加载
        self.config_manager.save_config()
        new_manager = UserConfigManager(self.config_path)
        
        assert new_manager.get_setting("user_preferences.theme") == chinese_text
    
    def test_error_handling_invalid_json(self):
        """测试无效JSON的错误处理"""
        # 写入无效的JSON
        with open(self.config_path, 'w') as f:
            f.write("invalid json content")
        
        # 应该回退到默认配置
        manager = UserConfigManager(self.config_path)
        assert isinstance(manager.config, dict)
        assert "version" in manager.config
    
    def test_error_handling_permission_denied(self):
        """测试权限拒绝的错误处理"""
        if os.name != 'nt':  # 仅在Unix系统上测试
            # 移除写权限
            os.chmod(self.temp_dir, 0o444)
            
            try:
                # 尝试保存应该引发异常
                with pytest.raises(Exception):
                    self.config_manager.save_config()
            finally:
                # 恢复权限以便清理
                os.chmod(self.temp_dir, 0o755)
    
    def test_default_config_structure(self):
        """测试默认配置结构"""
        default_config = self.config_manager._get_default_config()
        
        # 验证必要的配置节存在
        required_sections = [
            "version", "user_preferences", "agent_settings", 
            "ui_settings", "debate_settings", "directories"
        ]
        
        for section in required_sections:
            assert section in default_config
        
        # 验证Agent配置
        assert "apollo" in default_config["agent_settings"]
        assert "muses" in default_config["agent_settings"]
        
        # 验证模型配置
        apollo_config = default_config["agent_settings"]["apollo"]
        assert "model" in apollo_config
        assert "temperature" in apollo_config
        assert "max_tokens" in apollo_config
    
    def test_nested_setting_operations(self):
        """测试嵌套设置操作"""
        # 测试深层嵌套
        self.config_manager.set_setting("level1.level2.level3.value", "deep")
        assert self.config_manager.get_setting("level1.level2.level3.value") == "deep"
        
        # 测试部分路径获取
        level2 = self.config_manager.get_setting("level1.level2")
        assert isinstance(level2, dict)
        assert level2["level3"]["value"] == "deep"


if __name__ == "__main__":
    pytest.main([__file__])