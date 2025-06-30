# 阶段3：消息和通信系统

## 目标
建立Athens系统的消息传递和通信机制，实现智能体间的结构化对话、历史管理和上下文维护。

## 具体任务

### 3.1 消息结构定义
实现 `src/core/message.py`：
- 定义标准化的消息格式
- 支持不同类型的消息（论证、质疑、总结等）
- 包含元数据（时间戳、发送者、接收者等）
- 支持消息序列化和反序列化

消息结构：
```python
@dataclass
class Message:
    id: str
    sender: str
    recipient: str
    content: str
    message_type: MessageType
    timestamp: datetime
    context: Dict[str, Any]
    references: List[str]  # 引用的消息ID
```

消息类型：
- `ARGUMENT`: 论证陈述
- `COUNTER`: 反驳质疑
- `CLARIFICATION`: 澄清说明
- `SUMMARY`: 总结概述
- `USER_INPUT`: 用户输入

### 3.2 对话历史管理
实现 `src/core/conversation.py`：
- 管理完整的对话历史记录
- 支持按时间线/主题线组织消息
- 提供消息检索和过滤功能
- 支持对话分支和合并

核心功能：
```python
class Conversation:
    def add_message(self, message: Message)
    def get_messages_by_sender(self, sender: str)
    def get_context_for_agent(self, agent: str, depth: int)
    def get_recent_exchanges(self, count: int)
    def find_referenced_messages(self, message_id: str)
    def export_to_dict(self)
```

### 3.3 智能体间通信机制
实现 `src/core/communication.py`：
- 消息路由和分发
- 支持直接对话和广播
- 处理消息引用和回复链
- 管理通信状态和流程

通信功能：
- 点对点消息传递
- 消息确认机制
- 引用回复支持
- 通信日志记录

### 3.4 上下文管理
实现 `src/core/context_manager.py`：
- 智能地维护对话上下文
- 控制上下文长度和相关性
- 支持主题转换和上下文切换
- 优化AI模型的输入效率

上下文策略：
- 基于时间的上下文窗口
- 基于相关性的内容过滤
- 智能上下文压缩
- 关键信息保留

## 文件清单
需要创建的文件：
- [ ] src/core/message.py
- [ ] src/core/conversation.py
- [ ] src/core/communication.py
- [ ] src/core/context_manager.py
- [ ] tests/test_messaging.py

需要修改的文件：
- [ ] src/core/__init__.py (导出类)
- [ ] src/agents/base_agent.py (集成消息系统)

## 测试方法
1. 消息结构创建和序列化测试
2. 对话历史存储和检索测试
3. 智能体间消息传递测试
4. 上下文管理策略验证
5. 引用回复功能测试

## 依赖关系
- **前置条件**：阶段2的智能体系统
- **后续阶段**：阶段4的辩论管理器将使用通信系统
- **关键输出**：完整的消息传递基础设施

## 验收标准
- ✅ 消息结构完整且可序列化
- ✅ 对话历史正确保存和检索
- ✅ 智能体能够正常通信
- ✅ 上下文管理有效工作
- ✅ 所有消息传递测试通过

## 设计要点

### 消息流程示例
```
1. 用户提出话题 -> USER_INPUT 消息
2. 逻辑者分析 -> ARGUMENT 消息
3. 怀疑者质疑 -> COUNTER 消息(引用逻辑者消息)
4. 逻辑者回应 -> ARGUMENT 消息(引用怀疑者消息)
5. 用户介入 -> USER_INPUT 消息(引用某条消息)
```

### 上下文管理策略
- 保留最近N条消息
- 保留所有用户输入消息
- 保留被引用的关键消息
- 压缩过长的历史消息