from typing import Dict

TECH_KEYWORDS = {
    "python": ["python", "django", "fastapi", "flask"],
    "javascript": ["javascript", "typescript", "node.js", "nodejs"],
    "react": ["react", "react.js", "reactjs"],
    "vue": ["vue", "vue.js", "vuejs", "nuxt"],
    "golang": ["golang", "go lang", " go "],
    "postgresql": ["postgresql", "postgres"],
    "redis": ["redis"],
    "kafka": ["kafka", "apache kafka"],
    "kubernetes": ["kubernetes", "k8s"],
    "docker": ["docker"],
    "elasticsearch": ["elasticsearch", "elastic"],
    "mongodb": ["mongodb", "mongo"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud platform"],
}


def extract_tech_stack(text: str) -> Dict[str, bool]:
    """
    Извлекает технологический стек из текста.
    Возвращает словарь {tech: True} для найденных технологий.
    """
    text_lower = text.lower()
    tech_stack = {}
    
    for tech, keywords in TECH_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                tech_stack[tech] = True
                break
    
    return tech_stack