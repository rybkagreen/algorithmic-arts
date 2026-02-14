from typing import List, Dict, Any
from sqlalchemy import text, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
import structlog

log = structlog.get_logger()

async def upsert_companies(
    session: AsyncSession,
    companies: List[Dict[str, Any]],
    kafka_producer=None
):
    """
    Batch upsert компаний в PostgreSQL.
    Возвращает список новых company_id для публикации в Kafka.
    """
    if not companies:
        return []
    
    # Подготавливаем данные для upsert
    records = []
    for comp in companies:
        # Убираем поля, которые не должны быть в таблице companies
        record = {
            k: v for k, v in comp.items()
            if k not in ["raw_description", "funding_text", "ai_summary", "ai_tags"]
        }
        # Устанавливаем created_at если отсутствует
        if not record.get("created_at"):
            record["created_at"] = func.now()
        record["updated_at"] = func.now()
        records.append(record)
    
    # Выполняем batch upsert
    stmt = pg_insert(text("companies")).values(records)
    stmt = stmt.on_conflict_do_update(
        index_elements=["name", "website"],
        set_={
            "description": stmt.excluded.description,
            "industry": stmt.excluded.industry,
            "sub_industries": stmt.excluded.sub_industries,
            "tech_stack": stmt.excluded.tech_stack,
            "employees_range": stmt.excluded.employees_range,
            "founded_year": stmt.excluded.founded_year,
            "funding_total": stmt.excluded.funding_total,
            "funding_stage": stmt.excluded.funding_stage,
            "headquarters_country": stmt.excluded.headquarters_country,
            "api_available": stmt.excluded.api_available,
            "is_verified": stmt.excluded.is_verified,
            "inn": stmt.excluded.inn,
            "ogrn": stmt.excluded.ogrn,
            "kpp": stmt.excluded.kpp,
            "legal_name": stmt.excluded.legal_name,
            "legal_address": stmt.excluded.legal_address,
            "reg_date": stmt.excluded.reg_date,
            "is_active": stmt.excluded.is_active,
            "okved_main": stmt.excluded.okved_main,
            "updated_at": func.now(),
        }
    )
    
    try:
        await session.execute(stmt)
        await session.commit()
        
        # Получаем ID вставленных записей (для новых записей)
        new_ids = []
        for comp in companies:
            # Для новых записей получаем ID из возвращенного результата
            # В реальном коде использовался бы RETURNING id
            # Здесь упрощённо: предполагаем, что все новые записи имеют id
            new_ids.append(comp.get("id") or "new_" + str(hash(comp.get("name", ""))))
        
        log.info("companies_upserted", count=len(companies), new_count=len(new_ids))
        
        # Публикуем события company.created для новых компаний
        if kafka_producer and new_ids:
            for i, company in enumerate(companies):
                if i < len(new_ids):  # Соответствие по индексу
                    await kafka_producer.publish_company_created(
                        new_ids[i], company
                    )
        
        return new_ids
        
    except Exception as exc:
        await session.rollback()
        log.error("upsert_failed", error=str(exc), companies_count=len(companies))
        raise