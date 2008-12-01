##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                     Lucas Carvalho <lucas@nexedi.com>
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
from Products.ERP5Type.JSPacker import compressJavaScript
from os.path import abspath, join, dirname

PREFIX = abspath(dirname(__file__))

class TestJSPacker(unittest.TestCase):

  def test_compressJavaScript(self):
    script = open(join(PREFIX, 'input/input_erp5.js')).read()
    result = compressJavaScript(script)
    
    output = open(join(PREFIX, 'output/output_erp5.js')).read()
    self.assertEquals(result, output)

  def test_JavaScriptHandleMultLineComment(self):
    script = '/*** ' \
             'MochiKit.MochiKit 1.4 : PACKED VERSION ' \
             'All rights Reserved. ***/' \
             'if(typeof (dojo)!=\"undefined\"){' \
             '  dojo.provide(\"MochiKit.Base\");' \
             '}'
    result = compressJavaScript(script)
    expected_result = 'eval(function(p,a,c,k,e,d){e=function(c){'\
                      'return(c<a?"":e(parseInt(c/a)))+((c=c%a)>35?'\
                      'String.fromCharCode(c+29):c.toString(36))};'\
                      'if(!\'\'.replace(/^/,String)){while(c--)d'\
                      '[c.toString(a)]=k[c]||c.toString(a);k='\
                      '[function(e){return d[e]}];e=function(){'\
                      'return\'\\\\w+\'};c=1};while(c--)if(k[c])p='\
                      'p.replace(new RegExp("\\\\b"+e(c)+"\\\\b","g"),k[c]);'\
                      'return p}(\'/*** 0.0 1.4 : d c b a 9. ***/8(7 '\
                      '(2)!="6"){  2.5("0.3");}\\n\',14,14,\'MochiKit||dojo|'\
                      'Base||provide|undefined|typeof|if|Reserved|rights|'\
                      'All|VERSION|PACKED\'.split(\'|\'),0,{}))\n'
    self.assertEquals(result, expected_result)

if __name__ == '__main__':
  unittest.main()
