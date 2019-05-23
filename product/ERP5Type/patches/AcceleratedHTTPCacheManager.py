import time
from Products.StandardCacheManagers.AcceleratedHTTPCacheManager import \
    AcceleratedHTTPCache, AcceleratedHTTPCacheManager
from App.Common import rfc1123_date
from App.special_dtml import DTMLFile
from Products.ERP5Type import _dtmldir


def ZCache_set(self, ob, data, view_name, keywords, mtime_func):
    # Note the blatant ignorance of view_name and keywords.
    # Standard HTTP accelerators are not able to make use of this
    # data.  mtime_func is also ignored because using "now" for
    # Last-Modified is as good as using any time in the past.
    REQUEST = ob.REQUEST
    RESPONSE = REQUEST.RESPONSE
    anon = 1
    u = REQUEST.get('AUTHENTICATED_USER', None)
    if u is not None:
        if u.getUserName() != 'Anonymous User':
            anon = 0
    phys_path = ob.getPhysicalPath()
    if phys_path in self.hit_counts:
        hits = self.hit_counts[phys_path]
    else:
        self.hit_counts[phys_path] = hits = [0, 0]
    if anon:
        hits[0] = hits[0] + 1
    else:
        hits[1] = hits[1] + 1

    if not anon and self.anonymous_only:
        return
    # Set HTTP Expires and Cache-Control headers
    seconds=self.interval
    cache_control_parameter = ['max-age=%d' %(seconds,)]
    expires=rfc1123_date(time.time() + seconds)
    if getattr(self, 'stale_if_error_interval', 0):
        cache_control_parameter.append("stale-if-error=%d" \
                                       %(self.stale_if_error_interval))
    if getattr(self, 'stale_while_revalidate_interval', 0):
        cache_control_parameter.append("stale-while-revalidate=%d" \
                                       %(self.stale_while_revalidate_interval))
    if getattr(self, 'public', 0):
        cache_control_parameter.append('public')
    if getattr(self, 'must_revalidate', 0):
        cache_control_parameter.append('must-revalidate')
    RESPONSE.setHeader('Last-Modified', rfc1123_date(time.time()))
    RESPONSE.setHeader('Cache-Control', ", ".join(cache_control_parameter))
    RESPONSE.setHeader('Expires', expires)



AcceleratedHTTPCache.ZCache_set = ZCache_set


def __init__(self, ob_id):
    self.id = ob_id
    self.title = ''
    self._settings = {'anonymous_only': 1,
                      'interval': 3600,
                      'stale_if_error_interval' : 300,
                      'stale_while_revalidate' : 10,
                      'public': 1,
                      'must_revalidate': 0,
                      'notify_urls': ()}
    self._resetCacheId()

def manage_editProps(self, title, settings=None, REQUEST=None):
    ' '
    if settings is None:
        settings = REQUEST
    self.title = str(title)
    self._settings = {
        'anonymous_only': settings.get('anonymous_only') and 1 or 0,
        'interval': int(settings['interval']),
        'stale_if_error_interval' : int(settings['stale_if_error_interval']),
        'stale_while_revalidate_interval' : int(settings['stale_while_revalidate_interval']),
        'public': settings.get('public') and 1 or 0,
        'must_revalidate': settings.get('must_revalidate') and 1 or 0,
        'notify_urls': tuple(settings['notify_urls'])}
    cache = self.ZCacheManager_getCache()
    cache.initSettings(self._settings)
    if REQUEST is not None:
        return self.manage_main(
            self, REQUEST, manage_tabs_message='Properties changed.')



def getSettings(self):
    ' '
    if 'stale_if_error_interval' not in self._settings:
        self._settings.update({'stale_if_error_interval' : 0})
    if 'stale_while_revalidate_interval' not in self._settings:
        self._settings.update({'stale_while_revalidate_interval' : 0})
    if 'public' not in self._settings:
        self._settings.update({'public' : 0})
    if 'must_revalidate' not in self._settings:
        self._settings.update({'must_revalidate' : 0})
    return self._settings.copy()  # Don't let UI modify it.


AcceleratedHTTPCacheManager.__init__ = __init__
AcceleratedHTTPCacheManager.getSettings = getSettings
AcceleratedHTTPCacheManager.manage_editProps = manage_editProps
AcceleratedHTTPCacheManager.manage_main = DTMLFile("propsAccel", _dtmldir)
