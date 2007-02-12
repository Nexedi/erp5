##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type import Permissions
from Acquisition import aq_base
from time import time
from UserDict import UserDict

_marker=[]

def wrapper():
  """ Simple cache call wrapper."""
  s = Session()
  return s

class Session(UserDict):
  """ Session object acts as a plain python dictionary but can wrap/unwarp ZODB
      RAM object (newTempOrder, newTempDocument..) in order to safely store it inside. 
      Please be AWARE that there's no security checks applied! """
   
  ## we have our own security policy and do not want Zope's
  _guarded_writes = 1 
  __allow_access_to_unprotected_subobjects__ = 1
  
  ## a handle to current aquisition context
  _aq_context = None
  
  def _updatecontext(self, aq_context):
    """ Update current aquisition context. """
    self._aq_context = aq_context
  
  def __getattr__(self, key):
    return self.__getitem__(key)
  
  def __getitem__(self, key):
    value = self.data.get(key, None)
    if key is not None and hasattr(value, '__of__'):
      value = value.__of__(self._aq_context)
    return value
    
  def __setitem__(self, key, item):
    self.data[key] = aq_base(item)
    
  def __str__(self):
    return self.__repr__()
    
  def edit(self, **kw):
    """ Edit session object. """
    for key, item in kw.items():
      self.__setitem__(key, item)
 
class SessionTool(BaseTool):
  """ Using this tool you can get a RAM based session object by providing 
      your own generated session_id. 
            
      This session object can be used anywhere in Zope/ERP5 environment. 
      Because it uses lazy Cache as a storage backend you do not need to initialize it
      (Cache will take care for that first time it's called).
      
      Example:
      
      session_id = '1234567'
      session = context.portal_sessions[session_id]
      session['shopping_cart'] = newTempOrder(context, '987654321')
      (you can also use 'session.edit(shopping_cart= newTempOrder(context, '987654321'))' )
      
      (later in another script you can acquire shopping_cart):
      
      session_id = '1234567'
      session = context.portal_sessions[session_id]
      shopping_cart = session['shopping_cart']
      
      Please note that:
       - developer is responsible for handling an uniform sessiond_id (using cookies for example). 
       - it's not recommended to store in portal_sessions ZODB persistent objects because in order 
       to store them in Cache(RAM) portal_sessions tool will remove aquisition wrapper. At "get" 
       request they'll be returend wrapped. 
       - it's recommended that developer store temporary RAM based objects like 'TempOrder'
      """
    
  id = 'portal_sessions'
  meta_type = 'ERP5 Session Tool'    
  portal_type = 'Session Tool'
  allowed_types = ()
  security = ClassSecurityInfo()
  
  ## the ERP5 cache factory used as a storage
  _cache_factory = 'erp5_session_cache'
     
  def __getitem__(self, key):
    session = self._getSessionObject(key)
    session._updatecontext(self)
    return session
    
  def __setitem__(self, key, item):
    session = self._getSessionObject(session_id)
    session._updatecontext(self)

  def newContent(self, id, **kw):
    """ Create new session object. """
    session =  self._getSessionObject(id)
    session._updatecontext(self)
    session.edit(**kw)
    return session
         
  security.declareProtected(Permissions.ModifyPortalContent, 'manage_delObjects')
  def manage_delObjects(self, ids=[], REQUEST=None):
    """ Delete session object. """
    if not isinstance(ids, list) or isinstance(ids, list):
      ids = [ids]
    for session_id in ids:
      cache_method = self._getCacheMethod(session_id)
      cache_method.delete(session_id)
 
  def _getCacheMethod(self, session_id):
    """ Get caching method used to interact with Cache system. """
    cache_method = CachingMethod(callable_object = wrapper, \
                                 id = session_id, \
                                 cache_factory = self._cache_factory)
    return cache_method
    
  def _getSessionObject(self, session_id):
    """ Return session object. """
    return self._getCacheMethod(session_id)()
