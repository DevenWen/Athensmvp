# 阶段4：UI交互优化

## 目标
改进用户界面，实现固定在底部的输入框设计，提升用户交互体验，按照PRD要求实现类似于边框样式的输入框UI。

## 具体任务

### 4.1 输入框UI设计
实现PRD中指定的底部固定输入框：

#### 目标样式
```
╭───────────────────────────────────────────────────────────────────────────────────────────────────╮
│ > Try "how do I log an error?"                                                                    │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
```

#### 创建输入框组件
创建 `src/ui/input_box.py`：
```python
class InputBox:
    def __init__(self, console: Console, prompt_text: str = "> "):
        self.console = console
        self.prompt_text = prompt_text
        self.box_style = self._get_box_style()
    
    def _get_box_style(self) -> box.Box:
        """获取输入框样式"""
        pass
    
    def render_input_box(self, placeholder: str = "") -> Panel:
        """渲染输入框"""
        pass
    
    def get_user_input(self, placeholder: str = "Type your message...") -> str:
        """获取用户输入"""
        pass
    
    def clear_input_area(self) -> None:
        """清除输入区域"""
        pass
    
    def show_typing_indicator(self) -> None:
        """显示输入指示器"""
        pass
```

#### 布局管理器
创建 `src/ui/layout_manager.py`：
```python
class LayoutManager:
    def __init__(self, console: Console):
        self.console = console
        self.layout = Layout()
        self._setup_layout()
    
    def _setup_layout(self) -> None:
        """设置布局结构"""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="input", size=3)
        )
    
    def update_header(self, content) -> None:
        """更新头部内容"""
        pass
    
    def update_main_content(self, content) -> None:
        """更新主要内容区域"""
        pass
    
    def update_input_area(self, content) -> None:
        """更新输入区域"""
        pass
    
    def render_layout(self) -> None:
        """渲染整个布局"""
        pass
    
    def get_terminal_size(self) -> Tuple[int, int]:
        """获取终端大小"""
        pass
```

### 4.2 界面交互优化
改进用户输入和显示体验：

#### 实时更新系统
创建 `src/ui/realtime_updater.py`：
```python
class RealtimeUpdater:
    def __init__(self, layout_manager: LayoutManager):
        self.layout_manager = layout_manager
        self.update_queue = Queue()
        self.running = False
    
    def start_updater(self) -> None:
        """启动实时更新器"""
        pass
    
    def stop_updater(self) -> None:
        """停止实时更新器"""
        pass
    
    def queue_update(self, area: str, content) -> None:
        """队列更新请求"""
        pass
    
    def process_updates(self) -> None:
        """处理更新队列"""
        pass
    
    def handle_resize(self) -> None:
        """处理终端大小变化"""
        pass
```

#### 改进CLI界面
重构 `src/ui/cli_interface.py`：
```python
class CLIInterface:
    def __init__(self, config_manager: UserConfigManager):
        self.config_manager = config_manager
        self.console = Console()
        self.layout_manager = LayoutManager(self.console)
        self.input_box = InputBox(self.console)
        self.realtime_updater = RealtimeUpdater(self.layout_manager)
        self._setup_interface()
    
    def _setup_interface(self) -> None:
        """设置界面"""
        pass
    
    def show_welcome_screen(self) -> None:
        """显示欢迎界面"""
        pass
    
    def start_interactive_mode(self) -> None:
        """启动交互模式"""
        pass
    
    def handle_user_input(self) -> str:
        """处理用户输入"""
        pass
    
    def display_message_with_layout(self, message: Message) -> None:
        """使用新布局显示消息"""
        pass
    
    def show_typing_indicator(self, agent_name: str) -> None:
        """显示AI输入指示器"""
        pass
    
    def hide_typing_indicator(self) -> None:
        """隐藏输入指示器"""
        pass
```

### 4.3 消息显示优化
改进消息显示的视觉效果：

#### 书信格式显示
创建 `src/ui/message_renderer.py`：
```python
class MessageRenderer:
    def __init__(self, theme: Dict[str, str]):
        self.theme = theme
    
    def render_letter_message(self, message: Message) -> Panel:
        """渲染书信格式消息"""
        pass
    
    def render_user_message(self, message: Message) -> Panel:
        """渲染用户消息"""
        pass
    
    def render_system_message(self, message: Message) -> Panel:
        """渲染系统消息"""
        pass
    
    def format_letter_content(self, content: str, sender: str, recipient: str) -> str:
        """格式化书信内容"""
        pass
    
    def add_message_metadata(self, message: Message) -> Text:
        """添加消息元数据"""
        pass
    
    def apply_theme_styling(self, content: Text, message_type: str) -> Text:
        """应用主题样式"""
        pass
```

#### 滚动和历史管理
创建 `src/ui/scroll_manager.py`：
```python
class ScrollManager:
    def __init__(self, max_messages: int = 100):
        self.max_messages = max_messages
        self.message_history = []
        self.current_position = 0
    
    def add_message(self, rendered_message) -> None:
        """添加新消息"""
        pass
    
    def scroll_up(self, lines: int = 1) -> None:
        """向上滚动"""
        pass
    
    def scroll_down(self, lines: int = 1) -> None:
        """向下滚动"""
        pass
    
    def scroll_to_bottom(self) -> None:
        """滚动到底部"""
        pass
    
    def get_visible_messages(self, height: int) -> List:
        """获取可见消息"""
        pass
    
    def clear_history(self) -> None:
        """清除历史"""
        pass
```

### 4.4 键盘快捷键支持
添加键盘快捷键功能：

#### 快捷键处理器
创建 `src/ui/keyboard_handler.py`：
```python
class KeyboardHandler:
    def __init__(self, cli_interface: CLIInterface):
        self.cli_interface = cli_interface
        self.key_bindings = self._setup_key_bindings()
    
    def _setup_key_bindings(self) -> Dict[str, Callable]:
        """设置键盘绑定"""
        return {
            'ctrl+c': self.exit_application,
            'ctrl+l': self.clear_screen,
            'ctrl+d': self.end_debate,
            'ctrl+p': self.pause_debate,
            'ctrl+r': self.resume_debate,
            'ctrl+s': self.save_debate,
            'page_up': self.scroll_up,
            'page_down': self.scroll_down,
            'home': self.scroll_to_top,
            'end': self.scroll_to_bottom
        }
    
    def handle_key_press(self, key: str) -> bool:
        """处理按键事件"""
        pass
    
    def exit_application(self) -> None:
        """退出应用"""
        pass
    
    def clear_screen(self) -> None:
        """清屏"""
        pass
    
    def show_help(self) -> None:
        """显示帮助"""
        pass
```

### 4.5 响应式设计
实现终端大小自适应：

#### 响应式布局
修改 `LayoutManager` 添加响应式功能：
```python
class LayoutManager:
    def adapt_to_terminal_size(self) -> None:
        """适应终端大小"""
        width, height = self.get_terminal_size()
        
        if width < 80:  # 小屏幕
            self._setup_compact_layout()
        elif width > 120:  # 大屏幕
            self._setup_wide_layout()
        else:  # 标准屏幕
            self._setup_standard_layout()
    
    def _setup_compact_layout(self) -> None:
        """紧凑布局"""
        pass
    
    def _setup_wide_layout(self) -> None:
        """宽屏布局"""
        pass
    
    def _setup_standard_layout(self) -> None:
        """标准布局"""
        pass
```

#### 动态文本换行
创建 `src/ui/text_wrapper.py`：
```python
class TextWrapper:
    def __init__(self, width: int):
        self.width = width
    
    def wrap_message_content(self, content: str) -> List[str]:
        """包装消息内容"""
        pass
    
    def wrap_preserving_format(self, text: str) -> List[str]:
        """保持格式的文本包装"""
        pass
    
    def calculate_optimal_width(self, terminal_width: int) -> int:
        """计算最优文本宽度"""
        pass
```

### 4.6 性能优化
优化UI渲染性能：

#### 渲染缓存
创建 `src/ui/render_cache.py`：
```python
class RenderCache:
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
    
    def get_cached_render(self, message_id: str):
        """获取缓存的渲染结果"""
        pass
    
    def cache_render(self, message_id: str, rendered_content) -> None:
        """缓存渲染结果"""
        pass
    
    def invalidate_cache(self, message_id: str = None) -> None:
        """失效缓存"""
        pass
    
    def clear_cache(self) -> None:
        """清除所有缓存"""
        pass
```

#### 延迟渲染
实现消息的延迟渲染机制：
```python
class LazyRenderer:
    def __init__(self, message_renderer: MessageRenderer):
        self.message_renderer = message_renderer
        self.pending_renders = Queue()
    
    def queue_render(self, message: Message) -> None:
        """队列渲染任务"""
        pass
    
    def process_render_queue(self) -> None:
        """处理渲染队列"""
        pass
    
    def render_visible_only(self, visible_messages: List[Message]) -> None:
        """只渲染可见消息"""
        pass
```

### 4.7 单元测试
创建UI优化的测试套件：

#### 测试文件
1. `tests/test_input_box.py` - 输入框测试
2. `tests/test_layout_manager.py` - 布局管理器测试  
3. `tests/test_message_renderer.py` - 消息渲染器测试
4. `tests/test_keyboard_handler.py` - 键盘处理器测试
5. `tests/test_responsive_design.py` - 响应式设计测试

#### 测试用例
1. 输入框渲染和交互测试
2. 布局适应性测试
3. 消息显示格式测试
4. 键盘快捷键功能测试
5. 终端大小变化处理测试
6. 性能和内存使用测试

## 验收标准
1. 底部输入框按照PRD要求正确显示
2. 消息区域和输入区域布局合理
3. 支持终端大小变化的响应式设计
4. 键盘快捷键功能正常
5. 书信格式消息显示美观
6. 滚动和历史管理功能完善
7. UI性能良好，无明显卡顿
8. 所有UI测试通过

## 预计工作量
- 输入框UI设计：1天
- 布局管理器：1天
- 消息显示优化：1天
- 键盘快捷键：0.5天
- 响应式设计：0.5天
- 性能优化：0.5天
- 测试开发：1天
- 集成调试：0.5天

## 依赖关系
- 需要阶段2的书信格式支持
- 需要阶段3的配置系统支持主题和UI设置
- 为阶段5的日志显示提供UI基础