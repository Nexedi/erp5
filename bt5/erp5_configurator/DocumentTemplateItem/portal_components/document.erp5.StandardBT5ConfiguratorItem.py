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
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from erp5.component.mixin.ConfiguratorItemMixin import ConfiguratorItemMixin
from erp5.component.interface.IConfiguratorItem import IConfiguratorItem
from Products.ERP5Type.Cache import CachingMethod
from zLOG import LOG, INFO


@zope.interface.implementer(IConfiguratorItem)
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

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.StandardBT5ConfiguratorItem
                    )

  def _checkConsistency(self, fixit=False, **kw):
    template_tool = self.getPortalObject().portal_templates
    bt5_id = self.getBt5Id().split('.')[0]

    if bt5_id in template_tool.getInstalledBusinessTemplateTitleList():
      LOG("StandardBT5ConfiguratorItem", INFO,
        "Business Template already Installed: %s for %s" % (bt5_id, self.getRelativeUrl()))
      return []

    def _getRepositoryBusinessTemplateTitleList():
      return [bt.getTitle() for bt in \
              template_tool.getRepositoryBusinessTemplateList()]
    repository_bt_title_list = CachingMethod(
                         _getRepositoryBusinessTemplateTitleList,
                         id='StandardBT5_getRepositoryBusinessTemplateTitleList',
                         cache_factory='erp5_content_long')()

    if bt5_id in repository_bt_title_list:
      if fixit:
        template_tool.installBusinessTemplateListFromRepository([bt5_id],
                                  update_catalog=self.getUpdateCatalog(0),
                                  install_dependency=self.getInstallDependency(1),
                                  force_all=True,
                                  activate=False)

      return [self._createConstraintMessage('%s should be installed' % bt5_id),]

    raise ValueError("The business template %s was not found on available \
                         sources." % bt5_id)
