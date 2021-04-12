activate_kw = {"tag" : tag}
folder = context.restrictedTraverse(folder_path)
method = getattr(context, method)
for id_ in id_list:
  ob = folder.get(id_)
  new_id = method(ob)
  if new_id != id_:
    ob.setDefaultActivateParameterDict(activate_kw)
    ob.setId(new_id)
