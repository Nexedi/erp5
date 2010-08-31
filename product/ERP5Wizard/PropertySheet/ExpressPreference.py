##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yusei TAHARA <yusei@nexedi.com>
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

class ExpressPreference:
  """
    User Preferences for erp5 express
    
    Contains all preferences (see portal_preferences) relative to erp5 express.
  """
  
  _properties = (
    { 'id'          : 'preferred_witch_tool_server_url',
      'description' : 'The URL of a server which provides Witch Tool',
      'type'        : 'string',
      'preference'  : 1,
      #'read_permission' : 'Manage portal',
      'write_permission' : 'Manage portal',
      'mode'        : 'w' },
    { 'id'          : 'preferred_witch_tool_server_root',
      'description' : 'The root of a server which provides Witch Tool',
      'type'        : 'string',
      'preference'  : 1,
      #'read_permission' : 'Manage portal',
      'write_permission' : 'Manage portal',
      'mode'        : 'w' },
    { 'id'          : 'preferred_express_subscription_status',
      'description' : 'ERP5 Express subscription status',
      'type'        : 'string',
      'preference'  : 1,
      #'read_permission' : 'Manage portal',
      'write_permission' : 'Manage portal',
      'mode'        : 'w' },
    { 'id'          : 'preferred_express_configuration_status',
      'description' : 'ERP5 Express configuration status',
      'type'        : 'string',
      'preference'  : 1,
      #'read_permission' : 'Manage portal',
      'write_permission' : 'Manage portal',
      'mode'        : 'w' },
    { 'id'          : 'preferred_express_user_id',
      'description' : 'ERP5 Express subscription user id',
      'type'        : 'string',
      'preference'  : 1,
      #'read_permission' : 'Modify portal content',
      'write_permission' : 'Modify portal content',
      'mode'        : 'w' },
    { 'id'          : 'preferred_express_password',
      'description' : 'ERP5 Express subscription password',
      'type'        : 'string',
      'preference'  : 1,
      'read_permission' : 'Modify portal content',
      'write_permission' : 'Modify portal content',
      'mode'        : 'w' },
    { 'id'          : 'preferred_express_after_setup_script_id',
      'description' : 'ERP5 Express after setup script id',
      'type'        : 'string',
      'preference'  : 1,
      #'read_permission' : 'Modify portal content',
      'write_permission' : 'Modify portal content',
      'mode'        : 'w' },
    { 'id'          : 'preferred_express_erp5_uid',
      'description' : 'ERP5 Express unique ID',
      'type'        : 'string',
      'preference'  : 1,
      #'read_permission' : 'Modify portal content',
      'write_permission' : 'Modify portal content',
      'mode'        : 'w' },
    { 'id'          : 'preferred_express_client_uid',
      'description' : 'ERP5 Express client unique ID',
      'type'        : 'string',
      'preference'  : 1,
      #'read_permission' : 'Modify portal content',
      'write_permission' : 'Modify portal content',
      'mode'        : 'w' },        
  )
