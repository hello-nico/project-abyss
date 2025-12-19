DEFINE NAMESPACE IF NOT EXISTS abyss;
USE NS abyss;
DEFINE DATABASE IF NOT EXISTS core;
USE DB core;

-- ==========================================
-- 1. L3: 信号与情绪层 (Signal & Sentiment Layer)
-- ==========================================

-- A. Pulse: 社交媒体脉冲 (X, Weibo, Reddit)
-- 区别于 Article：无标题、碎片化、高频、强调互动数据
DEFINE TABLE IF NOT EXISTS pulse SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS content ON pulse TYPE string;
DEFINE FIELD IF NOT EXISTS platform ON pulse TYPE string; -- "x", "weibo"
DEFINE FIELD IF NOT EXISTS author_handle ON pulse TYPE string; -- e.g. "@elonmusk"
DEFINE FIELD IF NOT EXISTS url ON pulse TYPE string;
-- 互动数据：核心情报。通过 UPDATE 语句不断累加。
DEFINE FIELD IF NOT EXISTS engagement ON pulse TYPE object; 
-- e.g. { likes: 500, reposts: 200, quotes: 50, views: 10000 }
DEFINE FIELD IF NOT EXISTS created_at ON pulse TYPE datetime DEFAULT time::now();
-- 情感分：-1.0 (极负) ~ 1.0 (极正)。用于计算“恐慌指数”。
DEFINE FIELD IF NOT EXISTS sentiment_score ON pulse TYPE float;
-- 向量化可选：仅对高热度 Pulse 做 Embedding，节省资源。
DEFINE FIELD IF NOT EXISTS embedding ON pulse TYPE array<float>;

DEFINE INDEX IF NOT EXISTS pulse_embedding_idx ON pulse FIELDS embedding 
  HNSW DIMENSION 1536 DIST COSINE;


-- B. TrendMetric: 非金融趋势指标 (L3 纯数值)
-- e.g. Google Search Index, GitHub Trending Rank, App Store Rank
DEFINE TABLE IF NOT EXISTS trend_metric SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS concept ON trend_metric TYPE record<concept>; -- 关联到 L2 概念
DEFINE FIELD IF NOT EXISTS source ON trend_metric TYPE string; -- "google_trends", "github"
DEFINE FIELD IF NOT EXISTS value ON trend_metric TYPE float; -- e.g. 100 (Max Heat)
DEFINE FIELD IF NOT EXISTS velocity ON trend_metric TYPE float; -- 环比变化率 (WoW, MoM)
DEFINE FIELD IF NOT EXISTS timestamp ON trend_metric TYPE datetime DEFAULT time::now();

-- C. Directive: 平行于 L3 的指令任务表 (Hunter Tasks)
DEFINE TABLE IF NOT EXISTS directive SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS target ON directive TYPE string; -- e.g. "Elon Musk"
DEFINE FIELD IF NOT EXISTS type ON directive TYPE string; -- "monitor_user", "track_keyword"
DEFINE FIELD IF NOT EXISTS status ON directive TYPE string DEFAULT "active"; -- "active", "paused", "completed"
DEFINE FIELD IF NOT EXISTS context ON directive TYPE object; -- Extra params
DEFINE FIELD IF NOT EXISTS last_run ON directive TYPE datetime;
DEFINE FIELD IF NOT EXISTS created_at ON directive TYPE datetime DEFAULT time::now();


-- ==========================================
-- 2. L2: 逻辑与叙事层 (Logic & Narrative Layer)
-- ==========================================

-- Concept (概念/赛道) - 保持不变
DEFINE TABLE IF NOT EXISTS concept SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS name ON concept TYPE string;
DEFINE FIELD IF NOT EXISTS description ON concept TYPE string;
DEFINE FIELD IF NOT EXISTS embedding ON concept TYPE array<float>;
DEFINE INDEX IF NOT EXISTS concept_name_idx ON concept FIELDS name UNIQUE;
DEFINE INDEX IF NOT EXISTS concept_embedding_idx ON concept FIELDS embedding HNSW DIMENSION 1536 DIST COSINE;

-- Article (长文/逻辑) - 修正：更纯粹的逻辑载体
DEFINE TABLE IF NOT EXISTS article SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS url ON article TYPE string ASSERT $value != NONE;
DEFINE FIELD IF NOT EXISTS title ON article TYPE string;
DEFINE FIELD IF NOT EXISTS content ON article TYPE string;
DEFINE FIELD IF NOT EXISTS source_type ON article TYPE string; -- "news", "report", "blog"
DEFINE FIELD IF NOT EXISTS reliability ON article TYPE float DEFAULT 0.5;
DEFINE FIELD IF NOT EXISTS published_at ON article TYPE datetime;
DEFINE FIELD IF NOT EXISTS created_at ON article TYPE datetime DEFAULT time::now();
DEFINE FIELD IF NOT EXISTS embedding ON article TYPE array<float>;
DEFINE INDEX IF NOT EXISTS article_embedding_idx ON article FIELDS embedding HNSW DIMENSION 1536 DIST COSINE;


-- ==========================================
-- 3. L1: 事实与实体层 (Truth & Entity Layer)
-- ==========================================
-- Company, Person, Report, MarketMetric (保持不变)

DEFINE TABLE IF NOT EXISTS company SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS name ON company TYPE string;
DEFINE FIELD IF NOT EXISTS ticker ON company TYPE string;
DEFINE FIELD IF NOT EXISTS sector ON company TYPE string;
DEFINE INDEX IF NOT EXISTS company_ticker_idx ON company FIELDS ticker UNIQUE;

DEFINE TABLE IF NOT EXISTS person SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS name ON person TYPE string;
DEFINE FIELD IF NOT EXISTS role ON person TYPE string;

DEFINE TABLE IF NOT EXISTS report SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS company ON report TYPE record<company>;
DEFINE FIELD IF NOT EXISTS period ON report TYPE string;
DEFINE FIELD IF NOT EXISTS type ON report TYPE string;
DEFINE FIELD IF NOT EXISTS metrics ON report TYPE object;
DEFINE FIELD IF NOT EXISTS url ON report TYPE string;
DEFINE FIELD IF NOT EXISTS published_at ON report TYPE datetime;

DEFINE TABLE IF NOT EXISTS market_metric SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS company ON market_metric TYPE record<company>;
DEFINE FIELD IF NOT EXISTS date ON market_metric TYPE datetime;
DEFINE FIELD IF NOT EXISTS data ON market_metric TYPE object; 


-- ==========================================
-- 4. EDGES (关系连接) - 增强 L3 关联
-- ==========================================

-- mentions (通用提及)
DEFINE TABLE IF NOT EXISTS mentions SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS in ON mentions TYPE record<article> | record<pulse>; -- 文章或脉冲
DEFINE FIELD IF NOT EXISTS out ON mentions TYPE record<company> | record<person> | record<concept>;
DEFINE FIELD IF NOT EXISTS sentiment ON mentions TYPE float;
DEFINE FIELD IF NOT EXISTS created_at ON mentions TYPE datetime DEFAULT time::now();

-- reflects_on (趋势指标 -> 概念)
-- e.g. "Google Search: AI Agent" (Trend) reflects_on "Sector: AI" (Concept)
DEFINE TABLE IF NOT EXISTS reflects_on SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS in ON reflects_on TYPE record<trend_metric>;
DEFINE FIELD IF NOT EXISTS out ON reflects_on TYPE record<concept>;
DEFINE FIELD IF NOT EXISTS weight ON reflects_on TYPE float;

-- impacts, involves (保持不变)
DEFINE TABLE IF NOT EXISTS impacts SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS in ON impacts TYPE record<article>;
DEFINE FIELD IF NOT EXISTS out ON impacts TYPE record<company>;
DEFINE FIELD IF NOT EXISTS score ON impacts TYPE float;
DEFINE FIELD IF NOT EXISTS reason ON impacts TYPE string;

DEFINE TABLE IF NOT EXISTS involves SCHEMAFULL;
DEFINE FIELD IF NOT EXISTS in ON involves TYPE record<company> | record<article>;
DEFINE FIELD IF NOT EXISTS out ON involves TYPE record<concept>;
DEFINE FIELD IF NOT EXISTS weight ON involves TYPE float;

INFO FOR DB;
