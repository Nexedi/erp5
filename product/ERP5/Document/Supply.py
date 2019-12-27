# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2002-2009 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Łukasz Nowak <luke@nexedi.com>
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
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Path import Path

class Supply(Path, XMLObject):
  """A Supply defines precise pricing and shipping conditions between
  two trade parties for a limited selection of traded products,
  components, services, etc. It can be used to represent price
  catalogs, product referencing, pricing policy, etc.
  """
  # CMF Type Definition
  meta_type = 'ERP5 Supply'
  portal_type = 'Supply'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Price
                    , PropertySheet.Movement
                    , PropertySheet.Delivery
                    , PropertySheet.Path
                    , PropertySheet.FlowCapacity
                    , PropertySheet.Comment
                    )

  #######################################################
  # Defer indexing process
  def reindexObject(self, *k, **kw):
    """
      Reindex children, as editing properties on Supply need
      to be propagated into predicate table for Supply Line
    """
    self.recursiveReindexObject(*k, **kw)
