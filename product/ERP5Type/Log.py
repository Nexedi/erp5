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

from zLOG import LOG, INFO
from traceback import extract_stack

def log(self, description, content = '', level = INFO):
    """Put a log message. This method is supposed to be used by
    restricted environment, such as Script (Python)."""
    if not content: # allow for content only while keeping interface
        description, content = content, description
    st = extract_stack()
    head = []
    for frame in st[-2:-6:-1]: # assume no deep nesting in Script (Python)
        if frame[3] is not None and frame[3].startswith('self.log'): # called from class
            head.append('%s, %d' % (frame[2], frame[1]))
            break
        if frame[0] == 'Script (Python)': # does anybody log from ZPT or dtml?
            head.append('%s, %d' % (frame[2], frame[1]))
    del st # Prevent cycling references.
    head = ' -> '.join(head)
    description = '%s: %s' % (head, description)
    LOG(description, level, content)

