import difflib

def diff_recursive(object_a, object_b):
  """
    Recursively diffs between object a and object b.
    Well, not recursive yet - just analyses the first nesting level.
  """

  result_diff = {}
  result_absent_from_a = {}
  result_absent_from_b = {}

  object_a_id_list = object_a.objectIds()
  object_b_id_list = object_b.objectIds()
  in_a_not_in_b = []

  for id in object_a_id_list:
    try:
      index_in_b = object_b_id_list.index(id)
      del object_b_id_list[index_in_b]
      diff_result = diff_objects(object_a[id], object_b[id])
      if len(diff_result) > 0:
        result_diff[id] = []
        for line in diff_result:
          result_diff[id].append(line)
    except ValueError:
      in_a_not_in_b.append(id)
  for id in object_b_id_list:
    result_absent_from_a[id] = None
  for id in in_a_not_in_b:
    result_absent_from_b[id] = None
  return (result_diff, result_absent_from_a, result_absent_from_b)


def diff_objects(object_a, object_b):
  """
    Returns a list of lines of the unified diff between object a and object b.
    Requires tuning to support specific object types.
    Supported meta_types are:
      ERP5 Form (incomplete)
      Script (Python)
      Z SQL Method
      Page Template
      DTML Document (incomplete)
      DTML Method
  """
  if object_a.meta_type != object_b.meta_type:
    return ["Unable to diff : meta_type don't match !"]
  if object_a.meta_type == 'Script (Python)':
    a = object_a._body
    b = object_b._body
  elif object_a.meta_type == 'Page Template':
    a = object_a._text
    b = object_b._text
  elif object_a.meta_type in ('DTML Document', 'DTML Method'):
    a = object_a.raw
    b = object_b.raw
  elif object_a.meta_type == 'ERP5 Form':
    result = []
    a_field_id_list = object_a.objectIds()
    b_field_id_list = object_b.objectIds()
    in_a_not_in_b = []
    for id in a_field_id_list:
      try:
        index_in_b = b_field_id_list.index(id)
        del b_field_id_list[index_in_b]
        field_a = object_a[id]
        field_b = object_b[id]
        temp_result = []
        for property_dict_id in ('values', 'tales', 'overrides'):
          a_property_dict = getattr(field_a, property_dict_id)
          b_property_dict = getattr(field_b, property_dict_id)
          for property_id, a_property_value in six.iteritems(a_property_dict):
            b_property_value = b_property_dict[property_id]
            if a_property_value != b_property_value:
              if isinstance(a_property_value, str) and isinstance(b_property_value, str):
                temp_result.append('    %s:%s' % (property_dict_id, property_id))
                temp_result.append('    --- %s' % (a_property_value, ))
                temp_result.append('    +++ %s' % (b_property_value, ))
              else:
                temp_result.append('    %s:%s (difference cannot be displayed)' % (property_dict_id, property_id))
        if len(temp_result):
          result.append('  %s' % (id, ))
          result.extend(temp_result)
      except ValueError:
        in_a_not_in_b.append(id)
    if len(b_field_id_list):
      result.append('Fields missing in first object')
      for id in b_field_id_list:
        result.append('  %s' % (id, ))
    if len(in_a_not_in_b):
      result.append('Fields missing in second object')
      for id in in_a_not_in_b:
        result.append('  %s' % (id, ))
    return result
  elif object_a.meta_type == 'Z SQL Method':
    a = object_a.src
    b = object_b.src
  else:
    return ["Unable to diff : unknown meta_type '%s'" % (object_a.meta_type, )]
  result = []
  for line in difflib.unified_diff(a.split('\n'), b.split('\n')):
    result.append(line)
  return result
