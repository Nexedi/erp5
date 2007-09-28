import os

from Acquisition import Explicit
from OFS.SimpleItem import Item
from AccessControl import ClassSecurityInfo
from Globals import Persistent, InitializeClass

from Products.CMFCore.permissions import ManagePortal
from Products.MimetypesRegistry.interfaces import IMimetype
from Products.MimetypesRegistry.common import MimeTypeException


class MimeTypeItem(Persistent, Explicit, Item):
    security = ClassSecurityInfo()
    __implements__ = (IMimetype,)

    extensions = ()
    globs = ()

    def __init__(self, name='', mimetypes=None, extensions=None,
                 binary=None, icon_path='', globs=None):
        if name:
            self.__name__ = self.id = name
        if mimetypes is not None:
            self.mimetypes = mimetypes
        if extensions is not None:
            self.extensions = extensions
        if binary is not None:
            self.binary = binary
        if globs is not None:
            self.globs = globs
        self.icon_path = icon_path or guess_icon_path(self)

    def __str__(self):
        return self.normalized()

    def __repr__(self):
        return "<mimetype %s>" % self.mimetypes[0]

    def __cmp__(self, other):
        try:
            if isinstance(other, mimetype):
                other = other.normalized()
        except:
            pass
        return not (other in self.mimetypes)

    def __hash__(self):
        return hash(self.name())

    security.declarePublic('name')
    def name(self):
        """ The name of this object """
        return self.__name__

    security.declarePublic('major')
    def major(self):
        """ return the major part of the RFC-2046 name for this mime type """
        return self.normalized().split('/', 1)[0]

    security.declarePublic('minor')
    def minor(self):
        """ return the minor part of the RFC-2046 name for this mime type """
        return self.normalized().split('/', 1)[1]

    security.declarePublic('normalized')
    def normalized(self):
        """ return the main RFC-2046 name for this mime type

        e.g. if this object has names ('text/restructured', 'text-x-rst')
        then self.normalized() will always return the first form.
        """
        return self.mimetypes[0]

    security.declareProtected(ManagePortal, 'edit')
    def edit(self, name, mimetypes, extensions, icon_path,
             binary=0, globs=None, REQUEST=None):
        """edit this mime type"""
        # if mimetypes and extensions are string instead of lists,
        # split them on new lines
        if isinstance(mimetypes, basestring):
            mimetypes = [mts.strip() for mts in mimetypes.split('\n')
                         if mts.strip()]
        if isinstance(extensions, basestring):
            extensions = [mts.strip() for mts in extensions.split('\n')
                          if mts.strip()]
        if isinstance(globs, basestring):
            globs = [glob.strip() for glob in globs.split('\n')
                     if glob.strip()]
        self.__name__ = self.id = name
        self.mimetypes = mimetypes
        self.globs = globs
        self.extensions = extensions
        self.binary = binary
        self.icon_path = icon_path
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

InitializeClass(MimeTypeItem)


ICONS_DIR = os.path.join(os.path.dirname(__file__), 'skins', 'mimetypes_icons')

def guess_icon_path(mimetype, icons_dir=ICONS_DIR, icon_ext='png'):
    if mimetype.extensions:
        for ext in mimetype.extensions:
            icon_path = '%s.%s' % (ext, icon_ext)
            if os.path.exists(os.path.join(icons_dir, icon_path)):
                return icon_path
    icon_path = '%s.png' % mimetype.major()
    if os.path.exists(os.path.join(icons_dir, icon_path)):
        return icon_path
    return 'unknown.png'
