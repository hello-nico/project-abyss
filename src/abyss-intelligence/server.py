from mcp.server.fastmcp import FastMCP
from db_client import SurrealClient
import asyncio
import json

# Initialize FastMCP Server
mcp = FastMCP("abyss-intelligence")

# Initialize DB Client
# Note: We need to handle async startup/shutdown properly
db = SurrealClient()

@mcp.resource("config://surreal")
def get_db_config() -> str:
    """Return current DB configuration"""
    return json.dumps({
        "host": db.host,
        "namespace": db.namespace,
        "database": db.database
    })

# --- Tools Definition ---

@mcp.tool()
async def trace_narrative_chain(start_node: str, depth: int = 2) -> str:
    """
    Explore the knowledge graph starting from a specific node (e.g., 'company:catl').
    Useful for Analysts (L2) to find hidden connections.
    
    Args:
        start_node: The record ID to start from (e.g., 'company:catl', 'concept:solid_state_battery')
        depth: Traversal depth (default 2)
    """
    await db.connect()
    try:
        result = await db.trace_narrative_chain(start_node, depth)
        return json.dumps(result, indent=2, default=str)
    finally:
        await db.close()

@mcp.tool()
async def create_surveillance_directive(target: str, task_type: str, detailed_context: str) -> str:
    """
    Create a long-term surveillance task for the Hunter mechanism.
    Useful for Commander/Watcher to track entities.
    
    Args:
        target: The target entity (e.g., 'Elon Musk', '$TSLA')
        task_type: Type of task ('track_replies', 'monitor_sentiment', 'fetch_10k')
        detailed_context: Extra parameters in JSON string format (e.g., '{"platform": "x"}')
    """
    await db.connect()
    try:
        try:
            context_dict = json.loads(detailed_context)
        except:
            context_dict = {"raw": detailed_context}
            
        result = await db.create_directive(target, task_type, context_dict)
        return f"Directive created successfully: {json.dumps(result, default=str)}"
    finally:
        await db.close()

@mcp.tool()
async def verify_financial_claim(ticker: str, metric_name: str) -> str:
    """
    Verify a financial claim against L1 Truth (Report table).
    Useful for Auditor.
    
    Args:
        ticker: Company ticker symbol (e.g., 'TSLA')
        metric_name: The metric to check (e.g., 'cash_equivalents', 'gross_margin')
    """
    await db.connect()
    try:
        reports = await db.verify_financials(ticker, metric_name)
        if not reports or not reports[0].get('result'):
            return f"No reports found for ticker {ticker}. Hunter directive might differ."
        
        # Process logic could be added here to filter specific metric
        return json.dumps(reports, indent=2, default=str)
    finally:
        await db.close()

if __name__ == "__main__":
    mcp.run()
