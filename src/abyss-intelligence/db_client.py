import os
import json
import asyncio
from typing import Any, Dict, List, Optional
from surrealdb import Surreal
from dotenv import load_dotenv

load_dotenv()

class SurrealClient:
    def __init__(self):
        self.host = os.getenv("SURREAL_HOST", "localhost")
        self.port = os.getenv("SURREAL_PORT", "8000")
        self.user = os.getenv("SURREAL_USER", "root")
        self.password = os.getenv("SURREAL_PASS", "root")
        self.namespace = os.getenv("SURREAL_NS", "abyss")
        self.database = os.getenv("SURREAL_DB", "core")
        self.db = Surreal(f"ws://{self.host}:{self.port}/rpc")

    async def connect(self):
        """Connect and sign in"""
        await self.db.connect()
        await self.db.signin({"user": self.user, "pass": self.password})
        await self.db.use(self.namespace, self.database)
        print(f"[SurrealDB] Connected to ns:{self.namespace} db:{self.database}")

    async def close(self):
        await self.db.close()

    async def query(self, sql: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute a raw SurrealQL query"""
        try:
            result = await self.db.query(sql, params)
            # Check for errors in result
            if isinstance(result, list):
                for res in result:
                    if isinstance(res, dict) and res.get('status') == 'ERR':
                         raise Exception(f"SurrealDB Error: {res.get('detail')}")
            return result
        except Exception as e:
            print(f"[SurrealDB] Query failed: {e}")
            raise

    # --- Tool Implementations ---

    async def trace_narrative_chain(self, start_node: str, depth: int = 2) -> Dict:
        """
        Implementation of the trace_narrative_chain tool.
        Explore the graph starting from a node.
        """
        # Note: This is a simplifed graph walk. In real scenario, we might want
        # specific edge traversals.
        # SURQL Logic: SELECT * FROM (SELECT ->involves->out FROM $start)
        
        # We'll fetch the node itself, and its direct outgoing relations
        query = f"""
        SELECT *, 
            ->involves->concept AS related_concepts,
            ->mentions->article AS related_articles,
            ->mentions->pulse AS related_pulses
        FROM {start_node};
        """
        return await self.query(query)

    async def create_directive(self, target: str, type: str, context: Dict) -> Dict:
        """
        Create a new directive in the database.
        """
        query = """
        CREATE directive CONTENT {
            target: $target,
            type: $type,
            status: 'active',
            context: $context,
            created_at: time::now()
        };
        """
        params = {"target": target, "type": type, "context": context}
        return await self.query(query, params)

    async def verify_financials(self, ticker: str, metric: str) -> Dict:
        """
        Query L1 Report data.
        """
        # Find company by ticker
        query = """
        LET $comp = (SELECT id FROM company WHERE ticker = $ticker LIMIT 1)[0];
        SELECT * FROM report WHERE company = $comp.id ORDER BY published_at DESC LIMIT 5;
        """
        params = {"ticker": ticker}
        return await self.query(query, params)
