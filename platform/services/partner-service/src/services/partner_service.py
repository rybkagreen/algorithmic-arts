"""Partner service for partner service."""

from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
import uuid

from shared.logging import get_logger
from .config import settings
from .repositories.partner_repository import PartnerRepository
from .schemas.partner import PartnershipCreate, PartnershipUpdate, PartnershipOut, CompanyOut
from .core.exceptions import UserNotFoundError

logger = get_logger("partner-service")


class PartnerService:
    """Partner service."""
    
    def __init__(self):
        self.partner_repository = PartnerRepository()
    
    async def create_partnership(self, partnership_data: PartnershipCreate) -> PartnershipOut:
        """Create new partnership."""
        # Check if companies exist
        async with get_db() as db:
            company_1 = await self.partner_repository.get_company_by_id(db, partnership_data.company_id_1)
            company_2 = await self.partner_repository.get_company_by_id(db, partnership_data.company_id_2)
            
            if not company_1:
                raise UserNotFoundError(f"Company {partnership_data.company_id_1} not found")
            if not company_2:
                raise UserNotFoundError(f"Company {partnership_data.company_id_2} not found")
        
        # Calculate compatibility score (simplified version - in real implementation would use AI)
        compatibility_score = self._calculate_compatibility_score(company_1, company_2)
        
        # Create partnership
        partnership_data_dict = partnership_data.model_dump()
        partnership_data_dict['compatibility_score'] = compatibility_score
        
        async with get_db() as db:
            partnership = await self.partner_repository.create_partnership(db, partnership_data_dict)
            
            return PartnershipOut(
                id=str(partnership.id),
                company_id_1=str(partnership.company_id_1),
                company_id_2=str(partnership.company_id_2),
                status=partnership.status.value,
                compatibility_score=partnership.compatibility_score,
                reason=partnership_data.reason or f"Compatibility score: {compatibility_score:.2f}",
                created_at=partnership.created_at.isoformat(),
                updated_at=partnership.updated_at.isoformat(),
                company_1=CompanyOut(**self.partner_repository.to_company_dict(company_1)),
                company_2=CompanyOut(**self.partner_repository.to_company_dict(company_2))
            )
    
    async def get_partnership_by_id(self, partnership_id: uuid.UUID) -> PartnershipOut:
        """Get partnership by ID."""
        async with get_db() as db:
            partnership = await self.partner_repository.get_by_id(db, partnership_id)
            if not partnership:
                raise UserNotFoundError(f"Partnership with ID {partnership_id} not found")
            
            company_1 = await self.partner_repository.get_company_by_id(db, partnership.company_id_1)
            company_2 = await self.partner_repository.get_company_by_id(db, partnership.company_id_2)
            
            return PartnershipOut(
                id=str(partnership.id),
                company_id_1=str(partnership.company_id_1),
                company_id_2=str(partnership.company_id_2),
                status=partnership.status.value,
                compatibility_score=partnership.compatibility_score,
                reason=partnership.reason,
                created_at=partnership.created_at.isoformat(),
                updated_at=partnership.updated_at.isoformat(),
                company_1=CompanyOut(**self.partner_repository.to_company_dict(company_1)),
                company_2=CompanyOut(**self.partner_repository.to_company_dict(company_2))
            )
    
    async def update_partnership(self, partnership_id: uuid.UUID, update_data: PartnershipUpdate) -> PartnershipOut:
        """Update partnership."""
        async with get_db() as db:
            updated_partnership = await self.partner_repository.update_partnership(
                db, partnership_id, update_data.model_dump(exclude_unset=True)
            )
            
            company_1 = await self.partner_repository.get_company_by_id(db, updated_partnership.company_id_1)
            company_2 = await self.partner_repository.get_company_by_id(db, updated_partnership.company_id_2)
            
            return PartnershipOut(
                id=str(updated_partnership.id),
                company_id_1=str(updated_partnership.company_id_1),
                company_id_2=str(updated_partnership.company_id_2),
                status=updated_partnership.status.value,
                compatibility_score=updated_partnership.compatibility_score,
                reason=updated_partnership.reason,
                created_at=updated_partnership.created_at.isoformat(),
                updated_at=updated_partnership.updated_at.isoformat(),
                company_1=CompanyOut(**self.partner_repository.to_company_dict(company_1)),
                company_2=CompanyOut(**self.partner_repository.to_company_dict(company_2))
            )
    
    async def get_partnerships_for_company(self, company_id: uuid.UUID) -> List[PartnershipOut]:
        """Get all partnerships for a company."""
        async with get_db() as db:
            partnerships = await self.partner_repository.get_by_company(db, company_id)
            
            results = []
            for partnership in partnerships:
                company_1 = await self.partner_repository.get_company_by_id(db, partnership.company_id_1)
                company_2 = await self.partner_repository.get_company_by_id(db, partnership.company_id_2)
                
                results.append(PartnershipOut(
                    id=str(partnership.id),
                    company_id_1=str(partnership.company_id_1),
                    company_id_2=str(partnership.company_id_2),
                    status=partnership.status.value,
                    compatibility_score=partnership.compatibility_score,
                    reason=partnership.reason,
                    created_at=partnership.created_at.isoformat(),
                    updated_at=partnership.updated_at.isoformat(),
                    company_1=CompanyOut(**self.partner_repository.to_company_dict(company_1)),
                    company_2=CompanyOut(**self.partner_repository.to_company_dict(company_2))
                ))
            
            return results
    
    def _calculate_compatibility_score(self, company_1: dict, company_2: dict) -> float:
        """Calculate compatibility score between two companies."""
        # Simplified compatibility calculation (in real implementation would use AI models)
        score = 0.0
        weight = 0.0
        
        # Tech stack overlap (25%)
        tech_stack_1 = set(company_1.get('tech_stack', []) or [])
        tech_stack_2 = set(company_2.get('tech_stack', []) or [])
        if tech_stack_1 and tech_stack_2:
            overlap = len(tech_stack_1.intersection(tech_stack_2)) / len(tech_stack_1.union(tech_stack_2))
            score += 0.25 * overlap
            weight += 0.25
        
        # Market overlap (20%)
        industry_1 = company_1.get('industry', '')
        industry_2 = company_2.get('industry', '')
        if industry_1 and industry_2:
            market_overlap = 1.0 if industry_1 == industry_2 else 0.5
            score += 0.20 * market_overlap
            weight += 0.20
        
        # Company size match (15%)
        employees_1 = company_1.get('employees_count') or 0
        employees_2 = company_2.get('employees_count') or 0
        if employees_1 > 0 and employees_2 > 0:
            size_ratio = min(employees_1, employees_2) / max(employees_1, employees_2)
            score += 0.15 * size_ratio
            weight += 0.15
        
        # Geographic proximity (10%)
        country_1 = company_1.get('headquarters_country', 'RU')
        country_2 = company_2.get('headquarters_country', 'RU')
        geo_proximity = 1.0 if country_1 == country_2 else 0.5
        score += 0.10 * geo_proximity
        weight += 0.10
        
        # No direct competition (15%)
        # In real implementation, this would be determined by AI analysis
        no_competition = 0.8  # Default assumption
        score += 0.15 * no_competition
        weight += 0.15
        
        # Feature complementarity (15%)
        # In real implementation, this would be determined by AI analysis
        feature_complementarity = 0.7  # Default assumption
        score += 0.15 * feature_complementarity
        weight += 0.15
        
        # Normalize score
        if weight > 0:
            score = score / weight
        
        return min(max(score, 0.0), 1.0)