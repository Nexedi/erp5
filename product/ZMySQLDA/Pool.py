from Queue import Queue, Full, Empty

class Pool(Queue):

    """Manage a fixed-size pool of reusable, identical objects."""
    
    def __init__(self, constructor, poolsize=5):
        Queue.__init__(self, poolsize)
        self.constructor = constructor

    def get(self, block=1):
        """Get an object from the pool or a new one if empty."""
        try:
            return self.empty() and self.constructor() or Queue.get(self, block)
        except Empty:
            return self.constructor()
        
    def put(self, obj, block=1):
        """Put an object into the pool if it is not full. The caller must
        not use the object after this."""
        try:
            return self.full() and None or Queue.put(self, obj, block)
        except Full:
            pass


class Constructor:

    """Returns a constructor that returns apply(function, args, kwargs)
    when called."""

    def __init__(self, function, *args, **kwargs):
        self.f = function
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return apply(self.f, self.args, self.kwargs)

