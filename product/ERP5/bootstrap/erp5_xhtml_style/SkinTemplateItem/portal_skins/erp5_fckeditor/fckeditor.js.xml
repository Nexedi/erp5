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
            <value> <string>ts68196955.18</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>fckeditor.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * FCKeditor - The text editor for Internet - http://www.fckeditor.net\n
 * Copyright (C) 2003-2010 Frederico Caldeira Knabben\n
 *\n
 * == BEGIN LICENSE ==\n
 *\n
 * Licensed under the terms of any of the following licenses at your\n
 * choice:\n
 *\n
 *  - GNU General Public License Version 2 or later (the "GPL")\n
 *    http://www.gnu.org/licenses/gpl.html\n
 *\n
 *  - GNU Lesser General Public License Version 2.1 or later (the "LGPL")\n
 *    http://www.gnu.org/licenses/lgpl.html\n
 *\n
 *  - Mozilla Public License Version 1.1 or later (the "MPL")\n
 *    http://www.mozilla.org/MPL/MPL-1.1.html\n
 *\n
 * == END LICENSE ==\n
 *\n
 * This is the integration file for JavaScript.\n
 *\n
 * It defines the FCKeditor class that can be used to create editor\n
 * instances in a HTML page in the client side. For server side\n
 * operations, use the specific integration system.\n
 */\n
\n
// FCKeditor Class\n
var FCKeditor = function( instanceName, width, height, toolbarSet, value )\n
{\n
\t// Properties\n
\tthis.InstanceName\t= instanceName ;\n
\tthis.Width\t\t\t= width\t\t\t|| \'100%\' ;\n
\tthis.Height\t\t\t= height\t\t|| \'200\' ;\n
\tthis.ToolbarSet\t\t= toolbarSet\t|| \'Default\' ;\n
\tthis.Value\t\t\t= value\t\t\t|| \'\' ;\n
\tthis.BasePath\t\t= FCKeditor.BasePath ;\n
\tthis.CheckBrowser\t= true ;\n
\tthis.DisplayErrors\t= true ;\n
\n
\tthis.Config\t\t\t= new Object() ;\n
\n
\t// Events\n
\tthis.OnError\t\t= null ;\t// function( source, errorNumber, errorDescription )\n
};\n
\n
/**\n
 * This is the default BasePath used by all editor instances.\n
 */\n
FCKeditor.BasePath = \'/fckeditor/\' ;\n
\n
/**\n
 * The minimum height used when replacing textareas.\n
 */\n
FCKeditor.MinHeight = 200 ;\n
\n
/**\n
 * The minimum width used when replacing textareas.\n
 */\n
FCKeditor.MinWidth = 750 ;\n
\n
FCKeditor.prototype.Version\t\t\t= \'2.6.8\' ;\n
FCKeditor.prototype.VersionBuild\t= \'25427\' ;\n
\n
FCKeditor.prototype.Create = function()\n
{\n
\tdocument.write( this.CreateHtml() ) ;\n
};\n
\n
FCKeditor.prototype.CreateHtml = function()\n
{\n
\t// Check for errors\n
\tif ( !this.InstanceName || this.InstanceName.length === 0 )\n
\t{\n
\t\tthis._ThrowError( 701, \'You must specify an instance name.\' ) ;\n
\t\treturn \'\' ;\n
\t}\n
\n
\tvar sHtml = \'\' ;\n
\n
\tif ( !this.CheckBrowser || this._IsCompatibleBrowser() )\n
\t{\n
\t\tsHtml += \'<input type="hidden" id="\' + this.InstanceName + \'" name="\' + this.InstanceName + \'" value="\' + this._HTMLEncode( this.Value ) + \'" style="display:none" />\' ;\n
\t\tsHtml += this._GetConfigHtml() ;\n
\t\tsHtml += this._GetIFrameHtml() ;\n
\t}\n
\telse\n
\t{\n
\t\tvar sWidth  = this.Width.toString().indexOf(\'%\')  > 0 ? this.Width  : this.Width  + \'px\' ;\n
\t\tvar sHeight = this.Height.toString().indexOf(\'%\') > 0 ? this.Height : this.Height + \'px\' ;\n
\n
\t\tsHtml += \'<textarea name="\' + this.InstanceName +\n
\t\t\t\'" rows="4" cols="40" style="width:\' + sWidth +\n
\t\t\t\';height:\' + sHeight ;\n
\n
\t\tif ( this.TabIndex )\n
\t\t\tsHtml += \'" tabindex="\' + this.TabIndex ;\n
\n
\t\tsHtml += \'">\' +\n
\t\t\tthis._HTMLEncode( this.Value ) +\n
\t\t\t\'<\\/textarea>\' ;\n
\t}\n
\n
\treturn sHtml ;\n
};\n
\n
FCKeditor.prototype.ReplaceTextarea = function()\n
{\n
\tif ( document.getElementById( this.InstanceName + \'___Frame\' ) )\n
\t\treturn ;\n
\tif ( !this.CheckBrowser || this._IsCompatibleBrowser() )\n
\t{\n
\t\t// We must check the elements firstly using the Id and then the name.\n
\t\tvar oTextarea = document.getElementById( this.InstanceName ) ;\n
\t\tvar colElementsByName = document.getElementsByName( this.InstanceName ) ;\n
\t\tvar i = 0;\n
\t\twhile ( oTextarea || i === 0 )\n
\t\t{\n
\t\t\tif ( oTextarea && oTextarea.tagName.toLowerCase() == \'textarea\' )\n
\t\t\t\tbreak ;\n
                        i = i+1;\n
\t\t\toTextarea = colElementsByName[i] ;\n
\t\t}\n
\n
\t\tif ( !oTextarea )\n
\t\t{\n
\t\t\talert( \'Error: The TEXTAREA with id or name set to "\' + this.InstanceName + \'" was not found\' ) ;\n
\t\t\treturn ;\n
\t\t}\n
\n
\t\toTextarea.style.display = \'none\' ;\n
\n
\t\tif ( oTextarea.tabIndex )\n
\t\t\tthis.TabIndex = oTextarea.tabIndex ;\n
\n
\t\tthis._InsertHtmlBefore( this._GetConfigHtml(), oTextarea ) ;\n
\t\tthis._InsertHtmlBefore( this._GetIFrameHtml(), oTextarea ) ;\n
\t}\n
};\n
\n
FCKeditor.prototype._InsertHtmlBefore = function( html, element )\n
{\n
\tif ( element.insertAdjacentHTML )\t// IE\n
\t\telement.insertAdjacentHTML( \'beforeBegin\', html ) ;\n
\telse\t\t\t\t\t\t\t\t// Gecko\n
\t{\n
\t\tvar oRange = document.createRange() ;\n
\t\toRange.setStartBefore( element ) ;\n
\t\tvar oFragment = oRange.createContextualFragment( html );\n
\t\telement.parentNode.insertBefore( oFragment, element ) ;\n
\t}\n
};\n
\n
FCKeditor.prototype._GetConfigHtml = function()\n
{\n
\tvar sConfig = \'\' ;\n
\tfor ( var o in this.Config )\n
\t{\n
\t\tif ( sConfig.length > 0 ) sConfig += \'&amp;\' ;\n
\t\tsConfig += encodeURIComponent( o ) + \'=\' + encodeURIComponent( this.Config[o] ) ;\n
\t}\n
\n
\treturn \'<input type="hidden" id="\' + this.InstanceName + \'___Config" value="\' + sConfig + \'" style="display:none" />\' ;\n
};\n
\n
FCKeditor.prototype._GetIFrameHtml = function()\n
{\n
\tvar sFile = \'fckeditor.html\' ;\n
\n
\ttry\n
\t{\n
\t\tif ( (/fcksource=true/i).test( window.top.location.search ) )\n
\t\t\tsFile = \'fckeditor.original.html\' ;\n
\t}\n
\tcatch (e) { /* Ignore it. Much probably we are inside a FRAME where the "top" is in another domain (security error). */ }\n
\n
\tvar sLink = this.BasePath + \'editor/\' + sFile + \'?InstanceName=\' + encodeURIComponent( this.InstanceName ) ;\n
\tif (this.ToolbarSet)\n
\t\tsLink += \'&amp;Toolbar=\' + this.ToolbarSet ;\n
\n
\tvar html = \'<iframe id="\' + this.InstanceName +\n
\t\t\'___Frame" src="\' + sLink +\n
\t\t\'" width="\' + this.Width +\n
\t\t\'" height="\' + this.Height ;\n
\n
\tif ( this.TabIndex )\n
\t\thtml += \'" tabindex="\' + this.TabIndex ;\n
\n
\thtml += \'" frameborder="0" scrolling="no"></iframe>\' ;\n
\n
\treturn html ;\n
};\n
\n
FCKeditor.prototype._IsCompatibleBrowser = function()\n
{\n
\treturn FCKeditor_IsCompatibleBrowser() ;\n
};\n
\n
FCKeditor.prototype._ThrowError = function( errorNumber, errorDescription )\n
{\n
\tthis.ErrorNumber\t\t= errorNumber ;\n
\tthis.ErrorDescription\t= errorDescription ;\n
\n
\tif ( this.DisplayErrors )\n
\t{\n
\t\tdocument.write( \'<div style="COLOR: #ff0000">\' ) ;\n
\t\tdocument.write( \'[ FCKeditor Error \' + this.ErrorNumber + \': \' + this.ErrorDescription + \' ]\' ) ;\n
\t\tdocument.write( \'</div>\' ) ;\n
\t}\n
\n
\tif ( typeof( this.OnError ) == \'function\' )\n
\t\tthis.OnError( this, errorNumber, errorDescription ) ;\n
};\n
\n
FCKeditor.prototype._HTMLEncode = function( text )\n
{\n
\tif ( typeof( text ) != "string" )\n
\t\ttext = text.toString() ;\n
\n
\ttext = text.replace(\n
\t\t/&/g, "&amp;").replace(\n
\t\t/"/g, "&quot;").replace(\n
\t\t/</g, "&lt;").replace(\n
\t\t/>/g, "&gt;") ;\n
\n
\treturn text ;\n
}\n
\n
;(function()\n
{\n
\tvar textareaToEditor = function( textarea )\n
\t{\n
\t\tvar editor = new FCKeditor( textarea.name ) ;\n
\n
\t\teditor.Width = Math.max( textarea.offsetWidth, FCKeditor.MinWidth ) ;\n
\t\teditor.Height = Math.max( textarea.offsetHeight, FCKeditor.MinHeight ) ;\n
\n
\t\treturn editor ;\n
\t};\n
\n
\t/**\n
\t * Replace all <textarea> elements available in the document with FCKeditor\n
\t * instances.\n
\t *\n
\t *\t// Replace all <textarea> elements in the page.\n
\t *\tFCKeditor.ReplaceAllTextareas() ;\n
\t *\n
\t *\t// Replace all <textarea class="myClassName"> elements in the page.\n
\t *\tFCKeditor.ReplaceAllTextareas( \'myClassName\' ) ;\n
\t *\n
\t *\t// Selectively replace <textarea> elements, based on custom assertions.\n
\t *\tFCKeditor.ReplaceAllTextareas( function( textarea, editor )\n
\t *\t\t{\n
\t *\t\t\t// Custom code to evaluate the replace, returning false if it\n
\t *\t\t\t// must not be done.\n
\t *\t\t\t// It also passes the "editor" parameter, so the developer can\n
\t *\t\t\t// customize the instance.\n
\t *\t\t} ) ;\n
\t */\n
\tFCKeditor.ReplaceAllTextareas = function()\n
\t{\n
\t\tvar textareas = document.getElementsByTagName( \'textarea\' ) ;\n
\n
\t\tfor ( var i = 0 ; i < textareas.length ; i++ )\n
\t\t{\n
\t\t\tvar editor = null ;\n
\t\t\tvar textarea = textareas[i] ;\n
\t\t\tvar name = textarea.name ;\n
\n
\t\t\t// The "name" attribute must exist.\n
\t\t\tif ( !name || name.length === 0 )\n
\t\t\t\tcontinue ;\n
\n
\t\t\tif ( typeof arguments[0] == \'string\' )\n
\t\t\t{\n
\t\t\t\t// The textarea class name could be passed as the function\n
\t\t\t\t// parameter.\n
\n
\t\t\t\tvar classRegex = new RegExp( \'(?:^| )\' + arguments[0] + \'(?:$| )\' ) ;\n
\n
\t\t\t\tif ( !classRegex.test( textarea.className ) )\n
\t\t\t\t\tcontinue ;\n
\t\t\t}\n
\t\t\telse if ( typeof arguments[0] == \'function\' )\n
\t\t\t{\n
\t\t\t\t// An assertion function could be passed as the function parameter.\n
\t\t\t\t// It must explicitly return "false" to ignore a specific <textarea>.\n
\t\t\t\teditor = textareaToEditor( textarea ) ;\n
\t\t\t\tif ( arguments[0]( textarea, editor ) === false )\n
\t\t\t\t\tcontinue ;\n
\t\t\t}\n
\n
\t\t\tif ( !editor )\n
\t\t\t\teditor = textareaToEditor( textarea ) ;\n
\n
\t\t\teditor.ReplaceTextarea() ;\n
\t\t}\n
\t};\n
})() ;\n
\n
function FCKeditor_IsCompatibleBrowser()\n
{\n
\tvar sAgent = navigator.userAgent.toLowerCase() ;\n
\n
\t// Internet Explorer 5.5+\n
\tif ( false && sAgent.indexOf("mac") == -1 )  //@cc_on!@\n
\t{\n
\t\tvar sBrowserVersion = navigator.appVersion.match(/MSIE (.\\..)/)[1] ;\n
\t\treturn ( sBrowserVersion >= 5.5 ) ;\n
\t}\n
\n
\t// Gecko (Opera 9 tries to behave like Gecko at this point).\n
\tif ( navigator.product == "Gecko" && navigator.productSub >= 20030210 && !( typeof(opera) == \'object\' && opera.postError ) )\n
\t\treturn true ;\n
\n
\t// Opera 9.50+\n
\tif ( window.opera && window.opera.version && parseFloat( window.opera.version() ) >= 9.5 )\n
\t\treturn true ;\n
\n
\t// Adobe AIR\n
\t// Checked before Safari because AIR have the WebKit rich text editor\n
\t// features from Safari 3.0.4, but the version reported is 420.\n
\tif ( sAgent.indexOf( \' adobeair/\' ) != -1 )\n
\t\treturn ( sAgent.match( / adobeair\\/(\\d+)/ )[1] >= 1 ) ;\t// Build must be at least v1\n
\n
\t// Safari 3+\n
\tif ( sAgent.indexOf( \' applewebkit/\' ) != -1 )\n
\t\treturn ( sAgent.match( / applewebkit\\/(\\d+)/ )[1] >= 522 ) ;\t// Build must be at least 522 (v3)\n
\n
\treturn false ;\n
}\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>9321</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
