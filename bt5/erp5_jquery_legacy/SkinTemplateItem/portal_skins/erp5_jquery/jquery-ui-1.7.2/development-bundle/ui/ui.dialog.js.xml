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
            <value> <string>ts65545394.37</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ui.dialog.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Dialog 1.7.2\n
 *\n
 * Copyright (c) 2009 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Dialog\n
 *\n
 * Depends:\n
 *\tui.core.js\n
 *\tui.draggable.js\n
 *\tui.resizable.js\n
 */\n
(function($) {\n
\n
var setDataSwitch = {\n
\t\tdragStart: "start.draggable",\n
\t\tdrag: "drag.draggable",\n
\t\tdragStop: "stop.draggable",\n
\t\tmaxHeight: "maxHeight.resizable",\n
\t\tminHeight: "minHeight.resizable",\n
\t\tmaxWidth: "maxWidth.resizable",\n
\t\tminWidth: "minWidth.resizable",\n
\t\tresizeStart: "start.resizable",\n
\t\tresize: "drag.resizable",\n
\t\tresizeStop: "stop.resizable"\n
\t},\n
\t\n
\tuiDialogClasses =\n
\t\t\'ui-dialog \' +\n
\t\t\'ui-widget \' +\n
\t\t\'ui-widget-content \' +\n
\t\t\'ui-corner-all \';\n
\n
$.widget("ui.dialog", {\n
\n
\t_init: function() {\n
\t\tthis.originalTitle = this.element.attr(\'title\');\n
\n
\t\tvar self = this,\n
\t\t\toptions = this.options,\n
\n
\t\t\ttitle = options.title || this.originalTitle || \'&nbsp;\',\n
\t\t\ttitleId = $.ui.dialog.getTitleId(this.element),\n
\n
\t\t\tuiDialog = (this.uiDialog = $(\'<div/>\'))\n
\t\t\t\t.appendTo(document.body)\n
\t\t\t\t.hide()\n
\t\t\t\t.addClass(uiDialogClasses + options.dialogClass)\n
\t\t\t\t.css({\n
\t\t\t\t\tposition: \'absolute\',\n
\t\t\t\t\toverflow: \'hidden\',\n
\t\t\t\t\tzIndex: options.zIndex\n
\t\t\t\t})\n
\t\t\t\t// setting tabIndex makes the div focusable\n
\t\t\t\t// setting outline to 0 prevents a border on focus in Mozilla\n
\t\t\t\t.attr(\'tabIndex\', -1).css(\'outline\', 0).keydown(function(event) {\n
\t\t\t\t\t(options.closeOnEscape && event.keyCode\n
\t\t\t\t\t\t&& event.keyCode == $.ui.keyCode.ESCAPE && self.close(event));\n
\t\t\t\t})\n
\t\t\t\t.attr({\n
\t\t\t\t\trole: \'dialog\',\n
\t\t\t\t\t\'aria-labelledby\': titleId\n
\t\t\t\t})\n
\t\t\t\t.mousedown(function(event) {\n
\t\t\t\t\tself.moveToTop(false, event);\n
\t\t\t\t}),\n
\n
\t\t\tuiDialogContent = this.element\n
\t\t\t\t.show()\n
\t\t\t\t.removeAttr(\'title\')\n
\t\t\t\t.addClass(\n
\t\t\t\t\t\'ui-dialog-content \' +\n
\t\t\t\t\t\'ui-widget-content\')\n
\t\t\t\t.appendTo(uiDialog),\n
\n
\t\t\tuiDialogTitlebar = (this.uiDialogTitlebar = $(\'<div></div>\'))\n
\t\t\t\t.addClass(\n
\t\t\t\t\t\'ui-dialog-titlebar \' +\n
\t\t\t\t\t\'ui-widget-header \' +\n
\t\t\t\t\t\'ui-corner-all \' +\n
\t\t\t\t\t\'ui-helper-clearfix\'\n
\t\t\t\t)\n
\t\t\t\t.prependTo(uiDialog),\n
\n
\t\t\tuiDialogTitlebarClose = $(\'<a href="#"/>\')\n
\t\t\t\t.addClass(\n
\t\t\t\t\t\'ui-dialog-titlebar-close \' +\n
\t\t\t\t\t\'ui-corner-all\'\n
\t\t\t\t)\n
\t\t\t\t.attr(\'role\', \'button\')\n
\t\t\t\t.hover(\n
\t\t\t\t\tfunction() {\n
\t\t\t\t\t\tuiDialogTitlebarClose.addClass(\'ui-state-hover\');\n
\t\t\t\t\t},\n
\t\t\t\t\tfunction() {\n
\t\t\t\t\t\tuiDialogTitlebarClose.removeClass(\'ui-state-hover\');\n
\t\t\t\t\t}\n
\t\t\t\t)\n
\t\t\t\t.focus(function() {\n
\t\t\t\t\tuiDialogTitlebarClose.addClass(\'ui-state-focus\');\n
\t\t\t\t})\n
\t\t\t\t.blur(function() {\n
\t\t\t\t\tuiDialogTitlebarClose.removeClass(\'ui-state-focus\');\n
\t\t\t\t})\n
\t\t\t\t.mousedown(function(ev) {\n
\t\t\t\t\tev.stopPropagation();\n
\t\t\t\t})\n
\t\t\t\t.click(function(event) {\n
\t\t\t\t\tself.close(event);\n
\t\t\t\t\treturn false;\n
\t\t\t\t})\n
\t\t\t\t.appendTo(uiDialogTitlebar),\n
\n
\t\t\tuiDialogTitlebarCloseText = (this.uiDialogTitlebarCloseText = $(\'<span/>\'))\n
\t\t\t\t.addClass(\n
\t\t\t\t\t\'ui-icon \' +\n
\t\t\t\t\t\'ui-icon-closethick\'\n
\t\t\t\t)\n
\t\t\t\t.text(options.closeText)\n
\t\t\t\t.appendTo(uiDialogTitlebarClose),\n
\n
\t\t\tuiDialogTitle = $(\'<span/>\')\n
\t\t\t\t.addClass(\'ui-dialog-title\')\n
\t\t\t\t.attr(\'id\', titleId)\n
\t\t\t\t.html(title)\n
\t\t\t\t.prependTo(uiDialogTitlebar);\n
\n
\t\tuiDialogTitlebar.find("*").add(uiDialogTitlebar).disableSelection();\n
\n
\t\t(options.draggable && $.fn.draggable && this._makeDraggable());\n
\t\t(options.resizable && $.fn.resizable && this._makeResizable());\n
\n
\t\tthis._createButtons(options.buttons);\n
\t\tthis._isOpen = false;\n
\n
\t\t(options.bgiframe && $.fn.bgiframe && uiDialog.bgiframe());\n
\t\t(options.autoOpen && this.open());\n
\t\t\n
\t},\n
\n
\tdestroy: function() {\n
\t\t(this.overlay && this.overlay.destroy());\n
\t\tthis.uiDialog.hide();\n
\t\tthis.element\n
\t\t\t.unbind(\'.dialog\')\n
\t\t\t.removeData(\'dialog\')\n
\t\t\t.removeClass(\'ui-dialog-content ui-widget-content\')\n
\t\t\t.hide().appendTo(\'body\');\n
\t\tthis.uiDialog.remove();\n
\n
\t\t(this.originalTitle && this.element.attr(\'title\', this.originalTitle));\n
\t},\n
\n
\tclose: function(event) {\n
\t\tvar self = this;\n
\t\t\n
\t\tif (false === self._trigger(\'beforeclose\', event)) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\t(self.overlay && self.overlay.destroy());\n
\t\tself.uiDialog.unbind(\'keypress.ui-dialog\');\n
\n
\t\t(self.options.hide\n
\t\t\t? self.uiDialog.hide(self.options.hide, function() {\n
\t\t\t\tself._trigger(\'close\', event);\n
\t\t\t})\n
\t\t\t: self.uiDialog.hide() && self._trigger(\'close\', event));\n
\n
\t\t$.ui.dialog.overlay.resize();\n
\n
\t\tself._isOpen = false;\n
\t\t\n
\t\t// adjust the maxZ to allow other modal dialogs to continue to work (see #4309)\n
\t\tif (self.options.modal) {\n
\t\t\tvar maxZ = 0;\n
\t\t\t$(\'.ui-dialog\').each(function() {\n
\t\t\t\tif (this != self.uiDialog[0]) {\n
\t\t\t\t\tmaxZ = Math.max(maxZ, $(this).css(\'z-index\'));\n
\t\t\t\t}\n
\t\t\t});\n
\t\t\t$.ui.dialog.maxZ = maxZ;\n
\t\t}\n
\t},\n
\n
\tisOpen: function() {\n
\t\treturn this._isOpen;\n
\t},\n
\n
\t// the force parameter allows us to move modal dialogs to their correct\n
\t// position on open\n
\tmoveToTop: function(force, event) {\n
\n
\t\tif ((this.options.modal && !force)\n
\t\t\t|| (!this.options.stack && !this.options.modal)) {\n
\t\t\treturn this._trigger(\'focus\', event);\n
\t\t}\n
\t\t\n
\t\tif (this.options.zIndex > $.ui.dialog.maxZ) {\n
\t\t\t$.ui.dialog.maxZ = this.options.zIndex;\n
\t\t}\n
\t\t(this.overlay && this.overlay.$el.css(\'z-index\', $.ui.dialog.overlay.maxZ = ++$.ui.dialog.maxZ));\n
\n
\t\t//Save and then restore scroll since Opera 9.5+ resets when parent z-Index is changed.\n
\t\t//  http://ui.jquery.com/bugs/ticket/3193\n
\t\tvar saveScroll = { scrollTop: this.element.attr(\'scrollTop\'), scrollLeft: this.element.attr(\'scrollLeft\') };\n
\t\tthis.uiDialog.css(\'z-index\', ++$.ui.dialog.maxZ);\n
\t\tthis.element.attr(saveScroll);\n
\t\tthis._trigger(\'focus\', event);\n
\t},\n
\n
\topen: function() {\n
\t\tif (this._isOpen) { return; }\n
\n
\t\tvar options = this.options,\n
\t\t\tuiDialog = this.uiDialog;\n
\n
\t\tthis.overlay = options.modal ? new $.ui.dialog.overlay(this) : null;\n
\t\t(uiDialog.next().length && uiDialog.appendTo(\'body\'));\n
\t\tthis._size();\n
\t\tthis._position(options.position);\n
\t\tuiDialog.show(options.show);\n
\t\tthis.moveToTop(true);\n
\n
\t\t// prevent tabbing out of modal dialogs\n
\t\t(options.modal && uiDialog.bind(\'keypress.ui-dialog\', function(event) {\n
\t\t\tif (event.keyCode != $.ui.keyCode.TAB) {\n
\t\t\t\treturn;\n
\t\t\t}\n
\n
\t\t\tvar tabbables = $(\':tabbable\', this),\n
\t\t\t\tfirst = tabbables.filter(\':first\')[0],\n
\t\t\t\tlast  = tabbables.filter(\':last\')[0];\n
\n
\t\t\tif (event.target == last && !event.shiftKey) {\n
\t\t\t\tsetTimeout(function() {\n
\t\t\t\t\tfirst.focus();\n
\t\t\t\t}, 1);\n
\t\t\t} else if (event.target == first && event.shiftKey) {\n
\t\t\t\tsetTimeout(function() {\n
\t\t\t\t\tlast.focus();\n
\t\t\t\t}, 1);\n
\t\t\t}\n
\t\t}));\n
\n
\t\t// set focus to the first tabbable element in the content area or the first button\n
\t\t// if there are no tabbable elements, set focus on the dialog itself\n
\t\t$([])\n
\t\t\t.add(uiDialog.find(\'.ui-dialog-content :tabbable:first\'))\n
\t\t\t.add(uiDialog.find(\'.ui-dialog-buttonpane :tabbable:first\'))\n
\t\t\t.add(uiDialog)\n
\t\t\t.filter(\':first\')\n
\t\t\t.focus();\n
\n
\t\tthis._trigger(\'open\');\n
\t\tthis._isOpen = true;\n
\t},\n
\n
\t_createButtons: function(buttons) {\n
\t\tvar self = this,\n
\t\t\thasButtons = false,\n
\t\t\tuiDialogButtonPane = $(\'<div></div>\')\n
\t\t\t\t.addClass(\n
\t\t\t\t\t\'ui-dialog-buttonpane \' +\n
\t\t\t\t\t\'ui-widget-content \' +\n
\t\t\t\t\t\'ui-helper-clearfix\'\n
\t\t\t\t);\n
\n
\t\t// if we already have a button pane, remove it\n
\t\tthis.uiDialog.find(\'.ui-dialog-buttonpane\').remove();\n
\n
\t\t(typeof buttons == \'object\' && buttons !== null &&\n
\t\t\t$.each(buttons, function() { return !(hasButtons = true); }));\n
\t\tif (hasButtons) {\n
\t\t\t$.each(buttons, function(name, fn) {\n
\t\t\t\t$(\'<button type="button"></button>\')\n
\t\t\t\t\t.addClass(\n
\t\t\t\t\t\t\'ui-state-default \' +\n
\t\t\t\t\t\t\'ui-corner-all\'\n
\t\t\t\t\t)\n
\t\t\t\t\t.text(name)\n
\t\t\t\t\t.click(function() { fn.apply(self.element[0], arguments); })\n
\t\t\t\t\t.hover(\n
\t\t\t\t\t\tfunction() {\n
\t\t\t\t\t\t\t$(this).addClass(\'ui-state-hover\');\n
\t\t\t\t\t\t},\n
\t\t\t\t\t\tfunction() {\n
\t\t\t\t\t\t\t$(this).removeClass(\'ui-state-hover\');\n
\t\t\t\t\t\t}\n
\t\t\t\t\t)\n
\t\t\t\t\t.focus(function() {\n
\t\t\t\t\t\t$(this).addClass(\'ui-state-focus\');\n
\t\t\t\t\t})\n
\t\t\t\t\t.blur(function() {\n
\t\t\t\t\t\t$(this).removeClass(\'ui-state-focus\');\n
\t\t\t\t\t})\n
\t\t\t\t\t.appendTo(uiDialogButtonPane);\n
\t\t\t});\n
\t\t\tuiDialogButtonPane.appendTo(this.uiDialog);\n
\t\t}\n
\t},\n
\n
\t_makeDraggable: function() {\n
\t\tvar self = this,\n
\t\t\toptions = this.options,\n
\t\t\theightBeforeDrag;\n
\n
\t\tthis.uiDialog.draggable({\n
\t\t\tcancel: \'.ui-dialog-content\',\n
\t\t\thandle: \'.ui-dialog-titlebar\',\n
\t\t\tcontainment: \'document\',\n
\t\t\tstart: function() {\n
\t\t\t\theightBeforeDrag = options.height;\n
\t\t\t\t$(this).height($(this).height()).addClass("ui-dialog-dragging");\n
\t\t\t\t(options.dragStart && options.dragStart.apply(self.element[0], arguments));\n
\t\t\t},\n
\t\t\tdrag: function() {\n
\t\t\t\t(options.drag && options.drag.apply(self.element[0], arguments));\n
\t\t\t},\n
\t\t\tstop: function() {\n
\t\t\t\t$(this).removeClass("ui-dialog-dragging").height(heightBeforeDrag);\n
\t\t\t\t(options.dragStop && options.dragStop.apply(self.element[0], arguments));\n
\t\t\t\t$.ui.dialog.overlay.resize();\n
\t\t\t}\n
\t\t});\n
\t},\n
\n
\t_makeResizable: function(handles) {\n
\t\thandles = (handles === undefined ? this.options.resizable : handles);\n
\t\tvar self = this,\n
\t\t\toptions = this.options,\n
\t\t\tresizeHandles = typeof handles == \'string\'\n
\t\t\t\t? handles\n
\t\t\t\t: \'n,e,s,w,se,sw,ne,nw\';\n
\n
\t\tthis.uiDialog.resizable({\n
\t\t\tcancel: \'.ui-dialog-content\',\n
\t\t\talsoResize: this.element,\n
\t\t\tmaxWidth: options.maxWidth,\n
\t\t\tmaxHeight: options.maxHeight,\n
\t\t\tminWidth: options.minWidth,\n
\t\t\tminHeight: options.minHeight,\n
\t\t\tstart: function() {\n
\t\t\t\t$(this).addClass("ui-dialog-resizing");\n
\t\t\t\t(options.resizeStart && options.resizeStart.apply(self.element[0], arguments));\n
\t\t\t},\n
\t\t\tresize: function() {\n
\t\t\t\t(options.resize && options.resize.apply(self.element[0], arguments));\n
\t\t\t},\n
\t\t\thandles: resizeHandles,\n
\t\t\tstop: function() {\n
\t\t\t\t$(this).removeClass("ui-dialog-resizing");\n
\t\t\t\toptions.height = $(this).height();\n
\t\t\t\toptions.width = $(this).width();\n
\t\t\t\t(options.resizeStop && options.resizeStop.apply(self.element[0], arguments));\n
\t\t\t\t$.ui.dialog.overlay.resize();\n
\t\t\t}\n
\t\t})\n
\t\t.find(\'.ui-resizable-se\').addClass(\'ui-icon ui-icon-grip-diagonal-se\');\n
\t},\n
\n
\t_position: function(pos) {\n
\t\tvar wnd = $(window), doc = $(document),\n
\t\t\tpTop = doc.scrollTop(), pLeft = doc.scrollLeft(),\n
\t\t\tminTop = pTop;\n
\n
\t\tif ($.inArray(pos, [\'center\',\'top\',\'right\',\'bottom\',\'left\']) >= 0) {\n
\t\t\tpos = [\n
\t\t\t\tpos == \'right\' || pos == \'left\' ? pos : \'center\',\n
\t\t\t\tpos == \'top\' || pos == \'bottom\' ? pos : \'middle\'\n
\t\t\t];\n
\t\t}\n
\t\tif (pos.constructor != Array) {\n
\t\t\tpos = [\'center\', \'middle\'];\n
\t\t}\n
\t\tif (pos[0].constructor == Number) {\n
\t\t\tpLeft += pos[0];\n
\t\t} else {\n
\t\t\tswitch (pos[0]) {\n
\t\t\t\tcase \'left\':\n
\t\t\t\t\tpLeft += 0;\n
\t\t\t\t\tbreak;\n
\t\t\t\tcase \'right\':\n
\t\t\t\t\tpLeft += wnd.width() - this.uiDialog.outerWidth();\n
\t\t\t\t\tbreak;\n
\t\t\t\tdefault:\n
\t\t\t\tcase \'center\':\n
\t\t\t\t\tpLeft += (wnd.width() - this.uiDialog.outerWidth()) / 2;\n
\t\t\t}\n
\t\t}\n
\t\tif (pos[1].constructor == Number) {\n
\t\t\tpTop += pos[1];\n
\t\t} else {\n
\t\t\tswitch (pos[1]) {\n
\t\t\t\tcase \'top\':\n
\t\t\t\t\tpTop += 0;\n
\t\t\t\t\tbreak;\n
\t\t\t\tcase \'bottom\':\n
\t\t\t\t\tpTop += wnd.height() - this.uiDialog.outerHeight();\n
\t\t\t\t\tbreak;\n
\t\t\t\tdefault:\n
\t\t\t\tcase \'middle\':\n
\t\t\t\t\tpTop += (wnd.height() - this.uiDialog.outerHeight()) / 2;\n
\t\t\t}\n
\t\t}\n
\n
\t\t// prevent the dialog from being too high (make sure the titlebar\n
\t\t// is accessible)\n
\t\tpTop = Math.max(pTop, minTop);\n
\t\tthis.uiDialog.css({top: pTop, left: pLeft});\n
\t},\n
\n
\t_setData: function(key, value){\n
\t\t(setDataSwitch[key] && this.uiDialog.data(setDataSwitch[key], value));\n
\t\tswitch (key) {\n
\t\t\tcase "buttons":\n
\t\t\t\tthis._createButtons(value);\n
\t\t\t\tbreak;\n
\t\t\tcase "closeText":\n
\t\t\t\tthis.uiDialogTitlebarCloseText.text(value);\n
\t\t\t\tbreak;\n
\t\t\tcase "dialogClass":\n
\t\t\t\tthis.uiDialog\n
\t\t\t\t\t.removeClass(this.options.dialogClass)\n
\t\t\t\t\t.addClass(uiDialogClasses + value);\n
\t\t\t\tbreak;\n
\t\t\tcase "draggable":\n
\t\t\t\t(value\n
\t\t\t\t\t? this._makeDraggable()\n
\t\t\t\t\t: this.uiDialog.draggable(\'destroy\'));\n
\t\t\t\tbreak;\n
\t\t\tcase "height":\n
\t\t\t\tthis.uiDialog.height(value);\n
\t\t\t\tbreak;\n
\t\t\tcase "position":\n
\t\t\t\tthis._position(value);\n
\t\t\t\tbreak;\n
\t\t\tcase "resizable":\n
\t\t\t\tvar uiDialog = this.uiDialog,\n
\t\t\t\t\tisResizable = this.uiDialog.is(\':data(resizable)\');\n
\n
\t\t\t\t// currently resizable, becoming non-resizable\n
\t\t\t\t(isResizable && !value && uiDialog.resizable(\'destroy\'));\n
\n
\t\t\t\t// currently resizable, changing handles\n
\t\t\t\t(isResizable && typeof value == \'string\' &&\n
\t\t\t\t\tuiDialog.resizable(\'option\', \'handles\', value));\n
\n
\t\t\t\t// currently non-resizable, becoming resizable\n
\t\t\t\t(isResizable || this._makeResizable(value));\n
\t\t\t\tbreak;\n
\t\t\tcase "title":\n
\t\t\t\t$(".ui-dialog-title", this.uiDialogTitlebar).html(value || \'&nbsp;\');\n
\t\t\t\tbreak;\n
\t\t\tcase "width":\n
\t\t\t\tthis.uiDialog.width(value);\n
\t\t\t\tbreak;\n
\t\t}\n
\n
\t\t$.widget.prototype._setData.apply(this, arguments);\n
\t},\n
\n
\t_size: function() {\n
\t\t/* If the user has resized the dialog, the .ui-dialog and .ui-dialog-content\n
\t\t * divs will both have width and height set, so we need to reset them\n
\t\t */\n
\t\tvar options = this.options;\n
\n
\t\t// reset content sizing\n
\t\tthis.element.css({\n
\t\t\theight: 0,\n
\t\t\tminHeight: 0,\n
\t\t\twidth: \'auto\'\n
\t\t});\n
\n
\t\t// reset wrapper sizing\n
\t\t// determine the height of all the non-content elements\n
\t\tvar nonContentHeight = this.uiDialog.css({\n
\t\t\t\theight: \'auto\',\n
\t\t\t\twidth: options.width\n
\t\t\t})\n
\t\t\t.height();\n
\n
\t\tthis.element\n
\t\t\t.css({\n
\t\t\t\tminHeight: Math.max(options.minHeight - nonContentHeight, 0),\n
\t\t\t\theight: options.height == \'auto\'\n
\t\t\t\t\t? \'auto\'\n
\t\t\t\t\t: Math.max(options.height - nonContentHeight, 0)\n
\t\t\t});\n
\t}\n
});\n
\n
$.extend($.ui.dialog, {\n
\tversion: "1.7.2",\n
\tdefaults: {\n
\t\tautoOpen: true,\n
\t\tbgiframe: false,\n
\t\tbuttons: {},\n
\t\tcloseOnEscape: true,\n
\t\tcloseText: \'close\',\n
\t\tdialogClass: \'\',\n
\t\tdraggable: true,\n
\t\thide: null,\n
\t\theight: \'auto\',\n
\t\tmaxHeight: false,\n
\t\tmaxWidth: false,\n
\t\tminHeight: 150,\n
\t\tminWidth: 150,\n
\t\tmodal: false,\n
\t\tposition: \'center\',\n
\t\tresizable: true,\n
\t\tshow: null,\n
\t\tstack: true,\n
\t\ttitle: \'\',\n
\t\twidth: 300,\n
\t\tzIndex: 1000\n
\t},\n
\n
\tgetter: \'isOpen\',\n
\n
\tuuid: 0,\n
\tmaxZ: 0,\n
\n
\tgetTitleId: function($el) {\n
\t\treturn \'ui-dialog-title-\' + ($el.attr(\'id\') || ++this.uuid);\n
\t},\n
\n
\toverlay: function(dialog) {\n
\t\tthis.$el = $.ui.dialog.overlay.create(dialog);\n
\t}\n
});\n
\n
$.extend($.ui.dialog.overlay, {\n
\tinstances: [],\n
\tmaxZ: 0,\n
\tevents: $.map(\'focus,mousedown,mouseup,keydown,keypress,click\'.split(\',\'),\n
\t\tfunction(event) { return event + \'.dialog-overlay\'; }).join(\' \'),\n
\tcreate: function(dialog) {\n
\t\tif (this.instances.length === 0) {\n
\t\t\t// prevent use of anchors and inputs\n
\t\t\t// we use a setTimeout in case the overlay is created from an\n
\t\t\t// event that we\'re going to be cancelling (see #2804)\n
\t\t\tsetTimeout(function() {\n
\t\t\t\t// handle $(el).dialog().dialog(\'close\') (see #4065)\n
\t\t\t\tif ($.ui.dialog.overlay.instances.length) {\n
\t\t\t\t\t$(document).bind($.ui.dialog.overlay.events, function(event) {\n
\t\t\t\t\t\tvar dialogZ = $(event.target).parents(\'.ui-dialog\').css(\'zIndex\') || 0;\n
\t\t\t\t\t\treturn (dialogZ > $.ui.dialog.overlay.maxZ);\n
\t\t\t\t\t});\n
\t\t\t\t}\n
\t\t\t}, 1);\n
\n
\t\t\t// allow closing by pressing the escape key\n
\t\t\t$(document).bind(\'keydown.dialog-overlay\', function(event) {\n
\t\t\t\t(dialog.options.closeOnEscape && event.keyCode\n
\t\t\t\t\t\t&& event.keyCode == $.ui.keyCode.ESCAPE && dialog.close(event));\n
\t\t\t});\n
\n
\t\t\t// handle window resize\n
\t\t\t$(window).bind(\'resize.dialog-overlay\', $.ui.dialog.overlay.resize);\n
\t\t}\n
\n
\t\tvar $el = $(\'<div></div>\').appendTo(document.body)\n
\t\t\t.addClass(\'ui-widget-overlay\').css({\n
\t\t\t\twidth: this.width(),\n
\t\t\t\theight: this.height()\n
\t\t\t});\n
\n
\t\t(dialog.options.bgiframe && $.fn.bgiframe && $el.bgiframe());\n
\n
\t\tthis.instances.push($el);\n
\t\treturn $el;\n
\t},\n
\n
\tdestroy: function($el) {\n
\t\tthis.instances.splice($.inArray(this.instances, $el), 1);\n
\n
\t\tif (this.instances.length === 0) {\n
\t\t\t$([document, window]).unbind(\'.dialog-overlay\');\n
\t\t}\n
\n
\t\t$el.remove();\n
\t\t\n
\t\t// adjust the maxZ to allow other modal dialogs to continue to work (see #4309)\n
\t\tvar maxZ = 0;\n
\t\t$.each(this.instances, function() {\n
\t\t\tmaxZ = Math.max(maxZ, this.css(\'z-index\'));\n
\t\t});\n
\t\tthis.maxZ = maxZ;\n
\t},\n
\n
\theight: function() {\n
\t\t// handle IE 6\n
\t\tif ($.browser.msie && $.browser.version < 7) {\n
\t\t\tvar scrollHeight = Math.max(\n
\t\t\t\tdocument.documentElement.scrollHeight,\n
\t\t\t\tdocument.body.scrollHeight\n
\t\t\t);\n
\t\t\tvar offsetHeight = Math.max(\n
\t\t\t\tdocument.documentElement.offsetHeight,\n
\t\t\t\tdocument.body.offsetHeight\n
\t\t\t);\n
\n
\t\t\tif (scrollHeight < offsetHeight) {\n
\t\t\t\treturn $(window).height() + \'px\';\n
\t\t\t} else {\n
\t\t\t\treturn scrollHeight + \'px\';\n
\t\t\t}\n
\t\t// handle "good" browsers\n
\t\t} else {\n
\t\t\treturn $(document).height() + \'px\';\n
\t\t}\n
\t},\n
\n
\twidth: function() {\n
\t\t// handle IE 6\n
\t\tif ($.browser.msie && $.browser.version < 7) {\n
\t\t\tvar scrollWidth = Math.max(\n
\t\t\t\tdocument.documentElement.scrollWidth,\n
\t\t\t\tdocument.body.scrollWidth\n
\t\t\t);\n
\t\t\tvar offsetWidth = Math.max(\n
\t\t\t\tdocument.documentElement.offsetWidth,\n
\t\t\t\tdocument.body.offsetWidth\n
\t\t\t);\n
\n
\t\t\tif (scrollWidth < offsetWidth) {\n
\t\t\t\treturn $(window).width() + \'px\';\n
\t\t\t} else {\n
\t\t\t\treturn scrollWidth + \'px\';\n
\t\t\t}\n
\t\t// handle "good" browsers\n
\t\t} else {\n
\t\t\treturn $(document).width() + \'px\';\n
\t\t}\n
\t},\n
\n
\tresize: function() {\n
\t\t/* If the dialog is draggable and the user drags it past the\n
\t\t * right edge of the window, the document becomes wider so we\n
\t\t * need to stretch the overlay. If the user then drags the\n
\t\t * dialog back to the left, the document will become narrower,\n
\t\t * so we need to shrink the overlay to the appropriate size.\n
\t\t * This is handled by shrinking the overlay before setting it\n
\t\t * to the full document size.\n
\t\t */\n
\t\tvar $overlays = $([]);\n
\t\t$.each($.ui.dialog.overlay.instances, function() {\n
\t\t\t$overlays = $overlays.add(this);\n
\t\t});\n
\n
\t\t$overlays.css({\n
\t\t\twidth: 0,\n
\t\t\theight: 0\n
\t\t}).css({\n
\t\t\twidth: $.ui.dialog.overlay.width(),\n
\t\t\theight: $.ui.dialog.overlay.height()\n
\t\t});\n
\t}\n
});\n
\n
$.extend($.ui.dialog.overlay.prototype, {\n
\tdestroy: function() {\n
\t\t$.ui.dialog.overlay.destroy(this.$el);\n
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
            <value> <long>17390</long> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
