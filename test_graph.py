import asyncio
from app.models.schemas import DisputeRequest
import json
from langfuse.callback import CallbackHandler
from app.config import settings
from app.core.agentic_workflow import app_graph

def test_graph_locally():
    print("Initializing dummy dispute request...")
    request = DisputeRequest(
        txn_amount=12500,
        txn_status="failed",
        merchant_type="ecommerce",
        dispute_type="double_debit",
        txn_time="22:45",
        bank="SBI"
    )
    
    initial_state = {
        "request": request,
        "retrieved_policies": "",
        "decision": None,
        "retries": 0
    }
    
    print("Invoking LangGraph locally with Langfuse tracing...")
    
    # Initialize Langfuse Handler
    langfuse_handler = CallbackHandler(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        host=settings.LANGFUSE_HOST
    )
    
    try:
        result = app_graph.invoke(
            initial_state, 
            config={"callbacks": [langfuse_handler]}
        )
        
        trace_id = langfuse_handler.get_trace_id()
        print(f"\nTrace generated! Trace ID: {trace_id}")
        print(f"View trace: {settings.LANGFUSE_HOST}/project/{settings.LANGFUSE_PUBLIC_KEY}/traces/{trace_id}")
        
        # Ensure all traces are sent
        langfuse_handler.flush()
        
        decision = result.get("decision")
        
        print("\n=== FINAL DECISION ===")
        print(decision.model_dump_json(indent=2))
        
    except Exception as e:
        print(f"Error during graph execution: {e}")
        
    finally:
        from app.retrieval.advanced_rag import qdrant_client
        if qdrant_client:
            qdrant_client.close()

if __name__ == "__main__":
    test_graph_locally()
