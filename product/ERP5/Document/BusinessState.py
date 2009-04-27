##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject

class BusinessState(XMLObject):
  """
    The BusinessProcess class is a container class which is used
    to describe business processes in the area of trade, payroll
    and production.
  """
  meta_type = 'ERP5 Business State'
  portal_type = 'Business State'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Folder
                    , PropertySheet.Comment
                    )

  # Core API
  def isCompleted(self, explanation):
    """
      If all path which reach this state are completed
      then this state is completed
    """
    for path in self.getSuccessorRelatedValueList():
      if not path.isCompleted(explanation):
        return False
    return True


  def isPartiallyCompleted(self, explanation):
    """
      If all path which reach this state are partially completed
      then this state is completed
    """
    for path in self.getSuccessorRelatedValueList():
      if not path.isPartiallyCompleted(explanation):
        return False
    return True

  # Duration calculation
  def getExpectedCompletionDate(self, explanation):
    """
      Returns the expected completion date for this
      state based on the explanation.
    """

  def getExpectedCompletionDuration(self, explanation):
    """
      Returns the expected completion duration for this
      state.
    """
