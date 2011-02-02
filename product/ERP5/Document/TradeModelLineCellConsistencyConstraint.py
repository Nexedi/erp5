##############################################################################
#
# Copyright (c) 2009-2010 Nexedi SA and Contributors. All Rights Reserved.
#                         Fabien Morin <fabien@nexedi.com>
#                         Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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

from Products.ERP5Type.mixin.constraint import ConstraintMixin
from Products.ERP5Type import PropertySheet

class TradeModelLineCellConsistencyConstraint(ConstraintMixin):
  """
  This constraint checks if the Trade Model Line should contain cells (if
  variation categories are defined on it)

  This is only relevant for ZODB Property Sheets (filesystem Property
  Sheets rely on Products.ERP5.Constraint.TradeModelLineCellConsistency
  instead).
  """
  meta_type = 'ERP5 Trade Model Line Cell Consistency Constraint'
  portal_type = 'Trade Model Line Cell Consistency Constraint'

  __compatibility_class_name__ = 'TradeModelLineCellConsistency'

  property_sheets = ConstraintMixin.property_sheets + \
                    (PropertySheet.TradeModelLineCellConsistencyConstraint,)

  def _checkConsistency(self, document, fixit=0):
    """
    Check the object's consistency
    """
    base_id = self.getBaseId()
    for cell_coordinates in document.getCellKeyList(base_id=base_id):
      if document.getCell(base_id=base_id, *cell_coordinates) is None:
        return [self._generateError(
          document, self._getMessage('message_cell_inexistance'),
          mapping=dict(line=document.getTitle()))]

    return []

  _message_id_tuple = ('message_cell_inexistance',)

  @staticmethod
  def _convertFromFilesystemDefinition(base_id):
    """
    @see ERP5Type.mixin.constraint.ConstraintMixin._convertFromFilesystemDefinition
    """
    yield dict(base_id=base_id)

  def exportToFilesystemDefinitionDict(self):
    filesystem_definition_dict = super(TradeModelLineCellConsistencyConstraint,
                                       self).exportToFilesystemDefinitionDict()

    filesystem_definition_dict['base_id'] = self.getBaseId()

    return filesystem_definition_dict
