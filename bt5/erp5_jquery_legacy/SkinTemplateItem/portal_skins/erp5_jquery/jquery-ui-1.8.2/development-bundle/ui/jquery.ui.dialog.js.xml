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
            <value> <string>ts77895655.88</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.ui.dialog.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Dialog 1.8.2\n
 *\n
 * Copyright (c) 2010 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Dialog\n
 *\n
 * Depends:\n
 *\tjquery.ui.core.js\n
 *\tjquery.ui.widget.js\n
 *  jquery.ui.button.js\n
 *\tjquery.ui.draggable.js\n
 *\tjquery.ui.mouse.js\n
 *\tjquery.ui.position.js\n
 *\tjquery.ui.resizable.js\n
 */\n
(function($) {\n
\n
var uiDialogClasses =\n
\t\'ui-dialog \' +\n
\t\'ui-widget \' +\n
\t\'ui-widget-content \' +\n
\t\'ui-corner-all \';\n
\n
$.widget("ui.dialog", {\n
\toptions: {\n
\t\tautoOpen: true,\n
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
\t_create: function() {\n
\t\tthis.originalTitle = this.element.attr(\'title\');\n
\n
\t\tvar self = this,\n
\t\t\toptions = self.options,\n
\n
\t\t\ttitle = options.title || self.originalTitle || \'&#160;\',\n
\t\t\ttitleId = $.ui.dialog.getTitleId(self.element),\n
\n
\t\t\tuiDialog = (self.uiDialog = $(\'<div></div>\'))\n
\t\t\t\t.appendTo(document.body)\n
\t\t\t\t.hide()\n
\t\t\t\t.addClass(uiDialogClasses + options.dialogClass)\n
\t\t\t\t.css({\n
\t\t\t\t\tzIndex: options.zIndex\n
\t\t\t\t})\n
\t\t\t\t// setting tabIndex makes the div focusable\n
\t\t\t\t// setting outline to 0 prevents a border on focus in Mozilla\n
\t\t\t\t.attr(\'tabIndex\', -1).css(\'outline\', 0).keydown(function(event) {\n
\t\t\t\t\tif (options.closeOnEscape && event.keyCode &&\n
\t\t\t\t\t\tevent.keyCode === $.ui.keyCode.ESCAPE) {\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tself.close(event);\n
\t\t\t\t\t\tevent.preventDefault();\n
\t\t\t\t\t}\n
\t\t\t\t})\n
\t\t\t\t.attr({\n
\t\t\t\t\trole: \'dialog\',\n
\t\t\t\t\t\'aria-labelledby\': titleId\n
\t\t\t\t})\n
\t\t\t\t.mousedown(function(event) {\n
\t\t\t\t\tself.moveToTop(false, event);\n
\t\t\t\t}),\n
\n
\t\t\tuiDialogContent = self.element\n
\t\t\t\t.show()\n
\t\t\t\t.removeAttr(\'title\')\n
\t\t\t\t.addClass(\n
\t\t\t\t\t\'ui-dialog-content \' +\n
\t\t\t\t\t\'ui-widget-content\')\n
\t\t\t\t.appendTo(uiDialog),\n
\n
\t\t\tuiDialogTitlebar = (self.uiDialogTitlebar = $(\'<div></div>\'))\n
\t\t\t\t.addClass(\n
\t\t\t\t\t\'ui-dialog-titlebar \' +\n
\t\t\t\t\t\'ui-widget-header \' +\n
\t\t\t\t\t\'ui-corner-all \' +\n
\t\t\t\t\t\'ui-helper-clearfix\'\n
\t\t\t\t)\n
\t\t\t\t.prependTo(uiDialog),\n
\n
\t\t\tuiDialogTitlebarClose = $(\'<a href="#"></a>\')\n
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
\t\t\t\t.click(function(event) {\n
\t\t\t\t\tself.close(event);\n
\t\t\t\t\treturn false;\n
\t\t\t\t})\n
\t\t\t\t.appendTo(uiDialogTitlebar),\n
\n
\t\t\tuiDialogTitlebarCloseText = (self.uiDialogTitlebarCloseText = $(\'<span></span>\'))\n
\t\t\t\t.addClass(\n
\t\t\t\t\t\'ui-icon \' +\n
\t\t\t\t\t\'ui-icon-closethick\'\n
\t\t\t\t)\n
\t\t\t\t.text(options.closeText)\n
\t\t\t\t.appendTo(uiDialogTitlebarClose),\n
\n
\t\t\tuiDialogTitle = $(\'<span></span>\')\n
\t\t\t\t.addClass(\'ui-dialog-title\')\n
\t\t\t\t.attr(\'id\', titleId)\n
\t\t\t\t.html(title)\n
\t\t\t\t.prependTo(uiDialogTitlebar);\n
\n
\t\t//handling of deprecated beforeclose (vs beforeClose) option\n
\t\t//Ticket #4669 http://dev.jqueryui.com/ticket/4669\n
\t\t//TODO: remove in 1.9pre\n
\t\tif ($.isFunction(options.beforeclose) && !$.isFunction(options.beforeClose)) {\n
\t\t\toptions.beforeClose = options.beforeclose;\n
\t\t}\n
\n
\t\tuiDialogTitlebar.find("*").add(uiDialogTitlebar).disableSelection();\n
\n
\t\tif (options.draggable && $.fn.draggable) {\n
\t\t\tself._makeDraggable();\n
\t\t}\n
\t\tif (options.resizable && $.fn.resizable) {\n
\t\t\tself._makeResizable();\n
\t\t}\n
\n
\t\tself._createButtons(options.buttons);\n
\t\tself._isOpen = false;\n
\n
\t\tif ($.fn.bgiframe) {\n
\t\t\tuiDialog.bgiframe();\n
\t\t}\n
\t},\n
\t_init: function() {\n
\t\tif ( this.options.autoOpen ) {\n
\t\t\tthis.open();\n
\t\t}\n
\t},\n
\n
\tdestroy: function() {\n
\t\tvar self = this;\n
\t\t\n
\t\tif (self.overlay) {\n
\t\t\tself.overlay.destroy();\n
\t\t}\n
\t\tself.uiDialog.hide();\n
\t\tself.element\n
\t\t\t.unbind(\'.dialog\')\n
\t\t\t.removeData(\'dialog\')\n
\t\t\t.removeClass(\'ui-dialog-content ui-widget-content\')\n
\t\t\t.hide().appendTo(\'body\');\n
\t\tself.uiDialog.remove();\n
\n
\t\tif (self.originalTitle) {\n
\t\t\tself.element.attr(\'title\', self.originalTitle);\n
\t\t}\n
\n
\t\treturn self;\n
\t},\n
\t\n
\twidget: function() {\n
\t\treturn this.uiDialog;\n
\t},\n
\n
\tclose: function(event) {\n
\t\tvar self = this,\n
\t\t\tmaxZ;\n
\t\t\n
\t\tif (false === self._trigger(\'beforeClose\', event)) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\tif (self.overlay) {\n
\t\t\tself.overlay.destroy();\n
\t\t}\n
\t\tself.uiDialog.unbind(\'keypress.ui-dialog\');\n
\n
\t\tself._isOpen = false;\n
\n
\t\tif (self.options.hide) {\n
\t\t\tself.uiDialog.hide(self.options.hide, function() {\n
\t\t\t\tself._trigger(\'close\', event);\n
\t\t\t});\n
\t\t} else {\n
\t\t\tself.uiDialog.hide();\n
\t\t\tself._trigger(\'close\', event);\n
\t\t}\n
\n
\t\t$.ui.dialog.overlay.resize();\n
\n
\t\t// adjust the maxZ to allow other modal dialogs to continue to work (see #4309)\n
\t\tif (self.options.modal) {\n
\t\t\tmaxZ = 0;\n
\t\t\t$(\'.ui-dialog\').each(function() {\n
\t\t\t\tif (this !== self.uiDialog[0]) {\n
\t\t\t\t\tmaxZ = Math.max(maxZ, $(this).css(\'z-index\'));\n
\t\t\t\t}\n
\t\t\t});\n
\t\t\t$.ui.dialog.maxZ = maxZ;\n
\t\t}\n
\n
\t\treturn self;\n
\t},\n
\n
\tisOpen: function() {\n
\t\treturn this._isOpen;\n
\t},\n
\n
\t// the force parameter allows us to move modal dialogs to their correct\n
\t// position on open\n
\tmoveToTop: function(force, event) {\n
\t\tvar self = this,\n
\t\t\toptions = self.options,\n
\t\t\tsaveScroll;\n
\t\t\n
\t\tif ((options.modal && !force) ||\n
\t\t\t(!options.stack && !options.modal)) {\n
\t\t\treturn self._trigger(\'focus\', event);\n
\t\t}\n
\t\t\n
\t\tif (options.zIndex > $.ui.dialog.maxZ) {\n
\t\t\t$.ui.dialog.maxZ = options.zIndex;\n
\t\t}\n
\t\tif (self.overlay) {\n
\t\t\t$.ui.dialog.maxZ += 1;\n
\t\t\tself.overlay.$el.css(\'z-index\', $.ui.dialog.overlay.maxZ = $.ui.dialog.maxZ);\n
\t\t}\n
\n
\t\t//Save and then restore scroll since Opera 9.5+ resets when parent z-Index is changed.\n
\t\t//  http://ui.jquery.com/bugs/ticket/3193\n
\t\tsaveScroll = { scrollTop: self.element.attr(\'scrollTop\'), scrollLeft: self.element.attr(\'scrollLeft\') };\n
\t\t$.ui.dialog.maxZ += 1;\n
\t\tself.uiDialog.css(\'z-index\', $.ui.dialog.maxZ);\n
\t\tself.element.attr(saveScroll);\n
\t\tself._trigger(\'focus\', event);\n
\n
\t\treturn self;\n
\t},\n
\n
\topen: function() {\n
\t\tif (this._isOpen) { return; }\n
\n
\t\tvar self = this,\n
\t\t\toptions = self.options,\n
\t\t\tuiDialog = self.uiDialog;\n
\n
\t\tself.overlay = options.modal ? new $.ui.dialog.overlay(self) : null;\n
\t\tif (uiDialog.next().length) {\n
\t\t\tuiDialog.appendTo(\'body\');\n
\t\t}\n
\t\tself._size();\n
\t\tself._position(options.position);\n
\t\tuiDialog.show(options.show);\n
\t\tself.moveToTop(true);\n
\n
\t\t// prevent tabbing out of modal dialogs\n
\t\tif (options.modal) {\n
\t\t\tuiDialog.bind(\'keypress.ui-dialog\', function(event) {\n
\t\t\t\tif (event.keyCode !== $.ui.keyCode.TAB) {\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\t\n
\t\t\t\tvar tabbables = $(\':tabbable\', this),\n
\t\t\t\t\tfirst = tabbables.filter(\':first\'),\n
\t\t\t\t\tlast  = tabbables.filter(\':last\');\n
\t\n
\t\t\t\tif (event.target === last[0] && !event.shiftKey) {\n
\t\t\t\t\tfirst.focus(1);\n
\t\t\t\t\treturn false;\n
\t\t\t\t} else if (event.target === first[0] && event.shiftKey) {\n
\t\t\t\t\tlast.focus(1);\n
\t\t\t\t\treturn false;\n
\t\t\t\t}\n
\t\t\t});\n
\t\t}\n
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
\t\tself._trigger(\'open\');\n
\t\tself._isOpen = true;\n
\n
\t\treturn self;\n
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
\t\tself.uiDialog.find(\'.ui-dialog-buttonpane\').remove();\n
\n
\t\tif (typeof buttons === \'object\' && buttons !== null) {\n
\t\t\t$.each(buttons, function() {\n
\t\t\t\treturn !(hasButtons = true);\n
\t\t\t});\n
\t\t}\n
\t\tif (hasButtons) {\n
\t\t\t$.each(buttons, function(name, fn) {\n
\t\t\t\tvar button = $(\'<button type="button"></button>\')\n
\t\t\t\t\t.text(name)\n
\t\t\t\t\t.click(function() { fn.apply(self.element[0], arguments); })\n
\t\t\t\t\t.appendTo(uiDialogButtonPane);\n
\t\t\t\tif ($.fn.button) {\n
\t\t\t\t\tbutton.button();\n
\t\t\t\t}\n
\t\t\t});\n
\t\t\tuiDialogButtonPane.appendTo(self.uiDialog);\n
\t\t}\n
\t},\n
\n
\t_makeDraggable: function() {\n
\t\tvar self = this,\n
\t\t\toptions = self.options,\n
\t\t\tdoc = $(document),\n
\t\t\theightBeforeDrag;\n
\n
\t\tfunction filteredUi(ui) {\n
\t\t\treturn {\n
\t\t\t\tposition: ui.position,\n
\t\t\t\toffset: ui.offset\n
\t\t\t};\n
\t\t}\n
\n
\t\tself.uiDialog.draggable({\n
\t\t\tcancel: \'.ui-dialog-content, .ui-dialog-titlebar-close\',\n
\t\t\thandle: \'.ui-dialog-titlebar\',\n
\t\t\tcontainment: \'document\',\n
\t\t\tstart: function(event, ui) {\n
\t\t\t\theightBeforeDrag = options.height === "auto" ? "auto" : $(this).height();\n
\t\t\t\t$(this).height($(this).height()).addClass("ui-dialog-dragging");\n
\t\t\t\tself._trigger(\'dragStart\', event, filteredUi(ui));\n
\t\t\t},\n
\t\t\tdrag: function(event, ui) {\n
\t\t\t\tself._trigger(\'drag\', event, filteredUi(ui));\n
\t\t\t},\n
\t\t\tstop: function(event, ui) {\n
\t\t\t\toptions.position = [ui.position.left - doc.scrollLeft(),\n
\t\t\t\t\tui.position.top - doc.scrollTop()];\n
\t\t\t\t$(this).removeClass("ui-dialog-dragging").height(heightBeforeDrag);\n
\t\t\t\tself._trigger(\'dragStop\', event, filteredUi(ui));\n
\t\t\t\t$.ui.dialog.overlay.resize();\n
\t\t\t}\n
\t\t});\n
\t},\n
\n
\t_makeResizable: function(handles) {\n
\t\thandles = (handles === undefined ? this.options.resizable : handles);\n
\t\tvar self = this,\n
\t\t\toptions = self.options,\n
\t\t\t// .ui-resizable has position: relative defined in the stylesheet\n
\t\t\t// but dialogs have to use absolute or fixed positioning\n
\t\t\tposition = self.uiDialog.css(\'position\'),\n
\t\t\tresizeHandles = (typeof handles === \'string\' ?\n
\t\t\t\thandles\t:\n
\t\t\t\t\'n,e,s,w,se,sw,ne,nw\'\n
\t\t\t);\n
\n
\t\tfunction filteredUi(ui) {\n
\t\t\treturn {\n
\t\t\t\toriginalPosition: ui.originalPosition,\n
\t\t\t\toriginalSize: ui.originalSize,\n
\t\t\t\tposition: ui.position,\n
\t\t\t\tsize: ui.size\n
\t\t\t};\n
\t\t}\n
\n
\t\tself.uiDialog.resizable({\n
\t\t\tcancel: \'.ui-dialog-content\',\n
\t\t\tcontainment: \'document\',\n
\t\t\talsoResize: self.element,\n
\t\t\tmaxWidth: options.maxWidth,\n
\t\t\tmaxHeight: options.maxHeight,\n
\t\t\tminWidth: options.minWidth,\n
\t\t\tminHeight: self._minHeight(),\n
\t\t\thandles: resizeHandles,\n
\t\t\tstart: function(event, ui) {\n
\t\t\t\t$(this).addClass("ui-dialog-resizing");\n
\t\t\t\tself._trigger(\'resizeStart\', event, filteredUi(ui));\n
\t\t\t},\n
\t\t\tresize: function(event, ui) {\n
\t\t\t\tself._trigger(\'resize\', event, filteredUi(ui));\n
\t\t\t},\n
\t\t\tstop: function(event, ui) {\n
\t\t\t\t$(this).removeClass("ui-dialog-resizing");\n
\t\t\t\toptions.height = $(this).height();\n
\t\t\t\toptions.width = $(this).width();\n
\t\t\t\tself._trigger(\'resizeStop\', event, filteredUi(ui));\n
\t\t\t\t$.ui.dialog.overlay.resize();\n
\t\t\t}\n
\t\t})\n
\t\t.css(\'position\', position)\n
\t\t.find(\'.ui-resizable-se\').addClass(\'ui-icon ui-icon-grip-diagonal-se\');\n
\t},\n
\n
\t_minHeight: function() {\n
\t\tvar options = this.options;\n
\n
\t\tif (options.height === \'auto\') {\n
\t\t\treturn options.minHeight;\n
\t\t} else {\n
\t\t\treturn Math.min(options.minHeight, options.height);\n
\t\t}\n
\t},\n
\n
\t_position: function(position) {\n
\t\tvar myAt = [],\n
\t\t\toffset = [0, 0],\n
\t\t\tisVisible;\n
\n
\t\tposition = position || $.ui.dialog.prototype.options.position;\n
\n
\t\t// deep extending converts arrays to objects in jQuery <= 1.3.2 :-(\n
//\t\tif (typeof position == \'string\' || $.isArray(position)) {\n
//\t\t\tmyAt = $.isArray(position) ? position : position.split(\' \');\n
\n
\t\tif (typeof position === \'string\' || (typeof position === \'object\' && \'0\' in position)) {\n
\t\t\tmyAt = position.split ? position.split(\' \') : [position[0], position[1]];\n
\t\t\tif (myAt.length === 1) {\n
\t\t\t\tmyAt[1] = myAt[0];\n
\t\t\t}\n
\n
\t\t\t$.each([\'left\', \'top\'], function(i, offsetPosition) {\n
\t\t\t\tif (+myAt[i] === myAt[i]) {\n
\t\t\t\t\toffset[i] = myAt[i];\n
\t\t\t\t\tmyAt[i] = offsetPosition;\n
\t\t\t\t}\n
\t\t\t});\n
\t\t} else if (typeof position === \'object\') {\n
\t\t\tif (\'left\' in position) {\n
\t\t\t\tmyAt[0] = \'left\';\n
\t\t\t\toffset[0] = position.left;\n
\t\t\t} else if (\'right\' in position) {\n
\t\t\t\tmyAt[0] = \'right\';\n
\t\t\t\toffset[0] = -position.right;\n
\t\t\t}\n
\n
\t\t\tif (\'top\' in position) {\n
\t\t\t\tmyAt[1] = \'top\';\n
\t\t\t\toffset[1] = position.top;\n
\t\t\t} else if (\'bottom\' in position) {\n
\t\t\t\tmyAt[1] = \'bottom\';\n
\t\t\t\toffset[1] = -position.bottom;\n
\t\t\t}\n
\t\t}\n
\n
\t\t// need to show the dialog to get the actual offset in the position plugin\n
\t\tisVisible = this.uiDialog.is(\':visible\');\n
\t\tif (!isVisible) {\n
\t\t\tthis.uiDialog.show();\n
\t\t}\n
\t\tthis.uiDialog\n
\t\t\t// workaround for jQuery bug #5781 http://dev.jquery.com/ticket/5781\n
\t\t\t.css({ top: 0, left: 0 })\n
\t\t\t.position({\n
\t\t\t\tmy: myAt.join(\' \'),\n
\t\t\t\tat: myAt.join(\' \'),\n
\t\t\t\toffset: offset.join(\' \'),\n
\t\t\t\tof: window,\n
\t\t\t\tcollision: \'fit\',\n
\t\t\t\t// ensure that the titlebar is never outside the document\n
\t\t\t\tusing: function(pos) {\n
\t\t\t\t\tvar topOffset = $(this).css(pos).offset().top;\n
\t\t\t\t\tif (topOffset < 0) {\n
\t\t\t\t\t\t$(this).css(\'top\', pos.top - topOffset);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t});\n
\t\tif (!isVisible) {\n
\t\t\tthis.uiDialog.hide();\n
\t\t}\n
\t},\n
\n
\t_setOption: function(key, value){\n
\t\tvar self = this,\n
\t\t\tuiDialog = self.uiDialog,\n
\t\t\tisResizable = uiDialog.is(\':data(resizable)\'),\n
\t\t\tresize = false;\n
\t\t\n
\t\tswitch (key) {\n
\t\t\t//handling of deprecated beforeclose (vs beforeClose) option\n
\t\t\t//Ticket #4669 http://dev.jqueryui.com/ticket/4669\n
\t\t\t//TODO: remove in 1.9pre\n
\t\t\tcase "beforeclose":\n
\t\t\t\tkey = "beforeClose";\n
\t\t\t\tbreak;\n
\t\t\tcase "buttons":\n
\t\t\t\tself._createButtons(value);\n
\t\t\t\tbreak;\n
\t\t\tcase "closeText":\n
\t\t\t\t// convert whatever was passed in to a string, for text() to not throw up\n
\t\t\t\tself.uiDialogTitlebarCloseText.text("" + value);\n
\t\t\t\tbreak;\n
\t\t\tcase "dialogClass":\n
\t\t\t\tuiDialog\n
\t\t\t\t\t.removeClass(self.options.dialogClass)\n
\t\t\t\t\t.addClass(uiDialogClasses + value);\n
\t\t\t\tbreak;\n
\t\t\tcase "disabled":\n
\t\t\t\tif (value) {\n
\t\t\t\t\tuiDialog.addClass(\'ui-dialog-disabled\');\n
\t\t\t\t} else {\n
\t\t\t\t\tuiDialog.removeClass(\'ui-dialog-disabled\');\n
\t\t\t\t}\n
\t\t\t\tbreak;\n
\t\t\tcase "draggable":\n
\t\t\t\tif (value) {\n
\t\t\t\t\tself._makeDraggable();\n
\t\t\t\t} else {\n
\t\t\t\t\tuiDialog.draggable(\'destroy\');\n
\t\t\t\t}\n
\t\t\t\tbreak;\n
\t\t\tcase "height":\n
\t\t\t\tresize = true;\n
\t\t\t\tbreak;\n
\t\t\tcase "maxHeight":\n
\t\t\t\tif (isResizable) {\n
\t\t\t\t\tuiDialog.resizable(\'option\', \'maxHeight\', value);\n
\t\t\t\t}\n
\t\t\t\tresize = true;\n
\t\t\t\tbreak;\n
\t\t\tcase "maxWidth":\n
\t\t\t\tif (isResizable) {\n
\t\t\t\t\tuiDialog.resizable(\'option\', \'maxWidth\', value);\n
\t\t\t\t}\n
\t\t\t\tresize = true;\n
\t\t\t\tbreak;\n
\t\t\tcase "minHeight":\n
\t\t\t\tif (isResizable) {\n
\t\t\t\t\tuiDialog.resizable(\'option\', \'minHeight\', value);\n
\t\t\t\t}\n
\t\t\t\tresize = true;\n
\t\t\t\tbreak;\n
\t\t\tcase "minWidth":\n
\t\t\t\tif (isResizable) {\n
\t\t\t\t\tuiDialog.resizable(\'option\', \'minWidth\', value);\n
\t\t\t\t}\n
\t\t\t\tresize = true;\n
\t\t\t\tbreak;\n
\t\t\tcase "position":\n
\t\t\t\tself._position(value);\n
\t\t\t\tbreak;\n
\t\t\tcase "resizable":\n
\t\t\t\t// currently resizable, becoming non-resizable\n
\t\t\t\tif (isResizable && !value) {\n
\t\t\t\t\tuiDialog.resizable(\'destroy\');\n
\t\t\t\t}\n
\n
\t\t\t\t// currently resizable, changing handles\n
\t\t\t\tif (isResizable && typeof value === \'string\') {\n
\t\t\t\t\tuiDialog.resizable(\'option\', \'handles\', value);\n
\t\t\t\t}\n
\n
\t\t\t\t// currently non-resizable, becoming resizable\n
\t\t\t\tif (!isResizable && value !== false) {\n
\t\t\t\t\tself._makeResizable(value);\n
\t\t\t\t}\n
\t\t\t\tbreak;\n
\t\t\tcase "title":\n
\t\t\t\t// convert whatever was passed in o a string, for html() to not throw up\n
\t\t\t\t$(".ui-dialog-title", self.uiDialogTitlebar).html("" + (value || \'&#160;\'));\n
\t\t\t\tbreak;\n
\t\t\tcase "width":\n
\t\t\t\tresize = true;\n
\t\t\t\tbreak;\n
\t\t}\n
\n
\t\t$.Widget.prototype._setOption.apply(self, arguments);\n
\t\tif (resize) {\n
\t\t\tself._size();\n
\t\t}\n
\t},\n
\n
\t_size: function() {\n
\t\t/* If the user has resized the dialog, the .ui-dialog and .ui-dialog-content\n
\t\t * divs will both have width and height set, so we need to reset them\n
\t\t */\n
\t\tvar options = this.options,\n
\t\t\tnonContentHeight;\n
\n
\t\t// reset content sizing\n
\t\t// hide for non content measurement because height: 0 doesn\'t work in IE quirks mode (see #4350)\n
\t\tthis.element.css({\n
\t\t\twidth: \'auto\',\n
\t\t\tminHeight: 0,\n
\t\t\theight: 0\n
\t\t});\n
\n
\t\t// reset wrapper sizing\n
\t\t// determine the height of all the non-content elements\n
\t\tnonContentHeight = this.uiDialog.css({\n
\t\t\t\theight: \'auto\',\n
\t\t\t\twidth: options.width\n
\t\t\t})\n
\t\t\t.height();\n
\n
\t\tthis.element\n
\t\t\t.css(options.height === \'auto\' ? {\n
\t\t\t\t\tminHeight: Math.max(options.minHeight - nonContentHeight, 0),\n
\t\t\t\t\theight: \'auto\'\n
\t\t\t\t} : {\n
\t\t\t\t\tminHeight: 0,\n
\t\t\t\t\theight: Math.max(options.height - nonContentHeight, 0)\t\t\t\t\n
\t\t\t})\n
\t\t\t.show();\n
\n
\t\tif (this.uiDialog.is(\':data(resizable)\')) {\n
\t\t\tthis.uiDialog.resizable(\'option\', \'minHeight\', this._minHeight());\n
\t\t}\n
\t}\n
});\n
\n
$.extend($.ui.dialog, {\n
\tversion: "1.8.2",\n
\n
\tuuid: 0,\n
\tmaxZ: 0,\n
\n
\tgetTitleId: function($el) {\n
\t\tvar id = $el.attr(\'id\');\n
\t\tif (!id) {\n
\t\t\tthis.uuid += 1;\n
\t\t\tid = this.uuid;\n
\t\t}\n
\t\treturn \'ui-dialog-title-\' + id;\n
\t},\n
\n
\toverlay: function(dialog) {\n
\t\tthis.$el = $.ui.dialog.overlay.create(dialog);\n
\t}\n
});\n
\n
$.extend($.ui.dialog.overlay, {\n
\tinstances: [],\n
\t// reuse old instances due to IE memory leak with alpha transparency (see #5185)\n
\toldInstances: [],\n
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
\t\t\t\t\t\t// stop events if the z-index of the target is < the z-index of the overlay\n
\t\t\t\t\t\treturn ($(event.target).zIndex() >= $.ui.dialog.overlay.maxZ);\n
\t\t\t\t\t});\n
\t\t\t\t}\n
\t\t\t}, 1);\n
\n
\t\t\t// allow closing by pressing the escape key\n
\t\t\t$(document).bind(\'keydown.dialog-overlay\', function(event) {\n
\t\t\t\tif (dialog.options.closeOnEscape && event.keyCode &&\n
\t\t\t\t\tevent.keyCode === $.ui.keyCode.ESCAPE) {\n
\t\t\t\t\t\n
\t\t\t\t\tdialog.close(event);\n
\t\t\t\t\tevent.preventDefault();\n
\t\t\t\t}\n
\t\t\t});\n
\n
\t\t\t// handle window resize\n
\t\t\t$(window).bind(\'resize.dialog-overlay\', $.ui.dialog.overlay.resize);\n
\t\t}\n
\n
\t\tvar $el = (this.oldInstances.pop() || $(\'<div></div>\').addClass(\'ui-widget-overlay\'))\n
\t\t\t.appendTo(document.body)\n
\t\t\t.css({\n
\t\t\t\twidth: this.width(),\n
\t\t\t\theight: this.height()\n
\t\t\t});\n
\n
\t\tif ($.fn.bgiframe) {\n
\t\t\t$el.bgiframe();\n
\t\t}\n
\n
\t\tthis.instances.push($el);\n
\t\treturn $el;\n
\t},\n
\n
\tdestroy: function($el) {\n
\t\tthis.oldInstances.push(this.instances.splice($.inArray($el, this.instances), 1)[0]);\n
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
\t\tvar scrollHeight,\n
\t\t\toffsetHeight;\n
\t\t// handle IE 6\n
\t\tif ($.browser.msie && $.browser.version < 7) {\n
\t\t\tscrollHeight = Math.max(\n
\t\t\t\tdocument.documentElement.scrollHeight,\n
\t\t\t\tdocument.body.scrollHeight\n
\t\t\t);\n
\t\t\toffsetHeight = Math.max(\n
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
\t\tvar scrollWidth,\n
\t\t\toffsetWidth;\n
\t\t// handle IE 6\n
\t\tif ($.browser.msie && $.browser.version < 7) {\n
\t\t\tscrollWidth = Math.max(\n
\t\t\t\tdocument.documentElement.scrollWidth,\n
\t\t\t\tdocument.body.scrollWidth\n
\t\t\t);\n
\t\t\toffsetWidth = Math.max(\n
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
}(jQuery));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>20507</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
