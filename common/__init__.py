class Singleton(object):
 
    '''
    Singelton class
    '''
 
    def __init__(self, decorated):
        self._decorated = decorated
 
    def instance(self, *args, **kwargs):
        try:
            return self._instance
 
        except AttributeError:
            self._instance = self._decorated(*args, **kwargs)
            return self._instance
 
    def __call__(self, *args, **kwargs):
        raise TypeError('Singletons must be accessed through the `Instance` method.')
