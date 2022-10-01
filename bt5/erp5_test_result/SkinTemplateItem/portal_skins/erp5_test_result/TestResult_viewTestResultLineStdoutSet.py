"""
Web API intended for listing, one per line, the report URL (typically present
in node's stdout) of all nodes involved in a Test Result.
Multiline stdout values behaviour is undefined.
"""
for test_result_node in context.objectValues(portal_type='Test Result Node'):
  if test_result_node.getCmdline() == 'LOG url':
    print(test_result_node.getStdout())
return printed
