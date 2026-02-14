from datetime import datetime, timezone
from typing import List
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.amocrm import AmoCRMAdapter
from src.adapters.base import CRMConnection as CRMConnectionModel
from src.crypto.token_vault import TokenVault
from src.models.orm import CRMConnectionORM
from src.models.schemas import (
    CRMConnectionCreate,
    CRMConnectionResponse,
    CRMType,
    LeadData,
    TokenRefreshRequest,
)
from src.sync.audit_log import AuditLogger
from src.sync.conflict_resolver import ConflictResolutionStrategy
from src.sync.field_mapper import FieldMapper
from src.sync.sync_service import SyncService

log = structlog.get_logger()

router = APIRouter(prefix="/crm", tags=["crm"])


# Зависимости для получения сессии БД и других сервисов
async def get_db():
    # В реальной реализации здесь будет получение асинхронной сессии
    # Для упрощения возвращаем заглушку
    return None


def get_token_vault():
    # В реальной реализации здесь будет получение из конфигурации
    return TokenVault("dummy_secret_key")


def get_sync_service():
    # В реальной реализации здесь будет создание сервиса синхронизации
    return SyncService(
        adapter=None,
        field_mapper=FieldMapper(),
        conflict_resolver=ConflictResolutionStrategy(),
        audit_logger=AuditLogger(),
    )


@router.post(
    "/connections",
    response_model=CRMConnectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_crm_connection(
    connection_data: CRMConnectionCreate,
    db: AsyncSession = Depends(get_db),
    token_vault: TokenVault = Depends(get_token_vault),
):
    """
    Создает новое подключение к CRM.
    """
    try:
        # В реальной реализации здесь будет создание записи в БД
        # Для упрощения возвращаем заглушку

        # Создаем модель подключения
        connection = CRMConnectionORM(
            user_id=UUID("00000000-0000-0000-0000-000000000000"),  # Заглушка
            crm_type=connection_data.crm_type.value,
            account_subdomain=connection_data.account_subdomain,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # В реальной реализации здесь будет сохранение в БД

        return CRMConnectionResponse(
            id=connection.id,
            user_id=connection.user_id,
            crm_type=connection.crm_type,
            account_subdomain=connection.account_subdomain,
            account_id="dummy_account_id",
            expires_at=None,
            is_active=True,
            created_at=connection.created_at,
            updated_at=connection.updated_at,
        )

    except Exception as e:
        log.error("create_crm_connection_error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create CRM connection")


@router.get("/connections", response_model=List[CRMConnectionResponse])
async def list_crm_connections(db: AsyncSession = Depends(get_db)):
    """
    Получает список всех подключений к CRM.
    """
    try:
        # В реальной реализации здесь будет запрос к БД
        # Для упрощения возвращаем заглушку

        return [
            CRMConnectionResponse(
                id=UUID("00000000-0000-0000-0000-000000000001"),
                user_id=UUID("00000000-0000-0000-0000-000000000000"),
                crm_type=CRMType.AMOCRM,
                account_subdomain="example",
                account_id="12345",
                expires_at=datetime.now(timezone.utc),
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        ]

    except Exception as e:
        log.error("list_crm_connections_error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list CRM connections")


@router.post("/leads")
async def create_lead(
    lead_data: LeadData,
    connection_id: UUID,
    db: AsyncSession = Depends(get_db),
    token_vault: TokenVault = Depends(get_token_vault),
    sync_service: SyncService = Depends(get_sync_service),
):
    """
    Создает лид во внутренней системе и синхронизирует его с CRM.
    """
    try:
        # В реальной реализации здесь будет получение подключения из БД
        # Для упрощения используем заглушку

        # Создаем модель подключения
        connection_model = CRMConnectionModel(
            id=connection_id,
            user_id=UUID("00000000-0000-0000-0000-000000000000"),
            crm_type=CRMType.AMOCRM,
            access_token="dummy_access_token",
            refresh_token="dummy_refresh_token",
            expires_at=datetime.now(timezone.utc),
            account_subdomain="example",
            account_id="12345",
        )

        # Создаем адаптер для amoCRM (основной для РФ)
        adapter = AmoCRMAdapter(connection_model, "client_id", "client_secret")

        # Обновляем sync_service с правильным адаптером
        sync_service.adapter = adapter

        # Синхронизируем лид в CRM
        success, external_id = await sync_service.to_crm(lead_data, connection_id)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to create lead in CRM")

        # Обновляем external_id в lead_data
        lead_data.external_id = external_id

        return {"status": "success", "external_id": external_id}

    except Exception as e:
        log.error("create_lead_error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create lead")


@router.put("/leads/{external_id}")
async def update_lead(
    external_id: str,
    lead_data: LeadData,
    connection_id: UUID,
    db: AsyncSession = Depends(get_db),
    token_vault: TokenVault = Depends(get_token_vault),
    sync_service: SyncService = Depends(get_sync_service),
):
    """
    Обновляет лид во внутренней системе и синхронизирует изменения с CRM.
    """
    try:
        # В реальной реализации здесь будет получение подключения из БД
        # Для упрощения используем заглушку

        connection_model = CRMConnectionModel(
            id=connection_id,
            user_id=UUID("00000000-0000-0000-0000-000000000000"),
            crm_type=CRMType.AMOCRM,
            access_token="dummy_access_token",
            refresh_token="dummy_refresh_token",
            expires_at=datetime.now(timezone.utc),
            account_subdomain="example",
            account_id="12345",
        )

        adapter = AmoCRMAdapter(connection_model, "client_id", "client_secret")
        sync_service.adapter = adapter

        # Синхронизируем обновление в CRM
        success, _ = await sync_service.to_crm(lead_data, connection_id)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to update lead in CRM")

        return {"status": "success"}

    except Exception as e:
        log.error("update_lead_error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update lead")


@router.get("/leads/{external_id}", response_model=LeadData)
async def get_lead(
    external_id: str,
    connection_id: UUID,
    db: AsyncSession = Depends(get_db),
    token_vault: TokenVault = Depends(get_token_vault),
    sync_service: SyncService = Depends(get_sync_service),
):
    """
    Получает лид из внутренней системы или синхронизирует его из CRM.
    """
    try:
        # В реальной реализации здесь будет получение лида из БД
        # Для упрощения используем заглушку

        connection_model = CRMConnectionModel(
            id=connection_id,
            user_id=UUID("00000000-0000-0000-0000-000000000000"),
            crm_type=CRMType.AMOCRM,
            access_token="dummy_access_token",
            refresh_token="dummy_refresh_token",
            expires_at=datetime.now(timezone.utc),
            account_subdomain="example",
            account_id="12345",
        )

        adapter = AmoCRMAdapter(connection_model, "client_id", "client_secret")
        sync_service.adapter = adapter

        # Получаем лид из CRM
        crm_lead = await adapter.get_lead(external_id)

        return crm_lead

    except Exception as e:
        log.error("get_lead_error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get lead")


@router.post("/sync/{connection_id}")
async def sync_crm(
    connection_id: UUID,
    db: AsyncSession = Depends(get_db),
    token_vault: TokenVault = Depends(get_token_vault),
    sync_service: SyncService = Depends(get_sync_service),
):
    """
    Запускает синхронизацию с указанной CRM.
    """
    try:
        # В реальной реализации здесь будет получение подключения из БД
        # Для упрощения используем заглушку

        connection_model = CRMConnectionModel(
            id=connection_id,
            user_id=UUID("00000000-0000-0000-0000-000000000000"),
            crm_type=CRMType.AMOCRM,
            access_token="dummy_access_token",
            refresh_token="dummy_refresh_token",
            expires_at=datetime.now(timezone.utc),
            account_subdomain="example",
            account_id="12345",
        )

        adapter = AmoCRMAdapter(connection_model, "client_id", "client_secret")
        sync_service.adapter = adapter

        # Синхронизируем из CRM
        leads = await sync_service.from_crm(connection_id)

        return {"status": "success", "leads_synced": len(leads)}

    except Exception as e:
        log.error("sync_crm_error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to sync CRM")


@router.post("/token/refresh")
async def refresh_token(
    request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
    token_vault: TokenVault = Depends(get_token_vault),
):
    """
    Обновляет токен для подключения к CRM.
    """
    try:
        # В реальной реализации здесь будет получение подключения из БД
        # Для упрощения используем заглушку

        # Декодируем зашифрованный токен
        token_vault.decrypt(request.refresh_token)

        # В реальной реализации здесь будет вызов метода обновления токена у адаптера
        # Для упрощения возвращаем заглушку

        return {
            "status": "success",
            "access_token": "new_access_token",
            "expires_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        log.error("refresh_token_error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to refresh token")
