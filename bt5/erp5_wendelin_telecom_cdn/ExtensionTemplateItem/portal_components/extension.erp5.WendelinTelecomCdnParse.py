from zExceptions import Unauthorized
import re

CUSTOM_LOG_FORMAT_RE_LIST_LIST = [
  ['DEFAULT', re.compile(
   r'^(?P<client_ip>[^\s]+) - (?P<remote_user>[^\s]+) '
   r'\[(?P<date_time>.+)\] "(?P<http_method>[^\s]+) (?P<uri>[^\s]+) '
   r'(?P<http_version>[^\s]+)" (?P<status_code>.+) (?P<bytes>\d+) '
   r'"(?P<referer>.+)" "(?P<user_agent>.+)" (?P<request_time>\d+)')],
  ['FALLBACK_1', re.compile(
   r'^(?P<client_ip>[^\s]+) - (?P<remote_user>[^\s]+) '
   r'\[(?P<date_time>.+)\] "(?P<http_method>[^\s]+) (?P<uri>[^\s]+) '
   r'(?P<http_version>[^\s]+)" (?P<status_code>.+) (?P<bytes>\d+) '
   r'"(?P<referer>.+)" "(?P<user_agent>.+)')],
  ['FALLBACK_2', re.compile(
   r'^(?P<client_ip>[^\s]+) - (?P<remote_user>[^\s]+) '
   r'\[(?P<date_time>.+)\] "(?P<http_method>[^\s]+) (?P<uri>[^\s]+) '
   r'(?P<http_version>[^\s]+)" (?P<status_code>.+) (?P<bytes>\d+) '
   r'"(?P<referer>.+)')],
  ['FALLBACK_3', re.compile(
   r'^(?P<client_ip>[^\s]+) - (?P<remote_user>[^\s]+) '
   r'\[(?P<date_time>.+)\] "(?P<http_method>[^\s]+) (?P<uri>[^\s]+) '
   r'(?P<http_version>[^\s]+)" (?P<status_code>.+) (?P<bytes>\d+)')],
  ['FALLBACK_4', re.compile(
   r'^(?P<client_ip>[^\s]+) - (?P<remote_user>[^\s]+) '
   r'\[(?P<date_time>.+)\] "(?P<http_method>[^\s]+) (?P<uri>[^\s]+) '
   r'(?P<http_version>[^\s]+)" (?P<status_code>.+)')],
  ['FALLBACK_5', re.compile(
   r'^(?P<client_ip>[^\s]+) - (?P<remote_user>[^\s]+) '
   r'\[(?P<date_time>.+)\] "(?P<http_method>[^\s]+) (?P<uri>[^\s]+) '
   r'(?P<http_version>[^\s]+)"')],
  ['FALLBACK_LAST', re.compile(
   r'^(?P<client_ip>[^\s]+) - (?P<remote_user>[^\s]+) '
   r'\[(?P<date_time>.+)\] "(?P<http_method>[^\s]+) (?P<uri>[^\s]+)')]
]

def Base_parseFrontendLogLine(self, line, REQUEST=None):
  if REQUEST is not None:
    raise Unauthorized

  for _, matcher in CUSTOM_LOG_FORMAT_RE_LIST_LIST:
    match = matcher.match(line)
    if not match:
      continue
    return match.groupdict()
  return {}

def Base_parseFrontendLogLineList(self, log_line_list, REQUEST=None):
  if REQUEST is not None:
    raise Unauthorized

  result_list = []
  for line in log_line_list:
    match = Base_parseFrontendLogLine(self, line)
    if match:
      result_list.append(match)

  return result_list
