"""Cache
"""
from time import time
from Acquisition import aq_base

_marker = object()

class Cache:

    def __init__(self, obj, context=None, _id='_v_transform_cache'):
        self.obj = obj
        if context is None:
            self.context = obj
        else:
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
        if hasattr(aq_base(self.context), 'absolute_url'):
            return key, self.context.absolute_url()
        return key

    def setCache(self, key, value):
        """cache a value indexed by key"""
        if not value.isCacheable():
            return
        obj = self.obj
        key = self._genCacheKey(key)
        if getattr(aq_base(obj), self._id, None) is None:
            setattr(obj, self._id, {})
        getattr(obj, self._id)[key] = (time(), value)
        return key

    def getCache(self, key):
        """try to get a cached value for key

        return None if not present
        else return a tuple (time spent in cache, value)
        """
        obj = self.obj
        key = self._genCacheKey(key)
        dict = getattr(obj, self._id, None)
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
        obj = self.obj
        id = self._id
        if getattr(obj, id, _marker) is _marker:
            return
        if key is None:
            delattr(obj, id)
        else:
            cache = getattr(obj, id)
            key = self._genCacheKey(key)
            if cache.has_key(key):
                del cache[key]
