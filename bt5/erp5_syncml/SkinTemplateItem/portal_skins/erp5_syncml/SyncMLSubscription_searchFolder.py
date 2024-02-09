# This is the default "List Method ID" to use to list object from a module in erp5
# this method is optimized to return group of document based on what the syncml engine
# required
# XXX Some parameter are not managed (context_document, gid, etc)


if len(kw):
  context.log("kw %s" %(kw,))

catalog_kw = {'limit' : limit}
if min_id and id_list:
  raise NotImplementedError

if min_id:
  catalog_kw['id'] = {'query': min_id, 'range': 'nlt'}
elif id_list:
  catalog_kw['id'] = {'query': id_list, 'operator': 'in'}


return context.searchFolder(sort_on=(('id','ascending'),), **catalog_kw)
