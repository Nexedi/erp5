##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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

# pylint: disable=unused-import
from zLOG import (
  LOG,
  INFO,
  TRACE,
  DEBUG,
  BLATHER,
  PROBLEM,
  WARNING,
  ERROR,
  PANIC,
)

from traceback import extract_stack

marker_ = object()
def log(description, content=marker_, level=INFO):
  """Put a log message

  This method is supposed to be used by restricted environment,
  such as Script (Python).

  WARNING: When called with more than 1 argument, the first one is appended
           to the usual information about the caller, in order to form a
           subsystem string. Because a logging.Logger object is created for
           each subsystem, and is never freed, you can experience memory
           leaks if description is not constant.
  """
  if content is marker_: # allow for content only while keeping interface
    description, content = content, description
  st = extract_stack()
  head = []
  for frame in st[-2:-6:-1]: # assume no deep nesting in Script (Python)
    if frame[3] is not None and frame[3].startswith('self.log'): # called from class
      head.append('%s, %d' % (frame[2], frame[1]))
      break
    if frame[0] == 'Script (Python)': # does anybody log from ZPT or dtml?
      head.append('%s, %d' % (frame[2], frame[1]))
    elif frame[0] == 'ERP5 Python Script':
      head.append('%s, %d' % (frame[2], frame[1]))
  del st # Prevent cycling references.
  head = ' -> '.join(head)
  description = '%s: %s' % (head, description)
  LOG(description, level, content)

from AccessControl.SecurityInfo import allow_module
allow_module(__name__)