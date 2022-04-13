##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
#                    Christophe Dumez <christophe@nexedi.com>
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

"""
 Provide a feature not present into difflib, which is generate a colored diff
 from a diff file/string.

 This code is original form ERP5VCS and was moved to here for be used in
 general ERP5.

 XXX The organisation of DiffUtils should be reviewed and reorganised in a tool
 if a general tool want to be provided.
"""
import os, re
from xml.sax.saxutils import escape

NBSP = '&nbsp;'
NBSP_TAB = NBSP*8
NO_DIFF_COLOR = 'white'
MODIFIED_DIFF_COLOR = 'rgb(253, 228, 6);'#light orange
DELETED_DIFF_COLOR = 'rgb(253, 117, 74);'#light red
ADDITION_DIFF_COLOR = 'rgb(83, 253, 74);'#light green

class DiffFile(object):
  """
  # Members :
   - path : path of the modified file
   - children : sub codes modified
   - old_revision
   - new_revision
  """

  def __init__(self, raw_diff):
    self.children = []
    self.binary = raw_diff and '@@' not in raw_diff
    if self.binary or not raw_diff:
      return
    self.header = raw_diff.split('@@')[0][:-1]
    # Getting file path in header
    self.path = self.header.split('====')[0][:-1].strip()
    # Getting revisions in header
    for line in self.header.splitlines():
      if line.startswith('--- '):
        tmp = re.search('\\([^)]+\\)$', line)
        if tmp is not None:
          self.old_revision = tmp.string[tmp.start():tmp.end()][1:-1].strip()
        else:
          self.old_revision = line.replace("--- ", "")
      if line.startswith('+++ '):
        tmp = re.search('\\([^)]+\\)$', line)
        if tmp is not None:
          self.new_revision = tmp.string[tmp.start():tmp.end()][1:-1].strip()
        else:
          self.new_revision = line.replace("+++ ", "")
    # Splitting the body from the header
    self.body = os.linesep.join(raw_diff.strip().splitlines()[3:])
    if not self.body.startswith('@@'):
      self.body = os.linesep.join(raw_diff.strip().splitlines()[4:])
    # Now splitting modifications
    first = True
    tmp = []
    for line in self.body.splitlines():
      if line:
        if line.startswith('@@') and not first:
          self.children.append(CodeBlock(os.linesep.join(tmp)))
          tmp = [line, ]
        else:
          first = False
          tmp.append(line)
    self.children.append(CodeBlock(os.linesep.join(tmp)))

  def __bool__(self):
    return self.binary or bool(self.children)
  __nonzero__ = __bool__ # six.PY2

  def __len__(self):
    return len(self.children)

  toHTML__roles__ = None # public
  def toHTML(self):
    """ return HTML diff
    """
    # Adding header of the table
    if self.binary:
      return '<b>Folder or binary file or just no changes!</b><br/><br/><br/>'

    if not self:
      return ''

    html_list = []
    html_list.append('''
    <table style="text-align: left; width: 100%%; border: 0;" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td style="background-color: grey; text-align: center; font-weight: bold;">%s</td>
      <td style="background-color: black; width: 2px;"></td>
      <td style="background-color: grey; text-align: center; font-weight: bold;">%s</td>
    </tr>''' % (self.old_revision, self.new_revision))
    header_color = 'grey'
    child_html_text = '''<tr><td style="background-color: %(headcolor)s">
    &nbsp;</td><td style="background-color: black; width: 2px;"></td>
    <td style="background-color: %(headcolor)s">&nbsp;</td></tr><tr>
    <td style="background-color: rgb(68, 132, 255);font-weight: bold;">Line %(oldline)s</td>
    <td style="background-color: black; width: 2px;"></td>
    <td style="background-color: rgb(68, 132, 255);font-weight: bold;">Line %(newline)s</td>
    </tr>'''
    for child in self.children:
      # Adding line number of the modification
      html_list.append( child_html_text % {'headcolor':header_color, 'oldline':child.old_line, 'newline':child.new_line} )
      header_color = 'white'
      # Adding diff of the modification
      old_code_list = child.getOldCodeList()
      new_code_list = child.getNewCodeList()
      i = 0
      for old_line_tuple in old_code_list:
        new_line_tuple = new_code_list[i]
        new_line = new_line_tuple[0] or ' '
        old_line = old_line_tuple[0] or ' '
        i += 1
        html_list.append( '''<tr style="font-family: monospace">
        <td style="background-color: %s">%s</td>
        <td style="background-color: black; width: 2px;"></td>
        <td style="background-color: %s">%s</td>
        </tr>'''%(old_line_tuple[1],
        escape(old_line).replace(' ', NBSP).replace('\t', NBSP_TAB),
        new_line_tuple[1],
        escape(new_line).replace(' ', NBSP).replace('\t', NBSP_TAB))
        )
    html_list.append('''</tbody></table><br/>''')
    return '\n'.join(html_list)

  def getModifiedBlockList(self):
    """
    Return a list of modified blocks
    List contains tuples (block object : (old_modified_code, new_modified_code))
    """
    if self.binary:
      return []
    block_list = []
    for child in self.children:
      old_line_list = [line.strip() for line, color in child.getOldCodeList()
                       if line is not None and color in (MODIFIED_DIFF_COLOR,
                                                         DELETED_DIFF_COLOR)]
      new_line_list = [line.strip() for line, color in child.getNewCodeList()
                       if line is not None and color in (MODIFIED_DIFF_COLOR,
                                                         ADDITION_DIFF_COLOR)]
      if old_line_list or new_line_list:
        block_list.append((child,(old_line_list, new_line_list)))
    return block_list


class CodeBlock:
  """
   A code block contains several SubCodeBlocks
   Members :
   - old_line : line in old code (before modif)
   - new line : line in new code (after modif)

   Methods :
   - getOldCodeList() : return code before modif
   - getNewCodeList() : return code after modif
   Note: the code returned is a list of tuples (code line, background color)
  """

  def __init__(self, raw_diff):
    # Splitting body and header
    self.body = os.linesep.join(raw_diff.splitlines()[1:])
    self.header = raw_diff.splitlines()[0]
    # Getting modifications lines
    tmp = re.search(r'^@@ -\d+', self.header)
    self.old_line = tmp.string[tmp.start():tmp.end()][4:]
    tmp = re.search(r'\+\d+', self.header)
    self.new_line = tmp.string[tmp.start():tmp.end()][1:]
    # Splitting modifications in SubCodeBlocks
    in_modif = False
    self.children = []
    tmp = []
    for line in self.body.splitlines():
      if line:
        if (line.startswith('+') or line.startswith('-')):
          if in_modif:
            tmp.append(line)
          else:
            self.children.append(SubCodeBlock(os.linesep.join(tmp)))
            tmp = [line, ]
            in_modif = True
        else:
          if in_modif:
            self.children.append(SubCodeBlock(os.linesep.join(tmp)))
            tmp = [line, ]
            in_modif = False
          else:
            tmp.append(line)
    self.children.append(SubCodeBlock(os.linesep.join(tmp)))

  def getOldCodeList(self):
    """ Return code before modification
    """
    tmp = []
    for child in self.children:
      tmp.extend(child.getOldCodeList())
    return tmp

  def getNewCodeList(self):
    """ Return code after modification
    """
    tmp = []
    for child in self.children:
      tmp.extend(child.getNewCodeList())
    return tmp

class SubCodeBlock:
  """ a SubCodeBlock contain 0 or 1 modification (not more)
  """
  def __init__(self, code):
    self.body = code
    self.modification = self._getModif()
    self.old_code_length = self._getOldCodeLength()
    self.new_code_length = self._getNewCodeLength()
    # Choosing background color
    if self.modification == 'none':
      self.color = NO_DIFF_COLOR
    elif self.modification == 'change':
      self.color = MODIFIED_DIFF_COLOR
    elif self.modification == 'deletion':
      self.color = DELETED_DIFF_COLOR
    else: # addition
      self.color = ADDITION_DIFF_COLOR

  def _getModif(self):
    """ Return type of modification :
        addition, deletion, none
    """
    nb_plus = 0
    nb_minus = 0
    for line in self.body.splitlines():
      if line.startswith("-"):
        nb_minus -= 1
      elif line.startswith("+"):
        nb_plus += 1
    if (nb_plus == 0 and nb_minus == 0):
      return 'none'
    if (nb_minus == 0):
      return 'addition'
    if (nb_plus == 0):
      return 'deletion'
    return 'change'

  def _getOldCodeLength(self):
    """ Private function to return old code length
    """
    nb_lines = 0
    for line in self.body.splitlines():
      if not line.startswith("+"):
        nb_lines += 1
    return nb_lines

  def _getNewCodeLength(self):
    """ Private function to return new code length
    """
    nb_lines = 0
    for line in self.body.splitlines():
      if not line.startswith("-"):
        nb_lines += 1
    return nb_lines

  def getOldCodeList(self):
    """ Return code before modification
    """
    if self.modification == 'none':
      old_code = [(x, 'white') for x in self.body.splitlines()]
    elif self.modification == 'change':
      old_code = [self._getOldCodeList(x) for x in self.body.splitlines() \
      if self._getOldCodeList(x)[0]]
      # we want old_code_list and new_code_list to have the same length
      if(self.old_code_length < self.new_code_length):
        filling = [(None, self.color)] * (self.new_code_length - \
        self.old_code_length)
        old_code.extend(filling)
    else: # deletion or addition
      old_code = [self._getOldCodeList(x) for x in self.body.splitlines()]
    return old_code

  def _getOldCodeList(self, line):
    """ Private function to return code before modification
    """
    if line.startswith('+'):
      return (None, self.color)
    if line.startswith('-'):
      return (' ' + line[1:], self.color)
    return (line, self.color)

  def getNewCodeList(self):
    """ Return code after modification
    """
    if self.modification == 'none':
      new_code = [(x, 'white') for x in self.body.splitlines()]
    elif self.modification == 'change':
      new_code = [self._getNewCodeList(x) for x in self.body.splitlines() \
      if self._getNewCodeList(x)[0]]
      # we want old_code_list and new_code_list to have the same length
      if(self.new_code_length < self.old_code_length):
        filling = [(None, self.color)] * (self.old_code_length - \
        self.new_code_length)
        new_code.extend(filling)
    else: # deletion or addition
      new_code = [self._getNewCodeList(x) for x in self.body.splitlines()]
    return new_code

  def _getNewCodeList(self, line):
    """ Private function to return code after modification
    """
    if line.startswith('-'):
      return (None, self.color)
    if line.startswith('+'):
      return (' ' + line[1:], self.color)
    return (line, self.color)

from AccessControl.SecurityInfo import ModuleSecurityInfo
ModuleSecurityInfo(__name__).declarePublic('DiffFile')
