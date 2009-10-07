# Copyright (c) 2005-2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from AccessControl import ClassSecurityInfo
from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from App.class_init import default__class_init__ as InitializeClass
try:
  from zope.app.content_types import guess_content_type
except ImportError:
  from OFS.content_types import guess_content_type # Zope 2.7
from OFS.Image import File
from ZPublisher.HTTPRequest import FileUpload

def cookId(filename):
    return filename[max(filename.rfind('/'),
                        filename.rfind('\\'),
                        filename.rfind(':'),
                        )+1:]
    
class MTMultipart(MIMEMultipart):

    security = ClassSecurityInfo()
    
    security.setDefaultAccess('allow')
    
    def __init__(self,mt,mfrom,mto,_subtype='mixed',boundary=None):
        MIMEMultipart.__init__(self,_subtype,boundary)
        self.mfrom = mfrom
        self.mto = mto
        self.mt = mt

    security.declarePublic('send')
    def send(self):
        "send ourselves using our MailTemplate's send method"
        return self.mt._send(self.mfrom,self.mto,self)

    security.declarePublic('add_file')
    def add_file(self,theFile=None,data=None,filename=None,content_type=None):
        "add a Zope file or Image to ourselves as an attachment"
        if theFile and data is not None:
            raise TypeError(
                'A file-like object was passed as well as data to create a file'
                )
        if (data is None) != (not filename):
            raise TypeError(
                'Both data and filename must be specified'
                )
        if data is not None:
            if content_type is None:
                content_type, enc=guess_content_type(filename, data)
        elif isinstance(theFile,File):
            filename = theFile.getId()
            data = str(theFile.data)
            content_type = content_type or theFile.content_type
        elif isinstance(theFile,file):
            filename = cookId(theFile.name)
            data = theFile.read()
            if content_type is None:
                content_type,enc = guess_content_type(filename, data)
        elif isinstance(theFile,FileUpload):
            filename = cookId(theFile.filename)
            data=theFile.read()
            headers=theFile.headers
            if content_type is None:
                if headers.has_key('content-type'):
                    content_type=headers['content-type']
                else:
                    content_type, enc=guess_content_type(filename, data)
        else:
            raise TypeError('Unknown object type found: %r' % theFile)
        
        msg = MIMEBase(*content_type.split('/'))
        msg.set_payload(data)
        Encoders.encode_base64(msg)
        msg.add_header('Content-ID', '<%s>' % \
            ''.join(['%s' % ord(i) for i in filename]))
        msg.add_header('Content-Disposition', 'attachment',
                       filename=filename)
        self.attach(msg)
        
InitializeClass(MTMultipart)
