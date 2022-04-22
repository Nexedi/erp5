request = context.REQUEST

if kw.get('update', False):
  # Ensure ERP5JS correctly refresh the page
  request.RESPONSE.setStatus(400)

for k in list(kw.keys()):
  v = kw[k]
  if k.endswith('listbox'):
    listbox = {}
    listbox_key = "%s_key" % k
    if v is not None:
      i = 1
      for line in v:
        if listbox_key in line:
          key = '%s' % line[listbox_key]
        else:
          key = '%03d' % i
        listbox[key] = line
        i+=1
      request.set(k,listbox)
  else:
    request.set('your_%s' % k, v)
    request.set('%s' % k, v)
    # for backward compatibility, we keep my_ for dialog
    # using old naming conventions
    request.set('my_%s' % k, v)
