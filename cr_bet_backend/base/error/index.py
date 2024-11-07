from .system import SystemError
from .response import HttpResponseError


class BaseError(SystemError, HttpResponseError):
    pass
