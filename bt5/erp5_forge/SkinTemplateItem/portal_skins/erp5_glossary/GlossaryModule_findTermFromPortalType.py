result = context.GlossaryModule_getTermDictListFromPortalType(portal_type_list)

if export_tsv:
  for i in result:
    print('\t'.join(['"%s"' % x for x in (i['reference'], i['language'],
                                            i['business_field'],
                                            i['title'], i['description'],
                                            i['field_path'])]))
  return printed
else:
  portal_catalog = context.portal_catalog
  num = 0
  for i in result:
    item_list = portal_catalog(portal_type='Glossary Term',
                               reference=i['reference'], language_id=i['language'],
                               business_field_title=i['business_field'],
                               validation_state="!=deleted")
    if len(item_list)>0:
      continue

    new_id = context.generateNewId()
    context.newContent(id=new_id, portal_type='Glossary Term',
                       container=context,
                       reference=i['reference'], language=i['language'],
                       business_field=i['business_field'],
                       title=i['title'], description=i['description'],
                       comment=i['field_path'])
    num += 1


portal_status_message = context.Base_translateString('%d terms created.' % num)
context.Base_redirect(keep_items={'portal_status_message':portal_status_message})
