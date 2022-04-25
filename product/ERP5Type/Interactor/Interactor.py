# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

from MethodObject import Method

"""
  Current implementation uses callable objects.
  Using decorator would be more modern and consistent with
  recent evolution of python. But we have 2.3 ERP5 users
  so we should, at least, provide both implementations.

  Code structure should be changed so that Interactors
  because a new "type" of ERP5 class such Document
  with a modular plugin structure.

  TODO: multiple instances of interactors could
  use different parameters. This way, interactions
  can be defined on "instances" or can be
  made generic.
"""

class InteractorMethodCall:
  """
  Method's wrapper used to keep arguments passed, in order to retrieve them
  from before and after scripts if needed.
  """

  def __init__(self, method, instance, args, kw):
    self.instance = instance
    self.args = args
    self.kw = kw
    self.method = method

  def __call__(self):
    # We use self.__dict__['instance'] to prevent inserting the
    # InteractorMethodCall instance in the acquisition chain
    # which has some side effects
    return self.method(self.__dict__['instance'], *self.args, **self.kw)

class InteractorMethod(Method):
  """
  """

  def __init__(self, method):
    self.after_action_list = []
    self.before_action_list = []
    self.method = method
    self.func_code = method.func_code
    self.func_defaults = method.func_defaults
    self.__name__ = method.__name__

  def registerBeforeAction(self, action, args, kw):
    self.before_action_list.append((action, args, kw))

  def registerAfterAction(self, action, args, kw):
    self.after_action_list.append((action, args, kw))

  def __call__(self, instance, *args, **kw):
    method_call_object = InteractorMethodCall(self.method, instance, args, kw)
    for action, args, kw in self.before_action_list:
      action(method_call_object, *args, **kw)
    result = method_call_object()
    for action, args, kw in self.after_action_list:
      action(method_call_object, *args, **kw)
    return result

class InteractorSource:
  """
  """

  def __init__(self, *args):
    """
      Register method
    """
    if len(args) == 1:
      self.klass = method.im_class
      self.method = method
    else:
      # No im_class on Python3 and Interactors only makes sense with non-ERP5
      # objects anyway, so add a class argument to InteractorSource to make it
      # simple
      self.klass = args[0]
      self.method = getattr(self.klass, args[1])

  def doBefore(self, action, *args, **kw):
    """
    """
    if not isinstance(self.method, InteractorMethod):
      im_class = self.klass
      # Turn this into an InteractorMethod
      interactor_method = InteractorMethod(self.method)
      setattr(im_class, self.method.__name__, interactor_method)
      self.method = interactor_method
    # Register the action
    self.method.registerBeforeAction(action, args, kw)

  def doAfter(self, action, *args, **kw):
    """
    """
    if not isinstance(self.method, InteractorMethod):
      im_class = self.klass
      # Turn this into an InteractorMethod
      interactor_method = InteractorMethod(self.method)
      setattr(im_class, self.method.__name__, interactor_method)
      self.method = interactor_method
    # Register the action
    self.method.registerAfterAction(action, args, kw)

class Interactor:
  """
  Interactor base class.

  TODO:
    - implement uninstall in a generic way
      at the Interactor base class level
  """

  def install(self):
    """
    Install the interactions. This method must be subclassed.
    """
    raise NotImplementedError

  def uninstall(self):
    """
    Uninstall the interactions. Default implementation is provided
    by Interactor base class.
    """
    raise NotImplementedError

  # Interaction implementation
  def on(self, *args):
    """
      Parameters may hold predicates ?
      no need - use InteractorMethodCall and decide on action
    """
    return InteractorSource(*args)
