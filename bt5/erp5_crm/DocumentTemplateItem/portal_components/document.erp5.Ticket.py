##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5.Document.Project import Project

class Ticket(Project):
  """
  A Ticket allows to track a sales process involving
  multilple Person and Organisations. It is a placeholder for
  documents, events, etc.

  Tickets behave both a movements and as projects:

  - as movements because they relate to an amount
    of resource exchanged between multiple parties

  - as a project because it acts as a reporting
    node for other movements (ex. accounting,
    task reports)

  Ticket are a good example of documents which may require
  synchronisation process accross multiple sites and
  for which acquisition properties such as source_title
  may be useful to provide a simple way to synchronise
  data with relations.
  """
  meta_type = 'ERP5 Ticket'
  portal_type = 'Ticket'
  add_permission = Permissions.AddPortalContent
  isDelivery = ConstantGetter('isDelivery', value=True)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Arrow
                    , PropertySheet.Price
                    , PropertySheet.Movement
                    , PropertySheet.Amount
                    , PropertySheet.Ticket
                    )

  security.declareProtected(Permissions.AccessContentsInformation, 'isAccountable')
  def isAccountable(self):
    """Tickets are accountable.
    """
    return 1