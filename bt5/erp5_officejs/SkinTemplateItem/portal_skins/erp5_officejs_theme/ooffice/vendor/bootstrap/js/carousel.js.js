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
            <value> <string>ts44314528.77</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>carousel.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* ========================================================================\n
 * Bootstrap: carousel.js v3.0.3\n
 * http://getbootstrap.com/javascript/#carousel\n
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
  // CAROUSEL CLASS DEFINITION\n
  // =========================\n
\n
  var Carousel = function (element, options) {\n
    this.$element    = $(element)\n
    this.$indicators = this.$element.find(\'.carousel-indicators\')\n
    this.options     = options\n
    this.paused      =\n
    this.sliding     =\n
    this.interval    =\n
    this.$active     =\n
    this.$items      = null\n
\n
    this.options.pause == \'hover\' && this.$element\n
      .on(\'mouseenter\', $.proxy(this.pause, this))\n
      .on(\'mouseleave\', $.proxy(this.cycle, this))\n
  }\n
\n
  Carousel.DEFAULTS = {\n
    interval: 5000\n
  , pause: \'hover\'\n
  , wrap: true\n
  }\n
\n
  Carousel.prototype.cycle =  function (e) {\n
    e || (this.paused = false)\n
\n
    this.interval && clearInterval(this.interval)\n
\n
    this.options.interval\n
      && !this.paused\n
      && (this.interval = setInterval($.proxy(this.next, this), this.options.interval))\n
\n
    return this\n
  }\n
\n
  Carousel.prototype.getActiveIndex = function () {\n
    this.$active = this.$element.find(\'.item.active\')\n
    this.$items  = this.$active.parent().children()\n
\n
    return this.$items.index(this.$active)\n
  }\n
\n
  Carousel.prototype.to = function (pos) {\n
    var that        = this\n
    var activeIndex = this.getActiveIndex()\n
\n
    if (pos > (this.$items.length - 1) || pos < 0) return\n
\n
    if (this.sliding)       return this.$element.one(\'slid.bs.carousel\', function () { that.to(pos) })\n
    if (activeIndex == pos) return this.pause().cycle()\n
\n
    return this.slide(pos > activeIndex ? \'next\' : \'prev\', $(this.$items[pos]))\n
  }\n
\n
  Carousel.prototype.pause = function (e) {\n
    e || (this.paused = true)\n
\n
    if (this.$element.find(\'.next, .prev\').length && $.support.transition.end) {\n
      this.$element.trigger($.support.transition.end)\n
      this.cycle(true)\n
    }\n
\n
    this.interval = clearInterval(this.interval)\n
\n
    return this\n
  }\n
\n
  Carousel.prototype.next = function () {\n
    if (this.sliding) return\n
    return this.slide(\'next\')\n
  }\n
\n
  Carousel.prototype.prev = function () {\n
    if (this.sliding) return\n
    return this.slide(\'prev\')\n
  }\n
\n
  Carousel.prototype.slide = function (type, next) {\n
    var $active   = this.$element.find(\'.item.active\')\n
    var $next     = next || $active[type]()\n
    var isCycling = this.interval\n
    var direction = type == \'next\' ? \'left\' : \'right\'\n
    var fallback  = type == \'next\' ? \'first\' : \'last\'\n
    var that      = this\n
\n
    if (!$next.length) {\n
      if (!this.options.wrap) return\n
      $next = this.$element.find(\'.item\')[fallback]()\n
    }\n
\n
    this.sliding = true\n
\n
    isCycling && this.pause()\n
\n
    var e = $.Event(\'slide.bs.carousel\', { relatedTarget: $next[0], direction: direction })\n
\n
    if ($next.hasClass(\'active\')) return\n
\n
    if (this.$indicators.length) {\n
      this.$indicators.find(\'.active\').removeClass(\'active\')\n
      this.$element.one(\'slid.bs.carousel\', function () {\n
        var $nextIndicator = $(that.$indicators.children()[that.getActiveIndex()])\n
        $nextIndicator && $nextIndicator.addClass(\'active\')\n
      })\n
    }\n
\n
    if ($.support.transition && this.$element.hasClass(\'slide\')) {\n
      this.$element.trigger(e)\n
      if (e.isDefaultPrevented()) return\n
      $next.addClass(type)\n
      $next[0].offsetWidth // force reflow\n
      $active.addClass(direction)\n
      $next.addClass(direction)\n
      $active\n
        .one($.support.transition.end, function () {\n
          $next.removeClass([type, direction].join(\' \')).addClass(\'active\')\n
          $active.removeClass([\'active\', direction].join(\' \'))\n
          that.sliding = false\n
          setTimeout(function () { that.$element.trigger(\'slid.bs.carousel\') }, 0)\n
        })\n
        .emulateTransitionEnd(600)\n
    } else {\n
      this.$element.trigger(e)\n
      if (e.isDefaultPrevented()) return\n
      $active.removeClass(\'active\')\n
      $next.addClass(\'active\')\n
      this.sliding = false\n
      this.$element.trigger(\'slid.bs.carousel\')\n
    }\n
\n
    isCycling && this.cycle()\n
\n
    return this\n
  }\n
\n
\n
  // CAROUSEL PLUGIN DEFINITION\n
  // ==========================\n
\n
  var old = $.fn.carousel\n
\n
  $.fn.carousel = function (option) {\n
    return this.each(function () {\n
      var $this   = $(this)\n
      var data    = $this.data(\'bs.carousel\')\n
      var options = $.extend({}, Carousel.DEFAULTS, $this.data(), typeof option == \'object\' && option)\n
      var action  = typeof option == \'string\' ? option : options.slide\n
\n
      if (!data) $this.data(\'bs.carousel\', (data = new Carousel(this, options)))\n
      if (typeof option == \'number\') data.to(option)\n
      else if (action) data[action]()\n
      else if (options.interval) data.pause().cycle()\n
    })\n
  }\n
\n
  $.fn.carousel.Constructor = Carousel\n
\n
\n
  // CAROUSEL NO CONFLICT\n
  // ====================\n
\n
  $.fn.carousel.noConflict = function () {\n
    $.fn.carousel = old\n
    return this\n
  }\n
\n
\n
  // CAROUSEL DATA-API\n
  // =================\n
\n
  $(document).on(\'click.bs.carousel.data-api\', \'[data-slide], [data-slide-to]\', function (e) {\n
    var $this   = $(this), href\n
    var $target = $($this.attr(\'data-target\') || (href = $this.attr(\'href\')) && href.replace(/.*(?=#[^\\s]+$)/, \'\')) //strip for ie7\n
    var options = $.extend({}, $target.data(), $this.data())\n
    var slideIndex = $this.attr(\'data-slide-to\')\n
    if (slideIndex) options.interval = false\n
\n
    $target.carousel(options)\n
\n
    if (slideIndex = $this.attr(\'data-slide-to\')) {\n
      $target.data(\'bs.carousel\').to(slideIndex)\n
    }\n
\n
    e.preventDefault()\n
  })\n
\n
  $(window).on(\'load\', function () {\n
    $(\'[data-ride="carousel"]\').each(function () {\n
      var $carousel = $(this)\n
      $carousel.carousel($carousel.data())\n
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
            <value> <int>6493</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
