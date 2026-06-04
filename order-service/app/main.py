from asyncio import create_task, run
from typing import Callable

from app.presentation.api.rest.lifespan import lifespan
from app.presentation.api.rest.v1.controllers import callback, orders
from app.presentation.api.rest.v1.router import router as orders_router
from app.presentation.container import PresentationContainer
from fastapi import FastAPI
from uvicorn import Config, Server


def build_app(
    container: PresentationContainer,
    lifespan: Callable,
) -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        title=container.settings.OrderService.SERVICE_NAME,
    )
    app.include_router(orders_router)
    container.wire(modules=[orders, callback])
    return app


async def main():
    presentation_container = PresentationContainer()
    setting = presentation_container.settings

    app = build_app(
        presentation_container,
        lifespan,
    )

    api_task = create_task(
        Server(
            Config(
                app,
                host=setting.OrderService.SERVICE_HOST,
                port=setting.OrderService.SERVICE_PORT,
            )
        ).serve()
    )

    await api_task


if __name__ == "__main__":
    run(main())
