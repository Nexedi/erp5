portal = context.getPortalObject()
portal_types_tool = portal.portal_types

# --- Phase 1: discover the portal types actually usable by an end user,
# by walking every Module at the portal root and taking each module
# portal_type's Allowed Content Type List minus its Hidden Content Type
# List (the same "visible allowed content type" computation
# Folder.getVisibleAllowedContentTypeList() does, done here directly on
# the type info so it does not depend on the current user's permissions
# or on a live module instance).
module_list = []
for title, url in context.ERP5Site_getModuleItemList():
  module_id = url.rsplit('/', 1)[-1]
  module = portal.restrictedTraverse(module_id, None)
  if module is not None:
    module_list.append(module)

module_child_dict = {}  # module id -> sorted visible child portal_type ids
seed_type_set = set()
for module in module_list:
  module_type_info = portal_types_tool.getTypeInfo(module.getPortalType())
  if module_type_info is None:
    continue
  allowed = module_type_info.getTypeAllowedContentTypeList() or ()
  hidden = module_type_info.getTypeHiddenContentTypeList() or ()
  child_list = sorted(t for t in allowed if t not in hidden)
  if child_list:
    module_child_dict[module.getId()] = child_list
    seed_type_set.update(child_list)

# --- Phase 1b: extend the seed set with each discovered type's own
# visible allowed content types (e.g. Purchase Order -> Purchase Order
# Line), so line/sub-object types are documented too.
relevant_type_set = set()
allowed_child_dict = {}
queue = list(seed_type_set)
while queue:
  pt_id = queue.pop()
  if pt_id in relevant_type_set:
    continue
  relevant_type_set.add(pt_id)
  type_info = portal_types_tool.getTypeInfo(pt_id)
  if type_info is None:
    allowed_child_dict[pt_id] = []
    continue
  if type_info.getTypeFilterContentType():
    allowed = type_info.getTypeAllowedContentTypeList() or ()
    hidden = type_info.getTypeHiddenContentTypeList() or ()
    child_list = sorted(t for t in allowed if t not in hidden)
  else:
    child_list = None
  allowed_child_dict[pt_id] = child_list
  if child_list:
    queue.extend(child_list)

# Reverse map: portal_type -> which OTHER (non-module) portal types can
# contain it.
parent_dict = {}
for pt_id, child_list in allowed_child_dict.items():
  if child_list:
    for child_id in child_list:
      parent_dict.setdefault(child_id, []).append(pt_id)

# Reverse map: portal_type -> which module(s) it can be created directly
# inside.
module_parent_dict = {}
for module_id, child_list in module_child_dict.items():
  for child_id in child_list:
    module_parent_dict.setdefault(child_id, []).append(module_id)

line_list = [
  "# ERP5 Portal Type Reference",
  "",
  "Auto-generated reference of the portal types actually usable by an "
  "end user in this ERP5 instance: starting from every Module at the "
  "portal root, each module's Allowed Content Type List minus its "
  "Hidden Content Type List gives the portal types that can be created "
  "directly inside it; the same computation is then repeated on each "
  "discovered portal type to also reach sub-object types (e.g. order "
  "lines). For each portal type: its parent/child containment "
  "relations.",
  "",
  "## How to use this reference",
  "",
  "This reference only tells you which portal_type to use and where "
  "(module or parent document) - it says nothing about which actions "
  "or workflow transitions are available right now, since that depends "
  "on the specific document's current state and your permissions. For "
  "that, use this loop with the two generic tools below (there is no "
  "dedicated tool per portal_type or per action - creating a document "
  "is itself just an action):",
  "",
  "1. Look up the portal_type you need below to find where it can be "
  "created (a module id, or an existing parent document's relative_url).",
  "2. Call **ERP5Document_getActionList(relative_url)** on that module "
  "or parent document to see what can currently be created inside it "
  "(`can_create_here`) and, if it's an existing document, which "
  "workflow transitions (`workflow_action_list`) and custom object "
  "actions (`object_action_list`) are currently available on it - each "
  "entry has an `action_id` and, if that action opens a dialog, a "
  "`dialog_field_list` of the extra values it expects.",
  "3. Call **ERP5Document_doAction(relative_url, action_id, "
  "dry_run=True)** with `action_id = 'add <portal_type>'` (using one of "
  "the `can_create_here` values) to create the document. Before "
  "calling, go through step 2's `dialog_field_list` (or the equivalent "
  "listed against the parent type below) and pass a keyword argument "
  "for EVERY field the user already gave you a value for (a title, "
  "description, amount, related document, etc., with any `my_` prefix "
  "removed) - do not skip this and let it silently fall back to a "
  "blank default. A relation field, whose id usually ends in `_value`, "
  "takes the related document's relative_url as a string. Always "
  "preview with `dry_run=true` (the default) first and check its "
  "`property_dict` reflects what the user asked for; only pass "
  "`dry_run=false` once the user has confirmed.",
  "4. Call **ERP5Document_getActionList** again, this time on the "
  "newly-created (or just-acted-on) document's relative_url, to see "
  "what to do next - create a sub-object (e.g. an order line) by going "
  "back to step 3, or invoke a workflow transition or object action.",
  "5. Call **ERP5Document_doAction(relative_url, action_id, "
  "dry_run=True)** with an `action_id` taken from the most recent "
  "`ERP5Document_getActionList` call's `workflow_action_list` or "
  "`object_action_list` (never guess one). If that action had a "
  "`dialog_field_list`, pass a keyword argument for every field the "
  "user already gave you a value for, the same way as step 3 - do not "
  "call this with no keyword arguments just because the fields are "
  "optional; check dialog_field_list every time. Always preview with "
  "`dry_run=true` (the default) first and check its `property_dict`; "
  "only pass `dry_run=false` once the user has confirmed. Then go back "
  "to step 4 to see what's available next.",
  "",
]

for pt_id in sorted(relevant_type_set):
  type_info = portal_types_tool.getTypeInfo(pt_id)
  line_list.append("## %s" % pt_id)

  if type_info is None:
    line_list.append("(portal type definition not found)")
    line_list.append("")
    continue

  child_list = allowed_child_dict.get(pt_id)
  if child_list is None:
    line_list.append("Can contain: unrestricted (no allowed_content_type_list filter)")
  elif child_list:
    line_list.append("Can contain: %s" % ", ".join(child_list))
  else:
    line_list.append("Can contain: nothing (leaf type)")

  parent_hint_list = []
  for module_id in sorted(module_parent_dict.get(pt_id, [])):
    parent_hint_list.append("%s (module)" % module_id)
  for parent_id in sorted(parent_dict.get(pt_id, [])):
    parent_hint_list.append(parent_id)
  if parent_hint_list:
    line_list.append("Can be created inside: %s" % ", ".join(parent_hint_list))

  line_list.append("")

text_content = "\n".join(line_list)

skill_id = "skill_portal_type_reference"
web_page_module = portal.web_page_module
if getattr(web_page_module, skill_id, None) is not None:
  web_page = web_page_module[skill_id]
else:
  web_page = web_page_module.newContent(id=skill_id, portal_type="Web Page")

web_page.edit(
  title="ERP5 Portal Type Reference",
  content_type="text/plain",
  text_content=text_content,
)
try:
  if web_page.getValidationState() != 'validated':
    web_page.validate()
except Exception:
  pass

return "Generated %s (%d portal types, %d characters)" % (
  web_page.getRelativeUrl(), len(relevant_type_set), len(text_content))
