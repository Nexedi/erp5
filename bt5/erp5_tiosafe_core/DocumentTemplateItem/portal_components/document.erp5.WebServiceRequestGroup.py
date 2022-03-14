##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject

class WebServiceRequestGroup(XMLObject):
  # CMF Type Definition
  meta_type = 'ERP5 Web Service Request Group'
  portal_type = 'Web Service Request Group'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Arrow, )

  def __call__(self, **kw):
    """
      Make this object callable. It will calls each methods defined in the
      multi list field with the given parameters.
    """
    object_list = []
    for web_service_request in self.getSourceList():
      object_list += getattr(self, web_service_request)(**kw)
    return object_list

  def __getitem__(self, item):
    """
      Simulate the traversable behaviour by retrieving the item through
      the web service
    """
    object_list = []
    for web_service_request in self.getSourceList():
      try:
        object_list.append(
            getattr(self, web_service_request).__getitem__(item),
        )
      except KeyError:
        # no need to raise until all web service requests are browsed
        continue

    # after browsing all web service requests check that item exists and only
    # one time
    if len(object_list) != 1:
      raise KeyError("No entry for the item %s" % item)
    return object_list[0]

