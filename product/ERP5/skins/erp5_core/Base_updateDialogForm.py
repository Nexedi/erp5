##parameters=**kw

from string import zfill
request = context.REQUEST

from string import zfill

for k in kw.keys():
  v = kw[k]
  if k == 'listbox':
    listbox = {}
    if v is not None:
      i = 1
      for line in v:
        if line.has_key('listbox_key'):
          key = '%s' % line['listbox_key']
        else:
          key = str(zfill(i,3))
        listbox[key] = line
        i+=1
      request.set('listbox',listbox)
  else:
    request.set('my_%s' % k, v)

