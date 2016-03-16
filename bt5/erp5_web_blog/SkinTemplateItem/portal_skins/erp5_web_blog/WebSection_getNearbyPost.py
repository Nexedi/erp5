result = {"previous": None, "next": None}

items = [x.getReference() for x in context.getWebSectionValue().getDocumentValueList()]

try:
  index = items.index(context.getReference())
except:
  return result

if index > 0:
  result["previous"] = items[0]
if index+1 < len(items):
  result["next"] = items[index+1]

return result
