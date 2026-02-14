from datetime import datetime, timezone
from typing import NamedTuple, Optional

from ..adapters.base import LeadData
from .audit_log import AuditLogger


class ResolutionResult(NamedTuple):
    action: str  # "create", "update", "skip"
    updated_lead: LeadData


class ConflictResolutionStrategy:
    """
    Стратегия разрешения конфликтов при синхронизации.
    По умолчанию используем стратегию "последнее обновление побеждает".
    """

    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        self.audit_logger = audit_logger

    def resolve_conflict(
        self, internal_lead: LeadData, crm_lead: LeadData
    ) -> ResolutionResult:
        """
                Разрешает конфликт между внутренним и CRM лидом.

        1. Если оба лиды имеют external_id и совпадают - сравниваем даты обновления
        2. Если только один лид имеет external_id - создаем новый или обновляем существующий
        3. Если ни один не имеет external_id - создаем новый

                Returns:
                    ResolutionResult с действием и обновленным лидом
        """
        # Если оба лиды имеют external_id и они совпадают
        if (
            internal_lead.external_id
            and crm_lead.external_id
            and internal_lead.external_id == crm_lead.external_id
        ):
            # Сравниваем даты обновления
            internal_updated = internal_lead.updated_at or datetime.min.replace(
                tzinfo=timezone.utc
            )
            crm_updated = crm_lead.updated_at or datetime.min.replace(
                tzinfo=timezone.utc
            )

            if crm_updated > internal_updated:
                # CRM более свежий - обновляем внутренний лид
                return ResolutionResult("update", crm_lead)
            else:
                # Внутренний более свежий - обновляем CRM (но это делается в другом методе)
                # Для этой функции просто возвращаем внутренний лид как актуальный
                return ResolutionResult("update", internal_lead)

        # Если только внутренний лид имеет external_id, но он не совпадает с CRM
        elif internal_lead.external_id and not crm_lead.external_id:
            # Обновляем CRM с данными из внутреннего лида
            return ResolutionResult("update", internal_lead)

        # Если только CRM лид имеет external_id
        elif crm_lead.external_id and not internal_lead.external_id:
            # Создаем новый лид во внутренней системе
            return ResolutionResult("create", crm_lead)

        # Если ни один не имеет external_id
        else:
            # Создаем новый лид во внутренней системе
            return ResolutionResult("create", crm_lead)


class LastWriteWinsStrategy(ConflictResolutionStrategy):
    """Стратегия "последнее обновление побеждает"."""

    pass


class ManualReviewStrategy(ConflictResolutionStrategy):
    """Стратегия ручного подтверждения конфликтов."""

    def resolve_conflict(
        self, internal_lead: LeadData, crm_lead: LeadData
    ) -> ResolutionResult:
        # В реальной реализации здесь был бы вызов к сервису уведомлений
        # Для упрощения всегда выбираем CRM данные
        return ResolutionResult("update", crm_lead)


class MergeStrategy(ConflictResolutionStrategy):
    """Стратегия слияния данных."""

    def resolve_conflict(
        self, internal_lead: LeadData, crm_lead: LeadData
    ) -> ResolutionResult:
        # Создаем объединенный лид
        merged_lead = LeadData(
            title=crm_lead.title or internal_lead.title,
            company_name=crm_lead.company_name or internal_lead.company_name,
            contact_person=crm_lead.contact_person or internal_lead.contact_person,
            contact_email=crm_lead.contact_email or internal_lead.contact_email,
            contact_phone=crm_lead.contact_phone or internal_lead.contact_phone,
            deal_value=max(crm_lead.deal_value, internal_lead.deal_value),
            compatibility_score=max(
                crm_lead.compatibility_score, internal_lead.compatibility_score
            ),
            partnership_id=internal_lead.partnership_id or crm_lead.partnership_id,
            status=crm_lead.status or internal_lead.status,
            notes=crm_lead.notes or internal_lead.notes,
            external_id=crm_lead.external_id or internal_lead.external_id,
            created_at=internal_lead.created_at or crm_lead.created_at,
            updated_at=max(
                internal_lead.updated_at or datetime.min.replace(tzinfo=timezone.utc),
                crm_lead.updated_at or datetime.min.replace(tzinfo=timezone.utc),
            ),
        )

        return ResolutionResult("update", merged_lead)
