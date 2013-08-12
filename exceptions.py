class ObjectNotFound(Exception):
    """
    When unable to find a object
    """

class NoUniqueObjectFound(Exception):
    """
    When multiple object are found
    """

class MissingParameter(KeyError):
    """
    When one parameter is missing
    """

class InvalidParameter(KeyError):
    """
    When one parameter is not correct
    """


