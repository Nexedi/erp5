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


from Acquisition import aq_base
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Base import TempBase

from zLOG import LOG

def newContext(context=None, REQUEST=None, **kw):
    # Create context object
    context_obj = Context(context=context, REQUEST=REQUEST, **kw)
    # Wrap the context
    if context is not None:
      return context_obj.asContext(context = context)
    else:
      return context_obj

class Context(TempBase):
  """
    Context objects are used all over ERP5 in so-called context
    dependent function. Examples of context dependent methods
    include:

      - price methods (price depends on the context: customer,
        quantity, etc.)

      - BOM methods
  """

  def __init__(self, context=None, REQUEST=None, **kw):
    """
      context   --  The

      REQUEST   -- the request object

      kw        -- user specified parameters
    """
    # Copy REQUEST properties to self
    if REQUEST is not None:
      self.__dict__.update(REQUEST)
    # Define local properties
    if kw is not None: self.__dict__.update(kw)

  def asContext(self, context=None, REQUEST=None, **kw):
    """
      Update args of context
    """
    # Copy REQUEST properties to self
    if REQUEST is not None:
      aq_base(self).__dict__.update(REQUEST)
    # Define local properties
    if kw is not None: aq_base(self).__dict__.update(kw)
    # Wrap context
    if context is not None:
      return self.__of__(context)
    else:
      return self

InitializeClass(Context)
