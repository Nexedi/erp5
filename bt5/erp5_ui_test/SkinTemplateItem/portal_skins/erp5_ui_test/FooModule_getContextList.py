"""Return the list of subobject with an alternate title"""
context_list = []
for r in context.searchFolder(**kw):
  obj = r.getObject()
  context = obj.asContext(alternate_title = obj.getTitle())
  context_list.append(context)
return context_list
