# 阶段5：日志系统完善

## 目标
实现完整的对话记录和日志管理系统，在每次对话结束后将完整的辩论过程保存为markdown格式文件到log目录。

## 具体任务

### 5.1 对话记录功能
实现完整的markdown格式对话保存：

#### 对话记录器
创建 `src/core/debate_logger.py`：
```python
class DebateLogger:
    def __init__(self, config_manager: UserConfigManager):
        self.config_manager = config_manager
        self.log_directory = self._get_log_directory()
        self.current_session = None
        self._ensure_log_directory()
    
    def start_logging_session(self, topic: str, participants: List[str]) -> str:
        """开始记录会话"""
        pass
    
    def log_message(self, message: Message) -> None:
        """记录消息"""
        pass
    
    def log_system_event(self, event: str, details: Dict[str, Any] = None) -> None:
        """记录系统事件"""
        pass
    
    def end_logging_session(self, summary: str = None) -> str:
        """结束记录会话并保存文件"""
        pass
    
    def generate_session_filename(self, topic: str, timestamp: datetime) -> str:
        """生成会话文件名"""
        pass
    
    def _get_log_directory(self) -> str:
        """获取日志目录"""
        pass
    
    def _ensure_log_directory(self) -> None:
        """确保日志目录存在"""
        pass
```

#### 日志会话管理
创建 `src/core/logging_session.py`：
```python
class LoggingSession:
    def __init__(self, session_id: str, topic: str, participants: List[str]):
        self.session_id = session_id
        self.topic = topic
        self.participants = participants
        self.start_time = datetime.now()
        self.end_time = None
        self.messages = []
        self.system_events = []
        self.metadata = {}
    
    def add_message(self, message: Message) -> None:
        """添加消息到会话"""
        pass
    
    def add_system_event(self, event: SystemEvent) -> None:
        """添加系统事件"""
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """设置元数据"""
        pass
    
    def finalize_session(self, summary: str = None) -> None:
        """完成会话"""
        pass
    
    def get_session_stats(self) -> Dict[str, Any]:
        """获取会话统计"""
        pass
```

### 5.2 Markdown格式化器
实现结构化的markdown输出：

#### Markdown生成器
创建 `src/core/markdown_generator.py`：
```python
class MarkdownGenerator:
    def __init__(self, session: LoggingSession):
        self.session = session
        self.template_loader = MarkdownTemplateLoader()
    
    def generate_full_report(self) -> str:
        """生成完整报告"""
        pass
    
    def generate_header(self) -> str:
        """生成报告头部"""
        pass
    
    def generate_summary_section(self) -> str:
        """生成摘要部分"""
        pass
    
    def generate_participants_section(self) -> str:
        """生成参与者部分"""
        pass
    
    def generate_timeline_section(self) -> str:
        """生成时间线部分"""
        pass
    
    def generate_messages_section(self) -> str:
        """生成消息部分"""
        pass
    
    def generate_statistics_section(self) -> str:
        """生成统计部分"""
        pass
    
    def format_message_as_markdown(self, message: Message) -> str:
        """将消息格式化为markdown"""
        pass
    
    def format_letter_message(self, message: Message) -> str:
        """格式化书信格式消息"""
        pass
```

#### Markdown模板系统
创建 `src/core/markdown_templates.py`：
```python
class MarkdownTemplateLoader:
    def __init__(self, template_dir: str = "src/config/templates"):
        self.template_dir = template_dir
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """加载模板文件"""
        pass
    
    def get_template(self, template_name: str) -> str:
        """获取模板"""
        pass
    
    def render_template(self, template_name: str, **kwargs) -> str:
        """渲染模板"""
        pass

# 模板示例
DEBATE_REPORT_TEMPLATE = """
# Athens辩论记录

## 基本信息
- **辩论主题**: {topic}
- **开始时间**: {start_time}
- **结束时间**: {end_time}
- **总时长**: {duration}
- **参与者**: {participants}

## 辩论摘要
{summary}

## 参与者信息
### Apollo (逻辑者)
- **模型**: {apollo_model}
- **发言次数**: {apollo_message_count}
- **平均响应时间**: {apollo_avg_response_time}

### Muses (疑问者)  
- **模型**: {muses_model}
- **发言次数**: {muses_message_count}
- **平均响应时间**: {muses_avg_response_time}

## 辩论过程

{messages}

## 关键时刻
{key_moments}

## 统计信息
- **总消息数**: {total_messages}
- **总词数**: {total_words}
- **辩论轮次**: {debate_rounds}
- **共识达成**: {consensus_reached}

## 系统事件
{system_events}

---
*报告生成时间: {report_generated_at}*
*生成工具: Athens MVP v{version}*
"""
```

### 5.3 日志目录管理
实现规范的日志目录结构和文件管理：

#### 目录结构管理器
创建 `src/core/log_directory_manager.py`：
```python
class LogDirectoryManager:
    def __init__(self, base_log_dir: str):
        self.base_log_dir = base_log_dir
        self.structure = self._define_directory_structure()
    
    def _define_directory_structure(self) -> Dict[str, str]:
        """定义目录结构"""
        return {
            'debates': os.path.join(self.base_log_dir, 'debates'),
            'daily': os.path.join(self.base_log_dir, 'daily'),
            'archives': os.path.join(self.base_log_dir, 'archives'),
            'exports': os.path.join(self.base_log_dir, 'exports'),
            'temp': os.path.join(self.base_log_dir, 'temp')
        }
    
    def ensure_directory_structure(self) -> None:
        """确保目录结构存在"""
        pass
    
    def get_daily_log_dir(self, date: datetime = None) -> str:
        """获取每日日志目录"""
        pass
    
    def get_debate_log_path(self, session_id: str, timestamp: datetime) -> str:
        """获取辩论日志路径"""
        pass
    
    def archive_old_logs(self, days_to_keep: int = 30) -> None:
        """归档旧日志"""
        pass
    
    def clean_temp_files(self) -> None:
        """清理临时文件"""
        pass
    
    def get_directory_stats(self) -> Dict[str, Any]:
        """获取目录统计"""
        pass
```

#### 文件命名规范
```python
class LogFileNaming:
    @staticmethod
    def generate_debate_filename(topic: str, session_id: str, timestamp: datetime) -> str:
        """生成辩论文件名"""
        # 格式: YYYYMMDD_HHMMSS_topic_sessionid.md
        date_str = timestamp.strftime("%Y%m%d_%H%M%S")
        safe_topic = LogFileNaming._sanitize_filename(topic)
        return f"{date_str}_{safe_topic}_{session_id[:8]}.md"
    
    @staticmethod
    def generate_daily_summary_filename(date: datetime) -> str:
        """生成每日摘要文件名"""
        return f"daily_summary_{date.strftime('%Y%m%d')}.md"
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """清理文件名"""
        pass
```

### 5.4 日志检索和管理
实现日志文件的检索和管理功能：

#### 日志检索器
创建 `src/core/log_searcher.py`：
```python
class LogSearcher:
    def __init__(self, log_directory_manager: LogDirectoryManager):
        self.directory_manager = log_directory_manager
        self.index = self._build_search_index()
    
    def search_by_topic(self, topic: str) -> List[str]:
        """按主题搜索"""
        pass
    
    def search_by_date_range(self, start_date: datetime, end_date: datetime) -> List[str]:
        """按日期范围搜索"""
        pass
    
    def search_by_participant(self, participant: str) -> List[str]:
        """按参与者搜索"""
        pass
    
    def search_by_keywords(self, keywords: List[str]) -> List[str]:
        """按关键词搜索"""
        pass
    
    def get_recent_debates(self, limit: int = 10) -> List[str]:
        """获取最近的辩论"""
        pass
    
    def _build_search_index(self) -> Dict[str, Any]:
        """构建搜索索引"""
        pass
    
    def rebuild_index(self) -> None:
        """重建索引"""
        pass
```

#### 日志管理器
创建 `src/core/log_manager.py`：
```python
class LogManager:
    def __init__(self, config_manager: UserConfigManager):
        self.config_manager = config_manager
        self.directory_manager = LogDirectoryManager(self._get_log_base_dir())
        self.searcher = LogSearcher(self.directory_manager)
        self.cleaner = LogCleaner(self.directory_manager)
    
    def list_all_logs(self) -> List[LogFileInfo]:
        """列出所有日志"""
        pass
    
    def get_log_info(self, log_path: str) -> LogFileInfo:
        """获取日志信息"""
        pass
    
    def delete_log(self, log_path: str, confirm: bool = False) -> bool:
        """删除日志"""
        pass
    
    def export_logs(self, log_paths: List[str], export_format: str = "zip") -> str:
        """导出日志"""
        pass
    
    def import_logs(self, import_path: str) -> List[str]:
        """导入日志"""
        pass
    
    def generate_summary_report(self, date_range: Tuple[datetime, datetime]) -> str:
        """生成摘要报告"""
        pass
```

### 5.5 集成到辩论流程
将日志系统集成到现有的辩论管理流程：

#### 修改DebateManager
更新 `src/core/debate_manager.py`：
```python
class DebateManager:
    def __init__(self, apollo, muses, topic, config_manager: UserConfigManager):
        # 原有初始化代码...
        self.logger = DebateLogger(config_manager)
        self.session_id = None
    
    def start_debate(self, initial_statement: str) -> None:
        """开始辩论，启动日志记录"""
        self.session_id = self.logger.start_logging_session(
            topic=self.topic,
            participants=[self.apollo.role_name, self.muses.role_name]
        )
        # 原有开始逻辑...
    
    def process_message(self, message: Message) -> None:
        """处理消息，记录到日志"""
        # 原有处理逻辑...
        self.logger.log_message(message)
    
    def end_debate(self, reason: str = None) -> str:
        """结束辩论，保存日志"""
        # 原有结束逻辑...
        
        # 生成摘要
        summarizer = ConversationSummarizer(self.conversation)
        summary = summarizer.summarize_debate()
        
        # 保存日志
        log_file_path = self.logger.end_logging_session(summary)
        
        return log_file_path
    
    def pause_debate(self) -> None:
        """暂停辩论，记录事件"""
        # 原有暂停逻辑...
        self.logger.log_system_event("debate_paused", {"timestamp": datetime.now()})
```

### 5.6 命令行日志管理接口
添加日志管理的命令行接口：

#### 日志命令
```bash
# 列出所有日志
python -m athens logs list

# 搜索日志
python -m athens logs search --topic "人工智能" --date "2024-01-01"

# 查看日志详情
python -m athens logs show <log_id>

# 删除日志
python -m athens logs delete <log_id>

# 导出日志
python -m athens logs export --format zip --output debates.zip

# 清理旧日志
python -m athens logs cleanup --days 30
```

#### 日志命令处理器
创建 `src/cli/log_commands.py`：
```python
class LogCommands:
    def __init__(self, log_manager: LogManager):
        self.log_manager = log_manager
    
    def list_logs(self, limit: int = 20, sort_by: str = "date") -> None:
        """列出日志"""
        pass
    
    def search_logs(self, **criteria) -> None:
        """搜索日志"""
        pass
    
    def show_log(self, log_id: str, format: str = "preview") -> None:
        """显示日志"""
        pass
    
    def delete_log(self, log_id: str, confirm: bool = False) -> None:
        """删除日志"""
        pass
    
    def export_logs(self, log_ids: List[str], format: str = "zip", output: str = None) -> None:
        """导出日志"""
        pass
    
    def cleanup_logs(self, days: int = 30, dry_run: bool = False) -> None:
        """清理日志"""
        pass
```

### 5.7 单元测试
创建日志系统的完整测试套件：

#### 测试文件
1. `tests/test_debate_logger.py` - 辩论记录器测试
2. `tests/test_markdown_generator.py` - Markdown生成器测试
3. `tests/test_log_directory_manager.py` - 目录管理器测试
4. `tests/test_log_searcher.py` - 日志检索测试
5. `tests/test_log_manager.py` - 日志管理器测试

#### 测试用例
1. 日志会话创建和管理测试
2. Markdown格式输出测试
3. 日志文件存储和检索测试
4. 目录结构管理测试
5. 日志清理和归档测试
6. 命令行接口测试

## 验收标准
1. 每次辩论结束后自动保存完整的markdown日志
2. 日志文件结构清晰，包含所有必要信息
3. 日志目录管理规范，支持搜索和清理
4. 提供完整的命令行日志管理接口
5. 日志系统性能良好，不影响辩论进行
6. 支持日志导出和备份功能
7. 所有日志测试通过
8. 与现有系统无缝集成

## 预计工作量
- 对话记录功能：1.5天
- Markdown生成器：1天
- 日志目录管理：1天
- 日志检索和管理：1天
- 集成到辩论流程：0.5天
- 命令行接口：0.5天
- 测试开发：1天
- 文档和调试：0.5天

## 依赖关系
- 需要阶段1的对话整理功能支持
- 需要阶段3的配置系统支持日志配置
- 需要阶段4的UI系统支持日志显示
- 作为最后阶段，集成所有前面的功能