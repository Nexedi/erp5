<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts77895655.65</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.ui.accordion.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Accordion 1.8.2\n
 *\n
 * Copyright (c) 2010 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Accordion\n
 *\n
 * Depends:\n
 *\tjquery.ui.core.js\n
 *\tjquery.ui.widget.js\n
 */\n
(function($) {\n
\n
$.widget("ui.accordion", {\n
\toptions: {\n
\t\tactive: 0,\n
\t\tanimated: \'slide\',\n
\t\tautoHeight: true,\n
\t\tclearStyle: false,\n
\t\tcollapsible: false,\n
\t\tevent: "click",\n
\t\tfillSpace: false,\n
\t\theader: "> li > :first-child,> :not(li):even",\n
\t\ticons: {\n
\t\t\theader: "ui-icon-triangle-1-e",\n
\t\t\theaderSelected: "ui-icon-triangle-1-s"\n
\t\t},\n
\t\tnavigation: false,\n
\t\tnavigationFilter: function() {\n
\t\t\treturn this.href.toLowerCase() == location.href.toLowerCase();\n
\t\t}\n
\t},\n
\t_create: function() {\n
\n
\t\tvar o = this.options, self = this;\n
\t\tthis.running = 0;\n
\n
\t\tthis.element.addClass("ui-accordion ui-widget ui-helper-reset");\n
\t\t\n
\t\t// in lack of child-selectors in CSS we need to mark top-LIs in a UL-accordion for some IE-fix\n
\t\tthis.element.children("li").addClass("ui-accordion-li-fix");\n
\n
\t\tthis.headers = this.element.find(o.header).addClass("ui-accordion-header ui-helper-reset ui-state-default ui-corner-all")\n
\t\t\t.bind("mouseenter.accordion", function(){ $(this).addClass(\'ui-state-hover\'); })\n
\t\t\t.bind("mouseleave.accordion", function(){ $(this).removeClass(\'ui-state-hover\'); })\n
\t\t\t.bind("focus.accordion", function(){ $(this).addClass(\'ui-state-focus\'); })\n
\t\t\t.bind("blur.accordion", function(){ $(this).removeClass(\'ui-state-focus\'); });\n
\n
\t\tthis.headers\n
\t\t\t.next()\n
\t\t\t\t.addClass("ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom");\n
\n
\t\tif ( o.navigation ) {\n
\t\t\tvar current = this.element.find("a").filter(o.navigationFilter);\n
\t\t\tif ( current.length ) {\n
\t\t\t\tvar header = current.closest(".ui-accordion-header");\n
\t\t\t\tif ( header.length ) {\n
\t\t\t\t\t// anchor within header\n
\t\t\t\t\tthis.active = header;\n
\t\t\t\t} else {\n
\t\t\t\t\t// anchor within content\n
\t\t\t\t\tthis.active = current.closest(".ui-accordion-content").prev();\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\n
\t\tthis.active = this._findActive(this.active || o.active).toggleClass("ui-state-default").toggleClass("ui-state-active").toggleClass("ui-corner-all").toggleClass("ui-corner-top");\n
\t\tthis.active.next().addClass(\'ui-accordion-content-active\');\n
\n
\t\t//Append icon elements\n
\t\tthis._createIcons();\n
\n
\t\tthis.resize();\n
\n
\t\t//ARIA\n
\t\tthis.element.attr(\'role\',\'tablist\');\n
\n
\t\tthis.headers\n
\t\t\t.attr(\'role\',\'tab\')\n
\t\t\t.bind(\'keydown\', function(event) { return self._keydown(event); })\n
\t\t\t.next()\n
\t\t\t.attr(\'role\',\'tabpanel\');\n
\n
\t\tthis.headers\n
\t\t\t.not(this.active || "")\n
\t\t\t.attr(\'aria-expanded\',\'false\')\n
\t\t\t.attr("tabIndex", "-1")\n
\t\t\t.next()\n
\t\t\t.hide();\n
\n
\t\t// make sure at least one header is in the tab order\n
\t\tif (!this.active.length) {\n
\t\t\tthis.headers.eq(0).attr(\'tabIndex\',\'0\');\n
\t\t} else {\n
\t\t\tthis.active\n
\t\t\t\t.attr(\'aria-expanded\',\'true\')\n
\t\t\t\t.attr(\'tabIndex\', \'0\');\n
\t\t}\n
\n
\t\t// only need links in taborder for Safari\n
\t\tif (!$.browser.safari)\n
\t\t\tthis.headers.find(\'a\').attr(\'tabIndex\',\'-1\');\n
\n
\t\tif (o.event) {\n
\t\t\tthis.headers.bind((o.event) + ".accordion", function(event) {\n
\t\t\t\tself._clickHandler.call(self, event, this);\n
\t\t\t\tevent.preventDefault();\n
\t\t\t});\n
\t\t}\n
\n
\t},\n
\t\n
\t_createIcons: function() {\n
\t\tvar o = this.options;\n
\t\tif (o.icons) {\n
\t\t\t$("<span/>").addClass("ui-icon " + o.icons.header).prependTo(this.headers);\n
\t\t\tthis.active.find(".ui-icon").toggleClass(o.icons.header).toggleClass(o.icons.headerSelected);\n
\t\t\tthis.element.addClass("ui-accordion-icons");\n
\t\t}\n
\t},\n
\t\n
\t_destroyIcons: function() {\n
\t\tthis.headers.children(".ui-icon").remove();\n
\t\tthis.element.removeClass("ui-accordion-icons");\n
\t},\n
\n
\tdestroy: function() {\n
\t\tvar o = this.options;\n
\n
\t\tthis.element\n
\t\t\t.removeClass("ui-accordion ui-widget ui-helper-reset")\n
\t\t\t.removeAttr("role")\n
\t\t\t.unbind(\'.accordion\')\n
\t\t\t.removeData(\'accordion\');\n
\n
\t\tthis.headers\n
\t\t\t.unbind(".accordion")\n
\t\t\t.removeClass("ui-accordion-header ui-helper-reset ui-state-default ui-corner-all ui-state-active ui-corner-top")\n
\t\t\t.removeAttr("role").removeAttr("aria-expanded").removeAttr("tabIndex");\n
\n
\t\tthis.headers.find("a").removeAttr("tabIndex");\n
\t\tthis._destroyIcons();\n
\t\tvar contents = this.headers.next().css("display", "").removeAttr("role").removeClass("ui-helper-reset ui-widget-content ui-corner-bottom ui-accordion-content ui-accordion-content-active");\n
\t\tif (o.autoHeight || o.fillHeight) {\n
\t\t\tcontents.css("height", "");\n
\t\t}\n
\n
\t\treturn this;\n
\t},\n
\t\n
\t_setOption: function(key, value) {\n
\t\t$.Widget.prototype._setOption.apply(this, arguments);\n
\t\t\t\n
\t\tif (key == "active") {\n
\t\t\tthis.activate(value);\n
\t\t}\n
\t\tif (key == "icons") {\n
\t\t\tthis._destroyIcons();\n
\t\t\tif (value) {\n
\t\t\t\tthis._createIcons();\n
\t\t\t}\n
\t\t}\n
\t\t\n
\t},\n
\n
\t_keydown: function(event) {\n
\n
\t\tvar o = this.options, keyCode = $.ui.keyCode;\n
\n
\t\tif (o.disabled || event.altKey || event.ctrlKey)\n
\t\t\treturn;\n
\n
\t\tvar length = this.headers.length;\n
\t\tvar currentIndex = this.headers.index(event.target);\n
\t\tvar toFocus = false;\n
\n
\t\tswitch(event.keyCode) {\n
\t\t\tcase keyCode.RIGHT:\n
\t\t\tcase keyCode.DOWN:\n
\t\t\t\ttoFocus = this.headers[(currentIndex + 1) % length];\n
\t\t\t\tbreak;\n
\t\t\tcase keyCode.LEFT:\n
\t\t\tcase keyCode.UP:\n
\t\t\t\ttoFocus = this.headers[(currentIndex - 1 + length) % length];\n
\t\t\t\tbreak;\n
\t\t\tcase keyCode.SPACE:\n
\t\t\tcase keyCode.ENTER:\n
\t\t\t\tthis._clickHandler({ target: event.target }, event.target);\n
\t\t\t\tevent.preventDefault();\n
\t\t}\n
\n
\t\tif (toFocus) {\n
\t\t\t$(event.target).attr(\'tabIndex\',\'-1\');\n
\t\t\t$(toFocus).attr(\'tabIndex\',\'0\');\n
\t\t\ttoFocus.focus();\n
\t\t\treturn false;\n
\t\t}\n
\n
\t\treturn true;\n
\n
\t},\n
\n
\tresize: function() {\n
\n
\t\tvar o = this.options, maxHeight;\n
\n
\t\tif (o.fillSpace) {\n
\t\t\t\n
\t\t\tif($.browser.msie) { var defOverflow = this.element.parent().css(\'overflow\'); this.element.parent().css(\'overflow\', \'hidden\'); }\n
\t\t\tmaxHeight = this.element.parent().height();\n
\t\t\tif($.browser.msie) { this.element.parent().css(\'overflow\', defOverflow); }\n
\t\n
\t\t\tthis.headers.each(function() {\n
\t\t\t\tmaxHeight -= $(this).outerHeight(true);\n
\t\t\t});\n
\n
\t\t\tthis.headers.next().each(function() {\n
    \t\t   $(this).height(Math.max(0, maxHeight - $(this).innerHeight() + $(this).height()));\n
\t\t\t}).css(\'overflow\', \'auto\');\n
\n
\t\t} else if ( o.autoHeight ) {\n
\t\t\tmaxHeight = 0;\n
\t\t\tthis.headers.next().each(function() {\n
\t\t\t\tmaxHeight = Math.max(maxHeight, $(this).height());\n
\t\t\t}).height(maxHeight);\n
\t\t}\n
\n
\t\treturn this;\n
\t},\n
\n
\tactivate: function(index) {\n
\t\t// TODO this gets called on init, changing the option without an explicit call for that\n
\t\tthis.options.active = index;\n
\t\t// call clickHandler with custom event\n
\t\tvar active = this._findActive(index)[0];\n
\t\tthis._clickHandler({ target: active }, active);\n
\n
\t\treturn this;\n
\t},\n
\n
\t_findActive: function(selector) {\n
\t\treturn selector\n
\t\t\t? typeof selector == "number"\n
\t\t\t\t? this.headers.filter(":eq(" + selector + ")")\n
\t\t\t\t: this.headers.not(this.headers.not(selector))\n
\t\t\t: selector === false\n
\t\t\t\t? $([])\n
\t\t\t\t: this.headers.filter(":eq(0)");\n
\t},\n
\n
\t// TODO isn\'t event.target enough? why the seperate target argument?\n
\t_clickHandler: function(event, target) {\n
\n
\t\tvar o = this.options;\n
\t\tif (o.disabled)\n
\t\t\treturn;\n
\n
\t\t// called only when using activate(false) to close all parts programmatically\n
\t\tif (!event.target) {\n
\t\t\tif (!o.collapsible)\n
\t\t\t\treturn;\n
\t\t\tthis.active.removeClass("ui-state-active ui-corner-top").addClass("ui-state-default ui-corner-all")\n
\t\t\t\t.find(".ui-icon").removeClass(o.icons.headerSelected).addClass(o.icons.header);\n
\t\t\tthis.active.next().addClass(\'ui-accordion-content-active\');\n
\t\t\tvar toHide = this.active.next(),\n
\t\t\t\tdata = {\n
\t\t\t\t\toptions: o,\n
\t\t\t\t\tnewHeader: $([]),\n
\t\t\t\t\toldHeader: o.active,\n
\t\t\t\t\tnewContent: $([]),\n
\t\t\t\t\toldContent: toHide\n
\t\t\t\t},\n
\t\t\t\ttoShow = (this.active = $([]));\n
\t\t\tthis._toggle(toShow, toHide, data);\n
\t\t\treturn;\n
\t\t}\n
\n
\t\t// get the click target\n
\t\tvar clicked = $(event.currentTarget || target);\n
\t\tvar clickedIsActive = clicked[0] == this.active[0];\n
\t\t\n
\t\t// TODO the option is changed, is that correct?\n
\t\t// TODO if it is correct, shouldn\'t that happen after determining that the click is valid?\n
\t\to.active = o.collapsible && clickedIsActive ? false : $(\'.ui-accordion-header\', this.element).index(clicked);\n
\n
\t\t// if animations are still active, or the active header is the target, ignore click\n
\t\tif (this.running || (!o.collapsible && clickedIsActive)) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\t// switch classes\n
\t\tthis.active.removeClass("ui-state-active ui-corner-top").addClass("ui-state-default ui-corner-all")\n
\t\t\t.find(".ui-icon").removeClass(o.icons.headerSelected).addClass(o.icons.header);\n
\t\tif (!clickedIsActive) {\n
\t\t\tclicked.removeClass("ui-state-default ui-corner-all").addClass("ui-state-active ui-corner-top")\n
\t\t\t\t.find(".ui-icon").removeClass(o.icons.header).addClass(o.icons.headerSelected);\n
\t\t\tclicked.next().addClass(\'ui-accordion-content-active\');\n
\t\t}\n
\n
\t\t// find elements to show and hide\n
\t\tvar toShow = clicked.next(),\n
\t\t\ttoHide = this.active.next(),\n
\t\t\tdata = {\n
\t\t\t\toptions: o,\n
\t\t\t\tnewHeader: clickedIsActive && o.collapsible ? $([]) : clicked,\n
\t\t\t\toldHeader: this.active,\n
\t\t\t\tnewContent: clickedIsActive && o.collapsible ? $([]) : toShow,\n
\t\t\t\toldContent: toHide\n
\t\t\t},\n
\t\t\tdown = this.headers.index( this.active[0] ) > this.headers.index( clicked[0] );\n
\n
\t\tthis.active = clickedIsActive ? $([]) : clicked;\n
\t\tthis._toggle(toShow, toHide, data, clickedIsActive, down);\n
\n
\t\treturn;\n
\n
\t},\n
\n
\t_toggle: function(toShow, toHide, data, clickedIsActive, down) {\n
\n
\t\tvar o = this.options, self = this;\n
\n
\t\tthis.toShow = toShow;\n
\t\tthis.toHide = toHide;\n
\t\tthis.data = data;\n
\n
\t\tvar complete = function() { if(!self) return; return self._completed.apply(self, arguments); };\n
\n
\t\t// trigger changestart event\n
\t\tthis._trigger("changestart", null, this.data);\n
\n
\t\t// count elements to animate\n
\t\tthis.running = toHide.size() === 0 ? toShow.size() : toHide.size();\n
\n
\t\tif (o.animated) {\n
\n
\t\t\tvar animOptions = {};\n
\n
\t\t\tif ( o.collapsible && clickedIsActive ) {\n
\t\t\t\tanimOptions = {\n
\t\t\t\t\ttoShow: $([]),\n
\t\t\t\t\ttoHide: toHide,\n
\t\t\t\t\tcomplete: complete,\n
\t\t\t\t\tdown: down,\n
\t\t\t\t\tautoHeight: o.autoHeight || o.fillSpace\n
\t\t\t\t};\n
\t\t\t} else {\n
\t\t\t\tanimOptions = {\n
\t\t\t\t\ttoShow: toShow,\n
\t\t\t\t\ttoHide: toHide,\n
\t\t\t\t\tcomplete: complete,\n
\t\t\t\t\tdown: down,\n
\t\t\t\t\tautoHeight: o.autoHeight || o.fillSpace\n
\t\t\t\t};\n
\t\t\t}\n
\n
\t\t\tif (!o.proxied) {\n
\t\t\t\to.proxied = o.animated;\n
\t\t\t}\n
\n
\t\t\tif (!o.proxiedDuration) {\n
\t\t\t\to.proxiedDuration = o.duration;\n
\t\t\t}\n
\n
\t\t\to.animated = $.isFunction(o.proxied) ?\n
\t\t\t\to.proxied(animOptions) : o.proxied;\n
\n
\t\t\to.duration = $.isFunction(o.proxiedDuration) ?\n
\t\t\t\to.proxiedDuration(animOptions) : o.proxiedDuration;\n
\n
\t\t\tvar animations = $.ui.accordion.animations,\n
\t\t\t\tduration = o.duration,\n
\t\t\t\teasing = o.animated;\n
\n
\t\t\tif (easing && !animations[easing] && !$.easing[easing]) {\n
\t\t\t\teasing = \'slide\';\n
\t\t\t}\n
\t\t\tif (!animations[easing]) {\n
\t\t\t\tanimations[easing] = function(options) {\n
\t\t\t\t\tthis.slide(options, {\n
\t\t\t\t\t\teasing: easing,\n
\t\t\t\t\t\tduration: duration || 700\n
\t\t\t\t\t});\n
\t\t\t\t};\n
\t\t\t}\n
\n
\t\t\tanimations[easing](animOptions);\n
\n
\t\t} else {\n
\n
\t\t\tif (o.collapsible && clickedIsActive) {\n
\t\t\t\ttoShow.toggle();\n
\t\t\t} else {\n
\t\t\t\ttoHide.hide();\n
\t\t\t\ttoShow.show();\n
\t\t\t}\n
\n
\t\t\tcomplete(true);\n
\n
\t\t}\n
\n
\t\t// TODO assert that the blur and focus triggers are really necessary, remove otherwise\n
\t\ttoHide.prev().attr(\'aria-expanded\',\'false\').attr("tabIndex", "-1").blur();\n
\t\ttoShow.prev().attr(\'aria-expanded\',\'true\').attr("tabIndex", "0").focus();\n
\n
\t},\n
\n
\t_completed: function(cancel) {\n
\n
\t\tvar o = this.options;\n
\n
\t\tthis.running = cancel ? 0 : --this.running;\n
\t\tif (this.running) return;\n
\n
\t\tif (o.clearStyle) {\n
\t\t\tthis.toShow.add(this.toHide).css({\n
\t\t\t\theight: "",\n
\t\t\t\toverflow: ""\n
\t\t\t});\n
\t\t}\n
\t\t\n
\t\t// other classes are removed before the animation; this one needs to stay until completed\n
\t\tthis.toHide.removeClass("ui-accordion-content-active");\n
\n
\t\tthis._trigger(\'change\', null, this.data);\n
\t}\n
\n
});\n
\n
\n
$.extend($.ui.accordion, {\n
\tversion: "1.8.2",\n
\tanimations: {\n
\t\tslide: function(options, additions) {\n
\t\t\toptions = $.extend({\n
\t\t\t\teasing: "swing",\n
\t\t\t\tduration: 300\n
\t\t\t}, options, additions);\n
\t\t\tif ( !options.toHide.size() ) {\n
\t\t\t\toptions.toShow.animate({height: "show"}, options);\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\tif ( !options.toShow.size() ) {\n
\t\t\t\toptions.toHide.animate({height: "hide"}, options);\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\tvar overflow = options.toShow.css(\'overflow\'),\n
\t\t\t\tpercentDone = 0,\n
\t\t\t\tshowProps = {},\n
\t\t\t\thideProps = {},\n
\t\t\t\tfxAttrs = [ "height", "paddingTop", "paddingBottom" ],\n
\t\t\t\toriginalWidth;\n
\t\t\t// fix width before calculating height of hidden element\n
\t\t\tvar s = options.toShow;\n
\t\t\toriginalWidth = s[0].style.width;\n
\t\t\ts.width( parseInt(s.parent().width(),10) - parseInt(s.css("paddingLeft"),10) - parseInt(s.css("paddingRight"),10) - (parseInt(s.css("borderLeftWidth"),10) || 0) - (parseInt(s.css("borderRightWidth"),10) || 0) );\n
\t\t\t\n
\t\t\t$.each(fxAttrs, function(i, prop) {\n
\t\t\t\thideProps[prop] = \'hide\';\n
\t\t\t\t\n
\t\t\t\tvar parts = (\'\' + $.css(options.toShow[0], prop)).match(/^([\\d+-.]+)(.*)$/);\n
\t\t\t\tshowProps[prop] = {\n
\t\t\t\t\tvalue: parts[1],\n
\t\t\t\t\tunit: parts[2] || \'px\'\n
\t\t\t\t};\n
\t\t\t});\n
\t\t\toptions.toShow.css({ height: 0, overflow: \'hidden\' }).show();\n
\t\t\toptions.toHide.filter(":hidden").each(options.complete).end().filter(":visible").animate(hideProps,{\n
\t\t\t\tstep: function(now, settings) {\n
\t\t\t\t\t// only calculate the percent when animating height\n
\t\t\t\t\t// IE gets very inconsistent results when animating elements\n
\t\t\t\t\t// with small values, which is common for padding\n
\t\t\t\t\tif (settings.prop == \'height\') {\n
\t\t\t\t\t\tpercentDone = ( settings.end - settings.start === 0 ) ? 0 :\n
\t\t\t\t\t\t\t(settings.now - settings.start) / (settings.end - settings.start);\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\toptions.toShow[0].style[settings.prop] =\n
\t\t\t\t\t\t(percentDone * showProps[settings.prop].value) + showProps[settings.prop].unit;\n
\t\t\t\t},\n
\t\t\t\tduration: options.duration,\n
\t\t\t\teasing: options.easing,\n
\t\t\t\tcomplete: function() {\n
\t\t\t\t\tif ( !options.autoHeight ) {\n
\t\t\t\t\t\toptions.toShow.css("height", "");\n
\t\t\t\t\t}\n
\t\t\t\t\toptions.toShow.css("width", originalWidth);\n
\t\t\t\t\toptions.toShow.css({overflow: overflow});\n
\t\t\t\t\toptions.complete();\n
\t\t\t\t}\n
\t\t\t});\n
\t\t},\n
\t\tbounceslide: function(options) {\n
\t\t\tthis.slide(options, {\n
\t\t\t\teasing: options.down ? "easeOutBounce" : "swing",\n
\t\t\t\tduration: options.down ? 1000 : 200\n
\t\t\t});\n
\t\t}\n
\t}\n
});\n
\n
})(jQuery);\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>14039</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
