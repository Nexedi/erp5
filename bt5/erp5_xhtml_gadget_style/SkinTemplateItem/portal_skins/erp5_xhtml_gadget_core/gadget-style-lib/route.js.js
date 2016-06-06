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
            <value> <string>ts62728561.31</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>route.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*global window, jQuery */\n
/*!\n
 * route.js v1.0.0\n
 *\n
 * Copyright 2012, Romain Courteaud\n
 * Dual licensed under the MIT or GPL Version 2 licenses.\n
 *\n
 * Date: Mon Jul 16 2012\n
 */\n
"use strict";\n
(function (window, $) {\n
\n
  $.extend({\n
    StatelessDeferred: function () {\n
      var doneList = $.Callbacks("memory"),\n
        promise = {\n
          done: doneList.add,\n
\n
          // Get a promise for this deferred\n
          // If obj is provided, the promise aspect is added to the object\n
          promise: function (obj) {\n
            var i,\n
              keys = [\'done\', \'promise\'];\n
            if (obj === undefined) {\n
              obj = promise;\n
            } else {\n
              for (i = 0; i < keys.length; i += 1) {\n
                obj[keys[i]] = promise[keys[i]];\n
              }\n
            }\n
            return obj;\n
          }\n
        },\n
        deferred = promise.promise({});\n
\n
      deferred.resolveWith = doneList.fireWith;\n
\n
      // All done!\n
      return deferred;\n
    }\n
  });\n
\n
  var routes = [],\n
    current_priority = 0,\n
    methods = {\n
      add: function (pattern, priority) {\n
        var i = 0,\n
          inserted = false,\n
          length = routes.length,\n
          dfr = $.StatelessDeferred(),\n
          context = $(this),\n
          escapepattern,\n
          matchingpattern;\n
\n
        if (priority === undefined) {\n
          priority = 0;\n
        }\n
        if (pattern !== undefined) {\n
\n
          // http://simonwillison.net/2006/Jan/20/escape/\n
          escapepattern = pattern.replace(/[\\-\\[\\]{}()*+?.,\\\\\\^$|#\\s]/g, "\\\\$&");\n
          matchingpattern = escapepattern\n
                              .replace(/<int:\\w+>/g, "(\\\\d+)")\n
                              .replace(/<path:\\w+>/g, "(.+)")\n
                              .replace(/<\\w+>/g, "([^/]+)");\n
\n
          while (!inserted) {\n
            if ((i === length) || (priority >= routes[i][2])) {\n
              routes.splice(i, 0, [new RegExp(\'^\' + matchingpattern + \'$\'), dfr, priority, context]);\n
              inserted = true;\n
            } else {\n
              i += 1;\n
            }\n
          }\n
        }\n
        return dfr.promise();\n
      },\n
      go: function (path, min_priority) {\n
        var dfr = $.Deferred(),\n
          context = $(this),\n
          result;\n
\n
        if (min_priority === undefined) {\n
          min_priority = 0;\n
        }\n
        setTimeout(function () {\n
          var i = 0,\n
            found = false,\n
            slice_index = -1,\n
            slice_priority = -1;\n
          for (i = 0; i < routes.length; i += 1) {\n
            if (slice_priority !== routes[i][2]) {\n
              slice_priority = routes[i][2];\n
              slice_index = i;\n
            }\n
            if (routes[i][2] < min_priority) {\n
              break;\n
            } else if (routes[i][0].test(path)) {\n
              result = routes[i][0].exec(path);\n
              dfr = routes[i][1];\n
              context = routes[i][3];\n
              current_priority = routes[i][2];\n
              found = true;\n
              break;\n
            }\n
          }\n
          if (i === routes.length) {\n
            slice_index = i;\n
          }\n
          if (slice_index > -1) {\n
            routes = routes.slice(slice_index);\n
          }\n
          if (found) {\n
            dfr.resolveWith(\n
              context,\n
              result.slice(1)\n
            );\n
          } else {\n
            dfr.rejectWith(context);\n
          }\n
        });\n
        return dfr.promise();\n
      },\n
    };\n
\n
\n
  $.routereset = function () {\n
    routes = [];\n
    current_priority = 0;\n
  };\n
\n
  $.routepriority = function () {\n
    return current_priority;\n
  };\n
\n
  $.fn.route = function (method) {\n
    var result;\n
    if (methods.hasOwnProperty(method)) {\n
      result = methods[method].apply(\n
        this,\n
        Array.prototype.slice.call(arguments, 1)\n
      );\n
    } else {\n
      $.error(\'Method \' + method +\n
              \' does not exist on jQuery.route\');\n
    }\n
    return result;\n
  };\n
\n
}(window, jQuery));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3939</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>route.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
