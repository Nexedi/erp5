"""Usage example:

- in a url ``<your erp5 url>/portal_skins/Folder_resolvePath?path=**``
- in a script ``context.Folder_resolvePath("**")``
    - for a business template path list ``portal.Folder_resolvePath(bt.getTemplatePathList())``

Arguments:

- ``path`` can be a string or a list (if ``path_list`` is not defined).
- ``path_list`` must be a list (if ``path`` is not defined).
- ``traverse`` if True, return object list instead of path list.
- ``globbing`` if False, handle "*" and "**" as normal id.
"""
if path is None:
  if path_list is None:
    raise TypeError("`path` or `path_list` argument should be defined")
elif isinstance(path, (list, tuple)):
  path_list = path
else:
  path_list = [path]

context_is_portal = context.getPortalObject() == context
contextTraverse = context.restrictedTraverse

resolved_list = []
append = resolved_list.append

if globbing:
  for path in path_list:
    if path == "*" or (context_is_portal and path == "**"): # acts like _resolvePath in Products.ERP5.Document.BusinessTemplate.PathTemplateItem
      for sub_path, sub_obj in context.ZopeFind(context, search_sub=0):
        if traverse:
          append(sub_obj)
        else:
          append(sub_path)
    elif path == "**":
      for sub_path, sub_obj in context.ZopeFind(context, search_sub=1):
        if traverse:
          append(sub_obj)
        else:
          append(sub_path)
    elif path.endswith("/**"):
      parent_path = path[:-3]
      obj = contextTraverse(parent_path)
      for sub_path, sub_obj in obj.ZopeFind(obj, search_sub=1):
        if traverse:
          append(sub_obj)
        else:
          append(parent_path + "/" + sub_path)
    elif path.endswith("/*"):
      parent_path = path[:-2]
      obj = contextTraverse(parent_path)
      for sub_path, sub_obj in obj.ZopeFind(obj, search_sub=0):
        if traverse:
          append(sub_obj)
        else:
          append(parent_path + "/" + sub_path)
    else:
      if traverse:
        append(contextTraverse(path))
      else:
        append(path)
else:
  for path in path_list:
    if traverse:
      append(contextTraverse(path))
    else:
      append(path)
return resolved_list
