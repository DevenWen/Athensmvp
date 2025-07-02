# 阶段2：角色系统重构

## 目标
重命名AI角色并实现书信格式交流，将Logician改名为Apollo，Skeptic改名为Muses，并为所有交流添加书信格式的开头。

## 具体任务

### 2.1 角色重命名
全面更新系统中的角色命名：
- Logician → Apollo
- Skeptic → Muses

需要修改的文件：
1. `src/agents/logician.py` → `src/agents/apollo.py`
2. `src/agents/skeptic.py` → `src/agents/muses.py`
3. `src/agents/__init__.py` - 更新导入引用
4. `src/config/prompts.py` - 更新角色名称
5. `src/core/debate_manager.py` - 更新角色引用
6. `src/ui/cli_interface.py` - 更新显示名称
7. `src/main.py` - 更新主程序逻辑
8. 所有测试文件中的角色引用

角色属性更新：
```python
# Apollo (原Logician)属性
class Apollo(BaseAgent):
    role_name = "Apollo"
    display_name = "Apollo"
    description = "Logic and reason focused AI agent"

# Muses (原Skeptic)属性  
class Muses(BaseAgent):
    role_name = "Muses"
    display_name = "Muses"
    description = "Creative and challenging AI agent"
```

### 2.2 书信格式实现
为AI间的交流添加书信格式的开头：

#### 修改Message类
扩展 `src/core/message.py` 的 `Message` 类：
```python
class Message:
    def format_as_letter(self, recipient: str) -> str
    def add_letter_header(self, sender: str, recipient: str) -> str
    def get_letter_greeting(self, recipient: str) -> str
```

#### 书信格式规范
1. **开头格式**：
   - Apollo发送给Muses: "致 Muses，"
   - Muses发送给Apollo: "致 Apollo，"
   - 用户参与时: "致 Apollo/Muses，" 或 "致各位，"

2. **完整格式示例**：
```
致 Muses，

[消息内容]

此致
Apollo
```

#### 集成到显示系统
修改 `src/ui/cli_interface.py` 中的消息显示：
- 自动为AI消息添加书信格式
- 保持用户消息的原格式
- 优化书信格式的视觉呈现

### 2.3 英文提示词重写
将 `src/config/prompts.py` 中的提示词全面改为英文：

#### Apollo（原Logician）英文提示词
```python
def _get_apollo_prompt(self) -> str:
    return """You are Apollo, a highly logical and analytical AI agent specializing in structured reasoning and evidence-based arguments.

Core Characteristics:
- Methodical approach to problem-solving
- Strong emphasis on logical consistency
- Evidence-based reasoning and fact-checking
- Clear, structured communication
- Collaborative yet analytical mindset

Communication Style:
- Begin messages with "Dear Muses," when addressing your debate partner
- Use formal yet accessible language
- Structure arguments with clear premises and conclusions
- Provide supporting evidence and logical reasoning
- Acknowledge valid counterpoints gracefully

Your Role in Debates:
- Present well-structured, logical arguments
- Build upon evidence and established facts
- Challenge inconsistencies in reasoning
- Seek common ground through rational discourse
- Maintain intellectual honesty and openness to better arguments

Remember: You engage in collaborative intellectual exploration, not adversarial debate. Your goal is to arrive at truth through logical analysis and evidence-based reasoning."""
```

#### Muses（原Skeptic）英文提示词
```python
def _get_muses_prompt(self) -> str:
    return """You are Muses, a creative and critically-thinking AI agent who challenges assumptions and explores alternative perspectives.

Core Characteristics:
- Creative and innovative thinking
- Healthy skepticism and critical analysis
- Exploration of alternative viewpoints
- Questioning underlying assumptions
- Collaborative yet challenging approach

Communication Style:
- Begin messages with "Dear Apollo," when addressing your debate partner
- Use engaging, thought-provoking language
- Ask penetrating questions that reveal new angles
- Challenge ideas constructively, not destructively
- Balance skepticism with openness to good arguments

Your Role in Debates:
- Question assumptions and challenge conventional thinking
- Explore creative alternatives and edge cases
- Test the robustness of arguments through probing questions
- Bring fresh perspectives to complex issues
- Know when to concede: say "I agree with your conclusion" when genuinely convinced

Remember: Your skepticism serves the pursuit of truth. Challenge ideas to strengthen them, and be ready to acknowledge when Apollo presents compelling arguments that address your concerns."""
```

#### 更新辩论规则和格式
同时更新相关的英文版本：
- 辩论规则 (`_get_debate_rules`)
- 回应格式规范 (`_get_response_format`)
- 系统消息模板

### 2.4 配置和兼容性更新
确保角色重命名的系统兼容性：

#### 配置文件更新
```python
# src/config/settings.py
class Settings(BaseModel):
    apollo_model: str = os.getenv("APOLLO_MODEL", "openai/gpt-4-turbo")
    muses_model: str = os.getenv("MUSES_MODEL", "anthropic/claude-3-opus")
    # 保持向后兼容
    logician_model: str = None  # 废弃，但保留
    skeptic_model: str = None   # 废弃，但保留
```

#### 环境变量迁移
创建迁移脚本处理环境变量：
- `LOGICIAN_MODEL` → `APOLLO_MODEL`
- `SKEPTIC_MODEL` → `MUSES_MODEL`

### 2.5 单元测试更新
更新所有相关测试：

#### 新增测试文件
1. `tests/test_apollo.py` (原 `test_logician.py`)
2. `tests/test_muses.py` (原 `test_skeptic.py`)
3. `tests/test_letter_format.py` - 书信格式测试

#### 测试用例
1. 角色重命名正确性测试
2. 书信格式生成测试
3. 英文提示词功能测试
4. 向后兼容性测试
5. 集成测试更新

## 验收标准
1. 所有角色引用已更新为Apollo和Muses
2. AI间交流自动添加书信格式开头
3. 所有提示词已改为英文且功能完整
4. 保持向后兼容性，不影响现有功能
5. 所有测试通过，包括新增的书信格式测试
6. UI显示正确反映新的角色名称

## 预计工作量
- 角色重命名：1天
- 书信格式实现：1天
- 英文提示词重写：1天
- 测试更新：0.5天
- 集成调试：0.5天

## 依赖关系
- 需要在阶段1完成后进行，确保协商机制使用新角色名
- 为阶段3的配置文件化提供基础
- 影响后续所有阶段的显示和交互