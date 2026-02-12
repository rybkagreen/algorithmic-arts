import re
from rapidfuzz import fuzz
from typing import List, Dict, Optional

THRESHOLD = 88  # token_set_ratio threshold

def _normalize_name(name: str) -> str:
    """
    Нормализует название компании для сравнения.
    Удаляет юридические формы и пунктуацию.
    """
    if not name:
        return ""
    
    name = name.lower()
    # Удаляем юридические формы
    name = re.sub(r"\b(ооо|зао|пао|ао|ип|нпо|нко|гк|гуп|муп)\b", "", name)
    # Удаляем пунктуацию
    name = re.sub(r'["""«»"\',.()\-]', " ", name)
    # Схлопываем пробелы
    name = re.sub(r"\s+", " ", name).strip()
    return name


def find_duplicate(
    candidate: Dict[str, str], 
    existing_companies: List[Dict[str, str]]
) -> Optional[Dict[str, str]]:
    """
    Ищет дубликат среди существующих компаний.
    Сравнивает только по нормализованному названию.
    Возвращает найденную компанию или None.
    """
    if not existing_companies:
        return None
        
    candidate_norm = _normalize_name(candidate.get("name", ""))
    if not candidate_norm:
        return None
    
    # Быстрый фильтр: первые 3 символа
    candidates = [
        comp for comp in existing_companies 
        if _normalize_name(comp.get("name", ""))[:3] == candidate_norm[:3]
    ]
    
    if not candidates:
        return None
    
    # Полное сравнение с token_set_ratio
    best_match = None
    best_score = 0
    
    for comp in candidates:
        comp_norm = _normalize_name(comp.get("name", ""))
        if not comp_norm:
            continue
            
        score = fuzz.token_set_ratio(candidate_norm, comp_norm)
        if score >= THRESHOLD and score > best_score:
            best_score = score
            best_match = comp
    
    return best_match