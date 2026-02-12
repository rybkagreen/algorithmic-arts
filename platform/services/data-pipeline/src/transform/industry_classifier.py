from typing import List, Dict

INDUSTRY_KEYWORDS = {
    "Martech": ["маркетинг", "реклама", "retargeting", "crm", "lead", "conversion"],
    "Fintech": ["финансы", "платеж", "банкинг", "кредит", "инвестиц", "страхов"],
    "Healthtech": ["здравоохранение", "медицина", "клиника", "здоровье", "фарма"],
    "Edtech": ["образование", "обучение", "курс", "школа", "университет"],
    "PropTech": ["недвижимость", "ипотека", "риэлтор", "аренда", "дом"],
    "Logistics": ["логистика", "доставка", "транспорт", "груз", "склад"],
    "HRtech": ["hr", "персонал", "вакансия", "подбор", "рекрутмент"],
    "Cybersecurity": ["безопасность", "кибер", "защита", "шифрование", "пентест"],
    "AI/ML": ["искусственный интеллект", "нейросеть", "машинное обучение", "ai", "ml"],
    "SaaS": ["saas", "сервис", "платформа", "программное обеспечение", "облачный"],
}

def classify_industry(text: str) -> str:
    """
    Rule-based классификация индустрии по ключевым словам.
    Возвращает лучшую категорию или "SaaS" по умолчанию.
    """
    text_lower = text.lower()
    scores = {industry: 0 for industry in INDUSTRY_KEYWORDS}
    
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[industry] += 1
    
    best_industry, best_score = max(scores.items(), key=lambda x: x[1])
    
    return best_industry if best_score > 0 else "SaaS"