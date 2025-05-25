import sys
import argparse
import requests
import urllib.parse
import logging
import time
import concurrent.futures
from tqdm import tqdm

# Configure logging (will be updated based on verbosity level)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Default values
DEFAULT_THREADS = 10
DEFAULT_TIMEOUT = 3
DEFAULT_WORDLIST = "apiroutes.txt"

# Global variables to be set by command line arguments
MAX_THREADS = DEFAULT_THREADS
TIMEOUT = DEFAULT_TIMEOUT

def validate_url(url):
    """
    Validates that the URL starts with http:// or https://
    Raises ValueError if invalid
    """
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")
    return url

def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description="PyFuzz - A simple Python API fuzzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python fuzz.py -u https://example.com/api
  python fuzz.py -u https://example.com -w custom_wordlist.txt -t 20
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
        '-t', '--threads',
        type=int,
        default=DEFAULT_THREADS,
        help=f'Number of concurrent threads (default: {DEFAULT_THREADS})'
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
    
    return parser.parse_args()

# Worker function to check a single endpoint
def check_endpoint(word, base_url):
    """
    Check a single endpoint by appending word to base_url
    Returns None for 404 responses or on unrecoverable errors
    Returns a tuple of (endpoint, status_code, response_data) for non-404 responses
    """
    # Use urllib.parse.urljoin to ensure proper URL formation
    endpoint = urllib.parse.urljoin(base_url, word)
    
    # Retry logic for failed requests
    max_retries = 1
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            # Send the request with a timeout
            res = requests.get(endpoint, timeout=TIMEOUT)
            
            # Check for rate limiting
            if res.status_code == 429:
                logging.warning(f"Rate limit detected for {endpoint}. Consider slowing down requests.")
                time.sleep(2)  # Add a delay before retry
                retry_count += 1
                continue
                
            # If a 404 (Not Found) is returned, return None
            if res.status_code == 404:
                return None
            
            # For non-404 responses, process and return the result
            try:
                # Attempt to decode the response as JSON
                data = res.json()
                return (endpoint, res.status_code, data)
            except ValueError:
                # If not JSON, just return the status code
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
    
    return None  # Default return if we somehow exit the loop without returning

def loop(url, wordlist_path, show_progress=True):
    """
    Reads the wordlist and processes endpoints in parallel using ThreadPoolExecutor
    """
    try:
        # Read the wordlist from file, stripping whitespace and skipping empty lines
        with open(wordlist_path, "r") as file:
            words = [line.strip() for line in file if line.strip()]
    except Exception as e:
        # Print an error message if the wordlist cannot be read
        logging.error(f"Error reading wordlist: {e}")
        return []

    total = len(words)
    logging.info(f"Total words to check: {total}")
    results = []

    # Use ThreadPoolExecutor to process endpoints in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # Submit all tasks to the executor
        future_to_word = {executor.submit(check_endpoint, word, url): word for word in words}
        
        # Use tqdm to track progress if enabled
        if show_progress:
            iterator = tqdm(concurrent.futures.as_completed(future_to_word), total=len(words), desc="Scanning", unit="word")
        else:
            iterator = concurrent.futures.as_completed(future_to_word)
            
        for future in iterator:
            word = future_to_word[future]
            try:
                result = future.result()
                if result:  # Only store non-404 responses
                    results.append(result)
            except Exception as e:
                logging.error(f"Error processing {word}: {e}")

    return results

def print_results(results, output_file=None):
    """
    Print and optionally save the results
    """
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
        
        # Save to file if specified
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
    """
    Main function to handle command line arguments and run the fuzzer
    """
    global MAX_THREADS, TIMEOUT
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Configure logging based on verbosity
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set global variables from arguments
    MAX_THREADS = args.threads
    TIMEOUT = args.timeout
    
    try:
        # Validate URL
        url = validate_url(args.url)
        logging.info(f"Target URL: {url}")
        logging.info(f"Wordlist: {args.wordlist}")
        logging.info(f"Threads: {args.threads}")
        logging.info(f"Timeout: {args.timeout}s")
        
        # Run the fuzzer
        results = loop(url, args.wordlist, show_progress=not args.no_progress)
        
        # Print results
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
        # Exit gracefully upon receiving a keyboard interrupt
        logging.info("\nProcess interrupted by user. Exiting...")
        sys.exit(0)
    except EOFError:
        # Exit gracefully if an EOF error is received (e.g., Ctrl+D)
        logging.info("\nEOF received. Exiting...")
        sys.exit(0)