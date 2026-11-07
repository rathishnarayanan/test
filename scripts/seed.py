"""Seed script: demo workspace, user, 3 sample JDs, 50 mock candidates.
Run: python scripts/seed.py
Requires SYNC_DATABASE_URL to be set (or uses default).
"""
import uuid
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.config import settings
from app.models.workspace import Workspace, User
from app.models.role import Role
from app.models.candidate import Candidate, PlatformCandidate
from app.database import Base

DEMO_WORKSPACE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")

SAMPLE_JDS = [
    {
        "title": "Senior Python Backend Engineer",
        "jd_text": """We are looking for a Senior Python Backend Engineer to join our platform team.

Requirements:
- 4+ years of Python development experience
- Strong knowledge of FastAPI or Django
- PostgreSQL and Redis experience
- Docker and Kubernetes familiarity
- Experience with async Python and Celery preferred

Nice to have:
- pgvector or machine learning pipeline experience
- AWS or GCP cloud experience""",
        "search_spec": {
            "titles": ["Senior Python Engineer", "Backend Engineer", "Python Developer"],
            "skills_must": ["python", "postgresql", "docker"],
            "skills_nice": ["fastapi", "redis", "kubernetes", "aws"],
            "location": "Bangalore, India",
            "exclusions": [],
        },
        "rubric": {
            "criteria": [
                {"name": "primary_skill", "weight": 0.35, "must_have": True},
                {"name": "secondary_skill", "weight": 0.15, "must_have": False},
                {"name": "experience", "weight": 0.20, "must_have": False},
                {"name": "domain", "weight": 0.10, "must_have": False},
                {"name": "location", "weight": 0.10, "must_have": False},
                {"name": "recency", "weight": 0.10, "must_have": False},
            ]
        },
    },
    {
        "title": "React Frontend Engineer",
        "jd_text": """Join our product team as a Frontend Engineer.

Requirements:
- 3+ years of React and TypeScript experience
- Strong CSS and responsive design skills
- GraphQL or REST API integration experience

Nice to have:
- Next.js experience
- Jest and Playwright testing
- Design system experience""",
        "search_spec": {
            "titles": ["Frontend Engineer", "React Developer", "UI Engineer"],
            "skills_must": ["react", "typescript", "css"],
            "skills_nice": ["next.js", "graphql", "jest", "playwright"],
            "location": None,
            "exclusions": [],
        },
        "rubric": {
            "criteria": [
                {"name": "primary_skill", "weight": 0.35, "must_have": True},
                {"name": "secondary_skill", "weight": 0.20, "must_have": False},
                {"name": "experience", "weight": 0.20, "must_have": False},
                {"name": "domain", "weight": 0.10, "must_have": False},
                {"name": "location", "weight": 0.05, "must_have": False},
                {"name": "recency", "weight": 0.10, "must_have": False},
            ]
        },
    },
    {
        "title": "Machine Learning Engineer",
        "jd_text": """We're hiring an ML Engineer to build and deploy models at scale.

Requirements:
- 3+ years of machine learning experience
- Python, PyTorch or TensorFlow
- Experience with MLOps and model deployment
- Strong statistics and linear algebra fundamentals

Nice to have:
- Experience with scikit-learn
- Kubernetes-based ML serving
- Familiarity with vector databases""",
        "search_spec": {
            "titles": ["ML Engineer", "Machine Learning Engineer", "AI Engineer"],
            "skills_must": ["python", "pytorch", "machine learning"],
            "skills_nice": ["tensorflow", "scikit-learn", "mlflow", "mlops", "kubernetes"],
            "location": None,
            "exclusions": [],
        },
        "rubric": {
            "criteria": [
                {"name": "primary_skill", "weight": 0.40, "must_have": True},
                {"name": "secondary_skill", "weight": 0.20, "must_have": False},
                {"name": "experience", "weight": 0.20, "must_have": False},
                {"name": "domain", "weight": 0.10, "must_have": False},
                {"name": "location", "weight": 0.05, "must_have": False},
                {"name": "recency", "weight": 0.05, "must_have": False},
            ]
        },
    },
]

MOCK_CANDIDATES = [
    {"name": "Priya Sharma", "title": "Senior Software Engineer", "employer": "Infosys", "location": "Bangalore, India", "skills": ["python", "django", "postgresql", "docker", "aws"]},
    {"name": "Rahul Verma", "title": "Full Stack Developer", "employer": "TCS", "location": "Hyderabad, India", "skills": ["react", "node.js", "typescript", "mongodb", "redis"]},
    {"name": "Ananya Krishnan", "title": "Data Engineer", "employer": "Wipro", "location": "Chennai, India", "skills": ["python", "spark", "kafka", "airflow", "bigquery"]},
    {"name": "Vikram Nair", "title": "DevOps Engineer", "employer": "HCL", "location": "Pune, India", "skills": ["kubernetes", "terraform", "ansible", "aws", "ci/cd"]},
    {"name": "Deepika Patel", "title": "Machine Learning Engineer", "employer": "Fractal Analytics", "location": "Mumbai, India", "skills": ["python", "tensorflow", "pytorch", "scikit-learn", "mlflow"]},
    {"name": "Arjun Mehta", "title": "Backend Engineer", "employer": "Zomato", "location": "Gurgaon, India", "skills": ["golang", "grpc", "postgresql", "redis", "kafka"]},
    {"name": "Sneha Iyer", "title": "Frontend Engineer", "employer": "Swiggy", "location": "Bangalore, India", "skills": ["react", "typescript", "graphql", "jest", "webpack"]},
    {"name": "Karthik Subramaniam", "title": "Platform Engineer", "employer": "Razorpay", "location": "Bangalore, India", "skills": ["python", "fastapi", "kubernetes", "postgresql", "prometheus"]},
    {"name": "Meera Joshi", "title": "Site Reliability Engineer", "employer": "PhonePe", "location": "Bangalore, India", "skills": ["linux", "kubernetes", "terraform", "monitoring", "python"]},
    {"name": "Rohit Gupta", "title": "Product Engineer", "employer": "CRED", "location": "Bangalore, India", "skills": ["kotlin", "android", "java", "spring", "postgresql"]},
    {"name": "Lakshmi Raghavan", "title": "Senior Python Developer", "employer": "Freshworks", "location": "Chennai, India", "skills": ["python", "fastapi", "celery", "redis", "mysql"]},
    {"name": "Aditya Kapoor", "title": "Cloud Architect", "employer": "Deloitte", "location": "Delhi, India", "skills": ["aws", "azure", "terraform", "docker", "python"]},
    {"name": "Pooja Nambiar", "title": "AI Engineer", "employer": "Ola", "location": "Bangalore, India", "skills": ["python", "pytorch", "computer vision", "opencv", "mlops"]},
    {"name": "Suresh Kumar", "title": "Principal Engineer", "employer": "PayTM", "location": "Noida, India", "skills": ["java", "spring boot", "microservices", "kafka", "cassandra"]},
    {"name": "Nithya Chandran", "title": "Engineering Manager", "employer": "Meesho", "location": "Bangalore, India", "skills": ["python", "architecture", "team leadership", "agile", "aws"]},
    {"name": "Abhishek Rao", "title": "Backend Developer", "employer": "Flipkart", "location": "Bangalore, India", "skills": ["java", "scala", "spark", "kafka", "postgresql"]},
    {"name": "Kavitha Menon", "title": "Software Engineer", "employer": "Accenture", "location": "Bangalore, India", "skills": ["python", "django", "rest api", "postgresql", "redis"]},
    {"name": "Sanjay Pillai", "title": "Senior React Developer", "employer": "Infosys", "location": "Pune, India", "skills": ["react", "redux", "typescript", "webpack", "jest"]},
    {"name": "Divya Reddy", "title": "ML Scientist", "employer": "Mu Sigma", "location": "Bangalore, India", "skills": ["python", "scikit-learn", "pandas", "numpy", "machine learning"]},
    {"name": "Ramesh Babu", "title": "Infrastructure Engineer", "employer": "Mindtree", "location": "Bangalore, India", "skills": ["aws", "kubernetes", "docker", "ansible", "terraform"]},
    {"name": "Preethi Sundaram", "title": "Python Developer", "employer": "Mphasis", "location": "Bangalore, India", "skills": ["python", "flask", "postgresql", "celery", "aws"]},
    {"name": "Girish Kumar", "title": "Senior Data Scientist", "employer": "Tiger Analytics", "location": "Chennai, India", "skills": ["python", "pytorch", "statistics", "machine learning", "sql"]},
    {"name": "Archana Nair", "title": "Full Stack Engineer", "employer": "Swiggy", "location": "Bangalore, India", "skills": ["react", "python", "fastapi", "postgresql", "docker"]},
    {"name": "Vinay Sharma", "title": "Cloud Engineer", "employer": "TCS", "location": "Hyderabad, India", "skills": ["aws", "gcp", "kubernetes", "terraform", "python"]},
    {"name": "Shweta Agarwal", "title": "Frontend Developer", "employer": "MakeMyTrip", "location": "Gurgaon, India", "skills": ["react", "typescript", "css", "graphql", "node.js"]},
    {"name": "Naveen Krishnaswamy", "title": "Platform Engineer", "employer": "Zomato", "location": "Delhi, India", "skills": ["python", "golang", "kubernetes", "redis", "postgresql"]},
    {"name": "Pavithra Sundari", "title": "AI/ML Engineer", "employer": "Amazon", "location": "Bangalore, India", "skills": ["python", "tensorflow", "sagemaker", "mlops", "aws"]},
    {"name": "Manish Jaiswal", "title": "Backend Engineer", "employer": "Nykaa", "location": "Mumbai, India", "skills": ["python", "django", "celery", "postgresql", "redis"]},
    {"name": "Hema Krishnamurthy", "title": "Data Platform Engineer", "employer": "Flipkart", "location": "Bangalore, India", "skills": ["spark", "kafka", "python", "airflow", "bigquery"]},
    {"name": "Sunil Bhatt", "title": "DevOps Lead", "employer": "Zensar", "location": "Pune, India", "skills": ["kubernetes", "docker", "jenkins", "aws", "terraform"]},
    {"name": "Riya Saxena", "title": "Software Engineer", "employer": "Microsoft", "location": "Hyderabad, India", "skills": ["python", "azure", "postgresql", "docker", "rest api"]},
    {"name": "Amruth Rao", "title": "React Native Developer", "employer": "Ola", "location": "Bangalore, India", "skills": ["react native", "react", "typescript", "redux", "javascript"]},
    {"name": "Jyothi Srinivasan", "title": "NLP Engineer", "employer": "Unacademy", "location": "Bangalore, India", "skills": ["python", "pytorch", "nlp", "transformers", "machine learning"]},
    {"name": "Vignesh Prabhu", "title": "Senior Backend Engineer", "employer": "Navi", "location": "Bangalore, India", "skills": ["python", "fastapi", "postgresql", "redis", "kafka"]},
    {"name": "Sindhu Pillai", "title": "QA Automation Engineer", "employer": "Infosys", "location": "Chennai, India", "skills": ["python", "selenium", "playwright", "pytest", "api testing"]},
    {"name": "Arun Murugan", "title": "Database Engineer", "employer": "Cognizant", "location": "Chennai, India", "skills": ["postgresql", "mysql", "redis", "mongodb", "sql"]},
    {"name": "Shalini Verma", "title": "Product Engineer", "employer": "ShareChat", "location": "Bangalore, India", "skills": ["react", "typescript", "node.js", "postgresql", "aws"]},
    {"name": "Nikhil Bose", "title": "Senior Python Engineer", "employer": "Lenskart", "location": "Delhi, India", "skills": ["python", "django", "fastapi", "postgresql", "elasticsearch"]},
    {"name": "Tanvi Sharma", "title": "ML Engineer", "employer": "Swiggy", "location": "Bangalore, India", "skills": ["python", "pytorch", "scikit-learn", "mlflow", "kubernetes"]},
    {"name": "Prashanth Murthy", "title": "Staff Engineer", "employer": "Razorpay", "location": "Bangalore, India", "skills": ["python", "golang", "postgresql", "redis", "kafka"]},
    {"name": "Kritika Jain", "title": "Frontend Engineer", "employer": "Treebo Hotels", "location": "Bangalore, India", "skills": ["react", "javascript", "css", "jest", "webpack"]},
    {"name": "Sathish Kumar", "title": "Solutions Architect", "employer": "IBM", "location": "Chennai, India", "skills": ["aws", "kubernetes", "java", "spring", "microservices"]},
    {"name": "Leena Thomas", "title": "Python Developer", "employer": "Capgemini", "location": "Pune, India", "skills": ["python", "flask", "django", "postgresql", "docker"]},
    {"name": "Mohit Khanna", "title": "Senior React Developer", "employer": "BookMyShow", "location": "Mumbai, India", "skills": ["react", "typescript", "redux", "node.js", "postgresql"]},
    {"name": "Sudha Raman", "title": "Data Scientist", "employer": "Juspay", "location": "Bangalore, India", "skills": ["python", "machine learning", "scikit-learn", "sql", "statistics"]},
    {"name": "Pranav Kulkarni", "title": "Infrastructure Lead", "employer": "ClearTax", "location": "Bangalore, India", "skills": ["aws", "kubernetes", "terraform", "python", "monitoring"]},
    {"name": "Bhavana Rao", "title": "Backend Engineer", "employer": "Urban Company", "location": "Bangalore, India", "skills": ["python", "fastapi", "postgresql", "redis", "docker"]},
    {"name": "Ramakrishnan Pillai", "title": "Principal Data Engineer", "employer": "Walmart", "location": "Bangalore, India", "skills": ["spark", "kafka", "python", "scala", "bigquery"]},
    {"name": "Poornima Nair", "title": "Full Stack Developer", "employer": "Cure.fit", "location": "Bangalore, India", "skills": ["react", "python", "django", "postgresql", "aws"]},
    {"name": "Jagadeesh Reddy", "title": "Senior DevOps Engineer", "employer": "Cloudera", "location": "Bangalore, India", "skills": ["kubernetes", "docker", "ansible", "aws", "terraform"]},
    {"name": "Vartika Singh", "title": "AI Engineer", "employer": "Siemens", "location": "Pune, India", "skills": ["python", "pytorch", "computer vision", "tensorflow", "mlops"]},
]


def seed():
    engine = create_engine(settings.sync_database_url)

    with engine.connect() as conn:
        # Check if already seeded
        result = conn.execute(text("SELECT COUNT(*) FROM workspaces WHERE id = :id"), {"id": str(DEMO_WORKSPACE_ID)})
        if result.scalar() > 0:
            print("Already seeded. Skipping.")
            return

    with Session(engine) as session:
        ws = Workspace(
            id=DEMO_WORKSPACE_ID,
            name="Demo Workspace",
            slug="demo",
            settings={"retention_days": 90, "contact_reveal_enabled": False},
        )
        session.add(ws)
        session.flush()

        user = User(
            id=DEMO_USER_ID,
            workspace_id=DEMO_WORKSPACE_ID,
            email="recruiter@demo.com",
            role="recruiter",
            password_hash="$2b$12$PLACEHOLDER_HASH",
        )
        session.add(user)
        session.flush()

        for jd in SAMPLE_JDS:
            role = Role(
                workspace_id=DEMO_WORKSPACE_ID,
                title=jd["title"],
                jd_text=jd["jd_text"],
                search_spec=jd["search_spec"],
                rubric=jd["rubric"],
                mode="manual",
                status="draft",
                created_by=DEMO_USER_ID,
            )
            session.add(role)

        for c in MOCK_CANDIDATES:
            candidate = Candidate(
                workspace_id=DEMO_WORKSPACE_ID,
                full_name=c["name"],
                current_title=c["title"],
                current_employer=c["employer"],
                location=c["location"],
                skills=c["skills"],
                profile_urls={"github": f"https://github.com/{c['name'].lower().replace(' ', '')}"},
                source_names=["mock"],
                raw_sources=[{"mock": True}],
                email_masked=f"{c['name'][0].lower()}***@example.com",
                phone_masked="+91 ****5678",
            )
            session.add(candidate)

        session.commit()
        print(f"Seeded: 1 workspace, 1 user, {len(SAMPLE_JDS)} roles, {len(MOCK_CANDIDATES)} candidates.")


if __name__ == "__main__":
    seed()
