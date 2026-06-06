from asyncio import create_task, run
from typing import Callable

from fastapi import FastAPI
from uvicorn import Config, Server

from app.infrastructure.logging import setup_logging
from app.presentation.api.rest.handlers import handlers_mapping
from app.presentation.api.rest.lifespan import lifespan
from app.presentation.api.rest.v1.controllers import callback, orders
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

    setting = presentation_container.settings()

    app = build_app(
        presentation_container,
        lifespan,
    )

    api_task = create_task(
        Server(
            Config(
                app,
                host=setting["OrderService"]["SERVICE_HOST"],
                port=setting["OrderService"]["SERVICE_PORT"],
            )
        ).serve()
    )

    await api_task


if __name__ == "__main__":
    run(main())
