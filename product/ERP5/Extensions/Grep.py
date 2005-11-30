import re
import cgi
from Acquisition import aq_base

def traverse(ob, r, result):
  if hasattr(aq_base(ob), 'objectValues'):
    for sub in ob.objectValues():
      traverse(sub, r, result)
  try:
    if hasattr(aq_base(ob), 'manage_FTPget'):
      text = ob.manage_FTPget()
    else:
      text = None
  except:
    text = None
  if text:
    for l in text.split('\n'):
      if r.search(l) is not None:
        path = '/'.join(ob.getPhysicalPath())
        result.append((path, l))
        break

def grep(self, pattern):
  result = []
  traverse(self, re.compile(pattern), result)
  html_element_list = ['<html>', '<body>']
  for path, line in result:
    path = cgi.escape(path)
    line = cgi.escape(line)
    html_element_list.append('<a href="%s/manage_workspace">%s</a>: %s<br/>' % (
path, path, line))
  html_element_list.extend(['</body>', '</html>'])
  self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/html')
  return '\n'.join(html_element_list)

