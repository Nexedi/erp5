import os
import re
import fnmatch
from types import UnicodeType

from OFS.Folder import Folder
from Globals import InitializeClass
from Acquisition import aq_parent
from Acquisition import aq_base
from Globals import PersistentMapping
from AccessControl import ClassSecurityInfo
from BTrees.OOBTree import OOBTree
from Products.CMFCore.permissions import ManagePortal

from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.utils import UniqueObject
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.MimetypesRegistry.interfaces import ISourceAdapter
from Products.MimetypesRegistry.interfaces import IMimetypesRegistry
from Products.MimetypesRegistry.interfaces import IMimetype
from Products.MimetypesRegistry.interfaces import IClassifier
from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem
from Products.MimetypesRegistry.mime_types import initialize
from Products.MimetypesRegistry.mime_types import magic
from Products.MimetypesRegistry.common import log
from Products.MimetypesRegistry.common import MimeTypeException
from Products.MimetypesRegistry.common import STRING_TYPES
from Products.MimetypesRegistry.common import _www
from Products.MimetypesRegistry.encoding import guess_encoding
from Products.MimetypesRegistry.common import log

try:
    from zope.contenttype import guess_content_type
except ImportError: # BBB: Zope < 2.10
    try:
        from zope.app.content_types import guess_content_type
    except ImportError: # BBB: Zope < 2.9
        from OFS.content_types import guess_content_type

suffix_map = {
    'tgz': '.tar.gz',
    'taz': '.tar.gz',
    'tz': '.tar.gz',
    }

encodings_map = {
    'gz': 'gzip',
    'Z': 'compress',
    }

class MimeTypesRegistry(UniqueObject, ActionProviderBase, Folder):
    """Mimetype registry that deals with
    a) registering types
    b) wildcarding of rfc-2046 types
    c) classifying data into a given type
    """

    __implements__ = (IMimetypesRegistry, ISourceAdapter)

    id        = 'mimetypes_registry'
    meta_type = 'MimeTypes Registry'
    isPrincipiaFolderish = 1 # Show up in the ZMI

    meta_types = all_meta_types = (
        { 'name'   : 'MimeType',
          'action' : 'manage_addMimeTypeForm'},
        )

    manage_options = (
        ( { 'label'   : 'MimeTypes',
            'action' : 'manage_main'},) +
        Folder.manage_options[2:]
        )

    manage_addMimeTypeForm = PageTemplateFile('addMimeType', _www)
    manage_main = PageTemplateFile('listMimeTypes', _www)
    manage_editMimeTypeForm = PageTemplateFile('editMimeType', _www)

    security = ClassSecurityInfo()

    # FIXME
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self,):
        self.encodings_map = encodings_map.copy()
        self.suffix_map = suffix_map.copy()
        # Major key -> minor IMimetype objects
        self._mimetypes  = PersistentMapping()
        # ext -> IMimetype mapping
        self.extensions = PersistentMapping()
        # glob -> (regex, mimetype) mapping
        self.globs = OOBTree()
        self.manage_addProperty('defaultMimetype', 'text/plain', 'string')
        self.manage_addProperty('unicodePolicies', 'strict ignore replace',
                                'tokens')
        self.manage_addProperty('unicodePolicy', 'unicodePolicies', 'selection')
        self.manage_addProperty('fallbackEncoding', 'latin1', 'string')

        # initialize mime types
        initialize(self)
        self._new_style_mtr = 1

    security.declareProtected(ManagePortal, 'register')
    def register(self, mimetype):
        """ Register a new mimetype

        mimetype must implement IMimetype
        """
        mimetype = aq_base(mimetype)
        assert IMimetype.isImplementedBy(mimetype)
        for t in mimetype.mimetypes:
            self.register_mimetype(t, mimetype)
        for extension in mimetype.extensions:
            self.register_extension(extension, mimetype)
        for glob in mimetype.globs:
            self.register_glob(glob, mimetype)

    security.declareProtected(ManagePortal, 'register_mimetype')
    def register_mimetype(self, mt, mimetype):
        major, minor = split(mt)
        if not major or not minor or minor == '*':
            raise MimeTypeException('Can\'t register mime type %s' % mt)
        group = self._mimetypes.setdefault(major, PersistentMapping())
        if group.has_key(minor):
            if group.get(minor) != mimetype:
                log('Warning: redefining mime type %s (%s)' % (
                    mt, mimetype.__class__))
        group[minor] = mimetype

    security.declareProtected(ManagePortal, 'register_extension')
    def register_extension(self, extension, mimetype):
        """ Associate a file's extension to a IMimetype

        extension is a string representing a file extension (not
        prefixed by a dot) mimetype must implement IMimetype
        """
        mimetype = aq_base(mimetype)
        if self.extensions.has_key(extension):
            if self.extensions.get(extension) != mimetype:
                log('Warning: redefining extension %s from %s to %s' % (
                    extension, self.extensions[extension], mimetype))
        # we don't validate fmt yet, but its ["txt", "html"]
        self.extensions[extension] = mimetype

    security.declareProtected(ManagePortal, 'register_glob')
    def register_glob(self, glob, mimetype):
        """ Associate a glob to a IMimetype

        glob is a shell-like glob that will be translated to a regex
        to match against whole filename.
        mimetype must implement IMimetype.
        """
        globs = getattr(self, 'globs', None)
        if globs is None:
            self.globs = globs = OOBTree()
        mimetype = aq_base(mimetype)
        existing = globs.get(glob)
        if existing is not None:
            regex, mt = existing
            if mt != mimetype:
                log('Warning: redefining glob %s from %s to %s' % (
                    glob, mt, mimetype))
        # we don't validate fmt yet, but its ["txt", "html"]
        pattern = re.compile(fnmatch.translate(glob))
        globs[glob] = (pattern, mimetype)

    security.declareProtected(ManagePortal, 'unregister')
    def unregister(self, mimetype):
        """ Unregister a new mimetype

        mimetype must implement IMimetype
        """
        assert IMimetype.isImplementedBy(mimetype)
        for t in mimetype.mimetypes:
            major, minor = split(t)
            group = self._mimetypes.get(major, {})
            if group.get(minor) == mimetype:
                del group[minor]
        for e in mimetype.extensions:
            if self.extensions.get(e) == mimetype:
                del self.extensions[e]
        globs = getattr(self, 'globs', None)
        if globs is not None:
            for glob in mimetype.globs:
                existing = globs.get(glob)
                if existing is None:
                    continue
                regex, mt = existing
                if mt == mimetype:
                    del globs[glob]

    security.declarePublic('mimetypes')
    def mimetypes(self):
        """Return all defined mime types, each one implements at least
        IMimetype
        """
        res = {}
        for g in self._mimetypes.values():
            for mt in g.values():
                res[mt] =1
        return [aq_base(mtitem) for mtitem in res.keys()]


    security.declarePublic('list_mimetypes')
    def list_mimetypes(self):
        """Return all defined mime types, as string"""
        return [str(mt) for mt in self.mimetypes()]

    security.declarePublic('lookup')
    def lookup(self, mimetypestring):
        """Lookup for IMimetypes object matching mimetypestring

        mimetypestring may have an empty minor part or containing a
        wildcard (*) mimetypestring may and IMimetype object (in this
        case it will be returned unchanged

        Return a list of mimetypes objects associated with the
        RFC-2046 name return an empty list if no one is known.
        """
        if IMimetype.isImplementedBy(mimetypestring):
            return (aq_base(mimetypestring), )
        __traceback_info__ = (repr(mimetypestring), str(mimetypestring))
        major, minor = split(str(mimetypestring))
        group = self._mimetypes.get(major, {})
        if not minor or minor == '*':
            res = group.values()
        else:
            res = group.get(minor)
            if res:
                res = (res,)
            else:
                return ()
        return tuple([aq_base(mtitem) for mtitem in res])

    security.declarePublic('lookupExtension')
    def lookupExtension(self, filename):
        """Lookup for IMimetypes object matching filename

        Filename maybe a file name like 'content.txt' or an extension
        like 'rest'

        Return an IMimetype object associated with the file's
        extension or None
        """
        if filename.find('.') != -1:
            base, ext = os.path.splitext(filename)
            ext = ext[1:] # remove the dot
            while self.suffix_map.has_key(ext):
                base, ext = os.path.splitext(base + self.suffix_map[ext])
                ext = ext[1:] # remove the dot
        else:
            ext = filename
            base = None

        # XXX This code below make no sense and may break because base
        # isn't defined.
        if self.encodings_map.has_key(ext) and base:
            encoding = self.encodings_map[ext]
            base, ext = os.path.splitext(base)
            ext = ext[1:] # remove the dot
        else:
            encoding = None
        return aq_base(self.extensions.get(ext))

    security.declarePublic('globFilename')
    def globFilename(self, filename):
        """Lookup for IMimetypes object matching filename

        Filename must be a complete filename with extension.

        Return an IMimetype object associated with the glob's or None
        """
        globs = getattr(self, 'globs', None)
        if globs is None:
            return None
        for key in globs.keys():
            glob, mimetype = globs[key]
            if glob.match(filename):
                return aq_base(mimetype)
        return None

    security.declarePublic('lookupGlob')
    def lookupGlob(self, glob):
        globs = getattr(self, 'globs', None)
        if globs is None:
            return None
        return aq_base(globs.get(glob))

    def _classifiers(self):
        return [mt for mt in self.mimetypes() if IClassifier.isImplementedBy(mt)]

    security.declarePublic('classify')
    def classify(self, data, mimetype=None, filename=None):
        """Classify works as follows:
        1) you tell me the rfc-2046 name and I give you an IMimetype
           object
        2) the filename includes an extension from which we can guess
           the mimetype
        3) we can optionally introspect the data
        4) default to self.defaultMimetype if no data was provided
           else to application/octet-stream of no filename was provided,
           else to text/plain

        Return an IMimetype object or None 
        """
        mt = None
        if mimetype:
            mt = self.lookup(mimetype)
            if mt:
                mt = mt[0]
        elif filename:
            mt = self.lookupExtension(filename)
            if mt is None:
                mt = self.globFilename(filename)
        if data and not mt:
            for c in self._classifiers():
                if c.classify(data):
                    mt = c
                    break
            if not mt:
                mstr = magic.guessMime(data)
                if mstr:
                    mt = self.lookup(mstr)[0]
        if not mt:
            if not data:
                mtlist = self.lookup(self.defaultMimetype)
            elif filename:
                mtlist = self.lookup('application/octet-stream')
            else:
                failed = 'text/x-unknown-content-type'
                filename = filename or ''
                data = data or ''
                ct, enc = guess_content_type(filename, data, None)
                if ct == failed:
                    ct = 'text/plain'
                mtlist = self.lookup(ct)
            if len(mtlist)>0:
                mt = mtlist[0]
            else:
                return None

        # Remove acquisition wrappers
        return aq_base(mt)

    def __call__(self, data, **kwargs):
        """ Return a triple (data, filename, mimetypeobject) given
        some raw data and optional paramters

        method from the isourceAdapter interface
        """
        mimetype = kwargs.get('mimetype', None)
        filename = kwargs.get('filename', None)
        encoding = kwargs.get('encoding', None)
        mt = None
        if hasattr(data, 'filename'):
            filename = os.path.basename(data.filename)
        elif hasattr(data, 'name'):
            filename = os.path.basename(data.name)

        if hasattr(data, 'read'):
            _data = data.read()
            if hasattr(data, 'seek'):
                data.seek(0)
            data = _data

        # We need to figure out if data is binary and skip encoding if
        # it is
        mt = self.classify(data, mimetype=mimetype, filename=filename)

        if not mt.binary and not type(data) is UnicodeType:
            # if no encoding specified, try to guess it from data
            if encoding is None:
                encoding = self.guess_encoding(data)

            # ugly workaround for
            # https://sourceforge.net/tracker/?func=detail&aid=1068001&group_id=75272&atid=543430
            # covered by
            # https://sourceforge.net/tracker/?func=detail&atid=355470&aid=843590&group_id=5470
            # dont remove this code unless python is fixed.
            if encoding is "macintosh":
                encoding = 'mac_roman'

            try:
                try:
                    data = unicode(data, encoding, self.unicodePolicy)
                except (ValueError, LookupError):
                    # wrong unicodePolicy
                    data = unicode(data, encoding)
            except:
                data = unicode(data, self.fallbackEncoding)

        return (data, filename, aq_base(mt))

    security.declarePublic('guess_encoding')
    def guess_encoding(self, data):
        """ Try to guess encoding from a text value if no encoding
        guessed, used the default charset from site properties (Zope)
        with a fallback to UTF-8 (should never happen with correct
        site_properties, but always raise Attribute error without
        Zope)
        """
        if type(data) is type(u''):
            # data maybe unicode but with another encoding specified
            data = data.encode('UTF-8')
        encoding = guess_encoding(data)
        if encoding is None:
            try:
                site_props = self.portal_properties.site_properties
                encoding = site_props.getProperty('default_charset', 'UTF-8')
            except:
                encoding = 'UTF-8'
        return encoding

    security.declareProtected(ManagePortal, 'manage_delObjects')
    def manage_delObjects(self, ids, REQUEST=None):
        """ delete the selected mime types """
        for id in ids:
            self.unregister(self.lookup(id)[0])
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

    security.declareProtected(ManagePortal, 'manage_addMimeType')
    def manage_addMimeType(self, id, mimetypes, extensions, icon_path,
                           binary=0, globs=None, REQUEST=None):
        """add a mime type to the tool"""
        mt = MimeTypeItem(id, mimetypes, extensions=extensions,
                          binary=binary, icon_path=icon_path, globs=globs)
        self.register(mt)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

    security.declareProtected(ManagePortal, 'manage_editMimeType')
    def manage_editMimeType(self, name, new_name, mimetypes, extensions,
                            icon_path, binary=0, globs=None, REQUEST=None):
        """Edit a mime type by name
        """
        mt = self.lookup(name)[0]
        self.unregister(mt)
        mt.edit(new_name, mimetypes, extensions, icon_path=icon_path,
                binary=binary, globs=globs)
        self.register(mt)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

InitializeClass(MimeTypesRegistry)

def split(name):
    """ split a mime type in a (major / minor) 2-uple """
    try:
        major, minor = name.split('/', 1)
    except:
        raise MimeTypeException('Malformed MIME type (%s)' % name)
    return major, minor
