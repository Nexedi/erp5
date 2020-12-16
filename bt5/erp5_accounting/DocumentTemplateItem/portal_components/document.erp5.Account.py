##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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
from Products.ERP5.Document.Node import Node


class Account(Node):
  """An account is an abstract node which holds currencies and is used in
  accounting.

  Accounts are member of categories that are used to do aggregated reporting
  of accounting movements. Typically, the following categories are used::
    * GAP: This category represents the classification as defined by the
      legislations that the organisatation have to comply to. Accounts can be
      associated to multiple GAP category trees at the same time, and
      therefore it allows to generate reports for multiple legislations from
      the same accounting data.
    * Financial Section: This category is the representation of the financial
      structure as seen by the company, regardless of the fiscal
      requirements.  Balance Sheets and Profit & Loss reports can be
      generated using those categories.
    * Account Type: This category is used to describe what is the type of
      this account, and usually has impact on the behaviour of the
      application and reportings. For instance, when using a "payable"
      account in an accounting transaction, we set the supplier organisation
      as mirror section, and reports such as trial balance can display a
      breakdown of this account for each supplier.
  """
  meta_type = 'ERP5 Account'
  portal_type = 'Account'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Account
                    , PropertySheet.Arrow
                    , PropertySheet.Reference
                    )
