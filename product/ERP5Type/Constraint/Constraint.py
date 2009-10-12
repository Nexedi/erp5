##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#                    Jean-Paul Smets <jp@nexedi.com>
#                    Courteaud Romain <romain@nexedi.com>
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

from Products.CMFCore.Expression import Expression
from Products.ERP5Type.interfaces import IConstraint
from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage
from zope.interface import implements

class Constraint:
    """
      Default Constraint implementation
    """
    implements( IConstraint, )

    _message_id_list = []

    def __init__(self, id=None, description=None, type=None,
                 condition=None, **constraint_definition):
      """Initialize a constraint.
      """
      self.id = id
      self.description = description
      self.type = type
      self.constraint_definition = dict()
      self.message_id_dict = dict()
      self.edit(id, description, type, condition, **constraint_definition)

    def edit(self, id=None, description=None, type=None, condition=None,
        **constraint_definition):
      """Edit the constraint instance.
      """
      if id is not None:
        self.id = id
      if description is not None:
        self.description = description
      if type is not None:
        self.type = type
      self.condition = condition
      for key, value in constraint_definition.items():
        if key in self._message_id_list:
          self.message_id_dict[key] = value
        else:
          self.constraint_definition[key] = value

    def _getMessage(self, message_id):
      """Get the message corresponding to this message_id.
      """
      if message_id in self.message_id_dict:
        return self.message_id_dict[message_id]
      return getattr(self, message_id)
      
    def _generateError(self, obj, error_message, mapping={}):
      """Generic method used to generate error in checkConsistency.
      """
      if error_message is not None:
        msg = ConsistencyMessage(self, 
                                 object_relative_url=obj.getRelativeUrl(),
                                 message=error_message, 
                                 mapping=mapping)
        return msg

    def _checkConstraintCondition(self, obj):
      """
        method that will check if the TALES condition is true.
        It should be called by checkConsistency, which should ignore
        constraints if TALES is False
      """
      from Products.ERP5Type.Utils import createExpressionContext
      condition = getattr(self, 'condition', None)
      if condition not in (None, ''):
        expression = Expression(condition)
        econtext = createExpressionContext(obj)
        if not expression(econtext):
          return 0 # a condition was defined and is False
      return 1 # no condition or a True condition was defined

    def checkConsistency(self, obj, fixit=0):
      """
        Default method is to return no error.
      """
      errors = []
      return errors

    def fixConsistency(self, obj):
      """
        Default method is to call checkConsistency with
        fixit set to 1
      """
      return self.checkConsistency(obj, fixit=1)

