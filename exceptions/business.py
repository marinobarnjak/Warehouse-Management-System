
class BusinnesError(ValueError):
    pass

class NotFoundError(BusinnesError):
    pass

class ValidationError(BusinnesError):
    pass

class ConflictError(BusinnesError):
    pass
