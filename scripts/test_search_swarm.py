import subprocess
import json
import os
import sys
import time

def run_mcp_test(server_name, config):
    print(f"\n==========================================")
    print(f"🧪 Testing Server: {server_name}")
    print(f"==========================================")

    server_conf = config['mcpServers'].get(server_name)
    if not server_conf:
        print(f"❌ Server '{server_name}' not found in config.")
        return

    if server_conf.get('type') != 'stdio':
        print(f"⚠️ Skipping '{server_name}': Test script only supports 'stdio' type (found '{server_conf.get('type')}')")
        return

    cmd = [server_conf['command']] + server_conf['args']
    env = os.environ.copy()
    env.update(server_conf.get('env', {}))

    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            env=env,
            text=True,
            bufsize=1
        )
    except Exception as e:
        print(f"❌ Failed to start process: {e}")
        return

    def send_request(req):
        json_str = json.dumps(req)
        process.stdin.write(json_str + "\n")
        process.stdin.flush()

    def read_response(req_id):
        start_time = time.time()
        while time.time() - start_time < 15: # 15s timeout
            line = process.stdout.readline()
            if not line:
                return None
            try:
                msg = json.loads(line)
                if msg.get('id') == req_id:
                    return msg
            except:
                pass
        return None

    # Initialize
    send_request({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-swarm", "version": "1.0"}
        }
    })

    if not read_response(1):
        print("❌ Initialization failed.")
        process.terminate()
        return
    
    send_request({"jsonrpc": "2.0", "method": "notifications/initialized"})
    
    # List Tools
    send_request({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    })
    
    tools_resp = read_response(2)
    if not tools_resp or 'result' not in tools_resp:
        print("❌ Failed to list tools.")
        process.terminate()
        return

    tools = tools_resp['result'].get('tools', [])
    tool_names = [t['name'] for t in tools]
    print(f"🛠️  Tools found: {tool_names}")

    # Pick a search tool
    search_tool = None
    # Heuristics for finding the main search tool
    for t in tools:
        if t['name'] == 'search': # Priority for exact match (e.g. DDG)
            search_tool = t['name']
            break
        elif 'tavily' in t['name'] and 'search' in t['name']: search_tool = t['name']
        elif 'brave' in t['name'] and 'web' in t['name']: search_tool = t['name']
    
    # Fallback
    if not search_tool and tools:
        search_tool = tools[0]['name']

    if search_tool:
        print(f"🎯 Invoking tool: '{search_tool}' with query 'Project Abyss Agent'...")
        args = {"query": "Project Abyss Agent"}
        # Tavily sometimes uses 'query', duckduckgo uses 'query', brave uses 'query' (after your fix)
        
        send_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": search_tool,
                "arguments": args
            }
        })
        
        res = read_response(3)
        if res and not res.get('error'):
            print("✅ Call Successful.")
            # Preview content
            content = res['result'].get('content', [])
            preview = str(content)[:200].replace('\n', ' ')
            print(f"📄 Result Preview: {preview}...")
        else:
            err = res.get('error') if res else "Timeout"
            print(f"❌ Call Failed: {err}")

    process.terminate()
    process.wait()

def main():
    try:
        with open('.mcp.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Could not read .mcp.json: {e}")
        return

    servers_to_test = ['brave-search', 'tavily', 'duckduckgo']
    
    for s in servers_to_test:
        run_mcp_test(s, config)
        time.sleep(1)

if __name__ == "__main__":
    main()
