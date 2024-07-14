class BotException(Exception):
    """Base exception."""



class InvalidLinkException(BotException):
    """Provided link was not a valid URL."""

