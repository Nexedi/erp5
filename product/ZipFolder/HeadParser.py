##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################

#
# taken from utilities/load_site.py
#

import string
from sgmllib import SGMLParser


def join_attrs(attrs):
   attr_list = []
   for attrname, value in attrs:
      attr_list.append('%s="%s"' % (attrname, string.strip(value)))

   if attr_list:
      s = " " + string.join(attr_list, " ")
   else:
      s = ""

   return s

class HeadParser(SGMLParser):
   def __init__(self):
      SGMLParser.__init__(self)

      self.seen_starthead = 0
      self.seen_endhead   = 0
      self.seen_startbody = 0

      self.head = ""
      self.title = ""
      self.accumulator = ""


   def handle_data(self, data):
      if data:
         self.accumulator = self.accumulator + data

   def handle_comment(self, data):
      if data:
       self.handle_data("<!--%s-->" % data)

   def handle_charref(self, ref):
       self.handle_data("&#%s;" % ref)

   def handle_entityref(self, ref):
       self.handle_data("&%s;" % ref)

   def start_head(self, attrs):
      if not self.seen_starthead:
         self.seen_starthead = 1
         self.head = ""
         self.title = ""
         self.accumulator = ""

   def end_head(self):
      if not self.seen_endhead:
         self.seen_endhead = 1
         self.head = self.head + self.accumulator
         self.accumulator = ""


   def start_title(self, attrs):
      self.head = self.head + self.accumulator
      self.accumulator = ""

   def end_title(self):
      self.title = self.accumulator
      self.accumulator = ""


   def start_body(self, attrs):
      if not self.seen_startbody:
         self.seen_startbody = 1
         self.accumulator = ""

   def end_body(self): pass # Do not put </BODY> and </HTML>
   def end_html(self): pass # into output stream


   # Pass other tags unmodified
   def unknown_starttag(self, tag, attrs):
      self.accumulator = self.accumulator + "<%s%s>" % (string.upper(tag), join_attrs(attrs))

   def unknown_endtag(self, tag):
      self.accumulator = self.accumulator + "</%s>" % string.upper(tag)


   


