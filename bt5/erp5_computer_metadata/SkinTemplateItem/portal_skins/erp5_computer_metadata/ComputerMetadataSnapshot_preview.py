import json

def traverse(d, depth):
  res = ""

  for name, value in d.iteritems():
    for _ in range(depth):
      res += "\t"
    res += name + "\n"
    if len(value['childs']) > 0:
      res += traverse(value['childs'], depth+1)

  return res

return traverse(json.loads(context.getData())['fs_tree']['childs'], 0)
