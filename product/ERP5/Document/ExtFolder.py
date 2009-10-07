##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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

from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ExtFile.ExtFile import ExtFile
from Products.ExtFile.ExtImage import ExtImage
import os
from App.config import getConfiguration
from Products.ERP5Type.Globals import package_home
from Products.ERP5 import product_path
from Shared.DC.ZRDB.TM import TM
import shutil

from zLOG import LOG

class Deletion(TM):
  """Remove the directory at the end of a transaction.
  """
  def __init__(self, path):
    self.path = path
    self._register()
    
  def _finish(self):
    try:
      LOG('Deletion', 0, 'removing %s' % self.path)
      shutil.rmtree(self.path)
    except OSError:
      pass

  def _abort(self):
    pass

class ExtFolder( XMLObject ):
    """
       ExtFolder stores sub-objects as ExtFile or ExtImage.
    """

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      )

    # CMF Type Definition
    meta_type='ERP5 External Folder'
    portal_type='External Folder'    
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    security.declarePrivate('PUT_factory')
    def PUT_factory( self, name, typ, body ):
      """Return an ExtFile or ExtImage object.
      """
      major, minor = typ.split('/', 1)
      if major == 'image':
        return ExtImage(name)
      return ExtFile(name)

    def _getRepositoryPath(self):
      """Return the path in the filesystem.
      """
      instance_home = getConfiguration().instancehome
      repository = os.path.join(*ExtFile._repository)
      return os.path.sep.join((instance_home, repository, self.getPath()))

    security.declareProtected('Manage portal', 'generateRpmHeaderList')
    def generateRpmHeaderList(self):
      """Run genhdlist on the directory behind this object.
      """
      status = os.system("/usr/bin/genhdlist -s %s" % self._getRepositoryPath())
      if status != 0:
        raise RuntimeError, "failed in executing genhdlist"

    security.declareProtected('Manage portal', 'generateBt5HeaderList')
    def generateBt5HeaderList(self):
      """Run genbt5list on the directory behind this object.
      """
      status = os.system("%s/bin/genbt5list %s" % (product_path, self._getRepositoryPath()))
      if status != 0:
        raise RuntimeError, "failed in executing genbt5list"

    def manage_beforeDelete(self, item, container):
      """Called before deleting this object.
      """
      self._v_deletion = Deletion(self._getRepositoryPath())
      XMLObject.manage_beforeDelete(self, item, container)
