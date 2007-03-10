import re
import cgi
from Acquisition import aq_base

skip_meta_types = ('Image', 'File')

def traverse(ob, r, result, command_line_arguments):
  if command_line_arguments['r'] and \
                hasattr(aq_base(ob), 'objectValues'):
    for sub in [o for o in ob.objectValues() if o.meta_type not in skip_meta_types]:
      traverse(sub, r, result, command_line_arguments)
  try:
    if hasattr(aq_base(ob), 'manage_FTPget'):
      text = ob.manage_FTPget()
    else:
      text = None
  except:
    text = None
  if text:
    text_lines = text.split('\n')
    for i, l in enumerate(text_lines):
      if r.search(l) is not None:
        context = text_lines[i-command_line_arguments['B'] :
                             i+1+command_line_arguments['A']]
        path = '/'.join(ob.getPhysicalPath())
        result.append((path, "\n".join(context)))
        break

def grep(self, pattern, A=0, B=0, r=1, i=0):
  command_line_arguments = {} # emulate grep command line args
  command_line_arguments['A'] = int(A)
  command_line_arguments['B'] = int(B)
  command_line_arguments['r'] = int(r)
  re_flags = 0
  if int(i) :
    re_flags = re.IGNORECASE
  result = []
  traverse(self, re.compile(pattern, re_flags), result, command_line_arguments)
  html_element_list = ['<html>', '<body>']
  for path, line in result:
    path = cgi.escape(path)
    line = cgi.escape(line)
    html_element_list.append('<a href="%s/manage_workspace">%s</a>: %s<br/>' % (
path, path, line.replace('\n', '<br/>')))
  html_element_list.extend(['</body>', '</html>'])
  self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/html')
  return '\n'.join(html_element_list)

