# Sample resume data for testing

SAMPLE_RESUME_1 = """
John Smith
Senior Software Engineer

Contact: john.smith@example.com | (555) 123-4567 | LinkedIn: linkedin.com/in/johnsmith

WORK EXPERIENCE

Senior Software Engineer | TechCorp Inc. | 2021-01 to Present
- Led development of microservices architecture serving 10M+ users
- Managed team of 6 engineers and mentored junior developers
- Implemented CI/CD pipelines reducing deployment time by 50%
- Technologies: Python, Docker, Kubernetes, AWS

Software Engineer | StartupXYZ | 2019-03 to 2020-12
- Developed full-stack web applications using React and Node.js
- Collaborated with product team to deliver features ahead of schedule
- Optimized database queries improving performance by 30%

Junior Developer | DevStudio | 2018-06 to 2019-02
- Built responsive web interfaces using HTML, CSS, and JavaScript
- Participated in agile development processes
- Fixed bugs and implemented minor feature enhancements

EDUCATION

Bachelor of Science in Computer Science | University of Technology | 2014 to 2018
- Graduated Magna Cum Laude
- Relevant coursework: Data Structures, Algorithms, Software Engineering

SKILLS
- Programming: Python, JavaScript, Java, SQL
- Frameworks: React, Node.js, Django, Flask
- Tools: Docker, Kubernetes, AWS, Git
- Databases: PostgreSQL, MongoDB, Redis
"""

SAMPLE_RESUME_2 = """
Sarah Johnson
Marketing Manager

PROFESSIONAL EXPERIENCE

Marketing Manager | GrowthCo | 2020-06 to Present
- Developed and executed marketing strategies resulting in 40% increase in leads
- Managed marketing budget of $500K annually
- Led cross-functional team of 8 marketing professionals
- Launched successful product campaigns generating $2M in revenue

Marketing Specialist | BrandBuilders | 2018-09 to 2020-05
- Created content marketing strategies increasing website traffic by 60%
- Managed social media accounts with 100K+ followers
- Coordinated with design team for marketing collateral

Marketing Assistant | LocalBiz | 2017-01 to 2018-08
- Supported marketing campaigns and events
- Conducted market research and competitor analysis
- Managed email marketing campaigns with 25% open rate

EDUCATION

Master of Business Administration | Business School | 2015 to 2017
- Concentration in Marketing and Digital Strategy
- GPA: 3.8/4.0

Bachelor of Arts in Communications | State University | 2011 to 2015
- Minor in Psychology
- Dean's List: 4 semesters
"""

# Test cases for API endpoints
TEST_CASES = {
    "analyze_resume": {
        "valid_request": {
            "resume_text": SAMPLE_RESUME_1
        },
        "minimal_request": {
            "resume_text": "John Doe. Software Engineer with 3 years experience at Tech Company."
        },
        "invalid_request": {
            "resume_text": ""  # Too short
        }
    },
    "resume_questions": {
        "valid_request": {
            "checkpoint_id": "thread_12345678",
            "insights": [
                "5+ years of software engineering experience",
                "Led team of 6 engineers",
                "Experience with microservices and cloud technologies",
                "Strong background in Python and JavaScript"
            ],
            "summary": "Experienced software engineer with leadership skills"
        },
        "minimal_request": {
            "checkpoint_id": "thread_12345678"
        }
    }
}