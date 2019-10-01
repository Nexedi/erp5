##############################################################################
#
# Copyright (c) 2016 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from HTMLParser import HTMLParser
class HtmlParseHelper(HTMLParser):
  """
  Listens to all the HTMLParser methods and push results in a list of tuple.
  Tuple contains every method arguments, for instance the `handle_starttag`
  method pushes `('starttag', tag, attrs)` to the tuple list.

  See https://docs.python.org/2/library/htmlparser.html
  """
  def __init__(self, *args, **kw):
    HTMLParser.__init__(self, *args, **kw)
    self.result = []
  def handle_starttag(self, tag, attrs):
    self.result.append(("starttag", tag, attrs))
  def handle_startendtag(self, tag, attrs):
    self.result.append(("startendtag", tag, attrs))
  def handle_endtag(self, tag):
    self.result.append(("endtag", tag))
  def handle_data(self, data):
    self.result.append(("data", data))
  def handle_entityref(self, name):
    self.result.append(("entityref", name))
  def handle_charref(self, name):
    self.result.append(("charref", name))
  def handle_comment(self, data):
    self.result.append(("comment", data))
  def handle_decl(self, decl):
    self.result.append(("decl", decl))
  def handle_pi(self, data):
    self.result.append(("pi", data))
  def unknown_decl(self, data):
    self.result.append(("unknown_decl", data))

def parseHtml(text):
  """
  Parses a string and returns html parts as tuple list.

  Example:
  input: 'Click <a href="destination">here</a> to see the documentation.'
  return: [
    ('data', 'Click '),
    ('starttag', 'a', ('href', 'destination')),
    ('data', 'here'),
    ('endtag', 'a'),
    ('data', ' to see the documentation'),
  ]
  """
  hr = HtmlParseHelper()
  hr.feed(text)
  hr.close()
  return hr.result

import re
def partition(text, separatorRegexp):
  """
  partition("abcba", re.compile("(b)")) -> [
    ("a",),
    ("b", "b"),
    ("c",),
    ("b", "b"),
    ("a",),
  ]
  """
  result = []
  lastIndex = 0
  for match in separatorRegexp.finditer(text):
    result.append((text[lastIndex:match.start()],))
    result.append((match.group(0),) + match.groups())
    lastIndex = match.end()
  result.append((text[lastIndex:],))
  return result

css_comment_filter_re = re.compile(r"/\*((?:[^\*]|\*[^/])*)\*/")
css_url_re = re.compile(r"""(url\()(\s*(")([^"]*)"\s*|\s*(')([^']*)'\s*|([^\)]*))\)""")
def parseCssForUrl(text):
  """
  return tuple list like: [
    ("data", ""),
    ("comment", "/* set body background image */", " set body background image "),
    ("data", "\nbody {\n  background-image: url("),
    ("url", "  'http://ima.ge/bg.png' ", "http://ima.ge/bg.png", "'"),
    ("data", ");\n}\n"),
  ]
  """
  result = []
  parts = partition(text, css_comment_filter_re)  # filter comments
  i = 0
  for part in parts:
    i += 1
    if i % 2 == 0:  # comment
      result.append(("comment", part[0], part[1]))
    else:  # non comment
      parts = partition(part[0], css_url_re)
      data = ""
      j = 0
      for part in parts:
        j += 1
        if j % 2 == 1:  # css data
          data += part[0]
        else:  # url
          result.append(("data", data + part[1]))
          result.append(("url", part[2], (part[4] or part[6] or part[7] or "").strip(), part[3] or part[5] or ""))
          data = ")"
      result.append(("data", data))
  return result

def unescape(self, html):
  return HTMLParser().unescape(html)
