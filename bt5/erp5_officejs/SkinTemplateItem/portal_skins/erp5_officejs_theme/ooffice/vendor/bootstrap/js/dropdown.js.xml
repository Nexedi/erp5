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
            <value> <string>ts44314528.95</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>dropdown.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* ========================================================================\n
 * Bootstrap: dropdown.js v3.0.3\n
 * http://getbootstrap.com/javascript/#dropdowns\n
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
  // DROPDOWN CLASS DEFINITION\n
  // =========================\n
\n
  var backdrop = \'.dropdown-backdrop\'\n
  var toggle   = \'[data-toggle=dropdown]\'\n
  var Dropdown = function (element) {\n
    $(element).on(\'click.bs.dropdown\', this.toggle)\n
  }\n
\n
  Dropdown.prototype.toggle = function (e) {\n
    var $this = $(this)\n
\n
    if ($this.is(\'.disabled, :disabled\')) return\n
\n
    var $parent  = getParent($this)\n
    var isActive = $parent.hasClass(\'open\')\n
\n
    clearMenus()\n
\n
    if (!isActive) {\n
      if (\'ontouchstart\' in document.documentElement && !$parent.closest(\'.navbar-nav\').length) {\n
        // if mobile we use a backdrop because click events don\'t delegate\n
        $(\'<div class="dropdown-backdrop"/>\').insertAfter($(this)).on(\'click\', clearMenus)\n
      }\n
\n
      $parent.trigger(e = $.Event(\'show.bs.dropdown\'))\n
\n
      if (e.isDefaultPrevented()) return\n
\n
      $parent\n
        .toggleClass(\'open\')\n
        .trigger(\'shown.bs.dropdown\')\n
\n
      $this.focus()\n
    }\n
\n
    return false\n
  }\n
\n
  Dropdown.prototype.keydown = function (e) {\n
    if (!/(38|40|27)/.test(e.keyCode)) return\n
\n
    var $this = $(this)\n
\n
    e.preventDefault()\n
    e.stopPropagation()\n
\n
    if ($this.is(\'.disabled, :disabled\')) return\n
\n
    var $parent  = getParent($this)\n
    var isActive = $parent.hasClass(\'open\')\n
\n
    if (!isActive || (isActive && e.keyCode == 27)) {\n
      if (e.which == 27) $parent.find(toggle).focus()\n
      return $this.click()\n
    }\n
\n
    var $items = $(\'[role=menu] li:not(.divider):visible a\', $parent)\n
\n
    if (!$items.length) return\n
\n
    var index = $items.index($items.filter(\':focus\'))\n
\n
    if (e.keyCode == 38 && index > 0)                 index--                        // up\n
    if (e.keyCode == 40 && index < $items.length - 1) index++                        // down\n
    if (!~index)                                      index=0\n
\n
    $items.eq(index).focus()\n
  }\n
\n
  function clearMenus() {\n
    $(backdrop).remove()\n
    $(toggle).each(function (e) {\n
      var $parent = getParent($(this))\n
      if (!$parent.hasClass(\'open\')) return\n
      $parent.trigger(e = $.Event(\'hide.bs.dropdown\'))\n
      if (e.isDefaultPrevented()) return\n
      $parent.removeClass(\'open\').trigger(\'hidden.bs.dropdown\')\n
    })\n
  }\n
\n
  function getParent($this) {\n
    var selector = $this.attr(\'data-target\')\n
\n
    if (!selector) {\n
      selector = $this.attr(\'href\')\n
      selector = selector && /#/.test(selector) && selector.replace(/.*(?=#[^\\s]*$)/, \'\') //strip for ie7\n
    }\n
\n
    var $parent = selector && $(selector)\n
\n
    return $parent && $parent.length ? $parent : $this.parent()\n
  }\n
\n
\n
  // DROPDOWN PLUGIN DEFINITION\n
  // ==========================\n
\n
  var old = $.fn.dropdown\n
\n
  $.fn.dropdown = function (option) {\n
    return this.each(function () {\n
      var $this = $(this)\n
      var data  = $this.data(\'bs.dropdown\')\n
\n
      if (!data) $this.data(\'bs.dropdown\', (data = new Dropdown(this)))\n
      if (typeof option == \'string\') data[option].call($this)\n
    })\n
  }\n
\n
  $.fn.dropdown.Constructor = Dropdown\n
\n
\n
  // DROPDOWN NO CONFLICT\n
  // ====================\n
\n
  $.fn.dropdown.noConflict = function () {\n
    $.fn.dropdown = old\n
    return this\n
  }\n
\n
\n
  // APPLY TO STANDARD DROPDOWN ELEMENTS\n
  // ===================================\n
\n
  $(document)\n
    .on(\'click.bs.dropdown.data-api\', clearMenus)\n
    .on(\'click.bs.dropdown.data-api\', \'.dropdown form\', function (e) { e.stopPropagation() })\n
    .on(\'click.bs.dropdown.data-api\'  , toggle, Dropdown.prototype.toggle)\n
    .on(\'keydown.bs.dropdown.data-api\', toggle + \', [role=menu]\' , Dropdown.prototype.keydown)\n
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
            <value> <int>4477</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
