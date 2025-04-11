import sys
import requests
import urllib.parse
import logging
import time
import concurrent.futures
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Maximum number of concurrent threads
MAX_THREADS = 20

def validate_url(url):
    """
    Validates that the URL starts with http:// or https://
    Raises ValueError if invalid
    """
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")
    return url

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
            res = requests.get(endpoint, timeout=3)
            
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

def loop():
    """
    Reads the wordlist and processes endpoints in parallel using ThreadPoolExecutor
    """
    try:
        # Read the wordlist from file, stripping whitespace and skipping empty lines
        with open(wordlist, "r") as file:
            words = [line.strip() for line in file if line.strip()]
    except Exception as e:
        # Print an error message if the wordlist cannot be read
        logging.error(f"Error reading wordlist: {e}")
        return

    total = len(words)
    logging.info(f"Total words to check: {total}")
    results = []

    # Use ThreadPoolExecutor to process endpoints in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # Submit all tasks to the executor
        future_to_word = {executor.submit(check_endpoint, word, URL): word for word in words}
        
        # Use tqdm to track progress
        for future in tqdm(concurrent.futures.as_completed(future_to_word), total=len(words), desc="Scanning", unit="word"):
            word = future_to_word[future]
            try:
                result = future.result()
                if result:  # Only store non-404 responses
                    results.append(result)
            except Exception as e:
                logging.error(f"Error processing {word}: {e}")

    # Print all successful results after scanning is complete
    if results:
        logging.info(f"Found {len(results)} working endpoints")
        for endpoint, status_code, data in results:
            print(f"\n[+] Working endpoint: {endpoint}")
            print(f"    Status code: {status_code}")
            if data:
                print("    Response data:", data)
            else:
                print("    Response is not in JSON format.")
    else:
        logging.info("No working endpoints found")

try:
    # Prompt the user to enter the URL including the http(s) protocol
    URL = input("Give the url of the site, including the http(s)(NO TRAILING BACKSLASH)\n")
    URL = validate_url(URL)
except (KeyboardInterrupt, EOFError):
    print("\nExiting...")
    sys.exit(0)

# Define the path to the wordlist file containing potential API routes
wordlist = "apiroutes.txt"
            
if __name__ == "__main__":
    try:
        # Run the main loop
        loop()
    except KeyboardInterrupt:
        # Exit gracefully upon receiving a keyboard interrupt
        logging.info("\nProcess interrupted by user. Exiting...")
        sys.exit(0)
    except ValueError as e:
        # Handle URL validation errors
        logging.error(f"URL Error: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        # Handle request-specific exceptions at the top level
        logging.error(f"Request Error: {e}")
        sys.exit(1)
    except EOFError:
        # Exit gracefully if an EOF error is received (e.g., Ctrl+D)
        logging.info("\nEOF received. Exiting...")
        sys.exit(0)
    except Exception as e:
        # Log detailed context for any uncaught exceptions
        logging.exception(f"Unexpected error occurred during execution: {e}")
        sys.exit(1)