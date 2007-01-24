##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Cache import CachingMethod
from zLOG import LOG

class BankAccountReference(Constraint):
  """
    This constraint checks that the bank account follow
    the bank settings (len of field) :

    bank_country_code (1)
    bank_code (4)
    branch (5)
    bank_account_number (12)
    bank_account_key (2)
    
    Configuration example:
    { 'id'            : 'bank_account_reference',
      'description'   : 'bank properties must be correct',
      'type'          : 'BankAccountReference',
    },
  """

  def checkConsistency(self, obj, fixit=0):
    """
      This is the check method, we return a list of string,
      each string corresponds to an error.
    """
    if not self._checkConstraintCondition(obj):
      return []
    errors = []
    error_message = None

    def checkLen(property,size):
      value = obj.getProperty(property)
      if value is None:
        error_message = "%s is not defined" % property
        errors.append(self._generateError(obj, error_message))
      elif len(value) != size:
        error_message = "%s must have a lenth of $size" % property
        errors.append(self._generateError(obj, error_message,
                                          mapping={'size':size}))

    checkLen('bank_country_code',1)
    checkLen('bank_code',4)
    checkLen('branch',5)
    checkLen('bank_account_number',12)
    checkLen('bank_account_key',2)
    return errors

