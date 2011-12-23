<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="DTMLDocument" module="OFS.DTMLDocument"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>erp5_run_my_docs.js</string> </value>
        </item>
        <item>
            <key> <string>_vars</string> </key>
            <value>
              <dictionary/>
            </value>
        </item>
        <item>
            <key> <string>globals</string> </key>
            <value>
              <dictionary/>
            </value>
        </item>
        <item>
            <key> <string>raw</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.\n
\n
This program is Free Software; you can redistribute it and/or\n
modify it under the terms of the GNU General Public License\n
as published by the Free Software Foundation; either version 2\n
of the License, or (at your option) any later version.\n
\n
This program is distributed in the hope that it will be useful,\n
but WITHOUT ANY WARRANTY; without even the implied warranty of\n
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n
GNU General Public License for more details.\n
\n
You should have received a copy of the GNU General Public License\n
along with this program; if not, write to the Free Software\n
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.\n
*/\n
\n
//Add indentation to an HTML element\n
function addIndentation(container, first, level){\n
  var children = container.children;\n
  var text;\n
  var n = children.length;\n
  if(first){\n
    text = container.innerHTML.trim().replace(\'>\', \'>\\n\').split(\'\\n\');\n
    var m = text.length;\n
    for(var i = 0; i < m; i++){\n
      text[i] = text[i].trim();\n
    }\n
  }\n
  else\n
    text = container.innerHTML.trim().split(\'\\n\');\n
  if(n == 0 && text.length == 1)\n
    container.innerHTML = text[0];\n
  else if(n == 0) {\n
    container.innerHTML = \'\\n  \' + text.join(\'\\n  \') + \'\\n\';\n
  }\n
  else {\n
    container.innerHTML = text.join(\'\\n\');\n
    text = \'\';\n
    children = container.childNodes;\n
    n = children.length;\n
    for(var i = 0; i < n; i++){\n
      var child = children[i];\n
      var addNewLine = false;\n
      if(child.nodeType == 1){\n
        text += addIndentation(child, false, 0);\n
        addNewLine = child.tagName.length > 1 && child.tagName != \'P\' && i < n - 1;\n
      }\n
      else{\n
        var textNotEmpty = child.textContent.trim() != \'\';\n
        if(textNotEmpty)\n
          text += child.textContent;\n
        addNewLine = textNotEmpty && child.textContent.search(\'\\n\') > -1 && i < n - 1;\n
      }\n
      if(addNewLine)\n
        text += \'\\n\';\n
    }\n
    if(first){\n
      text = container.innerHTML.split(\'\\n\');\n
      var result = \'\\n  \';\n
      first = true;\n
      n = text.length;\n
      for(var i = 0; i < n; i++){\n
        if(text[i].trim() != \'\'){\n
          if(first){\n
            first = false;\n
            result += text[i];\n
          }\n
          else\n
            result += \'\\n  \' + text[i];\n
        }\n
      }\n
      result += \'\\n\';\n
      container.innerHTML = result;\n
    }\n
    else\n
      container.innerHTML = \'\\n  \' + text.split(\'\\n\').join(\'\\n  \') + \'\\n\';\n
  }\n
  var element = document.createElement(\'div\');\n
  element.appendChild(container.cloneNode(true));\n
  var whitespaces = Array(level + 1).join(\'  \');\n
  return whitespaces + element.innerHTML.split(\'\\n\').join(\'\\n\' + whitespaces);\n
}\n
\n
function indent(container, level){\n
  return addIndentation(container, true, level);\n
}

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
