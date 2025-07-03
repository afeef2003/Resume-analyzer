from setuptools import setup, find_packages

setup(
    name="resume-analyzer",
    version="1.0.0",
    description="LangGraph-powered resume analysis with streaming and checkpointing",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0", 
        "langgraph==0.0.62",
        "langchain==0.0.335",
        "langchain-openai==0.0.2",
        "pydantic==2.5.0",
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0",
        "aiosqlite==0.19.0",
        "requests==2.31.0"
    ],
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers", 
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
