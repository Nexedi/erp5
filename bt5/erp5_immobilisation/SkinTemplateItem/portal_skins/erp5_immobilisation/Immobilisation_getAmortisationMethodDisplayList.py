return_list = [(context.Base_translateString('No Change', 'content'), 'no_change'),
               (context.Base_translateString('Unimmobilise', 'content'), 'unimmobilise')]

amortisation_method_list = context.Immobilisation_getAmortisationMethodList()

for method in amortisation_method_list:
  id = method[1].getId()
  display = method[1].title or id
  display = context.Base_translateString(display, 'content')
  return_list.append( ('(%s) %s' % (method[0], display), '%s/%s' % (method[0], id) ) )

return [(context.Base_translateString('Default Amortisation Data'),'')] + return_list
