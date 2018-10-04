"""
================================================================================
Get Lastest Documents of a certain Publication Section
================================================================================
"""
portal = language = validation_state = None
portal = context.getPortalObject()
portal_catalog = portal.portal_catalog
language = portal.Localizer.get_selected_language()
validation_state = (
  'released',
  'released_alive',
  'published',
  'published_alive',
  'shared',
  'shared_alive',
  'public',
  'validated'
)

def getUid(publication_section):
  publication_section_smallcaps = publication_section.lower()
  return portal.portal_categories.publication_section[publication_section_smallcaps].getUid()

if len(publication_section_list) > 0:
  publication_section_uid_list = map(lambda x:getUid(x), publication_section_list)

# beware of different dates: modificatio_date, creation_date, effective_date

if len(publication_section_uid_list) > 0:
  return portal_catalog(
    portal_type='Web Page',
    publication_section_uid=[x for x in publication_section_uid_list],
    validation_state=validation_state,
    language=language,
    sort_on=[('creation_date', 'descending')],
    group_by=('reference',),
    limit=[0, upper_limit]
  )
return []
