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
            <value> <string>embedapi.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

﻿/*\n
Embedded SVG-edit API\n
\n
General usage:\n
- Have an iframe somewhere pointing to a version of svg-edit > r1000\n
- Initialize the magic with:\n
var svgCanvas = new EmbeddedSVGEdit(window.frames.svgedit);\n
- Pass functions in this format:\n
svgCanvas.setSvgString(\'string\')\n
- Or if a callback is needed:\n
svgCanvas.setSvgString(\'string\')(function(data, error){\n
  if (error){\n
    // There was an error\n
  } else{\n
    // Handle data\n
  }\n
})\n
\n
Everything is done with the same API as the real svg-edit,\n
and all documentation is unchanged.\n
\n
However, this file depends on the postMessage API which\n
can only support JSON-serializable arguments and\n
return values, so, for example, arguments whose value is\n
\'undefined\', a function, a non-finite number, or a built-in\n
object like Date(), RegExp(), etc. will most likely not behave\n
as expected. In such a case one may need to host\n
the SVG editor on the same domain and reference the\n
JavaScript methods on the frame itself.\n
\n
The only other difference is\n
when handling returns: the callback notation is used instead.\n
\n
var blah = new EmbeddedSVGEdit(window.frames.svgedit);\n
blah.clearSelection(\'woot\', \'blah\', 1337, [1, 2, 3, 4, 5, \'moo\'], -42, {a: \'tree\',b:6, c: 9})(function(){console.log(\'GET DATA\',arguments)})\n
*/\n
\n
(function () {\'use strict\';\n
\n
var cbid = 0;\n
\n
function getCallbackSetter (d) {\n
  return function () {\n
    var t = this, // New callback\n
      args = [].slice.call(arguments),\n
      cbid = t.send(d, args, function(){});  // The callback (currently it\'s nothing, but will be set later)\n
\n
    return function(newcallback){\n
      t.callbacks[cbid] = newcallback; // Set callback\n
    };\n
  };\n
}\n
\n
/*\n
* Having this separate from messageListener allows us to\n
* avoid using JSON parsing (and its limitations) in the case\n
* of same domain control\n
*/\n
function addCallback (t, data) {\n
  var result = data.result || data.error;\n
  cbid = data.id;\n
  if (t.callbacks[cbid]) {\n
    if (data.result) {\n
      t.callbacks[cbid](result);\n
    } else {\n
      t.callbacks[cbid](result, \'error\');\n
    }\n
  }\n
}\n
\n
function messageListener (e) {\n
  // We accept and post strings as opposed to objects for the sake of IE9 support; this\n
  //   will most likely be changed in the future\n
  if (typeof e.data !== \'string\') {\n
    return;\n
  }\n
  var allowedOrigins = this.allowedOrigins,\n
    data = e.data && JSON.parse(e.data);\n
  if (!data || typeof data !== \'object\' || data.namespace !== \'svg-edit\' ||\n
      e.source !== this.frame.contentWindow ||\n
      (allowedOrigins.indexOf(\'*\') === -1 && allowedOrigins.indexOf(e.origin) === -1)\n
  ) {\n
    return;\n
  }\n
  addCallback(this, data);\n
}\n
\n
function getMessageListener (t) {\n
\treturn function (e) {\n
\t\tmessageListener.call(t, e);\n
\t};\n
}\n
\n
/**\n
* @param {HTMLIFrameElement} frame\n
* @param {array} [allowedOrigins=[]] Array of origins from which incoming\n
*     messages will be allowed when same origin is not used; defaults to none.\n
*     If supplied, it should probably be the same as svgEditor\'s allowedOrigins\n
*/\n
function EmbeddedSVGEdit (frame, allowedOrigins) {\n
  if (!(this instanceof EmbeddedSVGEdit)) { // Allow invocation without \'new\' keyword\n
    return new EmbeddedSVGEdit(frame);\n
  }\n
  this.allowedOrigins = allowedOrigins || [];\n
  // Initialize communication\n
  this.frame = frame;\n
  this.callbacks = {};\n
  // List of functions extracted with this:\n
  // Run in firebug on http://svg-edit.googlecode.com/svn/trunk/docs/files/svgcanvas-js.html\n
\n
  // for (var i=0,q=[],f = document.querySelectorAll(\'div.CFunction h3.CTitle a\'); i < f.length; i++) { q.push(f[i].name); }; q\n
  // var functions = [\'clearSelection\', \'addToSelection\', \'removeFromSelection\', \'open\', \'save\', \'getSvgString\', \'setSvgString\',\n
  // \'createLayer\', \'deleteCurrentLayer\', \'setCurrentLayer\', \'renameCurrentLayer\', \'setCurrentLayerPosition\', \'setLayerVisibility\',\n
  // \'moveSelectedToLayer\', \'clear\'];\n
\n
  // Newer, well, it extracts things that aren\'t documented as well. All functions accessible through the normal thingy can now be accessed though the API\n
  // var l = []; for (var i in svgCanvas){ if (typeof svgCanvas[i] == \'function\') { l.push(i);} };\n
  // Run in svgedit itself\n
  var i,\n
    functions = [\'updateElementFromJson\', \'embedImage\', \'fixOperaXML\', \'clearSelection\',\n
      \'addToSelection\',\n
      \'removeFromSelection\', \'addNodeToSelection\', \'open\', \'save\', \'getSvgString\', \'setSvgString\', \'createLayer\',\n
      \'deleteCurrentLayer\', \'getCurrentDrawing\', \'setCurrentLayer\', \'renameCurrentLayer\', \'setCurrentLayerPosition\',\n
      \'setLayerVisibility\', \'moveSelectedToLayer\', \'clear\', \'clearPath\', \'getNodePoint\', \'clonePathNode\', \'deletePathNode\',\n
      \'getResolution\', \'getImageTitle\', \'setImageTitle\', \'setResolution\', \'setBBoxZoom\', \'setZoom\', \'getMode\', \'setMode\',\n
      \'getStrokeColor\', \'setStrokeColor\', \'getFillColor\', \'setFillColor\', \'setStrokePaint\', \'setFillPaint\', \'getStrokeWidth\',\n
      \'setStrokeWidth\', \'getStrokeStyle\', \'setStrokeStyle\', \'getOpacity\', \'setOpacity\', \'getFillOpacity\', \'setFillOpacity\',\n
      \'getStrokeOpacity\', \'setStrokeOpacity\', \'getTransformList\', \'getBBox\', \'getRotationAngle\', \'setRotationAngle\', \'each\',\n
      \'bind\', \'setIdPrefix\', \'getBold\', \'setBold\', \'getItalic\', \'setItalic\', \'getFontFamily\', \'setFontFamily\', \'getFontSize\',\n
      \'setFontSize\', \'getText\', \'setTextContent\', \'setImageURL\', \'setRectRadius\', \'setSegType\', \'quickClone\',\n
      \'changeSelectedAttributeNoUndo\', \'changeSelectedAttribute\', \'deleteSelectedElements\', \'groupSelectedElements\', \'zoomChanged\',\n
      \'ungroupSelectedElement\', \'moveToTopSelectedElement\', \'moveToBottomSelectedElement\', \'moveSelectedElements\',\n
      \'getStrokedBBox\', \'getVisibleElements\', \'cycleElement\', \'getUndoStackSize\', \'getRedoStackSize\', \'getNextUndoCommandText\',\n
      \'getNextRedoCommandText\', \'undo\', \'redo\', \'cloneSelectedElements\', \'alignSelectedElements\', \'getZoom\', \'getVersion\',\n
      \'setIconSize\', \'setLang\', \'setCustomHandlers\'];\n
\n
  // TODO: rewrite the following, it\'s pretty scary.\n
  for (i = 0; i < functions.length; i++) {\n
    this[functions[i]] = getCallbackSetter(functions[i]);\n
  }\n
 \n
  // Older IE may need a polyfill for addEventListener, but so it would for SVG\n
  window.addEventListener(\'message\', getMessageListener(this), false);\n
}\n
\n
EmbeddedSVGEdit.prototype.send = function (name, args, callback){\n
  var t = this;\n
  cbid++;\n
\n
  this.callbacks[cbid] = callback;\n
  setTimeout(function () { // Delay for the callback to be set in case its synchronous\n
    /*\n
    * Todo: Handle non-JSON arguments and return values (undefined,\n
    *   nonfinite numbers, functions, and built-in objects like Date,\n
    *   RegExp), etc.? Allow promises instead of callbacks? Review\n
    *   SVG-Edit functions for whether JSON-able parameters can be\n
    *   made compatile with all API functionality\n
    */\n
    // We accept and post strings for the sake of IE9 support\n
    if (window.location.origin === t.frame.contentWindow.location.origin) {\n
      // Although we do not really need this API if we are working same\n
      //  domain, it could allow us to write in a way that would work\n
      //  cross-domain as well, assuming we stick to the argument limitations\n
      //  of the current JSON-based communication API (e.g., not passing\n
      //  callbacks). We might be able to address these shortcomings; see\n
      //  the todo elsewhere in this file.\n
      var message = {id: cbid},\n
        svgCanvas = t.frame.contentWindow.svgCanvas;\n
      try {\n
        message.result = svgCanvas[name].apply(svgCanvas, args);\n
      }\n
      catch (err) {\n
        message.error = err.message;\n
      }\n
      addCallback(t, message);\n
    }\n
    else { // Requires the ext-xdomain-messaging.js extension\n
      t.frame.contentWindow.postMessage(JSON.stringify({namespace: \'svgCanvas\', id: cbid, name: name, args: args}), \'*\');\n
    }\n
  }, 0);\n
  return cbid;\n
};\n
\n
window.embedded_svg_edit = EmbeddedSVGEdit; // Export old, deprecated API\n
window.EmbeddedSVGEdit = EmbeddedSVGEdit; // Follows common JS convention of CamelCase and, as enforced in JSLint, of initial caps for constructors\n
\n
}());\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>8004</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
