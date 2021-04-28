# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#                    Jean-Paul Smets <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
#                    Nicolas Delaby <nicolas@nexedi.com>
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

from __future__ import absolute_import
from .PropertyExistence import PropertyExistence
from Products.CMFCore.Expression import Expression

class AttributeUnicity(PropertyExistence):
  """
    This constraint class allows to check
    attribute unicity.
    Configuration example:
    { 'id'            : 'title',
      'description'   : 'Title must be unique',
      'type'          : 'AttributeUnicity',
      'title': "python: {'portal_type': object.getPortalType(), 'title': object.getTitle(), 'validation_state': 'validated'}",
      'condition' : 'object/getTitle',
    },
  """

  _message_id_list = ['message_invalid_attribute_unicity',]

  message_invalid_attribute_unicity = "Attribute ${attribute_name} "\
       "value is ${value} but should be unique"

  def _checkConsistency(self, obj, fixit=0):
    """Check the object's consistency.
      We will make sure that each non None constraint_definition is
      satisfied (unicity)
      This Constraint use portal_catalog
    """
    errors = PropertyExistence._checkConsistency(self, obj, fixit=fixit)
    for attribute_name, expression_criterion_dict in self.constraint_definition.items():
      message_id = None
      mapping = dict(attribute_name=attribute_name)
      #Evaluate expression_criterion_dict
      expression = Expression(expression_criterion_dict)
      from Products.ERP5Type.Utils import createExpressionContext
      econtext = createExpressionContext(obj)
      criterion_dict = expression(econtext)
      from Products.ZSQLCatalog.SQLCatalog import Query, NegatedQuery
      # Add uid in criterion keys to avoid fetching current object.
      criterion_dict['query'] = NegatedQuery(Query(uid=obj.getUid()))
      portal = obj.getPortalObject()
      result = portal.portal_catalog.countResults(**criterion_dict)[0][0]
      if result >= 1:
        mapping['value'] = criterion_dict.get(attribute_name)
        message_id = 'message_invalid_attribute_unicity'
      # Generate error
      if message_id is not None:
        errors.append(self._generateError(obj,
                        self._getMessage(message_id), mapping))
    return errors

