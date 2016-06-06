<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts40515059.52</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery-svg.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals $, jQuery */\n
/*jslint vars: true */\n
/**\n
 * jQuery module to work with SVG.\n
 *\n
 * Licensed under the MIT License\n
 *\n
 */\n
\n
// Dependencies:\n
// 1) jquery\n
\n
(function() {\'use strict\';\n
\n
  // This fixes $(...).attr() to work as expected with SVG elements.\n
  // Does not currently use *AttributeNS() since we rarely need that.\n
\n
  // See http://api.jquery.com/attr/ for basic documentation of .attr()\n
\n
  // Additional functionality:\n
  // - When getting attributes, a string that\'s a number is return as type number.\n
  // - If an array is supplied as first parameter, multiple values are returned\n
  // as an object with values for each given attributes\n
\n
  var proxied = jQuery.fn.attr,\n
    // TODO use NS.SVG instead\n
    svgns = "http://www.w3.org/2000/svg";\n
  jQuery.fn.attr = function(key, value) {\n
    var i, attr;\n
\tvar len = this.length;\n
    if (!len) {return proxied.apply(this, arguments);}\n
    for (i = 0; i < len; ++i) {\n
      var elem = this[i];\n
      // set/get SVG attribute\n
      if (elem.namespaceURI === svgns) {\n
        // Setting attribute\n
        if (value !== undefined) {\n
          elem.setAttribute(key, value);\n
        } else if ($.isArray(key)) {\n
          // Getting attributes from array\n
          var j = key.length, obj = {};\n
\n
          while (j--) {\n
            var aname = key[j];\n
            attr = elem.getAttribute(aname);\n
            // This returns a number when appropriate\n
            if (attr || attr === "0") {\n
              attr = isNaN(attr) ? attr : (attr - 0);\n
            }\n
            obj[aname] = attr;\n
          }\n
          return obj;\n
        }\n
\t\tif (typeof key === "object") {\n
          // Setting attributes form object\n
\t\t  var v;\n
          for (v in key) {\n
            elem.setAttribute(v, key[v]);\n
          }\n
        // Getting attribute\n
        } else {\n
          attr = elem.getAttribute(key);\n
          if (attr || attr === "0") {\n
            attr = isNaN(attr) ? attr : (attr - 0);\n
          }\n
          return attr;\n
        }\n
      } else {\n
        return proxied.apply(this, arguments);\n
      }\n
    }\n
    return this;\n
  };\n
}());\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2085</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
