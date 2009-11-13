# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#               Jean-a
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

class SolverSelection:
  """
    Solver Selection provides provides properties to 
    store a selection of solver portal types.
  """

  _properties = (
    # XXX - this can not work and must be moved to MixIn (pt of pt)
    {   'id'          : 'delivery_solver_id',
        'description' : 'The ID the delivery solver which is selected',
        'type'        : 'string',
        'acquisition_base_category'     : ('solver',),
        'acquisition_portal_type'       : Expression('python:portal.getPortalDeliverySolverTypeList()'),
        'acquisition_copy_value'        : 0,
        'acquisition_accessor_id'       : 'getId',
        'acquisition_depends'           : None,
        'mode'        : 'r' },
    {   'id'          : 'target_solver_id',
        'description' : 'The title of the source organisation of this movement',
        'type'        : 'string',
        'acquisition_base_category'     : ('solver',),
        'acquisition_portal_type'       : Expression('python:portal.getPortalTargetSolverTypeList()'),
        'acquisition_copy_value'        : 0,
        'acquisition_accessor_id'       : 'getId',
        'acquisition_depends'           : None,
        'mode'        : 'r' },
  )

  _categories = ('solver',)
