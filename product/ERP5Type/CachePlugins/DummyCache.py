##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                     Ivan Tyagov <ivan@nexedi.com>
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

"Dummy (no cache)"

from BaseCache import BaseCache

class DummyCache(BaseCache):
  """ Dummy cache plugin. """
    
  def __init__(self, params):
    BaseCache.__init__(self)
 
  def __call__(self, callable_object, cache_id, scope, cache_duration=None,
              *args, **kwd):
    ## Just calculate and return result - no caching 
    return callable_object(*args, **kwd)
        
  def getCacheStorage(self):
    pass
    
  def get(self, cache_id, scope, default=None):
    pass
       
  def set(self, cache_id, scope, value,
          cache_duration=None, calculation_time=0):
    pass

  def expireOldCacheEntries(self, forceCheck=False):
    pass
        
  def delete(self, cache_id, scope):
    pass
        
  def has_key(self, cache_id, scope):
    pass
        
  def getScopeList(self):
    pass
        
  def getScopeKeyList(self, scope):
    pass
        
  def clearCache(self):
    pass
        
  def clearCacheForScope(self, scope):
    pass
    
