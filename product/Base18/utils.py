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

from cgi import escape
from types import StringType
import Globals, StructuredText, string, utils, re, os
from StructuredText.HTMLWithImages import HTMLWithImages
from Products.CMFDefault.utils import parseHeadersBody, formatRFC822Headers
from Products.CMFDefault.utils import SimpleHTMLParser, bodyfinder, _dtmldir
from Products.CMFCore.utils import _format_stx, keywordsplitter, \
                                   CMFHtmlWithImages, DocumentWithImages
from Globals import package_home

#
#   DTML Directory for ZMI
#

_dtmldir = os.path.join( package_home( globals() ), 'dtml' )



#
#   StructuredText handling
#   Translation
#

class Base18HtmlWithImages( HTMLWithImages ):
    """ Special subclass of HTMLWithImages, overriding document() """

    def dispatch(self, doc, level, output):
        getattr(self, self.element_types[doc.getNodeName()])(doc, level, output)

    def __call__(self, doc, md, lang, level=1, header=1):
        r = []
        self.md = md
        self.lang = lang
        self.header = header
        self.dispatch(doc, level-1, r.append)
        #return u''.join(r)
        result = ''
        # We must convert some parts from unicode to a suitable string format
        for i in r:
          if type(i) is StringType:
            result += i
          else:
            if lang == 'ja':
              result += i.encode('utf-8')
            else:
              result += i.encode('latin-1')
        return result
        #return ''.join(r)

    def appendTranslation(self, output, translatedOutput):
        md = self.md
        #uTranslatedOutput = u''
        #for i in translatedOutput:
        #  if type(i) is StringType:
        #    i = unicode(i, 'UTF-8')
        #  uTranslatedOutput += i
        #output(md.gettext(uTranslatedOutput,lang=self.lang))
        output(md.gettext(''.join(translatedOutput),lang=self.lang))

    def _text(self, doc, level, output):
        # Remove line breaks
        #output((' '.join(doc.getNodeValue().split('\n'))))
        output(doc.getNodeValue())

    def section(self, doc, level, output):
        children=doc.getChildNodes()
        for c in children:
            getattr(self, self.element_types[c.getNodeName()])(c, level+1,
                  output)

    def sectionTitle(self, doc, level, output):
        output('<h%d>' % (level))
        # Prepare translation
        translatedOutput=[]
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level,
                    translatedOutput.append)
        # Append translation
        self.appendTranslation(output, translatedOutput)
        output('</h%d>\n' % (level))

    def description(self, doc, level, output):
        p=doc.getPreviousSibling()
        if p is None or  p.getNodeName() is not doc.getNodeName():
            output('<dl>\n')
        # Prepare translation
        translatedOutput=[]
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level,
                    translatedOutput.append)
        # Append translation
        self.appendTranslation(output, translatedOutput)
        n=doc.getNextSibling()
        if n is None or n.getNodeName() is not doc.getNodeName():
            output('</dl>\n')

    def descriptionTitle(self, doc, level, output):
        output('<dt>')
        # Prepare translation
        translatedOutput=[]
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level,
                     translatedOutput.append)
        # Append translation
        self.appendTranslation(output, translatedOutput)
        output('</dt>\n')

    def descriptionBody(self, doc, level, output):
        output('<dd>')
        # Prepare translation
        translatedOutput=[]
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level,
                    translatedOutput.append)
        # Append translation
        self.appendTranslation(output, translatedOutput)
        output('</dd>\n')

    def bullet(self, doc, level, output):
        p=doc.getPreviousSibling()
        if p is None or p.getNodeName() is not doc.getNodeName():
            output('\n<ul>\n')
        output('<li>')
        # Prepare translation
        translatedOutput=[]
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level,
                    translatedOutput.append)
        # Append translation
        self.appendTranslation(output, translatedOutput)
        n=doc.getNextSibling()
        output('</li>\n')
        if n is None or n.getNodeName() is not doc.getNodeName():
            output('\n</ul>\n')

    def numbered(self, doc, level, output):
        p=doc.getPreviousSibling()
        if p is None or p.getNodeName() is not doc.getNodeName():
            output('\n<ol>\n')
        output('<li>')
        # Prepare translation
        translatedOutput=[]
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level,
                     translatedOutput.append)
        # Append translation
        self.appendTranslation(output, translatedOutput)
        n=doc.getNextSibling()
        output('</li>\n')
        if n is None or n.getNodeName() is not doc.getNodeName():
            output('\n</ol>\n')

    def example(self, doc, level, output):
        i=0
        for c in doc.getChildNodes():
            if i==0:
                output('\n<pre>\n')
                output(escape(c.getNodeValue()))
                output('\n</pre>\n')
            else:
                getattr(self, self.element_types[c.getNodeName()])(
                    c, level, output)

    def paragraph(self, doc, level, output):
        output('<p>')
        # Prepare translation
        translatedOutput=[]
        for c in doc.getChildNodes():
            if c.getNodeName() in ['StructuredTextParagraph']:
                getattr(self, self.element_types[c.getNodeName()])(
                    c, level, translatedOutput.append)
            else:
                getattr(self, self.element_types[c.getNodeName()])(
                    c, level, translatedOutput.append)
        # Append translation
        self.appendTranslation(output, translatedOutput)
        output('</p>\n')

    def link(self, doc, level, output):
        output('<a href="%s">' % doc.href)
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level, output)
        output('</a>')

    def emphasis(self, doc, level, output):
        output('<em>')
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level, output)
        output('</em>')

    def literal(self, doc, level, output):
        output('<code>')
        for c in doc.getChildNodes():
            output(escape(c.getNodeValue()))
        output('</code>')

    def strong(self, doc, level, output):
        output('<strong>')
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level, output)
        output('</strong>')

    def underline(self, doc, level, output):
        output("<u>")
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level, output)
        output("</u>")

    def innerLink(self, doc, level, output):
        output('<a href="#ref');
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level, output)
        output('">[')
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level, output)
        output(']</a>')
        
    def sgml(self,doc,level,output):
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level, output)

    def xref(self, doc, level, output):
        val = doc.getNodeValue()
        output('<a href="#ref%s">[%s]</a>' % (val, val) )
    
    def table(self,doc,level,output):
        """
        A StructuredTextTable holds StructuredTextRow(s) which
        holds StructuredTextColumn(s). A StructuredTextColumn
        is a type of StructuredTextParagraph and thus holds
        the actual data.
        """
        output('<table border="1" cellpadding="2">\n')
        for row in doc.getRows()[0]:
            output("<tr>\n")
            for column in row.getColumns()[0]:
                if hasattr(column,"getAlign"):
                    str = '<%s colspan="%s" align="%s" valign="%s">' % \
                        (column.getType(),  column.getSpan(), column.getAlign(),
                         column.getValign())
                else:
                    str = '<td colspan="%s">' % column.getSpan()
                output(str)
                for c in column.getChildNodes():
                    getattr(self, self.element_types[c.getNodeName()])(c, level,
                            output)
                if hasattr(column,"getType"):
                    output("</"+column.getType()+">\n")
                else:
                    output("</td>\n")
            output("</tr>\n")
        output("</table>\n")

    def namedLink(self, doc, level, output):
        """\
        XXX Trial subclassed implementation of HTMLClass#namedLink(),
        as default implementation seems to be broken...
        """
        name = doc.getNodeValue()
        if name[:2] == '..':
            name = name[2:]
        output('<a name="%s">[%s]</a>' % (name, name))

    def document(self, doc, level, output):
        """\
        HTMLWithImages.document renders full HTML (head, title, body).  For
        CMF Purposes, we don't want that.  We just want those nice juicy
        body parts perfectly rendered.
        """
        for c in doc.getChildNodes():
           getattr(self, self.element_types[c.getNodeName()])(c, level, output)


Base18HtmlWithImages = Base18HtmlWithImages()

# We need to add some conversion step to make sure
# pages are rendered properly
# This is taken from CMFWiki and is really uggly

intl_char_entities = (
    ('\300', '&Agrave;'),     #À#<--char
    ('\302', '&Acirc;'),      #Â#
    ('\311', '&Eacute;'),     #É#
    ('\312', '&Ecirc;'),      #Ê#
    ('\316', '&Icirc;'),      #Î#
    ('\324', '&Ocirc;'),      #Ô#
    ('\333', '&Ucirc;'),      #Û#
    ('\340', '&agrave;'),     #à#
    ('\342', '&acirc;'),      #â#
    ('\347', '&ccedil;'),     #ç#
    ('\350', '&egrave;'),     #è#
    ('\351', '&eacute;'),     #é#
    ('\352', '&ecirc;'),      #ê#
    ('\356', '&icirc;'),      #î#
    ('\364', '&ocirc;'),      #ô#
    ('\371', '&ugrave;'),     #ù#
    ('\373', '&ucirc;'),      #û#
)

def _translate_stx( text, md, level=1 , lang=None):
    """
        Render STX to HTML and Translate.
    """
    if callable(text): text = text()
    # We do not do conversions in order to preserver UTF text !
    # convert international characters to HTML entities for safekeeping
    # for c,e in intl_char_entities:
    #   text = re.sub(c, e, text)

    st = StructuredText.Basic( text )   # Creates the basic DOM
    if not st:                          # If it's an empty object
        return ""                       # return now or have errors!

    doc = DocumentWithImages( st )
    html = Base18HtmlWithImages( doc, md, lang, level )
    return html

def _translate_html( text, md, level=1 , lang=None):
    """
        Render HTML to HTML and Translate
        Must be updated later
    """
    if callable(text): text = text()
    st = StructuredText.Basic( text )   # Creates the basic DOM
    if not st:                          # If it's an empty object
        return ""                       # return now or have errors!

    doc = DocumentWithImages( st )
    html = Base18HtmlWithImages( doc, md, lang, level )
    return html

