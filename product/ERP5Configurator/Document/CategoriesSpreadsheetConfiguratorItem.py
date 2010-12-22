##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
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

from StringIO import StringIO

from Acquisition import aq_base

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin


class UnrestrictedStringIO(StringIO):
  __allow_access_to_unprotected_subobjects__ = 1


class CategoriesSpreadsheetConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """Import a categories spreadsheet.
  """

  meta_type = 'ERP5 Categories Spreadsheet Configurator Item'
  portal_type = 'Categories Spreadsheet Configurator Item'
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
                    , PropertySheet.CategoriesSpreadsheetConfiguratorItem
                    )

  def build(self, business_configuration):
    portal = self.getPortalObject()
    ctool = portal.portal_categories

    self._readSpreadSheet()
    cache = self._category_cache
    for bc_id, category_list in cache.items():
      if bc_id in ctool.objectIds():
        bc = ctool._getOb(bc_id)
      else:
        # TODO: test bc creation
        # the bc should be added as base category in bt5 ?
        bc = ctool.newContent(id=bc_id)

      for category_info in category_list:
        path = bc
        for cat in category_info['path'].split("/")[1:]:
          if not cat in path.objectIds():
            path = path.newContent(
              portal_type='Category',
              id=cat,)
          else:
            path = path[cat]

        edit_dict = category_info.copy()
        edit_dict.pop('path')
        path.edit(**edit_dict)
        ## add to customer template
        self.install(path, business_configuration)

  def _readSpreadSheet(self):
    """Read the spreadsheet and prepare internal category cache.
    """
    aq_self = aq_base(self)
    if getattr(aq_self, '_category_cache', None) is None:
      # TODO use a invalid_spreadsheet_error_handler to report invalid
      # spreadsheet messages (see http://svn.erp5.org?rev=24908&view=rev )
      aq_self._category_cache = self.Base_getCategoriesSpreadSheetMapping(
                    UnrestrictedStringIO(self.getDefaultCategoriesSpreadsheetData()))

  security.declareProtected(Permissions.ModifyPortalContent,
                           'setDefaultCategoriesSpreadsheetFile')
  def setDefaultCategoriesSpreadsheetFile(self, *args, **kw):
    """Reset the spreadsheet cache."""
    self._setDefaultCategoriesSpreadsheetFile(*args, **kw)
    self._category_cache = None
    self.reindexObject()

  security.declareProtected(Permissions.ModifyPortalContent,
                           'setCategoriesSpreadsheetFile')
  setCategoriesSpreadsheetFile = setDefaultCategoriesSpreadsheetFile

  security.declareProtected(Permissions.AccessContentsInformation,
                           'getCategoryTitleItemList')
  def getCategoryTitleItemList(self, base_category_id, base=0):
    """Returns title item list for a base category contained in this
    spreadsheet.
    """
    self._readSpreadSheet()
    cache = self._category_cache

    result = [('', '')]
    if base_category_id not in cache:
      return result # TODO: return some kind of default. Where is this
                    # default ??? configurator_%s % base_category_id ?
                    # If we add default here, it should also be used in build
                    # ...

    category_path_dict = dict()
    for item in cache[base_category_id]:
      category_path_dict[item['path']] = item

    for item in cache[base_category_id]:
      # the first item in this list is the base category itself, so we skip it.
      if item['path'] == base_category_id:
        continue

      # recreate logical path
      path_element_list = []
      title_list = []
      for path_element in item['path'].split('/'):
        path_element_list.append(path_element)
        title_list.append(category_path_dict['/'.join(path_element_list)]['title'])

      if base:
        result.append(('/'.join(title_list[1:]), item['path']))
      else:
        result.append(('/'.join(title_list[1:]),
                       '/'.join(item['path'].split('/')[1:])))

    return result
