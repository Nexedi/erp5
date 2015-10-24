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
            <value> <string>ts44314528.57</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>alert.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* ========================================================================\n
 * Bootstrap: alert.js v3.0.3\n
 * http://getbootstrap.com/javascript/#alerts\n
 * ========================================================================\n
 * Copyright 2013 Twitter, Inc.\n
 *\n
 * Licensed under the Apache License, Version 2.0 (the "License");\n
 * you may not use this file except in compliance with the License.\n
 * You may obtain a copy of the License at\n
 *\n
 * http://www.apache.org/licenses/LICENSE-2.0\n
 *\n
 * Unless required by applicable law or agreed to in writing, software\n
 * distributed under the License is distributed on an "AS IS" BASIS,\n
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n
 * See the License for the specific language governing permissions and\n
 * limitations under the License.\n
 * ======================================================================== */\n
\n
\n
+function ($) { "use strict";\n
\n
  // ALERT CLASS DEFINITION\n
  // ======================\n
\n
  var dismiss = \'[data-dismiss="alert"]\'\n
  var Alert   = function (el) {\n
    $(el).on(\'click\', dismiss, this.close)\n
  }\n
\n
  Alert.prototype.close = function (e) {\n
    var $this    = $(this)\n
    var selector = $this.attr(\'data-target\')\n
\n
    if (!selector) {\n
      selector = $this.attr(\'href\')\n
      selector = selector && selector.replace(/.*(?=#[^\\s]*$)/, \'\') // strip for ie7\n
    }\n
\n
    var $parent = $(selector)\n
\n
    if (e) e.preventDefault()\n
\n
    if (!$parent.length) {\n
      $parent = $this.hasClass(\'alert\') ? $this : $this.parent()\n
    }\n
\n
    $parent.trigger(e = $.Event(\'close.bs.alert\'))\n
\n
    if (e.isDefaultPrevented()) return\n
\n
    $parent.removeClass(\'in\')\n
\n
    function removeElement() {\n
      $parent.trigger(\'closed.bs.alert\').remove()\n
    }\n
\n
    $.support.transition && $parent.hasClass(\'fade\') ?\n
      $parent\n
        .one($.support.transition.end, removeElement)\n
        .emulateTransitionEnd(150) :\n
      removeElement()\n
  }\n
\n
\n
  // ALERT PLUGIN DEFINITION\n
  // =======================\n
\n
  var old = $.fn.alert\n
\n
  $.fn.alert = function (option) {\n
    return this.each(function () {\n
      var $this = $(this)\n
      var data  = $this.data(\'bs.alert\')\n
\n
      if (!data) $this.data(\'bs.alert\', (data = new Alert(this)))\n
      if (typeof option == \'string\') data[option].call($this)\n
    })\n
  }\n
\n
  $.fn.alert.Constructor = Alert\n
\n
\n
  // ALERT NO CONFLICT\n
  // =================\n
\n
  $.fn.alert.noConflict = function () {\n
    $.fn.alert = old\n
    return this\n
  }\n
\n
\n
  // ALERT DATA-API\n
  // ==============\n
\n
  $(document).on(\'click.bs.alert.data-api\', dismiss, Alert.prototype.close)\n
\n
}(jQuery);\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2582</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
