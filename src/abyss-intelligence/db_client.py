import os
import json
import base64
import httpx
from typing import Any, Dict, List, Optional
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
        self.base_url = f"http://{self.host}:{self.port}"
        self.sql_url = f"{self.base_url}/sql"
        
        # Prepare headers
        auth_str = f"{self.user}:{self.password}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        self.headers = {
            "Accept": "application/json",
            "NS": self.namespace,
            "DB": self.database,
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "text/plain",
        }
        self.client = httpx.AsyncClient(timeout=30.0)

    async def connect(self):
        # HTTP is stateless, but we'll check connection
        try:
            resp = await self.client.post(self.sql_url, content="INFO FOR DB;", headers=self.headers)
            resp.raise_for_status()
            print(f"[SurrealDB] HTTP Connected to ns:{self.namespace} db:{self.database}")
        except Exception as e:
            print(f"[SurrealDB] Connection Check Failed: {e}")
            # Don't raise here, allow retries or lazy failure
            
    async def close(self):
        await self.client.aclose()

    async def query(self, sql: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute a raw SurrealQL query"""
        # SurrealDB HTTP endpoint handles params differently (usually simpler to inline or use LET)
        # But for robustness, we will perform simple variable substitution if params are simple
        # Or just rely on string formatting from the caller for now.
        # The recommended way for HTTP is just sending the SQL string.
        # If params are needed, we can prepend `LET $key = value;` to the SQL.
        
        final_sql = sql
        if params:
            # Prepend LET statements for params
            # Note: This is a basic implementation. Complex types (objects) need JSON serialization.
            let_stmts = []
            for k, v in params.items():
                val_json = json.dumps(v, default=str)
                # SurrealQL var format
                let_stmts.append(f"LET ${k} = {val_json};")
            final_sql = "\n".join(let_stmts) + "\n" + sql

        # Explicitly set namespace/db for every request to be safe
        final_sql = f"USE NS {self.namespace} DB {self.database};\n{final_sql}"

        try:
            response = await self.client.post(self.sql_url, content=final_sql, headers=self.headers)
            response.raise_for_status()
            
            # SurrealDB returns a list of result objects, one for each statement
            json_resp = response.json()
            
            # Check for application-level errors
            if isinstance(json_resp, list):
                for res in json_resp:
                    if res.get('status') == 'ERR':
                        raise Exception(f"SurrealDBQL Error: {json.dumps(res)}")
            
            return json_resp
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
