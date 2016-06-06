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
            <value> <string>anonymous_http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts53291754.85</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>method-draw.gadget.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*jslint indent: 2 */\n
/*global window, rJS, RSVP, curConfig, svgCanvas */\n
(function (window, rJS, RSVP) {\n
  "use strict";\n
\n
  curConfig.jGraduatePath = "lib/jgraduate/images/";  // XXX images are not loaded at the good place\n
\n
  rJS(window)\n
    .ready(function (g) {\n
      g.props = {};\n
      [].forEach.call(window.document.head.querySelectorAll("base"), function (el) {\n
        // XXX GadgetField adds <base> tag to fit to the parent page location, it\'s BAD to remove them.\n
        //     In the case of method-draw, all component are loaded dynamicaly through ajax requests in\n
        //     method-draw "folder". By setting a <base> tag, we change the url resolution behavior, and\n
        //     we break all dynamic links. So, deleting <base> is required.\n
        window.document.head.removeChild(el);\n
      });\n
      var deferred = RSVP.defer();\n
      svgCanvas.ready(function () {\n
        deferred.resolve();\n
      });\n
      return deferred.promise;\n
    })\n
    .declareMethod(\'render\', function (options) {\n
      this.props.key = options.key;\n
      svgCanvas.setSvgString(options.value);\n
    })\n
    .declareService(function () {\n
      if (/(?:^\\?|&)auto_focus=(true|1)(?:&|$)/.test(window.location.search)) {\n
        window.focus();  // should be done by the parent gadget?\n
      }\n
    })\n
    .declareMethod(\'getContent\', function () {\n
      var form_data = {};\n
      form_data[this.props.key] = svgCanvas.getSvgString();\n
      return form_data;\n
    });\n
\n
}(window, rJS, RSVP));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1483</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
