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
    A Periodicity allows to define an event wich happens periodically.

    Here an explanation of wich kind of period we can define:
    - Every 2 days:
      - set periodicity_day to 2

    - Every monday and wednesday
      - set periodicity_week to 1
      - set periodicity_week_day to ['monday','wednesday']

    - Every 10th of every 3 months
      - set periodicity_month to 3
      - set periodicity_month_day to 10

    - Every 2nd Thursday of every 4 months
      - set periodicity_month to 4
      - set periodicity_month_week to 2
      - set periodicity_month_week_day to 'thursday'
    """

    _properties = (
        {   'id'          : 'periodicity_start_date',
            'description' : 'When this periodic event will start',
            'type'        : 'date',
            'mode'        : 'w' },                
        {   'id'          : 'periodicity_stop_date',
            'description' : 'When this periodic event will stop',
            'type'        : 'date',
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
        {   'id'          : 'periodicity_month_week',
            'description' : 'On wich (1st, 2nd, 3rd, 4th) month_week_day it will recur',
            'type'        : 'int',
            'mode'        : 'w' },                        
        {   'id'          : 'periodicity_month_week_day',
            'description' : 'The day of the week where it should recur (should be associated with periodicity_month_week),' \
                             'for example "wednesday"',
            'type'        : 'string',
            'mode'        : 'w' },                        
        {   'id'          : 'periodicity_year',
            'description' : 'Recur every periodicity years (ex every 1 year)',
            'type'        : 'int',
            'mode'        : 'w' },                        
    )

