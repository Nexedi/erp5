"""When account is edited, we only need to update the cache if the account is validated
because only validated accounts are displayed in the cache.
"""
if sci['object'].getValidationState() == 'validated':
  container.script_Account_flushAccountListCache(sci)
