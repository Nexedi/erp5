##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
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

class Periodicity:
    """
    A Recurence allows to define an event wich happens periodically.
    """

    _properties = (
        {   'id'          : 'peridocity_start_date',
            'description' : 'When this periodic event will start',
            'type'        : 'date',
            'mode'        : 'w' },                
        {   'id'          : 'periodicity_stop_date',
            'description' : 'When this periodic envent will stop',
            'type'        : 'date',
            'mode'        : 'w' },                        
        {   'id'          : 'reminder_minute',
            'description' : 'The time in minute before the begin where we should remind the user',
            'type'        : 'int',
            'mode'        : 'w' },                        
        {   'id'          : 'reminder_hour',
            'description' : 'The time in hours before the begin where we should remind the user',
            'type'        : 'int',
            'mode'        : 'w' },                        
        {   'id'          : 'reminder_day',
            'description' : 'The time in days before the begin where we should remind the user',
            'type'        : 'int',
            'mode'        : 'w' },                        
        {   'id'          : 'periodicity_day',
            'description' : 'Recur every periodicity days (ex every 2 days)',
            'type'        : 'int',
            'mode'        : 'w' },                        
        {   'id'          : 'periodicity_week',
            'description' : 'Recur every periodicity weeks (ex every 3 weeks)',
            'type'        : 'int',
            'mode'        : 'w' },                        
        {   'id'          : 'periodicity_week_day',
            'description' : 'Recur on some days of the week (ex monday and sunday)',
            'type'        : 'lines',
            'mode'        : 'w' },                        
        {   'id'          : 'periodicity_month',
            'description' : 'Recur every periodicity month (ex every 4 months)',
            'type'        : 'int',
            'mode'        : 'w' },                        
        {   'id'          : 'periodicity_month_day',
            'description' : 'Recur on some days of the month (ex 5th)',
            'type'        : 'int',
            'mode'        : 'w' },                        
        {   'id'          : 'periodicity_years',
            'description' : 'Recur every periodicity years (ex every 1 year)',
            'type'        : 'int',
            'mode'        : 'w' },                        
    )

