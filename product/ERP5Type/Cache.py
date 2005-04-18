##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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

from Globals import PersistentMapping
from AccessControl.SecurityInfo import allow_class
from time import time

from zLOG import LOG

# XXX need to expire old objects in a way.
cache_check_time = time()
CACHE_CHECK_TIMEOUT = 60

# Special Exception for this code.
class CachedMethodError(Exception): pass

# This is just a storage.
class CachedObject:
  pass

class CachingMethod:
  """
    CachingMethod wraps a callable object to cache the result.

    Example:

      def toto(arg=None):
        # heavy operations...

      method = CachingMethod(toto, id='toto')
      return method(arg='titi')

    Some caveats:

      - You must make sure that the method call takes all parameters which can make
        the result vary. Otherwise, you will get inconsistent results.

      - You should make sure that the method call does not take any parameter which
        never make the result vary. Otherwise, the cache ratio will be worse.

      - Choose the id carefully. If you use the same id in different methods, this may
        lead to inconsistent results.

      - This system can be sometimes quite slow if there are many entries, because
        all entries are checked to expire old ones. This should not be significant,
        since this is done once per 100 calls.
  """
  # Use this global variable to store cached objects.
  cached_object_dict = {}
  
  def __init__(self, callable_object, id = None, cache_duration = 180):
    """
      callable_object must be callable.
      id is used to identify what call should be treated as the same call.
      cache_duration is specified in seconds.
    """
    if not callable(callable_object):
      raise CachedMethodError, "callable_object %s is not callable" % str(callable_object)
    if not id:
      raise CachedMethodError, "id must be specified"
    self.method = callable_object
    self.id = id
    self.duration = cache_duration

  def __call__(self, *args, **kwd):
    """
      Call the method only if the result is not cached.

      This code looks not aware of multi-threading, but there should no bad effect in reality,
      since the worst case is that multiple threads compute the same call at a time.
    """
    global cache_check_time

    now = time()

    if cache_check_time + CACHE_CHECK_TIMEOUT < now:
      # If the time reachs the timeout, expire all old entries.
      # XXX this can be quite slow, if many results are cached.
      # LOG('CachingMethod', 0, 'checking all entries to expire')
      cache_check_time = now
      try:
        for index in CachingMethod.cached_object_dict.keys():
          obj = CachingMethod.cached_object_dict[index]
          if obj.time + obj.duration < now:
            # LOG('CachingMethod', 0, 'expire %s' % index)
            del CachingMethod.cached_object_dict[index]
      except:
        # This is necessary for multi-threading, because two threads can
        # delete the same entry at a time.
        pass

    key_list = kwd.keys()
    key_list.sort()
    index = [self.id]
    for arg in args:
      index.append((None, arg))
    for key in key_list:
      index.append((key, str(kwd[key])))
    index = str(index)

    obj = CachingMethod.cached_object_dict.get(index)
    if obj is None or obj.time + obj.duration < now:
      #LOG('CachingMethod', 0, 'cache miss: id = %s, duration = %s, method = %s, args = %s, kwd = %s' % (str(self.id), str(self.duration), str(self.method), str(args), str(kwd)))
      obj = CachedObject()
      obj.time = now
      obj.duration = self.duration
      obj.result = self.method(*args, **kwd)

      CachingMethod.cached_object_dict[index] = obj
    else:
      #LOG('CachingMethod', 0, 'cache hit: id = %s, duration = %s, method = %s, args = %s, kwd = %s' % (str(self.id), str(self.duration), str(self.method), str(args), str(kwd)))
      pass

    return obj.result

allow_class(CachingMethod)

def clearCache():
  CachingMethod.cached_object_dict.clear()
