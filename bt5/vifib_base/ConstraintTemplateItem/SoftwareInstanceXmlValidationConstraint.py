##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Lukasz Nowak <luke@nexedi.com>
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

from Products.ERP5Type.Constraint import Constraint
from lxml import etree
from slapos import slap
import pkg_resources

class SoftwareInstanceXmlValidationConstraint(Constraint):
  """
    Checks that Software Instance's XML is valid against its DSD.
  """

  _message_id_list = [ 'message_xml_invalid', 'message_xml_garbaged',\
                       'message_no_xml' ]

  message_xml_garbaged = "The string is not XML at all."
  message_xml_invalid = "The XML failed validation with error: ${xml_error}"
  message_no_xml = "No XML is set"

  def checkConsistency(self, obj, fixit=0):
    """Checks that Software Instance's XML is valid.
    """
    error_list = []
    if self._checkConstraintCondition(obj):
      xml_schema = etree.XMLSchema(
            file=pkg_resources.resource_filename(
              slap.__name__, 'doc/software_instance.xsd'))
      try:
        tree = etree.fromstring(obj.getTextContent())
      except etree.XMLSyntaxError:
        error_list.append(self._generateError(obj,
                            self._getMessage('message_xml_garbaged')))
      except ValueError:
        error_list.append(self._generateError(obj,
                            self._getMessage('message_no_xml')))
      else:
        if not xml_schema.validate(tree):
          mapping = {}
          mapping['xml_error'] = xml_schema.error_log.filter_from_errors()[0]
          error_list.append(self._generateError(obj,
                              self._getMessage('message_xml_garbaged'),
                              mapping))
    return error_list

