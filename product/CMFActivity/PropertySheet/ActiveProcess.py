##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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


class ActiveProcess:
    """
        Properties which allow to define a generic Active Process.

        Active Process objects usually have a causality.

        We can use start and stop date in order to know how much time
        we use the cpu.
    """

    _properties = (
        {   'id'          : 'start_date',
            'description' : 'The date which the process starts',
            'type'        : 'date',
            'default'     : None,
            'mode'        : 'w' },
        {   'id'          : 'stop_date',
            'description' : 'The date which the process stops',
            'type'        : 'date',
            'default'     : None,
            'mode'        : 'w' },
        {   'id'          : 'sense_value',
            'description' : 'true if there is a problem',
            'type'        : 'boolean',
            'default'     : 0,
            'mode'        : 'w' },
         )


    _categories = ( 'causality', )

