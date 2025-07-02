# 阶段1：AI协商机制优化

## 目标
实现AI间的协商确认机制，优化辩论结束条件，使得疑问者需要明确表达"同意你的结论"才能结束讨论。

## 具体任务

### 1.1 协商结束检测机制
实现 `src/core/debate_manager.py` 的协商检测功能：
- 修改 `DebateManager` 类添加 `check_consensus()` 方法
- 实现"同意你的结论"关键词检测逻辑
- 添加协商状态管理 (`NEGOTIATING`, `CONSENSUS_REACHED`)
- 支持多种表达方式的同意检测（如"我同意"、"赞同你的观点"等）

核心功能扩展：
```python
class DebateManager:
    def check_consensus(self, message: Message) -> bool
    def detect_agreement_keywords(self, content: str) -> bool
    def update_consensus_state(self, state: ConsensusState)
    def get_consensus_status(self) -> ConsensusState
```

协商状态枚举：
- `ONGOING`: 讨论进行中
- `NEGOTIATING`: 协商阶段
- `CONSENSUS_REACHED`: 达成共识
- `CONSENSUS_FAILED`: 协商失败

### 1.2 对话整理输出功能
实现对话整理和格式化输出：
- 创建 `src/core/conversation_summarizer.py` 模块
- 实现 `ConversationSummarizer` 类处理对话整理
- 添加markdown格式化输出功能
- 集成到辩论结束流程

核心功能：
```python
class ConversationSummarizer:
    def __init__(self, conversation: Conversation)
    def summarize_debate(self) -> str
    def format_as_markdown(self) -> str
    def extract_key_points(self) -> List[str]
    def generate_conclusion(self) -> str
```

输出格式：
```markdown
# 辩论总结

## 辩论主题
[主题内容]

## 参与者
- Apollo (逻辑者)
- Muses (疑问者)

## 关键论点
### Apollo的观点
- [关键论点1]
- [关键论点2]

### Muses的质疑
- [质疑点1]
- [质疑点2]

## 最终结论
[达成共识的结论]

## 完整对话记录
[按时间顺序的完整对话]
```

### 1.3 辩论状态管理优化
扩展现有的辩论状态管理系统：
- 修改 `src/core/debate_states.py` 添加协商相关状态
- 实现状态转换逻辑和验证
- 添加状态持久化支持

### 1.4 单元测试
创建 `tests/test_consensus.py`:
- 测试协商检测的准确性和可靠性
- 测试不同表达方式的同意识别
- 测试对话整理功能的完整性
- 测试边界情况和异常处理

测试用例：
1. 基本同意检测测试
2. 多种表达方式测试
3. 否定表达过滤测试
4. 对话整理格式测试
5. 状态转换测试

## 验收标准
1. 疑问者明确表达同意后，辩论能够正确结束
2. 系统能识别多种同意表达方式
3. 辩论结束后自动输出完整的markdown总结
4. 所有单元测试通过
5. 与现有系统无缝集成

## 预计工作量
- 开发时间：2-3天
- 测试时间：1天
- 集成调试：0.5天

## 依赖关系
- 依赖现有的 `DebateManager` 和 `Message` 系统
- 需要与阶段2的角色重命名同步进行