from zExceptions import Unauthorized
if REQUEST is not None:
  raise Unauthorized

result = None
accept = context.Base_getRequestHeader('Accept', default='*/*')
for accepted_type in accepted_type_list:
  if accepted_type in accept:
    # XXX Really simple and stupid matching.
    # Better test to ensure best matching type
    result = accepted_type
    break

if (result is None) and ('*/*' in accept):
  result = accepted_type_list[0]

return result
