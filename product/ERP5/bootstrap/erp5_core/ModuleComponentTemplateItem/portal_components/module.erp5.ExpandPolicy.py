# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SARL and Contributors. All Rights Reserved.
#          Julien Muchembled <jm@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

##############################################################################

import six
from time import time
import transaction
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5Type.Utils import convertToLowerCase
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

# XXX: Consider moving it to ERP5Type if it implements recursion policies
#      for anything other than expand.

# XXX: Policy of deferred expands currently is currently hardcoded to the
#      preferred one, which is itself hardcoded to "vertical_time_bound".
#      If any parameter is added to policies in order to make them customizable,
#      Base class should probably handle this automatically by:
#      - keeping all parameters in a 'kw' attribute and;
#      - activating with something like 'expand(policy, **self.kw)'
#      It may also be better if that 'kw' does not mix up several kinds of
#      parameters, for example those that are specific to the policy
#      (e.g. policy_kw), and other for expand() itself (e.g. expand_kw).
#      Any extension to the API must be reviewed first.

# Put there to avoid circular import loop.
TREE_DELIVERED_CACHE_KEY = 'AppliedRule._isTreeDelivered'

policy_dict = {} # {None: preferred, 'foo_bar': FooBar}

VERTICAL_EXPAND_TIMEOUT = 5  # XXX: hardcoded for the moment

class _PolicyMetaClass(type):
  """Automatically register policies in policy_dict"""
  def __init__(cls, name, bases, d):
    type.__init__(cls, name, bases, d)
    if name[0] != '_':
      policy_dict[convertToLowerCase(name)[1:]] = cls


class _Policy(six.with_metaclass(_PolicyMetaClass, object)):
  """Base class of policies for RuleMixin.expand and SimulationMovement.expand
  """
  def __init__(self, activate_kw=None):
    self.activate_kw = activate_kw

  @UnrestrictedMethod
  def expand(self, *args):
    """Initialize context, and really start to expand"""
    tv = getTransactionalVariable()
    assert TREE_DELIVERED_CACHE_KEY not in tv, "already expanding"
    self.context = args[-1]
    with self.context.defaultActivateParameterDict(self.activate_kw, True):
      tv[TREE_DELIVERED_CACHE_KEY] = {}
      try:
        self(*args)
      finally:
        del tv[TREE_DELIVERED_CACHE_KEY]

  # lazy computation of root applied rule path
  def __getattr__(self, attr):
    if attr == 'merge_parent':
      self.merge_parent = value = self.context.getRootAppliedRule().getPath()
    else:
      value = object.__getattribute__(self, attr)
    return value

  def deferAll(self):
    self.test = self.activate

  def activate(self, context):
    context.activate(merge_parent=self.merge_parent) \
           .expand(activate_kw=self.activate_kw)

  def __call__(self, *args):
    context = args[-1]
    if self.test(context):
      args[0]._expandNow(self, *args[1:])

class Deferred(_Policy):
  """Do not expand anything in the current transaction, but do it by activity"""

  # We won't expand at all so we override expand() to avoid wasting time on
  # initializing anything.
  def expand(self, *args):
    context = args[-1]
    kw = self.activate_kw
    context.activate(merge_parent=context.getRootAppliedRule().getPath(),
                     **(kw or {})).expand(activate_kw=kw)

class Immediate(_Policy):
  """Expand everything immediately"""

  # Optimize by overriding '__call__' instead of 'test'
  #test = lambda *args: True
  def __call__(self, *args):
    args[0]._expandNow(self, *args[1:])

class VerticalTimeBound(_Policy):
  """Vertical recursion, limited by duration

  Expand immediately only if the current transaction is young enough.
  Defer by activity otherwise.
  """

  def __init__(self, **kw):
    super(VerticalTimeBound, self).__init__(**kw)
    self.stop = transaction.get().start_time + VERTICAL_EXPAND_TIMEOUT

  def test(self, context): # pylint: disable=method-hidden
    if time() < self.stop:
      return True
    self.deferAll()
    self.test(context)

# XXX: Should be a function reading system preferences
preferred = VerticalTimeBound

policy_dict[None] = preferred
