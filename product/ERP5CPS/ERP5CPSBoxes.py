#!/usr/bin/python
# Authors : Tarek Ziade tziade@nuxeo.com
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# # by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#

boxes = {

            'erp5cps_header': {'type':'Base Box',
                                'title': 'En-tête page ERP5',
                                'btype': 'header',
                                'provider': 'erp5cps',
                                'slot': 'top',
                                'order': 1,
                                  },

            }


guard_boxes = {'erp5cps_header': {'guard_permissions' : '',
                                  'guard_roles' : 'Authenticated',
                                  'guard_expr' : '',
                                 },
             }


def getBoxes():
    return boxes


def getGuardBoxes():
    return guard_boxes


