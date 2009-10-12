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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
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

  _section_list = (
    dict(
      id='workflow_method',
      title='Workflow Method',
      class_name='WorkflowMethodDocumentationHelper',
    ),
    dict(
      id='accessor_method',
      title='Accessor',
      class_name='AccessorMethodDocumentationHelper',
    ),
    dict(
      id='class_method',
      title='Class Methods',
      class_name='ClassMethodDocumentationHelper',
    ),
  )

  security.declareProtected(Permissions.AccessContentsInformation, 'getType')
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Portal Type Instance"

  security.declareProtected(Permissions.AccessContentsInformation, 'getPortalType')
  def getPortalType(self):
    """
    """
    return self.getDocumentedObject().getPortalType()

  security.declareProtected(Permissions.AccessContentsInformation, 'getAccessorMethodItemList')
  def getAccessorMethodItemList(self):
    """
    """
    return self._getPropertyHolder().getAccessorMethodItemList()

  security.declareProtected(Permissions.AccessContentsInformation, 'getAccessorMethodIdList')
  def getAccessorMethodIdList(self):
    """
    """
    return self._getPropertyHolder().getAccessorMethodIdList()

  security.declareProtected(Permissions.AccessContentsInformation, 'getAccessorMethodUriList')
  def getAccessorMethodUriList(self):
    """
    Returns a list of URIs to accessor methods
    """
    method_id_list = self.getAccessorMethodIdList()
    klass = self.getDocumentedObject().__class__
    class_name = klass.__name__
    module = klass.__module__
    uri_prefix = '%s.%s.' % (module, class_name)
    return map(lambda x: '%s%s' % (uri_prefix, x), method_id_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getWorkflowMethodItemList')
  def getWorkflowMethodItemList(self):
    """
    """
    return self._getPropertyHolder().getWorkflowMethodItemList()

  security.declareProtected(Permissions.AccessContentsInformation, 'getWorkflowObject')
  def getWorkflowObject(self):
    """
    """
    return self._getPropertyHolder()

  security.declareProtected(Permissions.AccessContentsInformation, 'getWorkflowMethodIdList')
  def getWorkflowMethodIdList(self):
    """
    """
    return self._getPropertyHolder().getWorkflowMethodIdList()

  security.declareProtected(Permissions.AccessContentsInformation, 'getWorkflowMethodUriList')
  def getWorkflowMethodUriList(self):
    """
    Returns a list of URIs to workflow  methods
    """
    method_id_list = self.getWorkflowMethodIdList()
    klass = self.getDocumentedObject().__class__
    class_name = klass.__name__
    module = klass.__module__
    uri_prefix = '' #'%s.%s.' % (module, class_name)
    return map(lambda x: '%s%s' % (uri_prefix, x), method_id_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getActionMethodItemList')
  def getActionMethodItemList(self):
    """
    """
    return self._getPropertyHolder().getActionMethodItemList()

  security.declareProtected(Permissions.AccessContentsInformation, 'getActionMethodIdList')
  def getActionMethodIdList(self):
    """
    """
    return self._getPropertyHolder().getActionMethodIdList()

  security.declareProtected(Permissions.AccessContentsInformation, 'getClassMethodItemList')
  def getClassMethodItemList(self, **kw):
    """
    Return a list of tuple (id, method) for every class method
    """
    klass = self.getDocumentedObject().__class__
    return self._getPropertyHolder().getClassMethodItemList(klass, **kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'getClassMethodIdList')
  def getClassMethodIdList(self, **kw):
    """
    Return a list of tuple (id, method) for every class method
    """
    klass = self.getDocumentedObject().__class__
    return self._getPropertyHolder().getClassMethodIdList(klass, **kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'getClassMethodUriList')
  def getClassMethodUriList(self, inherited=0, **kw):
    """
    Returns a list of URIs to class methods
    """
    method_id_list = self.getClassMethodIdList(inherited=inherited, **kw)
    klass = self.getDocumentedObject().__class__
    class_name = klass.__name__
    module = klass.__module__
    uri_prefix = '%s.%s.' % (module, class_name)
    return map(lambda x: '%s%s' % (uri_prefix, x), method_id_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getClassPropertyItemList')
  def getClassPropertyItemList(self, **kw):
    """
    Return a list of tuple (id, method) for every class method
    """
    klass = self.getDocumentedObject().__class__
    return self._getPropertyHolder().getClassPropertyItemList(klass, **kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'getClassPropertyIdList')
  def getClassPropertyIdList(self, **kw):
    """
    Return a list of tuple (id, method) for every class method
    """
    klass = self.getDocumentedObject().__class__
    return self._getPropertyHolder().getClassPropertyIdList(klass, **kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'getGeneratedPropertyIdList')
  def getGeneratedPropertyIdList(self):
    """
    """

  security.declareProtected(Permissions.AccessContentsInformation, 'getGeneratedBaseCategoryIdList')
  def getGeneratedBaseCategoryIdList(self):
    """
    """

InitializeClass(PortalTypeInstanceDocumentationHelper)
