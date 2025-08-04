import requests
import time
import json
import os

# Your ngrok or localtunnel URL
# IMPORTANT: Update this with your actual public URL for the /hackrx/run endpoint
WEBHOOK_URL = "https://d5a562f9ed26.ngrok-free.app/hackrx/run" 

# Your bearer token
API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN", "74b1158d301e42af454a706d7610b664511de7b16c859c882a6bbb02cc936ed8")

# Sample request payload (from the hackathon problem statement)
PAYLOAD = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=...",
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

def test_api_latency(url, token, payload, num_runs=5):
    """
    Sends multiple requests to the API and calculates the average response time.
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
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60) # Timeout after 60s
            response.raise_for_status() # Raise an exception for bad status codes
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            response_times.append(latency_ms)
            print(f"Run {i+1}: {latency_ms:.2f} ms | Status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Run {i+1}: Error - {e}")
            print("Server might not be running or URL is incorrect.")
            return None

    if response_times:
        average_latency = sum(response_times) / len(response_times)
        return average_latency
    return None

if __name__ == '__main__':
    # Make sure to start your FastAPI server and ngrok tunnel before running this script.
    # The URL should be your active ngrok/localtunnel URL.
    
    # You will need to replace the URL below
    WEBHOOK_URL = "https://d5a562f9ed26.ngrok-free.app/hackrx/run"

    # For testing, you can use the local URL, but it won't reflect network latency
    local_url = "http://localhost:8000/hackrx/run"

    print("--- Testing against LOCAL server first (no network latency) ---")
    local_avg_latency = test_api_latency(local_url, API_BEARER_TOKEN, PAYLOAD)
    if local_avg_latency is not None:
        print(f"\nAverage local response time: {local_avg_latency:.2f} ms")

    print("\n" + "="*50 + "\n")

    print("--- Testing against PUBLIC URL (includes network latency) ---")
    print("Please ensure your ngrok/localtunnel tunnel is active and the URL is correct.")
    public_avg_latency = test_api_latency(WEBHOOK_URL, API_BEARER_TOKEN, PAYLOAD)
    if public_avg_latency is not None:
        print(f"\nAverage public response time: {public_avg_latency:.2f} ms")
        print(f"\nYour target response time is <15ms. Your current average is {public_avg_latency:.2f} ms")

