from typing import List, Dict, Any
from elasticsearch import AsyncElasticsearch
import structlog

log = structlog.get_logger()

INDEX_NAME = "companies"

INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "id":           {"type": "keyword"},
            "name":         {"type": "text",    "analyzer": "russian",
                             "fields": {"keyword": {"type": "keyword"}}},
            "description":  {"type": "text",    "analyzer": "russian"},
            "industry":     {"type": "keyword"},
            "sub_industries": {"type": "keyword"},  # array
            "ai_summary":   {"type": "text",    "analyzer": "russian"},
            "ai_tags":      {"type": "keyword"},
            "website":      {"type": "keyword",  "index": False},
            "headquarters_country": {"type": "keyword"},
            "headquarters_city":    {"type": "keyword"},
            "employees_range":      {"type": "keyword"},
            "funding_stage":        {"type": "keyword"},
            "api_available":        {"type": "boolean"},
            "is_verified":          {"type": "boolean"},
            "founded_year":         {"type": "integer"},
            "created_at":           {"type": "date"},
            "updated_at":           {"type": "date"},
        }
    },
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "russian": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "russian_morphology", "english_morphology"]
                }
            }
        }
    }
}

class ESIndexer:
    def __init__(self, hosts: str = "elasticsearch:9200"):
        self.hosts = hosts
        self._es = None

    async def connect(self):
        if not self._es:
            self._es = AsyncElasticsearch(
                hosts=[self.hosts],
                http_auth=None,
                timeout=30
            )
            # Создаем индекс если не существует
            try:
                await self._es.indices.create(index=INDEX_NAME, body=INDEX_MAPPING)
            except Exception as e:
                log.info("index_already_exists", error=str(e))

    async def index_company(self, company: Dict[str, Any]):
        """Индексирует одну компанию."""
        try:
            await self.connect()
            
            # Фильтруем поля по mapping
            doc = {
                k: v for k, v in company.items()
                if k in INDEX_MAPPING["mappings"]["properties"]
            }
            
            await self._es.index(
                index=INDEX_NAME,
                id=company.get("id"),
                document=doc
            )
            log.info("company_indexed", name=company.get("name"))
        except Exception as exc:
            log.error("es_index_failed", error=str(exc), company_name=company.get("name"))
            raise

    async def bulk_index(self, companies: List[Dict[str, Any]]):
        """Bulk индексация для первоначальной загрузки."""
        try:
            await self.connect()
            
            actions = []
            for company in companies:
                doc = {
                    k: v for k, v in company.items()
                    if k in INDEX_MAPPING["mappings"]["properties"]
                }
                actions.append({
                    "_index": INDEX_NAME,
                    "_id": company.get("id"),
                    "_source": doc
                })
            
            from elasticsearch.helpers import async_bulk
            await async_bulk(self._es, actions)
            log.info("bulk_indexed", count=len(companies))
        except Exception as exc:
            log.error("bulk_index_failed", error=str(exc), count=len(companies))
            raise