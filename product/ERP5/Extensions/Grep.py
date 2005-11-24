import re
import cgi

def traverse(ob, r, result):
  if hasattr(ob, 'objectValues'):
    for sub in ob.objectValues():
      traverse(sub, r, result)
  try:
    text = ob.manage_FTPget()
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

