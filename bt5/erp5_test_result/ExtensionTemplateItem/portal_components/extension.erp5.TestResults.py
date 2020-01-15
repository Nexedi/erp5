import difflib
import zipfile
import os
import re
import sys
from cStringIO import StringIO
from zExceptions import Unauthorized

separator1 = '=' * 70
separator2 = '-' * 70

RUN_RE = re.compile(
    r'Ran\s*(?P<all_tests>\d+)\s*test(s)?\s*in\s*(?P<seconds>\d+.\d+)s',
    re.DOTALL)

STATUS_RE = re.compile(r"""
    (OK|FAILED)\s+\(
      (failures=(?P<failures>\d+),?\s*)?
      (errors=(?P<errors>\d+),?\s*)?
      (skipped=(?P<skips>\d+),?\s*)?
      (expected\s+failures=(?P<expected_failures>\d+),?\s*)?
      (unexpected\s+successes=(?P<unexpected_successes>\d+),?\s*)?
    \)
    """, re.DOTALL | re.VERBOSE)

FTEST_PASS_FAIL_RE = re.compile(
    r'.*Functional Tests, (?P<passes>\d+) Passes, (?P<failures>\d+) Failures')

SVN_INFO_REV_RE = re.compile(r"Revision: (?P<rev>\d+)")

TRACEBACK_RE = re.compile(separator1 + "\n(?P<tb>.*)", re.DOTALL)  # XXX how does "\n" is interpreted here?

def parseTestSuiteResults(file_handler):
  """
    Parse test suite results.
    Return:
      - successfull tests
      - failed tests
      - errors
      - log files

    # Note: this can be debugged with:
      curl -u zope:zope -F filepath=@ERP5-5525.zip\
         -F test_report_id= .... \
         http://host/erp5/test_result_module/TestResultModule_reportCompleted
  """
  # when called with a string argument, zipfile.ZipFile will open a local file.
  # we don't want this to happen
  if isinstance(file_handler, basestring):
    raise Unauthorized, file_handler
  zf = zipfile.ZipFile(file_handler)

  result = {}
  test_results = {}
  sorted_test_dict = {}
  svn_revision = 0

  for file_name in zf.namelist():
    file_data = zf.read(file_name)
    test_index = file_name.split(os.sep)[1]
    test_name = file_name.split(os.sep)[-2]
    file_name = file_name.split(os.sep)[-1]
    if file_data != '':
      test_results.setdefault(test_name, {})[file_name] = file_data
      sorted_test_dict[test_index] = test_name

  for sort_test_key in sorted(sorted_test_dict.keys()):
    test_id = sorted_test_dict[sort_test_key]
    test_result_detail = test_results[test_id]

    # parse test log to get number of successful/failed test
    is_zelenium_test_suite = 0
    html_test_result = ""
    seconds = 0
    all_tests = -1
    failures = 0
    errors = 0
    skips = 0
    test_log = test_result_detail.get('stderr', '')
    stdout = test_result_detail.get('stdout', '')
    cmdline = test_result_detail['cmdline']
    test_case = cmdline.split(' ')[-1]

    # guess "svn info", the first one is int_index, the second is string_index XXX dirty
    if 'svn info' in cmdline:
      for line in stdout.splitlines():
        search = SVN_INFO_REV_RE.search(line)
        if search:
          edit = result.setdefault('edit', {})
          if 'int_index' not in edit:
            # first time -> ERP5 main revision
            edit['int_index'] = search.groupdict()['rev']
          else:
            # second time -> project revision
            edit['comment'] = stdout

      continue

    if '--save' in cmdline:
      test_case = '%s (--save)' % test_case
    if 'runFunctionalTest' in cmdline or \
       'runExpressFunctionalTest' in cmdline or \
       'Firefox running' in test_log:
      test_case = 'Functional Tests'
      is_zelenium_test_suite = 1

    if is_zelenium_test_suite:
      # if this was a zelenium functional test, the output is completly
      # different
      junk, title, summary, detail = stdout.split('-' * 79)
      test_result_detail['stdout'] = summary
      html_test_result = detail
      search = FTEST_PASS_FAIL_RE.search(title)
      if search:
        groupdict = search.groupdict()
        passes = int(groupdict.get('passes', 0))
        failures = int(groupdict.get('failures', 0))
        all_tests = passes + failures

    else:
      # get all tests and elapsed time
      search = RUN_RE.search(test_log)
      if search:
        groupdict = search.groupdict()
        seconds = float(groupdict.get('seconds', 0.0))
        all_tests = int(groupdict.get('all_tests', 0))

      search = STATUS_RE.search(test_log)
      if search:
        groupdict = search.groupdict()
        errors = int(groupdict['errors'] or 0)
        failures = int(groupdict['failures'] or 0)
        skips = int(groupdict['skips'] or 0) \
              + int(groupdict['expected_failures'] or 0) \
              + int(groupdict['unexpected_successes'] or 0)

    if errors == 0 and failures == 0:
      test_result = 'PASSED'
      if all_tests == -1:
        test_result = 'UNKNOWN'
        all_tests = 0
    else:
      test_result = 'FAILED'


    this_test_result = dict(files=test_result_detail,
                            seconds=seconds,
                            all_tests=all_tests,
                            failures=failures,
                            errors=errors,
                            skips=skips,
                            test_case=test_case,
                            html_test_result=html_test_result,
                            svn_revision=svn_revision,
                            result=test_result)
    result[test_id] = this_test_result

  return result


def TestResult_sendEmailNotification(self, mail_to=None, mail_from=None,
                                     include_link=0, include_diff=1,
                                     full_stderr=0, full_stdout=0,
                                     max_line_count=5000):
  portal = self.getPortalObject()
  if not mail_from:
    mail_from = '%s <%s>' % (portal.getProperty('email_from_name'),
                             portal.getProperty('email_from_address'))
  comment = self.getProperty('comment')
  if comment and comment.startswith('Webproject'):
    comment = comment.replace(' Revision: ', '@')
  else:
    comment = ''

  subject = '%s %s: %s Tests, %s Errors, %s Failures, %s Skips' % (
    self.getTitle(), comment, self.getProperty('all_tests'),
    self.getProperty('errors'), self.getProperty('failures'),
    self.getProperty('skips'))

  mail_to_list = mail_to
  if isinstance(mail_to_list, basestring):
    mail_to_list = [mail_to_list]

  def formatSummary(test_result):
    mail_body = []
    p = mail_body.append
    failed_test_case_list = []
    with_skips_test_case_list = []
    unknown_status_test_case_list = []
    only_func_test = 1
    for tcr in test_result.contentValues(portal_type='Test Result Line',
                                         sort_on='title'):
      if (tcr.getProperty('errors', 0) + tcr.getProperty('failures', 0)):
        failed_test_case_list.append(tcr)
      elif (tcr.getProperty('string_index') == 'UNKNOWN'
            and 'runUnitTest' in tcr.getProperty('cmdline', '')):
        unknown_status_test_case_list.append(tcr)
      if tcr.getProperty('skips'):
        with_skips_test_case_list.append(tcr)
      if not tcr.getProperty('html_test_result'):
        only_func_test = 0

    # Don't send mail if we only run functional tests
    #if only_func_test:
    #  return

    p('Test Suite: %s' % test_result.getTitle())
    p('Revision: %s' % test_result.getReference() or test_result.getIntIndex())
    comment = test_result.getProperty('comment')
    if comment:
      p(comment)
    p('Result: %s' % test_result.getStringIndex())
    p('')

    if len([x for x in test_result.contentValues(portal_type='Test Result Node')
            if x.getSimulationState() == 'failed']):
      p('Building Failed')
      p('')

    p('All tests: %s' % test_result.getProperty('all_tests'))
    p('Failures: %s' % test_result.getProperty('failures'))
    p('Errors: %s' % test_result.getProperty('errors'))
    p('Skips: %s' % test_result.getProperty('skips'))

    p('')
    if include_link:
      p(' %s/%s/view' % (test_result.ERP5Site_getAbsoluteUrl(),
                         test_result.getRelativeUrl()))
    p('')

    if unknown_status_test_case_list:
      p('The following tests have an unknown status:')
      for tcr in unknown_status_test_case_list:
        p(tcr.getProperty('cmdline', ''))
    p('')

    if test_result.getStringIndex() == 'FAIL':
      p('The following tests failed:')

    for tcr in failed_test_case_list:
      errors = tcr.getProperty('errors')
      failures = tcr.getProperty('failures')
      skips = tcr.getProperty('skips')
      statuses = []
      if failures:
        statuses.append("%s failures" % failures)
      if errors:
        statuses.append("%s errors" % errors)
      if skips:
        statuses.append("%s skips" % skips)
      p('\n  %-50s (%s)' % (tcr.getTitle(), ', '.join(statuses)))

      for line in tcr.getProperty('stderr', '').splitlines():
        if line.startswith('ERROR: '):
          p('   %s' % line[7:])
        elif line.startswith('FAIL: '):
          p('   %s' % line[6:])
    p('')

    if with_skips_test_case_list:
      p('The following tests were at least partly skipped:')
      for tcr in with_skips_test_case_list:
        p('\n  %-50s (%s skips)' % (tcr.getTitle(), tcr.getProperty('skips')))
        for line in tcr.getProperty('stderr', '').splitlines():
            if 'skipped ' in line:
                p('   %s' % line)
    p('')

    return ('\n'.join(mail_body),
            failed_test_case_list,
            unknown_status_test_case_list)

  summary = formatSummary(self)
  if summary is None:
    return

  mail_body, failed_test_case_list, unknown_status_test_case_list = summary
  traceback_attachment = []
  END = separator2 + "\nRan"
  extend_attachment = traceback_attachment.extend
  for tcr in self.contentValues(sort_on='title'):
    if full_stdout:
      extend_attachment(tcr.getProperty('stdout', '').splitlines())
    if full_stderr or tcr in unknown_status_test_case_list:
      extend_attachment(tcr.getProperty('stderr', '').splitlines())
    elif tcr in failed_test_case_list:
      tb_list = tcr.getProperty('stderr', '').split(separator1)[1:]
      if len(tb_list):
        for tb in tb_list[:-1]:
          extend_attachment(tb.splitlines())
        extend_attachment(tb_list[-1].split(END)[0].splitlines())

  attachment_list = []
  if traceback_attachment:
    if include_diff:
      previous_test = self.TestResult_getPrevious()
      if previous_test is not None:
        summary = formatSummary(previous_test)
        if summary:
          diff = difflib.unified_diff(summary[0].splitlines(1),
                                      mail_body.splitlines(1),
                                      'summary', 'summary')
          attachment_list.append(dict(name='summary.diff',
                                      mime_type='text/x-diff',
                                      content=''.join(diff)))

    if len(traceback_attachment) > max_line_count:
      mail_body += ("\nAttached traceback has been truncated to the first"
                    " %s lines" % max_line_count)
      traceback_attachment[max_line_count:] = '', '', '(truncated) ...'
    content = '\n'.join(traceback_attachment)
    if isinstance(content, unicode):
      content = content.encode('utf8')
    attachment_list.append(dict(name='traceback.txt',
                                mime_type='text/plain',
                                content=content))

  send_mail = self.newContent(temp_object=True, portal_type='Url', id='_').send
  for mail_to in mail_to_list:
    send_mail(from_url=mail_from,
              to_url=mail_to,
              msg=mail_body,
              subject=subject,
              extra_headers={'ERP5-Tests': self.getTitle()},
              attachment_list=attachment_list)


def TestResultModule_viewTestResultChart(self, REQUEST,
                    title='', min_rev='', max_rev=''):
  """Render a chart of test runs per svn revision, using matplotlib.

  This is experimental use of matplotlib, not integrated with a field.
  """
  return 'disabled'
  ## XXX matplotlib cannot be imported it $HOME is not writable
  #os.environ['HOME'] = '/tmp'

  ## use a backend that doesn't need a $DISPLAY
  #import matplotlib
  #matplotlib.use('Cairo')
  #import pylab

  #revision_list = []
  #all_test_list = []
  #success_list = []

  #for test in self.searchFolder(
  #                  title=title,
  #                  int_index=dict(range='minmax',
  #                                 query=(min_rev or 0,
  #                                        max_rev or sys.maxint))):
  #  test = test.getObject()
  #  if not test.getIntIndex():
  #    continue
  #  revision_list.append(test.getIntIndex())
  #  all_tests = int(test.getProperty('all_tests', 0))
  #  all_test_list.append(all_tests)
  #  failures = (int(test.getProperty('errors', 0)) +
  #              int(test.getProperty('failures', 0)))
  #  success_list.append(all_tests - failures)

  #pylab.plot(revision_list, all_test_list)
  #pylab.plot(revision_list, success_list)
  #pylab.xlabel('svn revision')
  #pylab.legend(['all tests', 'success'])

  ## returns the image
  #out = StringIO()
  #pylab.savefig(out, format='png')
  #REQUEST.RESPONSE.setHeader('Content-type', 'image/png')
  #pylab.close()
  #return out.getvalue()
