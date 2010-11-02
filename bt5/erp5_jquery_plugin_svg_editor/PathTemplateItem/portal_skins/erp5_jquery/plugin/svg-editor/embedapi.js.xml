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
            <value> <string>ts80046427.57</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>embedapi.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

﻿/*\n
function embedded_svg_edit(frame){\n
  //initialize communication\n
  this.frame = frame;\n
  this.stack = []; //callback stack\n
  \n
  var editapi = this;\n
  \n
  window.addEventListener("message", function(e){\n
    if(e.data.substr(0,5) == "ERROR"){\n
      editapi.stack.splice(0,1)[0](e.data,"error")\n
    }else{\n
      editapi.stack.splice(0,1)[0](e.data)\n
    }\n
  }, false)\n
}\n
\n
embedded_svg_edit.prototype.call = function(code, callback){\n
  this.stack.push(callback);\n
  this.frame.contentWindow.postMessage(code,"*");\n
}\n
\n
embedded_svg_edit.prototype.getSvgString = function(callback){\n
  this.call("svgCanvas.getSvgString()",callback)\n
}\n
\n
embedded_svg_edit.prototype.setSvgString = function(svg){\n
  this.call("svgCanvas.setSvgString(\'"+svg.replace(/\'/g, "\\\\\'")+"\')");\n
}\n
*/\n
\n
\n
/*\n
Embedded SVG-edit API\n
\n
General usage:\n
- Have an iframe somewhere pointing to a version of svg-edit > r1000\n
- Initialize the magic with:\n
var svgCanvas = new embedded_svg_edit(window.frames[\'svgedit\']);\n
- Pass functions in this format:\n
svgCanvas.setSvgString("string")\n
- Or if a callback is needed:\n
svgCanvas.setSvgString("string")(function(data, error){\n
  if(error){\n
    //there was an error\n
  }else{\n
    //handle data\n
  }\n
})\n
\n
Everything is done with the same API as the real svg-edit, \n
and all documentation is unchanged. The only difference is\n
when handling returns, the callback notation is used instead. \n
\n
var blah = new embedded_svg_edit(window.frames[\'svgedit\']);\n
blah.clearSelection("woot","blah",1337,[1,2,3,4,5,"moo"],-42,{a: "tree",b:6, c: 9})(function(){console.log("GET DATA",arguments)})\n
*/\n
\n
function embedded_svg_edit(frame){\n
  //initialize communication\n
  this.frame = frame;\n
  //this.stack = [] //callback stack\n
  this.callbacks = {}; //successor to stack\n
  this.encode = embedded_svg_edit.encode;\n
  //List of functions extracted with this:\n
  //Run in firebug on http://svg-edit.googlecode.com/svn/trunk/docs/files/svgcanvas-js.html\n
  \n
  //for(var i=0,q=[],f = document.querySelectorAll("div.CFunction h3.CTitle a");i<f.length;i++){q.push(f[i].name)};q\n
  //var functions = ["clearSelection", "addToSelection", "removeFromSelection", "open", "save", "getSvgString", "setSvgString", "createLayer", "deleteCurrentLayer", "getNumLayers", "getLayer", "getCurrentLayer", "setCurrentLayer", "renameCurrentLayer", "setCurrentLayerPosition", "getLayerVisibility", "setLayerVisibility", "moveSelectedToLayer", "getLayerOpacity", "setLayerOpacity", "clear"];\n
  \n
  \n
  //Newer, well, it extracts things that aren\'t documented as well. All functions accessible through the normal thingy can now be accessed though the API\n
  //var l=[];for(var i in svgCanvas){if(typeof svgCanvas[i] == "function"){l.push(i)}};\n
  //run in svgedit itself\n
  var functions = ["updateElementFromJson", "embedImage", "fixOperaXML", "clearSelection", "addToSelection", "removeFromSelection", "addNodeToSelection", "open", "save", "getSvgString", "setSvgString", "createLayer", "deleteCurrentLayer", "getNumLayers", "getLayer", "getCurrentLayer", "setCurrentLayer", "renameCurrentLayer", "setCurrentLayerPosition", "getLayerVisibility", "setLayerVisibility", "moveSelectedToLayer", "getLayerOpacity", "setLayerOpacity", "clear", "clearPath", "getNodePoint", "clonePathNode", "deletePathNode", "getResolution", "getImageTitle", "setImageTitle", "setResolution", "setBBoxZoom", "setZoom", "getMode", "setMode", "getStrokeColor", "setStrokeColor", "getFillColor", "setFillColor", "setStrokePaint", "setFillPaint", "getStrokeWidth", "setStrokeWidth", "getStrokeStyle", "setStrokeStyle", "getOpacity", "setOpacity", "getFillOpacity", "setFillOpacity", "getStrokeOpacity", "setStrokeOpacity", "getTransformList", "getBBox", "getRotationAngle", "setRotationAngle", "each", "bind", "setIdPrefix", "getBold", "setBold", "getItalic", "setItalic", "getFontFamily", "setFontFamily", "getFontSize", "setFontSize", "getText", "setTextContent", "setImageURL", "setRectRadius", "setSegType", "quickClone", "beginUndoableChange", "changeSelectedAttributeNoUndo", "finishUndoableChange", "changeSelectedAttribute", "deleteSelectedElements", "groupSelectedElements", "ungroupSelectedElement", "moveToTopSelectedElement", "moveToBottomSelectedElement", "moveSelectedElements", "getStrokedBBox", "getVisibleElements", "cycleElement", "getUndoStackSize", "getRedoStackSize", "getNextUndoCommandText", "getNextRedoCommandText", "undo", "redo", "cloneSelectedElements", "alignSelectedElements", "getZoom", "getVersion", "setIconSize", "setLang", "setCustomHandlers"]\n
  \n
  //TODO: rewrite the following, it\'s pretty scary.\n
  for(var i = 0; i < functions.length; i++){\n
    this[functions[i]] = (function(d){\n
      return function(){\n
        var t = this //new callback\n
        for(var g = 0, args = []; g < arguments.length; g++){\n
          args.push(arguments[g]);\n
        }\n
        var cbid = t.send(d,args, function(){})  //the callback (currently it\'s nothing, but will be set later\n
        \n
        return function(newcallback){\n
          t.callbacks[cbid] = newcallback; //set callback\n
        }\n
      }\n
    })(functions[i])\n
  }\n
  //TODO: use AddEvent for Trident browsers, currently they dont support SVG, but they do support onmessage\n
  var t = this;\n
  window.addEventListener("message", function(e){\n
    if(e.data.substr(0,4)=="SVGe"){ //because svg-edit is too longish\n
      var data = e.data.substr(4);\n
      var cbid = data.substr(0, data.indexOf(";"));\n
      if(t.callbacks[cbid]){\n
        if(data.substr(0,6) != "error:"){\n
          t.callbacks[cbid](eval("("+data.substr(cbid.length+1)+")"))\n
        }else{\n
          t.callbacks[cbid](data, "error");\n
        }\n
      }\n
    }\n
    //this.stack.shift()[0](e.data,e.data.substr(0,5) == "ERROR"?\'error\':null) //replace with shift\n
  }, false)\n
}\n
\n
embedded_svg_edit.encode = function(obj){\n
  //simple partial JSON encoder implementation\n
  if(window.JSON && JSON.stringify) return JSON.stringify(obj);\n
  var enc = arguments.callee; //for purposes of recursion\n
  \n
  if(typeof obj == "boolean" || typeof obj == "number"){\n
      return obj+\'\' //should work...\n
  }else if(typeof obj == "string"){\n
    //a large portion of this is stolen from Douglas Crockford\'s json2.js\n
    return \'"\'+\n
          obj.replace(\n
            /[\\\\\\"\\x00-\\x1f\\x7f-\\x9f\\u00ad\\u0600-\\u0604\\u070f\\u17b4\\u17b5\\u200c-\\u200f\\u2028-\\u202f\\u2060-\\u206f\\ufeff\\ufff0-\\uffff]/g\n
          , function (a) {\n
            return \'\\\\u\' + (\'0000\' + a.charCodeAt(0).toString(16)).slice(-4);\n
          })\n
          +\'"\'; //note that this isn\'t quite as purtyful as the usualness\n
  }else if(obj.length){ //simple hackish test for arrayish-ness\n
    for(var i = 0; i < obj.length; i++){\n
      obj[i] = enc(obj[i]); //encode every sub-thingy on top\n
    }\n
    return "["+obj.join(",")+"]";\n
  }else{\n
    var pairs = []; //pairs will be stored here\n
    for(var k in obj){ //loop through thingys\n
      pairs.push(enc(k)+":"+enc(obj[k])); //key: value\n
    }\n
    return "{"+pairs.join(",")+"}" //wrap in the braces\n
  }\n
}\n
\n
embedded_svg_edit.prototype.send = function(name, args, callback){\n
  var cbid = Math.floor(Math.random()*31776352877+993577).toString();\n
  //this.stack.push(callback);\n
  this.callbacks[cbid] = callback;\n
  for(var argstr = [], i = 0; i < args.length; i++){\n
    argstr.push(this.encode(args[i]))\n
  }\n
  var t = this;\n
  setTimeout(function(){//delay for the callback to be set in case its synchronous\n
    t.frame.contentWindow.postMessage(cbid+";svgCanvas[\'"+name+"\']("+argstr.join(",")+")","*");\n
  }, 0);\n
  return cbid;\n
  //this.stack.shift()("svgCanvas[\'"+name+"\']("+argstr.join(",")+")")\n
}\n
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
            <value> <int>7532</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
