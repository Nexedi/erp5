try:
  return context.getTypeInfo().getContentTranslationDomainPropertyNameList() and True
except:
  # First time after cache is cleared, something is wrong and does not work.
  return False
