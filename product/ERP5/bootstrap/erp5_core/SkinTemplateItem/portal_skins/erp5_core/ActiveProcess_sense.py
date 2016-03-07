for result in context.getResultList():
  if result is None:
    continue # Workaround for bogus results
  # This is useful is result is returned as a Return instance
  if result.isError():
    return True
  # This is the default case
  if getattr(result, 'result', False):
    return True
return False
