"""Unit tests for partner service."""

import pytest
from unittest.mock import patch
from datetime import datetime
from uuid import UUID

from src.services.partner_service import PartnerService
from src.schemas.partner import PartnershipCreate, PartnershipOut


class TestPartnerService:
    """Unit tests for partner service."""
    
    @pytest.fixture
    def partner_service(self):
        return PartnerService()
    
    def test_partnership_creation(self, partner_service):
        """Test partnership creation structure."""
        partnership_data = PartnershipCreate(
            company_id_1="12345678-1234-5678-1234-567812345678",
            company_id_2="87654321-4321-8765-4321-876543216789",
            status="proposed",
            compatibility_score=0.75,
            reason="Good tech stack overlap"
        )
        
        assert partnership_data.company_id_1 == "12345678-1234-5678-1234-567812345678"
        assert partnership_data.company_id_2 == "87654321-4321-8765-4321-876543216789"
        assert partnership_data.status == "proposed"
        assert partnership_data.compatibility_score == 0.75
    
    @pytest.mark.asyncio
    async def test_get_partnership_by_id(self, partner_service):
        """Test getting partnership by ID."""
        # Mock database
        with patch.object(partner_service.partnership_repository, 'get_by_id') as mock_get:
            mock_partnership = PartnershipOut(
                id=str(UUID("12345678-1234-5678-1234-567812345678")),
                company_id_1="12345678-1234-5678-1234-567812345678",
                company_id_2="87654321-4321-8765-4321-876543216789",
                status="active",
                compatibility_score=0.85,
                reason="Strategic alignment",
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat(),
                company_1={
                    "id": "12345678-1234-5678-1234-567812345678",
                    "name": "Company A",
                    "slug": "company-a",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                company_2={
                    "id": "87654321-4321-8765-4321-876543216789",
                    "name": "Company B",
                    "slug": "company-b",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            mock_get.return_value = mock_partnership
            
            result = await partner_service.get_partnership_by_id(UUID("12345678-1234-5678-1234-567812345678"))
            
            assert result.id == mock_partnership.id
            assert result.status == mock_partnership.status