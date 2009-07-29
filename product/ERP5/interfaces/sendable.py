# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from zope.interface import Interface

class ISendable(Interface):
  """
    Common Interface for all documents which can be sent.
    The notion of sending a document is independent of the 
    kind of transport. A document can be sent by email, 
    by fax, by chat, by printing it out, etc. The recipients are
    defined by the 'send' method, which can usually be overloaded
    through type based methods in order to implement all
    kinds of policies (ex. cc any sent invoice to a given 
    mailing list, selected based on some predicate information
    stored on email addresses of the Person or Organisation).

    Sent messages all use a common format: MIMEMultipart. Tools
    are invoked to send content. Tools must thus support MIMEMultipart
    and implement the IMIMESender interface.

    Sent messages can be recorded in the form of Event instances.
  """

  def send(from_url=None, to_url=None, cc_url=None, bcc_url=None,
           reply_url=None, subject=None, body=None, body_encoding=None,
           attachment_format=None, attachment_list=None, mime_sender=None,
           download=False, **kw):
    """
      High-level interface. The purpose of this method is to implement
      the sending logic ie. select recipients, select the tool to send
      the message, etc. Content of the message can either derive from
      document properties or can be provided through the 'body' a parameter.
      This method is not supposed to generate the actual message envelope.
      This is the role of asMIMEMultipart (bellow).

      from_url -- the sender of this email. If not provided
                  we will use source to find a valid
                  email address

      to_url   -- the recipients of this email. If not provided
                 we will use destination category to 
                 find a list of valid email addresses

      cc_url   -- the Cc recipients of this email (optional)

      bcc_url  -- the Bcc recipients of this email (optional)

      reply_url -- the email address to reply to. If nothing
                   is provided, use the email defined in 
                   preferences. (XXX)

      subject  -- a custom title. If not provided, we will use
                  getTitle XXX (getTranslatedTitle)

      body     -- a body message. If not provided, we will
                  use the text representation of the event
                  as body (UTF-8)

      body_encoding   -- the text encoding for the message body. 
                         this is required to send emails in countries
                         such as Japan where UTF-8 is not favoured

      attachment_list -- list of dictionary which contains raw data and
                         name and mimetype for attachment.
                         See NotificationTool.buildEmailMessage.

      attachment_format -- defines an option format
                 to convert attachments to (ex. application/pdf)

      download -- if set to True returns, the message online
                 rather than sending it.

      language -- selects the language to use for message generation
                  (ex. printout language, mail template language, content, etc.)
                   etc

      mime_sender -- the sender tool to use to send the message (optional)

      **kw -- optional parameters
    """
    pass

  def asMIMEMultipart(from_url, to_url,
                      cc_url=None, bcc_url=None,
                      reply_url=None, subject=None,
                      body=None, body_encoding=None, 
                      attachment_list=None,
                      attachment_format=None,
                      extra_header_dict=None, 
                      additional_header_dict=None,
                      **kw):
    """
      Low-level interface. Build a MIMEMultipart instance based on 
      the parameters and on the document content. Recipients
      must be provided explicitely. Actual MIMEMultipart generation
      uses mailtemplates.
    """
    pass

  def getMIMEMultipartLogList(mime_sender=None):
    """
      Retrieve the list of messages sent based on the current document
    """
    pass
