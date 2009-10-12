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

from Products.ERP5Type import interfaces, Permissions
from Products.ERP5Type.Context import Context
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5.Variated import Variated

from zope.interface import implements

def newVariationValue(context=None, REQUEST=None, **kw):
    # Create context object
    context_obj = VariationValue(context=context, REQUEST=REQUEST, **kw)
    # Wrap the context
    if context is not None:
      return context_obj.asContext(context = context)
    else:
      return context_obj

class VariationValue(Context, Variated):
  """
    Embodies a variation value. Implements discrete variations.
  """

  # Declarative interfaces
  implements(interfaces.IVariated)

  def __init__(self, context=None, REQUEST=None, **kw):
    Context.__init__(self, context=context, REQUEST=REQUEST, **kw)
    if hasattr(self, 'categories'):
      self.categories = getattr(self,'categories')
    elif hasattr(REQUEST,'categories'):
      self.categories = getattr(REQUEST,'categories')
    else:
      self.categories = context.getVariationCategoryList()

  def setVariationValue(self, context):
    context.setVariationCategoryList(self.categories)

  def __cmp__(self, other):
    same = 0
    a = getattr(self, 'categories', ())
    b = getattr(other, 'categories', ())
    for ka in a:
      if not ka in b:
        same = 1
    for kb in b:
      if not kb in a:
        same = -1
    return same

InitializeClass(VariationValue)
