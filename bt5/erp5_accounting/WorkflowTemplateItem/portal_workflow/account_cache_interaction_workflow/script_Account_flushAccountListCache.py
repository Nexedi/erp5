"""Increment cache cookie to flush the cache for list of accounts.

Because cache uses catalog, we can only flush cache once the account is reindex.
"""
tag = script.getId()
sci['object'].reindexObject(activate_kw={'tag': tag})

sci['object'].getPortalObject().account_module.activate(
  after_tag=tag
).newCacheCookie("account_list")
