import os
import requests
from dotenv import load_dotenv

load_dotenv()

LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

def get_recent_trace_metrics():
    if not LANGFUSE_PUBLIC_KEY or not LANGFUSE_SECRET_KEY:
        print("Missing Langfuse configuration.")
        return

    url = f"{LANGFUSE_HOST}/api/public/traces"
    auth = (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY)
   
    try:
        response = requests.get(url, auth=auth, params={"limit": 5})
        response.raise_for_status()
        data = response.json()
       
        traces = data.get("data", [])
        if not traces:
            print("No traces found.")
            return

        print(f"Analyzing {len(traces)} recent traces:\n")
        
        total_latency = 0
        total_tokens = 0
        
        for i, t in enumerate(traces):
            lat = t.get('latency', 0)
            tokens = t.get('totalUsage', 0)  # sometimes in totalTokens or usage
            if not tokens and 'usage' in t:
                tokens = t['usage'].get('total', 0)
                
            total_latency += lat
            total_tokens += tokens
            
            # Fetch observations (spans/generations) for this trace to count LLM calls
            obs_url = f"{LANGFUSE_HOST}/api/public/observations?traceId={t['id']}"
            obs_resp = requests.get(obs_url, auth=auth)
            obs_data = obs_resp.json().get('data', [])
            
            # Count generations (LLM calls)
            llm_calls = sum(1 for obs in obs_data if obs.get('type') == 'GENERATION')
            
            # Recalculate token usage if trace level is 0
            if tokens == 0:
                for obs in obs_data:
                    if obs.get('type') == 'GENERATION' and obs.get('usage'):
                        tokens += obs['usage'].get('totalUsage', 0) or obs['usage'].get('total', 0)
                total_tokens += tokens
            
            print(f"Trace {i+1}: Latency={lat:.2f}s | Tokens={tokens} | LLM Calls={llm_calls}")
        
        print(f"\nAverage Latency: {total_latency/len(traces):.2f}s")
        print(f"Average Tokens per Trace: {total_tokens/len(traces):.0f}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_recent_trace_metrics()
