structure = {}
structure['line'] = None
structure['line_list'] = []

if not ((is_report_tree_mode or is_domain_tree_mode) and max_section_depth):
  # When this is not a report tree, return the "plain structure"
  structure['line'] = None
  structure['line_list'] = [dict(line=x, line_list=[]) for x in listbox_line_list]
  return structure

def order_line_list(line_list, current_structure, depth=0, index=0, last_dict=None):
  if index < len(line_list):
    listbox_line = line_list[index]
    section_depth = listbox_line.getSectionDepth()
    if listbox_line.isDataLine():
      section_depth += 1
    if last_dict is None or section_depth == (depth +1):
      last_dict = {'line':listbox_line, 'line_list':[]}
      current_structure['line_list'].append(last_dict)
      index += 1
    elif section_depth == (depth +2):
      new_depth = section_depth
      new_structure = {'line':listbox_line, 'line_list':[]}
      last_dict['line_list'].append(new_structure)
      index += 1
      index = order_line_list(line_list, new_structure, depth=new_depth, index=index, last_dict=last_dict)
    elif section_depth > (depth +2):
      raise ValueError, "A depth is missing"
    else:
      return index
  if index < len(line_list):
    # FIXME: this way of recursing is not appropriate, as we reach very easily the maximum
    # recursion depth from python.
    index = order_line_list(line_list, current_structure, depth=depth, index=index, last_dict=last_dict)
  return index

order_line_list(listbox_line_list, structure, depth=-1, index=0)

return structure
