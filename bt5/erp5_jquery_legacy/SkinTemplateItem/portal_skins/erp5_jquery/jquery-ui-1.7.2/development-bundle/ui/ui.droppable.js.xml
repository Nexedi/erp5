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
            <value> <string>ts65545394.47</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ui.droppable.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Droppable 1.7.2\n
 *\n
 * Copyright (c) 2009 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Droppables\n
 *\n
 * Depends:\n
 *\tui.core.js\n
 *\tui.draggable.js\n
 */\n
(function($) {\n
\n
$.widget("ui.droppable", {\n
\n
\t_init: function() {\n
\n
\t\tvar o = this.options, accept = o.accept;\n
\t\tthis.isover = 0; this.isout = 1;\n
\n
\t\tthis.options.accept = this.options.accept && $.isFunction(this.options.accept) ? this.options.accept : function(d) {\n
\t\t\treturn d.is(accept);\n
\t\t};\n
\n
\t\t//Store the droppable\'s proportions\n
\t\tthis.proportions = { width: this.element[0].offsetWidth, height: this.element[0].offsetHeight };\n
\n
\t\t// Add the reference and positions to the manager\n
\t\t$.ui.ddmanager.droppables[this.options.scope] = $.ui.ddmanager.droppables[this.options.scope] || [];\n
\t\t$.ui.ddmanager.droppables[this.options.scope].push(this);\n
\n
\t\t(this.options.addClasses && this.element.addClass("ui-droppable"));\n
\n
\t},\n
\n
\tdestroy: function() {\n
\t\tvar drop = $.ui.ddmanager.droppables[this.options.scope];\n
\t\tfor ( var i = 0; i < drop.length; i++ )\n
\t\t\tif ( drop[i] == this )\n
\t\t\t\tdrop.splice(i, 1);\n
\n
\t\tthis.element\n
\t\t\t.removeClass("ui-droppable ui-droppable-disabled")\n
\t\t\t.removeData("droppable")\n
\t\t\t.unbind(".droppable");\n
\t},\n
\n
\t_setData: function(key, value) {\n
\n
\t\tif(key == \'accept\') {\n
\t\t\tthis.options.accept = value && $.isFunction(value) ? value : function(d) {\n
\t\t\t\treturn d.is(value);\n
\t\t\t};\n
\t\t} else {\n
\t\t\t$.widget.prototype._setData.apply(this, arguments);\n
\t\t}\n
\n
\t},\n
\n
\t_activate: function(event) {\n
\t\tvar draggable = $.ui.ddmanager.current;\n
\t\tif(this.options.activeClass) this.element.addClass(this.options.activeClass);\n
\t\t(draggable && this._trigger(\'activate\', event, this.ui(draggable)));\n
\t},\n
\n
\t_deactivate: function(event) {\n
\t\tvar draggable = $.ui.ddmanager.current;\n
\t\tif(this.options.activeClass) this.element.removeClass(this.options.activeClass);\n
\t\t(draggable && this._trigger(\'deactivate\', event, this.ui(draggable)));\n
\t},\n
\n
\t_over: function(event) {\n
\n
\t\tvar draggable = $.ui.ddmanager.current;\n
\t\tif (!draggable || (draggable.currentItem || draggable.element)[0] == this.element[0]) return; // Bail if draggable and droppable are same element\n
\n
\t\tif (this.options.accept.call(this.element[0],(draggable.currentItem || draggable.element))) {\n
\t\t\tif(this.options.hoverClass) this.element.addClass(this.options.hoverClass);\n
\t\t\tthis._trigger(\'over\', event, this.ui(draggable));\n
\t\t}\n
\n
\t},\n
\n
\t_out: function(event) {\n
\n
\t\tvar draggable = $.ui.ddmanager.current;\n
\t\tif (!draggable || (draggable.currentItem || draggable.element)[0] == this.element[0]) return; // Bail if draggable and droppable are same element\n
\n
\t\tif (this.options.accept.call(this.element[0],(draggable.currentItem || draggable.element))) {\n
\t\t\tif(this.options.hoverClass) this.element.removeClass(this.options.hoverClass);\n
\t\t\tthis._trigger(\'out\', event, this.ui(draggable));\n
\t\t}\n
\n
\t},\n
\n
\t_drop: function(event,custom) {\n
\n
\t\tvar draggable = custom || $.ui.ddmanager.current;\n
\t\tif (!draggable || (draggable.currentItem || draggable.element)[0] == this.element[0]) return false; // Bail if draggable and droppable are same element\n
\n
\t\tvar childrenIntersection = false;\n
\t\tthis.element.find(":data(droppable)").not(".ui-draggable-dragging").each(function() {\n
\t\t\tvar inst = $.data(this, \'droppable\');\n
\t\t\tif(inst.options.greedy && $.ui.intersect(draggable, $.extend(inst, { offset: inst.element.offset() }), inst.options.tolerance)) {\n
\t\t\t\tchildrenIntersection = true; return false;\n
\t\t\t}\n
\t\t});\n
\t\tif(childrenIntersection) return false;\n
\n
\t\tif(this.options.accept.call(this.element[0],(draggable.currentItem || draggable.element))) {\n
\t\t\tif(this.options.activeClass) this.element.removeClass(this.options.activeClass);\n
\t\t\tif(this.options.hoverClass) this.element.removeClass(this.options.hoverClass);\n
\t\t\tthis._trigger(\'drop\', event, this.ui(draggable));\n
\t\t\treturn this.element;\n
\t\t}\n
\n
\t\treturn false;\n
\n
\t},\n
\n
\tui: function(c) {\n
\t\treturn {\n
\t\t\tdraggable: (c.currentItem || c.element),\n
\t\t\thelper: c.helper,\n
\t\t\tposition: c.position,\n
\t\t\tabsolutePosition: c.positionAbs, //deprecated\n
\t\t\toffset: c.positionAbs\n
\t\t};\n
\t}\n
\n
});\n
\n
$.extend($.ui.droppable, {\n
\tversion: "1.7.2",\n
\teventPrefix: \'drop\',\n
\tdefaults: {\n
\t\taccept: \'*\',\n
\t\tactiveClass: false,\n
\t\taddClasses: true,\n
\t\tgreedy: false,\n
\t\thoverClass: false,\n
\t\tscope: \'default\',\n
\t\ttolerance: \'intersect\'\n
\t}\n
});\n
\n
$.ui.intersect = function(draggable, droppable, toleranceMode) {\n
\n
\tif (!droppable.offset) return false;\n
\n
\tvar x1 = (draggable.positionAbs || draggable.position.absolute).left, x2 = x1 + draggable.helperProportions.width,\n
\t\ty1 = (draggable.positionAbs || draggable.position.absolute).top, y2 = y1 + draggable.helperProportions.height;\n
\tvar l = droppable.offset.left, r = l + droppable.proportions.width,\n
\t\tt = droppable.offset.top, b = t + droppable.proportions.height;\n
\n
\tswitch (toleranceMode) {\n
\t\tcase \'fit\':\n
\t\t\treturn (l < x1 && x2 < r\n
\t\t\t\t&& t < y1 && y2 < b);\n
\t\t\tbreak;\n
\t\tcase \'intersect\':\n
\t\t\treturn (l < x1 + (draggable.helperProportions.width / 2) // Right Half\n
\t\t\t\t&& x2 - (draggable.helperProportions.width / 2) < r // Left Half\n
\t\t\t\t&& t < y1 + (draggable.helperProportions.height / 2) // Bottom Half\n
\t\t\t\t&& y2 - (draggable.helperProportions.height / 2) < b ); // Top Half\n
\t\t\tbreak;\n
\t\tcase \'pointer\':\n
\t\t\tvar draggableLeft = ((draggable.positionAbs || draggable.position.absolute).left + (draggable.clickOffset || draggable.offset.click).left),\n
\t\t\t\tdraggableTop = ((draggable.positionAbs || draggable.position.absolute).top + (draggable.clickOffset || draggable.offset.click).top),\n
\t\t\t\tisOver = $.ui.isOver(draggableTop, draggableLeft, t, l, droppable.proportions.height, droppable.proportions.width);\n
\t\t\treturn isOver;\n
\t\t\tbreak;\n
\t\tcase \'touch\':\n
\t\t\treturn (\n
\t\t\t\t\t(y1 >= t && y1 <= b) ||\t// Top edge touching\n
\t\t\t\t\t(y2 >= t && y2 <= b) ||\t// Bottom edge touching\n
\t\t\t\t\t(y1 < t && y2 > b)\t\t// Surrounded vertically\n
\t\t\t\t) && (\n
\t\t\t\t\t(x1 >= l && x1 <= r) ||\t// Left edge touching\n
\t\t\t\t\t(x2 >= l && x2 <= r) ||\t// Right edge touching\n
\t\t\t\t\t(x1 < l && x2 > r)\t\t// Surrounded horizontally\n
\t\t\t\t);\n
\t\t\tbreak;\n
\t\tdefault:\n
\t\t\treturn false;\n
\t\t\tbreak;\n
\t\t}\n
\n
};\n
\n
/*\n
\tThis manager tracks offsets of draggables and droppables\n
*/\n
$.ui.ddmanager = {\n
\tcurrent: null,\n
\tdroppables: { \'default\': [] },\n
\tprepareOffsets: function(t, event) {\n
\n
\t\tvar m = $.ui.ddmanager.droppables[t.options.scope];\n
\t\tvar type = event ? event.type : null; // workaround for #2317\n
\t\tvar list = (t.currentItem || t.element).find(":data(droppable)").andSelf();\n
\n
\t\tdroppablesLoop: for (var i = 0; i < m.length; i++) {\n
\n
\t\t\tif(m[i].options.disabled || (t && !m[i].options.accept.call(m[i].element[0],(t.currentItem || t.element)))) continue;\t//No disabled and non-accepted\n
\t\t\tfor (var j=0; j < list.length; j++) { if(list[j] == m[i].element[0]) { m[i].proportions.height = 0; continue droppablesLoop; } }; //Filter out elements in the current dragged item\n
\t\t\tm[i].visible = m[i].element.css("display") != "none"; if(!m[i].visible) continue; \t\t\t\t\t\t\t\t\t//If the element is not visible, continue\n
\n
\t\t\tm[i].offset = m[i].element.offset();\n
\t\t\tm[i].proportions = { width: m[i].element[0].offsetWidth, height: m[i].element[0].offsetHeight };\n
\n
\t\t\tif(type == "mousedown") m[i]._activate.call(m[i], event); //Activate the droppable if used directly from draggables\n
\n
\t\t}\n
\n
\t},\n
\tdrop: function(draggable, event) {\n
\n
\t\tvar dropped = false;\n
\t\t$.each($.ui.ddmanager.droppables[draggable.options.scope], function() {\n
\n
\t\t\tif(!this.options) return;\n
\t\t\tif (!this.options.disabled && this.visible && $.ui.intersect(draggable, this, this.options.tolerance))\n
\t\t\t\tdropped = this._drop.call(this, event);\n
\n
\t\t\tif (!this.options.disabled && this.visible && this.options.accept.call(this.element[0],(draggable.currentItem || draggable.element))) {\n
\t\t\t\tthis.isout = 1; this.isover = 0;\n
\t\t\t\tthis._deactivate.call(this, event);\n
\t\t\t}\n
\n
\t\t});\n
\t\treturn dropped;\n
\n
\t},\n
\tdrag: function(draggable, event) {\n
\n
\t\t//If you have a highly dynamic page, you might try this option. It renders positions every time you move the mouse.\n
\t\tif(draggable.options.refreshPositions) $.ui.ddmanager.prepareOffsets(draggable, event);\n
\n
\t\t//Run through all droppables and check their positions based on specific tolerance options\n
\n
\t\t$.each($.ui.ddmanager.droppables[draggable.options.scope], function() {\n
\n
\t\t\tif(this.options.disabled || this.greedyChild || !this.visible) return;\n
\t\t\tvar intersects = $.ui.intersect(draggable, this, this.options.tolerance);\n
\n
\t\t\tvar c = !intersects && this.isover == 1 ? \'isout\' : (intersects && this.isover == 0 ? \'isover\' : null);\n
\t\t\tif(!c) return;\n
\n
\t\t\tvar parentInstance;\n
\t\t\tif (this.options.greedy) {\n
\t\t\t\tvar parent = this.element.parents(\':data(droppable):eq(0)\');\n
\t\t\t\tif (parent.length) {\n
\t\t\t\t\tparentInstance = $.data(parent[0], \'droppable\');\n
\t\t\t\t\tparentInstance.greedyChild = (c == \'isover\' ? 1 : 0);\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t// we just moved into a greedy child\n
\t\t\tif (parentInstance && c == \'isover\') {\n
\t\t\t\tparentInstance[\'isover\'] = 0;\n
\t\t\t\tparentInstance[\'isout\'] = 1;\n
\t\t\t\tparentInstance._out.call(parentInstance, event);\n
\t\t\t}\n
\n
\t\t\tthis[c] = 1; this[c == \'isout\' ? \'isover\' : \'isout\'] = 0;\n
\t\t\tthis[c == "isover" ? "_over" : "_out"].call(this, event);\n
\n
\t\t\t// we just moved out of a greedy child\n
\t\t\tif (parentInstance && c == \'isout\') {\n
\t\t\t\tparentInstance[\'isout\'] = 0;\n
\t\t\t\tparentInstance[\'isover\'] = 1;\n
\t\t\t\tparentInstance._over.call(parentInstance, event);\n
\t\t\t}\n
\t\t});\n
\n
\t}\n
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
            <value> <long>9373</long> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
