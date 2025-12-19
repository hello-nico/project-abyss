这是一个为你量身定制的、完整的**“代号：深渊 (Project Abyss)”自主情报系统架构文档**。

这份文档将我们之前讨论的情报学方法论、技术选型（RSSHub, SurrealDB, MCP）以及实施步骤整合成一套严密的作战蓝图。它专为具备强 Coding 能力、追求轻量化与自主权的开发者设计。

---

#Project Abyss: 自主化开源情报系统架构书##I. 核心方法论 (The Doctrine)在编写任何代码之前，必须明确情报分析的底层逻辑。本系统遵循 **OSINT 金字塔** 结构，通过多源互证（Triangulation）消除噪音。

1. **分层数据摄入 (Layered Ingestion):**
* **L1 硬数据 (Truth):** 财报 (SEC/巨潮)、交易所数据 (Short Interest, Beta)。**作用：锚定现实。**
* **L2 逻辑层 (Logic):** 深度长文 (雪球/Seeking Alpha)、电话会议实录。**作用：获取多维视角。**
* **L3 情绪与信号 (Signal):** 社交媒体 (X/Weibo)、搜索热度、GitHub Trending。**作用：捕捉拐点与异常。**


2. **处理哲学:**
* **Code-First:** 拒绝低代码平台的黑盒，一切逻辑代码化。
* **Graph-Centric:** 世界是网状的，不是表状的。使用图数据库关联实体。
* **Agentic Swarm:** 模拟“专家委员会”，通过不同的人格（Persona）进行左右互搏。



---

##II. 技术架构栈 (The Tech Stack)我们要构建的是一个 **“事件驱动的图谱增强型 Agent 网络”**。

| 组件 | 选型 | 核心理由 |
| --- | --- | --- |
| **Ingestion (摄入)** | **RSSHub** (Self-Hosted) | 万能适配器，将封闭网页转为标准数据流。 |
| **Middleware (清洗)** | **Python** + `Crawl4AI` | 胶水层，负责轮询 RSS，并做深度网页抓取 (Markdown)。 |
| **Storage (核心)** | **SurrealDB** | **四合一神器：** 数据库 + 向量库 + 图数据库 + 实时订阅。 |
| **Protocol (连接)** | **MCP** (Model Context Protocol) | 建立本地工具与 LLM 的标准化通道。 |
| **Brain (大脑)** | **Claude 3.5 Sonnet** | 目前代码与逻辑推理最强的模型，支持超长 Context。 |
| **Interface (交互)** | **CLI / Claude Code** | 极客终端，高效、直观、零干扰。 |

---

##III. 系统拓扑图 (System Topology)```mermaid
graph TD
    subgraph "External World (The Wild)"
        Web[Social Media / News / SEC]
    end

    subgraph "Ingestion Layer (Docker)"
        RSS[RSSHub Service] -->|Standardize| Web
        Browser[Browserless/Chrome] -->|Render| RSS
    end

    subgraph "Logic Layer (Python Bridge)"
        Ingestor[Feed Ingestor Script] -->|Poll| RSS
        Ingestor -->|Clean & Embed| Crawler[Crawl4AI]
    end

    subgraph "Memory Layer (SurrealDB)"
        DB[(SurrealDB)]
        Graph[Knowledge Graph]
        Vector[Vector Index]
        Live[Live Query Stream]
        
        DB --- Graph
        DB --- Vector
        DB --- Live
    end

    subgraph "Agentic Layer (MCP Swarm)"
        Master[Orchestrator Agent]
        Analyst[Persona: Financial Expert]
        Risk[Persona: Risk Manager]
        
        Master <-->|MCP Protocol| DB
        Live -->|Trigger| Master
    end

    User[You / CLI] -->|Command| Master

```

---

##IV. 实施路线图 (Implementation Roadmap)###Phase 1: 基础设施搭建 (Infrastructure)*目标：在本地跑通数据源和存储。*

1. **Docker Compose 部署:**
创建一个 `docker-compose.yml`，编排 RSSHub, Browserless 和 SurrealDB。
```yaml
services:
  rsshub:
    image: diygod/rsshub
    environment:
      PUPPETEER_WS_ENDPOINT: 'ws://browserless:3000'
  browserless:
    image: browserless/chrome
  surrealdb:
    image: surrealdb/surreal:latest
    command: start --user root --pass root file://./data.db
    ports:
      - "8000:8000"

```


2. **配置 RSS 路由:**
在 RSSHub 中测试并锁定你的 `Alpha 10` 核心源（如：SEC Filings, 微博特定关键词, 雪球大V）。

###Phase 2: 数据管道与图谱构建 (Pipeline & Schema)*目标：数据自动化流入，并建立“文章-提及-公司”的关系。*

1. **SurrealQL 建模:**
定义 `article` (存向量), `company`, `person` 节点，以及 `mentions`, `impacts` 边。
2. **编写 Python Ingestor:**
* 使用 `feedparser` 轮询 RSSHub。
* 检测到新 URL -> 调用 `Crawl4AI` 获取正文 Markdown。
* 调用 OpenAI/Claude API 获取 Embedding。
* **写入 SurrealDB:** 使用 `RELATE` 语句自动构建图谱。


```python
# 伪代码：存入并建图
await db.query("""
    LET $art = CREATE article CONTENT { ... };
    LET $comp = UPDATE company SET ...;
    RELATE $art->mentions->$comp SET sentiment = $score;
""")

```



###Phase 3: MCP Agent 开发 (The Brain)*目标：让 Claude 能“使用”你的数据库和爬虫。*

1. **创建 MCP Server:**
使用 Python SDK 创建 `intelligence-server`。
2. **定义工具 (Tools):**
* `search_knowledge_base(query: str)`: 混合搜索 SurrealDB (向量 + 图遍历)。
* `fetch_realtime_web(url: str)`: 既然你有 Crawl4AI，让 Agent 也可以主动去读它发现的新链接。
* `get_asset_price(ticker: str)`: 调用 `yfinance`。


3. **专家人格注入 (Context Injection):**
创建 `prompts/` 目录，存放 `.md` 格式的专家设定（如“空头分析师.md”），在 MCP Server 启动时加载。

###Phase 4: 自主闭环 (The Loop)*目标：从“人找信息”变为“信息找人”。*

1. **设置 Live Query 监听器:**
编写一个后台脚本监听 SurrealDB：
`LIVE SELECT * FROM article WHERE sentiment < -0.8` (监控极度负面情绪)。
2. **触发 Agent Workflow:**
监听到事件 -> 唤醒 Claude -> 注入上下文 -> 生成简报 -> 推送到你的终端或 Slack。

---

##V. 最终工作流 (The Operational Workflow)部署完成后，作为指挥官，你的日常操作如下：

**场景：做空某家电动车公司**

1. **被动触发 (Passive Trigger):**
你的 CLI 终端突然弹出一行红字：
`[ALERT] SurrealDB Detected: 微博大量出现 "刹车失灵" 关键词 (5 mins ago).`
2. **主动介入 (Active Investigation):**
你在终端输入命令（通过 Claude Code）：
> "@MarketIntel 调取过去 24 小时关于该公司的所有负面舆情，并对比其最近一次财报中的‘保修准备金’数据。让 @Financial_Forensic (财务法医) 专家分析这是否会击穿利润表。"


3. **系统执行 (System Execution):**
* **Agent** 调用 MCP 工具查询 SurrealDB (Graph RAG)，找到了微博原文和历史上的类似投诉。
* **Agent** 调用 SEC 工具查阅 10-K 表，找到 "Warranty Reserve" 数据。
* **Agent** 加载“财务法医”人格，进行逻辑推理。


4. **决策输出 (Output):**
终端输出 Markdown 报告：
> **结论：高风险。**
> 舆情显示批量质量事故，且公司保修准备金处于历史低位 (0.5% vs 行业平均 2%)。一旦召回，Q3 EPS 可能由正转负。建议：买入 Put 期权。