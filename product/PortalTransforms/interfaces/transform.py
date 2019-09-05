from zope.interface import Interface

class ITransform(Interface):
    """A transformation plugin -- tranform data somehow
    must be threadsafe and stateless"""

    def name(self):
        """return the name of the transform instance"""

    def convert(data, idata, filename=None, **kwargs):
        """convert the data, store the result in idata and return that

        optional argument filename may give the original file name of received data

        additional arguments given to engine's convert, convertTo or __call__ are
        passed back to the transform

        The object on which the translation was invoked is available as context
        (default: None)
        """
