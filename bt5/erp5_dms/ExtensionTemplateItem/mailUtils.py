import re

def findAddress(txt):
  validchars='0-9A-Za-z.\-_'
  r=re.compile('[%s]+@[%s]+' % (validchars,validchars))
  m=r.search(txt)
  return m and m.group()


# vim: shiftwidth=2
