import json

return json.dumps(json.loads(context.getData()), sort_keys=True, indent=4)


def traverse(name, cur_dict, depth):
  raise NotImplementedError(cur_dict)
  for key, value in cur_dict['childs']:
    for i in range(depth):
      print "  ",
    print name
    traverse(key, value['childs'], depth+1)

traverse("", json.loads(context.getData())['fs_tree'], 0)

return printed
