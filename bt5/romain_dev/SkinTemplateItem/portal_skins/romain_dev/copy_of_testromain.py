portal = context.getPortalObject()

selection = portal.portal_selections.getSelectionFor('person_module_selection')

print selection.checked_uids
print selection.domain_path
print selection.domain_list
if selection.domain is not None:
  print selection.domain.asDomainDict()

return printed


for _, obj in portal.portal_skins.ZopeFind(portal.portal_skins.erp5_core, obj_metatypes=('ERP5 Form',), search_sub=1):
  if (obj.pt == 'form_view') and (obj.action == '') and ('FieldLibrary' not in obj.id):
    print obj.id

return printed




return

portal_object = portal = context.getPortalObject()
module = portal.person_module

i = counter
while i <= min(counter + 100, 80000):
  # module.newContent(portal_type='Person', title='test %i' % i)
  i += 1

if i != counter:
  module.activate(activity='SQLQueue', priority=5).testromain(i)

return 'couscous'

raise NotImplementedError('nutnut')
return '%s\n' % context.absolute_url()

from base64 import urlsafe_b64encode, urlsafe_b64decode
return 'data:text/css;base64,%s' % urlsafe_b64encode('couscous');

kw = {
  # 'select_dict': {'count': 'select 1;drop table catalog;', 'portal_type': None},
  'select_dict': {'count': 'count(*)', 'portal_type': None},
  # 'select_list': ['count(*)', 'portal_type'],
  # 'select_list': ['portal_type'],
  'limit': None,
  'group_by': ["portal_type"],
  # 'sort_on': [('portal_type', 'ASC')]
}

print context.portal_catalog(src__=1, **kw)
"""
for x in context.portal_catalog(**kw):
  print x.portal_type, x['count']
"""
print '---'
return printed

cp = context.manage_copyObjects(uids=uids)
context.manage_pasteObjects(cb_copy_data=cp)
return "couscous"

"""
result_list = context.portal_catalog.countResults(select_dict={'date': 'DATE_FORMAT(creation_date, "%s")' % sql_format, 'portal_type': None},
                                                  portal_type=portal_type_list,limit=None,
                                                  owner=reference,
                                                  group_by=['DATE_FORMAT(creation_date, "%s")' % sql_format, 'portal_type'],
                                                  **count_kw)
"""
