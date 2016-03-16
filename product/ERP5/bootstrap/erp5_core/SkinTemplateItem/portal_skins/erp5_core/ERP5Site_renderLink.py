if len(http_parameters) == 0:
  return link
if '?' in link:
  sep='&'
else:
  sep='?'
return '%s%s%s' % (link, sep, http_parameters)
