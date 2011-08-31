##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5TioSafe.Conduit.TioSafeBaseConduit import TioSafeBaseConduit
from lxml import etree

class OrganisationERP5IntegrationConduit(TioSafeBaseConduit):
  """
    This is the conduit use to synchonize ERP5 Organisations
  """
  def __init__(self):
    self.xml_object_tag = 'node'

  def getGidFromObject(self, object):
    """
      Return the Organisation GID of the object.
    """
    return 'Organisation %s' % object.getTitle()

  def getObjectType(self, xml):
    """
      Return the portal type of the object.
    """
    return 'Organisation'

  def updateNode(self, xml=None, object=None, previous_xml=None, force=0,
      simulate=0,  **kw):
    raise Exception("updateNode: Impossible to update Organisation")

  def deleteNode(self, xml=None, object=None, previous_xml=None, force=0,
      simulate=0,  **kw):
    raise Exception("deleteNode: Impossible to delete Organisation")

  def editDocument(self, object=None, **kw):
    """
      This is the editDocument method inherit of ERP5Conduit. This method
      is used to save the information of an Organisation.
    """
    # TODO: Check the list of element to mapping
    # Map the XML tags to the PropertySheet
    mapping = {
        'title': 'title',
        'description': 'description',
    }
    # Translate kw with the PropertySheet
    property = {}
    for k, v in kw.items():
      k = mapping.get(k, k)
      property[k] = v
    object._edit(**property)

