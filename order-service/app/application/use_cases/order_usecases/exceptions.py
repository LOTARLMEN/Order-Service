class OrderFailedCreateException(Exception):
    pass


class OrderFailedUpdateException(Exception):
    pass


class OutboxEventFailedCreateException(Exception):
    pass


class OrderNotFoundException(Exception):
    pass
