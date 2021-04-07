test_result = sci['object']
kw = sci['kwargs']
test_result.setStartDate(kw.get('date') or DateTime())
