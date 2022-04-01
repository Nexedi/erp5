#from Products.ERP5Type.Document import newTempBase
#from Products.ZSQLCatalog.SQLCatalog import ComplexQuery, SimpleQuery
from builtins import str
from past.utils import old_div
from DateTime import DateTime


"""
rev_query_list = []
if isinstance(kw.get('from_date'), DateTime):
  rev_query_list.append(SimpleQuery(creation_date=kw['from_date'],
                                    comparison_operator='>='))
if isinstance(kw.get('at_date'), DateTime):
  rev_query_list.append(SimpleQuery(creation_date=kw['at_date'],
                                    comparison_operator='<='))
"""
test_result_list = []
revision = None
new_test_result_list = []

portal = context.getPortalObject()
if query:
  for test in portal.test_result_module.searchFolder(title='PERF-ERP5-MASTER', simulation_state='stopped',
    full_text=query,
    sort_on=(('delivery.start_date', 'ASC'),)):
    test = test.getObject()
    if revision != test.getReference():
      revision = test.getReference()
      revision_list = []
      for revision_part in revision.split(','):
        repository, commit_hash = revision_part.split('-')
        revision_list.append('%s-%s' % (repository, commit_hash[0:7]))
      revision = ",".join(revision_list)
      test_result = {'revision': str(revision) + '|' + test.getStartDate().strftime("%Y/%m/%d")}
      test_result_list.append(test_result)
    for prop in 'all_tests', 'failures', 'errors':
      test_result[prop] = test_result.get(prop, 0) + test.getProperty(prop, 0)
    line_list = test.TestResult_getTestPerfTimingList()
    timing_dict = test_result.setdefault('timing_dict', {})
    for line in line_list:
      for k, v in list(line.items()):
        timing_dict.setdefault(k, []).append(v)

  normalize = kw.get('normalize', 1)
  base_result = {}

  for test_result in test_result_list:
    if test_result['errors'] < test_result['all_tests']:
      new_test_result = {}
      for k, v in list(test_result.pop('timing_dict').items()):
        if v:
          v = old_div(sum(v), len(v))
          # too much value is not productive
          if k in ('all_tests', 'errors', 'failures') or k.find('_') > 0 and k.split('_')[1] in ('200', '300', '400', '500', '600', '700', '800', '900'):
            continue
          new_test_result[k] = old_div(v, base_result.setdefault(k, normalize and v or 1))
      new_test_result['revision'] = test_result['revision']
      new_test_result.update(**new_test_result)
      new_test_result['_links'] = {'self': {}} # required by jio.allDocs API
      new_test_result_list.append(new_test_result)
import json
context.log("new_test_result_list", new_test_result_list)
return json.dumps({'_embedded': {'contents':new_test_result_list}})
