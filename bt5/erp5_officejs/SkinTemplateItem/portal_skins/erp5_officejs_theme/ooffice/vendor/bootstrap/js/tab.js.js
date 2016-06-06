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
            <value> <string>ts44314529.27</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>tab.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* ========================================================================\n
 * Bootstrap: tab.js v3.0.3\n
 * http://getbootstrap.com/javascript/#tabs\n
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
  // TAB CLASS DEFINITION\n
  // ====================\n
\n
  var Tab = function (element) {\n
    this.element = $(element)\n
  }\n
\n
  Tab.prototype.show = function () {\n
    var $this    = this.element\n
    var $ul      = $this.closest(\'ul:not(.dropdown-menu)\')\n
    var selector = $this.data(\'target\')\n
\n
    if (!selector) {\n
      selector = $this.attr(\'href\')\n
      selector = selector && selector.replace(/.*(?=#[^\\s]*$)/, \'\') //strip for ie7\n
    }\n
\n
    if ($this.parent(\'li\').hasClass(\'active\')) return\n
\n
    var previous = $ul.find(\'.active:last a\')[0]\n
    var e        = $.Event(\'show.bs.tab\', {\n
      relatedTarget: previous\n
    })\n
\n
    $this.trigger(e)\n
\n
    if (e.isDefaultPrevented()) return\n
\n
    var $target = $(selector)\n
\n
    this.activate($this.parent(\'li\'), $ul)\n
    this.activate($target, $target.parent(), function () {\n
      $this.trigger({\n
        type: \'shown.bs.tab\'\n
      , relatedTarget: previous\n
      })\n
    })\n
  }\n
\n
  Tab.prototype.activate = function (element, container, callback) {\n
    var $active    = container.find(\'> .active\')\n
    var transition = callback\n
      && $.support.transition\n
      && $active.hasClass(\'fade\')\n
\n
    function next() {\n
      $active\n
        .removeClass(\'active\')\n
        .find(\'> .dropdown-menu > .active\')\n
        .removeClass(\'active\')\n
\n
      element.addClass(\'active\')\n
\n
      if (transition) {\n
        element[0].offsetWidth // reflow for transition\n
        element.addClass(\'in\')\n
      } else {\n
        element.removeClass(\'fade\')\n
      }\n
\n
      if (element.parent(\'.dropdown-menu\')) {\n
        element.closest(\'li.dropdown\').addClass(\'active\')\n
      }\n
\n
      callback && callback()\n
    }\n
\n
    transition ?\n
      $active\n
        .one($.support.transition.end, next)\n
        .emulateTransitionEnd(150) :\n
      next()\n
\n
    $active.removeClass(\'in\')\n
  }\n
\n
\n
  // TAB PLUGIN DEFINITION\n
  // =====================\n
\n
  var old = $.fn.tab\n
\n
  $.fn.tab = function ( option ) {\n
    return this.each(function () {\n
      var $this = $(this)\n
      var data  = $this.data(\'bs.tab\')\n
\n
      if (!data) $this.data(\'bs.tab\', (data = new Tab(this)))\n
      if (typeof option == \'string\') data[option]()\n
    })\n
  }\n
\n
  $.fn.tab.Constructor = Tab\n
\n
\n
  // TAB NO CONFLICT\n
  // ===============\n
\n
  $.fn.tab.noConflict = function () {\n
    $.fn.tab = old\n
    return this\n
  }\n
\n
\n
  // TAB DATA-API\n
  // ============\n
\n
  $(document).on(\'click.bs.tab.data-api\', \'[data-toggle="tab"], [data-toggle="pill"]\', function (e) {\n
    e.preventDefault()\n
    $(this).tab(\'show\')\n
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
            <value> <int>3413</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
