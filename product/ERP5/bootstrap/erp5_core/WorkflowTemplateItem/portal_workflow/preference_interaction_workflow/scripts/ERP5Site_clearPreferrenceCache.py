"""Clear caches used by methods of this preference

# TODO: clear different caches according to the preference priority
# TODO: (XXX) currently, if one use enables / disables a cache, caches
        for all other users are reset. This is not good for a system
        in which users do a lot of preference validation. A better solution
        is needed for this. But it is not easy because the concept of
        "per user cache" has been proven to be ambiguous or useless.
        In theory, a solution could consist in using more keys to
        select caches or to delete "manually" certain cache keys.
"""
portal = sci['object'].getPortalObject()
portal.portal_caches.clearCache(cache_factory_list=('erp5_ui_short',))
