"""
  This scripts browses recursively a to generate a mirror structure
  within the current Web Section. It sets predicate parameters
  on all categories excluding itself.

  category -- the category to use
"""
# our pylint integration does not support global variabled in zope python script.
# pylint: disable=global-variable-undefined

from ZODB.POSException import ConflictError
portal = context.getPortalObject()
translateString = context.Base_translateString
category_tool = context.portal_categories
global section_count
section_count = 0
failed_list = []
portal_type_list = portal.getPortalDocumentTypeList() + portal.getPortalResourceTypeList()
valid_char = "abcdefghijklmnopqrstuvwxyz0123456789-_"

def getNiceID(s):
  if not s: return None
  s = s.lower()
  s = s.split()
  s = '-'.join(s)
  s = [c for c in s if c in valid_char]
  s = s.replace('_', '-')
  return s

def createWebSectionFromCategoryValue(container, category, depth, section_id=None):
  global section_count
  if section_id is None:
    try:
      # Check if this category looks like an int
      section_id = int(category.getId())
      # Looks like an int, so it should be converted into
      # something nicer based on the reference or on the title
      if category.hasReference():
        section_id = getNiceID(category.getReference())\
                  or getNiceID(category.getTitle()) or getNiceID(category.getId())
      if category.hasShortTitle():
        section_id = getNiceID(category.getShortTitle())\
                  or getNiceID(category.getTitle()) or getNiceID(category.getId())
      else:
        section_id = getNiceID(category.getTitle()) or getNiceID(category.getId())
    except ValueError:
      if not generate_nice_id:
        # It is not an int, so it can be used as is
        section_id = category.getId()
      else:
        if category.hasReference():
          section_id = getNiceID(category.getReference())\
                  or getNiceID(category.getTitle()) or getNiceID(category.getId())
        if category.hasShortTitle():
          section_id = getNiceID(category.getShortTitle())\
                  or getNiceID(category.getTitle()) or getNiceID(category.getId())
        else:
          section_id = getNiceID(category.getTitle()) or getNiceID(category.getId())
  # Create a new Web Section if necessary
  new_section = None
  if section_id not in container.contentIds():
    section_count += 1
    try:
      # If we are not browsing a standard Category tree, we
      # must add a trailing base_category_id
      if category.getPortalType() not in ('Category', 'Base Category'):
        category_url = '%s/%s' % (base_category_id, category.getRelativeUrl())
      else:
        category_url = category.getRelativeUrl()
      new_section = container.newContent( portal_type = 'Web Section'
                                        , id          = section_id
                                        , title       = category.getTitle()
                                        , description = category.getDescription()
                                        , visible     = True
                                        , membership_criterion_base_category = (base_category_id,)
                                        , membership_criterion_category      = (category_url,)
                                        , criterion_property_list = ['portal_type']
                                        )
      new_section.setCriterion('portal_type', identity=portal_type_list)
      new_section.updateLocalRolesOnSecurityGroups()
    except ConflictError:
      raise
    except Exception:
      failed_list.append(category.getRelativeUrl())
  else:
    new_section = container[section_id]
    # If we are not browsing a standard Category tree, we
    # must add a trailing base_category_id
    if category.getPortalType() not in ('Category', 'Base Category'):
      category_url = '%s/%s' % (base_category_id, category.getRelativeUrl())
    else:
      category_url = category.getRelativeUrl()
    if update_existing:
      new_section.edit(title       = category.getTitle()
                     , description = category.getDescription()
                     , visible     = True
                     , membership_criterion_base_category = (base_category_id,)
                     , membership_criterion_category      = (category_url,)
                     , criterion_property_list = ['portal_type']
                     )
      new_section.setCriterion('portal_type', identity=portal_type_list)
      new_section.updateLocalRolesOnSecurityGroups()
  # Call the function recursively
  if new_section is not None:
    # It is possible to browse objects which are not categories
    # ex. Projects
    if depth > 0:
      for sub_category in category.contentValues():
        createWebSectionFromCategoryValue(new_section, sub_category, depth - 1)
  # Remove sections which have no counterpart in categories
  if remove_missing:
    # XXX Not implemented yet
    pass

# Call the recursive section generator for each category
my_category_value = category_tool.restrictedTraverse(category)
base_category_id = my_category_value.getBaseCategory().getId()
createWebSectionFromCategoryValue(context, my_category_value, depth, section_id=section_id)

# Update section settings
if update_existing:
  section_value = getattr(context, section_id)
  if '/' in category:
    category_url = category
  else:
    # use the base category as a category to select all
    category_url = '%s/%s' % (category, category)
  section_value.edit(membership_criterion_base_category = (base_category_id,),
                     membership_criterion_category = (category_url,),
                     criterion_property_list = ['portal_type'])
  section_value.setCriterion('portal_type', identity=portal_type_list)

  section_value.updateLocalRolesOnSecurityGroups()


# Warn about failures if any
if failed_list:
  return context.Base_redirect(form_id,
    keep_items = dict(portal_status_message = translateString("Generated ${section_count} sections for the web site. Failed with ${failed_text}.",
    mapping = dict(section_count = section_count,
                 failed_text = ', '.join(failed_list)))))


return context.Base_redirect(form_id,
  keep_items = dict(portal_status_message = translateString("Generated ${section_count} sections for the Web Site.",
    mapping = dict(section_count = section_count))))
