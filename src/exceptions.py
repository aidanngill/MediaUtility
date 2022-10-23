class BotException(Exception):
    """Base exception."""

    pass


class InvalidLinkException(BotException):
    """Provided link was not a valid URL."""

    pass
