try:
  return context.getTypeInfo().getContentTranslationDomainPropertyNameList() and True
except Exception:
  # First time after cache is cleared, something is wrong and does not work.
  return False
