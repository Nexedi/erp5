import Globals
from AccessControl import ClassSecurityInfo

try:
    import Products.FileSystemSite
except ImportError:
    # use CMF product
    from Products.CMFCore.CMFCorePermissions import View
    from Products.CMFCore.FSObject import FSObject
    from Products.CMFCore.DirectoryView import registerFileExtension,\
                                               registerMetaType, expandpath
else:
    # use FileSystemSite product
    from Products.FileSystemSite.Permissions import View
    from Products.FileSystemSite.FSObject import FSObject
    from Products.FileSystemSite.DirectoryView import registerFileExtension,\
                                                      registerMetaType, expandpath

from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLToForm import XMLToForm

class FSForm(FSObject, ZMIForm):
    """FSForm."""

    meta_type = 'Filesystem Formulator Form'

    manage_options = (
        (
        {'label':'Customize', 'action':'manage_main'},
        {'label':'Test', 'action':'formTest'},
        )
        )

    _updateFromFS = FSObject._updateFromFS

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    def __init__(self, id, filepath, fullname=None, properties=None):
        FSObject.__init__(self, id, filepath, fullname, properties)

    def _createZODBClone(self):
        # not implemented yet
        return None

    def _readFile(self, reparse):
        file = open(expandpath(self._filepath), 'rb')
        try:
            data = file.read()
        finally:
            file.close()

        # update the form with the xml data
        try:
            XMLToForm(data, self)
        except:
            # bare except here, but I hope this is ok, as the
            # exception should be reraised
            # (except if the LOG raises another one ...
            # should we be more paranoid here?)
            import zLOG
            zLOG.LOG(
                'Formulator.FSForm', zLOG.ERROR,
                'error reading form from file ' +
                expandpath(self._filepath))
            raise

    #### The following is mainly taken from Form.py ACCESSORS section ###

##     def get_field_ids(self):
##         self._updateFromFS()
##         return ZMIForm.get_field_ids(self)

##     def get_fields_in_group(self, group):
##         self._updateFromFS()
##         return ZMIForm.get_fields_in_group(self, group)

##     def has_field(self, id):
##         self._updateFromFS()
##         return ZMIForm.has_field(self, id)

##     def get_field(self, id):
##         self._updateFromFS()
##         return ZMIForm.get_field(self, id)

##     def get_groups(self):
##         self._updateFromFS()
##         return ZMIForm.get_groups(self)

##     def get_form_encoding(self):
##         self._updateFromFS()
##         return ZMIForm.get_form_encoding(self)

##     def header(self):
##         self._updateFromFS()
##         return ZMIForm.header(self)

##     def get_xml(self):
##         self._updateFromFS()
##         return ZMIForm.get_xml(self)

##     def all_meta_types(self):
##         self._updateFromFS()
##         return ZMIForm.all_meta_types(self)

##     security.declareProtected('View management screens', 'get_group_rows')
##     def get_group_rows(self):
##         self._updateFromFS()
##         return ZMIForm.get_group_rows(self)

Globals.InitializeClass(FSForm)

registerFileExtension('form', FSForm)
registerMetaType('FSForm', FSForm)
