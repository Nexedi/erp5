"""
  This script creates assignments based on the fast input information.
  It should take into account any assignment which were already created
  so that they are not duplicated.
"""
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery
from Products.ZSQLCatalog.SQLCatalog import Query
portal = context.getPortalObject()
person_module = context.getPortalObject().person_module
items = []
for line in listbox:
  if line.has_key('listbox_key') and line['last_name'] not in ('', None):
    line_id = int(line['listbox_key'])
    item = {}
    item['id'] = line_id
   # item['title']= line['title']
    item['first_name'] = line['first_name']
    item['last_name'] = line['last_name']
    item['start_date'] = line['start_date']
    item['default_birthplace_address_city']= line['default_birthplace_address_city']
    item['function'] = line['function']
    item['choice'] = line['choice']
    items.append(item)
items.sort(lambda x, y: cmp(x['id'], y['id']))
context_obj = context.getObject()
if context_obj.getDuration():
  duration = context_obj.getDuration()
  duration_length = int(duration.split(' ').pop(0))
else:
  duration_length = int('99')
date = context_obj.getDate()
beginning_date = context_obj.getBeginningDate()
y = beginning_date.year()
m = beginning_date.month()
d = beginning_date.day()
stop_year = y+duration_length

# create corresponding assignment
for item in items:
  portal = context.getPortalObject()
  new_items=[]
#if the person in the fast input is a new person, create assignment
  if item['choice']=='_action_create':
    person_module = context.getPortalObject().person_module
    person_title = item['first_name'] + ' ' + item['last_name']
#    query = ComplexQuery(Query(title=person_title),
#                 Query(birth_date=item['start_date']),
#                 Query(birthplace_city=item['default_birthplace_address_city']),
#                 logical_operator="AND")
#    best_candidate_list=list(context.portal_catalog(portal_type='Person',
#                                        query=query))
#verify that the new person is not selected more than once in the fast input 
    new_items_list = filter(lambda x:(x['first_name']==item['first_name'] 
                           and x['last_name']==item['last_name']
                           and x['start_date']==item['start_date'] 
                           and x['default_birthplace_address_city']==item['default_birthplace_address_city']),items)
    person_title = item['first_name'] + ' ' + item['last_name']
#if the new person is selected only once then create the person and then the assignment
    if len(new_items_list)==1:
      person_third_party = person_module.newContent(portal_type='Person',
                                                   title=person_title,
                                                   first_name=item['first_name'],
                                                   last_name =item['last_name'],
                                                   start_date=item['start_date'],
                                                   password='secret',
                                        default_birthplace_address_city=item['default_birthplace_address_city'])
      person_third_party_assgmnt =person_third_party.newContent(portal_type='Assignment',
                                                                function=item['function'],
                                                                destination_form_value=context_obj,
                                                          start_date=context_obj.getBeginningDate(),
                                                     stop_date="%04d/%02d/%02d" % (stop_year, m, d))
      person_third_party_assgmnt.openSubmit()
#      if item['function']=='corporation/executive':
#         new_group = portal.portal_categories.group.newContent(portal_type='Category',
#                                                               id=context_obj.getReference())
#         new_group.setCodification(new_group.getId())
#         context_obj.setGroup(context_obj.getReference())
#if the person is selected more than once,create the person only once and then create the assignment
    elif len(new_items_list)>1:
      new_items.append(new_items_list[0])
      if item['id']==new_items_list[0]['id']:
        person_item =  person_module.newContent(portal_type ='Person',
                                            first_name=new_items_list[0]['first_name'],
                                            last_name=new_items_list[0]['last_name'],
                                            start_date=new_items_list[0]['start_date'],
                           default_birthplace_address_city=new_items_list[0]['default_birthplace_address_city'])
        person_item_asgt = person_item.newContent(portal_type ='Assignment',
                                                  function=item['function'],
                                                  destination_form_value=context_obj,
                                                  start_date=context_obj.getBeginningDate(),
                                                  stop_date="%04d/%02d/%02d" % (stop_year, m, d))
        person_item_asgt.openSubmit()
        new_items_assgt_list =filter(lambda x:(x['first_name']==item['first_name'] 
                                     and x['last_name'] ==item['last_name'] 
                                     and x['start_date']==item['start_date']
                                  and x['default_birthplace_address_city']==item['default_birthplace_address_city'] and x['function']!=item['function']),new_items_list)
        for w in new_items_assgt_list:
          w_assgmnt =person_item.newContent(portal_type='Assignment',
                                function=w['function'],
                                destination_form_value=context_obj,
                                start_date=context_obj.getBeginningDate(),
                                stop_date="%04d/%02d/%02d" % (stop_year, m, d))
          w_assgmnt.openSubmit()   
  elif item['choice']!='_action_create':
    result_list = portal.portal_catalog(parent_uid=portal.person_module.getUid(),
                                        relative_url=item['choice'])
    function_relative_url = '/'.join(('function', item['function']))
    destination_form_uid = context.portal_categories.destination_form.getUid()
    for object in result_list:
      asst_list = [x.getObject() for x in context.portal_catalog(parent_uid=object.getUid(),
                                                                 portal_type='Assignment',
                                                                 function_relative_url=function_relative_url,
                                                                 destination_form_uid=context_obj.getUid())]
      if asst_list ==[]:
        assgment = object.newContent(portal_type='Assignment',
                                     function=item['function'],
                                     destination_form_value=context_obj,
                                     start_date=context_obj.getBeginningDate(),
                                     stop_date="%04d/%02d/%02d" % (stop_year, m, d))
        assgment.openSubmit()
      else:
        pass
role_type = 'Assignment' 
form_id = 'P0_view'
ignore_layout = 0
editable_mode = 1
ignore_layout = int(ignore_layout)
editable_mode = int(editable_mode)
message = role_type.replace(' ', '+') + '(s)+added.'
redirect_url = '%s/%s?ignore_layout:int=%s&editable_mode:int=%s&portal_status_message=%s' % (
                                  context.absolute_url(),
                                  form_id,
                                  ignore_layout,
                                  editable_mode,
                                  message)
# return to the feature module
return context.REQUEST.RESPONSE.redirect(redirect_url)
