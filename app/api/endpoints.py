from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.schemas import DisputeRequest, DisputeResponse, DecisionResponse
from app.core.agentic_workflow import app_graph
from app.services.audit_logger import log_dispute
from langfuse.callback import CallbackHandler
from app.config import settings

router = APIRouter()

@router.post("/evaluate_dispute", response_model=DisputeResponse)
async def evaluate_dispute(request: DisputeRequest, background_tasks: BackgroundTasks):
    """
    Evaluates a financial dispute using an AI Agent workflow.
    Returns the decision immediately and logs the audit trail asynchronously.
    """
    try:
        # Define the initial state for the LangGraph workflow
        initial_state = {
            "request": request,
            "retrieved_policies": "",
            "decision": None,
            "retries": 0
        }
        
        # Initialize Langfuse Handler for full observability
        langfuse_handler = CallbackHandler(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST
        )
        
        # Execute the Agentic Workflow with tracing enabled
        result_state = app_graph.invoke(
            initial_state, 
            config={"callbacks": [langfuse_handler]}
        )
        
        # Capture trace ID for the audit log
        trace_id = langfuse_handler.get_trace_id()
        
        decision: DecisionResponse = result_state.get("decision")
        
        if not decision:
            raise ValueError("Workflow failed to generate a decision")

        # Asynchronously log this to MongoDB (Atlas M0 Free Tier)
        background_tasks.add_task(log_dispute, request.model_dump(), decision.model_dump(), run_id=trace_id)

        return DisputeResponse(success=True, data=decision)
        
    except Exception as e:
        return DisputeResponse(success=False, error=str(e))
