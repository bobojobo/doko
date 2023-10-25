class MissingEnvFile(Exception):
    """Incomplete or nonexistent .env file."""


class NoDatabaseConnection(Exception):
    """Couldn't connect to database."""


class InvalidUsername(Exception):
    pass


class InvalidPassword(Exception):
    pass


class AlreadyAuthenticated(Exception):
    pass
