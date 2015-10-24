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
            <value> <string>ts44314529.0</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>modal.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* ========================================================================\n
 * Bootstrap: modal.js v3.0.3\n
 * http://getbootstrap.com/javascript/#modals\n
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
  // MODAL CLASS DEFINITION\n
  // ======================\n
\n
  var Modal = function (element, options) {\n
    this.options   = options\n
    this.$element  = $(element)\n
    this.$backdrop =\n
    this.isShown   = null\n
\n
    if (this.options.remote) this.$element.load(this.options.remote)\n
  }\n
\n
  Modal.DEFAULTS = {\n
      backdrop: true\n
    , keyboard: true\n
    , show: true\n
  }\n
\n
  Modal.prototype.toggle = function (_relatedTarget) {\n
    return this[!this.isShown ? \'show\' : \'hide\'](_relatedTarget)\n
  }\n
\n
  Modal.prototype.show = function (_relatedTarget) {\n
    var that = this\n
    var e    = $.Event(\'show.bs.modal\', { relatedTarget: _relatedTarget })\n
\n
    this.$element.trigger(e)\n
\n
    if (this.isShown || e.isDefaultPrevented()) return\n
\n
    this.isShown = true\n
\n
    this.escape()\n
\n
    this.$element.on(\'click.dismiss.modal\', \'[data-dismiss="modal"]\', $.proxy(this.hide, this))\n
\n
    this.backdrop(function () {\n
      var transition = $.support.transition && that.$element.hasClass(\'fade\')\n
\n
      if (!that.$element.parent().length) {\n
        that.$element.appendTo(document.body) // don\'t move modals dom position\n
      }\n
\n
      that.$element.show()\n
\n
      if (transition) {\n
        that.$element[0].offsetWidth // force reflow\n
      }\n
\n
      that.$element\n
        .addClass(\'in\')\n
        .attr(\'aria-hidden\', false)\n
\n
      that.enforceFocus()\n
\n
      var e = $.Event(\'shown.bs.modal\', { relatedTarget: _relatedTarget })\n
\n
      transition ?\n
        that.$element.find(\'.modal-dialog\') // wait for modal to slide in\n
          .one($.support.transition.end, function () {\n
            that.$element.focus().trigger(e)\n
          })\n
          .emulateTransitionEnd(300) :\n
        that.$element.focus().trigger(e)\n
    })\n
  }\n
\n
  Modal.prototype.hide = function (e) {\n
    if (e) e.preventDefault()\n
\n
    e = $.Event(\'hide.bs.modal\')\n
\n
    this.$element.trigger(e)\n
\n
    if (!this.isShown || e.isDefaultPrevented()) return\n
\n
    this.isShown = false\n
\n
    this.escape()\n
\n
    $(document).off(\'focusin.bs.modal\')\n
\n
    this.$element\n
      .removeClass(\'in\')\n
      .attr(\'aria-hidden\', true)\n
      .off(\'click.dismiss.modal\')\n
\n
    $.support.transition && this.$element.hasClass(\'fade\') ?\n
      this.$element\n
        .one($.support.transition.end, $.proxy(this.hideModal, this))\n
        .emulateTransitionEnd(300) :\n
      this.hideModal()\n
  }\n
\n
  Modal.prototype.enforceFocus = function () {\n
    $(document)\n
      .off(\'focusin.bs.modal\') // guard against infinite focus loop\n
      .on(\'focusin.bs.modal\', $.proxy(function (e) {\n
        if (this.$element[0] !== e.target && !this.$element.has(e.target).length) {\n
          this.$element.focus()\n
        }\n
      }, this))\n
  }\n
\n
  Modal.prototype.escape = function () {\n
    if (this.isShown && this.options.keyboard) {\n
      this.$element.on(\'keyup.dismiss.bs.modal\', $.proxy(function (e) {\n
        e.which == 27 && this.hide()\n
      }, this))\n
    } else if (!this.isShown) {\n
      this.$element.off(\'keyup.dismiss.bs.modal\')\n
    }\n
  }\n
\n
  Modal.prototype.hideModal = function () {\n
    var that = this\n
    this.$element.hide()\n
    this.backdrop(function () {\n
      that.removeBackdrop()\n
      that.$element.trigger(\'hidden.bs.modal\')\n
    })\n
  }\n
\n
  Modal.prototype.removeBackdrop = function () {\n
    this.$backdrop && this.$backdrop.remove()\n
    this.$backdrop = null\n
  }\n
\n
  Modal.prototype.backdrop = function (callback) {\n
    var that    = this\n
    var animate = this.$element.hasClass(\'fade\') ? \'fade\' : \'\'\n
\n
    if (this.isShown && this.options.backdrop) {\n
      var doAnimate = $.support.transition && animate\n
\n
      this.$backdrop = $(\'<div class="modal-backdrop \' + animate + \'" />\')\n
        .appendTo(document.body)\n
\n
      this.$element.on(\'click.dismiss.modal\', $.proxy(function (e) {\n
        if (e.target !== e.currentTarget) return\n
        this.options.backdrop == \'static\'\n
          ? this.$element[0].focus.call(this.$element[0])\n
          : this.hide.call(this)\n
      }, this))\n
\n
      if (doAnimate) this.$backdrop[0].offsetWidth // force reflow\n
\n
      this.$backdrop.addClass(\'in\')\n
\n
      if (!callback) return\n
\n
      doAnimate ?\n
        this.$backdrop\n
          .one($.support.transition.end, callback)\n
          .emulateTransitionEnd(150) :\n
        callback()\n
\n
    } else if (!this.isShown && this.$backdrop) {\n
      this.$backdrop.removeClass(\'in\')\n
\n
      $.support.transition && this.$element.hasClass(\'fade\')?\n
        this.$backdrop\n
          .one($.support.transition.end, callback)\n
          .emulateTransitionEnd(150) :\n
        callback()\n
\n
    } else if (callback) {\n
      callback()\n
    }\n
  }\n
\n
\n
  // MODAL PLUGIN DEFINITION\n
  // =======================\n
\n
  var old = $.fn.modal\n
\n
  $.fn.modal = function (option, _relatedTarget) {\n
    return this.each(function () {\n
      var $this   = $(this)\n
      var data    = $this.data(\'bs.modal\')\n
      var options = $.extend({}, Modal.DEFAULTS, $this.data(), typeof option == \'object\' && option)\n
\n
      if (!data) $this.data(\'bs.modal\', (data = new Modal(this, options)))\n
      if (typeof option == \'string\') data[option](_relatedTarget)\n
      else if (options.show) data.show(_relatedTarget)\n
    })\n
  }\n
\n
  $.fn.modal.Constructor = Modal\n
\n
\n
  // MODAL NO CONFLICT\n
  // =================\n
\n
  $.fn.modal.noConflict = function () {\n
    $.fn.modal = old\n
    return this\n
  }\n
\n
\n
  // MODAL DATA-API\n
  // ==============\n
\n
  $(document).on(\'click.bs.modal.data-api\', \'[data-toggle="modal"]\', function (e) {\n
    var $this   = $(this)\n
    var href    = $this.attr(\'href\')\n
    var $target = $($this.attr(\'data-target\') || (href && href.replace(/.*(?=#[^\\s]+$)/, \'\'))) //strip for ie7\n
    var option  = $target.data(\'modal\') ? \'toggle\' : $.extend({ remote: !/#/.test(href) && href }, $target.data(), $this.data())\n
\n
    e.preventDefault()\n
\n
    $target\n
      .modal(option, this)\n
      .one(\'hide\', function () {\n
        $this.is(\':visible\') && $this.focus()\n
      })\n
  })\n
\n
  $(document)\n
    .on(\'show.bs.modal\',  \'.modal\', function () { $(document.body).addClass(\'modal-open\') })\n
    .on(\'hidden.bs.modal\', \'.modal\', function () { $(document.body).removeClass(\'modal-open\') })\n
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
            <value> <int>6975</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
