from typing import Any, Dict

from ..adapters.base import LeadData


class FieldMapper:
    """
    Маппинг полей между внутренней системой и CRM.
    """

    def __init__(self):
        # Сопоставление полей для разных CRM
        self.crm_field_mappings = {
            "amocrm": {
                "title": "name",
                "company_name": "COMPANY_NAME",
                "deal_value": "price",
                "status": "status_id",
                "notes": "DESCRIPTION",
                "compatibility_score": "COMPATIBILITY_SCORE",
            },
            "bitrix24": {
                "title": "TITLE",
                "company_name": "COMPANY_TITLE",
                "deal_value": "OPPORTUNITY",
                "status": "STATUS_ID",
                "notes": "COMMENTS",
                "compatibility_score": "UF_CRM_COMPAT",
            },
            "megaplan": {
                "title": "name",
                "company_name": "companyName",
                "deal_value": "price",
                "status": "status",
                "notes": "description",
                "compatibility_score": "compatibility_score",
            },
            "salesforce": {
                "title": "FirstName",
                "company_name": "Company",
                "deal_value": "AnnualRevenue",
                "status": "Status",
                "notes": "Description",
                "compatibility_score": "Custom_Compatibility_Score__c",
            },
            "hubspot": {
                "title": "firstname",
                "company_name": "company",
                "deal_value": "dealvalue",
                "status": "hs_lead_status",
                "notes": "description",
                "compatibility_score": "custom_compatibility_score",
            },
            "pipedrive": {
                "title": "title",
                "company_name": "org_name",
                "deal_value": "value",
                "status": "status",
                "notes": "notes",
                "compatibility_score": "compatibility_score",
            },
        }

    def map_to_crm_updates(
        self, internal_lead: "LeadData", crm_lead: "LeadData"
    ) -> Dict[str, Any]:
        """
        Преобразует изменения из внутреннего формата в формат CRM.
        """
        updates = {}

        # Определяем тип CRM по external_id или другим признакам
        crm_type = self._detect_crm_type(crm_lead)

        if crm_type in self.crm_field_mappings:
            mapping = self.crm_field_mappings[crm_type]

            # Сопоставляем поля, которые изменились
            if internal_lead.title != crm_lead.title:
                updates[mapping["title"]] = internal_lead.title

            if internal_lead.company_name != crm_lead.company_name:
                updates[mapping["company_name"]] = internal_lead.company_name

            if internal_lead.deal_value != crm_lead.deal_value:
                updates[mapping["deal_value"]] = internal_lead.deal_value

            if internal_lead.status != crm_lead.status:
                updates[mapping["status"]] = internal_lead.status

            if internal_lead.notes != crm_lead.notes:
                updates[mapping["notes"]] = internal_lead.notes

            if (
                abs(internal_lead.compatibility_score - crm_lead.compatibility_score)
                > 0.001
            ):
                updates[mapping["compatibility_score"]] = round(
                    internal_lead.compatibility_score, 4
                )

        return updates

    def map_from_crm(self, crm_lead: "LeadData") -> "LeadData":
        """
        Преобразует лид из CRM во внутренний формат.
        """
        # Определяем тип CRM по external_id или другим признакам
        self._detect_crm_type(crm_lead)

        # Создаем новый внутренний лид
        internal_lead = LeadData(
            title=crm_lead.title,
            company_name=crm_lead.company_name,
            contact_person=crm_lead.contact_person,
            contact_email=crm_lead.contact_email,
            contact_phone=crm_lead.contact_phone,
            deal_value=crm_lead.deal_value,
            compatibility_score=crm_lead.compatibility_score,
            partnership_id=crm_lead.partnership_id,
            status=crm_lead.status,
            notes=crm_lead.notes,
            external_id=crm_lead.external_id,
            created_at=crm_lead.created_at,
            updated_at=crm_lead.updated_at,
        )

        return internal_lead

    def _detect_crm_type(self, lead: "LeadData") -> str:
        """
        Определяет тип CRM по внешнему ID или другим признакам.
        """
        if lead.external_id and lead.external_id.startswith("AMO-"):
            return "amocrm"
        elif lead.external_id and lead.external_id.startswith("BX-"):
            return "bitrix24"
        elif lead.external_id and lead.external_id.startswith("MP-"):
            return "megaplan"
        elif lead.external_id and lead.external_id.startswith("SF-"):
            return "salesforce"
        elif lead.external_id and lead.external_id.startswith("HS-"):
            return "hubspot"
        elif lead.external_id and lead.external_id.startswith("PD-"):
            return "pipedrive"
        else:
            # По умолчанию используем amocrm (основной для РФ)
            return "amocrm"
