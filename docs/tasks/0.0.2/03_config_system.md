# 阶段3：配置管理系统

## 目标
实现文件化配置管理和用户偏好记忆，将Prompt从代码中抽离到配置文件，建立用户配置持久化系统。

## 具体任务

### 3.1 Prompt文件化存储
将提示词从代码中分离到独立的配置文件系统：

#### 创建Prompt文件结构
```
src/config/prompts/
├── agents/
│   ├── apollo.txt          # Apollo角色提示词
│   ├── muses.txt           # Muses角色提示词
│   └── base_agent.txt      # 基础Agent提示词
├── debate/
│   ├── rules.txt           # 辩论规则
│   ├── format.txt          # 回应格式规范
│   └── consensus.txt       # 协商规则
├── ui/
│   ├── welcome.txt         # 欢迎消息
│   ├── help.txt           # 帮助信息
│   └── commands.txt        # 命令说明
└── system/
    ├── error_messages.txt  # 错误消息
    └── status_messages.txt # 状态消息
```

#### 实现Prompt加载器
创建 `src/config/prompt_loader.py`：
```python
class PromptLoader:
    def __init__(self, base_path: str = "src/config/prompts")
    def load_prompt(self, category: str, name: str) -> str
    def load_all_prompts(self) -> Dict[str, str]
    def reload_prompts(self) -> None
    def validate_prompt_files(self) -> List[str]
    def get_prompt_info(self, prompt_key: str) -> PromptInfo
```

#### 重构PromptConfig类
修改 `src/config/prompts.py`：
```python
class PromptConfig:
    def __init__(self, loader: PromptLoader = None):
        self.loader = loader or PromptLoader()
        self._prompts = {}
        self._load_all_prompts()
    
    def _load_all_prompts(self):
        """从文件加载所有提示词"""
        pass
    
    def reload_from_files(self):
        """重新从文件加载提示词"""
        pass
    
    def get_prompt_source(self, role: str) -> str:
        """获取提示词来源（文件路径）"""
        pass
```

### 3.2 用户配置系统
实现用户配置的持久化存储和管理：

#### 配置文件结构
创建 `$HOME/.athens/config.json`：
```json
{
    "version": "0.0.2",
    "user_preferences": {
        "theme": "default",
        "language": "zh_CN",
        "auto_save_debates": true,
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
        "show_timestamps": true,
        "show_typing_indicator": true,
        "auto_scroll": true,
        "input_box_style": "bordered"
    },
    "debate_settings": {
        "max_rounds": 20,
        "auto_end_after_consensus": true,
        "save_summaries": true,
        "summary_format": "markdown"
    },
    "directories": {
        "logs": "~/.athens/logs",
        "reports": "~/.athens/reports",
        "exports": "~/.athens/exports"
    }
}
```

#### 用户配置管理器
创建 `src/config/user_config.py`：
```python
class UserConfigManager:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = {}
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """获取默认配置路径 $HOME/.athens/config.json"""
        pass
    
    def _load_config(self) -> None:
        """加载配置文件"""
        pass
    
    def save_config(self) -> None:
        """保存配置文件"""
        pass
    
    def get_setting(self, key: str, default=None):
        """获取配置项"""
        pass
    
    def set_setting(self, key: str, value) -> None:
        """设置配置项"""
        pass
    
    def reset_to_defaults(self) -> None:
        """重置为默认配置"""
        pass
    
    def migrate_from_old_config(self) -> None:
        """从旧版本配置迁移"""
        pass
    
    def validate_config(self) -> List[str]:
        """验证配置有效性"""
        pass
```

#### 配置初始化
创建 `src/config/config_init.py`：
```python
class ConfigInitializer:
    def __init__(self, user_config_manager: UserConfigManager):
        self.config_manager = user_config_manager
    
    def ensure_config_directory(self) -> None:
        """确保配置目录存在"""
        pass
    
    def create_default_config(self) -> None:
        """创建默认配置文件"""
        pass
    
    def setup_directories(self) -> None:
        """设置必要的目录结构"""
        pass
    
    def check_permissions(self) -> bool:
        """检查文件权限"""
        pass
```

### 3.3 样式记忆功能
实现用户偏好的记忆和自动应用：

#### 样式偏好管理
修改 `src/ui/cli_interface.py`：
```python
class CLIInterface:
    def __init__(self, config_manager: UserConfigManager):
        self.config_manager = config_manager
        self.theme = self._load_saved_theme()
        self.ui_settings = self._load_ui_settings()
    
    def _load_saved_theme(self) -> str:
        """加载保存的主题设置"""
        pass
    
    def save_theme_preference(self, theme: str) -> None:
        """保存主题偏好"""
        pass
    
    def apply_saved_settings(self) -> None:
        """应用保存的设置"""
        pass
    
    def prompt_for_missing_settings(self) -> None:
        """提示用户配置缺失的设置"""
        pass
```

#### 首次运行向导
创建 `src/ui/setup_wizard.py`：
```python
class SetupWizard:
    def __init__(self, config_manager: UserConfigManager):
        self.config_manager = config_manager
    
    def run_first_time_setup(self) -> None:
        """运行首次设置向导"""
        pass
    
    def prompt_basic_settings(self) -> Dict[str, Any]:
        """提示基础设置"""
        pass
    
    def prompt_agent_preferences(self) -> Dict[str, Any]:
        """提示Agent偏好设置"""
        pass
    
    def prompt_ui_preferences(self) -> Dict[str, Any]:
        """提示UI偏好设置"""
        pass
    
    def confirm_settings(self, settings: Dict[str, Any]) -> bool:
        """确认设置"""
        pass
```

### 3.4 配置集成
将配置系统集成到现有代码中：

#### 修改Settings类
更新 `src/config/settings.py`：
```python
class Settings(BaseModel):
    def __init__(self, user_config_manager: UserConfigManager = None):
        self.user_config = user_config_manager or UserConfigManager()
        super().__init__()
    
    @property
    def apollo_model(self) -> str:
        return self.user_config.get_setting("agent_settings.apollo.model", "openai/gpt-4-turbo")
    
    @property
    def muses_model(self) -> str:
        return self.user_config.get_setting("agent_settings.muses.model", "anthropic/claude-3-opus")
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """获取指定Agent的配置"""
        pass
    
    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI配置"""
        pass
```

#### 主程序集成
修改 `src/main.py`：
```python
def main():
    # 初始化配置系统
    config_manager = UserConfigManager()
    config_init = ConfigInitializer(config_manager)
    config_init.ensure_config_directory()
    
    # 检查是否为首次运行
    if config_manager.is_first_run():
        wizard = SetupWizard(config_manager)
        wizard.run_first_time_setup()
    
    # 加载配置
    settings = Settings(config_manager)
    prompt_config = PromptConfig(PromptLoader())
    
    # 继续原有逻辑...
```

### 3.5 配置命令行接口
添加配置管理的命令行接口：

#### 配置命令
```bash
# 查看当前配置
python -m athens config show

# 设置配置项
python -m athens config set theme dark
python -m athens config set agent.apollo.model openai/gpt-4

# 重置配置
python -m athens config reset

# 运行设置向导
python -m athens config setup
```

#### 命令处理器
创建 `src/cli/config_commands.py`：
```python
class ConfigCommands:
    def __init__(self, config_manager: UserConfigManager):
        self.config_manager = config_manager
    
    def show_config(self, section: str = None) -> None:
        """显示配置"""
        pass
    
    def set_config(self, key: str, value: str) -> None:
        """设置配置项"""
        pass
    
    def reset_config(self, confirm: bool = False) -> None:
        """重置配置"""
        pass
    
    def run_setup(self) -> None:
        """运行设置向导"""
        pass
```

### 3.6 单元测试
创建配置系统的完整测试套件：

#### 测试文件
1. `tests/test_prompt_loader.py` - Prompt加载器测试
2. `tests/test_user_config.py` - 用户配置管理测试
3. `tests/test_config_init.py` - 配置初始化测试
4. `tests/test_setup_wizard.py` - 设置向导测试

#### 测试用例
1. 配置文件创建和加载测试
2. 配置项读写测试
3. 配置验证和迁移测试
4. Prompt文件加载测试
5. 用户偏好记忆测试
6. 首次运行流程测试

## 验收标准
1. Prompt已完全从代码中分离到配置文件
2. 用户配置能够正确保存和加载
3. 首次运行时提供设置向导
4. 用户偏好能够正确记忆和应用
5. 配置系统向后兼容
6. 所有配置测试通过
7. 提供完整的配置管理命令行接口

## 预计工作量
- Prompt文件化：1天
- 用户配置系统：1.5天
- 样式记忆功能：0.5天
- 配置集成：1天
- 测试开发：1天
- 文档和调试：0.5天

## 依赖关系
- 需要阶段2的角色重命名完成
- 为阶段4的UI优化提供配置基础
- 为阶段5的日志系统提供配置支持