##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

class Task:
    """
        Properties which allow to define a generic Task.

        Task have a beginning and end.

        Task is used by

        - Movement

        If we want to use a single date, then use start_date and target_start date.
        stop dates will be acquired from start dates as long as they hold None
    """

    _properties = (
        # Accounting
        {   'id'          : 'start_date',
            'description' : 'The date which the movement starts',
            'type'        : 'date',
            'range'       : True,
            'default'     : None,
            'acquisition_base_category'     : ('delivery', 'order', 'parent',),
            'acquisition_portal_type'       : Expression('python: portal.getPortalAcquisitionMovementTypeList() + portal.getPortalDeliveryTypeList() + portal.getPortalOrderTypeList() + portal.getPortalInvoiceTypeList() + portal.getPortalSupplyTypeList()'),
            'acquisition_copy_value'        : 0,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getStartDate',
            'acquisition_depends'           : None,
            'mode'        : 'w' },
        {   'id'          : 'stop_date',
            'description' : 'The date which the movement stops',
            'type'        : 'date',
            'range'       : True,
            'default'     : None,
            'acquisition_base_category'     : ('delivery', 'order', 'parent',),
            'acquisition_portal_type'       : Expression('python: portal.getPortalAcquisitionMovementTypeList() + portal.getPortalDeliveryTypeList() + portal.getPortalOrderTypeList() + portal.getPortalInvoiceTypeList() + portal.getPortalSupplyTypeList()'),
            'acquisition_copy_value'        : 0,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getStopDate',
            'acquisition_depends'           : None,
            'alt_accessor_id'               : ('getStartDate', ),
            'mode'        : 'w' },
    )

    _categories = ( 'requirement', )
