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

import warnings
from threading import local
from transaction import get as get_transaction
import transaction.interfaces
import zope.interface

@zope.interface.implementer(transaction.interfaces.IDataManager)
class TransactionalVariable(dict):
  """TransactionalVariable provides a dict-like look-n-feel.
  This class must not be used directly outside.
  """

  _unregistered = True

  def sortKey(self):
    return chr(0)

  commit = tpc_vote = tpc_begin = tpc_abort = lambda self, transaction: None

  def abort(self, txn):
    self._unregistered = True
    self.clear()

  tpc_finish = abort

  # override all methods that may add entries to the dict

  def __setitem__(self, key, value):
    if self._unregistered:
      get_transaction().join(self)
      self._unregistered = False
    return dict.__setitem__(self, key, value)

  def setdefault(self, key, failobj=None):
    if self._unregistered:
      get_transaction().join(self)
      self._unregistered = False
    return dict.setdefault(self, key, failobj)

  def update(self, *args, **kw):
    if self._unregistered:
      get_transaction().join(self)
      self._unregistered = False
    return dict.update(self, *args, **kw)

transactional_variable_pool = local()

def getTransactionalVariable():
  """Return a transactional variable."""
  try:
    return transactional_variable_pool.instance
  except AttributeError:
    tv = TransactionalVariable()
    transactional_variable_pool.instance = tv
    return tv


@zope.interface.implementer(transaction.interfaces.IDataManager)
class TransactionalResource(object):

  def __init__(self, transaction_manager=None, **kw):
    if transaction_manager is None:
      from transaction import manager as transaction_manager
    self.__dict__.update(kw, transaction_manager=transaction_manager)
    transaction_manager.get().join(self)

  @classmethod
  def registerOnce(cls, *args):
    tv = getTransactionalVariable().setdefault(cls, set())
    return not (args in tv or tv.add(args))

  def sortKey(self):
    return chr(1)

  abort = commit = tpc_vote = tpc_begin = tpc_finish = tpc_abort = \
    lambda self, transaction: None
