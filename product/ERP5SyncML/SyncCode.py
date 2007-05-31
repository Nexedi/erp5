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
  SLOW_SYNC = 201 # This means we get the data from the publication
  WAITING_DATA = 214

  # SyncML Status Codes
  SUCCESS = 200
  CHUNK_OK = 214
  CONFLICT = 409 # A conflict is detected
  CONFLICT_MERGE = 207 # We have merged the two versions, sending
                       # whatever is needed to change(replace)
  CONFLICT_CLIENT_WIN = 208 # The client is the "winner", we keep
                            # the version of the client
  UNAUTHORIZED = 401
  AUTH_REQUIRED = 407
  AUTH_ACCEPTED = 212

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
  PUB_CONFLICT_CLIENT_WIN = 8

  MAX_LINES = 1000

  action_tag = 'workflow_action'
  #NOT_EDITABLE_PROPERTY = ('id','object','uid','xupdate:element',action_tag,
  #                         'xupdate:attribute','local_role')
  XUPDATE_INSERT =        ('xupdate:insert-after','xupdate:insert-before')
  XUPDATE_ADD =           ('xupdate:append',)
  XUPDATE_DEL =           ('xupdate:remove',)
  XUPDATE_UPDATE =        ('xupdate:update',)
  XUPDATE_EL =        ('xupdate:element',)
  XUPDATE_INSERT_OR_ADD = tuple(XUPDATE_INSERT) + tuple(XUPDATE_ADD)
  XUPDATE_TAG = tuple(XUPDATE_INSERT) + tuple(XUPDATE_ADD) + \
                tuple(XUPDATE_UPDATE) + tuple(XUPDATE_DEL)
  text_type_list = ('text','string')
  list_type_list = list_types
  force_conflict_list = ('layout_and_schema','ModificationDate')
  binary_type_list = ('image','file','document','pickle')
  date_type_list = ('date',)
  dict_type_list = ('dict',)
  int_type_list = ('int',)
  pickle_type_list = ('object',)
  xml_object_tag = 'object'
  #history_tag = 'workflow_history'
  history_tag = 'workflow_action'
  local_role_tag = 'local_role'
  local_permission_tag = 'local_permission'
  local_permission_list = (local_permission_tag,'/'+local_permission_tag)
  local_group_tag = 'local_group'
  local_role_list = (local_role_tag,'/'+local_role_tag,
                     local_group_tag,'/'+local_group_tag)
  ADDABLE_PROPERTY = local_role_list + (history_tag,) + local_permission_list
  NOT_EDITABLE_PROPERTY = ('id','object','uid','xupdate:attribute') \
                          + XUPDATE_EL + ADDABLE_PROPERTY
  sub_object_exp = "/object\[@id='.*'\]/"
  object_exp = "/object\[@id='.*'\]"
  sub_sub_object_exp = "/object\[@id='.*'\]/object\[@id='.*'\]/"
  history_exp = "/%s\[@id='.*'\]" % history_tag
  local_role_exp = "/%s\[@id='.*'\]" % local_role_tag
  local_group_exp = "/%s\[@id='.*'\]" % local_group_tag
  bad_local_role_exp = "/%s\[@id='.*'\]/" % local_role_tag
  bad_local_group_exp = "/%s\[@id='.*'\]/" % local_group_tag
  bad_history_exp = "/%s\[@id='.*'\]/" % history_tag
  local_role_and_group_list = (local_group_exp,local_role_exp)
  bad_local_role_and_group_list = (bad_local_group_exp,bad_local_role_exp)


  #media types :

  MEDIA_TYPE = {}
  MEDIA_TYPE['TEXT_XML'] = 'text/xml'
  MEDIA_TYPE['TEXT_VCARD'] = 'text/vcard'
