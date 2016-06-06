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
            <value> <string>anonymous_http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts52852217.37</string> </value>
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

/**\n
 * Package: svgedit.contextmenu\n
 * \n
 * Licensed under the Apache License, Version 2\n
 * \n
 * Author: Adam Bender\n
 */\n
// Dependencies:\n
// 1) jQuery (for dom injection of context menus)\\\n
\n
var svgedit = svgedit || {};\n
(function() {\n
  var self = this;\n
  if (!svgedit.contextmenu) {\n
    svgedit.contextmenu = {};\n
  }\n
  self.contextMenuExtensions = {}\n
  var addContextMenuItem = function(menuItem) {\n
    // menuItem: {id, label, shortcut, action}\n
    if (!menuItemIsValid(menuItem)) {\n
      console\n
          .error("Menu items must be defined and have at least properties: id, label, action, where action must be a function");\n
      return;\n
    }\n
    if (menuItem.id in self.contextMenuExtensions) {\n
      console.error(\'Cannot add extension "\' + menuItem.id\n
          + \'", an extension by that name already exists"\');\n
      return;\n
    }\n
    // Register menuItem action, see below for deferred menu dom injection\n
    console.log("Registed contextmenu item: {id:"+ menuItem.id+", label:"+menuItem.label+"}");\n
    self.contextMenuExtensions[menuItem.id] = menuItem;\n
    //TODO: Need to consider how to handle custom enable/disable behavior\n
  }\n
  var hasCustomHandler = function(handlerKey) {\n
    return self.contextMenuExtensions[handlerKey] && true;\n
  }\n
  var getCustomHandler = function(handlerKey) {\n
    return self.contextMenuExtensions[handlerKey].action;\n
  }\n
  var injectExtendedContextMenuItemIntoDom = function(menuItem) {\n
    if (Object.keys(self.contextMenuExtensions).length == 0) {\n
      // all menuItems appear at the bottom of the menu in their own container.\n
      // if this is the first extension menu we need to add the separator.\n
      $("#cmenu_canvas").append("<li class=\'separator\'>");\n
    }\n
    var shortcut = menuItem.shortcut || "";\n
    $("#cmenu_canvas").append("<li class=\'disabled\'><a href=\'#" + menuItem.id + "\'>"                   \n
                  + menuItem.label + "<span class=\'shortcut\'>"\n
                  + shortcut + "</span></a></li>");\n
  }\n
\n
  var menuItemIsValid = function(menuItem) {\n
    return menuItem && menuItem.id && menuItem.label && menuItem.action && typeof menuItem.action == \'function\';\n
  }\n
  \n
  // Defer injection to wait out initial menu processing. This probably goes away once all context\n
  // menu behavior is brought here.\n
  methodDraw.ready(function() {\n
    for (menuItem in contextMenuExtensions) {\n
      injectExtendedContextMenuItemIntoDom(contextMenuExtensions[menuItem]);\n
    }\n
  });\n
  svgedit.contextmenu.resetCustomMenus = function(){self.contextMenuExtensions = {}}\n
  svgedit.contextmenu.add = addContextMenuItem;\n
  svgedit.contextmenu.hasCustomHandler = hasCustomHandler;\n
  svgedit.contextmenu.getCustomHandler = getCustomHandler;\n
})();\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2703</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
