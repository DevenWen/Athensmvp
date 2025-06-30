# 阶段1：基础架构

## 目标
搭建Athens MVP项目的基础架构，包括目录结构、依赖管理、环境配置和OpenRouter客户端基础封装。

## 具体任务

### 1.1 项目目录结构
创建完整的项目目录结构：
```
athens_mvp/
├── src/
│   ├── agents/
│   │   └── __init__.py
│   ├── core/
│   │   └── __init__.py
│   ├── ui/
│   │   └── __init__.py
│   ├── config/
│   │   └── __init__.py
│   └── main.py
├── docs/
│   ├── work_logs/
│   └── tasks/
├── reports/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

### 1.2 依赖管理
创建 `requirements.txt` 包含：
- `openai>=1.0.0` (OpenRouter兼容客户端)
- `python-dotenv` (环境变量管理)
- `rich` (美化CLI输出)
- `pydantic>=2.0.0` (数据验证和序列化)
- `pytest` (测试框架)

### 1.3 环境配置
- 创建 `.env.example` 模板文件
- 实现 `src/config/settings.py` 配置管理
- 支持OpenRouter API密钥和模型配置

### 1.4 OpenRouter客户端基础封装
- 实现 `src/core/ai_client.py`
- 封装OpenAI兼容的客户端
- 支持多模型切换
- 基础错误处理和重试机制

## 文件清单
需要创建的文件：
- [ ] 所有目录和__init__.py文件
- [ ] requirements.txt
- [ ] .env.example
- [ ] .gitignore
- [ ] src/config/settings.py
- [ ] src/core/ai_client.py
- [ ] README.md
- [ ] 基础测试文件

## 测试方法
1. 检查项目目录结构完整性
2. 安装依赖包无报错
3. 配置文件正确加载
4. OpenRouter客户端能成功初始化
5. 基础测试通过

## 依赖关系
- **前置条件**：无
- **后续阶段**：阶段2需要使用AI客户端
- **关键输出**：可工作的OpenRouter客户端封装

## 验收标准
- ✅ 项目结构完整
- ✅ 依赖安装成功
- ✅ 环境配置正常加载
- ✅ AI客户端基础功能工作
- ✅ 基础测试通过