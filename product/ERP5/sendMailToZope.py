#!/usr/bin/python
##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets <jp@nexedi.com>
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

import sys
import urllib

# Configurable parameters
USER = ''
PASSWORD = ''
CONTRIBUTION_TOOL_URL = 'http://%s:%s@localhost:9080/erp5/portal_contributions/newContent' % (USER, PASSWORD)
PORTAL_TYPE = 'Mail Message'
FILE_NAME = 'postfix_mail.eml'
CONTAINER_PATH = 'event_module'

# Main program
if __name__ == '__main__':
  f = sys.stdin
  message_text = f.read()
  try:
    result = urllib.urlopen(CONTRIBUTION_TOOL_URL, urllib.urlencode(
      {'data': message_text,
       'portal_type': PORTAL_TYPE,
       'container_path': CONTAINER_PATH,
       'file_name': FILE_NAME,
      }
      )).read()
  except (IOError,EOFError), e:
    print "Zope Email Ingestion Error: Problem Connecting to server", e
    sys.exit(73)

  if result:
    print result
    sys.exit(1)

  sys.exit(0)