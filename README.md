# PyFuzz

PyFuzz is a simple API endpoint enumerator that helps discover hidden API routes by sending HTTP requests using a wordlist.

## Features  
- Reads potential API routes from a wordlist (`apiroutes.txt`)  
- Sends **GET** requests to detect valid API paths  
- Skips **404 Not Found** responses  
- Attempts to parse and display **JSON responses**  
- Handles errors gracefully  

## Installation & Usage  

### 1. Clone the Repository  
```bash
git clone https://github.com/Kushal-39/pyfuzz.git
cd pyfuzz
```

### 2. Install Dependencies  
Ensure you have Python installed, then install the required library:  
```bash
pip install requests
```

### 3. Run the Script  
```bash
python fuzz.py
```
You'll be prompted to enter a **base URL** (e.g., `https://example.com/api`). The script will then check each word in `apiroutes.txt` for valid API responses.  

## Example Output  
```
Give the url of the site, including the http(s)(NO TRAILING BACKSLASH)
> https://example.com/api
Total words to check: 50
[1/50] Checking: users
Response data: {"message": "Success", "users": [...]}
Status code: 200
Word: users
...
```

## Disclaimer  
This tool is intended for **educational and ethical security research only**.  
Do not use it on systems **without explicit permission**. Unauthorized use may violate legal and ethical guidelines.  

## License  
This project is open-source under the **GPL 3.0 License**.