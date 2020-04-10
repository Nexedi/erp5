from Products.ERP5Type import Globals
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import View, ViewManagementScreens
from Products.CMFCore.FSObject import FSObject
from Products.CMFCore.DirectoryView import registerFileExtension,\
     registerMetaType

from Products.ERP5Form import _dtmldir
from Products.ERP5Form.Form import ERP5Form
from Products.Formulator.XMLToForm import XMLToForm

class ERP5FSForm(FSObject, ERP5Form):
    """FSForm."""

    meta_type = 'ERP5 Filesystem Formulator Form'

    manage_options = (
        (
        {'label':'Customize', 'action':'manage_main'},
        {'label':'Test', 'action':'formTest'},
        )
        )

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = Globals.DTMLFile('FSForm_customize', _dtmldir)

    def __init__(self, id, filepath, fullname=None, properties=None):
        FSObject.__init__(self, id, filepath, fullname, properties)

    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        type_info = self.getPortalObject().portal_types.getTypeInfo('ERP5 Form')
        obj = type_info.constructInstance(container=self,
                                          temp_object=True,
                                          id=self.getId(),
                                          title=self.title).aq_base
        obj.set_xml(self.get_xml())
        return obj

    def _readFile(self, reparse):
        f = open(self._filepath, 'rb')
        # update the form with the xml data
        try:
            XMLToForm(f.read(), self)
        except:
            # bare except here, but I hope this is ok, as the
            # exception should be reraised
            # (except if the LOG raises another one ... should we be more paranoid here?)
            import zLOG
            zLOG.LOG('Formulator.FSForm',zLOG.ERROR,
                     'error reading form from file '+self._filepath)
            raise

        f.close()

Globals.InitializeClass(ERP5FSForm)

registerFileExtension('form', ERP5FSForm)
registerMetaType('FSForm', ERP5FSForm)
