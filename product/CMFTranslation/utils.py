##############################################################################
#
# Base18: a Zope product which provides multilingual services for CMF Default
#         documents.
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
__version__ = "$Revision$"[11:-2]
__doc__ = "This product provides the basic behaviour to CMF object which need\
 translation"

"""
    Utility functions for translation
"""

import os
from Products.CMFDefault.utils import _dtmldir, StrippingParser
from Globals import package_home
from zLOG import LOG

#
#   DTML Directory for ZMI
#

_dtmldir = os.path.join( package_home( globals() ), 'dtml' )


##############################################################################
#
#  Text Translation
#
##############################################################################
           
def indent(txt, level):
    indented_text = []
    for l in txt.split('\n'):
      indented_text.append(level * ' ' + l)
    return indented_text.join('\n') 

def unIndent(txt):
    """
        Counts the number of trailing white spaces
    """
    indent = 0    
    for l in txt.split('\n'):
      wc = len(l) - len(l.strip())
      indent = min (wc, indent)
    stripped_text = []
    for l in txt.split('\n'):
      stripped_text.append(l[indent:])
    return indent, stripped_text.join('\n') 

def _translate_txt( text, md, lang=None):
    """
        Render TXT to HTML and Translate.
    """
    translated_text = []
    text_blocks = text.split('\n\n')
    for block in text_blocks:
      indent, stripped_text = unIndent(block)
      translated_stripped_text = md.gettext(stripped_text, lang=lang)
      translated_text.append(indent(translated_stripped_text, indent))
    return translated_text.join('\n')

##############################################################################
#
#  Structured Text Translation
#
##############################################################################
           
_translate_stx = _translate_txt
    
##############################################################################
#
#  HTML Translation
#
##############################################################################
           
class TranslatingParser(StrippingParser):
    
    def handle_data( self, data ):

        if data:
            # encoding should be improved
            #if type(self.result) != type(u'a'): self.result = unicode(self.result, 'iso-8859-15')            
            #LOG('result', 0, self.result)
            translated_text = self.md.gettext(data, lang=self.lang)
            #LOG('translated_text', 0, translated_text)
            if type(translated_text) is type(u'a'):
              #LOG('data', 0, translated_text.encode('iso-8859-15'))
              translated_text = translated_text.encode('iso-8859-15')              
            self.result = self.result + translated_text
            
                
    
def _translate_html( text, md, level=1 , lang=None):
    """
        Render HTML to HTML and Translate
        Must be updated later
    """
    if callable(text): text = text()
    parser = TranslatingParser()
    parser.md = md
    parser.lang = lang
    parser.feed( text )
    parser.close()
    return parser.result
    
    
    st = StructuredText.Basic( text )   # Creates the basic DOM
    if not st:                          # If it's an empty object
        return ""                       # return now or have errors!

    doc = DocumentWithImages( st )
    html = Base18HtmlWithImages( doc, md, lang, level )
    return html


    