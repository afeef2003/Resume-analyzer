import json
import logging
from typing import Dict, Any
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import OutputParserException

from app.models.resume_models import (
    WorkExperienceList, EducationList, ResumeInsights, 
    InterviewQuestions, GraphState
)
from app.utils.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_llm_call(func):
    """Decorator for safe LLM calls with error handling"""
    def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return func(state)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            state["error"] = f"Error in {func.__name__}: {str(e)}"
            return state
    return wrapper

@safe_llm_call
def extract_work_experience(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract work experience from resume text"""
    logger.info("Extracting work experience")
    
    llm = Config.get_llm()
    parser = PydanticOutputParser(pydantic_object=WorkExperienceList)
    
    prompt = PromptTemplate(
        template="""
Extract work experience information from the resume text below. Be precise and accurate.

Resume Text:
{resume_text}

Instructions:
- Extract company names, job titles, dates, and descriptions
- Use YYYY-MM format for dates, or "Present" for current positions
- If no work experience found, return empty list
- Be thorough but accurate

{format_instructions}
        """,
        input_variables=["resume_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    try:
        chain = prompt | llm | parser
        result = chain.invoke({"resume_text": state["raw_text"]})
        state["work_experiences"] = [exp.dict() for exp in result.work_experiences]
        state["current_node"] = "extract_work"
        logger.info(f"Extracted {len(result.work_experiences)} work experiences")
    except OutputParserException as e:
        logger.warning(f"Parser error in work experience extraction: {e}")
        state["work_experiences"] = []
    
    return state

@safe_llm_call
def extract_education(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract education information from resume text"""
    logger.info("Extracting education")
    
    llm = Config.get_llm()
    parser = PydanticOutputParser(pydantic_object=EducationList)
    
    prompt = PromptTemplate(
        template="""
Extract education information from the resume text below.

Resume Text:
{resume_text}

Instructions:
- Extract institution names, degrees, fields of study, and years
- Use 4-digit years (e.g., 2020)
- If no education found, return empty list
- Be accurate with degree types and field names

{format_instructions}
        """,
        input_variables=["resume_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    try:
        chain = prompt | llm | parser
        result = chain.invoke({"resume_text": state["raw_text"]})
        state["education"] = [edu.dict() for edu in result.education]
        state["current_node"] = "extract_education"
        logger.info(f"Extracted {len(result.education)} education entries")
    except OutputParserException as e:
        logger.warning(f"Parser error in education extraction: {e}")
        state["education"] = []
    
    return state

@safe_llm_call
def generate_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate professional resume summary"""
    logger.info("Generating summary")
    
    llm = Config.get_llm()
    
    # Format extracted data
    work_text = ""
    if state["work_experiences"]:
        work_text = "\n".join([
            f"- {exp['role']} at {exp['company']} ({exp.get('start_date', 'N/A')} to {exp.get('end_date', 'N/A')})"
            for exp in state["work_experiences"]
        ])
    
    education_text = ""
    if state["education"]:
        education_text = "\n".join([
            f"- {edu['degree']} in {edu['field']} from {edu['institution']} ({edu['start_year']}-{edu['end_year']})"
            for edu in state["education"]
        ])
    
    prompt = PromptTemplate(
        template="""
Create a professional resume summary based on the structured data below.

Work Experience:
{work_experience}

Education:
{education}

Original Resume Text (for context):
{resume_text}

Instructions:
- Write a concise, professional summary (2-3 paragraphs)
- Highlight key qualifications, skills, and achievements
- Make it compelling for recruiters
- Focus on career progression and notable accomplishments
- If data is limited, work with what's available
        """,
        input_variables=["work_experience", "education", "resume_text"]
    )
    
    result = llm.invoke(prompt.format(
        work_experience=work_text or "No work experience data extracted",
        education=education_text or "No education data extracted",
        resume_text=state["raw_text"][:1000]  # Limit context
    ))
    
    state["summary"] = result.content
    state["current_node"] = "generate_summary"
    logger.info("Summary generated successfully")
    
    return state

@safe_llm_call
def extract_insights(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key insights from resume data"""
    logger.info("Extracting insights")
    
    llm = Config.get_llm()
    parser = PydanticOutputParser(pydantic_object=ResumeInsights)
    
    prompt = PromptTemplate(
        template="""
Extract key professional insights from the resume data below.

Summary: {summary}

Work Experience: {work_experience}

Education: {education}

Instructions:
- Identify years of experience in specific areas
- Note leadership roles and team management experience
- Highlight technical skills and expertise
- Mention educational background and certifications
- Point out career progression and achievements
- Focus on quantifiable and notable aspects

{format_instructions}
        """,
        input_variables=["summary", "work_experience", "education"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    work_summary = "; ".join([f"{exp['role']} at {exp['company']}" for exp in state["work_experiences"]])
    edu_summary = "; ".join([f"{edu['degree']} in {edu['field']}" for edu in state["education"]])
    
    try:
        chain = prompt | llm | parser
        result = chain.invoke({
            "summary": state.get("summary", ""),
            "work_experience": work_summary or "No work experience",
            "education": edu_summary or "No education data"
        })
        state["insights"] = result.insights
        state["current_node"] = "extract_insights"
        logger.info(f"Extracted {len(result.insights)} insights")
    except OutputParserException as e:
        logger.warning(f"Parser error in insights extraction: {e}")
        state["insights"] = ["Unable to extract detailed insights"]
    
    return state

@safe_llm_call
def generate_questions(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate tailored interview questions"""
    logger.info("Generating interview questions")
    
    llm = Config.get_llm()
    parser = PydanticOutputParser(pydantic_object=InterviewQuestions)
    
    insights_text = "\n".join([f"- {insight}" for insight in state["insights"]])
    
    prompt = PromptTemplate(
        template="""
Generate tailored interview questions based on the resume insights below.

Resume Insights:
{insights}

Instructions:
- Create 5-7 specific, thoughtful interview questions
- Mix behavioral, technical, and situational questions
- Target the candidate's specific experience and skills
- Include questions about leadership, problem-solving, and technical expertise
- Make questions open-ended and insightful
- Avoid generic questions

{format_instructions}
        """,
        input_variables=["insights"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    try:
        chain = prompt | llm | parser
        result = chain.invoke({"insights": insights_text})
        state["questions"] = result.questions
        state["current_node"] = "generate_questions"
        logger.info(f"Generated {len(result.questions)} interview questions")
    except OutputParserException as e:
        logger.warning(f"Parser error in question generation: {e}")
        state["questions"] = ["Tell me about your professional background and key achievements."]
    
    return state

def start_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize the workflow"""
    state["current_node"] = "start"
    logger.info("Workflow started")
    return state

def end_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Finalize the workflow"""
    state["current_node"] = "end"
    logger.info("Workflow completed")
    return state