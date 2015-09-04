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
            <value> <string>ts40515059.46</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>contextmenu.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals $, svgEditor*/\n
/*jslint vars: true, eqeq: true*/\n
/**\n
 * Package: svgedit.contextmenu\n
 * \n
 * Licensed under the Apache License, Version 2\n
 * \n
 * Author: Adam Bender\n
 */\n
// Dependencies:\n
// 1) jQuery (for dom injection of context menus)\n
var svgedit = svgedit || {};\n
(function() {\n
\tvar self = this;\n
\tif (!svgedit.contextmenu) {\n
\t\tsvgedit.contextmenu = {};\n
\t}\n
\tself.contextMenuExtensions = {};\n
\tvar menuItemIsValid = function(menuItem) {\n
\t\treturn menuItem && menuItem.id && menuItem.label && menuItem.action && typeof menuItem.action == \'function\';\n
\t};\n
\tvar addContextMenuItem = function(menuItem) {\n
\t\t// menuItem: {id, label, shortcut, action}\n
\t\tif (!menuItemIsValid(menuItem)) {\n
\t\t\tconsole.error("Menu items must be defined and have at least properties: id, label, action, where action must be a function");\n
\t\t\treturn;\n
\t\t}\n
\t\tif (menuItem.id in self.contextMenuExtensions) {\n
\t\t\tconsole.error(\'Cannot add extension "\' + menuItem.id + \'", an extension by that name already exists"\');\n
\t\t\treturn;\n
\t\t}\n
\t\t// Register menuItem action, see below for deferred menu dom injection\n
\t\tconsole.log("Registed contextmenu item: {id:"+ menuItem.id+", label:"+menuItem.label+"}");\n
\t\tself.contextMenuExtensions[menuItem.id] = menuItem;\n
\t\t//TODO: Need to consider how to handle custom enable/disable behavior\n
\t};\n
\tvar hasCustomHandler = function(handlerKey) {\n
\t\treturn self.contextMenuExtensions[handlerKey] && true;\n
\t};\n
\tvar getCustomHandler = function(handlerKey) {\n
\t\treturn self.contextMenuExtensions[handlerKey].action;\n
\t};\n
\tvar injectExtendedContextMenuItemIntoDom = function(menuItem) {\n
\t\tif (Object.keys(self.contextMenuExtensions).length === 0) {\n
\t\t\t// all menuItems appear at the bottom of the menu in their own container.\n
\t\t\t// if this is the first extension menu we need to add the separator.\n
\t\t\t$("#cmenu_canvas").append("<li class=\'separator\'>");\n
\t\t}\n
\t\tvar shortcut = menuItem.shortcut || "";\n
\t\t$("#cmenu_canvas").append("<li class=\'disabled\'><a href=\'#" + menuItem.id + "\'>"\n
\t\t\t\t\t\t\t\t\t+ menuItem.label + "<span class=\'shortcut\'>"\n
\t\t\t\t\t\t\t\t\t+ shortcut + "</span></a></li>");\n
\t};\n
\t// Defer injection to wait out initial menu processing. This probably goes away once all context\n
\t// menu behavior is brought here.\n
\tsvgEditor.ready(function() {\n
\t\tvar menuItem;\n
\t\tfor (menuItem in contextMenuExtensions) {\n
\t\t\tinjectExtendedContextMenuItemIntoDom(contextMenuExtensions[menuItem]);\n
\t\t}\n
\t});\n
\tsvgedit.contextmenu.resetCustomMenus = function(){self.contextMenuExtensions = {};};\n
\tsvgedit.contextmenu.add = addContextMenuItem;\n
\tsvgedit.contextmenu.hasCustomHandler = hasCustomHandler;\n
\tsvgedit.contextmenu.getCustomHandler = getCustomHandler;\n
}());\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2638</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
