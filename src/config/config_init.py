"""
配置初始化模块
负责系统首次运行时的配置初始化和目录设置
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from .user_config import UserConfigManager

logger = logging.getLogger(__name__)


class ConfigInitializer:
    """配置初始化器"""
    
    def __init__(self, user_config_manager: UserConfigManager):
        self.config_manager = user_config_manager
        
    def ensure_config_directory(self) -> None:
        """确保配置目录存在"""
        try:
            config_path = Path(self.config_manager.config_path)
            config_dir = config_path.parent
            
            # 创建配置目录
            if not config_dir.exists():
                config_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建配置目录: {config_dir}")
            
            # 设置适当的权限（仅用户可读写）
            if os.name != 'nt':  # 非Windows系统
                os.chmod(config_dir, 0o700)
                
        except Exception as e:
            logger.error(f"创建配置目录失败: {e}")
            raise
    
    def create_default_config(self) -> None:
        """创建默认配置文件"""
        try:
            if not Path(self.config_manager.config_path).exists():
                logger.info("创建默认配置文件...")
                self.config_manager.save_config()
                logger.info("默认配置文件创建完成")
            else:
                logger.debug("配置文件已存在，跳过创建")
                
        except Exception as e:
            logger.error(f"创建默认配置文件失败: {e}")
            raise
    
    def setup_directories(self) -> None:
        """设置必要的目录结构"""
        try:
            # 获取目录配置
            directories = self.config_manager.get_setting("directories", {})
            
            for dir_name, dir_path in directories.items():
                if dir_path:
                    # 展开用户目录
                    expanded_path = Path(dir_path).expanduser()
                    
                    if not expanded_path.exists():
                        expanded_path.mkdir(parents=True, exist_ok=True)
                        logger.info(f"创建目录 {dir_name}: {expanded_path}")
                    
                    # 创建子目录结构
                    self._create_subdirectories(dir_name, expanded_path)
                    
        except Exception as e:
            logger.error(f"设置目录结构失败: {e}")
            raise
    
    def _create_subdirectories(self, dir_type: str, base_path: Path) -> None:
        """为特定类型的目录创建子目录"""
        try:
            if dir_type == "logs":
                # 日志目录的子目录
                subdirs = ["debate", "system", "error"]
                for subdir in subdirs:
                    subdir_path = base_path / subdir
                    subdir_path.mkdir(exist_ok=True)
                    logger.debug(f"创建日志子目录: {subdir_path}")
                    
            elif dir_type == "reports":
                # 报告目录的子目录
                subdirs = ["summaries", "transcripts", "analysis"]
                for subdir in subdirs:
                    subdir_path = base_path / subdir
                    subdir_path.mkdir(exist_ok=True)
                    logger.debug(f"创建报告子目录: {subdir_path}")
                    
            elif dir_type == "exports":
                # 导出目录的子目录
                subdirs = ["json", "markdown", "pdf"]
                for subdir in subdirs:
                    subdir_path = base_path / subdir
                    subdir_path.mkdir(exist_ok=True)
                    logger.debug(f"创建导出子目录: {subdir_path}")
                    
        except Exception as e:
            logger.warning(f"创建子目录失败 {dir_type}: {e}")
    
    def check_permissions(self) -> bool:
        """检查文件权限"""
        try:
            config_path = Path(self.config_manager.config_path)
            config_dir = config_path.parent
            
            # 检查目录权限
            if not os.access(config_dir, os.R_OK | os.W_OK):
                logger.error(f"配置目录权限不足: {config_dir}")
                return False
            
            # 检查配置文件权限（如果存在）
            if config_path.exists():
                if not os.access(config_path, os.R_OK | os.W_OK):
                    logger.error(f"配置文件权限不足: {config_path}")
                    return False
            
            # 检查工作目录权限
            directories = self.config_manager.get_setting("directories", {})
            for dir_name, dir_path in directories.items():
                if dir_path:
                    expanded_path = Path(dir_path).expanduser()
                    if expanded_path.exists():
                        if not os.access(expanded_path, os.R_OK | os.W_OK):
                            logger.warning(f"目录权限不足 {dir_name}: {expanded_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"检查权限失败: {e}")
            return False
    
    def validate_environment(self) -> List[str]:
        """验证运行环境"""
        issues = []
        
        try:
            # 检查Python版本
            import sys
            if sys.version_info < (3, 7):
                issues.append(f"Python版本过低: {sys.version}")
            
            # 检查必要的环境变量
            required_env_vars = ["OPENROUTER_API_KEY"]
            for var in required_env_vars:
                if not os.getenv(var):
                    issues.append(f"缺失环境变量: {var}")
            
            # 检查磁盘空间
            config_dir = Path(self.config_manager.config_path).parent
            if config_dir.exists():
                import shutil
                free_space = shutil.disk_usage(config_dir).free
                if free_space < 10 * 1024 * 1024:  # 10MB
                    issues.append(f"磁盘空间不足: {free_space / 1024 / 1024:.1f}MB")
            
            # 检查网络连接（简单测试）
            try:
                import socket
                socket.create_connection(("8.8.8.8", 53), timeout=3)
            except Exception:
                issues.append("网络连接异常")
            
        except Exception as e:
            issues.append(f"环境验证失败: {e}")
        
        return issues
    
    def initialize_logging(self) -> None:
        """初始化日志系统"""
        try:
            # 获取日志目录
            log_dir = self.config_manager.get_setting("directories.logs", "/tmp/athensmvp/logs")
            log_path = Path(log_dir)
            
            # 确保日志目录存在
            log_path.mkdir(parents=True, exist_ok=True)
            
            # 配置日志
            log_level = self.config_manager.get_setting("user_preferences.log_level", "INFO")
            
            # 清除现有的日志处理器
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            
            # 设置新的日志配置
            logging.basicConfig(
                level=getattr(logging, log_level.upper(), logging.INFO),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_path / "athens.log", encoding='utf-8'),
                    # 只在DEBUG级别时输出到控制台
                    logging.StreamHandler() if log_level.upper() == 'DEBUG' else logging.NullHandler()
                ],
                force=True  # 强制重新配置
            )
            
            logger.info("日志系统初始化完成")
            logger.info(f"日志文件位置: {log_path / 'athens.log'}")
            
        except Exception as e:
            # 如果日志初始化失败，至少配置基本的控制台日志
            logging.basicConfig(level=logging.INFO, force=True)
            logger.error(f"日志系统初始化失败: {e}")
    
    def run_initialization(self) -> Dict[str, Any]:
        """运行完整的初始化流程"""
        result = {
            "success": False,
            "steps_completed": [],
            "errors": [],
            "warnings": []
        }
        
        try:
            # 步骤1: 确保配置目录
            self.ensure_config_directory()
            result["steps_completed"].append("配置目录创建")
            
            # 步骤2: 创建默认配置
            self.create_default_config()
            result["steps_completed"].append("默认配置创建")
            
            # 步骤3: 设置目录结构
            self.setup_directories()
            result["steps_completed"].append("目录结构设置")
            
            # 步骤4: 检查权限
            if self.check_permissions():
                result["steps_completed"].append("权限检查通过")
            else:
                result["warnings"].append("权限检查失败")
            
            # 步骤5: 验证环境
            env_issues = self.validate_environment()
            if env_issues:
                result["warnings"].extend(env_issues)
            else:
                result["steps_completed"].append("环境验证通过")
            
            # 步骤6: 初始化日志
            self.initialize_logging()
            result["steps_completed"].append("日志系统初始化")
            
            result["success"] = True
            logger.info("配置初始化完成")
            
        except Exception as e:
            error_msg = f"初始化失败: {e}"
            result["errors"].append(error_msg)
            logger.error(error_msg)
        
        return result
    
    def cleanup_old_files(self, days_old: int = 30) -> None:
        """清理旧文件"""
        try:
            import time
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            
            # 清理旧日志文件
            log_dir = Path(self.config_manager.get_setting("directories.logs", "~/.athens/logs")).expanduser()
            if log_dir.exists():
                for log_file in log_dir.rglob("*.log"):
                    if log_file.stat().st_mtime < cutoff_time:
                        log_file.unlink()
                        logger.debug(f"删除旧日志文件: {log_file}")
            
            # 清理旧备份文件
            config_dir = Path(self.config_manager.config_path).parent
            for backup_file in config_dir.glob("*.backup"):
                if backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
                    logger.debug(f"删除旧备份文件: {backup_file}")
                    
        except Exception as e:
            logger.warning(f"清理旧文件失败: {e}")