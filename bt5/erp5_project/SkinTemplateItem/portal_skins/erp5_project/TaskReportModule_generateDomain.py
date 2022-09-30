#from erp5.component.module.Log import log
request = context.REQUEST
object_path = request.get('object_path')
if object_path is None:
  # Sometimes the object_path not comes with the request, when you edit for example.
  object_path = context.REQUEST.get('URL1').split('/')[-1]
domain_list = []

if depth == 0:
  category_list = [ context.task_report_module.getObject() ]

# XXX this is usefull but Breaks the edition
#elif depth == 1:
#    category_list = context.portal_selections.getSelectionValueList(context=context,
#                                                                    selection_name= 'task_report_module_selection')


else:
  return domain_list

for category in category_list:
  domain = parent.generateTempDomain(id = 'sub' + category.getId() )
  domain.edit(title = category.getTitle(),
              membership_criterion_base_category = ('parent', ),
              membership_criterion_category = (category.getRelativeUrl(),),
              domain_generator_method_id = script.id,
              uid = category.getUid())

  domain_list.append(domain)

#log("%s on %s" % (script.getId(), context.getPath()), "%d objects domain" %  len(domain_list))
return domain_list
