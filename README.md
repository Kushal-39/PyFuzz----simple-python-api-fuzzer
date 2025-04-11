
# PyFuzz

**PyFuzz** is a fast, multithreaded API endpoint enumerator that helps discover hidden API routes by sending HTTP GET requests based on a wordlist.

## 🔍 Features

- Reads potential API routes from a wordlist (`apiroutes.txt`)
- Sends **GET** requests to detect valid API paths
- **Skips 404 Not Found** responses
- Attempts to parse and display **JSON responses**, with fallback for non-JSON responses
- Handles timeouts, connection errors, and rate limits with **retry logic**
- Displays real-time **progress bar** using `tqdm`
- Uses **multithreading** (`concurrent.futures`) for fast, efficient enumeration
- Clean and professional logging using Python's `logging` module

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

```bash
python fuzz.py
```

You'll be prompted to enter a **base URL** (e.g., `https://example.com/api`).  
The script will then check each word in `apiroutes.txt` for valid API responses using multithreaded scanning.

---

## 🧪 Example Output

```text
Give the url of the site, including the http(s)(NO TRAILING BACKSLASH)
> https://example.com/api
Total words to check: 50
Scanning: 100%|████████████████████████| 50/50 [00:02<00:00, 20.43word/s]

[+] Working endpoint: https://example.com/api/users
    Status code: 200
    Response data: {'message': 'Success', 'users': [...]}

[+] Working endpoint: https://example.com/api/status
    Status code: 403
    Response is not in JSON format.
```

---

## ⚠️ Disclaimer

This tool is intended for **educational and ethical security research only**.  
Do **not** use it on systems **without explicit permission**. Unauthorized use may violate legal and ethical guidelines.

---

## 🪪 License

This project is open-source under the **GPL 3.0 License**.