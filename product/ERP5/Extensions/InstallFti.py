from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.TypesTool import ScriptableTypeInformation
from Products.CMFCore.DirectoryView import addDirectoryViews, createDirectoryView
from Products.CMFCore.utils import getToolByName, minimalpath
from Products.ExternalMethod import ExternalMethod
from Products.CMFDefault.Portal import PortalGenerator
from  Products.ERP5.FtiExtension import factory_type_information
from  Products.ERP5.FtiExtension import scriptable_type_information
from App.Common import package_home
from cStringIO import StringIO
import string
import zLOG
try:
    from Products.Localizer import MessageCatalog
    use_localizer = 1
except:
    use_localizer = 0

out = StringIO()

def registerType(self, fti):
    """
        Register type defined in fti in the types tool
    """
    typestool = getToolByName(self, 'portal_types')
    if fti['id'] not in typestool.objectIds():
        cfm = apply(FactoryTypeInformation, (), fti)
        typestool._setObject(fti['id'], cfm)
        zLOG.LOG(fti['product'], 0, 'FTI Registered %s with the types tool' % fti['id'])
        out.write('FTI Registered %s with the types tool\n' % fti['id'])
    else:
        zLOG.LOG(fti['product'], 0, 'Object "%s" already existed in the types tool' % (fti['id']))
        out.write('Object "%s" already existed in the types tool\n' % (fti['id']))

def registerScript(self, fti):
    """
        Register type defined in fti in the types tool
    """
    typestool = getToolByName(self, 'portal_types')
    if fti['id'] not in typestool.objectIds():
        cfm = apply(ScriptableTypeInformation, (), fti)
        typestool._setObject(fti['id'], cfm)
        zLOG.LOG(fti['product'], 0, 'STI Registered %s with the types tool' % fti['id'])
        out.write('STI Registered %s with the types tool\n' % fti['id'])
    else:
        zLOG.LOG(fti['product'], 0, 'Object "%s" already existed in the types tool' % (fti['id']))
        out.write('Object "%s" already existed in the types tool\n' % (fti['id']))


def install(self):
    """Register all ERP5 components"""
    out.write('ERP5 Installation\n')
    out.write('===========================\n\n')

    t = factory_type_information
    if type(t) == type(()):
        for fti in t:
            registerType(self, fti)
    else:
        registerType(self, t)

    s = scriptable_type_information
    if type(s) == type(()):
        for fti in s:
            registerScript(self, fti)
    else:
        registerType(self, s)

    return out.getvalue()
