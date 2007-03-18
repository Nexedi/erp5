##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#          Jean-Paul Smets <jp@nexedi.com>
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

class Snapshot:
  """
     This property sheet defines the way to store data (file, images, etc.)
     in the form of an object of any type
  """

  _properties = (
    { 'id'          : 'snapshot_data',
      'description' : 'An object (string, stream, etc.) which contains raw data'
                      'of a snapshot. Snapshot is used to keep a visual representation'
                      'of a document such as an invoice.',
      'type'        : 'object',
      'write_permission' : 'Manage properties',
      'default'     : '',
      'mode'        : 'w' },
    { 'id'          : 'snapshot_content_type',
      'description' : 'A string which represents the mime type of the snapshot data',
      'type'        : 'string',
      'default'     : 'application/pdf',
      'mode'        : 'w' },
   )
