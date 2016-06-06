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
            <value> <string>ts77895655.93</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.ui.draggable.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Draggable 1.8.2\n
 *\n
 * Copyright (c) 2010 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Draggables\n
 *\n
 * Depends:\n
 *\tjquery.ui.core.js\n
 *\tjquery.ui.mouse.js\n
 *\tjquery.ui.widget.js\n
 */\n
(function($) {\n
\n
$.widget("ui.draggable", $.ui.mouse, {\n
\twidgetEventPrefix: "drag",\n
\toptions: {\n
\t\taddClasses: true,\n
\t\tappendTo: "parent",\n
\t\taxis: false,\n
\t\tconnectToSortable: false,\n
\t\tcontainment: false,\n
\t\tcursor: "auto",\n
\t\tcursorAt: false,\n
\t\tgrid: false,\n
\t\thandle: false,\n
\t\thelper: "original",\n
\t\tiframeFix: false,\n
\t\topacity: false,\n
\t\trefreshPositions: false,\n
\t\trevert: false,\n
\t\trevertDuration: 500,\n
\t\tscope: "default",\n
\t\tscroll: true,\n
\t\tscrollSensitivity: 20,\n
\t\tscrollSpeed: 20,\n
\t\tsnap: false,\n
\t\tsnapMode: "both",\n
\t\tsnapTolerance: 20,\n
\t\tstack: false,\n
\t\tzIndex: false\n
\t},\n
\t_create: function() {\n
\n
\t\tif (this.options.helper == \'original\' && !(/^(?:r|a|f)/).test(this.element.css("position")))\n
\t\t\tthis.element[0].style.position = \'relative\';\n
\n
\t\t(this.options.addClasses && this.element.addClass("ui-draggable"));\n
\t\t(this.options.disabled && this.element.addClass("ui-draggable-disabled"));\n
\n
\t\tthis._mouseInit();\n
\n
\t},\n
\n
\tdestroy: function() {\n
\t\tif(!this.element.data(\'draggable\')) return;\n
\t\tthis.element\n
\t\t\t.removeData("draggable")\n
\t\t\t.unbind(".draggable")\n
\t\t\t.removeClass("ui-draggable"\n
\t\t\t\t+ " ui-draggable-dragging"\n
\t\t\t\t+ " ui-draggable-disabled");\n
\t\tthis._mouseDestroy();\n
\n
\t\treturn this;\n
\t},\n
\n
\t_mouseCapture: function(event) {\n
\n
\t\tvar o = this.options;\n
\n
\t\t// among others, prevent a drag on a resizable-handle\n
\t\tif (this.helper || o.disabled || $(event.target).is(\'.ui-resizable-handle\'))\n
\t\t\treturn false;\n
\n
\t\t//Quit if we\'re not on a valid handle\n
\t\tthis.handle = this._getHandle(event);\n
\t\tif (!this.handle)\n
\t\t\treturn false;\n
\n
\t\treturn true;\n
\n
\t},\n
\n
\t_mouseStart: function(event) {\n
\n
\t\tvar o = this.options;\n
\n
\t\t//Create and append the visible helper\n
\t\tthis.helper = this._createHelper(event);\n
\n
\t\t//Cache the helper size\n
\t\tthis._cacheHelperProportions();\n
\n
\t\t//If ddmanager is used for droppables, set the global draggable\n
\t\tif($.ui.ddmanager)\n
\t\t\t$.ui.ddmanager.current = this;\n
\n
\t\t/*\n
\t\t * - Position generation -\n
\t\t * This block generates everything position related - it\'s the core of draggables.\n
\t\t */\n
\n
\t\t//Cache the margins of the original element\n
\t\tthis._cacheMargins();\n
\n
\t\t//Store the helper\'s css position\n
\t\tthis.cssPosition = this.helper.css("position");\n
\t\tthis.scrollParent = this.helper.scrollParent();\n
\n
\t\t//The element\'s absolute position on the page minus margins\n
\t\tthis.offset = this.positionAbs = this.element.offset();\n
\t\tthis.offset = {\n
\t\t\ttop: this.offset.top - this.margins.top,\n
\t\t\tleft: this.offset.left - this.margins.left\n
\t\t};\n
\n
\t\t$.extend(this.offset, {\n
\t\t\tclick: { //Where the click happened, relative to the element\n
\t\t\t\tleft: event.pageX - this.offset.left,\n
\t\t\t\ttop: event.pageY - this.offset.top\n
\t\t\t},\n
\t\t\tparent: this._getParentOffset(),\n
\t\t\trelative: this._getRelativeOffset() //This is a relative to absolute position minus the actual position calculation - only used for relative positioned helper\n
\t\t});\n
\n
\t\t//Generate the original position\n
\t\tthis.originalPosition = this.position = this._generatePosition(event);\n
\t\tthis.originalPageX = event.pageX;\n
\t\tthis.originalPageY = event.pageY;\n
\n
\t\t//Adjust the mouse offset relative to the helper if \'cursorAt\' is supplied\n
\t\t(o.cursorAt && this._adjustOffsetFromHelper(o.cursorAt));\n
\n
\t\t//Set a containment if given in the options\n
\t\tif(o.containment)\n
\t\t\tthis._setContainment();\n
\n
\t\t//Trigger event + callbacks\n
\t\tif(this._trigger("start", event) === false) {\n
\t\t\tthis._clear();\n
\t\t\treturn false;\n
\t\t}\n
\n
\t\t//Recache the helper size\n
\t\tthis._cacheHelperProportions();\n
\n
\t\t//Prepare the droppable offsets\n
\t\tif ($.ui.ddmanager && !o.dropBehaviour)\n
\t\t\t$.ui.ddmanager.prepareOffsets(this, event);\n
\n
\t\tthis.helper.addClass("ui-draggable-dragging");\n
\t\tthis._mouseDrag(event, true); //Execute the drag once - this causes the helper not to be visible before getting its correct position\n
\t\treturn true;\n
\t},\n
\n
\t_mouseDrag: function(event, noPropagation) {\n
\n
\t\t//Compute the helpers position\n
\t\tthis.position = this._generatePosition(event);\n
\t\tthis.positionAbs = this._convertPositionTo("absolute");\n
\n
\t\t//Call plugins and callbacks and use the resulting position if something is returned\n
\t\tif (!noPropagation) {\n
\t\t\tvar ui = this._uiHash();\n
\t\t\tif(this._trigger(\'drag\', event, ui) === false) {\n
\t\t\t\tthis._mouseUp({});\n
\t\t\t\treturn false;\n
\t\t\t}\n
\t\t\tthis.position = ui.position;\n
\t\t}\n
\n
\t\tif(!this.options.axis || this.options.axis != "y") this.helper[0].style.left = this.position.left+\'px\';\n
\t\tif(!this.options.axis || this.options.axis != "x") this.helper[0].style.top = this.position.top+\'px\';\n
\t\tif($.ui.ddmanager) $.ui.ddmanager.drag(this, event);\n
\n
\t\treturn false;\n
\t},\n
\n
\t_mouseStop: function(event) {\n
\n
\t\t//If we are using droppables, inform the manager about the drop\n
\t\tvar dropped = false;\n
\t\tif ($.ui.ddmanager && !this.options.dropBehaviour)\n
\t\t\tdropped = $.ui.ddmanager.drop(this, event);\n
\n
\t\t//if a drop comes from outside (a sortable)\n
\t\tif(this.dropped) {\n
\t\t\tdropped = this.dropped;\n
\t\t\tthis.dropped = false;\n
\t\t}\n
\t\t\n
\t\t//if the original element is removed, don\'t bother to continue\n
\t\tif(!this.element[0] || !this.element[0].parentNode)\n
\t\t\treturn false;\n
\n
\t\tif((this.options.revert == "invalid" && !dropped) || (this.options.revert == "valid" && dropped) || this.options.revert === true || ($.isFunction(this.options.revert) && this.options.revert.call(this.element, dropped))) {\n
\t\t\tvar self = this;\n
\t\t\t$(this.helper).animate(this.originalPosition, parseInt(this.options.revertDuration, 10), function() {\n
\t\t\t\tif(self._trigger("stop", event) !== false) {\n
\t\t\t\t\tself._clear();\n
\t\t\t\t}\n
\t\t\t});\n
\t\t} else {\n
\t\t\tif(this._trigger("stop", event) !== false) {\n
\t\t\t\tthis._clear();\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn false;\n
\t},\n
\t\n
\tcancel: function() {\n
\t\t\n
\t\tif(this.helper.is(".ui-draggable-dragging")) {\n
\t\t\tthis._mouseUp({});\n
\t\t} else {\n
\t\t\tthis._clear();\n
\t\t}\n
\t\t\n
\t\treturn this;\n
\t\t\n
\t},\n
\n
\t_getHandle: function(event) {\n
\n
\t\tvar handle = !this.options.handle || !$(this.options.handle, this.element).length ? true : false;\n
\t\t$(this.options.handle, this.element)\n
\t\t\t.find("*")\n
\t\t\t.andSelf()\n
\t\t\t.each(function() {\n
\t\t\t\tif(this == event.target) handle = true;\n
\t\t\t});\n
\n
\t\treturn handle;\n
\n
\t},\n
\n
\t_createHelper: function(event) {\n
\n
\t\tvar o = this.options;\n
\t\tvar helper = $.isFunction(o.helper) ? $(o.helper.apply(this.element[0], [event])) : (o.helper == \'clone\' ? this.element.clone() : this.element);\n
\n
\t\tif(!helper.parents(\'body\').length)\n
\t\t\thelper.appendTo((o.appendTo == \'parent\' ? this.element[0].parentNode : o.appendTo));\n
\n
\t\tif(helper[0] != this.element[0] && !(/(fixed|absolute)/).test(helper.css("position")))\n
\t\t\thelper.css("position", "absolute");\n
\n
\t\treturn helper;\n
\n
\t},\n
\n
\t_adjustOffsetFromHelper: function(obj) {\n
\t\tif (typeof obj == \'string\') {\n
\t\t\tobj = obj.split(\' \');\n
\t\t}\n
\t\tif ($.isArray(obj)) {\n
\t\t\tobj = {left: +obj[0], top: +obj[1] || 0};\n
\t\t}\n
\t\tif (\'left\' in obj) {\n
\t\t\tthis.offset.click.left = obj.left + this.margins.left;\n
\t\t}\n
\t\tif (\'right\' in obj) {\n
\t\t\tthis.offset.click.left = this.helperProportions.width - obj.right + this.margins.left;\n
\t\t}\n
\t\tif (\'top\' in obj) {\n
\t\t\tthis.offset.click.top = obj.top + this.margins.top;\n
\t\t}\n
\t\tif (\'bottom\' in obj) {\n
\t\t\tthis.offset.click.top = this.helperProportions.height - obj.bottom + this.margins.top;\n
\t\t}\n
\t},\n
\n
\t_getParentOffset: function() {\n
\n
\t\t//Get the offsetParent and cache its position\n
\t\tthis.offsetParent = this.helper.offsetParent();\n
\t\tvar po = this.offsetParent.offset();\n
\n
\t\t// This is a special case where we need to modify a offset calculated on start, since the following happened:\n
\t\t// 1. The position of the helper is absolute, so it\'s position is calculated based on the next positioned parent\n
\t\t// 2. The actual offset parent is a child of the scroll parent, and the scroll parent isn\'t the document, which means that\n
\t\t//    the scroll is included in the initial calculation of the offset of the parent, and never recalculated upon drag\n
\t\tif(this.cssPosition == \'absolute\' && this.scrollParent[0] != document && $.ui.contains(this.scrollParent[0], this.offsetParent[0])) {\n
\t\t\tpo.left += this.scrollParent.scrollLeft();\n
\t\t\tpo.top += this.scrollParent.scrollTop();\n
\t\t}\n
\n
\t\tif((this.offsetParent[0] == document.body) //This needs to be actually done for all browsers, since pageX/pageY includes this information\n
\t\t|| (this.offsetParent[0].tagName && this.offsetParent[0].tagName.toLowerCase() == \'html\' && $.browser.msie)) //Ugly IE fix\n
\t\t\tpo = { top: 0, left: 0 };\n
\n
\t\treturn {\n
\t\t\ttop: po.top + (parseInt(this.offsetParent.css("borderTopWidth"),10) || 0),\n
\t\t\tleft: po.left + (parseInt(this.offsetParent.css("borderLeftWidth"),10) || 0)\n
\t\t};\n
\n
\t},\n
\n
\t_getRelativeOffset: function() {\n
\n
\t\tif(this.cssPosition == "relative") {\n
\t\t\tvar p = this.element.position();\n
\t\t\treturn {\n
\t\t\t\ttop: p.top - (parseInt(this.helper.css("top"),10) || 0) + this.scrollParent.scrollTop(),\n
\t\t\t\tleft: p.left - (parseInt(this.helper.css("left"),10) || 0) + this.scrollParent.scrollLeft()\n
\t\t\t};\n
\t\t} else {\n
\t\t\treturn { top: 0, left: 0 };\n
\t\t}\n
\n
\t},\n
\n
\t_cacheMargins: function() {\n
\t\tthis.margins = {\n
\t\t\tleft: (parseInt(this.element.css("marginLeft"),10) || 0),\n
\t\t\ttop: (parseInt(this.element.css("marginTop"),10) || 0)\n
\t\t};\n
\t},\n
\n
\t_cacheHelperProportions: function() {\n
\t\tthis.helperProportions = {\n
\t\t\twidth: this.helper.outerWidth(),\n
\t\t\theight: this.helper.outerHeight()\n
\t\t};\n
\t},\n
\n
\t_setContainment: function() {\n
\n
\t\tvar o = this.options;\n
\t\tif(o.containment == \'parent\') o.containment = this.helper[0].parentNode;\n
\t\tif(o.containment == \'document\' || o.containment == \'window\') this.containment = [\n
\t\t\t0 - this.offset.relative.left - this.offset.parent.left,\n
\t\t\t0 - this.offset.relative.top - this.offset.parent.top,\n
\t\t\t$(o.containment == \'document\' ? document : window).width() - this.helperProportions.width - this.margins.left,\n
\t\t\t($(o.containment == \'document\' ? document : window).height() || document.body.parentNode.scrollHeight) - this.helperProportions.height - this.margins.top\n
\t\t];\n
\n
\t\tif(!(/^(document|window|parent)$/).test(o.containment) && o.containment.constructor != Array) {\n
\t\t\tvar ce = $(o.containment)[0]; if(!ce) return;\n
\t\t\tvar co = $(o.containment).offset();\n
\t\t\tvar over = ($(ce).css("overflow") != \'hidden\');\n
\n
\t\t\tthis.containment = [\n
\t\t\t\tco.left + (parseInt($(ce).css("borderLeftWidth"),10) || 0) + (parseInt($(ce).css("paddingLeft"),10) || 0) - this.margins.left,\n
\t\t\t\tco.top + (parseInt($(ce).css("borderTopWidth"),10) || 0) + (parseInt($(ce).css("paddingTop"),10) || 0) - this.margins.top,\n
\t\t\t\tco.left+(over ? Math.max(ce.scrollWidth,ce.offsetWidth) : ce.offsetWidth) - (parseInt($(ce).css("borderLeftWidth"),10) || 0) - (parseInt($(ce).css("paddingRight"),10) || 0) - this.helperProportions.width - this.margins.left,\n
\t\t\t\tco.top+(over ? Math.max(ce.scrollHeight,ce.offsetHeight) : ce.offsetHeight) - (parseInt($(ce).css("borderTopWidth"),10) || 0) - (parseInt($(ce).css("paddingBottom"),10) || 0) - this.helperProportions.height - this.margins.top\n
\t\t\t];\n
\t\t} else if(o.containment.constructor == Array) {\n
\t\t\tthis.containment = o.containment;\n
\t\t}\n
\n
\t},\n
\n
\t_convertPositionTo: function(d, pos) {\n
\n
\t\tif(!pos) pos = this.position;\n
\t\tvar mod = d == "absolute" ? 1 : -1;\n
\t\tvar o = this.options, scroll = this.cssPosition == \'absolute\' && !(this.scrollParent[0] != document && $.ui.contains(this.scrollParent[0], this.offsetParent[0])) ? this.offsetParent : this.scrollParent, scrollIsRootNode = (/(html|body)/i).test(scroll[0].tagName);\n
\n
\t\treturn {\n
\t\t\ttop: (\n
\t\t\t\tpos.top\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t// The absolute mouse position\n
\t\t\t\t+ this.offset.relative.top * mod\t\t\t\t\t\t\t\t\t\t// Only for relative positioned nodes: Relative offset from element to offset parent\n
\t\t\t\t+ this.offset.parent.top * mod\t\t\t\t\t\t\t\t\t\t\t// The offsetParent\'s offset without borders (offset + border)\n
\t\t\t\t- ($.browser.safari && $.browser.version < 526 && this.cssPosition == \'fixed\' ? 0 : ( this.cssPosition == \'fixed\' ? -this.scrollParent.scrollTop() : ( scrollIsRootNode ? 0 : scroll.scrollTop() ) ) * mod)\n
\t\t\t),\n
\t\t\tleft: (\n
\t\t\t\tpos.left\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t// The absolute mouse position\n
\t\t\t\t+ this.offset.relative.left * mod\t\t\t\t\t\t\t\t\t\t// Only for relative positioned nodes: Relative offset from element to offset parent\n
\t\t\t\t+ this.offset.parent.left * mod\t\t\t\t\t\t\t\t\t\t\t// The offsetParent\'s offset without borders (offset + border)\n
\t\t\t\t- ($.browser.safari && $.browser.version < 526 && this.cssPosition == \'fixed\' ? 0 : ( this.cssPosition == \'fixed\' ? -this.scrollParent.scrollLeft() : scrollIsRootNode ? 0 : scroll.scrollLeft() ) * mod)\n
\t\t\t)\n
\t\t};\n
\n
\t},\n
\n
\t_generatePosition: function(event) {\n
\n
\t\tvar o = this.options, scroll = this.cssPosition == \'absolute\' && !(this.scrollParent[0] != document && $.ui.contains(this.scrollParent[0], this.offsetParent[0])) ? this.offsetParent : this.scrollParent, scrollIsRootNode = (/(html|body)/i).test(scroll[0].tagName);\n
\t\tvar pageX = event.pageX;\n
\t\tvar pageY = event.pageY;\n
\n
\t\t/*\n
\t\t * - Position constraining -\n
\t\t * Constrain the position to a mix of grid, containment.\n
\t\t */\n
\n
\t\tif(this.originalPosition) { //If we are not dragging yet, we won\'t check for options\n
\n
\t\t\tif(this.containment) {\n
\t\t\t\tif(event.pageX - this.offset.click.left < this.containment[0]) pageX = this.containment[0] + this.offset.click.left;\n
\t\t\t\tif(event.pageY - this.offset.click.top < this.containment[1]) pageY = this.containment[1] + this.offset.click.top;\n
\t\t\t\tif(event.pageX - this.offset.click.left > this.containment[2]) pageX = this.containment[2] + this.offset.click.left;\n
\t\t\t\tif(event.pageY - this.offset.click.top > this.containment[3]) pageY = this.containment[3] + this.offset.click.top;\n
\t\t\t}\n
\n
\t\t\tif(o.grid) {\n
\t\t\t\tvar top = this.originalPageY + Math.round((pageY - this.originalPageY) / o.grid[1]) * o.grid[1];\n
\t\t\t\tpageY = this.containment ? (!(top - this.offset.click.top < this.containment[1] || top - this.offset.click.top > this.containment[3]) ? top : (!(top - this.offset.click.top < this.containment[1]) ? top - o.grid[1] : top + o.grid[1])) : top;\n
\n
\t\t\t\tvar left = this.originalPageX + Math.round((pageX - this.originalPageX) / o.grid[0]) * o.grid[0];\n
\t\t\t\tpageX = this.containment ? (!(left - this.offset.click.left < this.containment[0] || left - this.offset.click.left > this.containment[2]) ? left : (!(left - this.offset.click.left < this.containment[0]) ? left - o.grid[0] : left + o.grid[0])) : left;\n
\t\t\t}\n
\n
\t\t}\n
\n
\t\treturn {\n
\t\t\ttop: (\n
\t\t\t\tpageY\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t// The absolute mouse position\n
\t\t\t\t- this.offset.click.top\t\t\t\t\t\t\t\t\t\t\t\t\t// Click offset (relative to the element)\n
\t\t\t\t- this.offset.relative.top\t\t\t\t\t\t\t\t\t\t\t\t// Only for relative positioned nodes: Relative offset from element to offset parent\n
\t\t\t\t- this.offset.parent.top\t\t\t\t\t\t\t\t\t\t\t\t// The offsetParent\'s offset without borders (offset + border)\n
\t\t\t\t+ ($.browser.safari && $.browser.version < 526 && this.cssPosition == \'fixed\' ? 0 : ( this.cssPosition == \'fixed\' ? -this.scrollParent.scrollTop() : ( scrollIsRootNode ? 0 : scroll.scrollTop() ) ))\n
\t\t\t),\n
\t\t\tleft: (\n
\t\t\t\tpageX\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t// The absolute mouse position\n
\t\t\t\t- this.offset.click.left\t\t\t\t\t\t\t\t\t\t\t\t// Click offset (relative to the element)\n
\t\t\t\t- this.offset.relative.left\t\t\t\t\t\t\t\t\t\t\t\t// Only for relative positioned nodes: Relative offset from element to offset parent\n
\t\t\t\t- this.offset.parent.left\t\t\t\t\t\t\t\t\t\t\t\t// The offsetParent\'s offset without borders (offset + border)\n
\t\t\t\t+ ($.browser.safari && $.browser.version < 526 && this.cssPosition == \'fixed\' ? 0 : ( this.cssPosition == \'fixed\' ? -this.scrollParent.scrollLeft() : scrollIsRootNode ? 0 : scroll.scrollLeft() ))\n
\t\t\t)\n
\t\t};\n
\n
\t},\n
\n
\t_clear: function() {\n
\t\tthis.helper.removeClass("ui-draggable-dragging");\n
\t\tif(this.helper[0] != this.element[0] && !this.cancelHelperRemoval) this.helper.remove();\n
\t\t//if($.ui.ddmanager) $.ui.ddmanager.current = null;\n
\t\tthis.helper = null;\n
\t\tthis.cancelHelperRemoval = false;\n
\t},\n
\n
\t// From now on bulk stuff - mainly helpers\n
\n
\t_trigger: function(type, event, ui) {\n
\t\tui = ui || this._uiHash();\n
\t\t$.ui.plugin.call(this, type, [event, ui]);\n
\t\tif(type == "drag") this.positionAbs = this._convertPositionTo("absolute"); //The absolute position has to be recalculated after plugins\n
\t\treturn $.Widget.prototype._trigger.call(this, type, event, ui);\n
\t},\n
\n
\tplugins: {},\n
\n
\t_uiHash: function(event) {\n
\t\treturn {\n
\t\t\thelper: this.helper,\n
\t\t\tposition: this.position,\n
\t\t\toriginalPosition: this.originalPosition,\n
\t\t\toffset: this.positionAbs\n
\t\t};\n
\t}\n
\n
});\n
\n
$.extend($.ui.draggable, {\n
\tversion: "1.8.2"\n
});\n
\n
$.ui.plugin.add("draggable", "connectToSortable", {\n
\tstart: function(event, ui) {\n
\n
\t\tvar inst = $(this).data("draggable"), o = inst.options,\n
\t\t\tuiSortable = $.extend({}, ui, { item: inst.element });\n
\t\tinst.sortables = [];\n
\t\t$(o.connectToSortable).each(function() {\n
\t\t\tvar sortable = $.data(this, \'sortable\');\n
\t\t\tif (sortable && !sortable.options.disabled) {\n
\t\t\t\tinst.sortables.push({\n
\t\t\t\t\tinstance: sortable,\n
\t\t\t\t\tshouldRevert: sortable.options.revert\n
\t\t\t\t});\n
\t\t\t\tsortable._refreshItems();\t//Do a one-time refresh at start to refresh the containerCache\n
\t\t\t\tsortable._trigger("activate", event, uiSortable);\n
\t\t\t}\n
\t\t});\n
\n
\t},\n
\tstop: function(event, ui) {\n
\n
\t\t//If we are still over the sortable, we fake the stop event of the sortable, but also remove helper\n
\t\tvar inst = $(this).data("draggable"),\n
\t\t\tuiSortable = $.extend({}, ui, { item: inst.element });\n
\n
\t\t$.each(inst.sortables, function() {\n
\t\t\tif(this.instance.isOver) {\n
\n
\t\t\t\tthis.instance.isOver = 0;\n
\n
\t\t\t\tinst.cancelHelperRemoval = true; //Don\'t remove the helper in the draggable instance\n
\t\t\t\tthis.instance.cancelHelperRemoval = false; //Remove it in the sortable instance (so sortable plugins like revert still work)\n
\n
\t\t\t\t//The sortable revert is supported, and we have to set a temporary dropped variable on the draggable to support revert: \'valid/invalid\'\n
\t\t\t\tif(this.shouldRevert) this.instance.options.revert = true;\n
\n
\t\t\t\t//Trigger the stop of the sortable\n
\t\t\t\tthis.instance._mouseStop(event);\n
\n
\t\t\t\tthis.instance.options.helper = this.instance.options._helper;\n
\n
\t\t\t\t//If the helper has been the original item, restore properties in the sortable\n
\t\t\t\tif(inst.options.helper == \'original\')\n
\t\t\t\t\tthis.instance.currentItem.css({ top: \'auto\', left: \'auto\' });\n
\n
\t\t\t} else {\n
\t\t\t\tthis.instance.cancelHelperRemoval = false; //Remove the helper in the sortable instance\n
\t\t\t\tthis.instance._trigger("deactivate", event, uiSortable);\n
\t\t\t}\n
\n
\t\t});\n
\n
\t},\n
\tdrag: function(event, ui) {\n
\n
\t\tvar inst = $(this).data("draggable"), self = this;\n
\n
\t\tvar checkPos = function(o) {\n
\t\t\tvar dyClick = this.offset.click.top, dxClick = this.offset.click.left;\n
\t\t\tvar helperTop = this.positionAbs.top, helperLeft = this.positionAbs.left;\n
\t\t\tvar itemHeight = o.height, itemWidth = o.width;\n
\t\t\tvar itemTop = o.top, itemLeft = o.left;\n
\n
\t\t\treturn $.ui.isOver(helperTop + dyClick, helperLeft + dxClick, itemTop, itemLeft, itemHeight, itemWidth);\n
\t\t};\n
\n
\t\t$.each(inst.sortables, function(i) {\n
\t\t\t\n
\t\t\t//Copy over some variables to allow calling the sortable\'s native _intersectsWith\n
\t\t\tthis.instance.positionAbs = inst.positionAbs;\n
\t\t\tthis.instance.helperProportions = inst.helperProportions;\n
\t\t\tthis.instance.offset.click = inst.offset.click;\n
\t\t\t\n
\t\t\tif(this.instance._intersectsWith(this.instance.containerCache)) {\n
\n
\t\t\t\t//If it intersects, we use a little isOver variable and set it once, so our move-in stuff gets fired only once\n
\t\t\t\tif(!this.instance.isOver) {\n
\n
\t\t\t\t\tthis.instance.isOver = 1;\n
\t\t\t\t\t//Now we fake the start of dragging for the sortable instance,\n
\t\t\t\t\t//by cloning the list group item, appending it to the sortable and using it as inst.currentItem\n
\t\t\t\t\t//We can then fire the start event of the sortable with our passed browser event, and our own helper (so it doesn\'t create a new one)\n
\t\t\t\t\tthis.instance.currentItem = $(self).clone().appendTo(this.instance.element).data("sortable-item", true);\n
\t\t\t\t\tthis.instance.options._helper = this.instance.options.helper; //Store helper option to later restore it\n
\t\t\t\t\tthis.instance.options.helper = function() { return ui.helper[0]; };\n
\n
\t\t\t\t\tevent.target = this.instance.currentItem[0];\n
\t\t\t\t\tthis.instance._mouseCapture(event, true);\n
\t\t\t\t\tthis.instance._mouseStart(event, true, true);\n
\n
\t\t\t\t\t//Because the browser event is way off the new appended portlet, we modify a couple of variables to reflect the changes\n
\t\t\t\t\tthis.instance.offset.click.top = inst.offset.click.top;\n
\t\t\t\t\tthis.instance.offset.click.left = inst.offset.click.left;\n
\t\t\t\t\tthis.instance.offset.parent.left -= inst.offset.parent.left - this.instance.offset.parent.left;\n
\t\t\t\t\tthis.instance.offset.parent.top -= inst.offset.parent.top - this.instance.offset.parent.top;\n
\n
\t\t\t\t\tinst._trigger("toSortable", event);\n
\t\t\t\t\tinst.dropped = this.instance.element; //draggable revert needs that\n
\t\t\t\t\t//hack so receive/update callbacks work (mostly)\n
\t\t\t\t\tinst.currentItem = inst.element;\n
\t\t\t\t\tthis.instance.fromOutside = inst;\n
\n
\t\t\t\t}\n
\n
\t\t\t\t//Provided we did all the previous steps, we can fire the drag event of the sortable on every draggable drag, when it intersects with the sortable\n
\t\t\t\tif(this.instance.currentItem) this.instance._mouseDrag(event);\n
\n
\t\t\t} else {\n
\n
\t\t\t\t//If it doesn\'t intersect with the sortable, and it intersected before,\n
\t\t\t\t//we fake the drag stop of the sortable, but make sure it doesn\'t remove the helper by using cancelHelperRemoval\n
\t\t\t\tif(this.instance.isOver) {\n
\n
\t\t\t\t\tthis.instance.isOver = 0;\n
\t\t\t\t\tthis.instance.cancelHelperRemoval = true;\n
\t\t\t\t\t\n
\t\t\t\t\t//Prevent reverting on this forced stop\n
\t\t\t\t\tthis.instance.options.revert = false;\n
\t\t\t\t\t\n
\t\t\t\t\t// The out event needs to be triggered independently\n
\t\t\t\t\tthis.instance._trigger(\'out\', event, this.instance._uiHash(this.instance));\n
\t\t\t\t\t\n
\t\t\t\t\tthis.instance._mouseStop(event, true);\n
\t\t\t\t\tthis.instance.options.helper = this.instance.options._helper;\n
\n
\t\t\t\t\t//Now we remove our currentItem, the list group clone again, and the placeholder, and animate the helper back to it\'s original size\n
\t\t\t\t\tthis.instance.currentItem.remove();\n
\t\t\t\t\tif(this.instance.placeholder) this.instance.placeholder.remove();\n
\n
\t\t\t\t\tinst._trigger("fromSortable", event);\n
\t\t\t\t\tinst.dropped = false; //draggable revert needs that\n
\t\t\t\t}\n
\n
\t\t\t};\n
\n
\t\t});\n
\n
\t}\n
});\n
\n
$.ui.plugin.add("draggable", "cursor", {\n
\tstart: function(event, ui) {\n
\t\tvar t = $(\'body\'), o = $(this).data(\'draggable\').options;\n
\t\tif (t.css("cursor")) o._cursor = t.css("cursor");\n
\t\tt.css("cursor", o.cursor);\n
\t},\n
\tstop: function(event, ui) {\n
\t\tvar o = $(this).data(\'draggable\').options;\n
\t\tif (o._cursor) $(\'body\').css("cursor", o._cursor);\n
\t}\n
});\n
\n
$.ui.plugin.add("draggable", "iframeFix", {\n
\tstart: function(event, ui) {\n
\t\tvar o = $(this).data(\'draggable\').options;\n
\t\t$(o.iframeFix === true ? "iframe" : o.iframeFix).each(function() {\n
\t\t\t$(\'<div class="ui-draggable-iframeFix" style="background: #fff;"></div>\')\n
\t\t\t.css({\n
\t\t\t\twidth: this.offsetWidth+"px", height: this.offsetHeight+"px",\n
\t\t\t\tposition: "absolute", opacity: "0.001", zIndex: 1000\n
\t\t\t})\n
\t\t\t.css($(this).offset())\n
\t\t\t.appendTo("body");\n
\t\t});\n
\t},\n
\tstop: function(event, ui) {\n
\t\t$("div.ui-draggable-iframeFix").each(function() { this.parentNode.removeChild(this); }); //Remove frame helpers\n
\t}\n
});\n
\n
$.ui.plugin.add("draggable", "opacity", {\n
\tstart: function(event, ui) {\n
\t\tvar t = $(ui.helper), o = $(this).data(\'draggable\').options;\n
\t\tif(t.css("opacity")) o._opacity = t.css("opacity");\n
\t\tt.css(\'opacity\', o.opacity);\n
\t},\n
\tstop: function(event, ui) {\n
\t\tvar o = $(this).data(\'draggable\').options;\n
\t\tif(o._opacity) $(ui.helper).css(\'opacity\', o._opacity);\n
\t}\n
});\n
\n
$.ui.plugin.add("draggable", "scroll", {\n
\tstart: function(event, ui) {\n
\t\tvar i = $(this).data("draggable");\n
\t\tif(i.scrollParent[0] != document && i.scrollParent[0].tagName != \'HTML\') i.overflowOffset = i.scrollParent.offset();\n
\t},\n
\tdrag: function(event, ui) {\n
\n
\t\tvar i = $(this).data("draggable"), o = i.options, scrolled = false;\n
\n
\t\tif(i.scrollParent[0] != document && i.scrollParent[0].tagName != \'HTML\') {\n
\n
\t\t\tif(!o.axis || o.axis != \'x\') {\n
\t\t\t\tif((i.overflowOffset.top + i.scrollParent[0].offsetHeight) - event.pageY < o.scrollSensitivity)\n
\t\t\t\t\ti.scrollParent[0].scrollTop = scrolled = i.scrollParent[0].scrollTop + o.scrollSpeed;\n
\t\t\t\telse if(event.pageY - i.overflowOffset.top < o.scrollSensitivity)\n
\t\t\t\t\ti.scrollParent[0].scrollTop = scrolled = i.scrollParent[0].scrollTop - o.scrollSpeed;\n
\t\t\t}\n
\n
\t\t\tif(!o.axis || o.axis != \'y\') {\n
\t\t\t\tif((i.overflowOffset.left + i.scrollParent[0].offsetWidth) - event.pageX < o.scrollSensitivity)\n
\t\t\t\t\ti.scrollParent[0].scrollLeft = scrolled = i.scrollParent[0].scrollLeft + o.scrollSpeed;\n
\t\t\t\telse if(event.pageX - i.overflowOffset.left < o.scrollSensitivity)\n
\t\t\t\t\ti.scrollParent[0].scrollLeft = scrolled = i.scrollParent[0].scrollLeft - o.scrollSpeed;\n
\t\t\t}\n
\n
\t\t} else {\n
\n
\t\t\tif(!o.axis || o.axis != \'x\') {\n
\t\t\t\tif(event.pageY - $(document).scrollTop() < o.scrollSensitivity)\n
\t\t\t\t\tscrolled = $(document).scrollTop($(document).scrollTop() - o.scrollSpeed);\n
\t\t\t\telse if($(window).height() - (event.pageY - $(document).scrollTop()) < o.scrollSensitivity)\n
\t\t\t\t\tscrolled = $(document).scrollTop($(document).scrollTop() + o.scrollSpeed);\n
\t\t\t}\n
\n
\t\t\tif(!o.axis || o.axis != \'y\') {\n
\t\t\t\tif(event.pageX - $(document).scrollLeft() < o.scrollSensitivity)\n
\t\t\t\t\tscrolled = $(document).scrollLeft($(document).scrollLeft() - o.scrollSpeed);\n
\t\t\t\telse if($(window).width() - (event.pageX - $(document).scrollLeft()) < o.scrollSensitivity)\n
\t\t\t\t\tscrolled = $(document).scrollLeft($(document).scrollLeft() + o.scrollSpeed);\n
\t\t\t}\n
\n
\t\t}\n
\n
\t\tif(scrolled !== false && $.ui.ddmanager && !o.dropBehaviour)\n
\t\t\t$.ui.ddmanager.prepareOffsets(i, event);\n
\n
\t}\n
});\n
\n
$.ui.plugin.add("draggable", "snap", {\n
\tstart: function(event, ui) {\n
\n
\t\tvar i = $(this).data("draggable"), o = i.options;\n
\t\ti.snapElements = [];\n
\n
\t\t$(o.snap.constructor != String ? ( o.snap.items || \':data(draggable)\' ) : o.snap).each(function() {\n
\t\t\tvar $t = $(this); var $o = $t.offset();\n
\t\t\tif(this != i.element[0]) i.snapElements.push({\n
\t\t\t\titem: this,\n
\t\t\t\twidth: $t.outerWidth(), height: $t.outerHeight(),\n
\t\t\t\ttop: $o.top, left: $o.left\n
\t\t\t});\n
\t\t});\n
\n
\t},\n
\tdrag: function(event, ui) {\n
\n
\t\tvar inst = $(this).data("draggable"), o = inst.options;\n
\t\tvar d = o.snapTolerance;\n
\n
\t\tvar x1 = ui.offset.left, x2 = x1 + inst.helperProportions.width,\n
\t\t\ty1 = ui.offset.top, y2 = y1 + inst.helperProportions.height;\n
\n
\t\tfor (var i = inst.snapElements.length - 1; i >= 0; i--){\n
\n
\t\t\tvar l = inst.snapElements[i].left, r = l + inst.snapElements[i].width,\n
\t\t\t\tt = inst.snapElements[i].top, b = t + inst.snapElements[i].height;\n
\n
\t\t\t//Yes, I know, this is insane ;)\n
\t\t\tif(!((l-d < x1 && x1 < r+d && t-d < y1 && y1 < b+d) || (l-d < x1 && x1 < r+d && t-d < y2 && y2 < b+d) || (l-d < x2 && x2 < r+d && t-d < y1 && y1 < b+d) || (l-d < x2 && x2 < r+d && t-d < y2 && y2 < b+d))) {\n
\t\t\t\tif(inst.snapElements[i].snapping) (inst.options.snap.release && inst.options.snap.release.call(inst.element, event, $.extend(inst._uiHash(), { snapItem: inst.snapElements[i].item })));\n
\t\t\t\tinst.snapElements[i].snapping = false;\n
\t\t\t\tcontinue;\n
\t\t\t}\n
\n
\t\t\tif(o.snapMode != \'inner\') {\n
\t\t\t\tvar ts = Math.abs(t - y2) <= d;\n
\t\t\t\tvar bs = Math.abs(b - y1) <= d;\n
\t\t\t\tvar ls = Math.abs(l - x2) <= d;\n
\t\t\t\tvar rs = Math.abs(r - x1) <= d;\n
\t\t\t\tif(ts) ui.position.top = inst._convertPositionTo("relative", { top: t - inst.helperProportions.height, left: 0 }).top - inst.margins.top;\n
\t\t\t\tif(bs) ui.position.top = inst._convertPositionTo("relative", { top: b, left: 0 }).top - inst.margins.top;\n
\t\t\t\tif(ls) ui.position.left = inst._convertPositionTo("relative", { top: 0, left: l - inst.helperProportions.width }).left - inst.margins.left;\n
\t\t\t\tif(rs) ui.position.left = inst._convertPositionTo("relative", { top: 0, left: r }).left - inst.margins.left;\n
\t\t\t}\n
\n
\t\t\tvar first = (ts || bs || ls || rs);\n
\n
\t\t\tif(o.snapMode != \'outer\') {\n
\t\t\t\tvar ts = Math.abs(t - y1) <= d;\n
\t\t\t\tvar bs = Math.abs(b - y2) <= d;\n
\t\t\t\tvar ls = Math.abs(l - x1) <= d;\n
\t\t\t\tvar rs = Math.abs(r - x2) <= d;\n
\t\t\t\tif(ts) ui.position.top = inst._convertPositionTo("relative", { top: t, left: 0 }).top - inst.margins.top;\n
\t\t\t\tif(bs) ui.position.top = inst._convertPositionTo("relative", { top: b - inst.helperProportions.height, left: 0 }).top - inst.margins.top;\n
\t\t\t\tif(ls) ui.position.left = inst._convertPositionTo("relative", { top: 0, left: l }).left - inst.margins.left;\n
\t\t\t\tif(rs) ui.position.left = inst._convertPositionTo("relative", { top: 0, left: r - inst.helperProportions.width }).left - inst.margins.left;\n
\t\t\t}\n
\n
\t\t\tif(!inst.snapElements[i].snapping && (ts || bs || ls || rs || first))\n
\t\t\t\t(inst.options.snap.snap && inst.options.snap.snap.call(inst.element, event, $.extend(inst._uiHash(), { snapItem: inst.snapElements[i].item })));\n
\t\t\tinst.snapElements[i].snapping = (ts || bs || ls || rs || first);\n
\n
\t\t};\n
\n
\t}\n
});\n
\n
$.ui.plugin.add("draggable", "stack", {\n
\tstart: function(event, ui) {\n
\n
\t\tvar o = $(this).data("draggable").options;\n
\n
\t\tvar group = $.makeArray($(o.stack)).sort(function(a,b) {\n
\t\t\treturn (parseInt($(a).css("zIndex"),10) || 0) - (parseInt($(b).css("zIndex"),10) || 0);\n
\t\t});\n
\t\tif (!group.length) { return; }\n
\t\t\n
\t\tvar min = parseInt(group[0].style.zIndex) || 0;\n
\t\t$(group).each(function(i) {\n
\t\t\tthis.style.zIndex = min + i;\n
\t\t});\n
\n
\t\tthis[0].style.zIndex = min + group.length;\n
\n
\t}\n
});\n
\n
$.ui.plugin.add("draggable", "zIndex", {\n
\tstart: function(event, ui) {\n
\t\tvar t = $(ui.helper), o = $(this).data("draggable").options;\n
\t\tif(t.css("zIndex")) o._zIndex = t.css("zIndex");\n
\t\tt.css(\'zIndex\', o.zIndex);\n
\t},\n
\tstop: function(event, ui) {\n
\t\tvar o = $(this).data("draggable").options;\n
\t\tif(o._zIndex) $(ui.helper).css(\'zIndex\', o._zIndex);\n
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
            <value> <int>29422</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
