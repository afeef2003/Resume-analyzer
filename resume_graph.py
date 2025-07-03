import sqlite3
import uuid
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages

from app.models.resume_models import GraphState
from app.nodes.workflow_nodes import (
    start_node, extract_work_experience, extract_education,
    generate_summary, extract_insights, generate_questions, end_node
)

# Initialize SQLite checkpoint saver
def get_checkpointer():
    conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
    return SqliteSaver(conn)

def should_continue(state: Dict[str, Any]) -> Literal["extract_education", "end"]:
    """Conditional logic for workflow routing"""
    if state.get("error"):
        return "end"
    return "extract_education"

def create_resume_workflow():
    """Create and return the resume analysis workflow graph"""
    
    # Create workflow with type annotations
    workflow = StateGraph(dict)
    
    # Add all nodes
    workflow.add_node("start", start_node)
    workflow.add_node("extract_work", extract_work_experience)
    workflow.add_node("extract_education", extract_education)
    workflow.add_node("generate_summary", generate_summary)
    workflow.add_node("extract_insights", extract_insights)
    workflow.add_node("generate_questions", generate_questions)
    workflow.add_node("end", end_node)
    
    # Define the workflow edges
    workflow.add_edge("start", "extract_work")
    workflow.add_conditional_edges(
        "extract_work",
        should_continue,
        {
            "extract_education": "extract_education",
            "end": "end"
        }
    )
    workflow.add_edge("extract_education", "generate_summary")
    workflow.add_edge("generate_summary", "extract_insights")
    workflow.add_edge("extract_insights", "generate_questions")
    workflow.add_edge("generate_questions", "end")
    
    # Set entry point
    workflow.set_entry_point("start")
    
    # Compile with checkpointing
    checkpointer = get_checkpointer()
    app = workflow.compile(checkpointer=checkpointer)
    
    return app

# Global workflow instance
resume_workflow = create_resume_workflow()

def generate_thread_id() -> str:
    """Generate a unique thread ID for checkpointing"""
    return f"thread_{uuid.uuid4().hex[:8]}"

def resume_from_checkpoint(checkpoint_id: str, target_node: str = "generate_questions"):
    """Resume workflow from a specific checkpoint and node"""
    config = {"configurable": {"thread_id": checkpoint_id}}
    
    # Get the current state from checkpoint
    try:
        state_snapshot = resume_workflow.get_state(config)
        if not state_snapshot:
            raise ValueError(f"No checkpoint found for ID: {checkpoint_id}")
        
        # Update state to resume from target node
        current_state = state_snapshot.values
        current_state["current_node"] = target_node
        
        return current_state, config
    except Exception as e:
        raise ValueError(f"Failed to resume from checkpoint {checkpoint_id}: {str(e)}")