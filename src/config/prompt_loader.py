"""
Prompt加载器模块
负责从文件系统加载提示词配置
"""

import os
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PromptInfo:
    """提示词信息类"""
    def __init__(self, key: str, file_path: str, content: str):
        self.key = key
        self.file_path = file_path
        self.content = content
        self.last_modified = os.path.getmtime(file_path) if os.path.exists(file_path) else 0

    def is_modified(self) -> bool:
        """检查文件是否已被修改"""
        if not os.path.exists(self.file_path):
            return False
        current_mtime = os.path.getmtime(self.file_path)
        return current_mtime > self.last_modified

    def update_content(self, content: str) -> None:
        """更新内容和修改时间"""
        self.content = content
        if os.path.exists(self.file_path):
            self.last_modified = os.path.getmtime(self.file_path)


class PromptLoader:
    """提示词加载器"""
    
    def __init__(self, base_path: str = "src/config/prompts"):
        self.base_path = Path(base_path)
        self._prompts: Dict[str, PromptInfo] = {}
        self._file_mapping = self._build_file_mapping()
        
    def _build_file_mapping(self) -> Dict[str, str]:
        """构建提示词键到文件路径的映射"""
        return {
            # Agent prompts
            "apollo": "agents/apollo.txt",
            "muses": "agents/muses.txt", 
            "base_agent": "agents/base_agent.txt",
            
            # Legacy compatibility
            "logician": "agents/apollo.txt",  # 向后兼容
            "skeptic": "agents/muses.txt",   # 向后兼容
            
            # Debate prompts
            "debate_rules": "debate/rules.txt",
            "response_format": "debate/format.txt",
            "consensus": "debate/consensus.txt",
            
            # UI prompts
            "welcome": "ui/welcome.txt",
            "help": "ui/help.txt",
            "commands": "ui/commands.txt",
            
            # System prompts
            "error_messages": "system/error_messages.txt",
            "status_messages": "system/status_messages.txt"
        }
    
    def load_prompt(self, category: str, name: str) -> str:
        """加载指定类别和名称的提示词"""
        key = f"{category}.{name}" if category else name
        return self.get_prompt(key)
        
    def get_prompt(self, prompt_key: str) -> str:
        """获取指定键的提示词"""
        if prompt_key not in self._prompts:
            self._load_prompt_from_file(prompt_key)
        
        prompt_info = self._prompts.get(prompt_key)
        if not prompt_info:
            logger.warning(f"提示词未找到: {prompt_key}")
            return ""
            
        # 检查文件是否已修改，如果是则重新加载
        if prompt_info.is_modified():
            logger.info(f"检测到文件修改，重新加载: {prompt_key}")
            self._load_prompt_from_file(prompt_key)
            
        return self._prompts[prompt_key].content
    
    def _load_prompt_from_file(self, prompt_key: str) -> None:
        """从文件加载指定提示词"""
        if prompt_key not in self._file_mapping:
            logger.error(f"未知的提示词键: {prompt_key}")
            return
            
        file_path = self.base_path / self._file_mapping[prompt_key]
        
        try:
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8').strip()
                self._prompts[prompt_key] = PromptInfo(prompt_key, str(file_path), content)
                logger.debug(f"已加载提示词: {prompt_key} from {file_path}")
            else:
                logger.warning(f"提示词文件不存在: {file_path}")
                self._prompts[prompt_key] = PromptInfo(prompt_key, str(file_path), "")
        except Exception as e:
            logger.error(f"加载提示词失败 {prompt_key}: {e}")
            self._prompts[prompt_key] = PromptInfo(prompt_key, str(file_path), "")
    
    def load_all_prompts(self) -> Dict[str, str]:
        """加载所有提示词"""
        result = {}
        for prompt_key in self._file_mapping.keys():
            result[prompt_key] = self.get_prompt(prompt_key)
        return result
    
    def reload_prompts(self) -> None:
        """重新加载所有提示词"""
        logger.info("重新加载所有提示词...")
        self._prompts.clear()
        self.load_all_prompts()
    
    def validate_prompt_files(self) -> List[str]:
        """验证提示词文件的存在性和可读性"""
        issues = []
        
        for prompt_key, relative_path in self._file_mapping.items():
            file_path = self.base_path / relative_path
            
            if not file_path.exists():
                issues.append(f"文件不存在: {file_path}")
            elif not file_path.is_file():
                issues.append(f"不是文件: {file_path}")
            elif not os.access(file_path, os.R_OK):
                issues.append(f"文件不可读: {file_path}")
            else:
                # 尝试读取文件内容
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if not content.strip():
                        issues.append(f"文件为空: {file_path}")
                except Exception as e:
                    issues.append(f"读取文件失败 {file_path}: {e}")
        
        return issues
    
    def get_prompt_info(self, prompt_key: str) -> Optional[PromptInfo]:
        """获取提示词信息"""
        if prompt_key not in self._prompts:
            self._load_prompt_from_file(prompt_key)
        return self._prompts.get(prompt_key)
    
    def list_available_prompts(self) -> List[str]:
        """列出所有可用的提示词键"""
        return list(self._file_mapping.keys())
    
    def get_prompt_file_path(self, prompt_key: str) -> Optional[str]:
        """获取提示词文件路径"""
        if prompt_key in self._file_mapping:
            return str(self.base_path / self._file_mapping[prompt_key])
        return None


# 默认加载器实例
DEFAULT_PROMPT_LOADER = PromptLoader()