from app.application.interfaces import IUnitOfWork


class BaseUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self._unit_of_work = unit_of_work
