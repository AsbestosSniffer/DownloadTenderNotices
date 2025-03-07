import requests
from requests.exceptions import TooManyRedirects
from urllib.parse import urljoin

def print_request_response(request, response):
    print(f"\nRequest:")
    print(f"URL: {request.url}")
    print(f"Method: {request.method}")
    print("Headers:")
    for key, value in request.headers.items():
        print(f"  {key}: {value}")

    print(f"\nResponse:")
    print(f"Status Code: {response.status_code}")
    print(f"URL: {response.url}")
    print("Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    print(f"Content Type: {response.headers.get('Content-Type', 'Not specified')}")
    print(f"Content Length: {len(response.content)} bytes")

    # Print the body of the response
    print("\nResponse Body:")
    print(response.text)  # Print first 1000 characters to avoid overwhelming output

def follow_requests(url, max_requests=10):
    session = requests.Session()
    request_count = 0

    while request_count < max_requests:
        try:
            response = session.get(url, allow_redirects=False)
            print_request_response(response.request, response)

            # Check for redirects
            if 'Location' in response.headers:
                url = urljoin(response.url, response.headers['Location'])
                request_count += 1
            else:
                break  # No more redirects

        except TooManyRedirects:
            print("Too many redirects")
            break
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            break

    if request_count == max_requests:
        print(f"\nReached maximum number of requests ({max_requests})")

# Usage
#url = "https://www.ha.org.hk/visitor/ha_visitor_index.asp?Content_ID=2001&Lang=ENG&Dimension=100" 
url = "https://www.ha.org.hk/visitor/ha_browse_act.asp?Content_ID=2001&Parent_ID=&lang=ENG&Ver=HTML"
follow_requests(url)