## Script (Python) "listDict"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
ret = '<html><body><table width=100%>\n'

dict = context.showDict().items()
dict.sort()
i = 0
for k,v in dict:
  if (i % 2) == 0:
    c = '#88dddd'
  else:
    c = '#dddd88'
  i += 1
  ret += '<tr bgcolor="%s"><td >%s</td><td>%s</td></tr>\n' % (c, k, repr(v))

ret += '</table></body></html>\n'

return ret

