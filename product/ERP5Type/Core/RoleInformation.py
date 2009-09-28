##############################################################################
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
""" Information about customizable roles.

$Id$
"""

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Permissions import AccessContentsInformation
from Products.ERP5Type.XMLObject import XMLObject


class RoleInformation(XMLObject):
  """ Represent a role definition.

  Roles definitions defines local roles on ERP5Type documents. They are
  applied by the updateLocalRolesOnSecurityGroups method.
  """
  meta_type = 'ERP5 Role Information'
  portal_type = 'Role Information'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  security = ClassSecurityInfo()
  security.declareObjectProtected(AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.RoleInformation
                    )

  security.declarePrivate('testCondition')
  def testCondition(self, ec):
    """ Evaluate condition using context, 'ec', and return 0 or 1."""
    condition = self.getCondition()
    return condition is None and 1 or condition(ec)

  def _setCondition(self, value):
    if isinstance(value, basestring):
      value = Expression(value)
    self._baseSetCondition(value)

  def getCondition(self):
    if getattr(aq_base(self), 'condition', None) == '':
      del self.condition
    return self._baseGetCondition()

  security.declareProtected(AccessContentsInformation, 'getConditionText')
  def getConditionText(self):
    """
    """
    return getattr(self.getCondition(), 'text', None)

  def PrincipiaSearchSource(self):
    # Support for "Find" tab in ZMI
    return ' '.join((self.getId(),
                     self.getTitle(),
                     self.getDescription(),
                     self.getCondition(),
                     self.base_category_script))

InitializeClass(RoleInformation)
