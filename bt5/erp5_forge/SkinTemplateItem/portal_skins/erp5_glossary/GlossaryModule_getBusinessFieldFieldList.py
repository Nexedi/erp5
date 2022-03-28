from Products.ERP5Type.Document import newTempBase

portal_catalog = context.portal_catalog
portal_skins = context.portal_skins

def get_term_list(business_field, reference):
  reference = reference.rsplit('_title', 1)[0]
  term_list = portal_catalog(portal_type='Glossary Term',
                             validation_state='validated',
                             language_id='en',
                             business_field_title=('core', business_field),
                             reference=reference)
  return [i.getObject() for i in term_list]

def get_field_and_reference_list(business_field):
  business_field = business_field.split('/')[0]
  result = []
  skin_folder = getattr(portal_skins, 'erp5_%s' % business_field, None)
  if skin_folder is None:
    skin_folder = getattr(portal_skins, business_field)

  for i in skin_folder.objectValues():
    if i.meta_type=='ERP5 Form':
      for f in i.objectValues():
        if f.id.startswith('my_'):
          r = f.id[3:]
          result.append((f, r))
        elif f.id.startswith('your_'):
          r = f.id[5:]
          result.append((f, r))
  return result

business_field_list = [i for i in business_field_list if i]

line_list = []
c = 0
item_dict = {}
for business_field in business_field_list:
  for field, reference in get_field_and_reference_list(business_field):
    term_list = get_term_list(business_field, reference)
    #if not term_list:
    #  continue
    if field in item_dict:
      continue
    item_dict[field] = True

    field_path = '%s/%s/%s' % (field.aq_parent.aq_parent.getId(),
                               field.aq_parent.getId(),
                               field.getId())

    c += 1
    field_title = field.get_value('title')
    field_description = field.get_value('description')
    field_note_list = []
    if field.meta_type=='ProxyField':
      if field.is_delegated('title') is True:
        field_note_list.append('Delegated.')
      elif field.get_recursive_tales('title') is not None:
        field_note_list.append('Tales is used.')

    if len(term_list) == 1 and \
        term_list[0].getTitle() == field_title and \
        term_list[0].getDescription() == field_description:
      continue

    line = newTempBase(context, 'tmp_glossary_field_%s' %  c)
    line.edit(field_title=field_title,
              field_path=field_path,
              field_edit_url = '%s/manage_main' % field.absolute_url(),
              field_note=' '.join(field_note_list),
              field_description=field_description,
              reference=reference,
              term_list=term_list,
              field_meta_type=field.meta_type
              )
    line.setUid(field_path)
    line_list.append(line)

line_list.sort(key=lambda x:x.field_path)
return line_list
