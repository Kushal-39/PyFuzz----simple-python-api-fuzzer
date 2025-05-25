
# PyFuzz

**PyFuzz** is a fast, multithreaded API endpoint enumerator that helps discover hidden API routes by sending HTTP GET requests based on a wordlist.

## 🔍 Features

- **Command line interface** with comprehensive argument support
- Reads potential API routes from a customizable wordlist (default: `apiroutes.txt`)
- Sends **GET** requests to detect valid API paths
- **Skips 404 Not Found** responses
- Attempts to parse and display **JSON responses**, with fallback for non-JSON responses
- Handles timeouts, connection errors, and rate limits with **retry logic**
- Displays real-time **progress bar** using `tqdm` (can be disabled)
- Uses **configurable multithreading** (`concurrent.futures`) for fast, efficient enumeration
- **Multiple verbosity levels** (quiet, normal, verbose)
- **Save results to file** option
- Clean and professional logging using Python's `logging` module
- **Graceful error handling** and interruption support

---

## ⚙️ Installation & Usage

### 1. Clone the Repository

```bash
git clone https://github.com/Kushal-39/pyfuzz.git
cd pyfuzz
```

### 2. Install Dependencies

Make sure you have Python 3 installed. Then install the required libraries:

```bash
pip install requests tqdm
```

### 3. Run the Script

#### Basic Usage (Interactive Mode)
```bash
python fuzz.py -u https://example.com/api
```

#### Command Line Options
```bash
# Basic scan with custom wordlist and thread count
python fuzz.py -u https://example.com/api -w custom_wordlist.txt -t 20

# Verbose mode with custom timeout and save results
python fuzz.py -u https://example.com -v --timeout 5 -o results.txt

# Quiet mode with no progress bar
python fuzz.py -u https://example.com -q --no-progress

# High-performance scan
python fuzz.py -u https://example.com -t 50 --timeout 2
```

#### Command Line Arguments
- `-u, --url`: Target URL (required) - must include http:// or https://
- `-w, --wordlist`: Custom wordlist file (default: apiroutes.txt)
- `-t, --threads`: Number of concurrent threads (default: 10)
- `--timeout`: Request timeout in seconds (default: 3)
- `-v, --verbose`: Enable verbose output (debug level logging)
- `-q, --quiet`: Enable quiet mode (only show results)
- `-o, --output`: Output file to save results
- `--no-progress`: Disable progress bar
- `-h, --help`: Show help message and examples

#### Get Help
```bash
python fuzz.py --help
```

---

## 🧪 Example Output

### Interactive Mode
```text
python fuzz.py -u https://httpbin.org -w test_wordlist.txt -v
2025-05-25 21:42:46,929 - INFO - Target URL: https://httpbin.org
2025-05-25 21:42:46,929 - INFO - Wordlist: test_wordlist.txt
2025-05-25 21:42:46,929 - INFO - Threads: 10
2025-05-25 21:42:46,929 - INFO - Timeout: 3s
2025-05-25 21:42:46,929 - INFO - Total words to check: 10
Scanning: 100%|████████████████████████| 10/10 [00:04<00:00, 2.08word/s]
2025-05-25 21:42:51,772 - INFO - Found 8 working endpoints

[+] Working endpoint: https://httpbin.org/get
    Status code: 200
    Response data: {'args': {}, 'headers': {...}, 'origin': '...', 'url': '...'}

[+] Working endpoint: https://httpbin.org/json
    Status code: 200
    Response data: {'slideshow': {...}}

[+] Working endpoint: https://httpbin.org/headers
    Status code: 200
    Response data: {'headers': {...}}
```

### Quiet Mode
```text
python fuzz.py -u https://httpbin.org -w test_wordlist.txt -q
[+] Working endpoint: https://httpbin.org/get
    Status code: 200
    Response data: {...}

[+] Working endpoint: https://httpbin.org/json
    Status code: 200
    Response data: {...}
```

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