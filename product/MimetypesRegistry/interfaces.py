from Interface import Interface, Attribute

class IMimetype(Interface):
    """Specification for dealing with mimetypes RFC-2046 style"""

#     mimetypes = Attribute("List of mimetypes in the RFC-2046 format")
#     extensions = Attribute("""List of extensions mapped to this
#     mimetype w/o the leading .""")

#     binary = Attribute("""Boolean indicating if the mimetype should be
#     treated as binary (and not human readable)""")

    def name(self):
        """return the Human readable name of the mimetype"""

    def major(self):
        """ return the major part of the RFC-2046 name for this mime type """

    def minor(self):
        """ return the minor part of the RFC-2046 name for this mime type """

    def normalized(self):
        """ return the main RFC-2046 name for this mime type

        e.g. if this object has names ('text/restructured', 'text-x-rst')
        then self.normalized() will always return the first form.
        """

class IClassifier(Interface):
    """Optional mixin interface for imimetype, code to test if the
    mimetype is present in data
    """
    def classify(data):
        """ boolean indicating if the data fits the mimetype"""


class ISourceAdapter(Interface):

    def __call__(data, **kwargs):
        """convert data to unicode, may take optional kwargs to aid in
        conversion"""


class IMimetypesRegistry(Interface):

    def classify(data, mimetype=None, filename=None):
        """return a content type for this data or None
        None should rarely be returned as application/octet can be
        used to represent most types
        """

    def lookup(mimetypestring):
        """Lookup for imimetypes object matching mimetypestring

        mimetypestring may have an empty minor part or containing a wildcard (*)
        mimetypestring may be an imimetype object (in this case it will be
        returned unchanged, else it should be a RFC-2046 name

        return a list of mimetypes objects associated with the RFC-2046 name
        return an empty list if no one is known.
        """

    def lookupExtension(filename):
        """ return the mimetypes object associated with the file's extension
        return None if it is not known.

        filename maybe a file name like 'content.txt' or an extension like 'rest'
        """

    def mimetypes():
        """return all defined mime types, each one implements at least imimetype
        """

    def list_mimetypes():
        """return all defined mime types, as string"""
