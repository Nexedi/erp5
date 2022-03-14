from builtins import str
if (data):
  foo = str(data)
  foo = str(foo, "utf8")
  lenght = len(foo)
  if (lenght > 20):
    return(foo[:20]+ "...")
  else:
    return(foo)
