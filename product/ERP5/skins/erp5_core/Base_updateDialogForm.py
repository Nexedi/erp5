##parameters=**kw

from string import zfill
request = context.REQUEST

for k in kw.keys():
  v = kw[k]
  listbox = {}
  if k == 'listbox_lines':
    i = 1
    for line in v:
      #key = '_%s' % zfill(i,3)
      key = '_%s' % line['listbox_key']
      listbox[key] = line
      i+=1
    request.set('listbox',listbox)
  else:
    request.set('my_%s' % k, v)

