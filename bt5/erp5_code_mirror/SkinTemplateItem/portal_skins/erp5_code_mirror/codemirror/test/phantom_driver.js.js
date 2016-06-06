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
            <value> <string>ts21897151.3</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>phantom_driver.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

var page = require(\'webpage\').create();\n
\n
page.open("http://localhost:3000/test/index.html", function (status) {\n
  if (status != "success") {\n
    console.log("page couldn\'t be loaded successfully");\n
    phantom.exit(1);\n
  }\n
  waitFor(function () {\n
    return page.evaluate(function () {\n
      var output = document.getElementById(\'status\');\n
      if (!output) { return false; }\n
      return (/^(\\d+ failures?|all passed)/i).test(output.innerText);\n
    });\n
  }, function () {\n
    var failed = page.evaluate(function () { return window.failed; });\n
    var output = page.evaluate(function () {\n
      return document.getElementById(\'output\').innerText + "\\n" +\n
        document.getElementById(\'status\').innerText;\n
    });\n
    console.log(output);\n
    phantom.exit(failed > 0 ? 1 : 0);\n
  });\n
});\n
\n
function waitFor (test, cb) {\n
  if (test()) {\n
    cb();\n
  } else {\n
    setTimeout(function () { waitFor(test, cb); }, 250);\n
  }\n
}\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>921</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
