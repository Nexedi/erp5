from Products.ERP5Type.Document import newTempBase

portal_object = context.getPortalObject()
num = 0
result_listbox = []

if active_process_path is None:
  #return []
  active_process_path=context.REQUEST.get('active_process')

active_process_value = context.getPortalObject().restrictedTraverse(active_process_path)
result_list = [[x.method_id, x.result] for x in active_process_value.getResultList()]

result_list.sort()

for [method_id, result] in result_list:
  safe_id = context.Base_getSafeIdFromString('result %s' % num)
  num += 1
  int_len = 7
  if not result['success']:
      o = newTempBase(portal_object, safe_id)
      o.setUid(  'new_%s' % str(num).zfill(int_len)) # XXX There is a security issue here
      o.edit(uid='new_%s' % str(num).zfill(int_len)) # XXX There is a security issue here
      o.edit(**result['object'])
      result_listbox.append(o)

return result_listbox
