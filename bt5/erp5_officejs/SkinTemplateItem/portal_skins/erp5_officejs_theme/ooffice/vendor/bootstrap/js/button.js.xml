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
            <value> <string>ts44314528.67</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>button.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* ========================================================================\n
 * Bootstrap: button.js v3.0.3\n
 * http://getbootstrap.com/javascript/#buttons\n
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
  // BUTTON PUBLIC CLASS DEFINITION\n
  // ==============================\n
\n
  var Button = function (element, options) {\n
    this.$element = $(element)\n
    this.options  = $.extend({}, Button.DEFAULTS, options)\n
  }\n
\n
  Button.DEFAULTS = {\n
    loadingText: \'loading...\'\n
  }\n
\n
  Button.prototype.setState = function (state) {\n
    var d    = \'disabled\'\n
    var $el  = this.$element\n
    var val  = $el.is(\'input\') ? \'val\' : \'html\'\n
    var data = $el.data()\n
\n
    state = state + \'Text\'\n
\n
    if (!data.resetText) $el.data(\'resetText\', $el[val]())\n
\n
    $el[val](data[state] || this.options[state])\n
\n
    // push to event loop to allow forms to submit\n
    setTimeout(function () {\n
      state == \'loadingText\' ?\n
        $el.addClass(d).attr(d, d) :\n
        $el.removeClass(d).removeAttr(d);\n
    }, 0)\n
  }\n
\n
  Button.prototype.toggle = function () {\n
    var $parent = this.$element.closest(\'[data-toggle="buttons"]\')\n
    var changed = true\n
\n
    if ($parent.length) {\n
      var $input = this.$element.find(\'input\')\n
      if ($input.prop(\'type\') === \'radio\') {\n
        // see if clicking on current one\n
        if ($input.prop(\'checked\') && this.$element.hasClass(\'active\'))\n
          changed = false\n
        else\n
          $parent.find(\'.active\').removeClass(\'active\')\n
      }\n
      if (changed) $input.prop(\'checked\', !this.$element.hasClass(\'active\')).trigger(\'change\')\n
    }\n
\n
    if (changed) this.$element.toggleClass(\'active\')\n
  }\n
\n
\n
  // BUTTON PLUGIN DEFINITION\n
  // ========================\n
\n
  var old = $.fn.button\n
\n
  $.fn.button = function (option) {\n
    return this.each(function () {\n
      var $this   = $(this)\n
      var data    = $this.data(\'bs.button\')\n
      var options = typeof option == \'object\' && option\n
\n
      if (!data) $this.data(\'bs.button\', (data = new Button(this, options)))\n
\n
      if (option == \'toggle\') data.toggle()\n
      else if (option) data.setState(option)\n
    })\n
  }\n
\n
  $.fn.button.Constructor = Button\n
\n
\n
  // BUTTON NO CONFLICT\n
  // ==================\n
\n
  $.fn.button.noConflict = function () {\n
    $.fn.button = old\n
    return this\n
  }\n
\n
\n
  // BUTTON DATA-API\n
  // ===============\n
\n
  $(document).on(\'click.bs.button.data-api\', \'[data-toggle^=button]\', function (e) {\n
    var $btn = $(e.target)\n
    if (!$btn.hasClass(\'btn\')) $btn = $btn.closest(\'.btn\')\n
    $btn.button(\'toggle\')\n
    e.preventDefault()\n
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
            <value> <int>3265</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
