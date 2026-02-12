import structlog
from datetime import datetime
from typing import Dict, Any, Optional, List
from elasticsearch import AsyncElasticsearch

logger = structlog.get_logger()


class CompanyIndexer:
    """Утилита для индексации компаний в Elasticsearch."""

    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client = es_client
        self.index_name = "companies"

    async def create_index(self) -> None:
        """Создание индекса companies с необходимой маппинговой конфигурацией."""
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text", "analyzer": "russian"},
                    "slug": {"type": "keyword"},
                    "description": {"type": "text", "analyzer": "russian"},
                    "website": {"type": "keyword"},
                    "industry": {"type": "keyword"},
                    "sub_industries": {"type": "keyword"},
                    "business_model": {"type": "text", "analyzer": "russian"},
                    "founded_year": {"type": "integer"},
                    "headquarters_country": {"type": "keyword"},
                    "headquarters_city": {"type": "keyword"},
                    "employees_count": {"type": "integer"},
                    "employees_range": {"type": "keyword"},
                    "funding_stage": {"type": "keyword"},
                    "last_funding_date": {"type": "date"},
                    "legal_name": {"type": "text", "analyzer": "russian"},
                    "tech_stack": {"type": "object"},
                    "integrations": {"type": "keyword"},
                    "api_available": {"type": "boolean"},
                    "ai_summary": {"type": "text", "analyzer": "russian"},
                    "ai_tags": {"type": "keyword"},
                    "embedding": {"type": "dense_vector", "dims": 768},
                    "is_verified": {"type": "boolean"},
                    "view_count": {"type": "integer"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "deleted_at": {"type": "date"}
                }
            },
            "settings": {
                "analysis": {
                    "analyzer": {
                        "russian": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "russian_stop", "russian_stemmer"]
                        }
                    },
                    "filter": {
                        "russian_stop": {
                            "type": "stop",
                            "stopwords": "_russian_"
                        },
                        "russian_stemmer": {
                            "type": "stemmer",
                            "language": "russian"
                        }
                    }
                }
            }
        }

        try:
            # Проверяем, существует ли индекс
            exists = await self.es_client.indices.exists(index=self.index_name)
            if not exists:
                await self.es_client.indices.create(index=self.index_name, body=mapping)
                logger.info("elasticsearch_index_created", index=self.index_name)
            else:
                logger.info("elasticsearch_index_exists", index=self.index_name)
        except Exception as e:
            logger.error("elasticsearch_index_creation_failed", error=str(e))
            raise

    async def index_company(self, company: Any) -> None:
        """Индексация компании в Elasticsearch."""
        try:
            # Преобразуем компанию в словарь для индексации
            doc = {
                "id": str(company.id),
                "name": company.name,
                "slug": getattr(company, 'slug', ''),
                "description": getattr(company, 'description', ''),
                "website": getattr(company, 'website', ''),
                "industry": getattr(company, 'industry', ''),
                "sub_industries": getattr(company, 'sub_industries', []),
                "business_model": getattr(company, 'business_model', ''),
                "founded_year": getattr(company, 'founded_year', None),
                "headquarters_country": getattr(company, 'headquarters_country', 'RU'),
                "headquarters_city": getattr(company, 'headquarters_city', None),
                "employees_count": getattr(company, 'employees_count', None),
                "employees_range": getattr(company, 'employees_range', None),
                "funding_stage": getattr(company, 'funding_stage', None),
                "last_funding_date": getattr(company, 'last_funding_date', None),
                "legal_name": getattr(company, 'legal_name', ''),
                "tech_stack": getattr(company, 'tech_stack', {}),
                "integrations": getattr(company, 'integrations', []),
                "api_available": getattr(company, 'api_available', False),
                "ai_summary": getattr(company, 'ai_summary', ''),
                "ai_tags": getattr(company, 'ai_tags', []),
                "embedding": getattr(company, 'embedding', None),
                "is_verified": getattr(company, 'is_verified', False),
                "view_count": getattr(company, 'view_count', 0),
                "created_at": company.created_at.isoformat() if hasattr(company, 'created_at') else datetime.utcnow().isoformat(),
                "updated_at": company.updated_at.isoformat() if hasattr(company, 'updated_at') else datetime.utcnow().isoformat(),
                "deleted_at": company.deleted_at.isoformat() if hasattr(company, 'deleted_at') and company.deleted_at else None
            }

            # Индексируем документ
            await self.es_client.index(
                index=self.index_name,
                id=str(company.id),
                document=doc,
                refresh=True
            )
            logger.info("company_indexed", company_id=str(company.id))

        except Exception as e:
            logger.error("company_indexing_failed", company_id=str(getattr(company, 'id', 'unknown')), error=str(e))
            raise

    async def search_companies(self, query: str, filters: Optional[Dict[str, Any]] = None, 
                             size: int = 10, from_: int = 0) -> Dict[str, Any]:
        """Поиск компаний по тексту и фильтрам."""
        try:
            # Базовый запрос
            search_body: Dict[str, Any] = {
                "query": {
                    "bool": {
                        "must": []
                    }
                },
                "from": from_,
                "size": size
            }

            # Добавляем текстовый поиск
            if query:
                search_body["query"]["bool"]["must"].append({
                    "multi_match": {
                        "query": query,
                        "fields": ["name^3", "description^2", "ai_summary^2", "industry", "tech_stack.*"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                })

            # Добавляем фильтры
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        search_body["query"]["bool"]["filter"] = search_body["query"]["bool"].get("filter", [])
                        search_body["query"]["bool"]["filter"].append({
                            "terms": {key: value}
                        })
                    else:
                        search_body["query"]["bool"]["filter"] = search_body["query"]["bool"].get("filter", [])
                        search_body["query"]["bool"]["filter"].append({
                            "term": {key: value}
                        })

            # Выполняем поиск
            response = await self.es_client.search(
                index=self.index_name,
                body=search_body
            )

            return response

        except Exception as e:
            logger.error("company_search_failed", query=query, error=str(e))
            raise

    async def get_similar_companies(self, embedding: List[float], top_k: int = 5) -> Dict[str, Any]:
        """Поиск похожих компаний по векторному embedding."""
        try:
            search_body = {
                "knn": {
                    "field": "embedding",
                    "query_vector": embedding,
                    "k": top_k,
                    "num_candidates": top_k * 10
                },
                "_source": ["id", "name", "industry", "ai_tags", "similarity"]
            }

            response = await self.es_client.search(
                index=self.index_name,
                body=search_body
            )

            return response

        except Exception as e:
            logger.error("similar_companies_search_failed", error=str(e))
            raise