from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.schemas import DisputeRequest, DisputeResponse, DecisionResponse
from app.core.agentic_workflow import app_graph
from app.services.audit_logger import log_dispute
# import langfuse
# from langfuse.callback import CallbackHandler

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
        
        # In a real production app with Langfuse, you'd pass the handler:
        # langfuse_handler = CallbackHandler(...)
        # config={"callbacks": [langfuse_handler]}
        
        # Execute the Agentic Workflow
        result_state = app_graph.invoke(initial_state)
        
        decision: DecisionResponse = result_state.get("decision")
        
        if not decision:
            raise ValueError("Workflow failed to generate a decision")

        # Asynchronously log this to MongoDB (Atlas M0 Free Tier)
        background_tasks.add_task(log_dispute, request.model_dump(), decision.model_dump())

        return DisputeResponse(success=True, data=decision)
        
    except Exception as e:
        return DisputeResponse(success=False, error=str(e))
