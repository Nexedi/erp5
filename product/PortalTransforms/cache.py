"""Cache
"""
from time import time
from Acquisition import aq_base

class Cache:

    def __init__(self, context, _id='_v_transform_cache'):
        self.context = context
        self._id =_id

    def _genCacheKey(self, identifier, *args):
        key = identifier
        for arg in args:
            key = '%s_%s' % (key, arg)
        key = key.replace('/', '_')
        key = key.replace('+', '_')
        key = key.replace('-', '_')
        key = key.replace(' ', '_')
        return key

    def setCache(self, key, value):
        """cache a value indexed by key"""
        if not value.isCacheable():
            return
        context = self.context
        key = self._genCacheKey(key)
        if getattr(aq_base(context), self._id, None) is None:
            setattr(context, self._id, {})
        getattr(context, self._id)[key] = (time(), value)
        return key

    def getCache(self, key):
        """try to get a cached value for key

        return None if not present
        else return a tuple (time spent in cache, value)
        """
        context = self.context
        key = self._genCacheKey(key)
        dict = getattr(context, self._id, None)
        if dict is None :
            return None
        try:
            orig_time, value = dict.get(key, None)
            return time() - orig_time, value
        except TypeError:
            return None
        
    def purgeCache(self, key=None):
        """Remove cache
        """
        context = self.context
        id = self._id
        if not shasattr(context, id):
            return
        if key is None:
            delattr(context, id)
        else:
            cache = getattr(context, id)
            key = self._genCacheKey(key)
            if cache.has_key(key):
                del cache[key]
