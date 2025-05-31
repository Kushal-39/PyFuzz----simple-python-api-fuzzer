import sys
import argparse
import requests
import urllib.parse
import logging
import time
from tqdm import tqdm
import uuid
from datetime import datetime, timezone

TOOL_NAME = "PyFuzz"
TOOL_VERSION = "1.0.0"
SESSION_ID = str(uuid.uuid4())

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
    return parser.parse_args()

def check_endpoint(word, base_url, method='GET'):
    endpoint = urllib.parse.urljoin(base_url, word)
    max_retries = 1
    retry_count = 0
    method = method.upper()
    allowed_methods = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'}
    if method not in allowed_methods:
        logging.error(f"Unsupported HTTP method: {method}")
        return None
    while retry_count <= max_retries:
        try:
            res = requests.request(method, endpoint, timeout=TIMEOUT)
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

def loop(url, wordlist_path, show_progress=True, rate_limit=0, method='GET'):
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
            result = check_endpoint(word, url, method=method)
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
    try:
        url = validate_url(args.url)
        logging.info(f"Target URL: {url}")
        logging.info(f"Wordlist: {args.wordlist}")
        logging.info(f"Timeout: {args.timeout}s")
        logging.info(f"HTTP Method: {args.method.upper()}")
        results = loop(url, args.wordlist, show_progress=not args.no_progress, rate_limit=getattr(args, 'rate_limit', 0), method=args.method)
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