from app.infrastructure.unit_of_work import UnitOfWork


class BaseUseCase:
    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work
