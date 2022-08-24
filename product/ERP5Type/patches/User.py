##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2012 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from threading import local
from Acquisition import aq_inner, aq_parent
from AccessControl.PermissionRole import _what_not_even_god_should_do
from AccessControl.User import BasicUser, SimpleUser
from App.config import getConfiguration
from ..TransactionalVariable import TransactionalVariable

DEVELOPER_ROLE_ID = 'Developer'

SimpleUser_getRoles = SimpleUser.getRoles
def getRoles(self, _transactional_variable_pool=local()):
  """
  Add Developer Role if the user has been explicitely set as Developer in Zope
  configuration file
  """
  role_tuple = tuple(
    x
    for x in SimpleUser_getRoles(self)
    if x != DEVELOPER_ROLE_ID
  )
  # Use our private transactional cache pool, to avoid code meddling with
  # roles. Hide it in a default parameter value to make it harder to access
  # than just importing it from the module.
  try:
    tv = _transactional_variable_pool.instance
  except AttributeError:
    tv = TransactionalVariable()
    _transactional_variable_pool.instance = tv
  try:
    extra_role_tuple = tv[('user_extra_role_tuple', self.getId())]
  except KeyError:
    tv[('user_extra_role_tuple', self.getId())] = extra_role_tuple = (
      (DEVELOPER_ROLE_ID, )
      if self.getId() in getattr(
        getattr(
          getConfiguration(),
          'product_config',
          {},
        ).get('erp5'),
        'developer_list',
        (),
      ) else
      ()
    )
  return role_tuple + extra_role_tuple

SimpleUser.getRoles = getRoles
