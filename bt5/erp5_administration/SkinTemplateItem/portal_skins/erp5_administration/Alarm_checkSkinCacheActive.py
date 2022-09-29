"""\
Browse portal skins to seek for non cached files.

This Alarm returns one ActiveResult severity 100 if the file listed in this
script from portal_skins are not affected to a cache manager. If all files are
correct, it returns one ActiveResult severity 0.

If the `fixit` parameter is considered as true, the incorrect parsed files will
be affected to the chosen cache manager.
"""

# Cache manager to use
# examples: "http_cache" "anonymous_http_cache" "user_ram_cache"
cache_manager_id = "http_cache"

# check all files in..
meta_type_checklist = "Image", "File", "Filesystem Image", "Filesystem File"

# check all files which name endswith..
file_extension_checklist = ".css", ".js"

################################################################################
from Products.CMFActivity.ActiveResult import ActiveResult

incorrect_file_absolute_url_list = []

def some(iterable, function):
  for v in iterable:
    if function(v): return True
  return False

# Browse files and folders recursively
def execute(skin):
  for o in skin.objectValues():
    # browsing files
    oid = o.id
    # force oid to be a string
    if callable(oid): oid = oid()
    if o.meta_type in meta_type_checklist or \
       some(file_extension_checklist, oid.endswith):
      # this file matches the cheklists requirements
      current_cache_manager_id = o.ZCacheable_getManagerId()
      if current_cache_manager_id is None:
        # the current file is not cached
        if fixit: o.ZCacheable_setManagerId(cache_manager_id)
        else: incorrect_file_absolute_url_list.append(o.absolute_url(relative=1))
    elif o.meta_type == 'Folder':
      execute(o)

for skin in context.portal_skins.objectValues():
  execute(skin)

if incorrect_file_absolute_url_list != []:
  return ActiveResult(severity=100, detail="There is no cache set for:\n" + "\n".join(incorrect_file_absolute_url_list))

return ActiveResult(severity=0, detail="OK")
