class BestiauxError(Exception):
    pass


class NotFoundError(BestiauxError):
    pass


class ForbiddenError(BestiauxError):
    pass


class AuthenticationError(BestiauxError):
    pass


class ConflictError(BestiauxError):
    pass
