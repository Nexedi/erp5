# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import os, re, sys

if sys.version_info[:3] < (2, 7, 9):
    # Speed up email parsing (see also http://bugs.python.org/issue1243730)
    from email import feedparser

    NLCRE_crack_split = feedparser.NLCRE_crack.split
    def push(self, data):
        """Push some new data into this object."""
        # <patch>
        if self._partial[-1:] == '\r':
            parts = NLCRE_crack_split('\r' + data)
            parts[0] = self._partial[:-1]
        else:
            parts = NLCRE_crack_split(data)
            parts[0] = self._partial + parts[0]
        # </patch>
        # The *ahem* interesting behaviour of re.split when supplied grouping
        # parentheses is that the last element of the resulting list is the
        # data after the final RE.  In the case of a NL/CR terminated string,
        # this is the empty string.
        self._partial = parts.pop()
        #GAN 29Mar09  bugs 1555570, 1721862  Confusion at 8K boundary ending with \r:
        # is there a \n to follow later?
        if not self._partial and parts and parts[-1].endswith('\r'):
            self._partial = parts.pop(-2)+parts.pop()
        # parts is a list of strings, alternating between the line contents
        # and the eol character(s).  Gather up a list of lines after
        # re-attaching the newlines.
        lines = []
        for i in range(len(parts) // 2):
            lines.append(parts[i*2] + parts[i*2+1])
        self.pushlines(lines)
    feedparser.BufferedSubFile.push = push

if 1:
    from email import parser
    from email.feedparser import FeedParser
    def parse(self, fp, headersonly=False):
        """Create a message structure from the data in a file.

        Reads all the data from the file and returns the root of the message
        structure.  Optional headersonly is a flag specifying whether to stop
        parsing after reading the headers or not.  The default is False,
        meaning it parses the entire contents of the file.
        """
        feedparser = FeedParser(self._class)
        if headersonly:
            feedparser._set_headersonly()
        while True:
            # <patch>
            data = fp.read(65536)
            # </patch>
            if not data:
                break
            feedparser.feed(data)
        return feedparser.close()
    parser.Parser.parse = parse


# Workaround bad use of getcwd() in docutils.
# Required by PortalTransforms.transforms.rest
from docutils import utils
utils.relative_path = lambda source, target: os.path.abspath(target)

def patch_linecache():
  import linecache
  from os.path import basename

  expr_search = re.compile('^Python expression "(.+)"$').search

  def get_globals(frame):
    """
    ipdb does not pass module_globals to getlines()...
    """
    m = frame.f_globals['__name__']
    # 'linecache' or 'IPython.utils.ulinecache' (may be renamed/moved in
    # IPython so just check the presence of 'linecache'...)
    if isinstance(m, str) and 'linecache' in m:
      frame = frame.f_back
      m = frame.f_globals['__name__']
    if m == 'IPython.utils.ulinecache':
      frame = frame.f_back
      m = frame.f_globals['__name__']
      # IPython.utils.ulinecache.getline (used in `list` pdb command) call IPython.utils.ulinecache.getlines
      # so we may have two frames in IPython.utils.ulinecache module
      if m == 'IPython.utils.ulinecache':
        frame = frame.f_back
        m = frame.f_globals['__name__']
    if m == 'IPython.core.debugger':
      co_name = frame.f_code.co_name
      if co_name == 'format_stack_entry':
        return frame.f_locals['frame'].f_globals
      elif co_name == 'print_list_lines':
        return frame.f_locals['self'].curframe.f_globals

  linecache_getlines = linecache.getlines
  def getlines(filename, module_globals=None):
    """
    Patch of linecache module (used in traceback, ipdb, and pdb modules) to
    display ZODB Components, Python Script source code and TALES Expressions
    properly without requiring to create a temporary file on the filesystem

    The filename is is always '<portal_components/*>' for ZODB Components,
    '(FILENAME)?Script \(Python\)' for Zope Python Scripts and 'Python
    Expression "CODE"' for TALES expressions.

    linecache.cache filled by linecache.updatecache() called by the original
    linecache.getlines() is bypassed for Python Script to avoid getting
    inconsistent source code. Having no cache could be an issue if performances
    would be required here but as linecache module is only called by traceback
    and pdb modules not used often, this should not be an issue.
    """
    if filename:
      if module_globals is None:
        module_globals = get_globals(sys._getframe(1))

      # Get source code of ZODB Components following PEP 302
      if (filename.startswith('<portal_components/') and
          module_globals is not None):
        data = None
        name = module_globals.get('__name__')
        get_source = getattr(module_globals.get('__loader__'),
                             'get_source', None)
        if name and get_source:
          try:
            data = get_source(name)
          except (ImportError, AttributeError):
            pass

        return data.splitlines(True) if data is not None else ()

      if basename(filename) == 'Script (Python)':
        try:
          script = module_globals['script']
          if script._p_jar.opened:
            return script.body().splitlines(True)
        except Exception:
          pass
        return ()
      x = expr_search(filename)
      if x:
        return x.groups()
    return linecache_getlines(filename, module_globals)

  linecache.getlines = getlines

patch_linecache()
