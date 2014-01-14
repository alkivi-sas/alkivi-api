class ObjectNotFound(Exception):
    """Unable to find a object
    """

class MultipleObjectFound(Exception):
    """Multiple object are found
    """

class MissingParameter(KeyError):
    """One parameter is missing
    """

class InvalidParameter(KeyError):
    """One parameter is not correct
    """


