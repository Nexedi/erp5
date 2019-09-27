from string import zfill
request = context.REQUEST
request.RESPONSE.setStatus(400)

from string import zfill

for k in kw.keys():
  v = kw[k]
  if k.endswith('listbox'):
    listbox = {}
    listbox_key = "%s_key" % k
    if v is not None:
      i = 1
      for line in v:
        if line.has_key(listbox_key):
          key = '%s' % line[listbox_key]
        else:
          key = str(zfill(i,3))
        listbox[key] = line
        i+=1
      request.set(k,listbox)
  else:
    request.set('your_%s' % k, v)
    request.set('%s' % k, v)
    # for backward compatibility, we keep my_ for dialog
    # using old naming conventions
    request.set('my_%s' % k, v)
