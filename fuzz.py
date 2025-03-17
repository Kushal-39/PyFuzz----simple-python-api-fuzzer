import sys
import requests

# Prompt the user to enter the URL including the http(s) protocol
URL = input("Give the url of the site, including the http(s)(NO TRAILING BACKSLASH)\n")

# Define the path to the wordlist file containing potential API routes
wordlist = "apiroutes.txt"

def loop():
    """
    Reads the wordlist and loops through each word, appending it to the base URL.
    Sends a GET request and prints the result if the response is not a 404.
    """
    try:
        # Read the wordlist from file, stripping whitespace and skipping empty lines
        with open(wordlist, "r") as file:
            words = [line.strip() for line in file if line.strip()]
    except Exception as e:
        # Print an error message if the wordlist cannot be read
        print(f"Error reading wordlist: {e}")
        return

    total = len(words)
    print(f"Total words to check: {total}")
    for count, word in enumerate(words, start=1):
        # Print current progress (current word count and total)
        print(f"[{count}/{total}] Checking: {word}")
        try:
            # Construct the full URL by appending the word to the base URL and send the request
            res = requests.get(f"{URL}/{word}")
        except requests.exceptions.RequestException as e:
            # Print an error message if the request fails and continue to the next word
            print(f"Error accessing {URL}/{word}: {e}")
            continue

        # If a 404 (Not Found) is returned, skip to the next word
        if res.status_code == 404:
            continue
        else:
            try:
                # Attempt to decode the response as JSON
                data = res.json()
            except ValueError:
                # Inform the user if the response is not in JSON format
                print("Response is not in JSON format.")
                continue

            # Print the successful response details
            print("Response data:", data)
            print("Status code:", res.status_code)
            print("Word:", word)
            
            
if __name__ == "__main__":
    try:
        # Run the main loop
        loop()
    except KeyboardInterrupt:
        # Exit gracefully upon receiving a keyboard interrupt
        print("\nExiting...")
        sys.exit(0)
    except requests.exceptions.RequestException as e:
        # Handle request-specific exceptions at the top level
        print(f"An error occurred: {e}")
        sys.exit(1)
    except EOFError:
        # Exit gracefully if an EOF error is received (e.g., Ctrl+D)
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        # Catch any other unexpected exceptions
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)