"""
  Called by portal_contributions.getPropertyDictFromFilename

  Receives file name and a dict of properties found in file name by
  using regular expression defined in preferences. 

  Uses provided arguments to generate document's reference, language, 
  title, follow_up and/or source_conference.

  If necessary can do additional things (like mapping
  portal type id to portal type name).

  Type-based.
"""
# convert language to lowercase
if 'language' in property_dict:
  property_dict['language'] = property_dict['language'].lower()

language = property_dict.get('language', 'en')
version = property_dict.get('version', '001')
local_reference = property_dict.get('local_reference', 'undefined')
local_id = property_dict.get('local_id', 'undefined')
reference = property_dict.get('reference', None)
node_reference = property_dict.get('node_reference', None)
group_reference_path = property_dict.get('group_reference_path', None)
source_conference_reference = property_dict.get('source_conference_reference', None)
follow_up_reference = property_dict.get('follow_up_reference', None)

new_dict = dict(language = language, 
                version = version)

if reference:
  # we get directly extracted reference in property_dict (from re pattern)
  # this method has highest priority
  pass
elif node_reference:
  # generate document's reference using project reference
  reference = '%s-%s' % (node_reference, local_reference)
  node = context.portal_catalog.getResultValue(reference=node_reference)

  if node is not None:
    node_portal_type = node.getPortalType()
    if node_portal_type in context.getPortalTicketTypeList()+context.getPortalProjectTypeList():
      # For a project or a ticket, associate it explicitely to the document
      new_dict['follow_up'] = node.getRelativeUrl()
    elif node_portal_type == 'Category':
      # Check if it's a group
      # FIXME XXX Maybe we want to make it usable for all categories ?
      # new_dict[node.getBaseCategory().getId()] = node.getCategoryRelativeUrl()
      if node.getBaseCategory().getId() == 'group':
        new_dict['group'] = node.getCategoryRelativeUrl()
      elif node.getBaseCategory().getId() == 'publication_section':
        new_dict['publication_section'] = node.getCategoryRelativeUrl()
    else:
      # It seems to be a business document reference
      # Should be detected automatically, and no explicit relation is required
      pass

# XXX Is those hardcoded part required ?
# For now, keep it for compatibility
elif follow_up_reference:
  # generate document's reference using project reference
  reference = 'P-%s-%s' %(follow_up_reference, local_id)
  project = context.portal_catalog.getResultValue(reference = follow_up_reference,
                                                  portal_type = 'Project')
  if project:
    new_dict['follow_up'] = project.getRelativeUrl()
elif source_conference_reference:
  # generate document's reference using conference reference
  reference = 'C-%s-%s' % (source_conference_reference, local_id)
  conference = context.portal_catalog.getResultValue(reference = follow_up_reference,
                                                     portal_type = 'Conference')
  if conference:
    new_dict['source_conference'] = conference.getRelativeUrl()
elif group_reference_path:
  # generate document's reference using conference reference
  reference = '%s-%s' % (group_reference_path, local_id)
  group_reference_list = group_reference_path.split('-')
  if group_reference_list:
    group_id = group_reference_list[0]
    category = context.portal_catalog.getResultValue(reference = group_id, 
                                                     portal_type = 'Category')
    if category is not None and category.getBaseCategory().getId()=='group':
      for group_id in group_reference_list[1:]:
        category = context.portal_catalog.getResultValue(reference = group_id, 
                                                         parent_uid = category.getUid(),
                                                         portal_type = 'Category')
        if category is None: 
          break
  if category is not None:
    new_dict['group'] = '/'.join(category.getRelativeUrl().split('/')[1:])


else:
  # no reference could be found
  # XXX: This can break DMS/KM functionality especially revision support!
  reference = None

if reference:
  new_dict['reference'] = reference

# Set title to file_name by default
new_dict['title'] = property_dict.get('title', file_name.rsplit('.', 1)[0])

return new_dict
