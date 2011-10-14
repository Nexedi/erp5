# -*- coding: utf-8 -*-
##############################################################################
#                                                                             
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.       
#                    Francois-Xavier Algrain <fxalgrain@tiolive.com>                  
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

class SMSGateway:
    """
        Agent properties for Agent objects
    """

    _properties = (
        { 'id'         : 'gateway_user'
        , 'description': 'User name to connect '
        , 'type'       : 'string'
        , 'mode'       : 'w'
        },
        { 'id'         : 'gateway_password'
        , 'description': 'Password to connect'
        , 'type'       : 'string'
        , 'mode'       : 'w'
        },
        { 'id'         : 'gateway_account'
        , 'description': 'Account to use.'
        , 'type'       : 'string'
        , 'mode'       : 'w'
        },
        { 'id'         : 'gateway_account_id'
        , 'description': 'Id of the accound. Can be used for push notification'
        , 'type'       : 'string'
        , 'mode'       : 'w'
        },
        { 'id'         : 'default_sender'
        , 'description': 'Default sender when send message.'
        , 'type'       : 'string'
        , 'mode'       : 'w'
        },
        { 'id'         : 'simulation_mode'
        , 'description': 'Force the simulation mode.'
        , 'type'       : 'boolean'
        , 'mode'       : 'w'
        },
        { 'id'         : 'title_mode'
        , 'description': 'Allow or not to send by title'
        , 'type'       : 'boolean'
        , 'mode'       : 'w'
        },
        )