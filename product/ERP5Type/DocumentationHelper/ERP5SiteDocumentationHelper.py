
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
from zLOG import LOG, INFO

class ERP5SiteDocumentationHelper(DocumentationHelper):
  """
    Provides access to all documentation information
    of an ERP5 Site.
  """

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # API Implementation
  security.declareProtected( Permissions.AccessContentsInformation, 'getTitle' )
  def getTitle(self):
    """
    Returns the title of the documentation helper
    """
    return self.getDocumentedObject().title

  security.declareProtected( Permissions.AccessContentsInformation, 'getType' )
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "ERP5 Site"

  security.declareProtected( Permissions.AccessContentsInformation, 'getSectionList' )
  def getSectionList(self):
    """
    Returns a list of documentation sections
    """
    return map(lambda x: x.__of__(self), [
      DocumentationSection(
        id='business_template',
        title='Business Template',
        class_name='BusinessTemplateDocumentationHelper',
        uri_list=self.getBusinessTemplateUriList(),
      ),
    ])

  # Specific methods
  security.declareProtected( Permissions.AccessContentsInformation, 'getDescription' )
  def getDescription(self):
    """
    Returns the description of the documentation helper
    """
    return self.getDocumentedObject().description
  
  security.declareProtected( Permissions.AccessContentsInformation, 'getBusinessTemplateIdList' )
  def getBusinessTemplateIdList(self):
    """
    """
    bt_list = []
    for bt in self.getDocumentedObject().portal_templates.objectValues():
      current_state = ''
      for wh in bt.workflow_history['business_template_installation_workflow']:	
	current_state = wh['installation_state']      
      if current_state == 'installed': 	      
        bt_list.append(bt.getId())
    return bt_list

  security.declareProtected( Permissions.AccessContentsInformation, 'getBusinessTemplateItemList' )
  def getBusinessTemplateItemList(self):
    """
    """
    bt_list = []
    for bt in self.getDocumentedObject().portal_templates.objectValues():
      revision = ""
      version = "" 	    
      if hasattr(bt, 'revision'):
        revision = bt.revision
      if hasattr(bt, 'version'):
	version = bt.version   
      current_state = ''
      for wh in bt.workflow_history['business_template_installation_workflow']:
        current_state = wh['installation_state']
      if current_state == 'installed':	
        bt_list.append((bt.getId(), bt.title, bt.description, version, revision))
    return bt_list

  security.declareProtected( Permissions.AccessContentsInformation, 'getBusinessTemplateURIList' )
  def getBusinessTemplateURIList(self):
    """
    """
    bt_list = self.getBusinessTemplateItemList()
    base_uri = '/'+self.uri.split('/')[1]
    return map(lambda x: ('%s/portal_templates/%s' % (base_uri, x[0]),x[1], x[2], x[3], x[4]), bt_list)

  security.declareProtected( Permissions.AccessContentsInformation, 'getBusinessTemplateUriList' )
  def getBusinessTemplateUriList(self):
    """
    """
    bt_list = self.getBusinessTemplateItemList()
    base_uri = '/'+self.uri.split('/')[1]
    return map(lambda x: ('%s/portal_templates/%s' % (base_uri, x[0])), bt_list)

InitializeClass(ERP5SiteDocumentationHelper)
