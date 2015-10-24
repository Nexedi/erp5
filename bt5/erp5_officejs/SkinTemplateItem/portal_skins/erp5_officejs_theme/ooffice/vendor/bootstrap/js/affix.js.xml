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
            <value> <string>ts44314528.48</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>affix.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* ========================================================================\n
 * Bootstrap: affix.js v3.0.3\n
 * http://getbootstrap.com/javascript/#affix\n
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
  // AFFIX CLASS DEFINITION\n
  // ======================\n
\n
  var Affix = function (element, options) {\n
    this.options = $.extend({}, Affix.DEFAULTS, options)\n
    this.$window = $(window)\n
      .on(\'scroll.bs.affix.data-api\', $.proxy(this.checkPosition, this))\n
      .on(\'click.bs.affix.data-api\',  $.proxy(this.checkPositionWithEventLoop, this))\n
\n
    this.$element = $(element)\n
    this.affixed  =\n
    this.unpin    = null\n
\n
    this.checkPosition()\n
  }\n
\n
  Affix.RESET = \'affix affix-top affix-bottom\'\n
\n
  Affix.DEFAULTS = {\n
    offset: 0\n
  }\n
\n
  Affix.prototype.checkPositionWithEventLoop = function () {\n
    setTimeout($.proxy(this.checkPosition, this), 1)\n
  }\n
\n
  Affix.prototype.checkPosition = function () {\n
    if (!this.$element.is(\':visible\')) return\n
\n
    var scrollHeight = $(document).height()\n
    var scrollTop    = this.$window.scrollTop()\n
    var position     = this.$element.offset()\n
    var offset       = this.options.offset\n
    var offsetTop    = offset.top\n
    var offsetBottom = offset.bottom\n
\n
    if (typeof offset != \'object\')         offsetBottom = offsetTop = offset\n
    if (typeof offsetTop == \'function\')    offsetTop    = offset.top()\n
    if (typeof offsetBottom == \'function\') offsetBottom = offset.bottom()\n
\n
    var affix = this.unpin   != null && (scrollTop + this.unpin <= position.top) ? false :\n
                offsetBottom != null && (position.top + this.$element.height() >= scrollHeight - offsetBottom) ? \'bottom\' :\n
                offsetTop    != null && (scrollTop <= offsetTop) ? \'top\' : false\n
\n
    if (this.affixed === affix) return\n
    if (this.unpin) this.$element.css(\'top\', \'\')\n
\n
    this.affixed = affix\n
    this.unpin   = affix == \'bottom\' ? position.top - scrollTop : null\n
\n
    this.$element.removeClass(Affix.RESET).addClass(\'affix\' + (affix ? \'-\' + affix : \'\'))\n
\n
    if (affix == \'bottom\') {\n
      this.$element.offset({ top: document.body.offsetHeight - offsetBottom - this.$element.height() })\n
    }\n
  }\n
\n
\n
  // AFFIX PLUGIN DEFINITION\n
  // =======================\n
\n
  var old = $.fn.affix\n
\n
  $.fn.affix = function (option) {\n
    return this.each(function () {\n
      var $this   = $(this)\n
      var data    = $this.data(\'bs.affix\')\n
      var options = typeof option == \'object\' && option\n
\n
      if (!data) $this.data(\'bs.affix\', (data = new Affix(this, options)))\n
      if (typeof option == \'string\') data[option]()\n
    })\n
  }\n
\n
  $.fn.affix.Constructor = Affix\n
\n
\n
  // AFFIX NO CONFLICT\n
  // =================\n
\n
  $.fn.affix.noConflict = function () {\n
    $.fn.affix = old\n
    return this\n
  }\n
\n
\n
  // AFFIX DATA-API\n
  // ==============\n
\n
  $(window).on(\'load\', function () {\n
    $(\'[data-spy="affix"]\').each(function () {\n
      var $spy = $(this)\n
      var data = $spy.data()\n
\n
      data.offset = data.offset || {}\n
\n
      if (data.offsetBottom) data.offset.bottom = data.offsetBottom\n
      if (data.offsetTop)    data.offset.top    = data.offsetTop\n
\n
      $spy.affix(data)\n
    })\n
  })\n
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
            <value> <int>3861</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
