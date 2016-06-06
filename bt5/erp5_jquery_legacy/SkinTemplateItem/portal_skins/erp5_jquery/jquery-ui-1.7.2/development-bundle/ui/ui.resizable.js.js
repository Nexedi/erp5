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
            <value> <string>ts65545394.56</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ui.resizable.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Resizable 1.7.2\n
 *\n
 * Copyright (c) 2009 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Resizables\n
 *\n
 * Depends:\n
 *\tui.core.js\n
 */\n
(function($) {\n
\n
$.widget("ui.resizable", $.extend({}, $.ui.mouse, {\n
\n
\t_init: function() {\n
\n
\t\tvar self = this, o = this.options;\n
\t\tthis.element.addClass("ui-resizable");\n
\n
\t\t$.extend(this, {\n
\t\t\t_aspectRatio: !!(o.aspectRatio),\n
\t\t\taspectRatio: o.aspectRatio,\n
\t\t\toriginalElement: this.element,\n
\t\t\t_proportionallyResizeElements: [],\n
\t\t\t_helper: o.helper || o.ghost || o.animate ? o.helper || \'ui-resizable-helper\' : null\n
\t\t});\n
\n
\t\t//Wrap the element if it cannot hold child nodes\n
\t\tif(this.element[0].nodeName.match(/canvas|textarea|input|select|button|img/i)) {\n
\n
\t\t\t//Opera fix for relative positioning\n
\t\t\tif (/relative/.test(this.element.css(\'position\')) && $.browser.opera)\n
\t\t\t\tthis.element.css({ position: \'relative\', top: \'auto\', left: \'auto\' });\n
\n
\t\t\t//Create a wrapper element and set the wrapper to the new current internal element\n
\t\t\tthis.element.wrap(\n
\t\t\t\t$(\'<div class="ui-wrapper" style="overflow: hidden;"></div>\').css({\n
\t\t\t\t\tposition: this.element.css(\'position\'),\n
\t\t\t\t\twidth: this.element.outerWidth(),\n
\t\t\t\t\theight: this.element.outerHeight(),\n
\t\t\t\t\ttop: this.element.css(\'top\'),\n
\t\t\t\t\tleft: this.element.css(\'left\')\n
\t\t\t\t})\n
\t\t\t);\n
\n
\t\t\t//Overwrite the original this.element\n
\t\t\tthis.element = this.element.parent().data(\n
\t\t\t\t"resizable", this.element.data(\'resizable\')\n
\t\t\t);\n
\n
\t\t\tthis.elementIsWrapper = true;\n
\n
\t\t\t//Move margins to the wrapper\n
\t\t\tthis.element.css({ marginLeft: this.originalElement.css("marginLeft"), marginTop: this.originalElement.css("marginTop"), marginRight: this.originalElement.css("marginRight"), marginBottom: this.originalElement.css("marginBottom") });\n
\t\t\tthis.originalElement.css({ marginLeft: 0, marginTop: 0, marginRight: 0, marginBottom: 0});\n
\n
\t\t\t//Prevent Safari textarea resize\n
\t\t\tthis.originalResizeStyle = this.originalElement.css(\'resize\');\n
\t\t\tthis.originalElement.css(\'resize\', \'none\');\n
\n
\t\t\t//Push the actual element to our proportionallyResize internal array\n
\t\t\tthis._proportionallyResizeElements.push(this.originalElement.css({ position: \'static\', zoom: 1, display: \'block\' }));\n
\n
\t\t\t// avoid IE jump (hard set the margin)\n
\t\t\tthis.originalElement.css({ margin: this.originalElement.css(\'margin\') });\n
\n
\t\t\t// fix handlers offset\n
\t\t\tthis._proportionallyResize();\n
\n
\t\t}\n
\n
\t\tthis.handles = o.handles || (!$(\'.ui-resizable-handle\', this.element).length ? "e,s,se" : { n: \'.ui-resizable-n\', e: \'.ui-resizable-e\', s: \'.ui-resizable-s\', w: \'.ui-resizable-w\', se: \'.ui-resizable-se\', sw: \'.ui-resizable-sw\', ne: \'.ui-resizable-ne\', nw: \'.ui-resizable-nw\' });\n
\t\tif(this.handles.constructor == String) {\n
\n
\t\t\tif(this.handles == \'all\') this.handles = \'n,e,s,w,se,sw,ne,nw\';\n
\t\t\tvar n = this.handles.split(","); this.handles = {};\n
\n
\t\t\tfor(var i = 0; i < n.length; i++) {\n
\n
\t\t\t\tvar handle = $.trim(n[i]), hname = \'ui-resizable-\'+handle;\n
\t\t\t\tvar axis = $(\'<div class="ui-resizable-handle \' + hname + \'"></div>\');\n
\n
\t\t\t\t// increase zIndex of sw, se, ne, nw axis\n
\t\t\t\t//TODO : this modifies original option\n
\t\t\t\tif(/sw|se|ne|nw/.test(handle)) axis.css({ zIndex: ++o.zIndex });\n
\n
\t\t\t\t//TODO : What\'s going on here?\n
\t\t\t\tif (\'se\' == handle) {\n
\t\t\t\t\taxis.addClass(\'ui-icon ui-icon-gripsmall-diagonal-se\');\n
\t\t\t\t};\n
\n
\t\t\t\t//Insert into internal handles object and append to element\n
\t\t\t\tthis.handles[handle] = \'.ui-resizable-\'+handle;\n
\t\t\t\tthis.element.append(axis);\n
\t\t\t}\n
\n
\t\t}\n
\n
\t\tthis._renderAxis = function(target) {\n
\n
\t\t\ttarget = target || this.element;\n
\n
\t\t\tfor(var i in this.handles) {\n
\n
\t\t\t\tif(this.handles[i].constructor == String)\n
\t\t\t\t\tthis.handles[i] = $(this.handles[i], this.element).show();\n
\n
\t\t\t\t//Apply pad to wrapper element, needed to fix axis position (textarea, inputs, scrolls)\n
\t\t\t\tif (this.elementIsWrapper && this.originalElement[0].nodeName.match(/textarea|input|select|button/i)) {\n
\n
\t\t\t\t\tvar axis = $(this.handles[i], this.element), padWrapper = 0;\n
\n
\t\t\t\t\t//Checking the correct pad and border\n
\t\t\t\t\tpadWrapper = /sw|ne|nw|se|n|s/.test(i) ? axis.outerHeight() : axis.outerWidth();\n
\n
\t\t\t\t\t//The padding type i have to apply...\n
\t\t\t\t\tvar padPos = [ \'padding\',\n
\t\t\t\t\t\t/ne|nw|n/.test(i) ? \'Top\' :\n
\t\t\t\t\t\t/se|sw|s/.test(i) ? \'Bottom\' :\n
\t\t\t\t\t\t/^e$/.test(i) ? \'Right\' : \'Left\' ].join("");\n
\n
\t\t\t\t\ttarget.css(padPos, padWrapper);\n
\n
\t\t\t\t\tthis._proportionallyResize();\n
\n
\t\t\t\t}\n
\n
\t\t\t\t//TODO: What\'s that good for? There\'s not anything to be executed left\n
\t\t\t\tif(!$(this.handles[i]).length)\n
\t\t\t\t\tcontinue;\n
\n
\t\t\t}\n
\t\t};\n
\n
\t\t//TODO: make renderAxis a prototype function\n
\t\tthis._renderAxis(this.element);\n
\n
\t\tthis._handles = $(\'.ui-resizable-handle\', this.element)\n
\t\t\t.disableSelection();\n
\n
\t\t//Matching axis name\n
\t\tthis._handles.mouseover(function() {\n
\t\t\tif (!self.resizing) {\n
\t\t\t\tif (this.className)\n
\t\t\t\t\tvar axis = this.className.match(/ui-resizable-(se|sw|ne|nw|n|e|s|w)/i);\n
\t\t\t\t//Axis, default = se\n
\t\t\t\tself.axis = axis && axis[1] ? axis[1] : \'se\';\n
\t\t\t}\n
\t\t});\n
\n
\t\t//If we want to auto hide the elements\n
\t\tif (o.autoHide) {\n
\t\t\tthis._handles.hide();\n
\t\t\t$(this.element)\n
\t\t\t\t.addClass("ui-resizable-autohide")\n
\t\t\t\t.hover(function() {\n
\t\t\t\t\t$(this).removeClass("ui-resizable-autohide");\n
\t\t\t\t\tself._handles.show();\n
\t\t\t\t},\n
\t\t\t\tfunction(){\n
\t\t\t\t\tif (!self.resizing) {\n
\t\t\t\t\t\t$(this).addClass("ui-resizable-autohide");\n
\t\t\t\t\t\tself._handles.hide();\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t}\n
\n
\t\t//Initialize the mouse interaction\n
\t\tthis._mouseInit();\n
\n
\t},\n
\n
\tdestroy: function() {\n
\n
\t\tthis._mouseDestroy();\n
\n
\t\tvar _destroy = function(exp) {\n
\t\t\t$(exp).removeClass("ui-resizable ui-resizable-disabled ui-resizable-resizing")\n
\t\t\t\t.removeData("resizable").unbind(".resizable").find(\'.ui-resizable-handle\').remove();\n
\t\t};\n
\n
\t\t//TODO: Unwrap at same DOM position\n
\t\tif (this.elementIsWrapper) {\n
\t\t\t_destroy(this.element);\n
\t\t\tvar wrapper = this.element;\n
\t\t\twrapper.parent().append(\n
\t\t\t\tthis.originalElement.css({\n
\t\t\t\t\tposition: wrapper.css(\'position\'),\n
\t\t\t\t\twidth: wrapper.outerWidth(),\n
\t\t\t\t\theight: wrapper.outerHeight(),\n
\t\t\t\t\ttop: wrapper.css(\'top\'),\n
\t\t\t\t\tleft: wrapper.css(\'left\')\n
\t\t\t\t})\n
\t\t\t).end().remove();\n
\t\t}\n
\n
\t\tthis.originalElement.css(\'resize\', this.originalResizeStyle);\n
\t\t_destroy(this.originalElement);\n
\n
\t},\n
\n
\t_mouseCapture: function(event) {\n
\n
\t\tvar handle = false;\n
\t\tfor(var i in this.handles) {\n
\t\t\tif($(this.handles[i])[0] == event.target) handle = true;\n
\t\t}\n
\n
\t\treturn this.options.disabled || !!handle;\n
\n
\t},\n
\n
\t_mouseStart: function(event) {\n
\n
\t\tvar o = this.options, iniPos = this.element.position(), el = this.element;\n
\n
\t\tthis.resizing = true;\n
\t\tthis.documentScroll = { top: $(document).scrollTop(), left: $(document).scrollLeft() };\n
\n
\t\t// bugfix for http://dev.jquery.com/ticket/1749\n
\t\tif (el.is(\'.ui-draggable\') || (/absolute/).test(el.css(\'position\'))) {\n
\t\t\tel.css({ position: \'absolute\', top: iniPos.top, left: iniPos.left });\n
\t\t}\n
\n
\t\t//Opera fixing relative position\n
\t\tif ($.browser.opera && (/relative/).test(el.css(\'position\')))\n
\t\t\tel.css({ position: \'relative\', top: \'auto\', left: \'auto\' });\n
\n
\t\tthis._renderProxy();\n
\n
\t\tvar curleft = num(this.helper.css(\'left\')), curtop = num(this.helper.css(\'top\'));\n
\n
\t\tif (o.containment) {\n
\t\t\tcurleft += $(o.containment).scrollLeft() || 0;\n
\t\t\tcurtop += $(o.containment).scrollTop() || 0;\n
\t\t}\n
\n
\t\t//Store needed variables\n
\t\tthis.offset = this.helper.offset();\n
\t\tthis.position = { left: curleft, top: curtop };\n
\t\tthis.size = this._helper ? { width: el.outerWidth(), height: el.outerHeight() } : { width: el.width(), height: el.height() };\n
\t\tthis.originalSize = this._helper ? { width: el.outerWidth(), height: el.outerHeight() } : { width: el.width(), height: el.height() };\n
\t\tthis.originalPosition = { left: curleft, top: curtop };\n
\t\tthis.sizeDiff = { width: el.outerWidth() - el.width(), height: el.outerHeight() - el.height() };\n
\t\tthis.originalMousePosition = { left: event.pageX, top: event.pageY };\n
\n
\t\t//Aspect Ratio\n
\t\tthis.aspectRatio = (typeof o.aspectRatio == \'number\') ? o.aspectRatio : ((this.originalSize.width / this.originalSize.height) || 1);\n
\n
\t    var cursor = $(\'.ui-resizable-\' + this.axis).css(\'cursor\');\n
\t    $(\'body\').css(\'cursor\', cursor == \'auto\' ? this.axis + \'-resize\' : cursor);\n
\n
\t\tel.addClass("ui-resizable-resizing");\n
\t\tthis._propagate("start", event);\n
\t\treturn true;\n
\t},\n
\n
\t_mouseDrag: function(event) {\n
\n
\t\t//Increase performance, avoid regex\n
\t\tvar el = this.helper, o = this.options, props = {},\n
\t\t\tself = this, smp = this.originalMousePosition, a = this.axis;\n
\n
\t\tvar dx = (event.pageX-smp.left)||0, dy = (event.pageY-smp.top)||0;\n
\t\tvar trigger = this._change[a];\n
\t\tif (!trigger) return false;\n
\n
\t\t// Calculate the attrs that will be change\n
\t\tvar data = trigger.apply(this, [event, dx, dy]), ie6 = $.browser.msie && $.browser.version < 7, csdif = this.sizeDiff;\n
\n
\t\tif (this._aspectRatio || event.shiftKey)\n
\t\t\tdata = this._updateRatio(data, event);\n
\n
\t\tdata = this._respectSize(data, event);\n
\n
\t\t// plugins callbacks need to be called first\n
\t\tthis._propagate("resize", event);\n
\n
\t\tel.css({\n
\t\t\ttop: this.position.top + "px", left: this.position.left + "px",\n
\t\t\twidth: this.size.width + "px", height: this.size.height + "px"\n
\t\t});\n
\n
\t\tif (!this._helper && this._proportionallyResizeElements.length)\n
\t\t\tthis._proportionallyResize();\n
\n
\t\tthis._updateCache(data);\n
\n
\t\t// calling the user callback at the end\n
\t\tthis._trigger(\'resize\', event, this.ui());\n
\n
\t\treturn false;\n
\t},\n
\n
\t_mouseStop: function(event) {\n
\n
\t\tthis.resizing = false;\n
\t\tvar o = this.options, self = this;\n
\n
\t\tif(this._helper) {\n
\t\t\tvar pr = this._proportionallyResizeElements, ista = pr.length && (/textarea/i).test(pr[0].nodeName),\n
\t\t\t\t\t\tsoffseth = ista && $.ui.hasScroll(pr[0], \'left\') /* TODO - jump height */ ? 0 : self.sizeDiff.height,\n
\t\t\t\t\t\t\tsoffsetw = ista ? 0 : self.sizeDiff.width;\n
\n
\t\t\tvar s = { width: (self.size.width - soffsetw), height: (self.size.height - soffseth) },\n
\t\t\t\tleft = (parseInt(self.element.css(\'left\'), 10) + (self.position.left - self.originalPosition.left)) || null,\n
\t\t\t\ttop = (parseInt(self.element.css(\'top\'), 10) + (self.position.top - self.originalPosition.top)) || null;\n
\n
\t\t\tif (!o.animate)\n
\t\t\t\tthis.element.css($.extend(s, { top: top, left: left }));\n
\n
\t\t\tself.helper.height(self.size.height);\n
\t\t\tself.helper.width(self.size.width);\n
\n
\t\t\tif (this._helper && !o.animate) this._proportionallyResize();\n
\t\t}\n
\n
\t\t$(\'body\').css(\'cursor\', \'auto\');\n
\n
\t\tthis.element.removeClass("ui-resizable-resizing");\n
\n
\t\tthis._propagate("stop", event);\n
\n
\t\tif (this._helper) this.helper.remove();\n
\t\treturn false;\n
\n
\t},\n
\n
\t_updateCache: function(data) {\n
\t\tvar o = this.options;\n
\t\tthis.offset = this.helper.offset();\n
\t\tif (isNumber(data.left)) this.position.left = data.left;\n
\t\tif (isNumber(data.top)) this.position.top = data.top;\n
\t\tif (isNumber(data.height)) this.size.height = data.height;\n
\t\tif (isNumber(data.width)) this.size.width = data.width;\n
\t},\n
\n
\t_updateRatio: function(data, event) {\n
\n
\t\tvar o = this.options, cpos = this.position, csize = this.size, a = this.axis;\n
\n
\t\tif (data.height) data.width = (csize.height * this.aspectRatio);\n
\t\telse if (data.width) data.height = (csize.width / this.aspectRatio);\n
\n
\t\tif (a == \'sw\') {\n
\t\t\tdata.left = cpos.left + (csize.width - data.width);\n
\t\t\tdata.top = null;\n
\t\t}\n
\t\tif (a == \'nw\') {\n
\t\t\tdata.top = cpos.top + (csize.height - data.height);\n
\t\t\tdata.left = cpos.left + (csize.width - data.width);\n
\t\t}\n
\n
\t\treturn data;\n
\t},\n
\n
\t_respectSize: function(data, event) {\n
\n
\t\tvar el = this.helper, o = this.options, pRatio = this._aspectRatio || event.shiftKey, a = this.axis,\n
\t\t\t\tismaxw = isNumber(data.width) && o.maxWidth && (o.maxWidth < data.width), ismaxh = isNumber(data.height) && o.maxHeight && (o.maxHeight < data.height),\n
\t\t\t\t\tisminw = isNumber(data.width) && o.minWidth && (o.minWidth > data.width), isminh = isNumber(data.height) && o.minHeight && (o.minHeight > data.height);\n
\n
\t\tif (isminw) data.width = o.minWidth;\n
\t\tif (isminh) data.height = o.minHeight;\n
\t\tif (ismaxw) data.width = o.maxWidth;\n
\t\tif (ismaxh) data.height = o.maxHeight;\n
\n
\t\tvar dw = this.originalPosition.left + this.originalSize.width, dh = this.position.top + this.size.height;\n
\t\tvar cw = /sw|nw|w/.test(a), ch = /nw|ne|n/.test(a);\n
\n
\t\tif (isminw && cw) data.left = dw - o.minWidth;\n
\t\tif (ismaxw && cw) data.left = dw - o.maxWidth;\n
\t\tif (isminh && ch)\tdata.top = dh - o.minHeight;\n
\t\tif (ismaxh && ch)\tdata.top = dh - o.maxHeight;\n
\n
\t\t// fixing jump error on top/left - bug #2330\n
\t\tvar isNotwh = !data.width && !data.height;\n
\t\tif (isNotwh && !data.left && data.top) data.top = null;\n
\t\telse if (isNotwh && !data.top && data.left) data.left = null;\n
\n
\t\treturn data;\n
\t},\n
\n
\t_proportionallyResize: function() {\n
\n
\t\tvar o = this.options;\n
\t\tif (!this._proportionallyResizeElements.length) return;\n
\t\tvar element = this.helper || this.element;\n
\n
\t\tfor (var i=0; i < this._proportionallyResizeElements.length; i++) {\n
\n
\t\t\tvar prel = this._proportionallyResizeElements[i];\n
\n
\t\t\tif (!this.borderDif) {\n
\t\t\t\tvar b = [prel.css(\'borderTopWidth\'), prel.css(\'borderRightWidth\'), prel.css(\'borderBottomWidth\'), prel.css(\'borderLeftWidth\')],\n
\t\t\t\t\tp = [prel.css(\'paddingTop\'), prel.css(\'paddingRight\'), prel.css(\'paddingBottom\'), prel.css(\'paddingLeft\')];\n
\n
\t\t\t\tthis.borderDif = $.map(b, function(v, i) {\n
\t\t\t\t\tvar border = parseInt(v,10)||0, padding = parseInt(p[i],10)||0;\n
\t\t\t\t\treturn border + padding;\n
\t\t\t\t});\n
\t\t\t}\n
\n
\t\t\tif ($.browser.msie && !(!($(element).is(\':hidden\') || $(element).parents(\':hidden\').length)))\n
\t\t\t\tcontinue;\n
\n
\t\t\tprel.css({\n
\t\t\t\theight: (element.height() - this.borderDif[0] - this.borderDif[2]) || 0,\n
\t\t\t\twidth: (element.width() - this.borderDif[1] - this.borderDif[3]) || 0\n
\t\t\t});\n
\n
\t\t};\n
\n
\t},\n
\n
\t_renderProxy: function() {\n
\n
\t\tvar el = this.element, o = this.options;\n
\t\tthis.elementOffset = el.offset();\n
\n
\t\tif(this._helper) {\n
\n
\t\t\tthis.helper = this.helper || $(\'<div style="overflow:hidden;"></div>\');\n
\n
\t\t\t// fix ie6 offset TODO: This seems broken\n
\t\t\tvar ie6 = $.browser.msie && $.browser.version < 7, ie6offset = (ie6 ? 1 : 0),\n
\t\t\tpxyoffset = ( ie6 ? 2 : -1 );\n
\n
\t\t\tthis.helper.addClass(this._helper).css({\n
\t\t\t\twidth: this.element.outerWidth() + pxyoffset,\n
\t\t\t\theight: this.element.outerHeight() + pxyoffset,\n
\t\t\t\tposition: \'absolute\',\n
\t\t\t\tleft: this.elementOffset.left - ie6offset +\'px\',\n
\t\t\t\ttop: this.elementOffset.top - ie6offset +\'px\',\n
\t\t\t\tzIndex: ++o.zIndex //TODO: Don\'t modify option\n
\t\t\t});\n
\n
\t\t\tthis.helper\n
\t\t\t\t.appendTo("body")\n
\t\t\t\t.disableSelection();\n
\n
\t\t} else {\n
\t\t\tthis.helper = this.element;\n
\t\t}\n
\n
\t},\n
\n
\t_change: {\n
\t\te: function(event, dx, dy) {\n
\t\t\treturn { width: this.originalSize.width + dx };\n
\t\t},\n
\t\tw: function(event, dx, dy) {\n
\t\t\tvar o = this.options, cs = this.originalSize, sp = this.originalPosition;\n
\t\t\treturn { left: sp.left + dx, width: cs.width - dx };\n
\t\t},\n
\t\tn: function(event, dx, dy) {\n
\t\t\tvar o = this.options, cs = this.originalSize, sp = this.originalPosition;\n
\t\t\treturn { top: sp.top + dy, height: cs.height - dy };\n
\t\t},\n
\t\ts: function(event, dx, dy) {\n
\t\t\treturn { height: this.originalSize.height + dy };\n
\t\t},\n
\t\tse: function(event, dx, dy) {\n
\t\t\treturn $.extend(this._change.s.apply(this, arguments), this._change.e.apply(this, [event, dx, dy]));\n
\t\t},\n
\t\tsw: function(event, dx, dy) {\n
\t\t\treturn $.extend(this._change.s.apply(this, arguments), this._change.w.apply(this, [event, dx, dy]));\n
\t\t},\n
\t\tne: function(event, dx, dy) {\n
\t\t\treturn $.extend(this._change.n.apply(this, arguments), this._change.e.apply(this, [event, dx, dy]));\n
\t\t},\n
\t\tnw: function(event, dx, dy) {\n
\t\t\treturn $.extend(this._change.n.apply(this, arguments), this._change.w.apply(this, [event, dx, dy]));\n
\t\t}\n
\t},\n
\n
\t_propagate: function(n, event) {\n
\t\t$.ui.plugin.call(this, n, [event, this.ui()]);\n
\t\t(n != "resize" && this._trigger(n, event, this.ui()));\n
\t},\n
\n
\tplugins: {},\n
\n
\tui: function() {\n
\t\treturn {\n
\t\t\toriginalElement: this.originalElement,\n
\t\t\telement: this.element,\n
\t\t\thelper: this.helper,\n
\t\t\tposition: this.position,\n
\t\t\tsize: this.size,\n
\t\t\toriginalSize: this.originalSize,\n
\t\t\toriginalPosition: this.originalPosition\n
\t\t};\n
\t}\n
\n
}));\n
\n
$.extend($.ui.resizable, {\n
\tversion: "1.7.2",\n
\teventPrefix: "resize",\n
\tdefaults: {\n
\t\talsoResize: false,\n
\t\tanimate: false,\n
\t\tanimateDuration: "slow",\n
\t\tanimateEasing: "swing",\n
\t\taspectRatio: false,\n
\t\tautoHide: false,\n
\t\tcancel: ":input,option",\n
\t\tcontainment: false,\n
\t\tdelay: 0,\n
\t\tdistance: 1,\n
\t\tghost: false,\n
\t\tgrid: false,\n
\t\thandles: "e,s,se",\n
\t\thelper: false,\n
\t\tmaxHeight: null,\n
\t\tmaxWidth: null,\n
\t\tminHeight: 10,\n
\t\tminWidth: 10,\n
\t\tzIndex: 1000\n
\t}\n
});\n
\n
/*\n
 * Resizable Extensions\n
 */\n
\n
$.ui.plugin.add("resizable", "alsoResize", {\n
\n
\tstart: function(event, ui) {\n
\n
\t\tvar self = $(this).data("resizable"), o = self.options;\n
\n
\t\t_store = function(exp) {\n
\t\t\t$(exp).each(function() {\n
\t\t\t\t$(this).data("resizable-alsoresize", {\n
\t\t\t\t\twidth: parseInt($(this).width(), 10), height: parseInt($(this).height(), 10),\n
\t\t\t\t\tleft: parseInt($(this).css(\'left\'), 10), top: parseInt($(this).css(\'top\'), 10)\n
\t\t\t\t});\n
\t\t\t});\n
\t\t};\n
\n
\t\tif (typeof(o.alsoResize) == \'object\' && !o.alsoResize.parentNode) {\n
\t\t\tif (o.alsoResize.length) { o.alsoResize = o.alsoResize[0];\t_store(o.alsoResize); }\n
\t\t\telse { $.each(o.alsoResize, function(exp, c) { _store(exp); }); }\n
\t\t}else{\n
\t\t\t_store(o.alsoResize);\n
\t\t}\n
\t},\n
\n
\tresize: function(event, ui){\n
\t\tvar self = $(this).data("resizable"), o = self.options, os = self.originalSize, op = self.originalPosition;\n
\n
\t\tvar delta = {\n
\t\t\theight: (self.size.height - os.height) || 0, width: (self.size.width - os.width) || 0,\n
\t\t\ttop: (self.position.top - op.top) || 0, left: (self.position.left - op.left) || 0\n
\t\t},\n
\n
\t\t_alsoResize = function(exp, c) {\n
\t\t\t$(exp).each(function() {\n
\t\t\t\tvar el = $(this), start = $(this).data("resizable-alsoresize"), style = {}, css = c && c.length ? c : [\'width\', \'height\', \'top\', \'left\'];\n
\n
\t\t\t\t$.each(css || [\'width\', \'height\', \'top\', \'left\'], function(i, prop) {\n
\t\t\t\t\tvar sum = (start[prop]||0) + (delta[prop]||0);\n
\t\t\t\t\tif (sum && sum >= 0)\n
\t\t\t\t\t\tstyle[prop] = sum || null;\n
\t\t\t\t});\n
\n
\t\t\t\t//Opera fixing relative position\n
\t\t\t\tif (/relative/.test(el.css(\'position\')) && $.browser.opera) {\n
\t\t\t\t\tself._revertToRelativePosition = true;\n
\t\t\t\t\tel.css({ position: \'absolute\', top: \'auto\', left: \'auto\' });\n
\t\t\t\t}\n
\n
\t\t\t\tel.css(style);\n
\t\t\t});\n
\t\t};\n
\n
\t\tif (typeof(o.alsoResize) == \'object\' && !o.alsoResize.nodeType) {\n
\t\t\t$.each(o.alsoResize, function(exp, c) { _alsoResize(exp, c); });\n
\t\t}else{\n
\t\t\t_alsoResize(o.alsoResize);\n
\t\t}\n
\t},\n
\n
\tstop: function(event, ui){\n
\t\tvar self = $(this).data("resizable");\n
\n
\t\t//Opera fixing relative position\n
\t\tif (self._revertToRelativePosition && $.browser.opera) {\n
\t\t\tself._revertToRelativePosition = false;\n
\t\t\tel.css({ position: \'relative\' });\n
\t\t}\n
\n
\t\t$(this).removeData("resizable-alsoresize-start");\n
\t}\n
});\n
\n
$.ui.plugin.add("resizable", "animate", {\n
\n
\tstop: function(event, ui) {\n
\t\tvar self = $(this).data("resizable"), o = self.options;\n
\n
\t\tvar pr = self._proportionallyResizeElements, ista = pr.length && (/textarea/i).test(pr[0].nodeName),\n
\t\t\t\t\tsoffseth = ista && $.ui.hasScroll(pr[0], \'left\') /* TODO - jump height */ ? 0 : self.sizeDiff.height,\n
\t\t\t\t\t\tsoffsetw = ista ? 0 : self.sizeDiff.width;\n
\n
\t\tvar style = { width: (self.size.width - soffsetw), height: (self.size.height - soffseth) },\n
\t\t\t\t\tleft = (parseInt(self.element.css(\'left\'), 10) + (self.position.left - self.originalPosition.left)) || null,\n
\t\t\t\t\t\ttop = (parseInt(self.element.css(\'top\'), 10) + (self.position.top - self.originalPosition.top)) || null;\n
\n
\t\tself.element.animate(\n
\t\t\t$.extend(style, top && left ? { top: top, left: left } : {}), {\n
\t\t\t\tduration: o.animateDuration,\n
\t\t\t\teasing: o.animateEasing,\n
\t\t\t\tstep: function() {\n
\n
\t\t\t\t\tvar data = {\n
\t\t\t\t\t\twidth: parseInt(self.element.css(\'width\'), 10),\n
\t\t\t\t\t\theight: parseInt(self.element.css(\'height\'), 10),\n
\t\t\t\t\t\ttop: parseInt(self.element.css(\'top\'), 10),\n
\t\t\t\t\t\tleft: parseInt(self.element.css(\'left\'), 10)\n
\t\t\t\t\t};\n
\n
\t\t\t\t\tif (pr && pr.length) $(pr[0]).css({ width: data.width, height: data.height });\n
\n
\t\t\t\t\t// propagating resize, and updating values for each animation step\n
\t\t\t\t\tself._updateCache(data);\n
\t\t\t\t\tself._propagate("resize", event);\n
\n
\t\t\t\t}\n
\t\t\t}\n
\t\t);\n
\t}\n
\n
});\n
\n
$.ui.plugin.add("resizable", "containment", {\n
\n
\tstart: function(event, ui) {\n
\t\tvar self = $(this).data("resizable"), o = self.options, el = self.element;\n
\t\tvar oc = o.containment,\tce = (oc instanceof $) ? oc.get(0) : (/parent/.test(oc)) ? el.parent().get(0) : oc;\n
\t\tif (!ce) return;\n
\n
\t\tself.containerElement = $(ce);\n
\n
\t\tif (/document/.test(oc) || oc == document) {\n
\t\t\tself.containerOffset = { left: 0, top: 0 };\n
\t\t\tself.containerPosition = { left: 0, top: 0 };\n
\n
\t\t\tself.parentData = {\n
\t\t\t\telement: $(document), left: 0, top: 0,\n
\t\t\t\twidth: $(document).width(), height: $(document).height() || document.body.parentNode.scrollHeight\n
\t\t\t};\n
\t\t}\n
\n
\t\t// i\'m a node, so compute top, left, right, bottom\n
\t\telse {\n
\t\t\tvar element = $(ce), p = [];\n
\t\t\t$([ "Top", "Right", "Left", "Bottom" ]).each(function(i, name) { p[i] = num(element.css("padding" + name)); });\n
\n
\t\t\tself.containerOffset = element.offset();\n
\t\t\tself.containerPosition = element.position();\n
\t\t\tself.containerSize = { height: (element.innerHeight() - p[3]), width: (element.innerWidth() - p[1]) };\n
\n
\t\t\tvar co = self.containerOffset, ch = self.containerSize.height,\tcw = self.containerSize.width,\n
\t\t\t\t\t\twidth = ($.ui.hasScroll(ce, "left") ? ce.scrollWidth : cw ), height = ($.ui.hasScroll(ce) ? ce.scrollHeight : ch);\n
\n
\t\t\tself.parentData = {\n
\t\t\t\telement: ce, left: co.left, top: co.top, width: width, height: height\n
\t\t\t};\n
\t\t}\n
\t},\n
\n
\tresize: function(event, ui) {\n
\t\tvar self = $(this).data("resizable"), o = self.options,\n
\t\t\t\tps = self.containerSize, co = self.containerOffset, cs = self.size, cp = self.position,\n
\t\t\t\tpRatio = self._aspectRatio || event.shiftKey, cop = { top:0, left:0 }, ce = self.containerElement;\n
\n
\t\tif (ce[0] != document && (/static/).test(ce.css(\'position\'))) cop = co;\n
\n
\t\tif (cp.left < (self._helper ? co.left : 0)) {\n
\t\t\tself.size.width = self.size.width + (self._helper ? (self.position.left - co.left) : (self.position.left - cop.left));\n
\t\t\tif (pRatio) self.size.height = self.size.width / o.aspectRatio;\n
\t\t\tself.position.left = o.helper ? co.left : 0;\n
\t\t}\n
\n
\t\tif (cp.top < (self._helper ? co.top : 0)) {\n
\t\t\tself.size.height = self.size.height + (self._helper ? (self.position.top - co.top) : self.position.top);\n
\t\t\tif (pRatio) self.size.width = self.size.height * o.aspectRatio;\n
\t\t\tself.position.top = self._helper ? co.top : 0;\n
\t\t}\n
\n
\t\tself.offset.left = self.parentData.left+self.position.left;\n
\t\tself.offset.top = self.parentData.top+self.position.top;\n
\n
\t\tvar woset = Math.abs( (self._helper ? self.offset.left - cop.left : (self.offset.left - cop.left)) + self.sizeDiff.width ),\n
\t\t\t\t\thoset = Math.abs( (self._helper ? self.offset.top - cop.top : (self.offset.top - co.top)) + self.sizeDiff.height );\n
\n
\t\tvar isParent = self.containerElement.get(0) == self.element.parent().get(0),\n
\t\t    isOffsetRelative = /relative|absolute/.test(self.containerElement.css(\'position\'));\n
\n
\t\tif(isParent && isOffsetRelative) woset -= self.parentData.left;\n
\n
\t\tif (woset + self.size.width >= self.parentData.width) {\n
\t\t\tself.size.width = self.parentData.width - woset;\n
\t\t\tif (pRatio) self.size.height = self.size.width / self.aspectRatio;\n
\t\t}\n
\n
\t\tif (hoset + self.size.height >= self.parentData.height) {\n
\t\t\tself.size.height = self.parentData.height - hoset;\n
\t\t\tif (pRatio) self.size.width = self.size.height * self.aspectRatio;\n
\t\t}\n
\t},\n
\n
\tstop: function(event, ui){\n
\t\tvar self = $(this).data("resizable"), o = self.options, cp = self.position,\n
\t\t\t\tco = self.containerOffset, cop = self.containerPosition, ce = self.containerElement;\n
\n
\t\tvar helper = $(self.helper), ho = helper.offset(), w = helper.outerWidth() - self.sizeDiff.width, h = helper.outerHeight() - self.sizeDiff.height;\n
\n
\t\tif (self._helper && !o.animate && (/relative/).test(ce.css(\'position\')))\n
\t\t\t$(this).css({ left: ho.left - cop.left - co.left, width: w, height: h });\n
\n
\t\tif (self._helper && !o.animate && (/static/).test(ce.css(\'position\')))\n
\t\t\t$(this).css({ left: ho.left - cop.left - co.left, width: w, height: h });\n
\n
\t}\n
});\n
\n
$.ui.plugin.add("resizable", "ghost", {\n
\n
\tstart: function(event, ui) {\n
\n
\t\tvar self = $(this).data("resizable"), o = self.options, cs = self.size;\n
\n
\t\tself.ghost = self.originalElement.clone();\n
\t\tself.ghost\n
\t\t\t.css({ opacity: .25, display: \'block\', position: \'relative\', height: cs.height, width: cs.width, margin: 0, left: 0, top: 0 })\n
\t\t\t.addClass(\'ui-resizable-ghost\')\n
\t\t\t.addClass(typeof o.ghost == \'string\' ? o.ghost : \'\');\n
\n
\t\tself.ghost.appendTo(self.helper);\n
\n
\t},\n
\n
\tresize: function(event, ui){\n
\t\tvar self = $(this).data("resizable"), o = self.options;\n
\t\tif (self.ghost) self.ghost.css({ position: \'relative\', height: self.size.height, width: self.size.width });\n
\t},\n
\n
\tstop: function(event, ui){\n
\t\tvar self = $(this).data("resizable"), o = self.options;\n
\t\tif (self.ghost && self.helper) self.helper.get(0).removeChild(self.ghost.get(0));\n
\t}\n
\n
});\n
\n
$.ui.plugin.add("resizable", "grid", {\n
\n
\tresize: function(event, ui) {\n
\t\tvar self = $(this).data("resizable"), o = self.options, cs = self.size, os = self.originalSize, op = self.originalPosition, a = self.axis, ratio = o._aspectRatio || event.shiftKey;\n
\t\to.grid = typeof o.grid == "number" ? [o.grid, o.grid] : o.grid;\n
\t\tvar ox = Math.round((cs.width - os.width) / (o.grid[0]||1)) * (o.grid[0]||1), oy = Math.round((cs.height - os.height) / (o.grid[1]||1)) * (o.grid[1]||1);\n
\n
\t\tif (/^(se|s|e)$/.test(a)) {\n
\t\t\tself.size.width = os.width + ox;\n
\t\t\tself.size.height = os.height + oy;\n
\t\t}\n
\t\telse if (/^(ne)$/.test(a)) {\n
\t\t\tself.size.width = os.width + ox;\n
\t\t\tself.size.height = os.height + oy;\n
\t\t\tself.position.top = op.top - oy;\n
\t\t}\n
\t\telse if (/^(sw)$/.test(a)) {\n
\t\t\tself.size.width = os.width + ox;\n
\t\t\tself.size.height = os.height + oy;\n
\t\t\tself.position.left = op.left - ox;\n
\t\t}\n
\t\telse {\n
\t\t\tself.size.width = os.width + ox;\n
\t\t\tself.size.height = os.height + oy;\n
\t\t\tself.position.top = op.top - oy;\n
\t\t\tself.position.left = op.left - ox;\n
\t\t}\n
\t}\n
\n
});\n
\n
var num = function(v) {\n
\treturn parseInt(v, 10) || 0;\n
};\n
\n
var isNumber = function(value) {\n
\treturn !isNaN(parseInt(value, 10));\n
};\n
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
            <value> <long>25904</long> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
