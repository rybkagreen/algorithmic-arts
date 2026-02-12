#!/usr/bin/env python3
"""
Seed data generator for ALGORITHMIC ARTS platform.

Generates:
- 100 companies
- 50 users
- Sample partnerships and other related data
"""

import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Mock data generators
COMPANIES = [
    "Acme SaaS", "Nexus Tech", "Quantum Solutions", "Vertex Analytics", "Orion Systems",
    "Aurora Data", "Pioneer Cloud", "Stellar AI", "Horizon Platforms", "Eclipse Software",
    "Nova Technologies", "Zenith Innovations", "Apex Digital", "Crest Solutions", "Summit Labs",
    "Vista Systems", "Ridge Technologies", "Peak Analytics", "Terra Platforms", "Ocean SaaS",
]

INDUSTRIES = [
    "Fintech", "Healthtech", "Edtech", "Martech", "HRtech", "Proptech", "Logistics", 
    "Retail", "Manufacturing", "Energy", "Telecom", "Government", "Media", "Travel", "Real Estate"
]

SUB_INDUSTRY_MAP = {
    "Fintech": ["Payments", "Lending", "Wealth Management", "Insurtech", "Regtech"],
    "Healthtech": ["Telemedicine", "Digital Health", "Medical Imaging", "Pharma", "Biotech"],
    "Edtech": ["K-12", "Higher Education", "Corporate Training", "Language Learning", "Skills Development"],
    "Martech": ["CRM", "Analytics", "Advertising", "Content Marketing", "Email Marketing"],
    "HRtech": ["Recruiting", "Payroll", "Performance Management", "Learning & Development", "Employee Engagement"]
}

BUSINESS_MODELS = ["SaaS", "PaaS", "IaaS", "Marketplace", "Freemium", "Subscription", "Transaction Fee"]

TECH_STACKS = [
    ["Python", "PostgreSQL", "Redis", "React", "Docker"],
    ["Node.js", "MongoDB", "Elasticsearch", "Vue.js", "Kubernetes"],
    ["Java", "MySQL", "Kafka", "Angular", "AWS"],
    ["Go", "PostgreSQL", "Redis", "React", "GCP"],
    ["Rust", "ClickHouse", "Redis", "Svelte", "Azure"]
]

INTEGRATIONS = ["Slack", "Microsoft Teams", "Google Workspace", "Salesforce", "HubSpot", "Jira", "GitHub", "GitLab"]

AI_TAGS = ["AI-powered", "Machine Learning", "Natural Language Processing", "Computer Vision", "Predictive Analytics"]

def generate_random_string(length: int) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_email(name: str) -> str:
    domains = ["gmail.com", "yahoo.com", "outlook.com", "mail.ru", "yandex.ru"]
    return f"{name.lower().replace(' ', '.')}@{random.choice(domains)}"

def generate_company_data(count: int = 100) -> List[Dict[str, Any]]:
    companies = []
    
    for i in range(count):
        name = random.choice(COMPANIES)
        if i > 0:
            name += f" {i}"
        
        industry = random.choice(INDUSTRIES)
        sub_industries = random.sample(SUB_INDUSTRY_MAP.get(industry, []), k=random.randint(1, 3))
        
        company = {
            "id": str(uuid.uuid4()),
            "name": name,
            "slug": name.lower().replace(" ", "-"),
            "description": f"Leading {industry} solution provider specializing in {', '.join(sub_industries)}.",
            "website": f"https://www.{name.lower().replace(' ', '-')}.com",
            "logo_url": f"https://example.com/logos/{name.lower().replace(' ', '-')}.png",
            "industry": industry,
            "sub_industries": sub_industries,
            "business_model": random.choice(BUSINESS_MODELS),
            "founded_year": random.randint(2010, 2025),
            "headquarters_country": "Russia",
            "headquarters_city": random.choice(["Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Kazan"]),
            "employees_count": random.randint(10, 5000),
            "employees_range": random.choice(["1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"]),
            "funding_total": round(random.uniform(0, 50000000), 2),
            "funding_stage": random.choice(["Pre-seed", "Seed", "Series A", "Series B", "Series C", "Late Stage"]),
            "last_funding_date": (datetime.now() - timedelta(days=random.randint(1, 730))).date(),
            "inn": "".join(random.choices(string.digits, k=12)),
            "ogrn": "".join(random.choices(string.digits, k=13)),
            "kpp": "".join(random.choices(string.digits, k=9)),
            "legal_name": f"{name} LLC",
            "tech_stack": random.choice(TECH_STACKS),
            "integrations": random.sample(INTEGRATIONS, k=random.randint(1, 4)),
            "api_available": random.choice([True, False]),
            "ai_summary": "AI-powered platform for business intelligence and analytics.",
            "ai_tags": random.sample(AI_TAGS, k=random.randint(1, 3)),
            "embedding": [round(random.uniform(-1, 1), 4) for _ in range(1536)],
            "is_verified": random.choice([True, False]),
            "view_count": random.randint(0, 1000),
            "created_at": datetime.now() - timedelta(days=random.randint(1, 365)),
            "updated_at": datetime.now()
        }
        companies.append(company)
    
    return companies

def generate_user_data(count: int = 50) -> List[Dict[str, Any]]:
    users = []
    
    for i in range(count):
        first_names = ["Alex", "Maria", "Dmitry", "Elena", "Ivan", "Anna", "Sergey", "Olga", "Andrey", "Natalia"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"]
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        
        user = {
            "id": str(uuid.uuid4()),
            "email": generate_email(full_name),
            "password_hash": "$2b$12$K8vZQXqHjWxUzOeMnYpLrOuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZ",
            "full_name": full_name,
            "company_name": random.choice(COMPANIES),
            "role": random.choice(["admin", "manager", "analyst", "viewer"]),
            "is_active": True,
            "two_factor_enabled": random.choice([True, False]),
            "created_at": datetime.now() - timedelta(days=random.randint(1, 365)),
            "updated_at": datetime.now()
        }
        users.append(user)
    
    return users

def generate_partnerships(companies: List[Dict[str, Any]], users: List[Dict[str, Any]], count: int = 30) -> List[Dict[str, Any]]:
    partnerships = []
    
    for i in range(count):
        company_a = random.choice(companies)
        company_b = random.choice([c for c in companies if c["id"] != company_a["id"]])
        
        partnership = {
            "id": str(uuid.uuid4()),
            "company_a_id": company_a["id"],
            "company_b_id": company_b["id"],
            "compatibility_score": round(random.uniform(0.5, 0.95), 2),
            "match_reasons": [
                "Complementary product offerings",
                "Overlapping target markets",
                "Shared technology stack",
                "Geographic proximity"
            ],
            "synergy_areas": [
                "Joint marketing initiatives",
                "Product integration",
                "Co-development opportunities",
                "Shared customer base"
            ],
            "analysis_method": "AI-powered analysis",
            "analyzed_by_agent": "CompatibilityAnalyzerAgent",
            "ai_explanation": "High compatibility due to complementary product features and overlapping target markets.",
            "status": random.choice(["pending", "contacted", "negotiating", "agreed", "active"]),
            "contacted_at": datetime.now() - timedelta(days=random.randint(1, 60)) if random.choice([True, False]) else None,
            "partnership_started_at": datetime.now() - timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
            "deal_value": round(random.uniform(0, 1000000), 2),
            "revenue_generated": round(random.uniform(0, 500000), 2),
            "created_at": datetime.now() - timedelta(days=random.randint(1, 90)),
            "updated_at": datetime.now()
        }
        partnerships.append(partnership)
    
    return partnerships

def main():
    print("Generating seed data for ALGORITHMIC ARTS platform...")
    
    # Generate companies
    companies = generate_company_data(100)
    print(f"Generated {len(companies)} companies")
    
    # Generate users
    users = generate_user_data(50)
    print(f"Generated {len(users)} users")
    
    # Generate partnerships
    partnerships = generate_partnerships(companies, users, 30)
    print(f"Generated {len(partnerships)} partnerships")
    
    # Save to files
    import json
    
    with open("/home/alex/MyApps/SaasPlatform/platform/data/seed_companies.json", "w") as f:
        json.dump(companies, f, indent=2, default=str)
    
    with open("/home/alex/MyApps/SaasPlatform/platform/data/seed_users.json", "w") as f:
        json.dump(users, f, indent=2, default=str)
    
    with open("/home/alex/MyApps/SaasPlatform/platform/data/seed_partnerships.json", "w") as f:
        json.dump(partnerships, f, indent=2, default=str)
    
    print("Seed data saved to platform/data/ directory")
    
    # Print summary
    print("\nSummary:")
    print(f"- Companies: {len(companies)}")
    print(f"- Users: {len(users)}")
    print(f"- Partnerships: {len(partnerships)}")
    print("- Seed data files created in platform/data/")

if __name__ == "__main__":
    main()