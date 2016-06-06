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
            <value> <string>ts21897129.72</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>activebookmark.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

// Kludge in HTML5 tag recognition in IE8\n
document.createElement("section");\n
document.createElement("article");\n
\n
(function() {\n
  if (!window.addEventListener) return;\n
  var pending = false, prevVal = null;\n
\n
  function updateSoon() {\n
    if (!pending) {\n
      pending = true;\n
      setTimeout(update, 250);\n
    }\n
  }\n
\n
  function update() {\n
    pending = false;\n
    var marks = document.getElementById("nav").getElementsByTagName("a"), found;\n
    for (var i = 0; i < marks.length; ++i) {\n
      var mark = marks[i], m;\n
      if (mark.getAttribute("data-default")) {\n
        if (found == null) found = i;\n
      } else if (m = mark.href.match(/#(.*)/)) {\n
        var ref = document.getElementById(m[1]);\n
        if (ref && ref.getBoundingClientRect().top < 50)\n
          found = i;\n
      }\n
    }\n
    if (found != null && found != prevVal) {\n
      prevVal = found;\n
      var lis = document.getElementById("nav").getElementsByTagName("li");\n
      for (var i = 0; i < lis.length; ++i) lis[i].className = "";\n
      for (var i = 0; i < marks.length; ++i) {\n
        if (found == i) {\n
          marks[i].className = "active";\n
          for (var n = marks[i]; n; n = n.parentNode)\n
            if (n.nodeName == "LI") n.className = "active";\n
        } else {\n
          marks[i].className = "";\n
        }\n
      }\n
    }\n
  }\n
\n
  window.addEventListener("scroll", updateSoon);\n
  window.addEventListener("load", updateSoon);\n
  window.addEventListener("hashchange", function() {\n
    setTimeout(function() {\n
      var hash = document.location.hash, found = null, m;\n
      var marks = document.getElementById("nav").getElementsByTagName("a");\n
      for (var i = 0; i < marks.length; i++)\n
        if ((m = marks[i].href.match(/(#.*)/)) && m[1] == hash) { found = i; break; }\n
      if (found != null) for (var i = 0; i < marks.length; i++)\n
        marks[i].className = i == found ? "active" : "";\n
    }, 300);\n
  });\n
})();\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1897</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
