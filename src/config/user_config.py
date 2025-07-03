"""
用户配置管理模块
负责用户个人配置的持久化存储和管理
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class UserConfigManager:
    """用户配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}
        self._load_config()
        
    def _get_default_config_path(self) -> str:
        """获取默认配置路径 $HOME/.athens/config.json"""
        home_dir = Path.home()
        athens_dir = home_dir / ".athens"
        return str(athens_dir / "config.json")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "version": "0.0.3",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "user_preferences": {
                "theme": "default",
                "language": "zh_CN",
                "auto_save_debates": True,
                "debate_history_limit": 100
            },
            "agent_settings": {
                "apollo": {
                    "model": "openai/gpt-4-turbo",
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                "muses": {
                    "model": "anthropic/claude-3-opus",
                    "temperature": 0.8,
                    "max_tokens": 2000
                }
            },
            "ui_settings": {
                "theme": "default",
                "show_timestamps": True,
                "show_typing_indicator": True,
                "auto_scroll": True,
                "input_box_style": "bordered"
            },
            "debate_settings": {
                "max_rounds": 20,
                "auto_end_after_consensus": True,
                "save_summaries": True,
                "summary_format": "markdown"
            },
            "directories": {
                "logs": "/tmp/athensmvp/logs",
                "reports": "/tmp/athensmvp/reports",
                "exports": "/tmp/athensmvp/exports"
            }
        }
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"配置已从 {self.config_path} 加载")
                
                # 检查并更新配置版本
                self._migrate_config_if_needed()
            else:
                logger.info("配置文件不存在，使用默认配置")
                self.config = self._get_default_config()
                self._ensure_config_directory()
                self.save_config()
                
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            logger.info("使用默认配置")
            self.config = self._get_default_config()
    
    def _ensure_config_directory(self) -> None:
        """确保配置目录存在"""
        config_dir = Path(self.config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"确保配置目录存在: {config_dir}")
    
    def _migrate_config_if_needed(self) -> None:
        """如果需要，迁移配置文件到新版本"""
        current_version = self.config.get("version", "0.0.1")
        target_version = "0.0.3"
        
        if current_version != target_version:
            logger.info(f"配置版本从 {current_version} 迁移到 {target_version}")
            self.migrate_from_old_config()
            self.config["version"] = target_version
            self.config["updated_at"] = datetime.now().isoformat()
            self.save_config()
    
    def save_config(self) -> None:
        """保存配置文件"""
        try:
            self._ensure_config_directory()
            
            # 更新修改时间
            self.config["updated_at"] = datetime.now().isoformat()
            
            # 创建备份
            self._create_backup()
            
            # 保存配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已保存到 {self.config_path}")
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            raise
    
    def _create_backup(self) -> None:
        """创建配置文件备份"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                backup_path = config_file.with_suffix('.json.backup')
                import shutil
                shutil.copy2(config_file, backup_path)
                logger.debug(f"配置备份已创建: {backup_path}")
        except Exception as e:
            logger.warning(f"创建配置备份失败: {e}")
    
    def get_setting(self, key: str, default=None):
        """获取配置项，支持嵌套键如 'agent_settings.apollo.model'"""
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except Exception as e:
            logger.warning(f"获取配置项失败 {key}: {e}")
            return default
    
    def set_setting(self, key: str, value: Any) -> None:
        """设置配置项，支持嵌套键"""
        try:
            keys = key.split('.')
            config = self.config
            
            # 导航到父级字典
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            logger.info(f"配置项已更新: {key} = {value}")
            
        except Exception as e:
            logger.error(f"设置配置项失败 {key}: {e}")
            raise
    
    def reset_to_defaults(self) -> None:
        """重置为默认配置"""
        logger.info("重置配置为默认值")
        self.config = self._get_default_config()
        self.save_config()
    
    def migrate_from_old_config(self) -> None:
        """从旧版本配置迁移"""
        logger.info("迁移旧版本配置...")
        
        # 确保必要的配置节存在
        default_config = self._get_default_config()
        
        for section, default_values in default_config.items():
            if section not in self.config:
                self.config[section] = default_values
                logger.debug(f"添加缺失配置节: {section}")
            elif isinstance(default_values, dict):
                # 合并嵌套配置
                for key, default_value in default_values.items():
                    if key not in self.config[section]:
                        self.config[section][key] = default_value
                        logger.debug(f"添加缺失配置项: {section}.{key}")
    
    def validate_config(self) -> List[str]:
        """验证配置有效性"""
        issues = []
        
        # 检查必要的配置节
        required_sections = ["user_preferences", "agent_settings", "ui_settings", "debate_settings"]
        for section in required_sections:
            if section not in self.config:
                issues.append(f"缺失配置节: {section}")
        
        # 检查模型配置
        for agent in ["apollo", "muses"]:
            model = self.get_setting(f"agent_settings.{agent}.model")
            if not model:
                issues.append(f"缺失模型配置: agent_settings.{agent}.model")
        
        # 检查目录配置
        directories = self.get_setting("directories", {})
        for dir_name, dir_path in directories.items():
            if not dir_path:
                issues.append(f"目录路径为空: directories.{dir_name}")
        
        return issues
    
    def is_first_run(self) -> bool:
        """检查是否为首次运行"""
        return not Path(self.config_path).exists()
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置信息"""
        return {
            "config_path": self.config_path,
            "version": self.config.get("version", "unknown"),
            "created_at": self.config.get("created_at", "unknown"),
            "updated_at": self.config.get("updated_at", "unknown"),
            "file_exists": Path(self.config_path).exists(),
            "file_size": Path(self.config_path).stat().st_size if Path(self.config_path).exists() else 0
        }
    
    def export_config(self, export_path: str) -> None:
        """导出配置到指定路径"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"配置已导出到 {export_path}")
        except Exception as e:
            logger.error(f"导出配置失败: {e}")
            raise
    
    def import_config(self, import_path: str) -> None:
        """从指定路径导入配置"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # 验证导入的配置
            temp_manager = UserConfigManager()
            temp_manager.config = imported_config
            issues = temp_manager.validate_config()
            
            if issues:
                raise ValueError(f"导入的配置无效: {', '.join(issues)}")
            
            self.config = imported_config
            self.save_config()
            logger.info(f"配置已从 {import_path} 导入")
            
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            raise


# 默认用户配置管理器实例
DEFAULT_USER_CONFIG = UserConfigManager()