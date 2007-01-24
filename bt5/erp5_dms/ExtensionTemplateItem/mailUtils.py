import re

def findAddress(txt):
  """
  find email address in a string
  """
  validchars='0-9A-Za-z.\-_'
  r=re.compile('[%s]+@[%s]+' % (validchars,validchars))
  m=r.search(txt)
  return m and m.group()

def extractParams(txt):
  """
  extract parameters given in mail body
  We assume that parameters are given as lines of the format:
  name:value
  """
  r=re.compile('^([\w_]+):([\w_/]+)$')
  res=[]
  for line in txt.split():
    found=r.findall(line.strip())
    if len(found)==1:
      res.append(found[0])
  return dict(res)


# vim: shiftwidth=2
