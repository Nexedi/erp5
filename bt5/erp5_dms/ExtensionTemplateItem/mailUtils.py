import re

def findAddress(txt):
  validchars='A-Za-z.\-_'
  r=re.compile('[%s]+@[%s]+' % (validchars,validchars))
  m=r.search(txt)
  return m and m.group()


# vim: shiftwidth=2
