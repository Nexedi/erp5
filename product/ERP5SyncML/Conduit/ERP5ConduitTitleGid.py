##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#          Fabien Morin <fabien.morin@gmail.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from Products.ERP5SyncML.Conduit.ERP5Conduit import ERP5Conduit
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5SyncML.SyncCode import SyncCode

from zLOG import LOG

class ERP5ConduitTitleGid(ERP5Conduit):
  """
  ERP5ConduitTitleGid provides two methods who permit to have the GID
  The Gid is composed by the title : "FirtName LastName"
  this class is made for unit test
  """

  # Declarative security
  security = ClassSecurityInfo()

  def getGidFromObject(self, object):
    """
    return the Gid composed of FirstName and LastName generate with the object
    """
    return object.getTitle()

#  def getGidFromXML(self, xml):
#    """
#    return the Gid composed of FirstName and LastName generate with a peace of
#    xml
#    """
#    #to be defined
