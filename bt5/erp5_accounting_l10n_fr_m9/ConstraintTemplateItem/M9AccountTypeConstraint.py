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

from Products.ERP5.Constraint.AccountTypeConstraint import \
                                  AccountTypeConstraint

class M9AccountTypeConstraint(AccountTypeConstraint):
  """Account type constraints specific to erp5_accounting_l10n_fr_m9
  """
  _account_type_map = (
    ('gap/fr/m9/1', ('equity', )),
    ('gap/fr/m9/2', ('asset', )),
    ('gap/fr/m9/3', ('asset', )),
    ('gap/fr/m9/4/40', ('liability/payable', )),
    ('gap/fr/m9/4/41', ('asset/receivable', )),
    ('gap/fr/m9/4/42', ('liability/payable', )),
    ('gap/fr/m9/4/43', ('liability/payable', )),
    ('gap/fr/m9/4/47/471/4718', ('asset/receivable', )),
    ('gap/fr/m9/4/47/472/4721', ('liability/payable', )),
    ('gap/fr/m9/4/47/473/4731', ('asset/receivable', )),
    ('gap/fr/m9/4/47/473/4735', ('liability/payable', )),
    ('gap/fr/m9/4', ('liability/payable', 'asset/receivable')),
    ('gap/fr/m9/5/59', ('asset', )),
    ('gap/fr/m9/5', ('asset/cash', )),
    ('gap/fr/m9/6', ('expense', )),
    ('gap/fr/m9/7', ('income', )),
    ('gap/fr/m9/8', ('equity', )),
  )

