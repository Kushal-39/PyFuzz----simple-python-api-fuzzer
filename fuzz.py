import sys
import argparse
import requests
import urllib.parse
import logging
import time
from tqdm import tqdm
import uuid
from datetime import datetime, timezone
import random
import itertools

TOOL_NAME = "PyFuzz"
TOOL_VERSION = "1.0.0"
SESSION_ID = str(uuid.uuid4())

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
    "curl/7.68.0",
    "python-requests/2.28.0",
    "PostmanRuntime/7.29.0"
]

REFERERS = [
    "https://www.google.com",
    "https://www.bing.com",
    "https://github.com",
    "https://stackoverflow.com",
    ""
]

HEADER_MUTATIONS = {
    "X-Forwarded-For": ["127.0.0.1", "localhost", "192.168.1.1", "10.0.0.1"],
    "X-Forwarded-Host": ["localhost", "example.com", "admin.local"],
    "X-Original-URL": ["/admin", "/console", "/api/internal"],
    "X-Rewrite-URL": ["/admin", "/console", "/api/internal"],
    "X-Custom-IP-Authorization": ["127.0.0.1", "localhost"],
    "X-Originating-IP": ["127.0.0.1", "localhost"],
    "X-Remote-IP": ["127.0.0.1", "localhost"],
    "X-Client-IP": ["127.0.0.1", "localhost"],
    "X-Host": ["localhost", "127.0.0.1"],
    "X-ProxyUser-Ip": ["127.0.0.1"],
    "True-Client-IP": ["127.0.0.1"],
    "Cluster-Client-IP": ["127.0.0.1"],
    "CF-Connecting-IP": ["127.0.0.1"],
    "Forwarded": ["for=127.0.0.1", "for=localhost"]
}

class ContextLogFilter(logging.Filter):
    def filter(self, record):
        # Attach UTC timestamp, session ID, tool name/version to every log record
        record.utc_timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        record.session_id = SESSION_ID
        record.tool_name = TOOL_NAME
        record.tool_version = TOOL_VERSION
        return True

logging.basicConfig(
    level=logging.INFO,
    format='%(utc_timestamp)s [%(tool_name)s %(tool_version)s] [session:%(session_id)s] %(levelname)s - %(message)s'
)
logging.getLogger().addFilter(ContextLogFilter())

DEFAULT_TIMEOUT = 3
DEFAULT_WORDLIST = "apiroutes.txt"
TIMEOUT = DEFAULT_TIMEOUT

def validate_url(url):
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")
    return url

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="PyFuzz - A simple Python API fuzzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python fuzz.py -u https://example.com/api
  python fuzz.py -u https://example.com -w custom_wordlist.txt
  python fuzz.py -u https://example.com -v --timeout 5 --output results.txt
        """
    )
    parser.add_argument(
        '-u', '--url',
        type=str,
        help='Target URL (including http:// or https://)',
        required=True
    )
    parser.add_argument(
        '-w', '--wordlist',
        type=str,
        default=DEFAULT_WORDLIST,
        help=f'Wordlist file path (default: {DEFAULT_WORDLIST})'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f'Request timeout in seconds (default: {DEFAULT_TIMEOUT})'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output (debug level logging)'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Enable quiet mode (only show results)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file to save results'
    )
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Disable progress bar'
    )
    parser.add_argument(
        '--rate-limit',
        type=float,
        default=5,
        help='Maximum requests per second (default: 5)'
    )
    parser.add_argument(
        '--method',
        type=str,
        default='GET',
        help='HTTP method to use for requests (default: GET)'
    )
    parser.add_argument(
        '--token',
        type=str,
        help='Authorization token (e.g., Bearer token)'
    )
    parser.add_argument(
        '--token-type',
        type=str,
        default='Bearer',
        help='Token type for Authorization header (default: Bearer)'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        help='API key for X-API-Key header'
    )
    parser.add_argument(
        '--header',
        type=str,
        action='append',
        help='Custom header in format "Key: Value" (can be used multiple times)'
    )
    parser.add_argument(
        '--mutate-headers',
        action='store_true',
        help='Enable header mutation for bypass testing'
    )
    parser.add_argument(
        '--random-agent',
        action='store_true',
        help='Use random User-Agent for each request'
    )
    parser.add_argument(
        '--user-agent',
        type=str,
        help='Custom User-Agent string'
    )
    return parser.parse_args()

def generate_mutated_headers(base_headers=None):
    if base_headers is None:
        base_headers = {}
    mutated = base_headers.copy()
    for header_name, values in random.sample(list(HEADER_MUTATIONS.items()), min(3, len(HEADER_MUTATIONS))):
        mutated[header_name] = random.choice(values)
    return mutated

def check_endpoint(word, base_url, method='GET', headers=None):
    endpoint = urllib.parse.urljoin(base_url, word)
    max_retries = 1
    retry_count = 0
    method = method.upper()
    allowed_methods = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'}
    if method not in allowed_methods:
        logging.error(f"Unsupported HTTP method: {method}")
        return None
    if headers is None:
        headers = {}
    while retry_count <= max_retries:
        try:
            res = requests.request(method, endpoint, headers=headers, timeout=TIMEOUT)
            if res.status_code == 429:
                logging.warning(f"Rate limit detected for {endpoint}. Consider slowing down requests.")
                time.sleep(2)
                retry_count += 1
                continue
            if res.status_code == 404:
                return None
            try:
                data = res.json()
                return (endpoint, res.status_code, data)
            except ValueError:
                return (endpoint, res.status_code, None)
        except requests.exceptions.Timeout:
            if retry_count < max_retries:
                logging.debug(f"Timeout for {endpoint}. Retrying...")
                retry_count += 1
            else:
                logging.debug(f"Timeout for {endpoint} after retry. Skipping.")
                return None
        except requests.exceptions.ConnectionError:
            if retry_count < max_retries:
                logging.debug(f"Connection error for {endpoint}. Retrying...")
                retry_count += 1
            else:
                logging.debug(f"Connection error for {endpoint} after retry. Skipping.")
                return None
        except requests.exceptions.RequestException as e:
            logging.debug(f"Request error for {endpoint}: {e}. Skipping.")
            return None
    return None

def is_safe_word(word):
    # Prevent path traversal attempts
    if '..' in word or word.startswith('/') or word.startswith('\\'):
        return False
    return True

def loop(url, wordlist_path, show_progress=True, rate_limit=0, method='GET', headers=None, mutate_headers=False, random_agent=False):
    try:
        with open(wordlist_path, "r") as file:
            words = [line.strip() for line in file if line.strip()]
    except Exception as e:
        logging.error(f"Error reading wordlist: {e}")
        return []
    total = len(words)
    logging.info(f"Total words to check: {total}")
    results = []
    iterator = words
    if show_progress:
        iterator = tqdm(words, total=total, desc="Scanning", unit="word")
    min_interval = 1.0 / rate_limit if rate_limit > 0 else 0
    for word in iterator:
        if not is_safe_word(word):
            logging.warning(f"Skipping potentially unsafe word: {word}")
            continue
        start_time = time.time()
        try:
            request_headers = headers.copy() if headers else {}
            if random_agent:
                request_headers['User-Agent'] = random.choice(USER_AGENTS)
                request_headers['Referer'] = random.choice(REFERERS)
            if mutate_headers:
                request_headers.update(generate_mutated_headers())
            result = check_endpoint(word, url, method=method, headers=request_headers)
            if result:
                results.append(result)
        except Exception as e:
            logging.error(f"Error processing {word}: {e}")
        if min_interval > 0:
            elapsed = time.time() - start_time
            sleep_time = min_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
    return results

def print_results(results, output_file=None):
    if results:
        logging.info(f"Found {len(results)} working endpoints")
        output_lines = []
        for endpoint, status_code, data in results:
            result_text = f"\n[+] Working endpoint: {endpoint}\n"
            result_text += f"    Status code: {status_code}\n"
            if data:
                result_text += f"    Response data: {data}\n"
            else:
                result_text += "    Response is not in JSON format.\n"
            print(result_text)
            output_lines.append(result_text)
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    f.writelines(output_lines)
                logging.info(f"Results saved to {output_file}")
            except Exception as e:
                logging.error(f"Error saving results to file: {e}")
    else:
        logging.info("No working endpoints found")

def main():
    global TIMEOUT
    args = parse_arguments()
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    TIMEOUT = args.timeout
    print(f"{TOOL_NAME} v{TOOL_VERSION} | Session: {SESSION_ID} | UTC: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}")
    
    headers = {}
    if args.user_agent:
        headers['User-Agent'] = args.user_agent
        logging.info(f"Using custom User-Agent")
    if args.token:
        headers['Authorization'] = f"{args.token_type} {args.token}"
        logging.info(f"Using authorization token with type: {args.token_type}")
    if args.api_key:
        headers['X-API-Key'] = args.api_key
        logging.info("Using API key authentication")
    if args.header:
        for header in args.header:
            if ':' in header:
                key, value = header.split(':', 1)
                headers[key.strip()] = value.strip()
                logging.info(f"Added custom header: {key.strip()}")
            else:
                logging.warning(f"Invalid header format (expected 'Key: Value'): {header}")
    if args.mutate_headers:
        logging.info("Header mutation enabled for bypass testing")
    if args.random_agent:
        logging.info("Random User-Agent enabled")
    
    try:
        url = validate_url(args.url)
        logging.info(f"Target URL: {url}")
        logging.info(f"Wordlist: {args.wordlist}")
        logging.info(f"Timeout: {args.timeout}s")
        logging.info(f"HTTP Method: {args.method.upper()}")
        results = loop(url, args.wordlist, show_progress=not args.no_progress, rate_limit=getattr(args, 'rate_limit', 0), method=args.method, headers=headers, mutate_headers=args.mutate_headers, random_agent=args.random_agent)
        print_results(results, args.output)
    except ValueError as e:
        logging.error(f"URL Error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        logging.error(f"Wordlist file not found: {args.wordlist}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.exception(f"Unexpected error occurred during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("\nProcess interrupted by user. Exiting...")
        sys.exit(0)
    except EOFError:
        logging.info("\nEOF received. Exiting...")
        sys.exit(0)