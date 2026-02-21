"""Mask a personal record down to its name (GDPR).

The record half of the personal-data policy, kept in a script of its own so
that an instance can shadow Base_stripPersonalData -- and so add rules of its
own -- without either restating this one or recursing into itself. Called by
Base_stripPersonalData, and by an instance's shadow of it.

A record is personal when its portal type is one of
Base_getPersonalDataTypeList, or when it lives in the module of such a type,
which is what covers a Person's Address, Career and Assignment without any of
them being named here. Of such a record, only the name survives:

* the name itself -- title, first and last -- because it is how a document is
  spoken about at all. A search whose rows read "[redacted]" leaves a read
  tool with no answer to give, and the name is already spread over every
  document the same authenticated user may read;
* the scaffolding that says where the record is and how it is shaped:
  relative_url, portal_type, the views and actions a client offers, the
  columns of a listbox. Mask those and the record stops being addressable;
* everything else is masked, whatever it is called. Which is the point of
  deciding by portal type: a Person and an Organisation hold identically
  named properties, so no list of property names can tell an employee's home
  address from a company's billing address.

A field wrapper keeps its shape -- type, title, editability -- and loses only
what it says, so a client can still render the form.

Most results have nothing personal in them at all and are rebuilt unchanged,
which looks wasteful and is not: returning each node untouched unless
something below it was masked was measured against this, and came out
break-even where nothing is masked and slower where something is. The walk
itself is what costs, not the allocation, so it stays as simple as it reads.
"""
MASK = "[redacted]"
FIELD_PREFIX = "my_"

# Response scaffolding: the tool envelope (results, count, has_more), how a
# record is addressed (relative_url, uid, portal_type) and how a form is
# described (views, actions, columns). Returned untouched, and each resets the
# scope so that every record in a container is classified on its own -- which
# is why 'coordinate_type_title' belongs here: it names a label, not a party.
STRUCTURAL_SET = set([
  "relative_url", "url", "uid", "id", "portal_type", "translated_portal_type",
  "int_index", "parent", "views", "actions", "workflows", "exchanges",
  "reports", "jumps", "prints", "all_listboxes", "listbox",
  "columns", "default_sort", "form_relative_url",
  "has_create_action", "count", "offset", "next_offset", "has_more", "results",
  "items", "collected_count", "truncated", "total_count", "coordinate_type_title",
  "translated_id", "children", "children_common_fields",
])

# Where erp5_read puts the properties OF the record being read. Unlike the
# containers above these are not records of their own, so the scope carries
# into them rather than being worked out again.
SCOPED_CONTAINER_SET = set(["fields", "fields_by_view"])

# What a natural person may still be called.
NAME_SET = set([
  "title", "translated_title", "short_title",
  "first_name", "middle_name", "last_name", "name",
])

portal = context.getPortalObject()

declared_type_set = set(portal.Base_getPersonalDataTypeList())

# The module of each declared type, so that sub-objects are covered by where
# they live. getDefaultModule raises for a type that has no module of its own,
# such as Career; records of it are classified by their portal type instead.
personal_prefix_list = []
for declared_type in declared_type_set:
  try:
    module = portal.getDefaultModule(declared_type)
  except Exception:
    continue
  if module is not None:
    prefix = module.getId() + "/"
    if prefix not in personal_prefix_list:
      personal_prefix_list.append(prefix)


def in_personal_module(relative_url):
  for prefix in personal_prefix_list:
    if relative_url.startswith(prefix):
      return True
  return False


def record_portal_type(node):
  """The portal type of a record, as a single value.

  Listbox metadata carries 'portal_type' as a list of allowed types, which
  describes a form rather than a record, so only a scalar counts.
  """
  portal_type = node.get("portal_type")
  if isinstance(portal_type, (list, tuple, dict)):
    return None
  return portal_type


def is_personal_record(node, inherited):
  relative_url = node.get("relative_url") or ""
  portal_type = record_portal_type(node)
  if portal_type in declared_type_set or in_personal_module(relative_url):
    return True
  if portal_type or relative_url:
    return False
  return inherited          # a bare dict inherits the record it sits in


def is_name_key(key):
  if key.startswith(FIELD_PREFIX):
    key = key[len(FIELD_PREFIX):]
  return key in NAME_SET


def mask_value(value):
  """Keep a field's shape -- its type, title, editability -- lose what it says."""
  if isinstance(value, dict):
    if "value" in value:
      masked = dict(value)
      masked["value"] = MASK
      return masked
    return dict((k, mask_value(v)) for k, v in value.items())
  if isinstance(value, (list, tuple)):
    return [mask_value(item) for item in value]
  return MASK


def walk(node, personal):
  if isinstance(node, dict):
    personal = is_personal_record(node, personal)
    masked = {}
    for key, value in node.items():
      if key in SCOPED_CONTAINER_SET:
        masked[key] = walk(value, personal)    # the same record, still
      elif key in STRUCTURAL_SET:
        masked[key] = walk(value, None)        # scaffolding, or other records
      elif not personal:
        masked[key] = walk(value, personal)
      elif is_name_key(key):
        masked[key] = value                    # the name, wrapper and all
      else:
        masked[key] = mask_value(value)
    return masked
  if isinstance(node, (list, tuple)):
    return [walk(item, personal) for item in node]
  return node


return walk(data, None)
