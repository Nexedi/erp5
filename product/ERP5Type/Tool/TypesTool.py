##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Julien Muchembled <jm@nexedi.com>
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import imp, sys
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder as OFSFolder
import transaction
from Products.CMFCore import TypesTool as CMFCore_TypesTool
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type import Permissions
from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from zLOG import LOG, WARNING, PANIC

class TypesTool(BaseTool, CMFCore_TypesTool.TypesTool):
  """Provides a configurable registry of portal content types
  """
  id = 'portal_types'
  meta_type = 'ERP5 Types Tool'
  portal_type = 'Types Tool'
  allowed_types = ()

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declarePrivate('getFilteredActionListFor')
  def getFilteredActionListFor(self, ob=None):
    if ob is not None:
      type_info = self.getTypeInfo(ob)
      if type_info is not None:
        return type_info.getFilteredActionListFor(ob)
    return ()

  def getTypeInfo(self, *args):
    if not len(args): 
       return BaseTool.getTypeInfo(self)
    else:
      # The next 10 lines are taken from CMFCore
      # which means that the entire file is ZPLed
      # for now
      contentType = args[0]
      #return CMFCoreTypesTool.getTypeInfo(self, contentType)
      if not isinstance(contentType, basestring):
          if hasattr(aq_base(contentType), 'getPortalTypeName'):
              contentType = contentType.getPortalTypeName()
              if contentType is None:
                  return None
          else:
              return None
      #ob = getattr( self, contentType, None )
      ob = self._getOb(contentType, None)
      if getattr(aq_base(ob), '_isTypeInformation', 0):
          return ob
      else:
          return None

# Compatibility code to access old "ERP5 Role Information" objects.
OldRoleInformation = imp.new_module('Products.ERP5Type.RoleInformation')
sys.modules[OldRoleInformation.__name__] = OldRoleInformation
from OFS.SimpleItem import SimpleItem
OldRoleInformation.RoleInformation = SimpleItem

class OldTypesTool(OFSFolder):

  id = 'cmf_portal_types'

  def _migratePortalType(self, types_tool, old_type):
    if old_type.__class__ is not ERP5TypeInformation:
      LOG('OldTypesTool._migratePortalType', WARNING,
          "Can't convert %r (meta_type is %r)."
          % (old_type, old_type.meta_type))
      return
    new_type = ERP5TypeInformation(old_type.id, uid=None)
    types_tool._setObject(new_type.id, new_type, set_owner=0)
    new_type = types_tool[new_type.id]
    for k, v in  old_type.__dict__.iteritems():
      if k == '_actions':
        for action in v:
          new_type._importOldAction(action)
      elif k == '_roles':
        for role in v:
          new_type._importRole(role.__getstate__())
      elif k == '_property_domain_dict':
        v = dict((k, t.__class__(property_name=t.property_name,
                                 domain_name=t.property_name))
                 for k, t in v.iteritems())
      else:
        setattr(new_type, k, v)

  def _migrateTypesTool(self, parent):
    # 'parent' has no acquisition wrapper so migration must be done without
    # access to physical root. All activities are created with no leading '/'
    # in the path.
    LOG('OldTypesTool', WARNING, "Converting portal_types...")
    for object_info in parent._objects:
      if object_info['id'] == TypesTool.id:
        break
    types_tool = TypesTool()
    types_tool.__ac_local_roles__ = self.__ac_local_roles__.copy()
    try:
      setattr(parent, self.id, self)
      object_info['id'] = self.id
      del parent.portal_types
      parent._setObject(TypesTool.id, types_tool, set_owner=0)
      types_tool = types_tool.__of__(parent)
      if not parent.portal_categories.hasObject('action_type'):
        # Required to generate ActionInformation.getActionType accessor.
        from Products.ERP5Type.Document.BaseCategory import BaseCategory
        action_type = BaseCategory('action_type')
        action_type.uid = None
        parent.portal_categories._setObject(action_type.id, action_type)
      for type_info in self.objectValues():
        self._migratePortalType(types_tool, type_info)
      #types_tool.activate().Base_setDefaultSecurity()
    except:
      transaction.abort()
      LOG('OldTypesTool', PANIC, 'Could not convert portal_types: ',
          error=sys.exc_info())
      raise # XXX The exception may be hidden by acquisition code
            #     (None returned instead)
    else:
      LOG('OldTypesTool', WARNING, "... portal_types converted.")
      return types_tool

  def __of__(self, parent):
    base_self = aq_base(self) # Is it required ?
    if parent.__dict__[TypesTool.id] is not base_self:
      return OFSFolder.__of__(self, parent)
    return UnrestrictedMethod(base_self._migrateTypesTool)(parent)

CMFCore_TypesTool.TypesTool = OldTypesTool
