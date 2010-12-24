##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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

import zope.interface
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin
import transaction

class StandardBT5ConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ This class will install standard ERP5 template from a repository to
  fake site. """

  meta_type = 'ERP5 Standard BT5 Configurator Item'
  portal_type = 'Standard BT5 Configurator Item'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.IConfiguratorItem)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.StandardBT5ConfiguratorItem
                    )

  def build(self, business_configuration):
    bt5_id = self.getBt5Id()
    bt5_copy_id = '%s_copy' % bt5_id
    portal = self.getPortalObject()
    template_tool = getToolByName(portal, 'portal_templates')

    ## Is this standard template already gzipped?
    filename_bt5_id = '%s.bt5' % bt5_id
    if business_configuration.isStandardBT5(filename_bt5_id):
      bt_url = business_configuration.getPublicUrlForBT5Id(filename_bt5_id)

      business_configuration.newContent(portal_type='Link',
                    url_string = bt_url, title = filename_bt5_id) 
    else:
      ## we need to make a copy of template to be able to export it
      if not bt5_copy_id in template_tool.objectIds():
        bt5 = template_tool.getInstalledBusinessTemplate(bt5_id)
        template_copy = template_tool.manage_copyObjects(ids=(bt5.getId(),))
        new_id_list = template_tool.manage_pasteObjects(template_copy)
        new_bt5_id = new_id_list[0]['new_id']
        template_tool.manage_renameObject(new_bt5_id, bt5_copy_id)
      ## we are sure that we have this business template
      self._current_bt_id = bt5_copy_id
      return self.get_it_built(business_configuration)

  def get_it_built(self, business_configuration):
    portal = self.getPortalObject()
    template_tool = getToolByName(portal, 'portal_templates')
    bt5_obj = self._getCurrentBT(business_configuration)
    if bt5_obj.getBuildingState() != 'built':
      ## build template so it can be exported
      bt5_obj.edit()
      bt5_obj.build()
      # XXX Due a bug into Business Templates it is not possible build
      # the business template and export when this have one 
      # ActionTemplateItem. This is a TEMPORARY CHANGE and it should be
      # removed as soon as Business Template is FIXED.
      transaction.savepoint(optimistic=True)
    bt5_data = template_tool.export(bt5_obj)
    business_configuration.newContent(portal_type='File',
                                      title = '%s.bt5' % bt5_obj.getId(),
                                      data = bt5_data)

  def _getCurrentBT(self, business_configuration):
    """ Return current bt5 file. """
    portal = self.getPortalObject()
    template_tool = portal.portal_templates
    bt5_id = self._current_bt_id
    bt5_obj = portal.portal_templates[bt5_id]
    return bt5_obj
