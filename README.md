# EKP - Enterprise Knowledge Platform
# 企业级知识中台

AI 驱动的企业级知识管理与分析平台，整合多源数据，提供智能问答、知识检索、数据分析能力。

## 功能特性

- 📚 多源知识接入：支持文档、表格、数据库、API等多种数据源
- 🔍 智能检索：语义搜索、全文检索、知识图谱关联查询
- 🤖 智能问答：基于大模型的自然语言问答，支持复杂业务问题分析
- 📊 数据可视化：自动生成分析报表、可视化图表
- 🔌 可扩展架构：插件化设计，支持自定义数据源和处理流程
- 🏢 企业级特性：权限管控、审计日志、高可用部署

## 快速开始

### 安装

```bash
# 开发模式安装
pip install -e ".[dev]"
```

### 使用示例

```python
from ekp_platform import KnowledgePlatform

# 初始化知识中台
ekp = KnowledgePlatform()

# 接入数据源
ekp.add_datasource("file", path="data/")
ekp.add_datasource("database", connection_string="mysql://user:pass@host/db")

# 自然语言查询
result = ekp.query("统计Q2各部门的销售业绩，生成对比分析")
print(result)
```

## 项目结构

```
ekp-platform/
├── src/
│   └── ekp_platform/          # 主源码目录
│       ├── __init__.py
│       ├── core/             # 核心功能
│       ├── datasources/      # 数据源接入模块
│       ├── llm/              # LLM 集成与推理模块
│       ├── retrieval/        # 检索引擎模块
│       └── cli.py            # 命令行接口
├── tests/                    # 测试用例
├── docs/                     # 文档
├── examples/                 # 示例代码
└── data/                     # 示例数据
```

## 开发

```bash
# 运行测试
pytest tests/

# 代码格式化
black src/ tests/

# 类型检查
mypy src/
```

## License

MIT
