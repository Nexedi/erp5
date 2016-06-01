"""
  This parameters are default browser behavior with url normalization

  - if keep_empty is True: `a//` -> `a//` else `a//` -> `a/`;
  - if keep_single_dot is False: `./a` -> `a` else `./a` -> `./a`;
  - if keep_double_dot is False: `/../a` -> `/a` else `/../a` -> `/../a`
  - if keep_trailing_slash is True: `/a//` -> `/a//` else `/a//` -> `/a`
"""
outer_component_list = []
inner_component_list = []
suffix_list = []
dont_keep_empty = not keep_empty
dont_keep_single_dot = not keep_single_dot
dont_keep_double_dot = not keep_double_dot
starts_with_slash = False
if pathname[:1] == "/":
  pathname = pathname[1:]
  starts_with_slash = True
if pathname[-1:] == "/":
  pathname = pathname[:-1]
  if keep_trailing_slash:
    suffix_list.append("")
component_list = pathname.split("/")
for component in component_list:
  if component == ".." and dont_keep_double_dot:
    if inner_component_list:
      inner_component_list.pop()
    else:
      outer_component_list.append("..")
  elif not (component == "" and dont_keep_empty or
            component == "." and dont_keep_single_dot):
    inner_component_list.append(component)
if starts_with_slash:
  return "/" + "/".join(inner_component_list + suffix_list)
return "/".join(outer_component_list + inner_component_list + suffix_list)
