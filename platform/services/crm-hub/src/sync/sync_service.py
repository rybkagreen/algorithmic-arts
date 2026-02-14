from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from ..adapters.base import BaseCRMAdapter, LeadData
from .audit_log import AuditLogger
from .conflict_resolver import ConflictResolutionStrategy
from .field_mapper import FieldMapper


class SyncService:
    """
    Сервис двунаправленной синхронизации между внутренней системой и CRM.
    """

    def __init__(
        self,
        adapter: BaseCRMAdapter,
        field_mapper: FieldMapper,
        conflict_resolver: ConflictResolutionStrategy,
        audit_logger: AuditLogger,
    ):
        self.adapter = adapter
        self.field_mapper = field_mapper
        self.conflict_resolver = conflict_resolver
        self.audit_logger = audit_logger

    async def to_crm(
        self, lead_data: LeadData, connection_id: UUID
    ) -> Tuple[bool, str]:
        """
        Синхронизация лида из внутренней системы в CRM.

        Returns:
            (success: bool, external_id: str)
        """
        try:
            # Проверяем, существует ли уже лид в CRM
            if lead_data.external_id:
                try:
                    existing_lead = await self.adapter.get_lead(lead_data.external_id)
                    # Если лид существует, обновляем его
                    updates = self.field_mapper.map_to_crm_updates(
                        lead_data, existing_lead
                    )
                    success = await self.adapter.update_lead(
                        lead_data.external_id, updates
                    )
                    if success:
                        self.audit_logger.log_sync_event(
                            "to_crm_update",
                            connection_id,
                            lead_data.external_id,
                            lead_data.title,
                            "success",
                        )
                        return True, lead_data.external_id
                except Exception:
                    # Если не удалось получить лид, создаем новый
                    pass

            # Создаем новый лид
            external_id = await self.adapter.create_lead(lead_data)
            if external_id:
                # Обновляем lead_data с новым external_id
                lead_data.external_id = external_id

                self.audit_logger.log_sync_event(
                    "to_crm_create",
                    connection_id,
                    external_id,
                    lead_data.title,
                    "success",
                )
                return True, external_id

            self.audit_logger.log_sync_event(
                "to_crm_create",
                connection_id,
                None,
                lead_data.title,
                "failure",
                error="Failed to create lead in CRM",
            )
            return False, ""

        except Exception as e:
            self.audit_logger.log_sync_event(
                "to_crm", connection_id, None, lead_data.title, "failure", error=str(e)
            )
            return False, ""

    async def from_crm(
        self, connection_id: UUID, updated_since: Optional[datetime] = None
    ) -> List[LeadData]:
        """
        Синхронизация лида из CRM во внутреннюю систему.
        """
        leads = []
        try:
            crm_leads = await self.adapter.list_leads(updated_since)

            for crm_lead in crm_leads:
                # Преобразуем CRM-лид во внутренний формат
                internal_lead = self.field_mapper.map_from_crm(crm_lead)

                # Проверяем конфликты
                resolution = self.conflict_resolver.resolve_conflict(
                    internal_lead, crm_lead
                )

                if resolution.action == "update":
                    # Обновляем внутренний лид
                    leads.append(resolution.updated_lead)
                elif resolution.action == "create":
                    # Создаем новый лид
                    leads.append(resolution.updated_lead)
                elif resolution.action == "skip":
                    # Пропускаем
                    continue

            self.audit_logger.log_sync_event(
                "from_crm", connection_id, None, f"{len(leads)} leads", "success"
            )

        except Exception as e:
            self.audit_logger.log_sync_event(
                "from_crm", connection_id, None, "all leads", "failure", error=str(e)
            )

        return leads

    async def sync_single_lead(
        self, lead_data: LeadData, connection_id: UUID
    ) -> Tuple[bool, str]:
        """
        Синхронизация одного лида в обе стороны.
        """
        # Сначала пытаемся синхронизировать в CRM
        success_to_crm, external_id = await self.to_crm(lead_data, connection_id)

        if not success_to_crm:
            return False, ""

        # Обновляем external_id в lead_data
        lead_data.external_id = external_id

        # Затем синхронизируем обратно из CRM (чтобы убедиться в согласованности)
        try:
            crm_lead = await self.adapter.get_lead(external_id)
            internal_lead = self.field_mapper.map_from_crm(crm_lead)

            # Проверяем конфликты
            resolution = self.conflict_resolver.resolve_conflict(
                internal_lead, crm_lead
            )

            if resolution.action == "update":
                # Обновляем внутренний лид
                lead_data.title = resolution.updated_lead.title
                lead_data.company_name = resolution.updated_lead.company_name
                lead_data.deal_value = resolution.updated_lead.deal_value
                lead_data.status = resolution.updated_lead.status
                lead_data.notes = resolution.updated_lead.notes
                lead_data.contact_person = resolution.updated_lead.contact_person
                lead_data.contact_email = resolution.updated_lead.contact_email
                lead_data.contact_phone = resolution.updated_lead.contact_phone
                lead_data.compatibility_score = (
                    resolution.updated_lead.compatibility_score
                )
                lead_data.updated_at = resolution.updated_lead.updated_at
            elif resolution.action == "skip":
                # Ничего не меняем
                pass

        except Exception:
            # Если не удалось получить лид из CRM, продолжаем с тем, что есть
            pass

        return True, external_id
