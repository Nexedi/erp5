##############################################################################
#
# Copyright (c) 2007-2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from DocumentationHelper import DocumentationHelper
from DocumentationSection import DocumentationSection
from Products.ERP5Type import Permissions

class PortalTypeInstanceDocumentationHelper(DocumentationHelper):
  """
    Provides access to all documentation information
    of a portal type instance.
  """

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def __init__(self, uri):
    self.uri = uri

  def getInstance(self):
    return self.getPortalObject().restrictedTraverse(self.uri)

  # API Implementation
  security.declareProtected( Permissions.AccessContentsInformation, 'getTitle' )
  def getTitle(self):
    """
    Returns the title of the documentation helper
    """
    return self.getInstance().getTitleOrId()

  security.declareProtected( Permissions.AccessContentsInformation, 'getType' )
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Portal Type Instance"

  security.declareProtected( Permissions.AccessContentsInformation, 'getSectionList' )
  def getSectionList(self):
    """
    Returns a list of documentation sections
    """
    section_list = []
    if self.getWorkflowMethodURIList(inherited=0) != []:
      section_list.append(
        DocumentationSection(
          id='workflow_method',
          title='Workflow Method',
          class_name='WorkflowMethodDocumentationHelper',
          uri_list=self.getWorkflowMethodURIList(inherited=0),
        )
      )
    if self.getAccessorMethodURIList(inherited=0) != []:
      section_list.append(   
        DocumentationSection(
          id='accessor',
          title='Accessor',
          class_name='AccessorMethodDocumentationHelper',
          uri_list=self.getAccessorMethodURIList(inherited=0),
        )
      )
    if self.getClassMethodURIList(inherited=0) != []:  
      section_list.append(
        DocumentationSection(
          id='class_method',
          title='Class Methods',
          class_name='ClassMethodDocumentationHelper',
          uri_list=self.getClassMethodURIList(inherited=0),
        )
      )
    return map(lambda x: x.__of__(self.getInstance()), section_list)

  # Specific methods
  security.declareProtected( Permissions.AccessContentsInformation, 'getPortalType' )
  def getPortalType(self):
    """
    """
    return self.getInstance().getPortalType()

  def _getPropertyHolder(self):
    from Products.ERP5Type.Base import Base
    property_holder = None
    key = (self.getPortalType(), self.getInstance().__class__)
    if not(Base.aq_portal_type.has_key(key)):
      self.getInstance().initializePortalTypeDynamicProperties()
    property_holder =  Base.aq_portal_type[(self.getPortalType(), self.getInstance().__class__)]
    return property_holder

  security.declareProtected( Permissions.AccessContentsInformation, 'getAccessorMethodItemList' )
  def getAccessorMethodItemList(self):
    """
    """
    return self._getPropertyHolder().getAccessorMethodItemList()

  security.declareProtected( Permissions.AccessContentsInformation, 'getAccessorMethodIdList' )
  def getAccessorMethodIdList(self, inherited=1):
    """
    """
    return self._getPropertyHolder().getAccessorMethodIdList()

  security.declareProtected( Permissions.AccessContentsInformation, 'getAccessorMethodURIList' )
  def getAccessorMethodURIList(self, inherited=1, local=1):
    """
    Returns a list of URIs to accessor methods
    """
    method_id_list = self.getAccessorMethodIdList(inherited=inherited)
    klass = self.getInstance().__class__
    class_name = klass.__name__
    module = klass.__module__
    uri_prefix = '%s.%s.' % (module, class_name)
    return map(lambda x: '%s%s' % (uri_prefix, x), method_id_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getWorkflowMethodItemList' )
  def getWorkflowMethodItemList(self):
    """
    """
    return self._getPropertyHolder().getWorkflowMethodItemList()

  security.declareProtected(Permissions.AccessContentsInformation, 'getWorkflowObject' )
  def getWorkflowObject(self):
    """
    """
    return self._getPropertyHolder()

  security.declareProtected(Permissions.AccessContentsInformation, 'getWorkflowMethodIdList' )
  def getWorkflowMethodIdList(self, inherited=1):
    """
    """
    return self._getPropertyHolder().getWorkflowMethodIdList()

  security.declareProtected(Permissions.AccessContentsInformation, 'getWorkflowMethodURIList' )
  def getWorkflowMethodURIList(self, inherited=1, local=1):
    """
    Returns a list of URIs to workflow  methods
    """
    method_id_list = self.getWorkflowMethodIdList()
    klass = self.getInstance().__class__
    class_name = klass.__name__
    module = klass.__module__
    uri_prefix = '' #'%s.%s.' % (module, class_name)
    return map(lambda x: '%s%s' % (uri_prefix, x), method_id_list)


  security.declareProtected(Permissions.AccessContentsInformation, 'getActionMethodItemList' )
  def getActionMethodItemList(self):
    """
    """
    return self._getPropertyHolder().getActionMethodItemList()

  security.declareProtected( Permissions.AccessContentsInformation, 'getActionMethodIdList' )
  def getActionMethodIdList(self):
    """
    """
    return self._getPropertyHolder().getActionMethodIdList()

  security.declareProtected( Permissions.AccessContentsInformation, 'getClassMethodItemList' )
  def getClassMethodItemList(self, inherited=1, local=1):
    """
    Return a list of tuple (id, method) for every class method
    """
    klass = self.getInstance().__class__
    return self._getPropertyHolder().getClassMethodItemList(klass, inherited=inherited, local=local)

  security.declareProtected( Permissions.AccessContentsInformation, 'getClassMethodIdList' )
  def getClassMethodIdList(self, inherited=1, local=1):
    """
    Return a list of tuple (id, method) for every class method
    """
    klass = self.getInstance().__class__
    return self._getPropertyHolder().getClassMethodIdList(klass, inherited=inherited, local=local)

  security.declareProtected( Permissions.AccessContentsInformation, 'getClassMethodURIList' )
  def getClassMethodURIList(self, inherited=1, local=1):
    """
    Returns a list of URIs to class methods
    """
    method_id_list = self.getClassMethodIdList(inherited=inherited, local=local)
    klass = self.getInstance().__class__
    class_name = klass.__name__
    module = klass.__module__
    uri_prefix = '%s.%s.' % (module, class_name)
    return map(lambda x: '%s%s' % (uri_prefix, x), method_id_list)

  security.declareProtected( Permissions.AccessContentsInformation, 'getClassPropertyItemList' )
  def getClassPropertyItemList(self, inherited=1, local=1):
    """
    Return a list of tuple (id, method) for every class method
    """
    klass = self.getInstance().__class__
    return self._getPropertyHolder().getClassPropertyItemList(klass, inherited=inherited, local=local)

  security.declareProtected( Permissions.AccessContentsInformation, 'getClassPropertyIdList' )
  def getClassPropertyIdList(self, inherited=1, local=1):
    """
    Return a list of tuple (id, method) for every class method
    """
    klass = self.getInstance().__class__
    return self._getPropertyHolder().getClassPropertyIdList(klass, inherited=inherited, local=local)

  security.declareProtected( Permissions.AccessContentsInformation, 'getGeneratedPropertyIdList' )
  def getGeneratedPropertyIdList(self):
    """
    """

  security.declareProtected( Permissions.AccessContentsInformation, 'getGeneratedBaseCategoryIdList' )
  def getGeneratedBaseCategoryIdList(self):
    """
    """

InitializeClass(PortalTypeInstanceDocumentationHelper)
