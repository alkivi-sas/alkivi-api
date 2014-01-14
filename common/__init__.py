"""Several helpers used to make alkivi life easier
"""
class Singleton(object):
    """Class to handle singleton
    """
 
    def __init__(self, decorated):
        self._decorated = decorated
        self._instance = None
 
    def instance(self, *args, **kwargs):
        """Method to get the instance of a singleton

        Create the instance if not used yet or restore it
        """
        if self._instance is None:
            self._instance = self._decorated(*args, **kwargs)

        return self._instance
 
    def __call__(self, *args, **kwargs):
        raise TypeError('Singletons must be accessed through instance().')
