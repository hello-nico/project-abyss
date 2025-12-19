import subprocess
import json
import os
import sys
import time

def test_brave_mcp():
    print("🔍 Reading .mcp.json...")
    try:
        with open('.mcp.json', 'r') as f:
            config = json.load(f)
            brave_server = config['mcpServers'].get('brave-search')
            if not brave_server:
                print("❌ 'brave-search' not found in .mcp.json")
                return
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return

    # Extract command and env
    cmd = [brave_server['command']] + brave_server['args']
    env = os.environ.copy()
    env.update(brave_server.get('env', {}))

    print(f"🚀 Starting Brave MCP Server...")
    # print(f"Command: {cmd}") # Debug

    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            env=env,
            text=True,
            bufsize=1  # Line buffered
        )
    except Exception as e:
        print(f"❌ Failed to start subprocess: {e}")
        return

    def send_request(req):
        json_str = json.dumps(req)
        process.stdin.write(json_str + "\n")
        process.stdin.flush()

    def read_response(req_id):
        start_time = time.time()
        while time.time() - start_time < 10: # 10s timeout
            line = process.stdout.readline()
            if not line:
                return None
            try:
                msg = json.loads(line)
                if msg.get('id') == req_id:
                    return msg
            except json.JSONDecodeError:
                pass # Ignore non-JSON logs
        return None

    # 1. Initialize
    print("📡 Sending 'initialize'...")
    send_request({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-script", "version": "1.0"}
        }
    })

    resp = read_response(1)
    if not resp:
        print("❌ Initialize verify failed (Timeout or Error)")
        process.terminate()
        return
    
    print("✅ Initialized.")
    
    # 2. Initialized Notification
    send_request({
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    })

    # 3. List Tools
    print("📋 Requesting tool list...")
    send_request({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    })
    
    tools_resp = read_response(2)
    if not tools_resp or 'result' not in tools_resp:
        print("❌ Failed to list tools")
        process.terminate()
        return
        
    tools = tools_resp['result'].get('tools', [])
    print(f"🛠️  Available Tools: {[t['name'] for t in tools]}")
    
    search_tool = next((t for t in tools if 'search' in t['name']), None)
    
    if search_tool:
        tool_name = search_tool['name']
        print(f"🧪 Testing tool: {tool_name} with query 'SurrealDB'...")
        
        send_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": {"query": "SurrealDB features"}
            }
        })
        
        search_resp = read_response(3)
        if search_resp:
            if search_resp.get('error'):
                 print(f"❌ Tool execution error: {search_resp['error']}")
            else:
                 print("✅ Search successful! Result preview:")
                 content = search_resp['result'].get('content', [])
                 for item in content:
                     if item.get('type') == 'text':
                         print(f"---\n{item['text'][:300]}\n---")
        else:
            print("❌ Search Timeout")
    else:
        print("⚠️ No search tool found to test.")

    # Cleanup
    process.terminate()
    print("👋 Test Complete.")

if __name__ == "__main__":
    test_brave_mcp()
