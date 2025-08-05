import requests
import time
import json
import os

# --- Configuration for Testing ---

# IMPORTANT: Replace this with your actual public ngrok/localtunnel URL for the /hackrx/run endpoint.
# This URL changes every time you restart ngrok/localtunnel (unless you have a persistent domain).
WEBHOOK_URL = "https://5d0827674612.ngrok-free.app/hackrx/run" 

# Your bearer token, as specified in the HackRx problem statement.
API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN", "74b1158d301e42af454a706d7610b664511de7b16c859c882a6bbb02cc936ed8")

# Sample request payload (from the HackRx problem statement).
# The 'documents' URL is included for compatibility but is ignored by your current main.py
# which uses the local 'policy.pdf'.
PAYLOAD = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the waiting period for cataract surgery?",
        "Are the medical expenses for an organ donor covered under this policy?",
        "What is the No Claim Discount (NCD) offered in this policy?",
        "Is there a benefit for preventive health check-ups?",
        "How does the policy define a 'Hospital'?",
        "What is the extent of coverage for AYUSH treatments?",
        "Are there any sub-limits on room rent and ICU charges for Plan A?"
    ]
}

def test_api_latency(url: str, token: str, payload: dict, num_runs: int = 5) -> Optional[float]:
    """
    Sends multiple POST requests to the API endpoint and calculates the average response time.

    Args:
        url (str): The URL of the API endpoint (e.g., http://localhost:8000/hackrx/run or ngrok URL).
        token (str): The bearer token for authentication.
        payload (dict): The JSON payload to send with the request.
        num_runs (int): The number of times to send the request for averaging.

    Returns:
        Optional[float]: The average response time in milliseconds, or None if all runs failed.
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    response_times = []
    
    print(f"Testing latency for URL: {url}")
    print(f"Number of questions in payload: {len(payload['questions'])}")
    print(f"Running {num_runs} tests...")

    for i in range(num_runs):
        start_time = time.time()
        try:
            # Send the POST request with JSON payload
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=90) # Increased timeout to 90s
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            response_times.append(latency_ms)
            print(f"Run {i+1}: {latency_ms:.2f} ms | Status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Run {i+1}: Error - {e}")
            print("Please ensure your FastAPI server is running and accessible at this URL.")
            # If even one run fails, we might want to return None to indicate a problem
            # or continue and calculate average only for successful runs.
            # For hackathon, a single failure might mean a 0 score, so returning None on first error is fine.
            return None 

    if response_times:
        average_latency = sum(response_times) / len(response_times)
        return average_latency
    return None

if __name__ == '__main__':
    # --- IMPORTANT ---
    # Before running this script:
    # 1. Ensure your FastAPI server is running in a separate terminal on http://localhost:8000.
    # 2. If testing the public URL, ensure your ngrok/localtunnel tunnel is active.
    # 3. Update the WEBHOOK_URL variable above with your current public ngrok/localtunnel URL.

    # Local URL for testing your API directly on your machine (no internet latency)
    local_url = "http://localhost:8000/hackrx/run"

    print("--- Testing against LOCAL server first (no network latency) ---")
    local_avg_latency = test_api_latency(local_url, API_BEARER_TOKEN, PAYLOAD)
    if local_avg_latency is not None:
        print(f"\nAverage local response time: {local_avg_latency:.2f} ms")
    else:
        print("\nLocal server test failed. Please check your FastAPI server logs for errors.")

    print("\n" + "="*50 + "\n")

    print("--- Testing against PUBLIC URL (includes network latency) ---")
    print("Ensure your ngrok/localtunnel tunnel is active and WEBHOOK_URL is correctly set in this script.")
    public_avg_latency = test_api_latency(WEBHOOK_URL, API_BEARER_TOKEN, PAYLOAD)
    if public_avg_latency is not None:
        print(f"\nAverage public response time: {public_avg_latency:.2f} ms")
        print(f"\nYour target response time is <15ms. Your current average is {public_avg_latency:.2f} ms.")
    else:
        print("\nPublic URL test failed. Check your ngrok/localtunnel tunnel status and WEBHOOK_URL.")

