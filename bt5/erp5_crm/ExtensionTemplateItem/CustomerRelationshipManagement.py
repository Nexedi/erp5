##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Yusei TAHARA <yusei@nexedi.com>
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
"""External method for erp5_crm"""
import email
from cStringIO import StringIO


class MessageData:

  def __init__(self, data):
    self.message = email.message_from_string(data)

  def getHeader(self, name):
    return self.message.get(name)

  def replaceHeader(self, name, value):
    self.message.replace_header(name, value)

  def getBodyMessage(self):
    text_message = None
    html_message = None
    for part in self.message.walk():
      if part.get_content_type() == 'text/plain' and not text_message and not part.is_multipart():
        text_message = part
      elif part.get_content_type() == 'text/html' and not html_message and not part.is_multipart():
        return part
    return text_message

  def getTextContent(self):
    message = self.getBodyMessage()
    if message is not None:
      return message.get_payload(decode=1)

  def setTextContent(self, value):
    message = self.getBodyMessage()
    if message is not None:
      message.set_payload(value)

  def getValue(self, name):
    if name=='body':
      return self.getTextContent()
    else:
      return self.getHeader(name)

  def replaceValue(self, name, value):
    if name=='body':
      self.setTextContent(value)
    else:
      self.replaceHeader(name, value)

  def __str__(self):
    return self.message.as_string()


def Base_rewriteMessageFileForCRMIngestion(context, ingestion_file):
  ingestion_file.seek(0)
  data = ingestion_file.read()
  message = MessageData(data)
  Base_findPortalTypeNameAndMatchedValueForEvent = context.Base_findPortalTypeNameAndMatchedValueForEvent

  for name in ('subject', 'body'):
    value = message.getValue(name)
    portal_type, matched_value = Base_findPortalTypeNameAndMatchedValueForEvent(value)
    if portal_type is not None:
      new_value = value[len(matched_value)+1:]
      message.replaceValue(name, new_value)
      ingestion_file.seek(0)
      ingestion_file.truncate(0)
      ingestion_file.write(str(message))
      ingestion_file.seek(0)
      return ingestion_file
