"""Recursively call a script on all subobjects.

From document pointed to by 'relative_url':
- If its depth is 1 (ie no slash) and 'id_list' isn't empty, immediately call a
  script ('method_id') on all objects given by id_list. Also call it
  recursively on subobjects if 'recursive' is true.
- Else, forward this call to its subobjects, which are given by 'id_list'.
  If id_list is None:
  - if 'relative_url' points to a HBTree and if 'full' is false,
    all subobjects for last 'hbtree_days' are considered.
  - else, all subobjects are considered.

 method_id  - Script to call.
 method_kw  - Dict containing arguments for 'method_id'.
 packet     - Maximum size (in number of objects to process)
              of created activities.

For the portal, 'relative_url' must be false and only module objects are
considered if id_list is None.
"""
document = context.getPortalObject()
context = document.portal_activities
if relative_url:
  document = document.restrictedTraverse(relative_url)
  depth = len(relative_url.split('/'))
else:
  depth = 0
maximum_depth = 1

assert depth <= maximum_depth

def activate(**kw):
  return context.activate(activity='SQLQueue', tag=tag, **kw)

if depth == maximum_depth and id_list:
  # Immediate recursive check
  error_list = []
  if method_kw is None:
    method_kw = {}
  def recurse(document):
    error_list.extend(getattr(document, method_id)(**method_kw) or ())
    if recursive:
      for subdocument in document.objectValues():
        recurse(subdocument)
  for id_ in id_list:
    recurse(document[id_])
  if active_process is None:
    return error_list
  if error_list:
    # Create an activity to update active_process,
    #  in order to prevent conflict errors.
    activate(active_process=active_process, priority=2) \
    .Base_makeActiveResult(title=relative_url, error_list=error_list)
else:
  if id_list is None:
    if full or not getattr(document, 'isHBTree', lambda: 0)():
      id_list = document.objectIds()
      if not depth:
        id_list = tuple(x for x in id_list if x.endswith('_module') or x in [
          'portal_alarms',
          'portal_categories',
          'portal_deliveries',
          'portal_orders',
          'portal_preferences',
          'portal_simulation',
          'portal_templates',
          'portal_trash',
        ])
    else:
      id_list = []
      for day_ago in xrange(hbtree_days):
        date = (DateTime() - day_ago).strftime('%Y%m%d')
        try:
          id_list += document.objectIds(base_id=date)
        except (TypeError, IndexError):
          pass

  result = None
  if active_process is None:
    result = active_process = context.newActiveProcess().getPath()
  kw = dict(active_process=active_process,
            tag=tag, full=full, recursive=recursive, packet=packet,
            method_id=method_id, method_kw=method_kw)
  active_script = getattr(activate(priority=4), script.id)
  if depth < maximum_depth:
    relative_url = relative_url and relative_url + '/' or ''
    for id_ in id_list:
      active_script(relative_url=relative_url + id_, **kw)
  else:
    kw['relative_url'] = relative_url
    for i in xrange(0, len(id_list), packet):
      active_script(id_list=tuple(id_list[i:i + packet]), **kw)
  # return the active process path if we created one
  return result
