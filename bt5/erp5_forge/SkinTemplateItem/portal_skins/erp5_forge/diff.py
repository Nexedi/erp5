kw.update(context.REQUEST.form)

def getObjectFromArg(argument):
  """
    Return an object identified by argument.
    If argument is a string, assume it's the path to the object.
    Otherwise, assume it's the object itself.
  """
  if isinstance(argument, str):
    return context.restrictedTraverse(argument)
  return argument

kw_value_list = kw.values()
kw_len = len(kw_value_list)
if kw_len == 1:
  object_a = context
  object_b = getObjectFromArg(kw_value_list[0])
elif kw_len == 2:
  kw_value_list = kw.values()
  object_a = getObjectFromArg(kw_value_list[0])
  object_b = getObjectFromArg(kw_value_list[1])
else:
  raise ValueError('%s is not a valid number of arguments for diff.' % (kw_len, ))

diff_dict, missing_in_a_dict, missing_in_b_dict = diff_recursive(object_a, object_b)

context.REQUEST.RESPONSE.setHeader('Content-Type', 'text/html; charset=utf-8')
print '<html>'
print '<head><title>Diff between %s and %s</title></head>' % (object_a.id, object_b.id)
print '<body><pre>'
print '--- <a href="%s">%s</a>' % (object_a.absolute_url(), object_a.id)
print '+++ <a href="%s">%s</a>' % (object_b.absolute_url(), object_b.id)
print '</pre><h1>Modified files</h1><ul>'
for id, diff in diff_dict.items():
  print '<li><b>%s</b><pre>' % (id, )
  for line in diff:
    print line
  print '</pre></li>'
print '</ul>'
if len(missing_in_a_dict):
  print '<h1>Objects missing in first object</h1><ul>'
  for id in missing_in_a_dict.keys():
    print '<li>%s</li>' % (id, )
  print '</ul>'
if len(missing_in_b_dict):
  print '<h1>Objects missing in second object</h1><ul>'
  for id in missing_in_b_dict.keys():
    print '<li>%s</li>' % (id, )
  print '</ul>'
print '</body></html>'
return printed
