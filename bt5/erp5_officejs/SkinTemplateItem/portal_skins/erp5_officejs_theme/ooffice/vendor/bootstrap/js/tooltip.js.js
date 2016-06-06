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
            <value> <string>ts44314529.37</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>tooltip.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* ========================================================================\n
 * Bootstrap: tooltip.js v3.0.3\n
 * http://getbootstrap.com/javascript/#tooltip\n
 * Inspired by the original jQuery.tipsy by Jason Frame\n
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
  // TOOLTIP PUBLIC CLASS DEFINITION\n
  // ===============================\n
\n
  var Tooltip = function (element, options) {\n
    this.type       =\n
    this.options    =\n
    this.enabled    =\n
    this.timeout    =\n
    this.hoverState =\n
    this.$element   = null\n
\n
    this.init(\'tooltip\', element, options)\n
  }\n
\n
  Tooltip.DEFAULTS = {\n
    animation: true\n
  , placement: \'top\'\n
  , selector: false\n
  , template: \'<div class="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div>\'\n
  , trigger: \'hover focus\'\n
  , title: \'\'\n
  , delay: 0\n
  , html: false\n
  , container: false\n
  }\n
\n
  Tooltip.prototype.init = function (type, element, options) {\n
    this.enabled  = true\n
    this.type     = type\n
    this.$element = $(element)\n
    this.options  = this.getOptions(options)\n
\n
    var triggers = this.options.trigger.split(\' \')\n
\n
    for (var i = triggers.length; i--;) {\n
      var trigger = triggers[i]\n
\n
      if (trigger == \'click\') {\n
        this.$element.on(\'click.\' + this.type, this.options.selector, $.proxy(this.toggle, this))\n
      } else if (trigger != \'manual\') {\n
        var eventIn  = trigger == \'hover\' ? \'mouseenter\' : \'focus\'\n
        var eventOut = trigger == \'hover\' ? \'mouseleave\' : \'blur\'\n
\n
        this.$element.on(eventIn  + \'.\' + this.type, this.options.selector, $.proxy(this.enter, this))\n
        this.$element.on(eventOut + \'.\' + this.type, this.options.selector, $.proxy(this.leave, this))\n
      }\n
    }\n
\n
    this.options.selector ?\n
      (this._options = $.extend({}, this.options, { trigger: \'manual\', selector: \'\' })) :\n
      this.fixTitle()\n
  }\n
\n
  Tooltip.prototype.getDefaults = function () {\n
    return Tooltip.DEFAULTS\n
  }\n
\n
  Tooltip.prototype.getOptions = function (options) {\n
    options = $.extend({}, this.getDefaults(), this.$element.data(), options)\n
\n
    if (options.delay && typeof options.delay == \'number\') {\n
      options.delay = {\n
        show: options.delay\n
      , hide: options.delay\n
      }\n
    }\n
\n
    return options\n
  }\n
\n
  Tooltip.prototype.getDelegateOptions = function () {\n
    var options  = {}\n
    var defaults = this.getDefaults()\n
\n
    this._options && $.each(this._options, function (key, value) {\n
      if (defaults[key] != value) options[key] = value\n
    })\n
\n
    return options\n
  }\n
\n
  Tooltip.prototype.enter = function (obj) {\n
    var self = obj instanceof this.constructor ?\n
      obj : $(obj.currentTarget)[this.type](this.getDelegateOptions()).data(\'bs.\' + this.type)\n
\n
    clearTimeout(self.timeout)\n
\n
    self.hoverState = \'in\'\n
\n
    if (!self.options.delay || !self.options.delay.show) return self.show()\n
\n
    self.timeout = setTimeout(function () {\n
      if (self.hoverState == \'in\') self.show()\n
    }, self.options.delay.show)\n
  }\n
\n
  Tooltip.prototype.leave = function (obj) {\n
    var self = obj instanceof this.constructor ?\n
      obj : $(obj.currentTarget)[this.type](this.getDelegateOptions()).data(\'bs.\' + this.type)\n
\n
    clearTimeout(self.timeout)\n
\n
    self.hoverState = \'out\'\n
\n
    if (!self.options.delay || !self.options.delay.hide) return self.hide()\n
\n
    self.timeout = setTimeout(function () {\n
      if (self.hoverState == \'out\') self.hide()\n
    }, self.options.delay.hide)\n
  }\n
\n
  Tooltip.prototype.show = function () {\n
    var e = $.Event(\'show.bs.\'+ this.type)\n
\n
    if (this.hasContent() && this.enabled) {\n
      this.$element.trigger(e)\n
\n
      if (e.isDefaultPrevented()) return\n
\n
      var $tip = this.tip()\n
\n
      this.setContent()\n
\n
      if (this.options.animation) $tip.addClass(\'fade\')\n
\n
      var placement = typeof this.options.placement == \'function\' ?\n
        this.options.placement.call(this, $tip[0], this.$element[0]) :\n
        this.options.placement\n
\n
      var autoToken = /\\s?auto?\\s?/i\n
      var autoPlace = autoToken.test(placement)\n
      if (autoPlace) placement = placement.replace(autoToken, \'\') || \'top\'\n
\n
      $tip\n
        .detach()\n
        .css({ top: 0, left: 0, display: \'block\' })\n
        .addClass(placement)\n
\n
      this.options.container ? $tip.appendTo(this.options.container) : $tip.insertAfter(this.$element)\n
\n
      var pos          = this.getPosition()\n
      var actualWidth  = $tip[0].offsetWidth\n
      var actualHeight = $tip[0].offsetHeight\n
\n
      if (autoPlace) {\n
        var $parent = this.$element.parent()\n
\n
        var orgPlacement = placement\n
        var docScroll    = document.documentElement.scrollTop || document.body.scrollTop\n
        var parentWidth  = this.options.container == \'body\' ? window.innerWidth  : $parent.outerWidth()\n
        var parentHeight = this.options.container == \'body\' ? window.innerHeight : $parent.outerHeight()\n
        var parentLeft   = this.options.container == \'body\' ? 0 : $parent.offset().left\n
\n
        placement = placement == \'bottom\' && pos.top   + pos.height  + actualHeight - docScroll > parentHeight  ? \'top\'    :\n
                    placement == \'top\'    && pos.top   - docScroll   - actualHeight < 0                         ? \'bottom\' :\n
                    placement == \'right\'  && pos.right + actualWidth > parentWidth                              ? \'left\'   :\n
                    placement == \'left\'   && pos.left  - actualWidth < parentLeft                               ? \'right\'  :\n
                    placement\n
\n
        $tip\n
          .removeClass(orgPlacement)\n
          .addClass(placement)\n
      }\n
\n
      var calculatedOffset = this.getCalculatedOffset(placement, pos, actualWidth, actualHeight)\n
\n
      this.applyPlacement(calculatedOffset, placement)\n
      this.$element.trigger(\'shown.bs.\' + this.type)\n
    }\n
  }\n
\n
  Tooltip.prototype.applyPlacement = function(offset, placement) {\n
    var replace\n
    var $tip   = this.tip()\n
    var width  = $tip[0].offsetWidth\n
    var height = $tip[0].offsetHeight\n
\n
    // manually read margins because getBoundingClientRect includes difference\n
    var marginTop = parseInt($tip.css(\'margin-top\'), 10)\n
    var marginLeft = parseInt($tip.css(\'margin-left\'), 10)\n
\n
    // we must check for NaN for ie 8/9\n
    if (isNaN(marginTop))  marginTop  = 0\n
    if (isNaN(marginLeft)) marginLeft = 0\n
\n
    offset.top  = offset.top  + marginTop\n
    offset.left = offset.left + marginLeft\n
\n
    $tip\n
      .offset(offset)\n
      .addClass(\'in\')\n
\n
    // check to see if placing tip in new offset caused the tip to resize itself\n
    var actualWidth  = $tip[0].offsetWidth\n
    var actualHeight = $tip[0].offsetHeight\n
\n
    if (placement == \'top\' && actualHeight != height) {\n
      replace = true\n
      offset.top = offset.top + height - actualHeight\n
    }\n
\n
    if (/bottom|top/.test(placement)) {\n
      var delta = 0\n
\n
      if (offset.left < 0) {\n
        delta       = offset.left * -2\n
        offset.left = 0\n
\n
        $tip.offset(offset)\n
\n
        actualWidth  = $tip[0].offsetWidth\n
        actualHeight = $tip[0].offsetHeight\n
      }\n
\n
      this.replaceArrow(delta - width + actualWidth, actualWidth, \'left\')\n
    } else {\n
      this.replaceArrow(actualHeight - height, actualHeight, \'top\')\n
    }\n
\n
    if (replace) $tip.offset(offset)\n
  }\n
\n
  Tooltip.prototype.replaceArrow = function(delta, dimension, position) {\n
    this.arrow().css(position, delta ? (50 * (1 - delta / dimension) + "%") : \'\')\n
  }\n
\n
  Tooltip.prototype.setContent = function () {\n
    var $tip  = this.tip()\n
    var title = this.getTitle()\n
\n
    $tip.find(\'.tooltip-inner\')[this.options.html ? \'html\' : \'text\'](title)\n
    $tip.removeClass(\'fade in top bottom left right\')\n
  }\n
\n
  Tooltip.prototype.hide = function () {\n
    var that = this\n
    var $tip = this.tip()\n
    var e    = $.Event(\'hide.bs.\' + this.type)\n
\n
    function complete() {\n
      if (that.hoverState != \'in\') $tip.detach()\n
    }\n
\n
    this.$element.trigger(e)\n
\n
    if (e.isDefaultPrevented()) return\n
\n
    $tip.removeClass(\'in\')\n
\n
    $.support.transition && this.$tip.hasClass(\'fade\') ?\n
      $tip\n
        .one($.support.transition.end, complete)\n
        .emulateTransitionEnd(150) :\n
      complete()\n
\n
    this.$element.trigger(\'hidden.bs.\' + this.type)\n
\n
    return this\n
  }\n
\n
  Tooltip.prototype.fixTitle = function () {\n
    var $e = this.$element\n
    if ($e.attr(\'title\') || typeof($e.attr(\'data-original-title\')) != \'string\') {\n
      $e.attr(\'data-original-title\', $e.attr(\'title\') || \'\').attr(\'title\', \'\')\n
    }\n
  }\n
\n
  Tooltip.prototype.hasContent = function () {\n
    return this.getTitle()\n
  }\n
\n
  Tooltip.prototype.getPosition = function () {\n
    var el = this.$element[0]\n
    return $.extend({}, (typeof el.getBoundingClientRect == \'function\') ? el.getBoundingClientRect() : {\n
      width: el.offsetWidth\n
    , height: el.offsetHeight\n
    }, this.$element.offset())\n
  }\n
\n
  Tooltip.prototype.getCalculatedOffset = function (placement, pos, actualWidth, actualHeight) {\n
    return placement == \'bottom\' ? { top: pos.top + pos.height,   left: pos.left + pos.width / 2 - actualWidth / 2  } :\n
           placement == \'top\'    ? { top: pos.top - actualHeight, left: pos.left + pos.width / 2 - actualWidth / 2  } :\n
           placement == \'left\'   ? { top: pos.top + pos.height / 2 - actualHeight / 2, left: pos.left - actualWidth } :\n
        /* placement == \'right\' */ { top: pos.top + pos.height / 2 - actualHeight / 2, left: pos.left + pos.width   }\n
  }\n
\n
  Tooltip.prototype.getTitle = function () {\n
    var title\n
    var $e = this.$element\n
    var o  = this.options\n
\n
    title = $e.attr(\'data-original-title\')\n
      || (typeof o.title == \'function\' ? o.title.call($e[0]) :  o.title)\n
\n
    return title\n
  }\n
\n
  Tooltip.prototype.tip = function () {\n
    return this.$tip = this.$tip || $(this.options.template)\n
  }\n
\n
  Tooltip.prototype.arrow = function () {\n
    return this.$arrow = this.$arrow || this.tip().find(\'.tooltip-arrow\')\n
  }\n
\n
  Tooltip.prototype.validate = function () {\n
    if (!this.$element[0].parentNode) {\n
      this.hide()\n
      this.$element = null\n
      this.options  = null\n
    }\n
  }\n
\n
  Tooltip.prototype.enable = function () {\n
    this.enabled = true\n
  }\n
\n
  Tooltip.prototype.disable = function () {\n
    this.enabled = false\n
  }\n
\n
  Tooltip.prototype.toggleEnabled = function () {\n
    this.enabled = !this.enabled\n
  }\n
\n
  Tooltip.prototype.toggle = function (e) {\n
    var self = e ? $(e.currentTarget)[this.type](this.getDelegateOptions()).data(\'bs.\' + this.type) : this\n
    self.tip().hasClass(\'in\') ? self.leave(self) : self.enter(self)\n
  }\n
\n
  Tooltip.prototype.destroy = function () {\n
    this.hide().$element.off(\'.\' + this.type).removeData(\'bs.\' + this.type)\n
  }\n
\n
\n
  // TOOLTIP PLUGIN DEFINITION\n
  // =========================\n
\n
  var old = $.fn.tooltip\n
\n
  $.fn.tooltip = function (option) {\n
    return this.each(function () {\n
      var $this   = $(this)\n
      var data    = $this.data(\'bs.tooltip\')\n
      var options = typeof option == \'object\' && option\n
\n
      if (!data) $this.data(\'bs.tooltip\', (data = new Tooltip(this, options)))\n
      if (typeof option == \'string\') data[option]()\n
    })\n
  }\n
\n
  $.fn.tooltip.Constructor = Tooltip\n
\n
\n
  // TOOLTIP NO CONFLICT\n
  // ===================\n
\n
  $.fn.tooltip.noConflict = function () {\n
    $.fn.tooltip = old\n
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
            <value> <int>11908</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
