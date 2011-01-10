# -*- coding: utf-8 -*-
##############################################################################
#                                                                             
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.       
#                    François-Xavier Algrain <fxalgrain@tiolive.com>                  
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.Permissions import ManagePortal

from Globals import DTMLFile
from Products.ERP5ShortMessage import _dtmldir

class SMSTool(BaseTool):
  """
    This tool manages gadgets.

    It is used as a central point to manage gadgets (ERP5 or external ones)...
  """
  id = 'portal_sms'
  meta_type = 'ERP5 SMS Tool'
  portal_type = 'SMS Tool'

  # Declarative Security
  security = ClassSecurityInfo()
  security.declareProtected(ManagePortal, 'manage_overview')
  manage_overview = DTMLFile('explainSMSTool', _dtmldir )
     
  security.declareProtected(ManagePortal, 'send')
  def send(self, text,recipient, sender=None, message_type="text",
           test=False, gateway_reference='default', 
           document_relative_url=None, activate_kw=None, **kw):        
    """
    document_relative_url (optional) : allows to send back result to a document
    """
              
    gateway = self.find(gateway_reference)

    message_id_list =  gateway.send(text,recipient,
                        sender=sender, message_type="text",
                        test=False, **kw)
    if getattr(self, 'SMSTool_afterSend'):
      # We need to use activities in order to avoid any conflict
      send_activate_kw = {}
      if activate_kw is not None:
        send_activate_kw.update(**activate_kw)
      self.activate(**send_activate_kw).SMSTool_afterSend(
              message_id_list, 
              document_relative_url=document_relative_url, **kw)

  security.declareProtected(ManagePortal, 'getMessageStatus')
  def getMessageStatus(self,message_id, gateway_reference='default'):
     
     gateway = self.find(gateway_reference)     
     return gateway.getMessageStatus(message_id)
     
  security.declarePublic('isSendByTitleAllowed')
  def isSendByTitleAllowed(self, gateway_reference='default'):
    """Define the support or not to use the title of the telephone instead of 
        the number when send a message."""
    gateway = self.find(gateway_reference)
    return gateway.isTitleMode()
     

  security.declarePublic('find')
  def find(self,gateway_reference='default'):
    """Search the gateway by his reference"""
       
    result = self.searchFolder(reference=gateway_reference)
    if len(result) > 0:
      return result[0].getObject()
    else:
      raise ValueError, "Impossible to find gateway with reference %s" % gateway_reference

