from zope.interface import Interface

class IEngine(Interface):

    def registerTransform(transform):
        """register a transform

        transform must implements ITransform
        """

    def unregisterTransform(name):
        """ unregister a transform
        name is the name of a registered transform
        """

    def convertTo(mimetype, orig, data=None, object=None, context=None, **kwargs):
        """Convert orig to a given mimetype

        * orig is an encoded string

        * data an optional idatastream object. If None a new datastream will be
        created and returned

        * optional object argument is the object on which is bound the data.
        If present that object will be used by the engine to bound cached data.

        * optional context argument is the object on which the transformation
          was called.

        * additional arguments (kwargs) will be passed to the transformations.

        return an object implementing idatastream or None if no path has been
        found.
        """

    def convert(name, orig, data=None, context=None, **kwargs):
        """run a tranform of a given name on data

        * name is the name of a registered transform

        see convertTo docstring for more info
        """

    def __call__(name, orig, data=None, context=None, **kwargs):
        """run a transform by its name, returning the raw data product

        * name is the name of a registered transform.

        return an encoded string.
        see convert docstring for more info on additional arguments.
        """
