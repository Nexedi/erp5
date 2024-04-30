import datetime
from Products.PythonScripts.standard import Object

return [Object(duration=str(datetime.timedelta(seconds=int(context.getProperty('duration', 0)))),
               all_tests=context.getProperty('all_tests'),
               errors=context.getProperty('errors'),
               failures=context.getProperty('failures'),
               skips=context.getProperty('skips'),
               test_result_retry_count=context.getProperty('test_result_retry_count', 0),
               )]
