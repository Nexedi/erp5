"""Manage coverage reporting for ERP5 test runner.

This file is used in two contexts:
 - at the end of every test, this module is imported and `upload` is called to upload
 coverage data to WebDAV server.
 - this is ran as a unittest at the end, to download all coverage data from the WebDAV
 server and run coverage report.
"""

from __future__ import print_function
import datetime
import json
import logging
import os
import sys
import time
import unittest

import coverage
import requests
import six
import uritemplate
from six.moves.urllib.parse import urlparse, urljoin

from Products.ERP5Type.tests.runUnitTest import log_directory

REQUEST_TIMEOUT = 240

if six.PY2:
  TimeoutError = RuntimeError


def _get_auth_list_from_url(parsed_url):
  if parsed_url.username:
    # try Digest and Basic authentication
    return (
      requests.auth.HTTPDigestAuth(parsed_url.username, parsed_url.password),
      requests.auth.HTTPBasicAuth(parsed_url.username, parsed_url.password),
    )
  return (None,)


def _expand_uri_template(url, **kw):
  # Environment variables are set in product/ERP5Type/tests/runTestSuite.py
  kw.setdefault(
    'test_result_id',
    os.environ.get('ERP5_TEST_RESULT_ID', 'unknown_test_result_id'),
  )
  kw.setdefault(
    'test_result_revision',
    os.environ.get('ERP5_TEST_RESULT_REVISION', 'unknown_test_result_revision'),
  )
  return uritemplate.URITemplate(url).expand(**kw)


def upload(filename, upload_url_template, test_name):
  upload_url = _expand_uri_template(upload_url_template, test_name=test_name)
  parsed_url = urlparse(upload_url)
  hostname = parsed_url.hostname
  with requests.Session() as session:
    if 'insecure-skip-verify' in parsed_url.fragment:
      session.verify = False
    for retry in range(5):
      for auth in _get_auth_list_from_url(parsed_url):
        with open(filename, 'rb') as f:
          try:
            resp = session.put(upload_url, data=f, auth=auth, timeout=REQUEST_TIMEOUT)
          except requests.exceptions.RequestException as e:
            error = e
          else:
            if resp.ok:
              print('Uploaded coverage data to {hostname}'.format(hostname=hostname))
              return
            error = resp.status_code
        if (
          retry
        ):  # don't print error on first time, because `auth` might be wrong class
          print(
            'Error {error} uploading coverage data to {hostname} with {auth.__class__.__name__}'.format(
              error=error, hostname=hostname, auth=auth
            )
          )
        time.sleep(retry)


class CoverageReport(unittest.TestCase):
  def setUp(self):
    self._logger = logging.getLogger(__name__)
    self._coverage_process = coverage.Coverage.current()
    self._coverage_process.stop()

    with open(os.environ['ERP5_TEST_RUNNER_CONFIGURATION']) as f:
      self._test_runner_configuration = json.load(f)
    self._download_url_template = self._test_runner_configuration['coverage']['upload-url']
    assert self._download_url_template

    downloaded_coverage_path_set = self._download_coverage_data()
    self._coverage_process.combine(
      data_paths=downloaded_coverage_path_set,
    )
    self._coverage_process.save()

  def _download_coverage_data(self):
    downloaded_coverage_path_set = set()

    # TestResult_restartStuckLine redrafts a test line after 3 hours. Give up
    # before that to avoid silent restart instead of a clean TimeoutError.
    deadline = datetime.datetime.now() + datetime.timedelta(hours=2, minutes=45)

    coverage_data_directory = os.path.join(log_directory, 'coverage_data')
    if not os.path.exists(coverage_data_directory):
      os.makedirs(coverage_data_directory)

    to_download = set(
      json.loads(
        # ERP5_TEST_TEST_LIST is set in product/ERP5Type/tests/runTestSuite.py
        # it contains the list of tests as returned by ERP5TypeTestSuite.getTestList
        os.environ['ERP5_TEST_TEST_LIST'],
      )
    )

    with requests.Session() as session:
      if 'insecure-skip-verify' in urlparse(
          _expand_uri_template(self._download_url_template, test_name="")).fragment:
        session.verify = False
      while to_download:
        for test_name in list(to_download):
          test_file_name = test_name.replace(':', '_')
          download_destination = os.path.join(
            coverage_data_directory,
            '{test_name}.coverage.sqlite3'.format(test_name=test_file_name),
          )
          if os.path.exists(download_destination):
            downloaded_coverage_path_set.add(download_destination)
            to_download.remove(test_name)
            continue
          download_url = _expand_uri_template(
            self._download_url_template, test_name=test_file_name
          )
          parsed_url = urlparse(download_url)
          hostname = parsed_url.hostname
          for auth in _get_auth_list_from_url(parsed_url):
            try:
              resp = session.get(download_url, auth=auth, timeout=REQUEST_TIMEOUT)
            except requests.exceptions.RequestException:
              self._logger.exception('Error during request, retrying')
              continue
            if resp.ok:
              with open(download_destination + '.tmp', 'wb') as f:
                f.write(resp.content)
              os.rename(download_destination + '.tmp', download_destination)
              self._logger.info(
                'Downloaded %s coverage data from %s',
                test_name,
                hostname,
              )
              break
            self._logger.critical(
              'Error %s downloading coverage data for %s from %s with %s, retrying',
              resp.status_code,
              test_name,
              hostname,
              auth.__class__.__name__,
            )
            time.sleep(60 if resp.status_code == 404 else 5)
            if datetime.datetime.now() > deadline:
              raise TimeoutError("Timeout downloading %s" % to_download)
    return downloaded_coverage_path_set

  def test_coverage_report(self):
    # reports must run from the root of slapos software, because we recorded
    # relative paths.
    os.chdir(
      os.path.dirname(
        os.path.dirname(
          os.path.dirname(
            os.path.dirname(
              os.path.dirname(
                os.path.dirname(__file__),
              )
            )
          )
        )
      )
    )

    html_report_directory = os.path.join(log_directory, 'html_report')
    self._coverage_process.html_report(
      directory=html_report_directory,
      show_contexts=True,
      # We ignore errors because some tests execute code that does not exist on disk, causing
      # errors like this:
      #   NoSource: No source for code: 'parts/erp5/product/ERP5/Document/UnitTest.py'.
      #   Aborting report output, consider using -i.
      ignore_errors=True,
    )

    if six.PY3:
      self._coverage_process.lcov_report(
        outfile=os.path.join(log_directory, 'coverage.lcov'),
        ignore_errors=True,
      )

    total_coverage = self._coverage_process.report(
      file=sys.stderr,
      skip_covered=True,
      skip_empty=True,
      ignore_errors=True,
    )
    self.assertGreater(
      total_coverage,
      self._test_runner_configuration['coverage'].get('fail-under', 50),
    )

    # upload the coverage HTML report to the WebDAV server
    dirs_created = set()
    files_uploaded = set()
    parsed_url = urlparse(_expand_uri_template(self._download_url_template, test_name=''))
    with requests.Session() as session:
      if 'insecure-skip-verify' in parsed_url.fragment:
        session.verify = False
      for retry in range(10):
        last_error = None
        for auth in _get_auth_list_from_url(parsed_url):
          for root, dirs, files in os.walk(html_report_directory):
            for dir_ in dirs:
              if dir_ not in dirs_created:
                try:
                  resp = session.request(
                    'MKCOL',
                    urljoin(
                      _expand_uri_template(self._download_url_template, test_name=''),
                      'html_report/%s' % dir_),
                    auth=auth,
                    timeout=REQUEST_TIMEOUT,
                  )
                  resp.raise_for_status()
                  dirs_created.add(dir_)
                except requests.exceptions.RequestException as e:
                  last_error = e

            for filename in files:
              filepath = os.path.join(root, filename)
              if filepath not in files_uploaded:
                with open(filepath, 'rb') as f:
                  try:
                    resp = session.put(
                      urljoin(
                        _expand_uri_template(self._download_url_template, test_name=''),
                        'html_report/%s' % filename
                      ),
                      data=f,
                      auth=auth,
                      timeout=REQUEST_TIMEOUT
                    )
                    resp.raise_for_status()
                    files_uploaded.add(filepath)
                  except requests.exceptions.RequestException as e:
                    last_error = e
          if last_error:
            time.sleep(retry)
          else:
            break
    if last_error:
      raise last_error
