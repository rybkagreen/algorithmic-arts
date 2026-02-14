"""AI service for AI core service."""

from datetime import datetime

from shared.logging import get_logger
from .repositories.ai_repository import AIRepository
from .schemas.ai import CompatibilityAnalysisRequest, CompatibilityAnalysisResponse, OutreachMessageRequest, OutreachMessageResponse

logger = get_logger("ai-service")


class AIService:
    """AI service for partnership intelligence."""
    
    def __init__(self):
        self.ai_repository = AIRepository()
    
    async def analyze_compatibility(self, request: CompatibilityAnalysisRequest) -> CompatibilityAnalysisResponse:
        """Analyze compatibility between two companies."""
        # In real implementation, this would call LLM models (YandexGPT, GigaChat, etc.)
        # For now, return a mock response with calculated score
        
        # Calculate compatibility score (simplified version)
        compatibility_score = self._calculate_compatibility_score(
            request.company_1, request.company_2
        )
        
        # Generate analysis
        analysis = self._generate_analysis(request.company_1, request.company_2, compatibility_score)
        
        return CompatibilityAnalysisResponse(
            company_1=request.company_1,
            company_2=request.company_2,
            compatibility_score=compatibility_score,
            factors={
                "tech_stack_overlap": 0.8,
                "market_overlap": 0.6,
                "size_match": 0.7,
                "geographic_proximity": 0.9,
                "no_direct_competition": 0.8,
                "feature_complementarity": 0.7
            },
            explanation=analysis,
            created_at=datetime.utcnow().isoformat()
        )
    
    async def generate_outreach_message(self, request: OutreachMessageRequest) -> OutreachMessageResponse:
        """Generate personalized outreach message."""
        # In real implementation, this would use LLM to generate messages
        # For now, return a mock response
        
        message = f"Dear {request.recipient_name},\n\nI noticed that {request.company_1.name} and {request.company_2.name} have excellent potential for partnership based on our analysis.\n\nOur compatibility score is {request.compatibility_score:.2f}, indicating strong strategic alignment in technology stack, market positioning, and complementary capabilities.\n\nWould you be interested in exploring a potential collaboration?\n\nBest regards,\nThe ALGORITHMIC ARTS Team"
        
        return OutreachMessageResponse(
            message=message,
            style=request.style,
            language=request.language,
            created_at=datetime.utcnow().isoformat()
        )
    
    def _calculate_compatibility_score(self, company_1: dict, company_2: dict) -> float:
        """Calculate compatibility score between two companies."""
        # Simplified calculation - in real implementation would use AI models
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
        no_competition = 0.8
        score += 0.15 * no_competition
        weight += 0.15
        
        # Feature complementarity (15%)
        feature_complementarity = 0.7
        score += 0.15 * feature_complementarity
        weight += 0.15
        
        # Normalize score
        if weight > 0:
            score = score / weight
        
        return min(max(score, 0.0), 1.0)
    
    def _generate_analysis(self, company_1: dict, company_2: dict, score: float) -> str:
        """Generate analysis text."""
        if score >= 0.8:
            strength = "excellent"
            recommendation = "highly recommended"
        elif score >= 0.6:
            strength = "good"
            recommendation = "recommended"
        elif score >= 0.4:
            strength = "moderate"
            recommendation = "consider"
        else:
            strength = "weak"
            recommendation = "not recommended"
        
        return f"Analysis shows {strength} compatibility between {company_1.get('name', 'Company A')} and {company_2.get('name', 'Company B')} with a score of {score:.2f}. Key strengths include technology stack alignment and geographic proximity. This partnership is {recommendation} for strategic collaboration."