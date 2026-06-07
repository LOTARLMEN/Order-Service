import asyncio
from asyncio import create_task, run
from typing import Callable

from fastapi import FastAPI
from uvicorn import Config, Server

from app.infrastructure.logging import setup_logging
from app.presentation.api.rest.handlers import handlers_mapping
from app.presentation.api.rest.lifespan import lifespan
from app.presentation.api.rest.v1.controllers import orders
from app.presentation.api.rest.v1.controllers.callback import callback
from app.presentation.api.rest.v1.router import router
from app.presentation.container import PresentationContainer


def build_app(
    container: PresentationContainer,
    lifespan: Callable,
) -> FastAPI:
    setup_logging()
    app = FastAPI(
        lifespan=lifespan,
        title=container.settings()["OrderService"]["SERVICE_NAME"],
    )
    app.include_router(router)
    container.wire(modules=[orders, callback])

    for exc_class, handler in handlers_mapping.items():
        app.add_exception_handler(exc_class, handler)

    return app


async def main():
    presentation_container = PresentationContainer()
    application_container = presentation_container.application_container
    infrastructure_container = application_container.infrastructure_container

    setting = presentation_container.settings()

    app = build_app(
        presentation_container,
        lifespan,
    )

    kafka_producer = infrastructure_container.kafka_producer()
    await kafka_producer.start()

    outbox_worker = presentation_container.outbox_worker()
    outbox_task = create_task(outbox_worker.start())

    shipping_consumer = application_container.shipping_consumer()
    shipping_task = create_task(shipping_consumer.start())

    api_task = create_task(
        Server(
            Config(
                app,
                host=setting["OrderService"]["SERVICE_HOST"],
                port=setting["OrderService"]["SERVICE_PORT"],
            )
        ).serve()
    )

    try:
        await asyncio.gather(api_task, outbox_task, shipping_task)
    finally:
        await kafka_producer.stop()
        await outbox_worker.stop()
        await shipping_consumer.stop()


if __name__ == "__main__":
    run(main())
