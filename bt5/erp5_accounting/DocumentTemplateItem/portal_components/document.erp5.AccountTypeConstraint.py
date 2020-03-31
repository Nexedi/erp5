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

from Products.ERP5Type.mixin.constraint import ConstraintMixin
from Products.ERP5Type import PropertySheet
translateString = lambda msg: msg  # just to extract messages
_MARKER = []

class AccountTypeConstraint(ConstraintMixin):
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

  property_sheets = ConstraintMixin.property_sheets + \
                    (PropertySheet.AccountTypeConstraint,)

  def _checkConsistency(self, obj, fixit=0):
    """Implement here the consistency checker
    """
    # self, the constraint is a temp object without acquisition wrappers, for
    # now we need to add acquisition wrappers for category accessors
    self_in_context = self.__of__(obj.getPortalObject())
    error_list = []
    errors = []
    if getattr(obj, 'getAccountType', _MARKER) is _MARKER:
      errors.append(self._generateError(
        obj,
        translateString("Account does not have account_type category")))
    else:
      constraint_line_list = self_in_context.objectValues(sort_on='int_index')
      if len(constraint_line_list) == 0:
        raise NotImplementedError(
           "AccountTypeConstraint does not define an account type mapping lines")
      for constraint_line in constraint_line_list:
        gap = constraint_line.getGap(base=1)
        account_type_list = constraint_line.getAccountTypeList()
        if obj.isMemberOf(gap):
          if obj.getAccountType() not in account_type_list:
            error_list.append(self._generateError(obj,
                self._getMessage('message_inconsistent_account_type'),
                # XXX we should probably print translated logical path of
                # categories instead of category path.
                    mapping=dict(category=gap,
                                 account_type_list=
                                    ', '.join(account_type_list))))
            if fixit:
              obj.setAccountType(account_type_list[0])
          break
    return error_list

  _message_id_tuple = ('message_inconsistent_account_type',)
