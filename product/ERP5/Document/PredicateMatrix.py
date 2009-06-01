##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.Rule import Rule
from Products.ERP5Type.XMLMatrix import XMLMatrix

from zLOG import LOG, BLATHER, INFO, PROBLEM

class PredicateMatrix(XMLMatrix):
  """
    PredicateMatrix implements a matrix of predicates, and
    allows to get cell that match predicates.
  """

  # CMF Type Definition
  meta_type = 'ERP5 Predicate Matrix'
  portal_type = 'Predicate Matrix'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  predicate_matrix_base_id = "movement"

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    )
  
  def _getMatchingCell(self, movement):
    """
      Browse all cells and test them until match found
    """
    for cell in self.getCellValueList(
                        base_id=self.predicate_matrix_base_id) :
      if cell.test(movement):
        return cell
    return None          
  
  security.declareProtected( Permissions.AccessContentsInformation,
                             'getMatchingCell' )
  getMatchingCell = _getMatchingCell
  
  security.declareProtected(Permissions.ModifyPortalContent, 'updateMatrix')
  def updateMatrix(self) :
    """
      This methods updates the matrix so that cells are consistent
    with the predicates.
    """
    base_id = self.predicate_matrix_base_id
    kwd = {'base_id': base_id}
    self._updateCellRange(base_id) # calls PT dependant script.
    
    cell_range_key_list = self.getCellRangeKeyList(base_id = base_id)
    if cell_range_key_list != [[None, None]] :
      for k in cell_range_key_list :
        c = self.newCell(*k, **kwd)
        c.edit( mapped_value_property_list = ( 'title',),
                predicate_category_list = [self._getOb(k_item).getRelativeUrl()
                                           for k_item in k],
                title = " * ".join(map(lambda k_item : \
                        self.unrestrictedTraverse(k_item).getTitle(), k)),
                force_update = 1
              )
    else :
      # If empty matrix, delete all cells
      cell_range_id_list = self.getCellRangeIdList(base_id = base_id)
      for k in cell_range_id_list :
        if self.get(k) is not None :
          self.deleteContent(k)
    
