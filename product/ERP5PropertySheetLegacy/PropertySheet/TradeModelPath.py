# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Lukasz Nowak <luke@nexedi.com>
#                    Yusuke Muraoka <yusuke@nexedi.com>
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

class TradeModelPath:
    """
      Trade Model Path properties
    """
    _properties = (
        {   'id'          : 'source_method_id',
            'description' : 'ID of method to get source list of categories',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'destination_method_id',
            'description' : 'ID of method to get destination list of categories',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'reference_date_method_id',
            'description' : 'ID of method to get the reference date at the trade_phase defined by trade_date',
            'type'        : 'string',
            'default'     : 'getStopDate',
            'mode'        : 'w' },
    )

    _categories = ('end_of', # XXX-JPS What is end_of ????
                   'trade_phase' , 'incoterm') # XXX-JPS why incoterm ?
