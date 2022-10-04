from Products.ERP5Type.Document import newTempBase

portal_object = context.getPortalObject()
num = 0
result_listbox = []

# context.log(str(kw))
if active_process_path is None:
  if 'active_process' in kw and kw['active_process'] not in ('', None):
    active_process_path = kw['active_process']
#else:
#  if context.REQUEST.get('active_process', None) not in ('None', None):
#    active_process_path = context.REQUEST.get('active_process')
  else:
    return []

active_process_value = context.getPortalObject().restrictedTraverse(active_process_path)
result_list = [[x.method_id, x.result] for x in active_process_value.getResultList()]

result_list.sort()

for [method_id, result] in result_list:
  safe_id = context.Base_getSafeIdFromString('result %s' % num)
  num += 1
  int_len = 3
  o = newTempBase(portal_object, safe_id)
  o.setUid( 'new_%s' % str(num).zfill(int_len)) # XXX There is a security issue here
  o.edit(uid='new_%s' % str(num).zfill(int_len)) # XXX There is a security issue here
  o.edit( method_id   = method_id
         , result     = result['message']
         , object_url = result['object_url']
         , object     = result['object']
        )
  result_listbox.append(o)

return result_listbox
