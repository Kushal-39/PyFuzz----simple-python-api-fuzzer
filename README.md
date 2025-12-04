# PyFuzz

**PyFuzz** is an intelligent API security testing tool with token handling, header mutation, and bypass testing capabilities. Designed for discovering hidden endpoints and testing authentication/authorization mechanisms.

## 🔍 Features

- **Token Handling** - Bearer tokens, API keys, and custom authorization headers
- **Header Mutation** - Automatic header fuzzing for bypass testing (X-Forwarded-For, X-Original-URL, etc.)
- **Random User-Agent** - Rotate user agents and referers to evade detection
- **HTTP Method Selection** - Support for GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS
- **Rate Limiting** - Configurable requests per second (default: 5 req/sec)
- **Path Traversal Protection** - Automatically skips unsafe wordlist entries
- **Session Logging** - UTC timestamps, session IDs, and tool/version metadata in all logs
- **Multiple Output Options** - Save results to file, quiet/verbose modes
- **Progress Tracking** - Real-time progress bar (can be disabled)
- **Smart Retry Logic** - Handles timeouts, connection errors, and 429 rate limits

---

## ⚙️ Installation & Usage

### 1. Clone the Repository

```bash
git clone https://github.com/Kushal-39/PyFuzz----simple-python-api-fuzzer
cd PyFuzz----simple-python-api-fuzzer
```

### 2. Install Dependencies

```bash
pip install requests tqdm
```

### 3. Run the Script

#### Basic Usage
```bash
python fuzz.py -u https://example.com/api
```

#### Custom HTTP Method
```bash
python fuzz.py -u https://example.com/api --method POST
```

#### With Authentication
```bash
python fuzz.py -u https://example.com/api --token YOUR_TOKEN --method POST
```

#### With Header Mutation (Bypass Testing)
```bash
python fuzz.py -u https://example.com/api --mutate-headers --random-agent -v
```

#### Advanced Usage
```bash
python fuzz.py -u https://example.com/api \
  --token YOUR_TOKEN \
  --mutate-headers \
  --random-agent \
  --method POST \
  --rate-limit 2 \
  -o results.txt
```

#### Command Line Arguments

**Basic Options:**
- `-u, --url`: Target URL (required, must include http:// or https://)
- `-w, --wordlist`: Custom wordlist file (default: apiroutes.txt)
- `--method`: HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
- `--timeout`: Request timeout in seconds (default: 3)
- `--rate-limit`: Maximum requests per second (default: 5)

**Authentication:**
- `--token`: Authorization token (automatically formatted with Bearer prefix)
- `--token-type`: Token type for Authorization header (default: Bearer)
- `--api-key`: API key for X-API-Key header

**Header Options:**
- `--header`: Custom header in format "Key: Value" (repeatable)
- `--mutate-headers`: Enable header mutation for bypass testing
- `--random-agent`: Use random User-Agent for each request
- `--user-agent`: Custom User-Agent string

**Output Options:**
- `-o, --output`: Save results to file
- `-v, --verbose`: Enable verbose output (debug logging)
- `-q, --quiet`: Quiet mode (only show results)
- `--no-progress`: Disable progress bar
- `-h, --help`: Show help message

#### Get Help
```bash
python fuzz.py --help
```

---

## 🧪 Example Output

```text
PyFuzz v1.0.0 | Session: 123e4567-e89b-12d3-a456-426614174000 | UTC: 2025-12-04T12:00:00Z
2025-12-04T12:00:00Z [PyFuzz 1.0.0] [session:123e4567...] INFO - Target URL: https://example.com/api
2025-12-04T12:00:00Z [PyFuzz 1.0.0] [session:123e4567...] INFO - Using authorization token with type: Bearer
2025-12-04T12:00:00Z [PyFuzz 1.0.0] [session:123e4567...] INFO - Header mutation enabled for bypass testing
2025-12-04T12:00:00Z [PyFuzz 1.0.0] [session:123e4567...] INFO - HTTP Method: POST
Scanning: 100%|████████████████████████| 50/50 [00:10<00:00, 5.00word/s]

[+] Working endpoint: https://example.com/api/users
    Status code: 200
    Response data: {'message': 'Success', 'users': [...]}  

[+] Working endpoint: https://example.com/api/admin
    Status code: 200
    Response data: {'admin': true}

2025-12-04T12:00:10Z [PyFuzz 1.0.0] [session:123e4567...] INFO - Found 2 working endpoints
```

---

## 🔒 Security Testing Features

**Header Mutation** enables testing for:
- IP-based access control bypass (X-Forwarded-For, X-Real-IP, X-Client-IP)
- URL rewriting vulnerabilities (X-Original-URL, X-Rewrite-URL)
- Host header injection (X-Forwarded-Host, X-Host)
- Authentication/authorization bypasses

**Token Handling** supports:
- Bearer tokens for OAuth/JWT authentication
- API key authentication
- Custom authorization schemes
- Multiple custom headers per request

---

## ⚠️ Disclaimer

This tool is intended for **educational and ethical security research only**.  
Do **not** use it on systems **without explicit permission**. Unauthorized use may violate legal and ethical guidelines.

---

## 🪪 License

This project is open-source under the **GPL 3.0 License**.