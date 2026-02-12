import spacy
import structlog

log = structlog.get_logger()

_nlp = None

def get_nlp():
    """Lazy load spacy model."""
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("ru_core_news_sm")
        except OSError:
            log.error("spacy_model_not_found", model="ru_core_news_sm")
            raise
    return _nlp


def extract_entities(text: str) -> dict:
    """
    Извлекает сущности из текста с помощью spacy.
    Возвращает: {"companies": [...], "locations": [...]}
    """
    nlp = get_nlp()
    doc = nlp(text)
    
    companies = []
    locations = []
    
    for ent in doc.ents:
        if ent.label_ == "ORG":
            companies.append(ent.text)
        elif ent.label_ in ("LOC", "GPE"):
            locations.append(ent.text)
    
    # Удаляем дубликаты и фильтруем пустые
    companies = list(dict.fromkeys([c.strip() for c in companies if c.strip()]))
    locations = list(dict.fromkeys([l.strip() for l in locations if l.strip()]))
    
    return {
        "companies": companies,
        "locations": locations,
    }