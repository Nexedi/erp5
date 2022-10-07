"""
portal_type (None, string)
  Ignored if use_relative_url is not None.
  Used to determine use_relative_url, using preference settings for given
  portal type.
  When None, context's portal_type is used.
include_context (bool)
  Add context's category to return value if not already present.
empty_item (bool)
  Controls presence of ['', ''] element in result.
indent_category (bool)
  When true, category captions are indented.
  When false, categories captions are paths, relative to topmost category (not
  necessarily a Base Category !).
indent_resource (bool)
  When true, resource captions are indented.
  When false, resource captions are not indented.
compact (bool)
  When true, getCompactTranslatedTitle is used to generate captions.
  When false, getTranslatedTitle is used to generate captions.
empty_category (bool)
  When true, categories with no resource children (at any depth) are present
  in result.
  When false, categories with no resource children (at any depth) are pruned
  from result.
use_relative_url (None, string)
  The "use"-category-relative path of category to start recursing from.

When indent_category, indent_resource and compact are simultaneously not
provided (or None), a default is built from
getPreferredCategoryChildItemListMethodId.
"""
# Note: a possible improvement would be to merge consecutive disabled entries.
# This is difficult though, because it requires splitting work a lot,
# increasing complexity significantly for such little improvement:
# - non-child categories must not be concatenated (empty /1/12/ must not be
#   merged with a following /2/)
# - all resource child must be properly indented
# It is much simpler if only "empty_category=False" case is handled.
from Products.ERP5Type.Cache import CachingMethod
from AccessControl import getSecurityManager
from six.moves import range
portal = context.getPortalObject()
checkPermission = portal.portal_membership.checkPermission
portal_preferences = portal.portal_preferences
if use_relative_url is None:
  use_relative_url = portal_preferences.getPreference(
    'preferred_' + (portal_type or context.getPortalType()).lower().replace(' ', '_') + '_use',
  )
if indent_category == indent_resource == compact == None:
  indent_category, indent_resource, compact = {
    'getCategoryChildTranslatedCompactLogicalPathItemList': (False, False, True),
    'getCategoryChildTranslatedLogicalPathItemList': (False, True, False),
    'getCategoryChildTranslatedIndentedCompactTitleItemList': (True, False, True),
    'getCategoryChildTranslatedIndentedTitleItemList': (True, True, False),
  }.get(portal_preferences.getPreferredCategoryChildItemListMethodId(), (True, True, False))

accessor_id = 'getCompactTranslatedTitle' if compact else 'getTranslatedTitle'

def getResourceItemList():
  INDENT = portal_preferences.getPreferredWhitespaceNumberForChildItemIndentation() * '\xc2\xa0' # UTF-8 Non-breaking space
  RESOURCE_INDENT = INDENT if indent_resource else ''
  getResourceTitle = lambda resource, category, depth: RESOURCE_INDENT * depth + getattr(resource, accessor_id)()
  if indent_category:
    def getCategoryTitle(category, depth):
      return INDENT * depth + getattr(category, accessor_id)()
  else:
    def getCategoryTitle_(category, depth):
      result = []
      append = result.append
      for _ in range(depth + 1):
        append(getattr(category, accessor_id)())
        category = category.getParentValue()
      return '/'.join(result[::-1])
    if indent_resource:
      getCategoryTitle = getCategoryTitle_
    else:
      getCategoryTitle = lambda category, depth: None
      def getResourceTitle(resource, category, depth): # pylint:disable=function-redefined
        resource_title = getattr(resource, accessor_id)()
        # depth - 1 because we are at category's child level
        category_path = getCategoryTitle_(category, depth - 1)
        if category_path:
          return category_path + '/' + resource_title
        return resource_title
  def recurse(category, depth):
    child_list, resource_list = category.Category_getUseCategoryListAndResourceList()
    # Resources before child categories, to avoid ambiguity when resources are not indented
    result = sorted(
      [(getResourceTitle(x, category, depth), x.getRelativeUrl()) for x in resource_list],
      key=lambda x: x[0],
    )
    append = result.append
    extend = result.extend
    for _, caption, grand_child_list in sorted(
          [(x.getIntIndex(), getCategoryTitle(x, depth), recurse(x, depth + 1)) for x in child_list if checkPermission('View', x)],
          key=lambda x: x[:2],
        ):
      if grand_child_list or empty_category:
        if caption is not None:
          append((caption, None))
        extend(grand_child_list)
    return result
  category = portal.portal_categories.getCategoryValue(use_relative_url, base_category='use')
  if category is None or not checkPermission('View', category):
    return []
  return recurse(category, 0)

result = CachingMethod(
  getResourceItemList,
  id=(
    script.id,
    context.Localizer.get_selected_language(),
    bool(indent_resource),
    bool(indent_category),
    accessor_id,
    bool(empty_category),
    use_relative_url,
    getSecurityManager().getUser().getId(),
  ),
  cache_factory='erp5_ui_long',
)()
if empty_item:
  prefix = [('', '')]
else:
  prefix = []
if include_context:
  context_resource_value = context.getResourceValue()
  context_resource = context.getResource()
  if context_resource_value is not None and context_resource not in [x for _, x in result]:
    prefix.append((getattr(context_resource_value, accessor_id)(), context_resource))
return prefix + result
