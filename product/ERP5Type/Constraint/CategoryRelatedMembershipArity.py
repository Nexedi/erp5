# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

from __future__ import absolute_import
from .Constraint import Constraint
from Products.ERP5Type.Constraint.CategoryMembershipArity \
          import CategoryMembershipArity

class CategoryRelatedMembershipArity(CategoryMembershipArity):
  """
    This method checks if an object respects the arity from a category reverse
    membership point of view.

    For example we can check if every Order has at
    most one Order Applied Rule.
    Configuration example:
    { 'id'            : 'applied_rule',
      'description'   : 'There must at most one Applied Rule using this order',
      'type'          : 'CategoryRelatedMembershipArity',
      'min_arity'     : '1',
      'max_arity'     : '1',
      'portal_type'   : ('Applied Rule', ),
      'base_category' : ('causality',)
      'condition'     : 'python: object.getPortalType() == 'Foo',
    },

  additional parameters passed to catalog are accepted:
    'filter_parameter': {'simulation_state': ('planned',)},
  """

  def _calculateArity(self, obj):
    base_category = self.constraint_definition['base_category']
    sql_kw = {'portal_type': self.constraint_definition['portal_type'],
              '%s_uid' % base_category: obj.getUid()}
    filter_parameter = self.constraint_definition.get('filter_parameter', {})
    sql_kw.update(filter_parameter)
    portal = obj.getPortalObject()
    return len(portal.portal_catalog.unrestrictedSearchResults(**sql_kw))

