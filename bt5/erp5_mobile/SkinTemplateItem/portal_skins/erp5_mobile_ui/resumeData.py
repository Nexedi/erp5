if (data):
  foo = str(data)
  foo = unicode(foo, "utf8")
  lenght = len(foo)
  if (lenght > 20):
    return(foo[:20]+ "...")
  else:
    return(foo)
