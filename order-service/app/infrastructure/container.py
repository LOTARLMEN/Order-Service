from typing import Callable

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.services.capashino_services.catalog import CatalogServiceClient
from app.infrastructure.services.kafka.producer.producer import KafkaProducerService
from app.infrastructure.unit_of_work import UnitOfWork


class InfrastructureContainer(containers.DeclarativeContainer):
    settings = providers.Configuration()
    async_engine = providers.Singleton[AsyncEngine](
        create_async_engine,
        settings.Database.URL,
    )
    session_factory: Callable[..., AsyncSession] = providers.Factory(
        sessionmaker, async_engine, expire_on_commit=False, class_=AsyncSession
    )
    unit_of_work = providers.Singleton[UnitOfWork](
        UnitOfWork, session_factory=session_factory
    )
    kafka_producer = providers.Singleton[KafkaProducerService](
        KafkaProducerService,
        url=settings.Kafka.BOOTSTRAP_SERVERS,
    )
    catalog_service = providers.Singleton[CatalogServiceClient](CatalogServiceClient)
