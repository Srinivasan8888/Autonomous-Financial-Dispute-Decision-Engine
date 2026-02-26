from pydantic import BaseModel, Field
from typing import List, Optional

class DisputeRequest(BaseModel):
    txn_amount: float = Field(..., description="The amount of the transaction in the local currency.", example=12500)
    txn_status: str = Field(..., description="The status of the transaction.", example="failed")
    merchant_type: str = Field(..., description="The category of the merchant.", example="ecommerce")
    dispute_type: str = Field(..., description="The category of the dispute raised by the user.", example="double_debit")
    txn_time: str = Field(..., description="The time the transaction occurred.", example="22:45")
    bank: str = Field(..., description="The bank associated with the transaction.", example="SBI")

class DecisionResponse(BaseModel):
    decision: str = Field(..., description="The final decision regarding the dispute (e.g., 'Auto Refund Eligible', 'Requires Manual Review', 'Merchant Liability').")
    risk_score: float = Field(..., description="A calculated risk score between 0.0 and 1.0.")
    confidence: float = Field(..., description="The confidence score of the LLM decision between 0.0 and 1.0.")
    policy_clause: str = Field(..., description="Reference to the specific RBI or NPCI guideline used to make the decision.")
    reasoning_chain: List[str] = Field(..., description="A step-by-step chain of thought explaining how the policy applies to the input transaction.")
    
class DisputeResponse(BaseModel):
    success: bool
    data: Optional[DecisionResponse] = None
    error: Optional[str] = None
