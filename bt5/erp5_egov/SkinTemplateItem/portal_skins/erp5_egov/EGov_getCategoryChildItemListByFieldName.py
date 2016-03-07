if field_name is None or field_name=="":
  return [('','')]

category = None

if field_name == "my_contact_function":
  category = context.portal_categories.function
elif field_name =="my_organisation_direction_service":
  category = context.portal_categories.group
elif field_name.startswith('my_involved_service_group_'):
  category = context.portal_categories.group
elif field_name.startswith('my_involved_service_function_'):
  category = context.portal_categories.function
elif field_name == "my_procedure_target":
  category = context.portal_categories.target
elif field_name == "my_submission_site_list":
  category = context.portal_categories.site
elif field_name == "my_procedure_publication_section":
  category = context.portal_categories.publication_section
elif field_name == "my_submission_site":
  category = context.portal_categories.site
elif field_name.startswith("my_civility"):
  category = context.portal_categories.gender


if category is not None:
  return context.Base_getPreferredCategoryChildItemList(category, filter_node=0, translate=False)
elif field_name.startswith("my_attachment_model_"):
  portal_type_list = context.portal_catalog(portal_type='Contribution Predicate')
  return [('','')] + [(a.getObject().getTitle(),a.getObject().getTitle()) for a in portal_type_list]
else:
  return [('','')]
