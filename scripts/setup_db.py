import os
import sys
import urllib.request
import base64
import json

# Configuration
SURREAL_HOST = os.getenv("SURREAL_HOST", "localhost")
SURREAL_PORT = os.getenv("SURREAL_PORT", "8000")
SURREAL_URL = f"http://{SURREAL_HOST}:{SURREAL_PORT}/sql"
NS = "abyss"
DB = "core"
USER = "root"
PASS = "root"

def setup_db():
    # 1. Read the SURQL script
    script_path = os.path.join(os.path.dirname(__file__), 'init_db.surql')
    if not os.path.exists(script_path):
        print(f"[-] Script not found at: {script_path}")
        sys.exit(1)

    with open(script_path, 'r', encoding='utf-8') as f:
        sql_query = f.read()

    print(f"[*] Loaded schema from {script_path}")
    print(f"[*] Target: {SURREAL_URL} (NS={NS}, DB={DB})")

    # 2. Prepare Request
    auth_str = f"{USER}:{PASS}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()

    headers = {
        'Accept': 'application/json',
        #'NS': NS,  <-- REMOVED to allow script to define them
        #'DB': DB,  <-- REMOVED
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'text/plain',
    }

    # 3. Execute
    try:
        req = urllib.request.Request(
            SURREAL_URL, 
            data=sql_query.encode('utf-8'), 
            headers=headers, 
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')
            
            # 4. Parse Response
            try:
                json_resp = json.loads(response_body)
                
                # Check for errors in any of the statements
                has_error = False
                for i, result in enumerate(json_resp):
                    if result.get('status') == 'ERR':
                        print(f"[-] SQL Error (stmt {i}): {json.dumps(result)}")
                        has_error = True
                
                if not has_error:
                    print(f"[+] Schema initialized successfully! ({len(json_resp)} statements executed)")
                    print(json.dumps(json_resp[-1], indent=2)) # Show output of last statement (INFO FOR DB)
                else:
                    print("[-] Some statements failed.")
                    sys.exit(1)

            except json.JSONDecodeError:
                print(f"[-] Failed to decode JSON response: {response_body}")
                sys.exit(1)

    except urllib.error.URLError as e:
        print(f"[-] Connection failed: {e}")
        if hasattr(e, 'read'):
             print(e.read().decode())
        print("Ensure SurrealDB is running via `docker-compose up -d`")
        sys.exit(1)

if __name__ == "__main__":
    setup_db()
