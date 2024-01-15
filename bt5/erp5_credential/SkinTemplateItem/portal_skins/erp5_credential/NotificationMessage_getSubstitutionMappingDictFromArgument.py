'''This script should be removed as soon as the
bug #1998 ('TextDocument should not required a substitution method')
is fixed'''

result = kw

if mapping_dict is not None:
  result.update(mapping_dict)

return result
