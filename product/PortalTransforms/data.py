from Products.PortalTransforms.interfaces import idatastream

class datastream:
    """A transformation datastream packet"""
    __implements__ = idatastream
    __slots__ = ('name', '_data', '_metadata')

    def __init__(self, name):
        self.__name__ = name
        self._data = ''
        self._metadata = {}
        self._objects = {}
        self._cacheable = 1

    def __str__(self):
        return self.getData()

    def name(self):
        return self.__name__

    def setData(self, value):
        """set the main data produced by a transform, i.e. usually a string"""
        self._data = value

    def getData(self):
        """provide access to the transformed data object, i.e. usually a string.
        This data may references subobjects.
        """
        if callable(self._data):
            data = self._data()
        else:
            data = self._data
        return data

    def setSubObjects(self, objects):
        """set a dict-like object containing subobjects.
        keys should be object's identifier (e.g. usually a filename) and
        values object's content.
        """
        self._objects = objects

    def getSubObjects(self):
        """return a dict-like object with any optional subobjects associated
        with the data"""
        return self._objects

    def getMetadata(self):
        """return a dict-like object with any optional metadata from
        the transform"""
        return self._metadata
    
    def isCacheable(self):
        """Return a bool which indicates wether the result should be cached
        
        Default is true
        """
        return self._cacheable
    
    def setCacheable(self, value):
        """Set cacheable flag to yes or no
        """
        self._cacheable = not not value

    #data = property('getData', 'setData', None, """idata.data""")

    #metadata = property('getMetadata', 'setMetadata', None,
    #"""idata.metadata""")
