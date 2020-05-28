from Products.ERP5Type.Document import newTempBase

portal_catalog = context.portal_catalog

def get_term_list(reference):
  reference = reference.rsplit(' Module', 1)[0]
  term_list = portal_catalog(portal_type='Glossary Term',
                             validation_state='validated',
                             language_id='en',
                             reference=reference)
  return [i.getObject() for i in term_list]

line_list = []
c = 0
portal_type_list = context.GlossaryModule_getAvailablePortalTypeList()
for reference in portal_type_list:
  portal_type = context.getPortalObject().portal_types[reference]
  term_list = get_term_list(reference)
  #if not term_list:
  #  continue

  c += 1
  field_description = portal_type.description
  if len(term_list) == 1 and \
     term_list[0].getDescription() == field_description:
    continue

  line = newTempBase(context, 'tmp_glossary_field_%s' %  c)
  line.edit(field_path=reference,
            field_edit_url = '%s/manage_main' % portal_type.absolute_url(),
            field_description=field_description,
            reference=reference,
            term_list=term_list,
            )
  line.setUid(reference)
  line_list.append(line)

line_list.sort(key=lambda x:x.field_path)
return line_list
