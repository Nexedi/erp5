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
            <value> <string>ts86919616.08</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>DetachedDialog.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

\n
  /*--------------------------------------:noTabs=true:tabSize=2:indentSize=2:--\n
    --  Xinha (is not htmlArea) - http://xinha.gogo.co.nz/\n
    --\n
    --  Use of Xinha is granted by the terms of the htmlArea License (based on\n
    --  BSD license)  please read license.txt in this package for details.\n
    --\n
    --  Xinha was originally based on work by Mihai Bazon which is:\n
    --      Copyright (c) 2003-2004 dynarch.com.\n
    --      Copyright (c) 2002-2003 interactivetools.com, inc.\n
    --      This copyright notice MUST stay intact for use.\n
    --\n
    --  $HeadURL: http://svn.xinha.webfactional.com/trunk/modules/Dialogs/inline-dialog.js $\n
    --  $LastChangedDate: 2007-01-24 03:26:04 +1300 (Wed, 24 Jan 2007) $\n
    --  $LastChangedRevision: 694 $\n
    --  $LastChangedBy: gogo $\n
    --------------------------------------------------------------------------*/\n
 \n
/** The DivDialog is used as a semi-independant means of using a Plugin outside of \n
 *  Xinha, it does not depend on having a Xinha editor available - not that of of course\n
 *  Plugins themselves may (and very likely do) require an editor.\n
 *\n
 *  @param Div into which the dialog will draw itself.\n
 *\n
 *  @param HTML for the dialog, with the special subtitutions...\n
 *    id="[someidhere]" will assign a unique id to the element in question\n
 *        and this can be retrieved with yourDialog.getElementById(\'someidhere\')   \n
 *    _(Some Text Here) will localize the text, this is used for within attributes\n
 *    <l10n>Some Text Here</l10n> will localize the text, this is used outside attributes\n
 *\n
 *  @param A function which can take a native (english) string and return a localized version,\n
 *   OR;   A "context" to be used with the standard Xinha._lc() method,\n
 *   OR;   Null - no localization will happen, only native strings will be used.\n
 *\n
 */\n
\n
Xinha.DetachedDialog = function( html, localizer, size, options)\n
{\n
  var fakeeditor =\n
  {\n
    \'config\': new Xinha.Config(),\n
    \'scrollPos\': Xinha.prototype.scrollPos,\n
    \'_someEditorHasBeenActivated\': false,\n
    \'saveSelection\': function() { },\n
    \'deactivateEditor\' : function() { },\n
    \'_textArea\': document.createElement(\'textarea\'),\n
    \'_iframe\'  : document.createElement(\'div\'),\n
    \'_doc\'     : document,\n
    \'hidePanels\': function() { },    \n
    \'showPanels\': function() { },\n
    \'_isFullScreen\': false, // maybe not ?\n
    \'activateEditor\': function() { },\n
    \'restoreSelection\': function() { },\n
    \'updateToolbar\': function() { },\n
    \'focusEditor\': function() { }    \n
  };\n
  \n
  Xinha.Dialog.initialZ = 100;\n
  this.attached = false;\n
  \n
  Xinha.DetachedDialog.parentConstructor.call(this, fakeeditor, html, localizer, size, options);\n
}\n
\n
Xinha.extend(Xinha.DetachedDialog, Xinha.Dialog);\n
\n
\n
Xinha.DetachedDialog.prototype.attachToPanel \n
  = function() { return false; }\n
  \n
Xinha.DetachedDialog.prototype.detachFromToPanel \n
  = function() { return false; }\n
\n
\n
\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2900</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>DetachedDialog.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
