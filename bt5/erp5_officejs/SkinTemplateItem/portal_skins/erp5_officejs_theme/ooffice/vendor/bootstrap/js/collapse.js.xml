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
            <value> <string>ts44314528.85</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>collapse.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* ========================================================================\n
 * Bootstrap: collapse.js v3.0.3\n
 * http://getbootstrap.com/javascript/#collapse\n
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
  // COLLAPSE PUBLIC CLASS DEFINITION\n
  // ================================\n
\n
  var Collapse = function (element, options) {\n
    this.$element      = $(element)\n
    this.options       = $.extend({}, Collapse.DEFAULTS, options)\n
    this.transitioning = null\n
\n
    if (this.options.parent) this.$parent = $(this.options.parent)\n
    if (this.options.toggle) this.toggle()\n
  }\n
\n
  Collapse.DEFAULTS = {\n
    toggle: true\n
  }\n
\n
  Collapse.prototype.dimension = function () {\n
    var hasWidth = this.$element.hasClass(\'width\')\n
    return hasWidth ? \'width\' : \'height\'\n
  }\n
\n
  Collapse.prototype.show = function () {\n
    if (this.transitioning || this.$element.hasClass(\'in\')) return\n
\n
    var startEvent = $.Event(\'show.bs.collapse\')\n
    this.$element.trigger(startEvent)\n
    if (startEvent.isDefaultPrevented()) return\n
\n
    var actives = this.$parent && this.$parent.find(\'> .panel > .in\')\n
\n
    if (actives && actives.length) {\n
      var hasData = actives.data(\'bs.collapse\')\n
      if (hasData && hasData.transitioning) return\n
      actives.collapse(\'hide\')\n
      hasData || actives.data(\'bs.collapse\', null)\n
    }\n
\n
    var dimension = this.dimension()\n
\n
    this.$element\n
      .removeClass(\'collapse\')\n
      .addClass(\'collapsing\')\n
      [dimension](0)\n
\n
    this.transitioning = 1\n
\n
    var complete = function () {\n
      this.$element\n
        .removeClass(\'collapsing\')\n
        .addClass(\'in\')\n
        [dimension](\'auto\')\n
      this.transitioning = 0\n
      this.$element.trigger(\'shown.bs.collapse\')\n
    }\n
\n
    if (!$.support.transition) return complete.call(this)\n
\n
    var scrollSize = $.camelCase([\'scroll\', dimension].join(\'-\'))\n
\n
    this.$element\n
      .one($.support.transition.end, $.proxy(complete, this))\n
      .emulateTransitionEnd(350)\n
      [dimension](this.$element[0][scrollSize])\n
  }\n
\n
  Collapse.prototype.hide = function () {\n
    if (this.transitioning || !this.$element.hasClass(\'in\')) return\n
\n
    var startEvent = $.Event(\'hide.bs.collapse\')\n
    this.$element.trigger(startEvent)\n
    if (startEvent.isDefaultPrevented()) return\n
\n
    var dimension = this.dimension()\n
\n
    this.$element\n
      [dimension](this.$element[dimension]())\n
      [0].offsetHeight\n
\n
    this.$element\n
      .addClass(\'collapsing\')\n
      .removeClass(\'collapse\')\n
      .removeClass(\'in\')\n
\n
    this.transitioning = 1\n
\n
    var complete = function () {\n
      this.transitioning = 0\n
      this.$element\n
        .trigger(\'hidden.bs.collapse\')\n
        .removeClass(\'collapsing\')\n
        .addClass(\'collapse\')\n
    }\n
\n
    if (!$.support.transition) return complete.call(this)\n
\n
    this.$element\n
      [dimension](0)\n
      .one($.support.transition.end, $.proxy(complete, this))\n
      .emulateTransitionEnd(350)\n
  }\n
\n
  Collapse.prototype.toggle = function () {\n
    this[this.$element.hasClass(\'in\') ? \'hide\' : \'show\']()\n
  }\n
\n
\n
  // COLLAPSE PLUGIN DEFINITION\n
  // ==========================\n
\n
  var old = $.fn.collapse\n
\n
  $.fn.collapse = function (option) {\n
    return this.each(function () {\n
      var $this   = $(this)\n
      var data    = $this.data(\'bs.collapse\')\n
      var options = $.extend({}, Collapse.DEFAULTS, $this.data(), typeof option == \'object\' && option)\n
\n
      if (!data) $this.data(\'bs.collapse\', (data = new Collapse(this, options)))\n
      if (typeof option == \'string\') data[option]()\n
    })\n
  }\n
\n
  $.fn.collapse.Constructor = Collapse\n
\n
\n
  // COLLAPSE NO CONFLICT\n
  // ====================\n
\n
  $.fn.collapse.noConflict = function () {\n
    $.fn.collapse = old\n
    return this\n
  }\n
\n
\n
  // COLLAPSE DATA-API\n
  // =================\n
\n
  $(document).on(\'click.bs.collapse.data-api\', \'[data-toggle=collapse]\', function (e) {\n
    var $this   = $(this), href\n
    var target  = $this.attr(\'data-target\')\n
        || e.preventDefault()\n
        || (href = $this.attr(\'href\')) && href.replace(/.*(?=#[^\\s]+$)/, \'\') //strip for ie7\n
    var $target = $(target)\n
    var data    = $target.data(\'bs.collapse\')\n
    var option  = data ? \'toggle\' : $this.data()\n
    var parent  = $this.attr(\'data-parent\')\n
    var $parent = parent && $(parent)\n
\n
    if (!data || !data.transitioning) {\n
      if ($parent) $parent.find(\'[data-toggle=collapse][data-parent="\' + parent + \'"]\').not($this).addClass(\'collapsed\')\n
      $this[$target.hasClass(\'in\') ? \'addClass\' : \'removeClass\'](\'collapsed\')\n
    }\n
\n
    $target.collapse(option)\n
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
            <value> <int>5228</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
