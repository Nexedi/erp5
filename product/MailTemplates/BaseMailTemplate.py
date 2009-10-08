# Copyright (c) 2005-2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import os
import rfc822

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from App.class_init import default__class_init__ as InitializeClass
from App.Common import package_home
from MTMultipart import MTMultipart
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from ZPublisher import HTTPResponse

# Configured using zope.conf in Zope 2.7.8, Zope 2.8.2, and above
default_encoding = getattr(HTTPResponse,'default_encoding','iso-8859-15')

class BaseMailTemplate:

    security = ClassSecurityInfo()

    _properties = ()
    
    ZScriptHTML_tryForm = None

    content_type = 'text/plain'

    mailhost = None
    
    security.declarePrivate('_process')
    def _process(self,kw):
        # sort out what encoding we're going to use
        encoding = kw.get('encoding',
                          self.getProperty('encoding',
                                           default_encoding))
        text = self.__class__.__bases__[1].__call__(self,**kw)
        if not self.html():
            text = text.encode(encoding,'replace')
        # now turn the result into a MIMEText object
        msg = MIMEText(
            text.replace('\r',''),
            self.content_type.split('/')[1],
            encoding
            )
        # sort out what headers and addresses we're going to use
        headers = {}
        values = {}
        # headers from the headers property
        for header in getattr(self,'headers',()):
            name,value = header.split(':',1)
            headers[name]=value
        # headers from the headers parameter
        headers_param = kw.get('headers',{})
        headers.update(headers_param)
        # values and some specific headers
        for key,header in (('mfrom','From'),
                           ('mto','To'),
                           ('mcc','Cc'),
                           ('mbcc','Bcc'),
                           ('subject','Subject')):
            value = kw.get(key,
                           headers_param.get(header,
                                             getattr(self,
                                                     key,
                                                     headers.get(header))))
            if value is not None:
                values[key]=value
                # turn some sequences in coma-seperated strings
                if isinstance(value,tuple) or isinstance(value,list):
                    value = ', '.join(value)
                # make sure we have no unicode headers
                if isinstance(value,unicode):
                    value = value.encode(encoding)
                headers[header]=value
        # check required values have been supplied
        errors = []
        for param in ('mfrom','mto','subject'):
            if not values.get(param):
                errors.append(param)
        if errors:
            raise TypeError(
                'The following parameters were required by not specified: '+(
                ', '.join(errors)
                ))
        # add date header
        headers['Date']=DateTime().rfc822()
        # turn headers into an ordered list for predictable header order
        keys = headers.keys()
        keys.sort()
        return msg,values,[(key,headers[key]) for key in keys]
        
    security.declarePrivate('_send')
    def _send(self,mfrom,mto,msg):
            
        mailhost = self.restrictedTraverse(self.mailhost,None)
        if not getattr(mailhost,'meta_type',None) in (
            'Mail Host','Maildrop Host'
            ):
            raise RuntimeError(
                'Could not traverse to MailHost %r' % self.mailhost
                )
        
        mailhost._send(mfrom,mto,msg.as_string())

    security.declareProtected('View', 'send')
    def send(self,**kw):

        msg,values,headers = self._process(kw)

        for header,value in headers:
            msg[header]=value

        to_addrs = ()
        for key in ('mto', 'mcc', 'mbcc'):
            v = values.get(key)
            if v:
                if isinstance(v, basestring):
                    v = [rfc822.dump_address_pair(addr) for addr \
                            in rfc822.AddressList(v)]
                to_addrs += tuple(v)
        
        self._send(values['mfrom'], to_addrs, msg)

    security.declareProtected('View', '__call__')
    __call__ = send

    security.declareProtected('View', 'as_message')
    def as_message(self,**kw):
        msg,values,headers = self._process(kw)
        multipart_kw = {}
        #subtype = kw.get('subtype')
        #if subtype:
        #    multipart_kw['_subtype'] = subtype
        #boundary = kw.get('boundary')
        #if boundary:
        #    multipart_kw['boundary'] = boundary
            
        multipart = MTMultipart(self,
                                values['mfrom'],
                                values['mto'],
                                **multipart_kw)

        # set the encoding for the container
        #multipart.set_charset(msg.get_charset())
        
        for header,value in headers:
            multipart[header]=value
            
        multipart.attach(msg)

        return multipart
        
InitializeClass(BaseMailTemplate)

    
