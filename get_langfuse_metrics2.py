import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

def get_recent_trace_metrics():
    url = f"{LANGFUSE_HOST}/api/public/traces?limit=5"
    auth = (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY)
    
    response = requests.get(url, auth=auth)
    data = response.json()
    
    traces = data.get("data", [])
    
    for i, t in enumerate(traces):
        trace_id = t['id']
        latency = t.get('latency', 0)
        
        # Get observations (generations contain tokens)
        obs_url = f"{LANGFUSE_HOST}/api/public/observations?traceId={trace_id}"
        obs_resp = requests.get(obs_url, auth=auth)
        obs_data = obs_resp.json().get('data', [])
        
        llm_calls = 0
        tokens = 0
        
        for obs in obs_data:
            if obs.get('type') == 'GENERATION':
                llm_calls += 1
                usage = obs.get('usage')
                if usage:
                    tokens += usage.get('total', 0)
                    
        print(f"Test {i+1}: Latency={latency:.2f}s | Tokens={tokens} | LLM Calls={llm_calls}")

if __name__ == "__main__":
    get_recent_trace_metrics()
