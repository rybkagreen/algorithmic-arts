from typing import Dict, Any
from .ner_extractor import extract_entities
from .funding_parser import parse_funding
from .tech_extractor import extract_tech_stack
from .industry_classifier import classify_industry

def normalize_company_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Нормализует сырые данные компании в стандартную структуру.
    """
    normalized = {
        "name": raw_data.get("name", "").strip(),
        "description": raw_data.get("description", "").strip(),
        "website": raw_data.get("website", "").strip(),
        "source": raw_data.get("source", ""),
        "source_url": raw_data.get("source_url", ""),
        "created_at": raw_data.get("pub_date") or raw_data.get("created_at"),
        "updated_at": None,
        "deleted_at": None,
        # Поля из EGRUL
        "inn": raw_data.get("inn"),
        "ogrn": raw_data.get("ogrn"),
        "kpp": raw_data.get("kpp"),
        "legal_name": raw_data.get("legal_name"),
        "legal_address": raw_data.get("legal_address"),
        "reg_date": raw_data.get("reg_date"),
        "is_active": raw_data.get("is_active"),
        "okved_main": raw_data.get("okved_main"),
        # Поля из Crunchbase/Habr
        "employees_range": raw_data.get("employees_range"),
        "founded_year": raw_data.get("founded_year"),
        "funding_total": raw_data.get("funding_total"),  # копейки
        "funding_stage": raw_data.get("funding_stage"),
        "headquarters_country": raw_data.get("headquarters_country"),
        # Технологии и индустрия
        "tech_stack": {},
        "industry": "SaaS",
        "sub_industries": [],
        # AI-поля (будут заполнены позже)
        "ai_summary": "",
        "ai_tags": [],
        # Статистика
        "vacancy_count": raw_data.get("vacancy_count", 0),
        "raw_description": raw_data.get("raw_description", ""),
        "funding_text": raw_data.get("funding_text", ""),
    }
    
    # Извлекаем технологии из description и raw_description
    text_for_tech = (
        normalized["description"] + " " + 
        normalized["raw_description"] + " " +
        raw_data.get("company_name_hint", "") + " " +
        raw_data.get("title", "")
    )
    normalized["tech_stack"] = extract_tech_stack(text_for_tech)
    
    # Классифицируем индустрию
    text_for_industry = (
        normalized["description"] + " " + 
        normalized["raw_description"] + " " +
        raw_data.get("title", "")
    )
    normalized["industry"] = classify_industry(text_for_industry)
    
    # Парсим финансирование из funding_text
    if raw_data.get("funding_text"):
        funding = parse_funding(raw_data["funding_text"])
        if funding:
            normalized["funding_total"] = funding["amount"]
    
    # Извлекаем сущности через NER
    entities = extract_entities(text_for_industry)
    if entities["companies"]:
        normalized["ai_tags"].extend([f"company:{c}" for c in entities["companies"]])
    if entities["locations"]:
        normalized["ai_tags"].extend([f"location:{l}" for l in entities["locations"]])
    
    return normalized