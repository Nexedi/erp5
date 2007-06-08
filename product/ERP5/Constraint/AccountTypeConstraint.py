##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#          Jerome Perrin <jerome@nexedi.com>
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

from Products.ERP5Type.Constraint import Constraint
from Products.ERP5Type.Message import Message
N_ = lambda msg: msg
_MARKER = []

class AccountTypeConstraint(Constraint):
  """Account type constraint is a base class to check that account_type
  category is consistent with the gap category.
  This is an abstract class, subclasses have to define a mapping as a class
  attribute, like this one:
  
  _account_type_map = (
    ('gap/fr/pcg/4/40', ('liability/payable',),
    ('gap/fr/pcg/4', ('asset/receivable', 'liability/payable'),
  )

  In this example, the constraint will check that if 'gap/fr/pcg/4' is used, we
  must be member of 'account_type/asset/receivable' or
  'account_type/liability/payable'.
  The order is important, ie. that if the account is member of
  'gap/fr/pcg/4/40', it must be member of 'account_type/liability/payable'.

  This constraints supports fixing consistency.
  """

  def checkConsistency(self, obj, fixit=0):
    """Implement here the consistency checker
    """
    errors = []
    if getattr(obj, 'getAccountType', _MARKER) is _MARKER:
      errors.append(self._generateError(obj,
                N_("Account doesn't have account_type category")))
    else:
      account_type_map = getattr(self, '_account_type_map', ())
      if not account_type_map:
        raise NotImplementedError(
            "AccountTypeConstraint doesn't define an _account_type_map")
      found = 0
      for category, account_type_list in account_type_map:
        if obj.isMemberOf(category):
          if obj.getAccountType() not in account_type_list:
            errors.append(self._generateError(obj,
                N_("Account is member of ${category}, thus should have"
                   " account_type in ${account_type_list}"),
                # XXX we should probably print translated logical path of
                # categories instead of category path.
                    mapping=dict(category=category,
                                 account_type_list=
                                    ', '.join(account_type_list))))
            if fixit:
              obj.setAccountType(account_type_list[0])
          break
    return errors

