# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#                    Jean-Paul Smets <jp@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage

from zLOG import LOG, INFO                           

class Component(Base):
  # CMF Type Definition
  meta_type = 'ERP5 Component'
  portal_type = 'Component'

  isPortalContent = 1
  isRADContent = 1
  isDelivery = ConstantGetter('isDelivery', value=True)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ('Base',
                     'XMLObject',
                     'CategoryCore',
                     'DublinCore',
                     'Version',
                     'Reference',
                     'TextDocument')

  def checkConsistency(self, *args, **kw):
    """
    XXX-arnau: should probably in a separate Constraint class
    """
    if not self.getTextContent():
      return [ConsistencyMessage(self,
                                 object_relative_url=self.getRelativeUrl(),
                                 message="No source code",
                                 mapping={})]

    message = None
    try:
      self.load()
    except SyntaxError, e:
      message = "%s (line: %d, column: %d)" % (e.msg, e.lineno, e.offset)
    except Exception, e:
      message = str(e)

    if message:
      return [ConsistencyMessage(self,
                                 object_relative_url=self.getRelativeUrl(),
                                 message="Source Code: %s" % message,
                                 mapping={})]

    return []

  def load(self, namespace_dict={}):
    """
    Load the source code into the given dict. Using exec() rather than
    imp.load_source() as the latter would required creating an intermediary
    file. Also, for traceback readability sake, the destination module
    __dict__ is given rather than creating an empty dict and returning
    it. By default namespace_dict is an empty dict to allow checking the
    source code before validate.
    """
    exec self.getTextContent() in namespace_dict

  @staticmethod
  def _getFilesystemPath():
    raise NotImplementedError

  security.declareProtected(Permissions.ModifyPortalContent,
                            'importAllFromFilesystem')
  @classmethod
  def importAllFromFilesystem(cls, context, erase_existing=False):
    """
    Try to import all Components and returns error as a dict if any
    """
    import os.path
    path_pattern = "%s%s*.py" % (cls._getFilesystemPath(), os.path.sep)    

    LOG("ERP5Type.Core.Component", INFO, "Importing from %s" % path_pattern)

    import glob
    failed_import_dict = {}
    for path in glob.iglob(path_pattern):
      try:
        cls.importFromFilesystem(context, path, erase_existing)
      except Exception, e:
        failed_import_dict[path] = str(e)
      else:
        LOG("ERP5Type.Core.Component", INFO, "Imported %s" % path)

    return failed_import_dict

  @staticmethod
  def _getDynamicModuleNamespace():
    raise NotImplementedError

  security.declareProtected(Permissions.ModifyPortalContent,
                            'importFromFilesystem')
  @classmethod
  def importFromFilesystem(cls, context, path, erase_existing=False):
    """
    Import a Component from the given path into ZODB after checking that the
    source code is valid
    """
    import os.path
    class_name = os.path.basename(path).replace('.py', '')
    id = '%s.%s' % (cls._getDynamicModuleNamespace(), class_name)

    # XXX-arnau: not efficient at all
    if id in context:
      if not erase_existing:
        return

      context.deleteContent(id)

    with open(path) as f:
      source_code = f.read()

    # Try to load it first
    namespace_dict = {}
    exec source_code in namespace_dict

    return context.newContent(id=id,
                              # XXX-arnau: useless field?
                              reference=class_name,
                              text_content=source_code,
                              portal_type=cls.portal_type)
