##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                   Lucas Carvalho <lucas@nexedi.com>
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

import unittest
from Products.ERP5Type.CSSPacker import compressCSS
from os.path import abspath, join, dirname

PREFIX = abspath(dirname(__file__))

class TestCSSPacker(unittest.TestCase):

  def test_compressCSS(self):
    script = open(join(PREFIX, 'input/input_erp5.css')).read()
    result = compressCSS(script)
    
    output = open(join(PREFIX, 'output/output_erp5.css')).read()
    self.assertEquals(result, output)

  def test_CSSStyleWithoutSemicolon(self):
    result = compressCSS('.something {color: #FFFFF}')
    self.assertEquals('.something{color:#FFFFF;}', result)

  def test_CSSStyleAndClassWithSpaces(self):
    css = '.something       {color: #FFFFFF; border: 0px;        }'
    result = compressCSS(css)
    self.assertEquals('.something{color:#FFFFFF;border:0px;}', result)

  def test_CSSClassWithSpecialCharacter(self):
    css = 'div#main_content input.button, input[type="submit"] { \
      /* XXX Is this case happend in current web implementation ? */ \
        background: #fff url(erp5-website-button.png) bottom repeat-x; \
        }'
    result = compressCSS(css)
    expected_result = 'div#main_content input.button, \
input[type="submit"]{background:#fff url(erp5-website-button.png) bottom \
repeat-x;}'
    self.assertEquals(result, expected_result)

if __name__ == '__main__':
  unittest.main()
