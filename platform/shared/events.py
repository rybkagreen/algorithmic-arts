"""Shared Kafka event handling utilities for all services."""

import json
import logging
from typing import Any, Dict, Optional, Union
from uuid import UUID

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DomainEvent(BaseModel):
    """Base domain event structure."""
    event_type: str
    aggregate_id: str
    payload: Dict[str, Any]
    occurred_at: str  # ISO format datetime string


class KafkaEventProducer:
    """Base Kafka producer with retry logic and error handling."""
    
    def __init__(
        self,
        bootstrap_servers: str,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        topic_prefix: str = ""
    ):
        self.bootstrap_servers = bootstrap_servers
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.topic_prefix = topic_prefix
        self.producer: Optional[AIOKafkaProducer] = None
    
    async def start(self) -> None:
        """Start the Kafka producer."""
        if not self.producer:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                enable_idempotence=True,
                request_timeout_ms=30000,
                max_in_flight_requests_per_connection=5
            )
            await self.producer.start()
            logger.info("Kafka producer started", bootstrap_servers=self.bootstrap_servers)
    
    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if self.producer:
            await self.producer.stop()
            self.producer = None
            logger.info("Kafka producer stopped")
    
    async def produce_event(
        self,
        event: Union[DomainEvent, Dict[str, Any]],
        topic_suffix: str = "",
        key: Optional[str] = None
    ) -> None:
        """Produce a domain event to Kafka with retry logic."""
        if isinstance(event, DomainEvent):
            event_dict = event.model_dump()
        else:
            event_dict = event
        
        # Build topic name
        topic = f"{self.topic_prefix}{topic_suffix}" if self.topic_prefix else topic_suffix
        
        # Ensure we have a valid topic
        if not topic:
            raise ValueError("Topic suffix is required when no topic prefix is set")
        
        # Convert UUID to string if needed
        if isinstance(key, UUID):
            key = str(key)
        
        # Retry logic
        for attempt in range(self.max_retries + 1):
            try:
                if not self.producer:
                    await self.start()
                
                # Send message
                await self.producer.send(
                    topic=topic,
                    value=event_dict,
                    key=key.encode('utf-8') if key else None
                )
                
                logger.debug("Event produced", 
                           event_type=event_dict.get('event_type'), 
                           topic=topic, 
                           attempt=attempt + 1)
                return
                
            except Exception as e:
                logger.error("Failed to produce event",
                           event_type=event_dict.get('event_type'),
                           topic=topic,
                           attempt=attempt + 1,
                           error=str(e))
                
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise e


class KafkaEventConsumer:
    """Base Kafka consumer with retry logic and error handling."""
    
    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topics: list,
        value_deserializer=None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topics = topics
        self.value_deserializer = value_deserializer or (lambda v: json.loads(v.decode('utf-8')))
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.consumer: Optional[AIOKafkaConsumer] = None
    
    async def start(self) -> None:
        """Start the Kafka consumer."""
        if not self.consumer:
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=self.value_deserializer,
                enable_auto_commit=True,
                auto_offset_reset="earliest",
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            await self.consumer.start()
            logger.info("Kafka consumer started", 
                       group_id=self.group_id,
                       topics=self.topics)
    
    async def stop(self) -> None:
        """Stop the Kafka consumer."""
        if self.consumer:
            await self.consumer.stop()
            self.consumer = None
            logger.info("Kafka consumer stopped")
    
    async def consume_events(self, handler_func):
        """Consume events and handle them with the provided handler function."""
        if not self.consumer:
            await self.start()
        
        try:
            async for msg in self.consumer:
                try:
                    # Process message
                    await handler_func(msg.value, msg.key)
                    
                except Exception as e:
                    logger.error("Error processing message",
                               topic=msg.topic,
                               partition=msg.partition,
                               offset=msg.offset,
                               error=str(e))
                    # In production, this would go to a dead-letter queue
                    # For now, just log and continue
                    continue
                    
        except Exception as e:
            logger.error("Consumer error", error=str(e))
            raise