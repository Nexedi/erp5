# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2018 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from Products.ERP5Type.Utils import guessEncodingFromText # TODO: guessEncodingFromBytes
from zLOG import LOG, INFO

from email.header import decode_header, HeaderParseError

import re
import six

filename_regexp = 'name="([^"]*)"'

def testCharsetAndConvert(text_content, content_type, encoding):
  if not isinstance(text_content, six.text_type):
    try:
      if encoding is not None:
        text_content = text_content.decode(encoding)
      else:
        text_content = text_content.decode()
      if six.PY2:
        text_content = text_content.encode('utf-8')
    except (UnicodeDecodeError, LookupError):
      encoding = guessEncodingFromText(text_content, content_type)
      if encoding is not None:
        try:
          text_content = text_content.decode(encoding)
        except (UnicodeDecodeError, LookupError):
          # TODO: errors= repr ?
          text_content = repr(text_content)[1:-1]
      else:
        text_content = repr(text_content)[1:-1]
  return text_content, encoding


class MailMessageMixin:
  """
  Contains methods to read email's content or metadata for the data property
  of the self object.
  Sub-classes should implement a self._getMessage function returning a python
  instance of email.message.Message.
  The methods of this Mixin were originally in the Product.ERP5.Document.EmailDocument
  class, but have been moved in a mixin to be shared with InternetMessagePost.
  """

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _getMessage(self):
    """
    Method to overwrite in children classes, as it is the base of all
    other methods of the mixin.
    It should return an instance of email.message.Message
    """
    raise NotImplementedError

  def _getMessageTextPart(self):
    """
    Return the main text part of the message data

    Based on rfc: http://tools.ietf.org/html/rfc2046#section-5.1.4)
    """
    part_list = [self._getMessage()]
    found_part_list = []
    preferred_content_type = self.getPortalObject().portal_preferences.getPreferredTextFormat('text/html')
    while part_list:
      part = part_list.pop(0)
      if part.is_multipart():
        if part.get_content_subtype() in ('alternative', 'mixed', 'related'):
          # Try to get the favourite text format defined on preference
          for subpart in part.get_payload():
            if subpart.get_content_maintype() == 'text' and not subpart.get_filename():
              if subpart.get_content_type() == preferred_content_type:
                found_part_list.insert(0, subpart)
                break
              elif not found_part_list:
                found_part_list.append(subpart)
            else:
              part_list.extend(part.get_payload())
      elif part.get_content_maintype() == 'text':
        found_part_list.append(part)
    if found_part_list:
      return found_part_list[0]

  security.declareProtected(Permissions.AccessContentsInformation, 'getContentInformation')
  def getContentInformation(self):
    """
    Returns the content information from the header information.
    This is used by the metadata discovery system.
    """
    result = {}
    for (name, value) in self._getMessage().items():
      try:
        decoded_header_parts = decode_header(value)
      except HeaderParseError as error_message:
        decoded_header_parts = ()
        LOG('MailMessageMixin.getContentInformation', INFO,
            'Failed to decode %s header of %s with error: %s' %
            (name, self.getPath(), error_message))
      header_parts = []
      for text, encoding in decoded_header_parts:
        text, _ = testCharsetAndConvert(text, 'text/plain', encoding)
        header_parts.append(text)
      if six.PY3:
        result[name] = ''.join(header_parts)
      else:
        # https://bugs.python.org/issue1079
        result[name] = ' '.join(header_parts)
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'getAttachmentInformationList')
  def getAttachmentInformationList(self, **kw):
    """
    Returns a list of dictionnaries for every attachment. Each dictionnary
    represents the metadata of the attachment.
    **kw - support for listbox (TODO: improve it)
    """
    result = []
    for i, part in enumerate(self._getMessage().walk()):
      if not part.is_multipart():
        kw = dict(part.items())
        kw['uid'] = 'part_%s' % i
        kw['index'] = i
        filename = part.get_filename()
        if not filename:
          # get_filename return name only from Content-Disposition header
          # of the message but sometimes this value is stored in
          # Content-Type header
          content_type_header = kw.get('Content-Type',
                                       kw.get('Content-type', ''))
          filename_list = re.findall(filename_regexp,
                                     content_type_header,
                                     re.MULTILINE)
          if filename_list:
            filename = filename_list[0]
        if filename:
          kw['filename'] = filename
        else:
          content_disposition = kw.get('Content-Disposition',
                                       kw.get('Content-disposition', None))
          prefix = 'part_'
          if content_disposition:
            if content_disposition.split(';')[0] == 'attachment':
              prefix = 'attachment_'
            elif content_disposition.split(';')[0] == 'inline':
              prefix = 'inline_'
          kw['filename'] = '%s%s' % (prefix, i)
        kw['content_type'] = part.get_content_type()
        result.append(kw)
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'getAttachmentData')
  def getAttachmentData(self, index, REQUEST=None):
    """
    Returns the decoded data of an attachment.
    """
    for i, part in enumerate(self._getMessage().walk()):
      if index == i:
        # This part should be handled in skin script
        # but it was a bit easier to access items here
        kw = dict(part.items())
        content_type = part.get_content_type()
        if REQUEST is not None:
          filename = part.get_filename()
          if not filename:
            # get_filename return name only from Content-Disposition header
            # of the message but sometimes this value is stored in
            # Content-Type header
            content_type_header = kw.get('Content-Type',
                                         kw.get('Content-type', ''))
            filename_list = re.findall(filename_regexp,
                                       content_type_header,
                                       re.MULTILINE)
            if filename_list:
              filename = filename_list[0]
          RESPONSE = REQUEST.RESPONSE
          RESPONSE.setHeader('Accept-Ranges', 'bytes')
          if content_type and filename:
            RESPONSE.setHeader('Content-Type', content_type)
            RESPONSE.setHeader('Content-disposition',
                               'attachment; filename="%s"' % filename)
        if 'text/html' in content_type:
          part_encoding = part.get_content_charset()
          message_text = part.get_payload(decode=1)
          text_result, _ = testCharsetAndConvert(message_text,
                                                 content_type,
                                                 part_encoding)
          # Strip out html content in safe mode.
          _, content = self.convert(format='html',
                                    text_content=text_result,
                                       encoding=part_encoding,
                                       index=index) # add index to generate
                                       # a unique cache key per attachment
          if six.PY3:
            content = content.encode()
        else:
          content = part.get_payload(decode=1)
        return content
    return KeyError, "No attachment with index %s" % index

  # Helper methods which override header property sheet
  security.declareProtected(Permissions.AccessContentsInformation, 'getSender')
  def getSender(self, *args):
    """
    """
    if not self.hasData():
      return self._baseGetSender(*args)
    return self.getContentInformation().get('From', *args)

  security.declareProtected(Permissions.AccessContentsInformation, 'getRecipient')
  def getRecipient(self, *args):
    """
    """
    if not self.hasData():
      return self._baseGetRecipient(*args)
    return self.getContentInformation().get('To', *args)

  security.declareProtected(Permissions.AccessContentsInformation, 'getCcRecipient')
  def getCcRecipient(self, *args):
    """
    """
    if not self.hasData():
      return self._baseGetCcRecipient(*args)
    return self.getContentInformation().get('Cc', *args)

  security.declareProtected(Permissions.AccessContentsInformation, 'getGroupingReference')
  def getGroupingReference(self, *args):
    """
      The reference refers here to the Thread of messages.
    """
    if not self.hasData():
      result = self._baseGetGroupingReference(*args)
    else:
      if not len(args):
        args = (self._baseGetGroupingReference(),)
      result = self.getContentInformation().get('References', *args)
      if result:
        result = result.split()  # Only take the first reference
        if result:
          result = result[0]
    if result:
      return result
    return self.getFilename(*args)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSourceReference')
  def getSourceReference(self, *args):
    """
      The Message-ID is considered here as the source reference
      of the message on the sender side (source)
    """
    if not self.hasData():
      return self._baseGetSourceReference(*args)
    if not len(args):
      args = (self._baseGetSourceReference(),)
    content_information = self.getContentInformation()
    return content_information.get('Message-ID') or content_information.get('Message-Id', *args)

  security.declareProtected(Permissions.AccessContentsInformation, 'getDestinationReference')
  def getDestinationReference(self, *args):
    """
      The In-Reply-To is considered here as the reference
      of the thread on the side of a former sender (destination)

      This is a hack which can be acceptable since
      the reference of an email is shared.
    """
    if not self.hasData():
      return self._baseGetDestinationReference(*args)
    if not len(args):
      args = (self._baseGetDestinationReference(),)
    return self.getContentInformation().get('In-Reply-To', *args)


InitializeClass(MailMessageMixin)
