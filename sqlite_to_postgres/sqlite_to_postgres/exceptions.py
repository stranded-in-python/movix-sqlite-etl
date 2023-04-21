class Error(BaseException):
    ...


class DataInconsistentError(Error):
    ...


class ConnectionFailedError(Error):
    ...


class InputError(Error):
    ...
