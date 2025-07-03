import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = "gpt-3.5-turbo"
    TEMPERATURE = 0.1
    MAX_TOKENS = 2000
    
    @classmethod
    def get_llm(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        return ChatOpenAI(
            model=cls.MODEL_NAME,
            temperature=cls.TEMPERATURE,
            max_tokens=cls.MAX_TOKENS,
            openai_api_key=cls.OPENAI_API_KEY
        )