"""some common utilities
"""

FB_REGISTRY = None

# base class
from ExtensionClass import Base
from Acquisition import aq_base

# logging function
from zLOG import LOG, INFO
def log(msg, severity=INFO, id='PortalTransforms'):
    LOG(id, severity, msg)

# directory where template for the ZMI are located
import os.path
_www = os.path.join(os.path.dirname(__file__), 'www')
skins_dir = os.path.join(os.path.dirname(__file__), 'skins')

# list and dict classes to use
from Globals import PersistentMapping as DictClass
try:
    from ZODB.PersistentList import PersistentList as ListClass
except ImportError:
    from persistent.list import PersistentList as ListClass

# interfaces
try:
    # Zope >= 2.6
    from Interface import Interface, Attribute
except ImportError:
    # Zope < 2.6
    from Interface import Base as Interface, Attribute

def implements(object, interface):
    return interface.isImplementedBy(object)

# getToolByName
from Products.CMFCore.utils import getToolByName as _getToolByName
_marker = []

def getToolByName(context, name, default=_marker):
    global FB_REGISTRY
    tool = _getToolByName(context, name, default)
    if name == 'mimetypes_registry' and tool is default:
        if FB_REGISTRY is None:
            from Products.MimetypesRegistry.MimeTypesRegistry \
                 import MimeTypesRegistry
            FB_REGISTRY = MimeTypesRegistry()
        tool = FB_REGISTRY
    return tool

from zExceptions import BadRequest

__all__ = ('Base', 'log', 'DictClass', 'ListClass', 'getToolByName', 'aq_base',
           'Interface', 'Attribute', 'implements', 'skins_dir', '_www',
           'BadRequest', )
