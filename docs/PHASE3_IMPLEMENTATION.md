# Phase 3: Abyss Intelligence 实施计划

本文档详细描述了 Project Abyss 第三阶段（大脑构建）的实施原则与执行路线图。

## 1. 核心处理原则 (Core Doctrines)

我们在开发 Agent 系统时，严格遵循以下三大法则：

1.  **Code-First (逻辑代码化)**
    *   **原则**: 拒绝低代码 (Low-Code/No-Code) 平台的黑盒。一切业务逻辑（如财报分析算法、图谱游走路径）必须沉淀为 Python 代码，而不是仅仅存在于 Prompt 中。
    *   **实现**: 自研 `abyss-intelligence` MCP Server，将复杂逻辑封装为 Tool。

2.  **Graph-Centric (图谱思维)**
    *   **原则**: 世界是网状的。Agent 不应只看单点数据，必须具备“图谱游走”能力，发现跨实体的隐性关联。
    *   **实现**: 核心工具 `trace_narrative_chain`，支持在 SurrealDB 中进行多跳查询 (Multi-hop Query)。

3.  **Agentic Swarm (专家委员会)**
    *   **原则**: 通过“左右互搏”消除幻觉。设立不同立场的专家角色，互相验证。
    *   **实现**: 定义 `Watcher` (L3), `Analyst` (L2), `Auditor` (L1) 三种人格。

---

## 2. 生态集成策略 (Integration Strategy)

遵循 **DRY (Don't Repeat Yourself)** 原则，我们将能力分为“核心自研”与“生态集成”两部分。

### A. 生态集成 (The "Buy" List)
*直接复用成熟的 MCP Servers：*

| 能力 (Capability) | 选型 (Server) | 用途 |
| :--- | :--- | :--- |
| **实时搜索** | `brave-search` | 为 `trend_metric` 提供外部数据源；进行广泛信息检索。 |
| **网页浏览** | `puppeteer` | 连接本地 `browserless` 容器，赋予 Agent“看”网页的能力。 |
| **文件操作** | `filesystem` | 允许 Agent 自我更新文档、读取本地日志。 |

### B. 核心自研 (The "Build" List)
*仅开发 Project Abyss 独有的业务逻辑：*

*   **Server Name**: `abyss-intelligence`
*   **Location**: `src/abyss-intelligence/`
*   **Tech Stack**: Python, `mcp`, `surrealdb`

#### 关键工具定义 (Tools)
1.  **`trace_narrative_chain(start_node, depth)`**:
    *   *Role*: Analyst
    *   *Logic*: 从指定节点出发，沿 `involves`, `mentions` 边游走，返回关联的概念和实体。
2.  **`create_surveillance_directive(target, type, context)`**:
    *   *Role*: Commander / Hunter
    *   *Logic*: 向 `directive` 表写入任务，触发后台 Hunter 机制。
3.  **`verify_financial_claim(ticker, metric)`**:
    *   *Role*: Auditor
    *   *Logic*: 查询 `report` 表，核对财务事实（如 "Cash Flow"）。

---

## 3. 架构组件 (Architecture Components)

### A. The Agent Swarm (大脑)
通过 Prompt Engineering 在客户端（如 Claude Desktop）实现：
*   **Watcher (哨兵)**: 监听 L3 `pulse` 和 `trend_metric`。
*   **Analyst (分析师)**: 负责 L2 `concept` 和 `article` 的逻辑推理。
*   **Auditor (审计师)**: 负责 L1 `report` 的事实核查。
*   **Commander (指挥官)**: 综合决策。

### B. The Proactive Hunter (四肢)
*   **Directives Table**: 存储持久化任务（如“监控马斯克推特”）。
*   **Hunter Daemon**: 一个后台 Python 进程（待开发），轮询 `directive` 表，调用 `puppeteer`/`brave` 抓取数据并存入 `pulse` 表。

---

## 4. 实施路线图 (Roadmap)

- [x] **Step 1: 基础设施** (Docker: SurrealDB, Browserless, RSSHub)
- [x] **Step 2: 数据建模** (Schema: Truth-Logic-Signal 三层架构)
- [x] **Step 3.1: 核心 Brain 开发** (`abyss-intelligence` MCP Server 骨架)
- [ ] **Step 3.2: 完善 Graph Tools** (实现更复杂的 SurQL 游走逻辑)
- [ ] **Step 3.3: Hunter Daemon 开发** (实现后台爬虫逻辑)
- [ ] **Step 4: 闭环测试** (从“发现推特热点”到“生成做空报告”的全流程跑通)
