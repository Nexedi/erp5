#!/usr/bin/python
# Copyright (c) 2005 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

"""
this patch is based on MailTemplates 1.1.0
it will only try to encode() text if it's of type unicode
"""

try:
  from Products.MailTemplates import BaseMailTemplate
except ImportError:
  BaseMailTemplate = None

from email.Header import make_header
from email.utils import make_msgid

if BaseMailTemplate is not None:
  def _process_utf8(self,kw):
      # sort out what encoding we're going to use
      encoding = kw.get('encoding',
                        self.getProperty('encoding',
                                         BaseMailTemplate.default_encoding))
      text = self.__class__.__bases__[1].__call__(self,**kw)
      # ZPT adds newline at the end, but it breaks backward compatibility.
      # So I remove it.
      if text and text[-1]=='\n':
        text = text[:-1]
      if not self.html() and isinstance(text, unicode):
          text = text.encode(encoding,'replace')
      # now turn the result into a MIMEText object
      msg = BaseMailTemplate.MIMEText(
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
              if isinstance(value, (tuple, list)):
                  value = ', '.join(value)
              # make sure we have no unicode headers
              if isinstance(value,unicode):
                  value = value.encode(encoding)
              if key=='subject':
                  value = make_header([(value, 'utf-8')]).encode()
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
      headers['Date']=BaseMailTemplate.DateTime().rfc822()
      # add message-id header
      headers['Message-ID']=make_msgid()
      # turn headers into an ordered list for predictable header order
      keys = headers.keys()
      keys.sort()
      return msg,values,[(key,headers[key]) for key in keys]

  BaseMailTemplate.BaseMailTemplate._process = _process_utf8

