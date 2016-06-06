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
            <value> <string>ts65545394.7</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ui.sortable.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Sortable 1.7.2\n
 *\n
 * Copyright (c) 2009 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Sortables\n
 *\n
 * Depends:\n
 *\tui.core.js\n
 */\n
(function($) {\n
\n
$.widget("ui.sortable", $.extend({}, $.ui.mouse, {\n
\t_init: function() {\n
\n
\t\tvar o = this.options;\n
\t\tthis.containerCache = {};\n
\t\tthis.element.addClass("ui-sortable");\n
\n
\t\t//Get the items\n
\t\tthis.refresh();\n
\n
\t\t//Let\'s determine if the items are floating\n
\t\tthis.floating = this.items.length ? (/left|right/).test(this.items[0].item.css(\'float\')) : false;\n
\n
\t\t//Let\'s determine the parent\'s offset\n
\t\tthis.offset = this.element.offset();\n
\n
\t\t//Initialize mouse events for interaction\n
\t\tthis._mouseInit();\n
\n
\t},\n
\n
\tdestroy: function() {\n
\t\tthis.element\n
\t\t\t.removeClass("ui-sortable ui-sortable-disabled")\n
\t\t\t.removeData("sortable")\n
\t\t\t.unbind(".sortable");\n
\t\tthis._mouseDestroy();\n
\n
\t\tfor ( var i = this.items.length - 1; i >= 0; i-- )\n
\t\t\tthis.items[i].item.removeData("sortable-item");\n
\t},\n
\n
\t_mouseCapture: function(event, overrideHandle) {\n
\n
\t\tif (this.reverting) {\n
\t\t\treturn false;\n
\t\t}\n
\n
\t\tif(this.options.disabled || this.options.type == \'static\') return false;\n
\n
\t\t//We have to refresh the items data once first\n
\t\tthis._refreshItems(event);\n
\n
\t\t//Find out if the clicked node (or one of its parents) is a actual item in this.items\n
\t\tvar currentItem = null, self = this, nodes = $(event.target).parents().each(function() {\n
\t\t\tif($.data(this, \'sortable-item\') == self) {\n
\t\t\t\tcurrentItem = $(this);\n
\t\t\t\treturn false;\n
\t\t\t}\n
\t\t});\n
\t\tif($.data(event.target, \'sortable-item\') == self) currentItem = $(event.target);\n
\n
\t\tif(!currentItem) return false;\n
\t\tif(this.options.handle && !overrideHandle) {\n
\t\t\tvar validHandle = false;\n
\n
\t\t\t$(this.options.handle, currentItem).find("*").andSelf().each(function() { if(this == event.target) validHandle = true; });\n
\t\t\tif(!validHandle) return false;\n
\t\t}\n
\n
\t\tthis.currentItem = currentItem;\n
\t\tthis._removeCurrentsFromItems();\n
\t\treturn true;\n
\n
\t},\n
\n
\t_mouseStart: function(event, overrideHandle, noActivation) {\n
\n
\t\tvar o = this.options, self = this;\n
\t\tthis.currentContainer = this;\n
\n
\t\t//We only need to call refreshPositions, because the refreshItems call has been moved to mouseCapture\n
\t\tthis.refreshPositions();\n
\n
\t\t//Create and append the visible helper\n
\t\tthis.helper = this._createHelper(event);\n
\n
\t\t//Cache the helper size\n
\t\tthis._cacheHelperProportions();\n
\n
\t\t/*\n
\t\t * - Position generation -\n
\t\t * This block generates everything position related - it\'s the core of draggables.\n
\t\t */\n
\n
\t\t//Cache the margins of the original element\n
\t\tthis._cacheMargins();\n
\n
\t\t//Get the next scrolling parent\n
\t\tthis.scrollParent = this.helper.scrollParent();\n
\n
\t\t//The element\'s absolute position on the page minus margins\n
\t\tthis.offset = this.currentItem.offset();\n
\t\tthis.offset = {\n
\t\t\ttop: this.offset.top - this.margins.top,\n
\t\t\tleft: this.offset.left - this.margins.left\n
\t\t};\n
\n
\t\t// Only after we got the offset, we can change the helper\'s position to absolute\n
\t\t// TODO: Still need to figure out a way to make relative sorting possible\n
\t\tthis.helper.css("position", "absolute");\n
\t\tthis.cssPosition = this.helper.css("position");\n
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
\t\tthis.originalPosition = this._generatePosition(event);\n
\t\tthis.originalPageX = event.pageX;\n
\t\tthis.originalPageY = event.pageY;\n
\n
\t\t//Adjust the mouse offset relative to the helper if \'cursorAt\' is supplied\n
\t\tif(o.cursorAt)\n
\t\t\tthis._adjustOffsetFromHelper(o.cursorAt);\n
\n
\t\t//Cache the former DOM position\n
\t\tthis.domPosition = { prev: this.currentItem.prev()[0], parent: this.currentItem.parent()[0] };\n
\n
\t\t//If the helper is not the original, hide the original so it\'s not playing any role during the drag, won\'t cause anything bad this way\n
\t\tif(this.helper[0] != this.currentItem[0]) {\n
\t\t\tthis.currentItem.hide();\n
\t\t}\n
\n
\t\t//Create the placeholder\n
\t\tthis._createPlaceholder();\n
\n
\t\t//Set a containment if given in the options\n
\t\tif(o.containment)\n
\t\t\tthis._setContainment();\n
\n
\t\tif(o.cursor) { // cursor option\n
\t\t\tif ($(\'body\').css("cursor")) this._storedCursor = $(\'body\').css("cursor");\n
\t\t\t$(\'body\').css("cursor", o.cursor);\n
\t\t}\n
\n
\t\tif(o.opacity) { // opacity option\n
\t\t\tif (this.helper.css("opacity")) this._storedOpacity = this.helper.css("opacity");\n
\t\t\tthis.helper.css("opacity", o.opacity);\n
\t\t}\n
\n
\t\tif(o.zIndex) { // zIndex option\n
\t\t\tif (this.helper.css("zIndex")) this._storedZIndex = this.helper.css("zIndex");\n
\t\t\tthis.helper.css("zIndex", o.zIndex);\n
\t\t}\n
\n
\t\t//Prepare scrolling\n
\t\tif(this.scrollParent[0] != document && this.scrollParent[0].tagName != \'HTML\')\n
\t\t\tthis.overflowOffset = this.scrollParent.offset();\n
\n
\t\t//Call callbacks\n
\t\tthis._trigger("start", event, this._uiHash());\n
\n
\t\t//Recache the helper size\n
\t\tif(!this._preserveHelperProportions)\n
\t\t\tthis._cacheHelperProportions();\n
\n
\n
\t\t//Post \'activate\' events to possible containers\n
\t\tif(!noActivation) {\n
\t\t\t for (var i = this.containers.length - 1; i >= 0; i--) { this.containers[i]._trigger("activate", event, self._uiHash(this)); }\n
\t\t}\n
\n
\t\t//Prepare possible droppables\n
\t\tif($.ui.ddmanager)\n
\t\t\t$.ui.ddmanager.current = this;\n
\n
\t\tif ($.ui.ddmanager && !o.dropBehaviour)\n
\t\t\t$.ui.ddmanager.prepareOffsets(this, event);\n
\n
\t\tthis.dragging = true;\n
\n
\t\tthis.helper.addClass("ui-sortable-helper");\n
\t\tthis._mouseDrag(event); //Execute the drag once - this causes the helper not to be visible before getting its correct position\n
\t\treturn true;\n
\n
\t},\n
\n
\t_mouseDrag: function(event) {\n
\n
\t\t//Compute the helpers position\n
\t\tthis.position = this._generatePosition(event);\n
\t\tthis.positionAbs = this._convertPositionTo("absolute");\n
\n
\t\tif (!this.lastPositionAbs) {\n
\t\t\tthis.lastPositionAbs = this.positionAbs;\n
\t\t}\n
\n
\t\t//Do scrolling\n
\t\tif(this.options.scroll) {\n
\t\t\tvar o = this.options, scrolled = false;\n
\t\t\tif(this.scrollParent[0] != document && this.scrollParent[0].tagName != \'HTML\') {\n
\n
\t\t\t\tif((this.overflowOffset.top + this.scrollParent[0].offsetHeight) - event.pageY < o.scrollSensitivity)\n
\t\t\t\t\tthis.scrollParent[0].scrollTop = scrolled = this.scrollParent[0].scrollTop + o.scrollSpeed;\n
\t\t\t\telse if(event.pageY - this.overflowOffset.top < o.scrollSensitivity)\n
\t\t\t\t\tthis.scrollParent[0].scrollTop = scrolled = this.scrollParent[0].scrollTop - o.scrollSpeed;\n
\n
\t\t\t\tif((this.overflowOffset.left + this.scrollParent[0].offsetWidth) - event.pageX < o.scrollSensitivity)\n
\t\t\t\t\tthis.scrollParent[0].scrollLeft = scrolled = this.scrollParent[0].scrollLeft + o.scrollSpeed;\n
\t\t\t\telse if(event.pageX - this.overflowOffset.left < o.scrollSensitivity)\n
\t\t\t\t\tthis.scrollParent[0].scrollLeft = scrolled = this.scrollParent[0].scrollLeft - o.scrollSpeed;\n
\n
\t\t\t} else {\n
\n
\t\t\t\tif(event.pageY - $(document).scrollTop() < o.scrollSensitivity)\n
\t\t\t\t\tscrolled = $(document).scrollTop($(document).scrollTop() - o.scrollSpeed);\n
\t\t\t\telse if($(window).height() - (event.pageY - $(document).scrollTop()) < o.scrollSensitivity)\n
\t\t\t\t\tscrolled = $(document).scrollTop($(document).scrollTop() + o.scrollSpeed);\n
\n
\t\t\t\tif(event.pageX - $(document).scrollLeft() < o.scrollSensitivity)\n
\t\t\t\t\tscrolled = $(document).scrollLeft($(document).scrollLeft() - o.scrollSpeed);\n
\t\t\t\telse if($(window).width() - (event.pageX - $(document).scrollLeft()) < o.scrollSensitivity)\n
\t\t\t\t\tscrolled = $(document).scrollLeft($(document).scrollLeft() + o.scrollSpeed);\n
\n
\t\t\t}\n
\n
\t\t\tif(scrolled !== false && $.ui.ddmanager && !o.dropBehaviour)\n
\t\t\t\t$.ui.ddmanager.prepareOffsets(this, event);\n
\t\t}\n
\n
\t\t//Regenerate the absolute position used for position checks\n
\t\tthis.positionAbs = this._convertPositionTo("absolute");\n
\n
\t\t//Set the helper position\n
\t\tif(!this.options.axis || this.options.axis != "y") this.helper[0].style.left = this.position.left+\'px\';\n
\t\tif(!this.options.axis || this.options.axis != "x") this.helper[0].style.top = this.position.top+\'px\';\n
\n
\t\t//Rearrange\n
\t\tfor (var i = this.items.length - 1; i >= 0; i--) {\n
\n
\t\t\t//Cache variables and intersection, continue if no intersection\n
\t\t\tvar item = this.items[i], itemElement = item.item[0], intersection = this._intersectsWithPointer(item);\n
\t\t\tif (!intersection) continue;\n
\n
\t\t\tif(itemElement != this.currentItem[0] //cannot intersect with itself\n
\t\t\t\t&&\tthis.placeholder[intersection == 1 ? "next" : "prev"]()[0] != itemElement //no useless actions that have been done before\n
\t\t\t\t&&\t!$.ui.contains(this.placeholder[0], itemElement) //no action if the item moved is the parent of the item checked\n
\t\t\t\t&& (this.options.type == \'semi-dynamic\' ? !$.ui.contains(this.element[0], itemElement) : true)\n
\t\t\t) {\n
\n
\t\t\t\tthis.direction = intersection == 1 ? "down" : "up";\n
\n
\t\t\t\tif (this.options.tolerance == "pointer" || this._intersectsWithSides(item)) {\n
\t\t\t\t\tthis._rearrange(event, item);\n
\t\t\t\t} else {\n
\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\n
\t\t\t\tthis._trigger("change", event, this._uiHash());\n
\t\t\t\tbreak;\n
\t\t\t}\n
\t\t}\n
\n
\t\t//Post events to containers\n
\t\tthis._contactContainers(event);\n
\n
\t\t//Interconnect with droppables\n
\t\tif($.ui.ddmanager) $.ui.ddmanager.drag(this, event);\n
\n
\t\t//Call callbacks\n
\t\tthis._trigger(\'sort\', event, this._uiHash());\n
\n
\t\tthis.lastPositionAbs = this.positionAbs;\n
\t\treturn false;\n
\n
\t},\n
\n
\t_mouseStop: function(event, noPropagation) {\n
\n
\t\tif(!event) return;\n
\n
\t\t//If we are using droppables, inform the manager about the drop\n
\t\tif ($.ui.ddmanager && !this.options.dropBehaviour)\n
\t\t\t$.ui.ddmanager.drop(this, event);\n
\n
\t\tif(this.options.revert) {\n
\t\t\tvar self = this;\n
\t\t\tvar cur = self.placeholder.offset();\n
\n
\t\t\tself.reverting = true;\n
\n
\t\t\t$(this.helper).animate({\n
\t\t\t\tleft: cur.left - this.offset.parent.left - self.margins.left + (this.offsetParent[0] == document.body ? 0 : this.offsetParent[0].scrollLeft),\n
\t\t\t\ttop: cur.top - this.offset.parent.top - self.margins.top + (this.offsetParent[0] == document.body ? 0 : this.offsetParent[0].scrollTop)\n
\t\t\t}, parseInt(this.options.revert, 10) || 500, function() {\n
\t\t\t\tself._clear(event);\n
\t\t\t});\n
\t\t} else {\n
\t\t\tthis._clear(event, noPropagation);\n
\t\t}\n
\n
\t\treturn false;\n
\n
\t},\n
\n
\tcancel: function() {\n
\n
\t\tvar self = this;\n
\n
\t\tif(this.dragging) {\n
\n
\t\t\tthis._mouseUp();\n
\n
\t\t\tif(this.options.helper == "original")\n
\t\t\t\tthis.currentItem.css(this._storedCSS).removeClass("ui-sortable-helper");\n
\t\t\telse\n
\t\t\t\tthis.currentItem.show();\n
\n
\t\t\t//Post deactivating events to containers\n
\t\t\tfor (var i = this.containers.length - 1; i >= 0; i--){\n
\t\t\t\tthis.containers[i]._trigger("deactivate", null, self._uiHash(this));\n
\t\t\t\tif(this.containers[i].containerCache.over) {\n
\t\t\t\t\tthis.containers[i]._trigger("out", null, self._uiHash(this));\n
\t\t\t\t\tthis.containers[i].containerCache.over = 0;\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t}\n
\n
\t\t//$(this.placeholder[0]).remove(); would have been the jQuery way - unfortunately, it unbinds ALL events from the original node!\n
\t\tif(this.placeholder[0].parentNode) this.placeholder[0].parentNode.removeChild(this.placeholder[0]);\n
\t\tif(this.options.helper != "original" && this.helper && this.helper[0].parentNode) this.helper.remove();\n
\n
\t\t$.extend(this, {\n
\t\t\thelper: null,\n
\t\t\tdragging: false,\n
\t\t\treverting: false,\n
\t\t\t_noFinalSort: null\n
\t\t});\n
\n
\t\tif(this.domPosition.prev) {\n
\t\t\t$(this.domPosition.prev).after(this.currentItem);\n
\t\t} else {\n
\t\t\t$(this.domPosition.parent).prepend(this.currentItem);\n
\t\t}\n
\n
\t\treturn true;\n
\n
\t},\n
\n
\tserialize: function(o) {\n
\n
\t\tvar items = this._getItemsAsjQuery(o && o.connected);\n
\t\tvar str = []; o = o || {};\n
\n
\t\t$(items).each(function() {\n
\t\t\tvar res = ($(o.item || this).attr(o.attribute || \'id\') || \'\').match(o.expression || (/(.+)[-=_](.+)/));\n
\t\t\tif(res) str.push((o.key || res[1]+\'[]\')+\'=\'+(o.key && o.expression ? res[1] : res[2]));\n
\t\t});\n
\n
\t\treturn str.join(\'&\');\n
\n
\t},\n
\n
\ttoArray: function(o) {\n
\n
\t\tvar items = this._getItemsAsjQuery(o && o.connected);\n
\t\tvar ret = []; o = o || {};\n
\n
\t\titems.each(function() { ret.push($(o.item || this).attr(o.attribute || \'id\') || \'\'); });\n
\t\treturn ret;\n
\n
\t},\n
\n
\t/* Be careful with the following core functions */\n
\t_intersectsWith: function(item) {\n
\n
\t\tvar x1 = this.positionAbs.left,\n
\t\t\tx2 = x1 + this.helperProportions.width,\n
\t\t\ty1 = this.positionAbs.top,\n
\t\t\ty2 = y1 + this.helperProportions.height;\n
\n
\t\tvar l = item.left,\n
\t\t\tr = l + item.width,\n
\t\t\tt = item.top,\n
\t\t\tb = t + item.height;\n
\n
\t\tvar dyClick = this.offset.click.top,\n
\t\t\tdxClick = this.offset.click.left;\n
\n
\t\tvar isOverElement = (y1 + dyClick) > t && (y1 + dyClick) < b && (x1 + dxClick) > l && (x1 + dxClick) < r;\n
\n
\t\tif(\t   this.options.tolerance == "pointer"\n
\t\t\t|| this.options.forcePointerForContainers\n
\t\t\t|| (this.options.tolerance != "pointer" && this.helperProportions[this.floating ? \'width\' : \'height\'] > item[this.floating ? \'width\' : \'height\'])\n
\t\t) {\n
\t\t\treturn isOverElement;\n
\t\t} else {\n
\n
\t\t\treturn (l < x1 + (this.helperProportions.width / 2) // Right Half\n
\t\t\t\t&& x2 - (this.helperProportions.width / 2) < r // Left Half\n
\t\t\t\t&& t < y1 + (this.helperProportions.height / 2) // Bottom Half\n
\t\t\t\t&& y2 - (this.helperProportions.height / 2) < b ); // Top Half\n
\n
\t\t}\n
\t},\n
\n
\t_intersectsWithPointer: function(item) {\n
\n
\t\tvar isOverElementHeight = $.ui.isOverAxis(this.positionAbs.top + this.offset.click.top, item.top, item.height),\n
\t\t\tisOverElementWidth = $.ui.isOverAxis(this.positionAbs.left + this.offset.click.left, item.left, item.width),\n
\t\t\tisOverElement = isOverElementHeight && isOverElementWidth,\n
\t\t\tverticalDirection = this._getDragVerticalDirection(),\n
\t\t\thorizontalDirection = this._getDragHorizontalDirection();\n
\n
\t\tif (!isOverElement)\n
\t\t\treturn false;\n
\n
\t\treturn this.floating ?\n
\t\t\t( ((horizontalDirection && horizontalDirection == "right") || verticalDirection == "down") ? 2 : 1 )\n
\t\t\t: ( verticalDirection && (verticalDirection == "down" ? 2 : 1) );\n
\n
\t},\n
\n
\t_intersectsWithSides: function(item) {\n
\n
\t\tvar isOverBottomHalf = $.ui.isOverAxis(this.positionAbs.top + this.offset.click.top, item.top + (item.height/2), item.height),\n
\t\t\tisOverRightHalf = $.ui.isOverAxis(this.positionAbs.left + this.offset.click.left, item.left + (item.width/2), item.width),\n
\t\t\tverticalDirection = this._getDragVerticalDirection(),\n
\t\t\thorizontalDirection = this._getDragHorizontalDirection();\n
\n
\t\tif (this.floating && horizontalDirection) {\n
\t\t\treturn ((horizontalDirection == "right" && isOverRightHalf) || (horizontalDirection == "left" && !isOverRightHalf));\n
\t\t} else {\n
\t\t\treturn verticalDirection && ((verticalDirection == "down" && isOverBottomHalf) || (verticalDirection == "up" && !isOverBottomHalf));\n
\t\t}\n
\n
\t},\n
\n
\t_getDragVerticalDirection: function() {\n
\t\tvar delta = this.positionAbs.top - this.lastPositionAbs.top;\n
\t\treturn delta != 0 && (delta > 0 ? "down" : "up");\n
\t},\n
\n
\t_getDragHorizontalDirection: function() {\n
\t\tvar delta = this.positionAbs.left - this.lastPositionAbs.left;\n
\t\treturn delta != 0 && (delta > 0 ? "right" : "left");\n
\t},\n
\n
\trefresh: function(event) {\n
\t\tthis._refreshItems(event);\n
\t\tthis.refreshPositions();\n
\t},\n
\n
\t_connectWith: function() {\n
\t\tvar options = this.options;\n
\t\treturn options.connectWith.constructor == String\n
\t\t\t? [options.connectWith]\n
\t\t\t: options.connectWith;\n
\t},\n
\t\n
\t_getItemsAsjQuery: function(connected) {\n
\n
\t\tvar self = this;\n
\t\tvar items = [];\n
\t\tvar queries = [];\n
\t\tvar connectWith = this._connectWith();\n
\n
\t\tif(connectWith && connected) {\n
\t\t\tfor (var i = connectWith.length - 1; i >= 0; i--){\n
\t\t\t\tvar cur = $(connectWith[i]);\n
\t\t\t\tfor (var j = cur.length - 1; j >= 0; j--){\n
\t\t\t\t\tvar inst = $.data(cur[j], \'sortable\');\n
\t\t\t\t\tif(inst && inst != this && !inst.options.disabled) {\n
\t\t\t\t\t\tqueries.push([$.isFunction(inst.options.items) ? inst.options.items.call(inst.element) : $(inst.options.items, inst.element).not(".ui-sortable-helper"), inst]);\n
\t\t\t\t\t}\n
\t\t\t\t};\n
\t\t\t};\n
\t\t}\n
\n
\t\tqueries.push([$.isFunction(this.options.items) ? this.options.items.call(this.element, null, { options: this.options, item: this.currentItem }) : $(this.options.items, this.element).not(".ui-sortable-helper"), this]);\n
\n
\t\tfor (var i = queries.length - 1; i >= 0; i--){\n
\t\t\tqueries[i][0].each(function() {\n
\t\t\t\titems.push(this);\n
\t\t\t});\n
\t\t};\n
\n
\t\treturn $(items);\n
\n
\t},\n
\n
\t_removeCurrentsFromItems: function() {\n
\n
\t\tvar list = this.currentItem.find(":data(sortable-item)");\n
\n
\t\tfor (var i=0; i < this.items.length; i++) {\n
\n
\t\t\tfor (var j=0; j < list.length; j++) {\n
\t\t\t\tif(list[j] == this.items[i].item[0])\n
\t\t\t\t\tthis.items.splice(i,1);\n
\t\t\t};\n
\n
\t\t};\n
\n
\t},\n
\n
\t_refreshItems: function(event) {\n
\n
\t\tthis.items = [];\n
\t\tthis.containers = [this];\n
\t\tvar items = this.items;\n
\t\tvar self = this;\n
\t\tvar queries = [[$.isFunction(this.options.items) ? this.options.items.call(this.element[0], event, { item: this.currentItem }) : $(this.options.items, this.element), this]];\n
\t\tvar connectWith = this._connectWith();\n
\n
\t\tif(connectWith) {\n
\t\t\tfor (var i = connectWith.length - 1; i >= 0; i--){\n
\t\t\t\tvar cur = $(connectWith[i]);\n
\t\t\t\tfor (var j = cur.length - 1; j >= 0; j--){\n
\t\t\t\t\tvar inst = $.data(cur[j], \'sortable\');\n
\t\t\t\t\tif(inst && inst != this && !inst.options.disabled) {\n
\t\t\t\t\t\tqueries.push([$.isFunction(inst.options.items) ? inst.options.items.call(inst.element[0], event, { item: this.currentItem }) : $(inst.options.items, inst.element), inst]);\n
\t\t\t\t\t\tthis.containers.push(inst);\n
\t\t\t\t\t}\n
\t\t\t\t};\n
\t\t\t};\n
\t\t}\n
\n
\t\tfor (var i = queries.length - 1; i >= 0; i--) {\n
\t\t\tvar targetData = queries[i][1];\n
\t\t\tvar _queries = queries[i][0];\n
\n
\t\t\tfor (var j=0, queriesLength = _queries.length; j < queriesLength; j++) {\n
\t\t\t\tvar item = $(_queries[j]);\n
\n
\t\t\t\titem.data(\'sortable-item\', targetData); // Data for target checking (mouse manager)\n
\n
\t\t\t\titems.push({\n
\t\t\t\t\titem: item,\n
\t\t\t\t\tinstance: targetData,\n
\t\t\t\t\twidth: 0, height: 0,\n
\t\t\t\t\tleft: 0, top: 0\n
\t\t\t\t});\n
\t\t\t};\n
\t\t};\n
\n
\t},\n
\n
\trefreshPositions: function(fast) {\n
\n
\t\t//This has to be redone because due to the item being moved out/into the offsetParent, the offsetParent\'s position will change\n
\t\tif(this.offsetParent && this.helper) {\n
\t\t\tthis.offset.parent = this._getParentOffset();\n
\t\t}\n
\n
\t\tfor (var i = this.items.length - 1; i >= 0; i--){\n
\t\t\tvar item = this.items[i];\n
\n
\t\t\t//We ignore calculating positions of all connected containers when we\'re not over them\n
\t\t\tif(item.instance != this.currentContainer && this.currentContainer && item.item[0] != this.currentItem[0])\n
\t\t\t\tcontinue;\n
\n
\t\t\tvar t = this.options.toleranceElement ? $(this.options.toleranceElement, item.item) : item.item;\n
\n
\t\t\tif (!fast) {\n
\t\t\t\titem.width = t.outerWidth();\n
\t\t\t\titem.height = t.outerHeight();\n
\t\t\t}\n
\n
\t\t\tvar p = t.offset();\n
\t\t\titem.left = p.left;\n
\t\t\titem.top = p.top;\n
\t\t};\n
\n
\t\tif(this.options.custom && this.options.custom.refreshContainers) {\n
\t\t\tthis.options.custom.refreshContainers.call(this);\n
\t\t} else {\n
\t\t\tfor (var i = this.containers.length - 1; i >= 0; i--){\n
\t\t\t\tvar p = this.containers[i].element.offset();\n
\t\t\t\tthis.containers[i].containerCache.left = p.left;\n
\t\t\t\tthis.containers[i].containerCache.top = p.top;\n
\t\t\t\tthis.containers[i].containerCache.width\t= this.containers[i].element.outerWidth();\n
\t\t\t\tthis.containers[i].containerCache.height = this.containers[i].element.outerHeight();\n
\t\t\t};\n
\t\t}\n
\n
\t},\n
\n
\t_createPlaceholder: function(that) {\n
\n
\t\tvar self = that || this, o = self.options;\n
\n
\t\tif(!o.placeholder || o.placeholder.constructor == String) {\n
\t\t\tvar className = o.placeholder;\n
\t\t\to.placeholder = {\n
\t\t\t\telement: function() {\n
\n
\t\t\t\t\tvar el = $(document.createElement(self.currentItem[0].nodeName))\n
\t\t\t\t\t\t.addClass(className || self.currentItem[0].className+" ui-sortable-placeholder")\n
\t\t\t\t\t\t.removeClass("ui-sortable-helper")[0];\n
\n
\t\t\t\t\tif(!className)\n
\t\t\t\t\t\tel.style.visibility = "hidden";\n
\n
\t\t\t\t\treturn el;\n
\t\t\t\t},\n
\t\t\t\tupdate: function(container, p) {\n
\n
\t\t\t\t\t// 1. If a className is set as \'placeholder option, we don\'t force sizes - the class is responsible for that\n
\t\t\t\t\t// 2. The option \'forcePlaceholderSize can be enabled to force it even if a class name is specified\n
\t\t\t\t\tif(className && !o.forcePlaceholderSize) return;\n
\n
\t\t\t\t\t//If the element doesn\'t have a actual height by itself (without styles coming from a stylesheet), it receives the inline height from the dragged item\n
\t\t\t\t\tif(!p.height()) { p.height(self.currentItem.innerHeight() - parseInt(self.currentItem.css(\'paddingTop\')||0, 10) - parseInt(self.currentItem.css(\'paddingBottom\')||0, 10)); };\n
\t\t\t\t\tif(!p.width()) { p.width(self.currentItem.innerWidth() - parseInt(self.currentItem.css(\'paddingLeft\')||0, 10) - parseInt(self.currentItem.css(\'paddingRight\')||0, 10)); };\n
\t\t\t\t}\n
\t\t\t};\n
\t\t}\n
\n
\t\t//Create the placeholder\n
\t\tself.placeholder = $(o.placeholder.element.call(self.element, self.currentItem));\n
\n
\t\t//Append it after the actual current item\n
\t\tself.currentItem.after(self.placeholder);\n
\n
\t\t//Update the size of the placeholder (TODO: Logic to fuzzy, see line 316/317)\n
\t\to.placeholder.update(self, self.placeholder);\n
\n
\t},\n
\n
\t_contactContainers: function(event) {\n
\t\tfor (var i = this.containers.length - 1; i >= 0; i--){\n
\n
\t\t\tif(this._intersectsWith(this.containers[i].containerCache)) {\n
\t\t\t\tif(!this.containers[i].containerCache.over) {\n
\n
\t\t\t\t\tif(this.currentContainer != this.containers[i]) {\n
\n
\t\t\t\t\t\t//When entering a new container, we will find the item with the least distance and append our item near it\n
\t\t\t\t\t\tvar dist = 10000; var itemWithLeastDistance = null; var base = this.positionAbs[this.containers[i].floating ? \'left\' : \'top\'];\n
\t\t\t\t\t\tfor (var j = this.items.length - 1; j >= 0; j--) {\n
\t\t\t\t\t\t\tif(!$.ui.contains(this.containers[i].element[0], this.items[j].item[0])) continue;\n
\t\t\t\t\t\t\tvar cur = this.items[j][this.containers[i].floating ? \'left\' : \'top\'];\n
\t\t\t\t\t\t\tif(Math.abs(cur - base) < dist) {\n
\t\t\t\t\t\t\t\tdist = Math.abs(cur - base); itemWithLeastDistance = this.items[j];\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tif(!itemWithLeastDistance && !this.options.dropOnEmpty) //Check if dropOnEmpty is enabled\n
\t\t\t\t\t\t\tcontinue;\n
\n
\t\t\t\t\t\tthis.currentContainer = this.containers[i];\n
\t\t\t\t\t\titemWithLeastDistance ? this._rearrange(event, itemWithLeastDistance, null, true) : this._rearrange(event, null, this.containers[i].element, true);\n
\t\t\t\t\t\tthis._trigger("change", event, this._uiHash());\n
\t\t\t\t\t\tthis.containers[i]._trigger("change", event, this._uiHash(this));\n
\n
\t\t\t\t\t\t//Update the placeholder\n
\t\t\t\t\t\tthis.options.placeholder.update(this.currentContainer, this.placeholder);\n
\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tthis.containers[i]._trigger("over", event, this._uiHash(this));\n
\t\t\t\t\tthis.containers[i].containerCache.over = 1;\n
\t\t\t\t}\n
\t\t\t} else {\n
\t\t\t\tif(this.containers[i].containerCache.over) {\n
\t\t\t\t\tthis.containers[i]._trigger("out", event, this._uiHash(this));\n
\t\t\t\t\tthis.containers[i].containerCache.over = 0;\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t};\n
\t},\n
\n
\t_createHelper: function(event) {\n
\n
\t\tvar o = this.options;\n
\t\tvar helper = $.isFunction(o.helper) ? $(o.helper.apply(this.element[0], [event, this.currentItem])) : (o.helper == \'clone\' ? this.currentItem.clone() : this.currentItem);\n
\n
\t\tif(!helper.parents(\'body\').length) //Add the helper to the DOM if that didn\'t happen already\n
\t\t\t$(o.appendTo != \'parent\' ? o.appendTo : this.currentItem[0].parentNode)[0].appendChild(helper[0]);\n
\n
\t\tif(helper[0] == this.currentItem[0])\n
\t\t\tthis._storedCSS = { width: this.currentItem[0].style.width, height: this.currentItem[0].style.height, position: this.currentItem.css("position"), top: this.currentItem.css("top"), left: this.currentItem.css("left") };\n
\n
\t\tif(helper[0].style.width == \'\' || o.forceHelperSize) helper.width(this.currentItem.width());\n
\t\tif(helper[0].style.height == \'\' || o.forceHelperSize) helper.height(this.currentItem.height());\n
\n
\t\treturn helper;\n
\n
\t},\n
\n
\t_adjustOffsetFromHelper: function(obj) {\n
\t\tif(obj.left != undefined) this.offset.click.left = obj.left + this.margins.left;\n
\t\tif(obj.right != undefined) this.offset.click.left = this.helperProportions.width - obj.right + this.margins.left;\n
\t\tif(obj.top != undefined) this.offset.click.top = obj.top + this.margins.top;\n
\t\tif(obj.bottom != undefined) this.offset.click.top = this.helperProportions.height - obj.bottom + this.margins.top;\n
\t},\n
\n
\t_getParentOffset: function() {\n
\n
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
\t\t\tvar p = this.currentItem.position();\n
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
\t\t\tleft: (parseInt(this.currentItem.css("marginLeft"),10) || 0),\n
\t\t\ttop: (parseInt(this.currentItem.css("marginTop"),10) || 0)\n
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
\t\tif(!(/^(document|window|parent)$/).test(o.containment)) {\n
\t\t\tvar ce = $(o.containment)[0];\n
\t\t\tvar co = $(o.containment).offset();\n
\t\t\tvar over = ($(ce).css("overflow") != \'hidden\');\n
\n
\t\t\tthis.containment = [\n
\t\t\t\tco.left + (parseInt($(ce).css("borderLeftWidth"),10) || 0) + (parseInt($(ce).css("paddingLeft"),10) || 0) - this.margins.left,\n
\t\t\t\tco.top + (parseInt($(ce).css("borderTopWidth"),10) || 0) + (parseInt($(ce).css("paddingTop"),10) || 0) - this.margins.top,\n
\t\t\t\tco.left+(over ? Math.max(ce.scrollWidth,ce.offsetWidth) : ce.offsetWidth) - (parseInt($(ce).css("borderLeftWidth"),10) || 0) - (parseInt($(ce).css("paddingRight"),10) || 0) - this.helperProportions.width - this.margins.left,\n
\t\t\t\tco.top+(over ? Math.max(ce.scrollHeight,ce.offsetHeight) : ce.offsetHeight) - (parseInt($(ce).css("borderTopWidth"),10) || 0) - (parseInt($(ce).css("paddingBottom"),10) || 0) - this.helperProportions.height - this.margins.top\n
\t\t\t];\n
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
\t\t\t\t- ($.browser.safari && this.cssPosition == \'fixed\' ? 0 : ( this.cssPosition == \'fixed\' ? -this.scrollParent.scrollTop() : ( scrollIsRootNode ? 0 : scroll.scrollTop() ) ) * mod)\n
\t\t\t),\n
\t\t\tleft: (\n
\t\t\t\tpos.left\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t// The absolute mouse position\n
\t\t\t\t+ this.offset.relative.left * mod\t\t\t\t\t\t\t\t\t\t// Only for relative positioned nodes: Relative offset from element to offset parent\n
\t\t\t\t+ this.offset.parent.left * mod\t\t\t\t\t\t\t\t\t\t\t// The offsetParent\'s offset without borders (offset + border)\n
\t\t\t\t- ($.browser.safari && this.cssPosition == \'fixed\' ? 0 : ( this.cssPosition == \'fixed\' ? -this.scrollParent.scrollLeft() : scrollIsRootNode ? 0 : scroll.scrollLeft() ) * mod)\n
\t\t\t)\n
\t\t};\n
\n
\t},\n
\n
\t_generatePosition: function(event) {\n
\n
\t\tvar o = this.options, scroll = this.cssPosition == \'absolute\' && !(this.scrollParent[0] != document && $.ui.contains(this.scrollParent[0], this.offsetParent[0])) ? this.offsetParent : this.scrollParent, scrollIsRootNode = (/(html|body)/i).test(scroll[0].tagName);\n
\n
\t\t// This is another very weird special case that only happens for relative elements:\n
\t\t// 1. If the css position is relative\n
\t\t// 2. and the scroll parent is the document or similar to the offset parent\n
\t\t// we have to refresh the relative offset during the scroll so there are no jumps\n
\t\tif(this.cssPosition == \'relative\' && !(this.scrollParent[0] != document && this.scrollParent[0] != this.offsetParent[0])) {\n
\t\t\tthis.offset.relative = this._getRelativeOffset();\n
\t\t}\n
\n
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
\t\t\t\t+ ($.browser.safari && this.cssPosition == \'fixed\' ? 0 : ( this.cssPosition == \'fixed\' ? -this.scrollParent.scrollTop() : ( scrollIsRootNode ? 0 : scroll.scrollTop() ) ))\n
\t\t\t),\n
\t\t\tleft: (\n
\t\t\t\tpageX\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t// The absolute mouse position\n
\t\t\t\t- this.offset.click.left\t\t\t\t\t\t\t\t\t\t\t\t// Click offset (relative to the element)\n
\t\t\t\t- this.offset.relative.left\t\t\t\t\t\t\t\t\t\t\t\t// Only for relative positioned nodes: Relative offset from element to offset parent\n
\t\t\t\t- this.offset.parent.left\t\t\t\t\t\t\t\t\t\t\t\t// The offsetParent\'s offset without borders (offset + border)\n
\t\t\t\t+ ($.browser.safari && this.cssPosition == \'fixed\' ? 0 : ( this.cssPosition == \'fixed\' ? -this.scrollParent.scrollLeft() : scrollIsRootNode ? 0 : scroll.scrollLeft() ))\n
\t\t\t)\n
\t\t};\n
\n
\t},\n
\n
\t_rearrange: function(event, i, a, hardRefresh) {\n
\n
\t\ta ? a[0].appendChild(this.placeholder[0]) : i.item[0].parentNode.insertBefore(this.placeholder[0], (this.direction == \'down\' ? i.item[0] : i.item[0].nextSibling));\n
\n
\t\t//Various things done here to improve the performance:\n
\t\t// 1. we create a setTimeout, that calls refreshPositions\n
\t\t// 2. on the instance, we have a counter variable, that get\'s higher after every append\n
\t\t// 3. on the local scope, we copy the counter variable, and check in the timeout, if it\'s still the same\n
\t\t// 4. this lets only the last addition to the timeout stack through\n
\t\tthis.counter = this.counter ? ++this.counter : 1;\n
\t\tvar self = this, counter = this.counter;\n
\n
\t\twindow.setTimeout(function() {\n
\t\t\tif(counter == self.counter) self.refreshPositions(!hardRefresh); //Precompute after each DOM insertion, NOT on mousemove\n
\t\t},0);\n
\n
\t},\n
\n
\t_clear: function(event, noPropagation) {\n
\n
\t\tthis.reverting = false;\n
\t\t// We delay all events that have to be triggered to after the point where the placeholder has been removed and\n
\t\t// everything else normalized again\n
\t\tvar delayedTriggers = [], self = this;\n
\n
\t\t// We first have to update the dom position of the actual currentItem\n
\t\t// Note: don\'t do it if the current item is already removed (by a user), or it gets reappended (see #4088)\n
\t\tif(!this._noFinalSort && this.currentItem[0].parentNode) this.placeholder.before(this.currentItem);\n
\t\tthis._noFinalSort = null;\n
\n
\t\tif(this.helper[0] == this.currentItem[0]) {\n
\t\t\tfor(var i in this._storedCSS) {\n
\t\t\t\tif(this._storedCSS[i] == \'auto\' || this._storedCSS[i] == \'static\') this._storedCSS[i] = \'\';\n
\t\t\t}\n
\t\t\tthis.currentItem.css(this._storedCSS).removeClass("ui-sortable-helper");\n
\t\t} else {\n
\t\t\tthis.currentItem.show();\n
\t\t}\n
\n
\t\tif(this.fromOutside && !noPropagation) delayedTriggers.push(function(event) { this._trigger("receive", event, this._uiHash(this.fromOutside)); });\n
\t\tif((this.fromOutside || this.domPosition.prev != this.currentItem.prev().not(".ui-sortable-helper")[0] || this.domPosition.parent != this.currentItem.parent()[0]) && !noPropagation) delayedTriggers.push(function(event) { this._trigger("update", event, this._uiHash()); }); //Trigger update callback if the DOM position has changed\n
\t\tif(!$.ui.contains(this.element[0], this.currentItem[0])) { //Node was moved out of the current element\n
\t\t\tif(!noPropagation) delayedTriggers.push(function(event) { this._trigger("remove", event, this._uiHash()); });\n
\t\t\tfor (var i = this.containers.length - 1; i >= 0; i--){\n
\t\t\t\tif($.ui.contains(this.containers[i].element[0], this.currentItem[0]) && !noPropagation) {\n
\t\t\t\t\tdelayedTriggers.push((function(c) { return function(event) { c._trigger("receive", event, this._uiHash(this)); };  }).call(this, this.containers[i]));\n
\t\t\t\t\tdelayedTriggers.push((function(c) { return function(event) { c._trigger("update", event, this._uiHash(this));  }; }).call(this, this.containers[i]));\n
\t\t\t\t}\n
\t\t\t};\n
\t\t};\n
\n
\t\t//Post events to containers\n
\t\tfor (var i = this.containers.length - 1; i >= 0; i--){\n
\t\t\tif(!noPropagation) delayedTriggers.push((function(c) { return function(event) { c._trigger("deactivate", event, this._uiHash(this)); };  }).call(this, this.containers[i]));\n
\t\t\tif(this.containers[i].containerCache.over) {\n
\t\t\t\tdelayedTriggers.push((function(c) { return function(event) { c._trigger("out", event, this._uiHash(this)); };  }).call(this, this.containers[i]));\n
\t\t\t\tthis.containers[i].containerCache.over = 0;\n
\t\t\t}\n
\t\t}\n
\n
\t\t//Do what was originally in plugins\n
\t\tif(this._storedCursor) $(\'body\').css("cursor", this._storedCursor); //Reset cursor\n
\t\tif(this._storedOpacity) this.helper.css("opacity", this._storedOpacity); //Reset cursor\n
\t\tif(this._storedZIndex) this.helper.css("zIndex", this._storedZIndex == \'auto\' ? \'\' : this._storedZIndex); //Reset z-index\n
\n
\t\tthis.dragging = false;\n
\t\tif(this.cancelHelperRemoval) {\n
\t\t\tif(!noPropagation) {\n
\t\t\t\tthis._trigger("beforeStop", event, this._uiHash());\n
\t\t\t\tfor (var i=0; i < delayedTriggers.length; i++) { delayedTriggers[i].call(this, event); }; //Trigger all delayed events\n
\t\t\t\tthis._trigger("stop", event, this._uiHash());\n
\t\t\t}\n
\t\t\treturn false;\n
\t\t}\n
\n
\t\tif(!noPropagation) this._trigger("beforeStop", event, this._uiHash());\n
\n
\t\t//$(this.placeholder[0]).remove(); would have been the jQuery way - unfortunately, it unbinds ALL events from the original node!\n
\t\tthis.placeholder[0].parentNode.removeChild(this.placeholder[0]);\n
\n
\t\tif(this.helper[0] != this.currentItem[0]) this.helper.remove(); this.helper = null;\n
\n
\t\tif(!noPropagation) {\n
\t\t\tfor (var i=0; i < delayedTriggers.length; i++) { delayedTriggers[i].call(this, event); }; //Trigger all delayed events\n
\t\t\tthis._trigger("stop", event, this._uiHash());\n
\t\t}\n
\n
\t\tthis.fromOutside = false;\n
\t\treturn true;\n
\n
\t},\n
\n
\t_trigger: function() {\n
\t\tif ($.widget.prototype._trigger.apply(this, arguments) === false) {\n
\t\t\tthis.cancel();\n
\t\t}\n
\t},\n
\n
\t_uiHash: function(inst) {\n
\t\tvar self = inst || this;\n
\t\treturn {\n
\t\t\thelper: self.helper,\n
\t\t\tplaceholder: self.placeholder || $([]),\n
\t\t\tposition: self.position,\n
\t\t\tabsolutePosition: self.positionAbs, //deprecated\n
\t\t\toffset: self.positionAbs,\n
\t\t\titem: self.currentItem,\n
\t\t\tsender: inst ? inst.element : null\n
\t\t};\n
\t}\n
\n
}));\n
\n
$.extend($.ui.sortable, {\n
\tgetter: "serialize toArray",\n
\tversion: "1.7.2",\n
\teventPrefix: "sort",\n
\tdefaults: {\n
\t\tappendTo: "parent",\n
\t\taxis: false,\n
\t\tcancel: ":input,option",\n
\t\tconnectWith: false,\n
\t\tcontainment: false,\n
\t\tcursor: \'auto\',\n
\t\tcursorAt: false,\n
\t\tdelay: 0,\n
\t\tdistance: 1,\n
\t\tdropOnEmpty: true,\n
\t\tforcePlaceholderSize: false,\n
\t\tforceHelperSize: false,\n
\t\tgrid: false,\n
\t\thandle: false,\n
\t\thelper: "original",\n
\t\titems: \'> *\',\n
\t\topacity: false,\n
\t\tplaceholder: false,\n
\t\trevert: false,\n
\t\tscroll: true,\n
\t\tscrollSensitivity: 20,\n
\t\tscrollSpeed: 20,\n
\t\tscope: "default",\n
\t\ttolerance: "intersect",\n
\t\tzIndex: 1000\n
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
            <value> <long>38040</long> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
