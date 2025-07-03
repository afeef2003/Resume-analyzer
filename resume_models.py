from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class WorkExperience(BaseModel):
    company: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)
    start_date: Optional[str] = Field(default=None, description="YYYY-MM format")
    end_date: Optional[str] = Field(default=None, description="YYYY-MM or Present")
    description: str = Field(..., min_length=1)
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        if v and v != "Present":
            try:
                datetime.strptime(v, "%Y-%m")
            except ValueError:
                raise ValueError("Date must be in YYYY-MM format or 'Present'")
        return v

class WorkExperienceList(BaseModel):
    work_experiences: List[WorkExperience] = Field(default_factory=list)

class Education(BaseModel):
    institution: str = Field(..., min_length=1)
    degree: str = Field(..., min_length=1)
    field: str = Field(..., min_length=1)
    start_year: int = Field(..., ge=1900, le=2030)
    end_year: int = Field(..., ge=1900, le=2030)
    
    @validator('end_year')
    def validate_end_year(cls, v, values):
        if 'start_year' in values and v < values['start_year']:
            raise ValueError("End year must be after start year")
        return v

class EducationList(BaseModel):
    education: List[Education] = Field(default_factory=list)

class ResumeInsights(BaseModel):
    insights: List[str] = Field(..., min_items=1)

class InterviewQuestions(BaseModel):
    questions: List[str] = Field(..., min_items=1)

class GraphState(BaseModel):
    """State for LangGraph workflow"""
    raw_text: str = ""
    work_experiences: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    summary: str = ""
    insights: List[str] = Field(default_factory=list)
    questions: List[str] = Field(default_factory=list)
    current_node: str = "start"
    error: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True

# API Models
class ResumeAnalysisRequest(BaseModel):
    resume_text: str = Field(..., min_length=10)

class CheckpointResumeRequest(BaseModel):
    checkpoint_id: str
    insights: Optional[List[str]] = None
    summary: Optional[str] = None

class StreamResponse(BaseModel):
    type: str  # 'summary', 'question', 'complete', 'error'
    content: str
    checkpoint_id: Optional[str] = None