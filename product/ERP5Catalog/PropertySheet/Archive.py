##############################################################################
# -*- coding: utf8 -*-
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurélien Calonne <aurel@nexedi.com>
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

class Archive:
    """
    """
    _properties = (
      { 'id'      : 'catalog_id',
        'description' : 'The id of the catalog used by the archive',
        'type'    : 'string',
        'mode'    : 'w' },
      { 'id'      : 'connection_id',
        'description' : 'The id of the connection used by the archive',
        'type'    : 'string',
        'mode'    : 'w' },
      { 'id'      : 'deferred_connection_id',
        'description' : 'The id of the deferred connection used by the archive',
        'type'    : 'string',
        'mode'    : 'w' },
      { 'id'      : 'priority',
        'description' : 'Priority of activity use to index object into the archive',
        'type'    : 'int',
        'mode'    : 'w' ,
        'default' : 5},
      { 'id'      : 'stop_date',
        'description' : 'The stop date at which we archive document',
        'type'    : 'date',
        'range'   : True,
        'default' : None,
        'mode'    : 'w' },
      { 'id'      : 'inventory_method_id',
        'description' : 'The method that will be used to create inventory when creating archive',
        'type'    : 'string',
        'mode'    : 'w' },
      )

