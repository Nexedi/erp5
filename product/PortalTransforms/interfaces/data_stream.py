from zope.interface import Interface

class IDataStream(Interface):
    """data stream, is the result of a transform"""

    def setData(value):
        """set the main data produced by a transform, i.e. usually a string"""

    def getData():
        """provide access to the transformed data object, i.e. usually a string.
        This data may references subobjects.
        """

    def setSubObjects(objects):
        """set a dict-like object containing subobjects.
        keys should be object's identifier (e.g. usually a filename) and
        values object's content.
        """

    def getSubObjects():
        """return a dict-like object with any optional subobjects associated
        with the data"""

    def getMetadata():
        """return a dict-like object with any optional metadata from
        the transform
        You can modify the returned dictionnary to add/change metadata
        """

    def isCacheable():
        """Return a bool which indicates wether the result should be cached

        Default is true
        """

    def setCachable(value):
        """Set cacheable flag to yes or no
        """
