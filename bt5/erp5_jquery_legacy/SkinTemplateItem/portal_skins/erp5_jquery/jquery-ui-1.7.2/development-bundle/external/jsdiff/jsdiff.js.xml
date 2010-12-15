<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts65545387.59</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jsdiff.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * Javascript Diff Algorithm\n
 *  By John Resig (http://ejohn.org/)\n
 *  Modified by Chu Alan "sprite"\n
 *\n
 * More Info:\n
 *  http://ejohn.org/projects/javascript-diff-algorithm/\n
 */\n
\n
function escape(s) {\n
    var n = s;\n
    n = n.replace(/&/g, "&amp;");\n
    n = n.replace(/</g, "&lt;");\n
    n = n.replace(/>/g, "&gt;");\n
    n = n.replace(/"/g, "&quot;");\n
\n
    return n;\n
}\n
\n
function diffString( o, n ) {\n
  o = o.replace(/\\s+$/, \'\');\n
  n = n.replace(/\\s+$/, \'\');\n
\n
  var out = diff(o == "" ? [] : o.split(/\\s+/), n == "" ? [] : n.split(/\\s+/) );\n
  var str = "";\n
\n
  var oSpace = o.match(/\\s+/g);\n
  if (oSpace == null) {\n
    oSpace = ["\\n"];\n
  } else {\n
    oSpace.push("\\n");\n
  }\n
  var nSpace = n.match(/\\s+/g);\n
  if (nSpace == null) {\n
    nSpace = ["\\n"];\n
  } else {\n
    nSpace.push("\\n");\n
  }\n
\n
  if (out.n.length == 0) {\n
      for (var i = 0; i < out.o.length; i++) {\n
        str += \'<del>\' + escape(out.o[i]) + oSpace[i] + "</del>";\n
      }\n
  } else {\n
    if (out.n[0].text == null) {\n
      for (n = 0; n < out.o.length && out.o[n].text == null; n++) {\n
        str += \'<del>\' + escape(out.o[n]) + oSpace[n] + "</del>";\n
      }\n
    }\n
\n
    for ( var i = 0; i < out.n.length; i++ ) {\n
      if (out.n[i].text == null) {\n
        str += \'<ins>\' + escape(out.n[i]) + nSpace[i] + "</ins>";\n
      } else {\n
        var pre = "";\n
\n
        for (n = out.n[i].row + 1; n < out.o.length && out.o[n].text == null; n++ ) {\n
          pre += \'<del>\' + escape(out.o[n]) + oSpace[n] + "</del>";\n
        }\n
        str += " " + out.n[i].text + nSpace[i] + pre;\n
      }\n
    }\n
  }\n
  \n
  return str;\n
}\n
\n
function randomColor() {\n
    return "rgb(" + (Math.random() * 100) + "%, " + \n
                    (Math.random() * 100) + "%, " + \n
                    (Math.random() * 100) + "%)";\n
}\n
function diffString2( o, n ) {\n
  o = o.replace(/\\s+$/, \'\');\n
  n = n.replace(/\\s+$/, \'\');\n
\n
  var out = diff(o == "" ? [] : o.split(/\\s+/), n == "" ? [] : n.split(/\\s+/) );\n
\n
  var oSpace = o.match(/\\s+/g);\n
  if (oSpace == null) {\n
    oSpace = ["\\n"];\n
  } else {\n
    oSpace.push("\\n");\n
  }\n
  var nSpace = n.match(/\\s+/g);\n
  if (nSpace == null) {\n
    nSpace = ["\\n"];\n
  } else {\n
    nSpace.push("\\n");\n
  }\n
\n
  var os = "";\n
  var colors = new Array();\n
  for (var i = 0; i < out.o.length; i++) {\n
      colors[i] = randomColor();\n
\n
      if (out.o[i].text != null) {\n
          os += \'<span style="background-color: \' +colors[i]+ \'">\' + \n
                escape(out.o[i].text) + oSpace[i] + "</span>";\n
      } else {\n
          os += "<del>" + escape(out.o[i]) + oSpace[i] + "</del>";\n
      }\n
  }\n
\n
  var ns = "";\n
  for (var i = 0; i < out.n.length; i++) {\n
      if (out.n[i].text != null) {\n
          ns += \'<span style="background-color: \' +colors[out.n[i].row]+ \'">\' + \n
                escape(out.n[i].text) + nSpace[i] + "</span>";\n
      } else {\n
          ns += "<ins>" + escape(out.n[i]) + nSpace[i] + "</ins>";\n
      }\n
  }\n
\n
  return { o : os , n : ns };\n
}\n
\n
function diff( o, n ) {\n
  var ns = new Object();\n
  var os = new Object();\n
  \n
  for ( var i = 0; i < n.length; i++ ) {\n
    if ( ns[ n[i] ] == null )\n
      ns[ n[i] ] = { rows: new Array(), o: null };\n
    ns[ n[i] ].rows.push( i );\n
  }\n
  \n
  for ( var i = 0; i < o.length; i++ ) {\n
    if ( os[ o[i] ] == null )\n
      os[ o[i] ] = { rows: new Array(), n: null };\n
    os[ o[i] ].rows.push( i );\n
  }\n
  \n
  for ( var i in ns ) {\n
    if ( ns[i].rows.length == 1 && typeof(os[i]) != "undefined" && os[i].rows.length == 1 ) {\n
      n[ ns[i].rows[0] ] = { text: n[ ns[i].rows[0] ], row: os[i].rows[0] };\n
      o[ os[i].rows[0] ] = { text: o[ os[i].rows[0] ], row: ns[i].rows[0] };\n
    }\n
  }\n
  \n
  for ( var i = 0; i < n.length - 1; i++ ) {\n
    if ( n[i].text != null && n[i+1].text == null && n[i].row + 1 < o.length && o[ n[i].row + 1 ].text == null && \n
         n[i+1] == o[ n[i].row + 1 ] ) {\n
      n[i+1] = { text: n[i+1], row: n[i].row + 1 };\n
      o[n[i].row+1] = { text: o[n[i].row+1], row: i + 1 };\n
    }\n
  }\n
  \n
  for ( var i = n.length - 1; i > 0; i-- ) {\n
    if ( n[i].text != null && n[i-1].text == null && n[i].row > 0 && o[ n[i].row - 1 ].text == null && \n
         n[i-1] == o[ n[i].row - 1 ] ) {\n
      n[i-1] = { text: n[i-1], row: n[i].row - 1 };\n
      o[n[i].row-1] = { text: o[n[i].row-1], row: i - 1 };\n
    }\n
  }\n
  \n
  return { o: o, n: n };\n
}\n
\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <long>4256</long> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
