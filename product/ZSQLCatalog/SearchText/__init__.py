from SearchTextParser import parse, isAdvancedSearchText

def dequote(value):
  assert isinstance(value, basestring), value
  if len(value) >= 2 and value[0] == value[-1] == '"' and value[-2] != '\\':
    escaped = False
    value_list = []
    append = value_list.append
    for char in value[1:-1]:
      if escaped:
        escaped = False
        if char != '"':
          append('\\')
      else:
        if char == '\\':
          escaped = True
          continue
        if char == '"':
          raise ValueError('Cannot dequote substrings.')
      append(char)
    assert not escaped
    value = ''.join(value_list)
  return value

