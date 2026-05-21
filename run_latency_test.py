import time
from app.models.schemas import DisputeRequest
from app.core.agentic_workflow import app_graph
from langfuse.callback import CallbackHandler
from app.config import settings

disputes = [
    {"txn_amount": 1000, "txn_status": "failed", "merchant_type": "ecommerce", "dispute_type": "double_debit", "txn_time": "10:00", "bank": "HDFC"},
    {"txn_amount": 500, "txn_status": "pending", "merchant_type": "food_delivery", "dispute_type": "amount_deducted_not_credited", "txn_time": "12:00", "bank": "SBI"},
    {"txn_amount": 15000, "txn_status": "failed", "merchant_type": "travel", "dispute_type": "fraudulent_transaction", "txn_time": "14:00", "bank": "ICICI"},
    {"txn_amount": 200, "txn_status": "success", "merchant_type": "retail", "dispute_type": "merchant_not_provided_service", "txn_time": "16:00", "bank": "Axis"},
    {"txn_amount": 10000, "txn_status": "failed", "merchant_type": "ecommerce", "dispute_type": "refund_not_processed", "txn_time": "18:00", "bank": "Kotak"},
]

latencies = []

print("Starting latency tests for 5 disputes...")
for i, d in enumerate(disputes):
    request = DisputeRequest(**d)
    initial_state = {
        "request": request,
        "retrieved_policies": "",
        "decision": None,
        "retries": 0
    }
    
    langfuse_handler = CallbackHandler(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        host=settings.LANGFUSE_HOST
    )
    
    start_time = time.time()
    try:
        result = app_graph.invoke(initial_state, config={"callbacks": [langfuse_handler]})
        latency = time.time() - start_time
        latencies.append(latency)
        
        langfuse_handler.flush()
        decision = result.get('decision')
        decision_text = decision.decision if decision else "None"
        print(f"Test {i+1} Latency: {latency:.2f}s | Decision: {decision_text[:40]}...")
    except Exception as e:
        print(f"Test {i+1} failed: {e}")

if latencies:
    avg_latency = sum(latencies) / len(latencies)
    print(f"\nAverage E2E Latency across {len(latencies)} runs: {avg_latency:.2f}s")
