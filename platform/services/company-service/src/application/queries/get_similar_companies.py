from typing import List
from uuid import UUID

from .domain.company import Company
from .infrastructure.repositories.company_repository import CompanyRepository
from .infrastructure.elasticsearch.company_indexer import CompanyIndexer


class GetSimilarCompaniesQuery:
    def __init__(self, company_repository: CompanyRepository, indexer: CompanyIndexer):
        self.company_repository = company_repository
        self.indexer = indexer

    async def execute(self, company_id: UUID, top_k: int = 5) -> List[Company]:
        """Получить похожие компании по embedding (только активные)."""
        # Сначала получаем компанию для получения embedding
        company = await self.company_repository.get_by_id(company_id)
        if not company:
            raise Exception(f"Company with id {company_id} not found or deleted")

        # Если у компании нет embedding, возвращаем пустой список
        if not company.embedding:
            return []

        # Ищем похожие компании через Elasticsearch
        try:
            response = await self.indexer.get_similar_companies(
                embedding=company.embedding,
                top_k=top_k
            )
            
            # Фильтруем только активные компании из результатов
            similar_company_ids = [hit["_id"] for hit in response["hits"]["hits"]]
            
            # Получаем активные компании по ID
            companies_data = []
            for company_id_str in similar_company_ids:
                try:
                    company_data = await self.company_repository.get_by_id(UUID(company_id_str))
                    if company_data:
                        companies_data.append(company_data)
                except Exception:
                    continue
            
            return [
                Company(**company.__dict__)
                for company in companies_data[:top_k]
            ]
            
        except Exception:
            # Если Elasticsearch недоступен, используем базовый поиск по отрасли
            industry = company.industry
            companies_data = await self.company_repository.get_by_industry(industry, limit=top_k)
            
            return [
                Company(**company.__dict__)
                for company in companies_data
            ]