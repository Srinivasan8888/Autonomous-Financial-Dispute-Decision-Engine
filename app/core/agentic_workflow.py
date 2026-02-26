import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.models.schemas import DisputeRequest, DecisionResponse
from app.config import settings
from app.retrieval.advanced_rag import retrieve_policies

# Initialize the LLM (using Groq for speed and free tier)
# Ensure you set GROQ_API_KEY in your environment
try:
    llm = ChatGroq(
        temperature=0.1, 
        model_name="llama3-70b-8192", 
        groq_api_key=settings.GROQ_API_KEY
    )
except Exception as e:
    # Fallback to dummy if key not set during build/test
    print(f"Warning: Failed to init Groq LLM: {e}")
    llm = None

# Define the state for the LangGraph workflow
class DisputeGraphState(TypedDict):
    request: DisputeRequest
    retrieved_policies: str
    decision: DecisionResponse
    retries: int

def query_rewriter_node(state: DisputeGraphState):
    """
    Transforms the structured JSON into a natural language query for better vector retrieval.
    """
    request = state["request"]
    # Simple query formulation based on dispute type
    query = f"RBI guidelines or NPCI rules regarding {request.dispute_type} for {request.txn_status} transactions of amount {request.txn_amount}."
    
    # In a real app, an LLM could rewrite this
    
    # Retrieve rules from Pinecone/Chroma via Advanced RAG
    policies = retrieve_policies(query)
    
    return {"retrieved_policies": policies}

def evaluator_node(state: DisputeGraphState):
    """
    Evaluates the dispute against the retrieved policies and returns a structured decision.
    """
    request = state["request"]
    policies = state["retrieved_policies"]
    
    if not llm:
        # Dummy fallback if LLM fail to load
        decision = DecisionResponse(
            decision="Auto Refund Eligible (MOCK API KEY MISSING)",
            risk_score=0.1,
            confidence=0.99,
            policy_clause="Mocked-Rule-1.1",
            reasoning_chain=["Dummy API Key", "Assumed refund"]
        )
        return {"decision": decision}
        
    parser = PydanticOutputParser(pydantic_object=DecisionResponse)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a senior financial compliance officer and dispute resolution engine. "
                   "Your job is to read the user's dispute information, read the specific banking regulations (RBI/NPCI), "
                   "and calculate a precise risk score and decision.\n\n"
                   "You must format your exact output as strictly valid JSON matching following schema:\n"
                   "{format_instructions}\n\n"
                   "AVAILABLE POLICIES:\n{policies}\n"),
        ("human", "DISPUTE DATA:\n"
                  "Amount: {amount}\n"
                  "Status: {status}\n"
                  "Type: {dispute_type}\n"
                  "Time: {time}\n"
                  "Merchant: {merchant}\n"
                  "Bank: {bank}")
    ])
    
    # Combine prompt with output parsing instructions
    chain = prompt | llm | parser
    
    try:
        decision = chain.invoke({
            "format_instructions": parser.get_format_instructions(),
            "policies": policies,
            "amount": request.txn_amount,
            "status": request.txn_status,
            "dispute_type": request.dispute_type,
            "time": request.txn_time,
            "merchant": request.merchant_type,
            "bank": request.bank
        })
    except Exception as e:
        # Dummy fallback if LLM fails dynamically
        decision = DecisionResponse(
            decision=f"Failed to parse LLM: {str(e)}",
            risk_score=0.99,
            confidence=0.0,
            policy_clause="ERROR",
            reasoning_chain=["LLM Invocation Failed"]
        )
        
    return {"decision": decision}

def critic_node(state: DisputeGraphState):
    """
    Reflects on the confidence score. If confidence is too low, perhaps retry or escalate.
    """
    decision = state.get("decision")
    retries = state.get("retries", 0)
    
    if decision and decision.confidence < 0.6 and retries < 1:
        # Loop back logic (handled by edges)
        return {"retries": retries + 1}
        
    return {"retries": retries}

def route_critic(state: DisputeGraphState):
    """
    Edge logic: determine whether to loop back to the rewriter or end.
    """
    decision = state.get("decision")
    retries = state.get("retries", 0)
    
    if decision.confidence < 0.6 and retries < 1:
        return "query_rewriter" # Needs better context
    return "end"

# Build the LangGraph
workflow = StateGraph(DisputeGraphState)

workflow.add_node("query_rewriter", query_rewriter_node)
workflow.add_node("evaluator", evaluator_node)
workflow.add_node("critic", critic_node)

workflow.set_entry_point("query_rewriter")
workflow.add_edge("query_rewriter", "evaluator")
workflow.add_edge("evaluator", "critic")

workflow.add_conditional_edges(
    "critic",
    route_critic,
    {
        "query_rewriter": "query_rewriter",
        "end": END
    }
)

app_graph = workflow.compile()
