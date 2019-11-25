domain_list=[]
request = context.REQUEST
filter_ = {}

try:
  # first, try to get form_id from the request
  listbox = getattr(getattr(request['here'], request['form_id']), 'listbox', None)
except KeyError:
  # then, try current_form_id
  listbox = getattr(getattr(request['here'], request['current_form_id']), 'listbox', None)

if listbox is not None:
  portal_type_list = [x[0] for x in listbox.get_value('portal_types')]
  filter_['portal_type'] = portal_type_list

if depth == 0:
  parent_obj = request['here']
  parent_url = parent_obj.getRelativeUrl()
  
else:
  parent_url = parent.getProperty('parent_url')
  parent_obj = context.restrictedTraverse(parent_url)

for obj in parent_obj.contentValues(filter=filter_):
  domain = parent.generateTempDomain(id='%s_%s' % (depth, obj.getId()))
  domain.edit(title=obj.getTitle(),
              parent_url=obj.getRelativeUrl(),
              domain_generator_method_id=script.id,
              list_method='searchFolder',
              context_url=parent_url,
              uid=obj.getUid())
  domain.setCriterion(property='uid', identity=obj.getUid())
  domain.setCriterionPropertyList(['uid'])

  domain_list.append(domain)

return domain_list
