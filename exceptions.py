class AuthException(Exception):
    pass


class BuildFailedException(Exception):
    pass


class NoBranchesException(Exception):
    pass


class MongoConnectionException(Exception):
    pass


class FilestoreWriteError(Exception):
    pass


class FilestoreReadError(Exception):
    pass
