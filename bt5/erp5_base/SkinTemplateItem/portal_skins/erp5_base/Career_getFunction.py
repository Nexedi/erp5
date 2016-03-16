'''Returns the function of this career or person.

We can only select leaves for career of person functions, so we don't show the
function if the function is a node in the function tree (this happens when
function is acquired from the subordination organisation).
'''
function_value = context.getFunctionValue()
if function_value is None or len(function_value):
  return None
return context.getFunction()
