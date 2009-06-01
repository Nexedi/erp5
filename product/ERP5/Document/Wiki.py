##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.Document import Document

from zLOG import LOG

import cgi
import re

class Wiki( Document ):
    """
       A simple Wiki document. A Wiki page may contain
       subobjects (File, Image, etc.) just like any text
       based Document.
    """

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Document
                      )

    # CMF Type Definition
    meta_type='ERP5 Wiki'
    portal_type='Wiki'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Compile regular expressions at load time.
    table_expr = re.compile(r"^\|\|(.+)\|\|$")
    heading_expr = re.compile(r"^(={1,5}) (.+) \1$")
    horizontal_line_expr = re.compile(r"^-{4,}$")
    enumerated_list_expr = re.compile(r"^(\s+)[0-9]+\.(.*)")
    item_list_expr = re.compile(r"^(\s+)\*(.*)")
    preformatted_text_expr = re.compile(r"^{{{$")
    empty_line_expr = re.compile(r"^\s*$")
    
    line_expr_map = { 
      'table' : table_expr,
      'heading' : heading_expr,
      'horizontal_line' : horizontal_line_expr,
      'enumerated_list' : enumerated_list_expr,
      'item_list' : item_list_expr,
      'preformatted_text' : preformatted_text_expr,
      'empty_line' : empty_line_expr,
    }
    
    wiki_name_expr = re.compile(r"!?([A-Z][a-z]+){2,}(/([A-Z][a-z]+){2,})*")
    underscore_expr = re.compile(r"__([^_]+)__")
    bold_expr = re.compile(r"'''([^']+)'''")
    italic_expr = re.compile(r"(?<!')''([^']+)''(?!')")
    strike_expr = re.compile(r"~~([^~]+)~~")
    url_expr = re.compile(r"(!?[a-z]+://[^ ]+)")
    link_expr = re.compile(r"(?<!\[)\[([^\] ]+) ([^\]]+)\](?!\])")
    tales_expr = re.compile(r"\[\[([^\]]+)\]\]")
    
    text_expr_map = {
      'wiki_name' : wiki_name_expr,
      'underscore': underscore_expr,
      'bold' : bold_expr,
      'italic' : italic_expr,
      'strike' : strike_expr,
      'url' : url_expr,
      'link' : link_expr,
      'tales' : tales_expr,
    }
    
    def _getTopLevelUrl(self):
      o = self.getParentValue()
      while o.meta_type == 'ERP5 Wiki':
        o = o.getParentValue()
      return o.absolute_url()
      
    def _render_text(self, text):
      """
        Render a piece of text.
      """      
      text_list = []
      append = text_list.append
      
      while text:
        min_start = len(text)
        match = None
        min_key = None
        for key, expr in self.text_expr_map.items():
          m = expr.search(text)
          if m is not None:
            start = m.start(0)
            if min_start > start:
              min_start = start
              min_key = key
              match = m
              
        if match is None:
          # Nothing special.
          append(cgi.escape(text))
          break
        else:
          if min_start > 0:
            append(text[:min_start])
            
          if min_key == 'wiki_name':
            name = match.string[match.start(0):match.end(0)]
            if name.startswith('!'):
              append(name[1:])
            else:
              # FIMXE: Create a new wiki instance if not present.
              append('<a href="%s/%s/view">%s</a>' % (self._getTopLevelUrl(), name, name))
          elif min_key == 'url':
            url = match.string[match.start(1):match.end(1)]
            if url.startswith('!'):
              append(url[1:])
            else:
              # XXX Language-specific evil hack.
              if url[-1] in r",.')]}":
                extra = url[-1]
                url = url[:-1]
              else:
                extra = None
              append('<a href="%s">%s</a>' % (url, cgi.escape(url)))
              if extra is not None:
                append(extra)
          elif min_key == 'tales':
            append(self._render_tales(match.string[match.start(1):match.end(1)]))
          elif min_key == 'link':
            link, label = match.groups()
            label = self._render_text(label)
            if self.wiki_name_expr.search(link):
              # FIXME: Create a new wiki instance if not present
              append('<a href="%s/%s/view">%s</a>' % (self._getTopLevelUrl(), link, label))
            else:
              append('<a href="%s">%s</a>' % (link, label))
          else:
            word = self._render_text(match.string[match.start(1):match.end(1)])
            if min_key == 'underscore':
              append('<u>%s</u>' % word)
            elif min_key == 'italic':
              append('<i>%s</i>' % word)
            elif min_key == 'bold':
              append('<b>%s</b>' % word)
            elif min_key == 'strike':
              append('<del>%s</del>' % word)
            
          text = text[match.end(0):]
          
      return ''.join(text_list)
      
    def _render_tales(self, expr):
      """
        Evaluate the expression.
        
        FIXME
      """
      return ''
      
    def _render_table_row(self, text):
      """
        Render a row of a table.
      """
      text_list = ['<tr>']
      append = text_list.append
      for cell in text.split('||'):
        append('<td>')
        append(self._render_text(cell))
        append('</td>')
      append('</tr>')
      return ''.join(text_list)
      
    security.declareProtected(Permissions.View, 'render')
    def render(self, content=None, format=None):
      """
        Render the contents and generate HTML.
        
        FIXME: Very dirty. Better to rewrite this with a state machine.
      """
      if content is None:
        content = self.getTextContent()
        if content is None:
          content = ''
          
      preformatted = False
      in_table = False
      in_paragraph = False
      list_stack = []
      line_list = []
      append = line_list.append
      
      for line in content.split('\n'): # Used to be \r\n
        if preformatted:
          if line == '}}}':
            preformatted = False
            append('</pre>')
          else:
            append(cgi.escape(line))
          continue
          
        if in_table:
          m = self.table_expr.search(line)
          if m is not None:
            append(self._render_table_row(m.string[m.start(1):m.end(1)]))
            continue
          else:
            append('</table>')
            
        if list_stack:
          for key, expr in (('enumerated_list', self.enumerated_list_expr), ('item_list', self.item_list_expr)):
            m = expr.search(line)
            if m is not None:
              break
          else:
            key = None

          if key is None:
            level = 0
          else:
            level = m.end(1) - m.start(1)
                    
          while list_stack and list_stack[-1][1] > level:
            prev_key, prev_level = list_stack.pop()
            if prev_key == 'enumerated_list':
              append('</ol>')
            else:
              append('</ul>')
              
          if list_stack and list_stack[-1][1] == level:
            if key == list_stack[-1][0]:
              append('<li>')
              append(self._render_text(m.string[m.start(2):m.end(2)]))
              continue
            else:
              prev_key, prev_level = list_stack.pop()
              if prev_key == 'enumerated_list':
                append('</ol>')
              else:
                append('</ul>')
                
          if key is not None:
            list_stack.append((key, level))
            if key == 'enumerated_list':
              append('<ol><li>')
              append(self._render_text(m.string[m.start(2):m.end(2)]))
            else:
              append('<ul><li>')
              append(self._render_text(m.string[m.start(2):m.end(2)]))
            continue
            
        for key, expr in self.line_expr_map.items():
          m = expr.search(line)
          if m is not None:
            break
        else:
          key = None
      
        if in_paragraph and key is not None:
          in_paragraph = False
          append('</p>')
            
        if key == 'preformatted_text':
          preformatted = True
          append('<pre>')
        elif key == 'horizontal_line':
          append('<hr>')
        elif key == 'table':
          in_table = True
          append('<table>')
          append(self._render_table_row(m.string[m.start(1):m.end(1)]))
        elif key == 'heading':
          level = m.end(1) - m.start(1)
          append('<h%d>' % level)
          append(self._render_text(m.string[m.start(2):m.end(2)]))
          append('</h%d>' % level)
        elif key == 'enumerated_list':
          list_stack.append((key, m.end(1) - m.start(1)))
          append('<ol><li>')
          append(self._render_text(m.string[m.start(2):m.end(2)]))
        elif key == 'item_list':
          list_stack.append((key, m.end(1) - m.start(1)))
          append('<ul><li>')
          append(self._render_text(m.string[m.start(2):m.end(2)]))
        elif key == 'empty_line':
          pass
        else:
          if not in_paragraph:
            in_paragraph = True
            append('<p>')
          append(self._render_text(line))
          
      while list_stack:
        key, level = list_stack.pop()
        if key == 'enumerated_list':
          append('</ol>')
        else:
          append('</ul>')
          
      if in_paragraph:
        append('</p>')
        
      if in_table: 
        append('</table>')
        
      if preformatted:
        append('</pre>')
        
      return '\n'.join(line_list)