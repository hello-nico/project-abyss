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

1. **SurrealQL 建模 (Tripartite Schema):**
实施 **"Truth-Logic-Signal"** 三层架构，确保数据源的互证能力：
*   **L1 事实层 (Truth Anchors):** `report` (10-K/Q, 公告), `market_metric` (股价, SI). **作用：反驳与验真。**
*   **L2 逻辑层 (Conceptual Logic):** `concept` (宏观/赛道), `article` (长文/逻辑). **作用：连接趋势与实体。**
*   **L3 信号层 (Raw Signals):** `pulse` (高频舆情/X/Weibo), `trend_metric` (Google Trends). **作用：捕捉拐点。**
*   **核心关系:** `reflects_on` (信号->概念), `involves` (概念<->公司), `mentions` (叙事->实体).
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



###Phase 3: MCP Agent Swarm (The Brain)
*目标：构建具备“主动/被动”双重能力的专家委员会。*

1.  **Agent 组织架构 (The Committee):**
    *   **Watcher (哨兵):** 专注于 L3 信号，使用 `scan_anomalies` 工具。
    *   **Analyst (分析师):** 专注于 L2 逻辑与图谱游走，使用 `trace_narrative_chain`。
    *   **Auditor (审计师):** 专注于 L1 事实核查，使用 `verify_financials`。
    *   **Commander (指挥官):** 综合决策，并有权下达“指令”。

2.  **主动猎人机制 (Proactive Hunter):**
    *   引入 `directive` 表，存储长期监视任务（如 "Track Elon Musk's replies"）。
    *   开发 **Hunter Worker**：区别于被动 RSS，它根据指令主动调用 Browserless 执行深度抓取（Deep Dive）。
    *   **Tool**: `create_surveillance_directive(target, rules)` 让 Agent 可以主动建立长期追踪。

3.  **MCP 工具集 (Graph & Action Tools):**
    *   `graph_explore(start_node, depth)`: 在知识图谱中游走发现隐性关联。
    *   `deep_dive_search(query)`: 触发实时深度爬取，不依赖历史库存。
    *   `verify_claim(fact)`: 交叉验证 L1 数据。

###Phase 4: 自主闭环 (The Loop)
*目标：从“人找信息”变为“信息找人”，再到“人命令信息”。*

1.  **设置 Live Query 监听器:**
    编写一个后台脚本监听 SurrealDB：
    `LIVE SELECT * FROM pulse WHERE sentiment < -0.8 AND engagement.reposts > 1000` (监控恐慌爆发)。
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