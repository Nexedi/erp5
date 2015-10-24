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
            <value> <string>ts44314529.19</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>scrollspy.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* ========================================================================\n
 * Bootstrap: scrollspy.js v3.0.3\n
 * http://getbootstrap.com/javascript/#scrollspy\n
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
  // SCROLLSPY CLASS DEFINITION\n
  // ==========================\n
\n
  function ScrollSpy(element, options) {\n
    var href\n
    var process  = $.proxy(this.process, this)\n
\n
    this.$element       = $(element).is(\'body\') ? $(window) : $(element)\n
    this.$body          = $(\'body\')\n
    this.$scrollElement = this.$element.on(\'scroll.bs.scroll-spy.data-api\', process)\n
    this.options        = $.extend({}, ScrollSpy.DEFAULTS, options)\n
    this.selector       = (this.options.target\n
      || ((href = $(element).attr(\'href\')) && href.replace(/.*(?=#[^\\s]+$)/, \'\')) //strip for ie7\n
      || \'\') + \' .nav li > a\'\n
    this.offsets        = $([])\n
    this.targets        = $([])\n
    this.activeTarget   = null\n
\n
    this.refresh()\n
    this.process()\n
  }\n
\n
  ScrollSpy.DEFAULTS = {\n
    offset: 10\n
  }\n
\n
  ScrollSpy.prototype.refresh = function () {\n
    var offsetMethod = this.$element[0] == window ? \'offset\' : \'position\'\n
\n
    this.offsets = $([])\n
    this.targets = $([])\n
\n
    var self     = this\n
    var $targets = this.$body\n
      .find(this.selector)\n
      .map(function () {\n
        var $el   = $(this)\n
        var href  = $el.data(\'target\') || $el.attr(\'href\')\n
        var $href = /^#\\w/.test(href) && $(href)\n
\n
        return ($href\n
          && $href.length\n
          && [[ $href[offsetMethod]().top + (!$.isWindow(self.$scrollElement.get(0)) && self.$scrollElement.scrollTop()), href ]]) || null\n
      })\n
      .sort(function (a, b) { return a[0] - b[0] })\n
      .each(function () {\n
        self.offsets.push(this[0])\n
        self.targets.push(this[1])\n
      })\n
  }\n
\n
  ScrollSpy.prototype.process = function () {\n
    var scrollTop    = this.$scrollElement.scrollTop() + this.options.offset\n
    var scrollHeight = this.$scrollElement[0].scrollHeight || this.$body[0].scrollHeight\n
    var maxScroll    = scrollHeight - this.$scrollElement.height()\n
    var offsets      = this.offsets\n
    var targets      = this.targets\n
    var activeTarget = this.activeTarget\n
    var i\n
\n
    if (scrollTop >= maxScroll) {\n
      return activeTarget != (i = targets.last()[0]) && this.activate(i)\n
    }\n
\n
    for (i = offsets.length; i--;) {\n
      activeTarget != targets[i]\n
        && scrollTop >= offsets[i]\n
        && (!offsets[i + 1] || scrollTop <= offsets[i + 1])\n
        && this.activate( targets[i] )\n
    }\n
  }\n
\n
  ScrollSpy.prototype.activate = function (target) {\n
    this.activeTarget = target\n
\n
    $(this.selector)\n
      .parents(\'.active\')\n
      .removeClass(\'active\')\n
\n
    var selector = this.selector\n
      + \'[data-target="\' + target + \'"],\'\n
      + this.selector + \'[href="\' + target + \'"]\'\n
\n
    var active = $(selector)\n
      .parents(\'li\')\n
      .addClass(\'active\')\n
\n
    if (active.parent(\'.dropdown-menu\').length)  {\n
      active = active\n
        .closest(\'li.dropdown\')\n
        .addClass(\'active\')\n
    }\n
\n
    active.trigger(\'activate.bs.scrollspy\')\n
  }\n
\n
\n
  // SCROLLSPY PLUGIN DEFINITION\n
  // ===========================\n
\n
  var old = $.fn.scrollspy\n
\n
  $.fn.scrollspy = function (option) {\n
    return this.each(function () {\n
      var $this   = $(this)\n
      var data    = $this.data(\'bs.scrollspy\')\n
      var options = typeof option == \'object\' && option\n
\n
      if (!data) $this.data(\'bs.scrollspy\', (data = new ScrollSpy(this, options)))\n
      if (typeof option == \'string\') data[option]()\n
    })\n
  }\n
\n
  $.fn.scrollspy.Constructor = ScrollSpy\n
\n
\n
  // SCROLLSPY NO CONFLICT\n
  // =====================\n
\n
  $.fn.scrollspy.noConflict = function () {\n
    $.fn.scrollspy = old\n
    return this\n
  }\n
\n
\n
  // SCROLLSPY DATA-API\n
  // ==================\n
\n
  $(window).on(\'load\', function () {\n
    $(\'[data-spy="scroll"]\').each(function () {\n
      var $spy = $(this)\n
      $spy.scrollspy($spy.data())\n
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
            <value> <int>4635</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
