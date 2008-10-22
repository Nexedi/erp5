===================================
Portal Transforms'Developper manual
===================================

:Author: Sylvain Thenault
:Contact: syt@logilab.fr
:Date: $Date: 2005-08-19 23:43:41 +0200 (Fre, 19 Aug 2005) $
:Version: $Revision: 1.5 $
:Web site: http://sourceforge.net/projects/archetypes

.. contents::


Tools interfaces
----------------

The MIME types registry
```````````````````````

    class isourceAdapter(Interface):

	def __call__(data, \**kwargs):
	    """convert data to unicode, may take optional kwargs to aid in conversion"""

    class imimetypes_registry(isourceAdapter):

	def classify(data, mimetype=None, filename=None):
	    """return a content type for this data or None
	    None should rarely be returned as application/octet can be
	    used to represent most types.
	    """

	def lookup(mimetypestring):
	    """Lookup for imimetypes object matching mimetypestring.
	    mimetypestring may have an empty minor part or containing a wildcard (*).
	    mimetypestring may be an imimetype object (in this case it will be
	    returned unchanged, else it should be a RFC-2046 name.
	    Return a list of mimetypes objects associated with the RFC-2046 name.
	    Return an empty list if no one is known.
	    """

	def lookupExtension(filename):
	    """ return the mimetypes object associated with the file's extension
	    or None if it is not known.
	    filename maybe a file name like 'content.txt' or an extension like 'rest'
	    """

	def mimetypes():
	    """return all defined mime types, each one implements at least imimetype
	    """

	def list_mimetypes():
	    """return all defined mime types, as string"""



The tranformation tool
``````````````````````

    class iengine(Interface):

	def registerTransform(transform):
	    """register a transform
	    transform must implements itransform
	    """

	def unregisterTransform(name):
	    """ unregister a transform
	    name is the name of a registered transform
	    """

	def convertTo(mimetype, orig, idata=None, \**kwargs):
	    """Convert orig to a given mimetype
	    return an object implementing idatastream or None if not path has been
	    found
	    """

	def convert(name, orig, idata=None, \**kwargs):
	    """run a tranform of a given name on data
	    name is the name of a registered transform
	    return an object implementing idatastream
	    """

	def __call__(name, orig, idata=None, \**kwargs):
	    """run a transform returning the raw data product
	    name is the name of a registered transform
	    return an object implementing idatastream
	    """



Writing a new transformation
----------------------------

Writing a new transform should be an easy task. You only have to follow a
simple interface to do it, but knowing some advanced features and provided
utilities may help to do it quicker... 


Related interfaces
``````````````````

    class itransform(Interface):
	"""A transformation plugin -- tranform data somehow must be threadsafe and stateless"""

        inputs = Attribute("""list of imimetypes (or registered rfc-2046
                              names) this transform accepts as inputs""")

        output = Attribute("output imimetype as instance or rfc-2046 name"")

	def name(self):
	    """return the name of the transform instance"""

	def convert(data, idata, \**kwargs):
	    """convert the data, store the result in idata and return that"""

    class idatastream(Interface):
	"""data stream, is the result of a transform"""

	def setData(self, value):
	    """set the main data produced by a transform, i.e. usually a string"""

	def getData():
	    """provide access to the transformed data object, i.e. usually a string.
	    This data may references subobjects.
	    """

	def setSubObjects(self, objects):
	    """set a dict-like object containing subobjects.
            keys should be object's identifier (e.g. usually a filename) and
	    values object's content.
	    """

	def getSubObjects(self):
	    """return a dict-like object with any optional subobjects associated
	    with the data"""

	def getMetadata():
	    """return a dict-like object with any optional metadata from
	    the transform"""


Important note about encoding
`````````````````````````````

A transform receive data as an encoded string. A priori, no assumption can be
made about the used encoding. Data returned by a transform must use the same
encoding as received data, unless the transform provides a *output_encoding*
attribute indicating the output encoding (for instance this may be usefull for
XSLT based transforms).


Configurable transformation
```````````````````````````

You can make your transformation configurable through the ZMI by setting a
*config* dictionnary on your transform instance or class. Keys are parameter's
name and values parameter's value. Another dictionnary *config_metadata*
describes each parameter. In this mapping, keys are also parameter's name but
values are a tree-uple : (<parameter's type>, <parameter's label>, <parameter's
description>).

Possible types for parameters are :

  :int: field is an integer

  :string: field is a string

  :list: field is a list

  :dict: field is a dictionnary

You can look at the **command** and **xml** transforms for an example of
configurable transform.


Images / sub-objects  management
````````````````````````````````

A transformation may produce some sub-objects, for instance when you convert a
PDF document to HTML. That's the purpose of the setObjects method of
the idatastream interface.


Some utilities
``````````````

Transform utilities may be found in the libtransforms subpackage. You'll find
there the following modules :

*commandtransform*
  provides a base class for external command based transforms. 

*retransform*
  provides a base class for regular expression based transforms. 

*html4zope*
  provides a docutils HTML writer for Zope.

*utils*
  provides some utilities functions. 


Write a test your transform !
`````````````````````````````

Every transform should have its test... And it's easy to write a test for your
transform ! Imagine you have made a transform named "colabeer" which transforms
cola into beer (I let you find MIME type for these content types ;). Basically,
your test file should be :

    from test_transforms import make_tests
    
    tests =('Products.MyTransforms.colabeer', "drink.cola", "drink.beer", None, 0)

    def test_suite():
        return TestSuite([makeSuite(test) for test in make_tests()])

    if __name__=='__main__':
        main(defaultTest='test_suite')



In this example :

- "Products.MyTransforms.colabeer" is the module defining your transform (you
  can also give directly the transform instance).  

- "drink.cola" is the name of the file containing data to give to your transform
  as input. 

- "drink.beer" is the file containing expected transform result (what the getData
  method of idatastream will return).

- Additional arguments (*None* and *0*) are respectivly an optional normalizing
  function to apply to both the transform result and the output file content, and
  the number of subobjects that the transform is expected to produce.

This example supposes your test is in the *tests* directory of PortalTransforms
and your input and output files respectively in *tests/input* and
*tests/output*.