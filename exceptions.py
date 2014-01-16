class ObjectNotFound(Exception):
    """Unable to find a object
    """

class MultipleObjectFound(Exception):
    """Multiple object are found
    """

class MissingParameter(KeyError):
    """One parameter is missing
    """
    def __init__(self, *args, **kwargs):

        if 'parameter' in kwargs:
            self.parameter = kwargs['parameter']
        else:
            self.parameter = args[0]

        super(MissingParameter, self).__init__(*args, **kwargs)

    def __str__(self):
        return 'Parameter %s is missing' % self.parameter

class InvalidParameter(KeyError):
    """One parameter is not correct
    """


