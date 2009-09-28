##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SARL and Contributors. All Rights Reserved.
#                         Jean-Paul Smets <jp@nexedi.com>
#                         Ivan Tyagov <ivan@nerpix.com>
#                         Julien Muchembled <jm@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.CMFCore.Expression import Expression
from Products.CMFCore.ActionInformation import ActionInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Permissions import AccessContentsInformation
from Products.ERP5Type.XMLObject import XMLObject
from zLOG import LOG

class ActionInformation(XMLObject):
  """
  EXPERIMENTAL - DO NOT USE THIS CLASS BESIDES R&D
  ActionInformation is an ERP5 type which will eventually replace respective ActionInformation from CMF.
  """
  # XXX 'icon' property is not used. We can problably drop it.

  meta_type = 'ERP5 Action Information'
  portal_type = 'Action Information'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  icon = None # Override DynamicType.icon from CMFCore

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.ActionInformation
                    )

  def testCondition(self, ec):
    """ Evaluate condition using context, 'ec', and return 0 or 1."""
    condition = self.getCondition()
    return condition is None and 1 or condition(ec)

  security.declarePublic('getVisibility')
  def getVisibility(self):
    """ Return whether the action should be visible in the CMF UI."""
    return self.isVisible()

  def _setActionExpression(self, value):
    if isinstance(value, basestring):
      value = value and Expression(value) or None
    self._baseSetActionExpression(value)
  def _setCondition(self, value):
    if isinstance(value, basestring):
      value = value and Expression(value) or None
    self._baseSetCondition(value)
  def _setIcon(self, value):
    if isinstance(value, basestring):
      value = value and Expression(value) or None
    self._baseSetIcon(value)

  def getCondition(self):
    if getattr(aq_base(self), 'condition', None) == '':
      del self.condition
    return self._baseGetCondition()
  def getIcon(self):
    if getattr(aq_base(self), 'icon', None) == '':
      del self.icon
    return self._baseGetIcon()

  security.declareProtected(AccessContentsInformation, 'getActionText')
  def getActionText(self):
    """
    """
    return getattr(self.getActionExpression(), 'text', None)
  security.declareProtected(AccessContentsInformation, 'getConditionText')
  def getConditionText(self):
    """
    """
    return getattr(self.getCondition(), 'text', None)
  security.declareProtected(AccessContentsInformation, 'getIconText')
  def getIconText(self):
    """
    """
    return getattr(self.getIcon(), 'text', None)

  security.declareProtected(AccessContentsInformation, 'PrincipiaSearchSource')
  def PrincipiaSearchSource(self):
    # Support for "Find" tab in ZMI
    search_source_list = [self.getReference(),
                          self.getTitle(),
                          self.getDescription(),
                          self.getActionText(),
                          self.getConditionText()]
    return ' '.join(filter(None, search_source_list))

  #
  # XXX CMF compatibility
  #

  def _getActionObject(self):
    return self.getActionExpression()

  security.declarePrivate('getCategory')
  def getCategory(self):
    return self.getActionType()

  security.declarePrivate('getPermissions')
  def getPermissions(self):
    return self.getActionPermissionList()

  #def getActionCategorySelectionList(self):
  #  return self._getCategoryTool().action_type.objectIds()
  #def getPriority(self):
  #  return self.getFloatIndex()

  security.declarePrivate('getMapping')
  def getMapping(self):
    """ Get a mapping of this object's data.
    """
    return { 'id': self.getReference(),
             'title': self.getTitle(),
             'description': self.getDescription(),
             'category':  self.getActionType(),
             'condition': self.getCondition(),
             'permissions': self.getPermissions(),   #self.permissions,
             'visible': self.getVisibility(), #bool(self.visible),
             'action': self.getActionText() }

  security.declarePrivate('getAction')
  def getAction(self, ec):
    """ Compute the action using context, 'ec'; return a mapping of
          info about the action.
       XXX To be renamed or removed,
           so that 'action_expression' property can be renamed to 'action'.
    """
    return ActionInfo(self, ec)
