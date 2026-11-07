"""Mock source adapter — returns deterministic fixture candidates."""
import hashlib
from app.adapters.base import SourceAdapter, SearchQuery, RawProfile

FIXTURE_CANDIDATES = [
    {"full_name": "Priya Sharma", "current_title": "Senior Software Engineer", "current_employer": "Infosys", "location": "Bangalore, India", "skills": ["python", "django", "postgresql", "docker", "aws"], "github": "https://github.com/priyasharma"},
    {"full_name": "Rahul Verma", "current_title": "Full Stack Developer", "current_employer": "TCS", "location": "Hyderabad, India", "skills": ["react", "node.js", "typescript", "mongodb", "redis"], "github": "https://github.com/rahulverma"},
    {"full_name": "Ananya Krishnan", "current_title": "Data Engineer", "current_employer": "Wipro", "location": "Chennai, India", "skills": ["python", "spark", "kafka", "airflow", "bigquery"], "github": "https://github.com/ananyak"},
    {"full_name": "Vikram Nair", "current_title": "DevOps Engineer", "current_employer": "HCL", "location": "Pune, India", "skills": ["kubernetes", "terraform", "ansible", "aws", "ci/cd"], "github": "https://github.com/vikramnair"},
    {"full_name": "Deepika Patel", "current_title": "Machine Learning Engineer", "current_employer": "Fractal Analytics", "location": "Mumbai, India", "skills": ["python", "tensorflow", "pytorch", "scikit-learn", "mlflow"], "github": "https://github.com/deepikapatel"},
    {"full_name": "Arjun Mehta", "current_title": "Backend Engineer", "current_employer": "Zomato", "location": "Gurgaon, India", "skills": ["golang", "grpc", "postgresql", "redis", "kafka"], "github": "https://github.com/arjunmehta"},
    {"full_name": "Sneha Iyer", "current_title": "Frontend Engineer", "current_employer": "Swiggy", "location": "Bangalore, India", "skills": ["react", "typescript", "graphql", "jest", "webpack"], "github": "https://github.com/snehaiyer"},
    {"full_name": "Karthik Subramaniam", "current_title": "Platform Engineer", "current_employer": "Razorpay", "location": "Bangalore, India", "skills": ["python", "fastapi", "kubernetes", "postgresql", "prometheus"], "github": "https://github.com/karthiks"},
    {"full_name": "Meera Joshi", "current_title": "Site Reliability Engineer", "current_employer": "PhonePe", "location": "Bangalore, India", "skills": ["linux", "kubernetes", "terraform", "monitoring", "python"], "github": "https://github.com/meeraj"},
    {"full_name": "Rohit Gupta", "current_title": "Product Engineer", "current_employer": "CRED", "location": "Bangalore, India", "skills": ["kotlin", "android", "java", "spring", "postgresql"], "github": "https://github.com/rohitg"},
    {"full_name": "Lakshmi Raghavan", "current_title": "Senior Python Developer", "current_employer": "Freshworks", "location": "Chennai, India", "skills": ["python", "fastapi", "celery", "redis", "mysql"], "github": "https://github.com/lakshmir"},
    {"full_name": "Aditya Kapoor", "current_title": "Cloud Architect", "current_employer": "Deloitte", "location": "Delhi, India", "skills": ["aws", "azure", "terraform", "docker", "python"], "github": "https://github.com/adityak"},
    {"full_name": "Pooja Nambiar", "current_title": "AI Engineer", "current_employer": "Ola", "location": "Bangalore, India", "skills": ["python", "pytorch", "computer vision", "opencv", "mlops"], "github": "https://github.com/poojan"},
    {"full_name": "Suresh Kumar", "current_title": "Principal Engineer", "current_employer": "PayTM", "location": "Noida, India", "skills": ["java", "spring boot", "microservices", "kafka", "cassandra"], "github": "https://github.com/sureshk"},
    {"full_name": "Nithya Chandran", "current_title": "Engineering Manager", "current_employer": "Meesho", "location": "Bangalore, India", "skills": ["python", "architecture", "team leadership", "agile", "aws"], "github": "https://github.com/nithyac"},
]


class MockSourceAdapter(SourceAdapter):
    """Returns deterministic fixture candidates filtered by skill overlap."""

    async def search(self, query: SearchQuery) -> list[RawProfile]:
        query_skills = {s.lower() for s in query.skills_must + query.skills_nice}
        results = []

        for f in FIXTURE_CANDIDATES:
            candidate_skills = {s.lower() for s in f["skills"]}
            overlap = query_skills & candidate_skills
            if not overlap and query_skills:
                continue

            uid = hashlib.md5(f["full_name"].encode()).hexdigest()[:8]
            results.append(RawProfile(
                adapter_name="mock",
                source_url=f["github"],
                full_name=f["full_name"],
                current_title=f["current_title"],
                current_employer=f["current_employer"],
                location=f["location"],
                skills=f["skills"],
                profile_urls={"github": f["github"]},
                raw_data={**f, "mock_id": uid, "matched_skills": list(overlap)},
            ))

        return results[:query.limit]
