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
            <value> <string>ts86919632.48</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>div-dialog.js</string> </value>
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
Xinha.DivDialog = function(rootElem, html, localizer)\n
{\n
  this.id    = { };\n
  this.r_id  = { }; // reverse lookup id\n
  this.document = document;\n
  \n
  this.rootElem = rootElem;\n
  this.rootElem.className += \' dialog\';\n
  this.rootElem.style.display  = \'none\';\n
    \n
  this.width  =  this.rootElem.offsetWidth + \'px\';\n
  this.height =  this.rootElem.offsetHeight + \'px\';\n
  \n
  this.setLocalizer(localizer);\n
  this.rootElem.innerHTML = this.translateHtml(html);  \n
}\n
\n
Xinha.extend(Xinha.DivDialog, Xinha.Dialog);\n
\n
Xinha.DivDialog.prototype.show = function(values)\n
{  \n
  if(typeof values != \'undefined\')\n
  {\n
    this.setValues(values);\n
  }\n
  \n
  this.rootElem.style.display   = \'\';\n
};\n
\n
Xinha.DivDialog.prototype.hide = function()\n
{\n
  this.rootElem.style.display         = \'none\';\n
  return this.getValues();\n
};\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2631</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>div-dialog.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
