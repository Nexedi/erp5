portal_catalog = context.getPortalObject().portal_catalog
if kw.get('path'):
  assert 'uid' not in kw
  kw['uid'] = [
    b.uid for b in portal_catalog(portal_type=kw['portal_type'], path=kw.pop('path'))
  ] or [-1]

kw['parent_specialise_reference'] = 'default_bank_reconciliation_rule'
kw['delivery_uid'] = None
kw['left_join_list'] = ['delivery_uid']
kw['select_dict'] = dict(delivery_uid=None)
kw['group_by'] = ('uid',)

kw['src__'] = src__

return portal_catalog(**kw)
