##############################################################################
#
# Copyright (c) 2003 Coramy SAS and Contributors. All Rights Reserved.
#                    Romain Courteaud <Romain_Courteaud@coramy.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
#
# This program as such is not intended to be used by end users. End
# users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the Zope Public License (ZPL) Version 2.0
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

#http://www.zopera.org/Members/grival/mailavecpiecejointe/view
# http://www.pythonapocrypha.com/Chapter17/Chapter17.shtml

import StringIO
import MimeWriter
import base64
import multifile
import mimetools
import mimetypes

def sendMail(self, mMsg, mTo, mFrom, mSubj, attachmentList=None ):
  
  # get the mailhost object
  try:
    mailhost=getattr(self, self.portal_url.superValues('Mail Host')[0].id)
  except:
    raise AttributeError, "Cannot find a Mail Host object"
  else:

    # XXX can t see the message with sylpheed ...
    # no attachment means no mime message
    #if attachmentList==None:
    #  mailhost.send(mMsg,mTo,mFrom,mSubj)

    # construct the mime message
    #else:
    if 1==1:
      # Create multi-part MIME message.
      message = StringIO.StringIO()
      writer = MimeWriter.MimeWriter(message)

      writer.addheader('From', mFrom)
      writer.addheader('To', mTo)
      writer.addheader('Subject', mSubj)
      writer.addheader('MimeVersion', '1.0')
      # Don't forget to flush the headers for Communicator
      writer.flushheaders()
      # Generate a unique section boundary:
      outer_boundary=mimetools.choose_boundary()

      # Start the main message body. Write a brief message
      # for non-MIME-capable readers:
      dummy_file=writer.startmultipartbody("mixed",outer_boundary)
      dummy_file.write("If you can read this, your mailreader\n")
      dummy_file.write("can not handle multi-part messages!\n")
      #dummy_file.write("This is a multi-part message in MIME format.\n")
    
      submsg = writer.nextpart()
      submsg.addheader("Content-Transfer-Encoding", "7bit")
      FirstPartFile=submsg.startbody("text/plain", [("charset","US-ASCII")])
      FirstPartFile.write(mMsg)



      if attachmentList!=None:
      # attachment: { 'name': ,  'content': ,  'mime_type': }
        for attachment in attachmentList:

          if attachment.has_key('name'):
            attachment_name = attachment['name']
          else:
            attachment_name = ''

          # try to guess the mime type
          if not attachment.has_key('mime_type'):
            type, encoding = mimetypes.guess_type( attachment_name )

            if type != None:
              attachment['mime_type'] = type
            else:
              attachment['mime_type'] = 'application/octet-stream'   

          
          
        
          # attach it
          submsg = writer.nextpart()
       
          if attachment['mime_type'] == 'text/plain':
            attachment_file = StringIO.StringIO( attachment['content'] )
          
            submsg.addheader("Content-Transfer-Encoding", "7bit")
            submsg.addheader("Content-Disposition", "attachment;\nfilename="+attachment_name)
            submsg.flushheaders()

            f = submsg.startbody(attachment['mime_type'] , [("name", attachment_name)])
            f.write(attachment_file.getvalue())

          else:
            #  encode non-plaintext attachment in base64
            attachment_file = StringIO.StringIO( attachment['content'] )
            submsg.addheader("Content-Transfer-Encoding", "base64")
            submsg.flushheaders()
        
            f = submsg.startbody(attachment['mime_type'] , [("name", attachment_name)])
            base64.encode(attachment_file, f)

      # close the writer
      writer.lastpart()
    
      # send mail to user
      mailhost.send(message.getvalue(),mTo,mFrom)

      return None








