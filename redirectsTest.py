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
    # print("..." if len(response.text) > 1000 else "")  # Indicate if content was truncated

def follow_requests(url, max_requests=10):
    session = requests.Session()
    try:
        response = session.get(url, allow_redirects=False)
        print_request_response(response.request, response)

        request_count = 1
        while 'Location' in response.headers and request_count < max_requests:
            next_url = urljoin(response.url, response.headers['Location'])
            response = session.get(next_url, allow_redirects=False)
            print_request_response(response.request, response)
            request_count += 1

        if request_count == max_requests:
            print(f"\nReached maximum number of requests ({max_requests})")

    except TooManyRedirects:
        print("Too many redirects")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

# Usage
url = "https://www.ha.org.hk/visitor/ha_view_content.asp?Parent_ID=2001&Content_ID=257201&Lang=ENG" 
follow_requests(url)
