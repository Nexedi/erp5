from Products.ERP5Type.Document import newTempBase
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery, SimpleQuery
from DateTime import DateTime

rev_query_list = []
if isinstance(kw.get('from_date'), DateTime):
  rev_query_list.append(SimpleQuery(creation_date=kw['from_date'],
                                    comparison_operator='>='))
if isinstance(kw.get('at_date'), DateTime):
  rev_query_list.append(SimpleQuery(creation_date=kw['at_date'],
                                    comparison_operator='<='))

test_result_list = []
revision = None
new_test_result_list = []
context.log("rev_query_list", rev_query_list)
if rev_query_list:
  result = context.searchFolder(title='PERF-ERP5-MASTER', simulation_state='stopped',
    revision=ComplexQuery(operator='AND', *rev_query_list),
    sort_on=(('delivery.start_date', 'ASC'),),src__=1)
  context.log("result", result)
  for test in context.searchFolder(title='PERF-ERP5-MASTER', simulation_state='stopped',
    revision=ComplexQuery(operator='AND', *rev_query_list),
    sort_on=(('delivery.start_date', 'ASC'),)):
    test = test.getObject()
    if revision != test.getReference():
      revision = test.getReference()
      test_result = {'rev': str(revision)}
      test_result_list.append(test_result)
    for prop in 'all_tests', 'failures', 'errors':
      test_result[prop] = test_result.get(prop, 0) + test.getProperty(prop, 0)
    line_list = test.TestResult_getTestPerfTimingList()
    timing_dict = test_result.setdefault('timing_dict', {})
    for line in line_list:
      for k, v in line.items():
        timing_dict.setdefault(k, []).append(v)

  normalize = kw.get('normalize')
  base_result = {}

  for test_result in test_result_list:
    if test_result['errors'] < test_result['all_tests']:
      new_test_result = newTempBase(context, '')
      for k, v in test_result.pop('timing_dict').items():
        if v:
          v = sum(v) / len(v)
          test_result[k] = v / base_result.setdefault(k, normalize and v or 1)
      new_test_result.edit(**test_result)
      new_test_result_list.append(new_test_result)

return new_test_result_list
