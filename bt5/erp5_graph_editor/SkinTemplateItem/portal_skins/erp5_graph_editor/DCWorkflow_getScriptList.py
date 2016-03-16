from Products.PythonScripts.standard import Object
object_list = []

def add(script):
  # we use a function for lambda's closure
  object_list.append(
    Object(uid='new_',
           getUid=lambda: 'new_',
           id=script.id,
           title_or_id=script.title_or_id,
           absolute_url=lambda: "%s/manage_main" % script.absolute_url(),
           getListItemUrl=lambda *args: "%s/manage_main" % script.absolute_url()))

for script in context.scripts.objectValues('Script (Python)'):
  add(script)
return object_list
