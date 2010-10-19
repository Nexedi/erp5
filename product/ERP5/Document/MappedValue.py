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

from Products.ERP5Type.Core.Predicate import Predicate
from Products.ERP5.Document.Amount import Amount

class MappedValue(Predicate, Amount):
  """
    A MappedValue allows to associate a value to a domain

    Although MappedValue are supposed to be independent of any
    design choice, we have to implement them as subclasses of
    Amount in order to make sure they provide a complete
    variation interface. In particular, we want to be able
    to call getVariationValue / setVariationValue on a
    MappedValue.

    XXX - Amount should be remove from here
    
    
    Interesting Idea: properties and categories of the mapped value
    (not of the predicate) could be handled through additional matrix
    dimensions rather than through ad-hoc definition.    
  """
  meta_type = 'ERP5 Mapped Value'
  portal_type = 'Mapped Value'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.CategoryCore
                      , PropertySheet.Predicate
                      , PropertySheet.MappedValue
                    )

  def _edit(self, **kw):
    # We must first prepare the mapped value before we do the edit
    edit_order = ['mapped_value_property_list',
                  'default_mapped_value_property',
                  'mapped_value_property',
                  'mapped_value_property_set']
    i = len(edit_order)
    edit_order += [x for x in kw.pop('edit_order', ()) if x not in edit_order]
    # Base._edit updates unordered properties first
    edit_order[i:i] = [x for x in kw if x not in edit_order]
    return Predicate._edit(self, edit_order=edit_order, **kw)
