NBSP_UTF8 = u'\xA0'.encode('utf-8')
def getCategoryLevel(category=None):
    if getattr(category.getParentValue(), "getDestinationReference", None) is None:
      return 0
    return 1 + getCategoryLevel(category.getParentValue())
level = getCategoryLevel(context.getParentValue())
return "%s%s" % (NBSP_UTF8 * 8 * level, context.getSourceReference())
