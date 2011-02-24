##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Nicolas Dumazet <nicolas.dumazet@nexedi.com>
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import transaction

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5Type.Accessor import Translation
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Core.PropertySheet import PropertySheet as PropertySheetDocument

from zLOG import LOG, INFO

class PropertySheetTool(BaseTool):
  """
  Provides a configurable registry of property sheets
  """
  id = 'portal_property_sheets'
  meta_type = 'ERP5 Property Sheet Tool'
  portal_type = 'Property Sheet Tool'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _isBootstrapRequired(self):
    return not self.has_key('BaseType')

  def _bootstrap(self):
    bt_name = 'erp5_property_sheets'
    super(PropertySheetTool, self)._bootstrap(bt_name,
                                              'PropertySheetTemplateItem', (
      'BaseType',
      'BusinessTemplate',
      'Folder',
      'SimpleItem',
      'Version',
      'Comment',
      # the following ones are required to upgrade an existing site
      'Reference',
      'BaseCategory',
      'SQLIdGenerator',
    ))
    def install():
      template_tool = self.getPortalObject().portal_templates
      if template_tool.getInstalledBusinessTemplate(bt_name) is None:
        from Products.ERP5.ERP5Site import getBootstrapBusinessTemplateUrl
        url = getBootstrapBusinessTemplateUrl(bt_name)
        template_tool.download(url).activate().install()
    transaction.get().addBeforeCommitHook(install)

  security.declarePublic('getTranslationDomainNameList')
  def getTranslationDomainNameList(self):
    return (['']+
            [object_.id
             for object_ in getToolByName(self, 'Localizer').objectValues()
             if object_.meta_type=='MessageCatalog']+
            [Translation.TRANSLATION_DOMAIN_CONTENT_TRANSLATION]
            )

  security.declareProtected(Permissions.ManagePortal,
                            'createAllPropertySheetsFromFilesystem')
  def createAllPropertySheetsFromFilesystem(self, erase_existing=False,
                                            REQUEST=None):
    """
    Create Property Sheets in portal_property_sheets from _all_
    filesystem Property Sheets
    """
    from Products.ERP5Type import PropertySheet

    # Get all the filesystem Property Sheets
    for name, klass in PropertySheet.__dict__.iteritems():
      # If the Property Sheet is a string, it means that the Property
      # Sheets has either been already migrated or it is not available
      # (perhaps defined in a bt5 not installed yet?)
      if name[0] == '_' or isinstance(klass, basestring):
        continue

      if name in self.objectIds():
        if not erase_existing:
          continue

        self.portal_property_sheets.deleteContent(name)

      LOG("Tool.PropertySheetTool", INFO,
          "Creating %s in portal_property_sheets" % repr(name))

      PropertySheetDocument.importFromFilesystemDefinition(self, klass)

    if REQUEST is not None:
      portal = self.getPortalObject()
      message = portal.Base_translateString('Property Sheets successfully'\
                                          ' imported from filesystem to ZODB.')
      return self.Base_redirect('view',
                                keep_items={'portal_status_message': message})

  security.declareProtected(Permissions.ManagePortal,
                            'getPropertyAvailablePermissionList')
  def getPropertyAvailablePermissionList(self):
    """
    Return a sorted set of all the permissions useful for read/write
    permissions for properties of ZODB Property Sheets
    """
    return sorted(set([ value for key, value in Permissions.__dict__.iteritems() \
                        if key[0].isupper() ]))
