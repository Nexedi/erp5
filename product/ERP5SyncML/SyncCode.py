##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from Products.ERP5Type.Accessor.TypeDefinition import list_types
from Globals import Persistent

class SyncCode(Persistent):
  """
    Class giving the Synchronization's Constants
  """

  # SyncML Alert Codes
  TWO_WAY = 200
  SLOW_SYNC = 201
  WAITING_DATA = 214

  # SyncML Status Codes
  SUCCESS = 200
  CHUNK_OK = 214
  CONFLICT = 409 # A conflict is detected
  CONFLICT_MERGE = 207 # We have merged the two versions, sending
                       # whatever is needed to change(replace)
  CONFLICT_CLIENT_WIN = 208 # The client is the "winner", we keep
                            # the version of the client

  # Difference between publication and subscription
  PUB = 1
  SUB = 0

  NULL_ANCHOR = '00000000T000000Z'

  # ERP5 Sync Codes
  SYNCHRONIZED = 1
  SENT = 2
  NOT_SENT = 3
  PARTIAL = 4
  NOT_SYNCHRONIZED = 5
  PUB_CONFLICT_MERGE = 6
  #SUB_CONFLICT_MERGE = 7
  PUB_CONFLICT_CLIENT_WIN = 8
  #SUB_CONFLICT_CLIENT_WIN = 9

  MAX_LINES = 1000

  #ENCODING='iso-8859-1'


  NOT_EDITABLE_PROPERTY = ('id','object','workflow_history','security_info','uid'
                           'xupdate:element','xupdate:attribute')
  XUPDATE_INSERT =        ('xupdate:insert-after','xupdate:insert-before')
  XUPDATE_ADD =           ('xupdate:append',)
  XUPDATE_DEL =           ('xupdate:remove',)
  XUPDATE_UPDATE =        ('xupdate:update',)
  XUPDATE_INSERT_OR_ADD = tuple(XUPDATE_INSERT) + tuple(XUPDATE_ADD)
  XUPDATE_TAG = tuple(XUPDATE_INSERT) + tuple(XUPDATE_ADD) + \
                tuple(XUPDATE_UPDATE) + tuple(XUPDATE_DEL)
  text_type_list = ('text','string')
  list_type_list = list_types
  binary_type_list = ('image','file','document')
  date_type_list = ('date',)
  dict_type_list = ('dict',)
  xml_object_tag = 'object'
  sub_object_exp = "/object\[@id='.*'\]/object\[@id='.*'\]"
