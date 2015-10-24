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
            <value> <string>ts44314529.09</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>popover.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* ========================================================================\n
 * Bootstrap: popover.js v3.0.3\n
 * http://getbootstrap.com/javascript/#popovers\n
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
  // POPOVER PUBLIC CLASS DEFINITION\n
  // ===============================\n
\n
  var Popover = function (element, options) {\n
    this.init(\'popover\', element, options)\n
  }\n
\n
  if (!$.fn.tooltip) throw new Error(\'Popover requires tooltip.js\')\n
\n
  Popover.DEFAULTS = $.extend({} , $.fn.tooltip.Constructor.DEFAULTS, {\n
    placement: \'right\'\n
  , trigger: \'click\'\n
  , content: \'\'\n
  , template: \'<div class="popover"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>\'\n
  })\n
\n
\n
  // NOTE: POPOVER EXTENDS tooltip.js\n
  // ================================\n
\n
  Popover.prototype = $.extend({}, $.fn.tooltip.Constructor.prototype)\n
\n
  Popover.prototype.constructor = Popover\n
\n
  Popover.prototype.getDefaults = function () {\n
    return Popover.DEFAULTS\n
  }\n
\n
  Popover.prototype.setContent = function () {\n
    var $tip    = this.tip()\n
    var title   = this.getTitle()\n
    var content = this.getContent()\n
\n
    $tip.find(\'.popover-title\')[this.options.html ? \'html\' : \'text\'](title)\n
    $tip.find(\'.popover-content\')[this.options.html ? \'html\' : \'text\'](content)\n
\n
    $tip.removeClass(\'fade top bottom left right in\')\n
\n
    // IE8 doesn\'t accept hiding via the `:empty` pseudo selector, we have to do\n
    // this manually by checking the contents.\n
    if (!$tip.find(\'.popover-title\').html()) $tip.find(\'.popover-title\').hide()\n
  }\n
\n
  Popover.prototype.hasContent = function () {\n
    return this.getTitle() || this.getContent()\n
  }\n
\n
  Popover.prototype.getContent = function () {\n
    var $e = this.$element\n
    var o  = this.options\n
\n
    return $e.attr(\'data-content\')\n
      || (typeof o.content == \'function\' ?\n
            o.content.call($e[0]) :\n
            o.content)\n
  }\n
\n
  Popover.prototype.arrow = function () {\n
    return this.$arrow = this.$arrow || this.tip().find(\'.arrow\')\n
  }\n
\n
  Popover.prototype.tip = function () {\n
    if (!this.$tip) this.$tip = $(this.options.template)\n
    return this.$tip\n
  }\n
\n
\n
  // POPOVER PLUGIN DEFINITION\n
  // =========================\n
\n
  var old = $.fn.popover\n
\n
  $.fn.popover = function (option) {\n
    return this.each(function () {\n
      var $this   = $(this)\n
      var data    = $this.data(\'bs.popover\')\n
      var options = typeof option == \'object\' && option\n
\n
      if (!data) $this.data(\'bs.popover\', (data = new Popover(this, options)))\n
      if (typeof option == \'string\') data[option]()\n
    })\n
  }\n
\n
  $.fn.popover.Constructor = Popover\n
\n
\n
  // POPOVER NO CONFLICT\n
  // ===================\n
\n
  $.fn.popover.noConflict = function () {\n
    $.fn.popover = old\n
    return this\n
  }\n
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
            <value> <int>3488</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
