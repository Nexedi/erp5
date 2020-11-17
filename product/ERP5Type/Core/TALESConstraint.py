##############################################################################
#
# Copyright (c) 2006-2010 Nexedi SARL and Contributors. All Rights Reserved.
#                         Jerome Perrin <jerome@nexedi.com>
#                         Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
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
from zLOG import LOG, PROBLEM
from ZODB.POSException import ConflictError

import Products.PageTemplates.Expressions
# this gets the CompilerError class wherever it is defined (which is
# different depending on the Zope version
CompilerError = Products.PageTemplates.Expressions.getEngine().getCompilerError()

class TALESConstraint(ConstraintMixin):
  """
  This constraint uses an arbitrary TALES expression on the context of the
  object; if this expression is evaluated as False, the object will be
  considered in an inconsistent state.

  This is only relevant for ZODB Property Sheets (filesystem Property
  Sheets rely on Products.ERP5Type.Constraint.TALESConstraint
  instead).

  For example, if we would like to check whether the expression
  'python: object.getTitle() != 'foo'' is False, then we would create
  a 'TALES Constraint' within that Property Sheet and set 'Expression'
  to 'python: object.getTitle() != 'foo'', then set the 'Predicate' if
  necessary (known as 'condition' for filesystem Property Sheets).

  For readability, please don't abuse this constraint to evaluate complex
  things. If necessary, write your own constraint class.
  """
  meta_type = 'ERP5 TALES Constraint'
  portal_type = 'TALES Constraint'

  property_sheets = ConstraintMixin.property_sheets + \
                    (PropertySheet.TALESConstraint,)

  def _checkConsistency(self, obj, fixit=0):
    """
    Check that the Expression does not contain an error and is not
    evaluated to False
    """
    expression_text = self.getExpression()

    try:
      if not self._getExpressionValue(obj, expression_text):
        return [self._generateError(obj,
                                    self._getMessage('message_expression_false'))]
    except (ConflictError, CompilerError):
      raise
    except Exception as e:
      LOG('ERP5Type', PROBLEM, 'TALESConstraint error on "%s" on %s' %
          (expression_text, obj), error=True)

      return [self._generateError(obj,
                                  self._getMessage('message_expression_error'),
                                  mapping=dict(error=str(e)))]

    return []

  _message_id_tuple = ('message_expression_false',
                       'message_expression_error')

  @staticmethod
  def _convertFromFilesystemDefinition(expression):
    yield dict(expression=expression)
