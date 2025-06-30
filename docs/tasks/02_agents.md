# 阶段2：AI智能体核心

## 目标
实现Athens的双AI智能体系统，包括基础智能体抽象类、逻辑者角色和怀疑者角色，以及精心设计的角色提示词。

## 具体任务

### 2.1 基础智能体抽象类
实现 `src/agents/base_agent.py`：
- 定义智能体基础接口和行为
- 管理对话历史和上下文
- 提供统一的消息发送和接收机制
- 支持角色切换和状态管理

核心功能：
```python
class BaseAgent:
    def __init__(self, name, role_prompt, ai_client)
    def send_message(self, content, recipient=None)
    def receive_message(self, message)
    def generate_response(self, context)
    def get_conversation_history(self)
    def reset_conversation(self)
```

### 2.2 逻辑者角色实现
实现 `src/agents/logician.py`：
- 继承BaseAgent
- 专注于逻辑论证和支持观点
- 倾向于寻找证据和理性分析
- 构建有条理的论述结构

角色特征：
- 系统性思维
- 证据导向
- 逻辑严谨
- 支持论证

### 2.3 怀疑者角色实现
实现 `src/agents/skeptic.py`：
- 继承BaseAgent
- 专注于批判思维和质疑反驳
- 寻找论证中的漏洞和问题
- 提出反例和替代观点

角色特征：
- 批判性思维
- 问题导向
- 挑战假设
- 反驳论证

### 2.4 角色提示词设计
实现 `src/config/prompts.py`：
- 逻辑者的系统提示词
- 怀疑者的系统提示词  
- 辩论规则和行为准则
- 回应格式规范

提示词要素：
- 角色人格定义
- 思维方式指导
- 回应风格规范
- 辩论礼仪要求

## 文件清单
需要创建的文件：
- [ ] src/agents/base_agent.py
- [ ] src/agents/logician.py
- [ ] src/agents/skeptic.py
- [ ] src/config/prompts.py
- [ ] tests/test_agents.py

需要修改的文件：
- [ ] src/agents/__init__.py (导出类)
- [ ] src/config/__init__.py (导出配置)

## 测试方法
1. 基础智能体类功能测试
2. 逻辑者角色行为验证
3. 怀疑者角色行为验证
4. 角色提示词效果测试
5. 智能体间基础交互测试

## 依赖关系
- **前置条件**：阶段1的AI客户端
- **后续阶段**：阶段3的消息系统将使用智能体
- **关键输出**：可工作的双AI智能体

## 验收标准
- ✅ 基础智能体类完整实现
- ✅ 逻辑者能生成支持性论证
- ✅ 怀疑者能生成批判性质疑
- ✅ 角色提示词效果明显
- ✅ 智能体测试全部通过

## 示例交互流程
```
用户话题：Elixir具有很强的容错性

逻辑者：基于Actor模型和Let it crash哲学，Elixir确实具有...[支持论证]
怀疑者：但是这种说法忽略了...[质疑反驳]
逻辑者：你提到的问题确实存在，但是...[进一步论证]
怀疑者：即使如此，还有一个关键问题...[深度质疑]
```