"""
Prompt加载器测试模块
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.config.prompt_loader import PromptLoader, PromptInfo


class TestPromptLoader:
    """测试PromptLoader类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_loader = PromptLoader(self.temp_dir)
        
    def teardown_method(self):
        """每个测试方法后的清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, relative_path: str, content: str):
        """创建测试文件"""
        file_path = Path(self.temp_dir) / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        return str(file_path)
    
    def test_init(self):
        """测试初始化"""
        loader = PromptLoader(self.temp_dir)
        assert loader.base_path == Path(self.temp_dir)
        assert isinstance(loader._file_mapping, dict)
        assert len(loader._file_mapping) > 0
    
    def test_file_mapping(self):
        """测试文件映射"""
        mapping = self.test_loader._file_mapping
        
        # 检查必要的提示词键
        required_keys = ["apollo", "muses", "debate_rules", "response_format"]
        for key in required_keys:
            assert key in mapping
        
        # 检查向后兼容性
        assert "logician" in mapping
        assert "skeptic" in mapping
    
    def test_load_existing_prompt(self):
        """测试加载存在的提示词"""
        test_content = "This is a test prompt for Apollo."
        self.create_test_file("agents/apollo.txt", test_content)
        
        result = self.test_loader.get_prompt("apollo")
        assert result == test_content
    
    def test_load_non_existing_prompt(self):
        """测试加载不存在的提示词"""
        result = self.test_loader.get_prompt("apollo")
        assert result == ""  # 应该返回空字符串而不是报错
    
    def test_load_all_prompts(self):
        """测试加载所有提示词"""
        # 创建一些测试文件
        test_files = {
            "agents/apollo.txt": "Apollo prompt",
            "agents/muses.txt": "Muses prompt",
            "debate/rules.txt": "Debate rules"
        }
        
        for path, content in test_files.items():
            self.create_test_file(path, content)
        
        all_prompts = self.test_loader.load_all_prompts()
        
        assert isinstance(all_prompts, dict)
        assert "apollo" in all_prompts
        assert "muses" in all_prompts
        assert "debate_rules" in all_prompts
        
        assert all_prompts["apollo"] == "Apollo prompt"
        assert all_prompts["muses"] == "Muses prompt"
        assert all_prompts["debate_rules"] == "Debate rules"
    
    def test_prompt_info_creation(self):
        """测试PromptInfo创建"""
        test_content = "Test content"
        file_path = self.create_test_file("agents/apollo.txt", test_content)
        
        info = self.test_loader.get_prompt_info("apollo")
        
        assert isinstance(info, PromptInfo)
        assert info.key == "apollo"
        assert info.content == test_content
        assert info.file_path == file_path
    
    def test_file_modification_detection(self):
        """测试文件修改检测"""
        test_content = "Original content"
        file_path = self.create_test_file("agents/apollo.txt", test_content)
        
        # 首次加载
        original_content = self.test_loader.get_prompt("apollo")
        assert original_content == test_content
        
        # 修改文件
        import time
        time.sleep(0.1)  # 确保修改时间不同
        new_content = "Modified content"
        Path(file_path).write_text(new_content, encoding='utf-8')
        
        # 再次加载应该获取新内容
        modified_content = self.test_loader.get_prompt("apollo")
        assert modified_content == new_content
    
    def test_validate_prompt_files(self):
        """测试提示词文件验证"""
        # 创建一些有效文件
        self.create_test_file("agents/apollo.txt", "Apollo content")
        self.create_test_file("agents/muses.txt", "Muses content")
        
        # 创建一个空文件
        self.create_test_file("debate/rules.txt", "")
        
        issues = self.test_loader.validate_prompt_files()
        
        # 应该报告空文件问题
        assert any("文件为空" in issue for issue in issues)
    
    def test_reload_prompts(self):
        """测试重新加载提示词"""
        # 创建初始文件
        self.create_test_file("agents/apollo.txt", "Original")
        
        # 首次加载
        original = self.test_loader.get_prompt("apollo")
        assert original == "Original"
        
        # 修改文件
        self.create_test_file("agents/apollo.txt", "Updated")
        
        # 重新加载
        self.test_loader.reload_prompts()
        updated = self.test_loader.get_prompt("apollo")
        assert updated == "Updated"
    
    def test_get_prompt_file_path(self):
        """测试获取提示词文件路径"""
        apollo_path = self.test_loader.get_prompt_file_path("apollo")
        expected_path = str(Path(self.temp_dir) / "agents" / "apollo.txt")
        assert apollo_path == expected_path
        
        # 测试不存在的键
        invalid_path = self.test_loader.get_prompt_file_path("nonexistent")
        assert invalid_path is None
    
    def test_list_available_prompts(self):
        """测试列出可用提示词"""
        available = self.test_loader.list_available_prompts()
        
        assert isinstance(available, list)
        assert "apollo" in available
        assert "muses" in available
        assert "debate_rules" in available
        assert "logician" in available  # 向后兼容
    
    def test_unicode_support(self):
        """测试Unicode字符支持"""
        chinese_content = "这是一个中文提示词测试。包含特殊字符：🤖💭"
        self.create_test_file("agents/apollo.txt", chinese_content)
        
        result = self.test_loader.get_prompt("apollo")
        assert result == chinese_content
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试读取权限被拒绝的情况（在Linux/Mac上）
        if os.name != 'nt':
            file_path = self.create_test_file("agents/apollo.txt", "test")
            os.chmod(file_path, 0o000)  # 移除所有权限
            
            try:
                result = self.test_loader.get_prompt("apollo")
                # 应该返回空字符串而不是抛出异常
                assert result == ""
            finally:
                os.chmod(file_path, 0o644)  # 恢复权限以便清理


class TestPromptInfo:
    """测试PromptInfo类"""
    
    def test_prompt_info_creation(self):
        """测试PromptInfo创建"""
        info = PromptInfo("test_key", "/test/path", "test content")
        
        assert info.key == "test_key"
        assert info.file_path == "/test/path"
        assert info.content == "test content"
        assert info.last_modified >= 0
    
    def test_modification_check_with_nonexistent_file(self):
        """测试不存在文件的修改检测"""
        info = PromptInfo("test", "/nonexistent/file", "content")
        
        # 不存在的文件应该返回False
        assert not info.is_modified()
    
    def test_update_content(self):
        """测试更新内容"""
        info = PromptInfo("test", "/test/path", "original")
        
        info.update_content("updated")
        assert info.content == "updated"


if __name__ == "__main__":
    pytest.main([__file__])