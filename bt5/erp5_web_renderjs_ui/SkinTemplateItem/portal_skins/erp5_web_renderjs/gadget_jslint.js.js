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
            <value> <string>ts21077825.13</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>gadget_jslint.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*global window, rJS, JSLINT, Handlebars */\n
/*jslint nomen: true, maxlen:80, indent:2*/\n
(function (rJS, Handlebars, JSLINT, window) {\n
  "use strict";\n
  var gk = rJS(window),\n
    template_source = gk.__template_element\n
                        .getElementById(\'jslint_template\')\n
                        .innerHTML,\n
    template = Handlebars.compile(template_source);\n
\n
  rJS(window)\n
    .ready(function (g) {\n
      g.props = {};\n
    })\n
    .ready(function (g) {\n
      return g.getElement().push(function (element) {\n
        g.props.element = element;\n
      });\n
    })\n
\n
    .declareMethod("render", function (options) {\n
      var text_content = options.value,\n
        data,\n
        html_content,\n
        i,\n
        line_letter = "A",\n
        len,\n
        gadget = this;\n
      JSLINT(text_content, {});\n
      data = JSLINT.data();\n
\n
      for (i = 0, len = data.errors.length; i < len; i += 1) {\n
        if (data.errors[i] !== null) {\n
          data.errors[i].line_letter = line_letter;\n
          line_letter = line_letter === "A" ? "B" : "A";\n
        }\n
      }\n
      html_content = template({\n
        error_list: data.errors\n
      });\n
\n
      gadget.props.element.querySelector("tbody")\n
                          .innerHTML = html_content;\n
    });\n
}(rJS, Handlebars, JSLINT, window));

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1278</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
