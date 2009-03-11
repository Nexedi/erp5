import re
import cgi
from Acquisition import aq_base
from AccessControl import Unauthorized
from Products.CMFCore.utils import _checkPermission
from Products.ERP5Type import Permissions

try:
  from Products import ExternalEditor
except:
  ExternalEditor = None

skip_meta_types = ('Image', 'File')

def traverse(ob, r, result, command_line_arguments, first_occurence):
  if command_line_arguments['r'] and \
                hasattr(aq_base(ob), 'objectValues'):
    for sub in [o for o in ob.objectValues() if o.meta_type not in skip_meta_types]:
      traverse(sub, r, result, command_line_arguments, first_occurence)
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
        result.append((ob.absolute_url(), path, "\n".join(context)))
        if first_occurence:
          break

def grep(self, pattern, A=0, B=0, r=1, i=0, highlight=1, first_occurence=0):
  if not _checkPermission(Permissions.ManagePortal, self):
    raise Unauthorized(self)
  command_line_arguments = {} # emulate grep command line args
  command_line_arguments['A'] = int(A)
  command_line_arguments['B'] = int(B)
  command_line_arguments['r'] = int(r)
  highlight = int(highlight)
  first_occurence = int(first_occurence)
  re_flags = 0
  if int(i) :
    re_flags = re.IGNORECASE
  result = []
  rx = re.compile(pattern, re_flags)
  traverse(self, rx, result, command_line_arguments, first_occurence)

  doctype = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
  html = '<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">'
  head = '''<head>
  <title>Grep result</title>
  <style type="text/css">
    body{
      background-color: #F9F9F9;
      font-family: Verdana,Tahoma,Georgia,Geneva,Arial,Sans,sans-serif;
      font-size: 90%;
      white-space:nowrap;
    }
    img{
      border:0;
    }
    .highlight{
      background-color: #8DFF6F;
    }
  </style>
</head>'''
  html_element_list = [doctype, html, head, '<body>' '<p>']
  result_list = []
  for url, path, line in result:
    path = cgi.escape(path)
    line = cgi.escape(line)
    if highlight:
      line = rx.sub('<span class="highlight">\g<0></span>', line)
    if ExternalEditor is None:
      result_list.append(
          '<a href="%s/manage_workspace">%s</a>: %s<br/>' %
          (url, path, line.replace('\n', '<br/>')))
    else:
      # if we have ExternalEditor installed, add the "external edit" link
      path_element_list = url.split('/')
      external_editor_link = '%s/externalEdit_/%s' % (
         '/'.join(path_element_list[:-1]), path_element_list[-1])
      result_list.append(
        '<a href="%s/manage_workspace">%s</a>&nbsp;<a href="%s">'
        '<img src="misc_/ExternalEditor/edit_icon" '\
            'alt="externalEditor Icon"/></a> %s<br/>'
         % (url, path, external_editor_link, line.replace('\n', '<br/>')))

  result_list.sort()
  html_element_list.extend(result_list)
  html_element_list.extend(['</p>', '</body>', '</html>'])
  self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/html')
  return '\n'.join(html_element_list)

