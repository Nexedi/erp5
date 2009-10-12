##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
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

import sys

from Products.CMFCore.Expression import Expression
from ZODB.POSException import ConflictError

import Products.PageTemplates.Expressions
# this gets the CompilerError class wherever it is defined (which is different
# depending on the Zope version
CompilerError = Products.PageTemplates.Expressions.getEngine().getCompilerError()

from zLOG import LOG, PROBLEM

from Constraint import Constraint

class TALESConstraint(Constraint):
  """This constraint uses an arbitrary TALES expression on the context of the
  object; if this expression is evaluated as False, the object will be
  considered in an inconsistent state.
    
    Configuration example:
    { 'id'            : 'tales_constraint',
      'description'   : 'Title should not be equals to foo',
      'type'          : 'TALESConstraint',
      'expression'    : 'python: object.getTitle() != 'foo',
    },

  For readability, please don't abuse this constraint to evaluate complex
  things. If necessary, write your own constraint class.
  """
  
  _message_id_list = [ 'message_expression_false',
                       'message_expression_error' ]

  message_expression_false = "Expression was false"
  message_expression_error = \
      "Error while evaluating expression: ${error_text}"

  def checkConsistency(self, obj, fixit=0):
    """Check the object's consistency.
    """
    # import this later to prevent circular import
    from Products.ERP5Type.Utils import createExpressionContext
    if not self._checkConstraintCondition(obj):
      return []
    error_list = []
    expression_text = self.constraint_definition['expression']
    expression = Expression(expression_text)
    econtext = createExpressionContext(obj)
    try:
      if not expression(econtext):
        error_list.append(self._generateError(obj,
                  self._getMessage('message_expression_false')))
    except (ConflictError, CompilerError):
      raise
    except Exception, e:
      LOG('ERP5Type', PROBLEM, 'TALESConstraint error on "%s" on %s' %
         (self.constraint_definition['expression'], obj), error=sys.exc_info())
      error_list.append(self._generateError(obj,
                  self._getMessage('message_expression_error'),
                  mapping=dict(error_text=str(e))))
    return error_list

