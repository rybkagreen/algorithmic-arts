from dataclasses import dataclass, field
from typing import Any, List, Dict
from uuid import UUID
from datetime import datetime


@dataclass
class AgentState:
    """Глобальное состояние, передаваемое между агентами в LangGraph."""
    # Входные данные
    trigger:          str             # 'company_created' | 'user_request' | 'scheduled'
    company_id:       UUID | None = None
    company_a_id:     UUID | None = None
    company_b_id:     UUID | None = None
    user_id:          UUID | None = None
    outreach_style:   str = "formal"  # 'formal' | 'friendly' | 'technical'

    # Результаты каждого агента
    scout_insights:       List[Dict[str, Any]] = field(default_factory=list)
    enriched_company:     Dict[str, Any] | None = None
    compatibility_score:  float | None = None
    compatibility_report: Dict[str, Any] | None = None
    outreach_message:     str | None = None
    deal_probability:     float | None = None

    # Служебные
    errors:     List[str] = field(default_factory=list)
    should_notify: bool = False
    last_updated: datetime = field(default_factory=datetime.utcnow)