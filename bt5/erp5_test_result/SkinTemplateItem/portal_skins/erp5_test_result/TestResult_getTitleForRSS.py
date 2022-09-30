test_result = context

return "%s (T:%s/F:%s/E:%s/S:%s)" % (context.getTitle(),
               test_result.getProperty('all_tests'),
               test_result.getProperty('failures'),
               test_result.getProperty('errors'),
               test_result.getProperty('skips'))
