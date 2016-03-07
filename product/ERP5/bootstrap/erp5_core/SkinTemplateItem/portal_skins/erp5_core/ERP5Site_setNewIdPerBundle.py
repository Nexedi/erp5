activate_kw = {"tag" : tag}
folder = context.restrictedTraverse(folder_path)
method = getattr(context, method)
for id in id_list:
  ob = folder.get(id)
  new_id = method(ob)
  ob.setDefaultActivateParameterDict(activate_kw)
  ob.setId(new_id)
