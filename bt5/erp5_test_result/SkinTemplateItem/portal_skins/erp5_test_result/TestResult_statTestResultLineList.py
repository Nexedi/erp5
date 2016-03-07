from Products.PythonScripts.standard import Object

return [Object(duration=int(context.getProperty('duration', 0)),
               all_tests=context.getProperty('all_tests'),
               errors=context.getProperty('errors'),
               failures=context.getProperty('failures'),
               skips=context.getProperty('skips'))]
