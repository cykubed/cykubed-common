class AuthException(Exception):
    pass


class BuildFailedException(Exception):
    def __init__(self, msg=None, status_code=None):
        super().__init__(msg)
        self.msg = msg
        self.status_code = status_code

    def __str__(self):
        return f'{self.msg}'


class NoBranchesException(Exception):
    pass


class FilestoreWriteError(Exception):
    pass


class FilestoreReadError(Exception):
    pass


class InvalidTemplateException(Exception):
    pass


