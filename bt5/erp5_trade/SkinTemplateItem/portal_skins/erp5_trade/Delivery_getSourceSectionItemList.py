from erp5.component.module.Log import log
log('Deprecated: use Base_getPreferredSectionItemList instead.')

section_cat = context.portal_preferences.getPreferredSectionCategory()
if section_cat in (None, '') :
  section_cat = context.getPortalDefaultSectionCategory()

section_cat_obj = None
result = []

if section_cat is not None:
  # get the organisations belonging to this group
  section_cat_obj = context.portal_categories.resolveCategory(section_cat)

if section_cat_obj is not None:
  result = section_cat_obj.getGroupRelatedValueList(portal_type='Organisation',
                                                    checked_permission='View')
  result = [r for r in result
            if r.getProperty('validation_state') not in ('invalidated', 'deleted')]

current_source_section = context.getSourceSectionValue()
if current_source_section is not None and current_source_section not in result:
  result.append(current_source_section)

# convert to ListField format
return [('', '')] + [(i.getTitle(), i.getRelativeUrl()) for i in result]
