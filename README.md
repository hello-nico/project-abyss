# Project Abyss (代号：深渊)

**An Autonomous Intelligence System for Deep Insights**
*自主化开源情报系统*

> "从噪音中提取信号，从信号中重构逻辑，从逻辑中推导真相。"

---

## 📖 Introduction

Project Abyss 是一个专为高阶开发者设计的**自主情报分析系统**。它不仅仅是一个 RSS 阅读器或爬虫集合，而是一个具备**多层认知能力**的 Agentic Swarm（智能体集群）。

它基于 **"Truth-Logic-Signal" (事实-逻辑-信号)** 三元架构设计，利用 SurrealDB 的图数据库特性，将碎片化的互联网信息重构为可推理的知识图谱。

## 🏗 Architecture

系统遵循 **Graph-Centric** 和 **Code-First** 原则。

### The Trinity Schema (数据三元组)
1.  **L1 Truth (事实层)**: `report` (财报), `market_metric`. 用于**锚定现实**，反驳谎言。
2.  **L2 Logic (逻辑层)**: `concept` (行业/赛道), `article` (深度长文). 用于**连接实体**，构建叙事。
3.  **L3 Signal (信号层)**: `pulse` (社交脉冲), `trend_metric` (搜索热度). 用于**捕捉拐点**，发现异常。

### The Component Stack
*   **Infrastructure**: `Docker Compose` (RSSHub, Browserless, SurrealDB)
*   **Database**: `SurrealDB v2` (Graph + Vector + Realtime)
*   **Brain (Agent)**: `MCP` (Model Context Protocol) + `Claude 3.5 Sonnet`
*   **Ingestion**: `RSSHub` (被动), `Hunter Daemon` (主动/指令驱动)

## 🚀 Getting Started

### Prerequisites
*   Docker & Docker Compose
*   Python 3.10+ & `uv` package manager
*   Claude Desktop (or other MCP client)

### 1. Start Infrastructure
启动核心服务（数据库、爬虫节点、RSS源）：
```bash
docker-compose up -d
```

### 2. Initialize Database
创建 Schema 和数据表结构：
```bash
uv venv
source .venv/bin/activate
uv pip install -r scripts/requirements.txt # (如果存在) 或直接运行脚本
python scripts/setup_db.py
```

### 3. Run Intelligence Server (MCP)
启动 Python MCP Server，赋予 Claude 操作数据库的能力：
```bash
cd src/abyss-intelligence
uv run server.py
```
*注意：需要配置 Claude Desktop将此 Server 加入 `mcpServers` 配置中。*

## 🧠 Core Features

### Agentic Swarm (专家委员会)
我们预设了不同的专家人格进行“左右互搏”：
*   👹 **Watcher**: 24小时盯着 `pulse` 表，发现恐慌或狂热信号。
*   🧐 **Analyst**: 在图谱中游走，寻找“A公司下跌是否会影响B公司”的逻辑链。
*   ⚖️ **Auditor**: 不听故事，只查 `report` 表里的现金流和债务。

### Proactive Hunter (主动猎人)
系统不仅被动接收 RSS，还支持 **Directives (指令)**：
> *"@Abyss, deep dive Elon Musk on X for the last 30 days."*
Agent 会创建一条 `directive`，后台 Hunter 进程会主动调用 Browserless 进行深度数据挖掘。

## 📂 Project Structure

```
project-abyss/
├── docker-compose.yml       # 基础设施编排 (SurrealDB, RSSHub, Browserless)
├── docs/
│   ├── ARCHITECTURE.md      # 核心架构文档 (必读)
│   └── PHASE3_IMPLEMENTATION.md # Phase 3 实施细节
├── scripts/
│   ├── init_db.surql        # SurrealQL Schema定义
│   └── setup_db.py          # 数据库初始化脚本
├── src/
│   └── abyss-intelligence/  # MCP Server (Python) - 核心大脑
└── surrealdb-data/          # 数据库持久化目录
```

## 📜 License
MIT
