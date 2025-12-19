
import asyncio
import sys
import os

# Add src to path so we can import abyss-intelligence components
sys.path.append(os.path.join(os.getcwd(), "src", "abyss-intelligence"))

from db_client import SurrealClient

async def test_brain():
    print("🧠 Testing Abyss Intelligence Core...")
    
    client = SurrealClient()
    try:
        print(f"🔌 Connecting to SurrealDB at {client.host}:{client.port}...")
        await client.connect()
        print("✅ Connection Successful!")
        
        # Test 1: Verify Directives Table Exists (Read)
        print("🔍 Checking 'directive' table access...")
        # Simple SELECT to verify access
        result = await client.query("SELECT * FROM directive LIMIT 1")
        print(f"✅ Query OK. Result: {result}")

        # Test 2: Simulate 'trace_narrative_chain'
        print("🕸️  Testing Graph Walker (trace_narrative_chain)...")
        # Ensure we have at least one company to trace. 
        # Create a dummy one if needed for test, then delete it?
        # Ideally we stick to reading. If DB is empty, this returns empty list, which is valid.
        try:
            res = await client.trace_narrative_chain("company:test_dummy_for_check")
            print("✅ Graph Query executed without syntax error.")
        except Exception as e:
            print(f"❌ Graph Query Failed: {e}")
            
    except Exception as e:
        print(f"❌ Connection/Test Failed: {e}")
    finally:
        await client.close()
        print("👋 Connection Closed.")

if __name__ == "__main__":
    asyncio.run(test_brain())
