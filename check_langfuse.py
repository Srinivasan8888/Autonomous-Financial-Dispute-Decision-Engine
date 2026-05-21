import os
import requests
from dotenv import load_dotenv

load_dotenv()

LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

def check_langfuse_data():
    if not LANGFUSE_PUBLIC_KEY or not LANGFUSE_SECRET_KEY:
        print("Missing Langfuse configuration.")
        return

    url = f"{LANGFUSE_HOST}/api/public/traces"
    
    auth = (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY)
    
    try:
        response = requests.get(url, auth=auth, params={"limit": 10})
        response.raise_for_status()
        data = response.json()
        
        traces = data.get("data", [])
        print(f"Total traces found (latest limit 10): {len(traces)}")
        
        if traces:
            print(f"Total count from meta: {data.get('meta', {}).get('totalItems')}")
            
            # Rough latency calc
            latencies = [t.get('latency', 0) for t in traces if t.get('latency')]
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                print(f"Average latency (last {len(latencies)} traces): {avg_latency:.2f}s")
            else:
                print("No latency data available for these traces.")
        else:
            print("No trace data found yet.")
            
    except Exception as e:
        print(f"Error connecting to Langfuse API: {e}")

if __name__ == "__main__":
    check_langfuse_data()
