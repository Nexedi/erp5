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
from Products.ERP5Type.UnrestrictedMethod import unrestricted_apply
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Core.PropertySheet import PropertySheet as PropertySheetDocument
from zExceptions import BadRequest

from zLOG import LOG, INFO, WARNING

KNOWN_BROKEN_PROPERTY_SHEET_DICT = {
  'InventoryConstraint': 'erp5_trade',
}

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

  # Business Template properties introduced later on have to be there as
  # _importFile a bt will look at propertyMap() to set properties
  _bootstrap_business_template_property_tuple = (
    'template_catalog_security_uid_column_property',
    'template_interface_id_property',
    'template_mixin_id_property')

  def _isBootstrapRequired(self):
    if not self.has_key('BaseType'):
      return True

    bt_has_key = self.BusinessTemplate.has_key
    for bt_property in self._bootstrap_business_template_property_tuple:
      if not bt_has_key(bt_property):
        return True

    return False

  def _bootstrap(self):
    bt_name = 'erp5_property_sheets'
    from Products.ERP5.ERP5Site import ERP5Generator
    content_path_list = [
      'BaseType',
      'BusinessTemplate',
      'Folder',
      'SimpleItem',
      'Version',
      'Comment',
      # the following ones are required to upgrade an existing site
      'Reference',
      'BaseCategory',
      'SQLIdGenerator']
    content_path_list.extend([
      'BusinessTemplate/' + bt_property
      for bt_property in self._bootstrap_business_template_property_tuple])
    ERP5Generator.bootstrap(self, bt_name, 'PropertySheetTemplateItem',
                            content_path_list)
    def install():
      from ZPublisher.BaseRequest import RequestContainer
      from Products.ERP5Type.Globals import get_request
      portal = self.getPortalObject()
      # BusinessTemplate.install needs a request
      template_tool = portal.aq_base.__of__(portal.aq_parent.__of__(
        RequestContainer(REQUEST=get_request()))).portal_templates
      if template_tool.getInstalledBusinessTemplate(bt_name) is None:
        from Products.ERP5.ERP5Site import getBootstrapBusinessTemplateUrl
        url = getBootstrapBusinessTemplateUrl(bt_name)
        template_tool.download(url).install()
    transaction.get().addBeforeCommitHook(unrestricted_apply, (install,))

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
    Returns the list of PropertySheet names which failed being imported.
    """
    from Products.ERP5Type import PropertySheet

    failed_import = []
    append = failed_import.append
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

      try:
        PropertySheetDocument.importFromFilesystemDefinition(self, klass)
      except BadRequest:
        if name in KNOWN_BROKEN_PROPERTY_SHEET_DICT:
          LOG('PropertySheetTool', WARNING, 'Failed to import %s with error:' % (
            name, ), error=True)
          # Don't fail, this property sheet is known to have been broken in the
          # past, this site might be upgrading from such broken version.
          append(name)
        else:
          raise

    if REQUEST is None:
      return failed_import
    else:
      portal = self.getPortalObject()
      base_message = 'Property Sheets successfully imported from ' \
        'filesystem to ZODB.'
      mapping = {}
      if failed_import:
        base_message += ' These property sheets failed to be imported: ' \
          '$failed_import . You must update the following business ' \
          'templates to have fixed version of these property sheets: ' \
          '$business_templates'
        mapping['failed_import'] = ', '.join(failed_import)
        mapping['business_templates'] = ', '.join({
          KNOWN_BROKEN_PROPERTY_SHEET_DICT[x] for x in failed_import})
      message = portal.Base_translateString(base_message, mapping=mapping)
      return self.Base_redirect('view',
                                keep_items={'portal_status_message': message})

  security.declareProtected(Permissions.ManagePortal,
                            'getPropertyAvailablePermissionList')
  def getPropertyAvailablePermissionList(self):
    """
    Return a sorted set of all the permissions useful for read/write
    permissions for properties of ZODB Property Sheets
    """
    return sorted({value for key, value in Permissions.__dict__.iteritems()
                         if key[0].isupper()})
