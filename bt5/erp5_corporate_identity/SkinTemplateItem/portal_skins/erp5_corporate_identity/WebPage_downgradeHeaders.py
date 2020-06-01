"""
================================================================================
Downgrade headers in passed content by 1 or number of levels specified
================================================================================
"""
import re

REGEXP = re.compile('<h([1-6]).*>.*</h([1-6])>')

def pushDown(regexp_match):
  text = '%r' % regexp_match.group()
  start_level = regexp_match.group(1)
  stop_level = regexp_match.group(2)
  if (start_level == stop_level):
    next_level = "%i" % (int(start_level) + downgrade)
    text = '<h' + next_level + text[4:-3] + next_level + '>'
  return text

return REGEXP.sub(pushDown, content)
