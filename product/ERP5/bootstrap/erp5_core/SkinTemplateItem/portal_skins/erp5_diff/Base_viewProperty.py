def escape(data):
  """
    Escape &, <, and > in a string of data.
    This is a copy of the xml.sax.saxutils.escape function.
  """
  # must do ampersand first
  data = data.replace("&", "&amp;")
  data = data.replace(">", "&gt;")
  data = data.replace("<", "&lt;")
  return data

from pprint import pformat

ret = '<html><body><table width=100%>\n'

# Get the dict only for the properties having non-empty property values
dict = [(k, v) for k, v in context.propertyItems() if v]
dict.sort()
i = 0
for k,v in dict:
  if (i % 2) == 0:
    c = '#88dddd'
  else:
    c = '#dddd88'
  i += 1
  ret += '<tr bgcolor="%s"><td ><a href="Base_viewPropertyHistoryList?property_name=%s">%s</td><td><pre>%s</pre></td></tr>\n' % (escape(c), escape(k), escape(k), escape(pformat(v)))

ret += '</table></body></html>\n'

return ret
