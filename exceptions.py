class AuthException(Exception):
    pass


class BuildFailedException(Exception):
    def __init__(self, stage='building', msg=None, status_code=None,
                 testrun_id=None):
        super().__init__(msg)
        self.testrun_id = testrun_id
        self.msg = msg
        self.stage = stage
        self.status_code = status_code

    def __str__(self):
        return f'{self.msg}'


class RunFailedException(BuildFailedException):
    def __init__(self, *args, **kwargs):
        super().__init__('running', *args, **kwargs)


class NoBranchesException(Exception):
    pass


class FilestoreWriteError(Exception):
    pass


class FilestoreReadError(Exception):
    pass


class InvalidTemplateException(Exception):
    pass


class ServerConnectionFailed(Exception):
    pass

