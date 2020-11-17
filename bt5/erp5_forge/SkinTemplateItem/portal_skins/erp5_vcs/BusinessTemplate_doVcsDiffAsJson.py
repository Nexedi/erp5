import json

vcs_tool = context.getVcsTool()

result_dict = {
  'added_list': [],
  'modified_list': [],
  'deleted_list': []
}

for path in modified:
  result_dict['modified_list'].append({
    'path': path,
    # 'edit_path': vcs_tool.editPath(path, True),
    'diff': vcs_tool.diff(path)
  })
for path in added:
  result_dict['added_list'].append({
    'path': path
  })
for path in deleted:
  result_dict['deleted_list'].append({
    'path': path
  })

if REQUEST is not None:
  REQUEST.RESPONSE.setHeader('Content-Type', 'application/hal+json')
  return json.dumps(result_dict, indent=2)
else:
  return result_dict
