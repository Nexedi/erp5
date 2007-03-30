##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
#
##############################################################################

r"""This module provides an interface for transactional variables.

Transactional variables are data slots which can store arbitrary values
during a transaction. Transactional variables are guaranteed to vanish
when a transaction finishes or aborts, and specific to a single thread and
a single transaction. They are never shared by different threads.

Transactional variables are different from user-defined data in a REQUEST
object, in the sense that one request may execute multiple transactions, but
not vice versa. If data should persist beyond a transaction, but must not
persist over a single request, you should use a REQUEST object instead of
transactional variables.

Also, transactional variables are different from volatile attributes,
because transactional variables may not disappear within a transaction.

The constraint is that each key must be hashable, so that it can be used
as a key to a dictionary.

Example::

  from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
  tv = getTransactionalVariable()
  try:
    toto = tv['toto']
  except KeyError:
    toto = tv['toto'] = getToto()
"""

from UserDict import IterableUserDict
from Shared.DC.ZRDB.TM import TM
from threading import local

class TransactionalVariable(TM, IterableUserDict):
  """TransactionalVariable provides a dict-like look-n-feel.
  This class must not be used directly outside.
  """
  _finalize = None

  def _begin(self, *ignored):
    pass

  def _finish(self, *ignored):
    self.clear()

  def _abort(self, *ignored):
    self.clear()

  def __hash__(self):
    return hash(id(self))

  def __setitem__(self, key, value):
    IterableUserDict.__setitem__(self, key, value)
    self._register()

transactional_variable_pool = local()

def getTransactionalVariable(context):
  """Return a transactional variable."""
  portal = context.portal_url.getPortalObject()
  try:
    instance = transactional_variable_pool.instance
    if getattr(portal, '_v_erp5_transactional_variable', None) is not instance:
      portal._v_erp5_transactional_variable = instance
    return instance
  except AttributeError:
    transactional_variable_pool.instance = TransactionalVariable()
    return getTransactionalVariable(context)
