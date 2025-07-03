import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from app.models.resume_models import (
    ResumeAnalysisRequest, CheckpointResumeRequest, StreamResponse
)
from app.workflow.resume_graph import (
    resume_workflow, generate_thread_id, resume_from_checkpoint
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Resume Analysis API",
    description="LangGraph-powered resume analysis with streaming and checkpointing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Resume Analysis API is running", "status": "healthy"}

@app.post("/analyze-resume")
async def analyze_resume(request: ResumeAnalysisRequest):
    """
    Analyze resume and stream summary and first question asynchronously.
    
    This endpoint:
    1. Processes the resume through the full workflow
    2. Streams the summary as it's generated
    3. Streams the first interview question when ready
    4. Returns a checkpoint ID for resumption
    """
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        thread_id = generate_thread_id()
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Initialize state
            initial_state = {
                "raw_text": request.resume_text,
                "work_experiences": [],
                "education": [],
                "summary": "",
                "insights": [],
                "questions": [],
                "current_node": "start",
                "error": None
            }
            
            logger.info(f"Starting resume analysis for thread {thread_id}")
            
            # Process through the workflow step by step
            current_state = initial_state
            
            # Run extraction nodes
            for node_name in ["start", "extract_work", "extract_education"]:
                result = resume_workflow.invoke(current_state, config)
                current_state = result
                
                if current_state.get("error"):
                    error_response = StreamResponse(
                        type="error", 
                        content=current_state["error"]
                    )
                    yield f"data: {error_response.json()}\n\n"
                    return
            
            # Generate and stream summary
            result = resume_workflow.invoke(current_state, config)
            current_state = result
            
            if current_state.get("summary"):
                # Stream summary in chunks for better UX
                summary_lines = current_state["summary"].split('. ')
                for i, line in enumerate(summary_lines):
                    if line.strip():
                        chunk = line.strip() + ('.' if i < len(summary_lines) - 1 else '')
                        summary_response = StreamResponse(
                            type="summary",
                            content=chunk
                        )
                        yield f"data: {summary_response.json()}\n\n"
                        await asyncio.sleep(0.2)  # Streaming delay
            
            # Complete insights and questions generation
            for node_name in ["extract_insights", "generate_questions"]:
                result = resume_workflow.invoke(current_state, config)
                current_state = result
            
            # Stream first question
            if current_state.get("questions") and len(current_state["questions"]) > 0:
                first_question = current_state["questions"][0]
                question_response = StreamResponse(
                    type="question",
                    content=first_question
                )
                yield f"data: {question_response.json()}\n\n"
            
            # Send completion with checkpoint ID
            complete_response = StreamResponse(
                type="complete",
                content="Analysis completed successfully",
                checkpoint_id=thread_id
            )
            yield f"data: {complete_response.json()}\n\n"
            
            logger.info(f"Resume analysis completed for thread {thread_id}")
            
        except Exception as e:
            logger.error(f"Error in resume analysis: {str(e)}")
            error_response = StreamResponse(
                type="error",
                content=f"Analysis failed: {str(e)}"
            )
            yield f"data: {error_response.json()}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

@app.post("/resume-questions")
async def resume_questions(request: CheckpointResumeRequest):
    """
    Resume workflow from checkpoint to generate interview questions.
    
    This endpoint demonstrates checkpoint resumption by starting
    directly from the question generation node.
    """
    
    try:
        logger.info(f"Resuming from checkpoint: {request.checkpoint_id}")
        
        # Resume from checkpoint
        current_state, config = resume_from_checkpoint(
            request.checkpoint_id, 
            "generate_questions"
        )
        
        # Update state with provided data if available
        if request.insights:
            current_state["insights"] = request.insights
        if request.summary:
            current_state["summary"] = request.summary
        
        # Resume workflow from question generation
        result = resume_workflow.invoke(current_state, config)
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "questions": result.get("questions", []),
            "checkpoint_id": request.checkpoint_id,
            "insights_used": result.get("insights", []),
            "status": "success"
        }
        
    except ValueError as ve:
        logger.error(f"Checkpoint error: {str(ve)}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in question generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test workflow creation
        test_state = {"raw_text": "test", "current_node": "start"}
        thread_id = generate_thread_id()
        config = {"configurable": {"thread_id": thread_id}}
        
        # Quick workflow test
        resume_workflow.invoke(test_state, config)
        
        return {
            "status": "healthy",
            "workflow": "operational",
            "checkpointing": "enabled"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )