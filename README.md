# PyFuzz

**PyFuzz** is a fast API endpoint enumerator that helps discover hidden API routes by sending HTTP GET requests based on a wordlist.

## 🔍 Features

- Command line interface with comprehensive argument support
- Reads potential API routes from a customizable wordlist (default: `apiroutes.txt`)
- Sends requests with configurable HTTP method (`--method`, default: GET)
- Skips 404 Not Found responses
- Attempts to parse and display JSON responses, with fallback for non-JSON responses
- Handles timeouts, connection errors, and rate limits with retry logic
- Displays real-time progress bar using `tqdm` (can be disabled)
- Configurable rate limiting (`--rate-limit`, default: 5 req/sec)
- Prevents path traversal attempts in wordlist entries
- Logs include UTC timestamps, session identifiers, and tool/version metadata
- Save results to file option
- Multiple verbosity levels (quiet, normal, verbose)
- Graceful error handling and interruption support

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

#### Advanced Usage
```bash
python fuzz.py -u https://example.com/api -w custom_wordlist.txt --method PUT --rate-limit 2 -v -o results.txt
```

#### Command Line Arguments
- `-u, --url`: Target URL (required, must include http:// or https://)
- `-w, --wordlist`: Custom wordlist file (default: apiroutes.txt)
- `--timeout`: Request timeout in seconds (default: 3)
- `-v, --verbose`: Enable verbose output (debug level logging)
- `-q, --quiet`: Enable quiet mode (only show results)
- `-o, --output`: Output file to save results
- `--no-progress`: Disable progress bar
- `--rate-limit`: Maximum requests per second (default: 5)
- `--method`: HTTP method to use for requests (default: GET)
- `-h, --help`: Show help message and examples

#### Get Help
```bash
python fuzz.py --help
```

---

## 🧪 Example Output

```text
PyFuzz v1.0.0 | Session: 123e4567-e89b-12d3-a456-426614174000 | UTC: 2025-05-31T12:00:00Z
2025-05-31T12:00:00Z [PyFuzz 1.0.0] [session:123e4567-e89b-12d3-a456-426614174000] INFO - Target URL: https://example.com/api
2025-05-31T12:00:00Z [PyFuzz 1.0.0] [session:123e4567-e89b-12d3-a456-426614174000] INFO - Wordlist: apiroutes.txt
2025-05-31T12:00:00Z [PyFuzz 1.0.0] [session:123e4567-e89b-12d3-a456-426614174000] INFO - Timeout: 3s
2025-05-31T12:00:00Z [PyFuzz 1.0.0] [session:123e4567-e89b-12d3-a456-426614174000] INFO - HTTP Method: GET
2025-05-31T12:00:00Z [PyFuzz 1.0.0] [session:123e4567-e89b-12d3-a456-426614174000] INFO - Total words to check: 10
Scanning: 100%|████████████████████████| 10/10 [00:02<00:00, 4.00word/s]

[+] Working endpoint: https://example.com/api/users
    Status code: 200
    Response data: {'message': 'Success', 'users': [...]}  

[+] Working endpoint: https://example.com/api/status
    Status code: 403
    Response is not in JSON format.

2025-05-31T12:00:02Z [PyFuzz 1.0.0] [session:123e4567-e89b-12d3-a456-426614174000] INFO - Found 2 working endpoints
```

---

## ⚠️ Notes
- Path traversal attempts (e.g., entries with `..`, `/`, or `\`) are automatically skipped for safety.
- All logs include UTC timestamps, session IDs, and tool/version for traceability.
- Supported HTTP methods: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS.
- Default rate limit is 5 requests per second. Use `--rate-limit` to adjust.

---

## 🆕 Recent Updates

### Command Line Interface
- **Complete command line argument support** - no more interactive prompts required
- **Flexible configuration** - customize threads, timeout, wordlist, and verbosity
- **Output to file** - save results for later analysis
- **Multiple verbosity levels** - from quiet mode to debug logging
- **Progress control** - enable/disable progress bar as needed
- **Better error handling** - comprehensive validation and error messages

### Performance Improvements
- **Configurable threading** - adjust concurrent threads based on target and system capabilities
- **Customizable timeouts** - fine-tune request timeouts for optimal performance
- **Progress tracking** - optional progress bars for long-running scans

---

## ⚠️ Disclaimer

This tool is intended for **educational and ethical security research only**.  
Do **not** use it on systems **without explicit permission**. Unauthorized use may violate legal and ethical guidelines.

---

## 🪪 License

This project is open-source under the **GPL 3.0 License**.