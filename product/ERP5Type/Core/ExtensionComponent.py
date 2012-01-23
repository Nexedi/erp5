# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import os.path

from Products.ERP5Type.Core.Component import Component
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions

from zLOG import LOG, INFO                           

class ExtensionComponent(Component):
  # CMF Type Definition
  meta_type = 'ERP5 Extension Component'
  portal_type = 'Extension Component'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'importAllFromFilesystem')
  @classmethod
  def importAllFromFilesystem(cls, context, erase_existing=False):
    """
    Try to import all Extensions as found in INSTANCEHOME/Extensions and
    returns error as a dict if any
    """
    from App.config import getConfiguration
    extension_path_pattern = "%s%s%s/*" % (getConfiguration().instancehome,
                                           os.path.sep,
                                           'Extensions')

    LOG("ERP5Type.Core.ExtensionComponent", INFO,
        "Importing from %s" % extension_path_pattern)

    import glob
    failed_import_dict = {}
    for extension_path in glob.iglob(extension_path_pattern):
      try:
        cls.importFromFilesystem(context, extension_path, erase_existing)
      except Exception, e:
        failed_import_dict[extension_path] = str(e)
      else:
        LOG("ERP5Type.Core.ExtensionComponent", INFO,
            "Imported %s" % extension_path)

    return failed_import_dict

  security.declareProtected(Permissions.ModifyPortalContent,
                            'importFromFilesystem')
  @classmethod
  def importFromFilesystem(cls, context, path, erase_existing=False):
    """
    Import an Extension from the given path into ZODB after checking that the
    source code is valid
    """
    class_name = os.path.basename(path).replace('.py', '')
    id = 'erp5.component.extension.%s' % class_name

    # XXX-arnau: not efficient at all
    if id in context:
      if not erase_existing:
        return

      context.deleteContent(id)

    with open(path) as extension_file:
      source_code = extension_file.read()

    # Try to load it first
    namespace_dict = {}
    exec source_code in namespace_dict

    return context.newContent(id=id,
                              # XXX-arnau: useless field?
                              reference=class_name,
                              text_content=source_code,
                              portal_type=cls.portal_type)
