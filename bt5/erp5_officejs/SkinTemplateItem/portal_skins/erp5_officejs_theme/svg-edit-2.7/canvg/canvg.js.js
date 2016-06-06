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
            <value> <string>canvg.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAI=</string> </persistent>
            </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>86764</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="2" aka="AAAAAAAAAAI=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\r\n
 * canvg.js - Javascript SVG parser and renderer on Canvas\r\n
 * MIT Licensed\r\n
 * Gabe Lerner (gabelerner@gmail.com)\r\n
 * http://code.google.com/p/canvg/\r\n
 *\r\n
 * Requires: rgbcolor.js - http://www.phpied.com/rgb-color-parser-in-javascript/\r\n
 */\r\n
if(!window.console) {\r\n
\twindow.console = {};\r\n
\twindow.console.log = function(str) {};\r\n
\twindow.console.dir = function(str) {};\r\n
}\r\n
\r\n
if(!Array.prototype.indexOf){\r\n
\tArray.prototype.indexOf = function(obj){\r\n
\t\tfor(var i=0; i<this.length; i++){\r\n
\t\t\tif(this[i]==obj){\r\n
\t\t\t\treturn i;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\treturn -1;\r\n
\t}\r\n
}\r\n
\r\n
(function(){\r\n
\t// canvg(target, s)\r\n
\t// empty parameters: replace all \'svg\' elements on page with \'canvas\' elements\r\n
\t// target: canvas element or the id of a canvas element\r\n
\t// s: svg string, url to svg file, or xml document\r\n
\t// opts: optional hash of options\r\n
\t//\t\t ignoreMouse: true => ignore mouse events\r\n
\t//\t\t ignoreAnimation: true => ignore animations\r\n
\t//\t\t ignoreDimensions: true => does not try to resize canvas\r\n
\t//\t\t ignoreClear: true => does not clear canvas\r\n
\t//\t\t offsetX: int => draws at a x offset\r\n
\t//\t\t offsetY: int => draws at a y offset\r\n
\t//\t\t scaleWidth: int => scales horizontally to width\r\n
\t//\t\t scaleHeight: int => scales vertically to height\r\n
\t//\t\t renderCallback: function => will call the function after the first render is completed\r\n
\t//\t\t forceRedraw: function => will call the function on every frame, if it returns true, will redraw\r\n
\tthis.canvg = function (target, s, opts) {\r\n
\t\t// no parameters\r\n
\t\tif (target == null && s == null && opts == null) {\r\n
\t\t\tvar svgTags = document.getElementsByTagName(\'svg\');\r\n
\t\t\tfor (var i=0; i<svgTags.length; i++) {\r\n
\t\t\t\tvar svgTag = svgTags[i];\r\n
\t\t\t\tvar c = document.createElement(\'canvas\');\r\n
\t\t\t\tc.width = svgTag.clientWidth;\r\n
\t\t\t\tc.height = svgTag.clientHeight;\r\n
\t\t\t\tsvgTag.parentNode.insertBefore(c, svgTag);\r\n
\t\t\t\tsvgTag.parentNode.removeChild(svgTag);\r\n
\t\t\t\tvar div = document.createElement(\'div\');\r\n
\t\t\t\tdiv.appendChild(svgTag);\r\n
\t\t\t\tcanvg(c, div.innerHTML);\r\n
\t\t\t}\r\n
\t\t\treturn;\r\n
\t\t}\r\n
\t\topts = opts || {};\r\n
\r\n
\t\tif (typeof target == \'string\') {\r\n
\t\t\ttarget = document.getElementById(target);\r\n
\t\t}\r\n
\r\n
\t\t// reuse class per canvas\r\n
\t\tvar svg;\r\n
\t\tif (target.svg == null) {\r\n
\t\t\tsvg = build();\r\n
\t\t\ttarget.svg = svg;\r\n
\t\t}\r\n
\t\telse {\r\n
\t\t\tsvg = target.svg;\r\n
\t\t\tsvg.stop();\r\n
\t\t}\r\n
\t\tsvg.opts = opts;\r\n
\r\n
\t\tvar ctx = target.getContext(\'2d\');\r\n
\t\tif (typeof(s.documentElement) != \'undefined\') {\r\n
\t\t\t// load from xml doc\r\n
\t\t\tsvg.loadXmlDoc(ctx, s);\r\n
\t\t}\r\n
\t\telse if (s.substr(0,1) == \'<\') {\r\n
\t\t\t// load from xml string\r\n
\t\t\tsvg.loadXml(ctx, s);\r\n
\t\t}\r\n
\t\telse {\r\n
\t\t\t// load from url\r\n
\t\t\tsvg.load(ctx, s);\r\n
\t\t}\r\n
\t}\r\n
\r\n
\tfunction build() {\r\n
\t\tvar svg = { };\r\n
\r\n
\t\tsvg.FRAMERATE = 30;\r\n
\t\tsvg.MAX_VIRTUAL_PIXELS = 30000;\r\n
\r\n
\t\t// globals\r\n
\t\tsvg.init = function(ctx) {\r\n
\t\t\tsvg.Definitions = {};\r\n
\t\t\tsvg.Styles = {};\r\n
\t\t\tsvg.Animations = [];\r\n
\t\t\tsvg.Images = [];\r\n
\t\t\tsvg.ctx = ctx;\r\n
\t\t\tsvg.ViewPort = new (function () {\r\n
\t\t\t\tthis.viewPorts = [];\r\n
\t\t\t\tthis.Clear = function() { this.viewPorts = []; }\r\n
\t\t\t\tthis.SetCurrent = function(width, height) { this.viewPorts.push({ width: width, height: height }); }\r\n
\t\t\t\tthis.RemoveCurrent = function() { this.viewPorts.pop(); }\r\n
\t\t\t\tthis.Current = function() { return this.viewPorts[this.viewPorts.length - 1]; }\r\n
\t\t\t\tthis.width = function() { return this.Current().width; }\r\n
\t\t\t\tthis.height = function() { return this.Current().height; }\r\n
\t\t\t\tthis.ComputeSize = function(d) {\r\n
\t\t\t\t\tif (d != null && typeof(d) == \'number\') return d;\r\n
\t\t\t\t\tif (d == \'x\') return this.width();\r\n
\t\t\t\t\tif (d == \'y\') return this.height();\r\n
\t\t\t\t\treturn Math.sqrt(Math.pow(this.width(), 2) + Math.pow(this.height(), 2)) / Math.sqrt(2);\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t}\r\n
\t\tsvg.init();\r\n
\r\n
\t\t// images loaded\r\n
\t\tsvg.ImagesLoaded = function() {\r\n
\t\t\tfor (var i=0; i<svg.Images.length; i++) {\r\n
\t\t\t\tif (!svg.Images[i].loaded) return false;\r\n
\t\t\t}\r\n
\t\t\treturn true;\r\n
\t\t}\r\n
\r\n
\t\t// trim\r\n
\t\tsvg.trim = function(s) { return s.replace(/^\\s+|\\s+$/g, \'\'); }\r\n
\r\n
\t\t// compress spaces\r\n
\t\tsvg.compressSpaces = function(s) { return s.replace(/[\\s\\r\\t\\n]+/gm,\' \'); }\r\n
\r\n
\t\t// ajax\r\n
\t\tsvg.ajax = function(url) {\r\n
\t\t\tvar AJAX;\r\n
\t\t\tif(window.XMLHttpRequest){AJAX=new XMLHttpRequest();}\r\n
\t\t\telse{AJAX=new ActiveXObject(\'Microsoft.XMLHTTP\');}\r\n
\t\t\tif(AJAX){\r\n
\t\t\t   AJAX.open(\'GET\',url,false);\r\n
\t\t\t   AJAX.send(null);\r\n
\t\t\t   return AJAX.responseText;\r\n
\t\t\t}\r\n
\t\t\treturn null;\r\n
\t\t}\r\n
\r\n
\t\t// parse xml\r\n
\t\tsvg.parseXml = function(xml) {\r\n
\t\t\tif (window.DOMParser)\r\n
\t\t\t{\r\n
\t\t\t\tvar parser = new DOMParser();\r\n
\t\t\t\treturn parser.parseFromString(xml, \'text/xml\');\r\n
\t\t\t}\r\n
\t\t\telse\r\n
\t\t\t{\r\n
\t\t\t\txml = xml.replace(/<!DOCTYPE svg[^>]*>/, \'\');\r\n
\t\t\t\tvar xmlDoc = new ActiveXObject(\'Microsoft.XMLDOM\');\r\n
\t\t\t\txmlDoc.async = \'false\';\r\n
\t\t\t\txmlDoc.loadXML(xml);\r\n
\t\t\t\treturn xmlDoc;\r\n
\t\t\t}\r\n
\t\t}\r\n
\r\n
\t\tsvg.Property = function(name, value) {\r\n
\t\t\tthis.name = name;\r\n
\t\t\tthis.value = value;\r\n
\r\n
\t\t\tthis.hasValue = function() {\r\n
\t\t\t\treturn (this.value != null && this.value !== \'\');\r\n
\t\t\t}\r\n
\r\n
\t\t\t// return the numerical value of the property\r\n
\t\t\tthis.numValue = function() {\r\n
\t\t\t\tif (!this.hasValue()) return 0;\r\n
\r\n
\t\t\t\tvar n = parseFloat(this.value);\r\n
\t\t\t\tif ((this.value + \'\').match(/%$/)) {\r\n
\t\t\t\t\tn = n / 100.0;\r\n
\t\t\t\t}\r\n
\t\t\t\treturn n;\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.valueOrDefault = function(def) {\r\n
\t\t\t\tif (this.hasValue()) return this.value;\r\n
\t\t\t\treturn def;\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.numValueOrDefault = function(def) {\r\n
\t\t\t\tif (this.hasValue()) return this.numValue();\r\n
\t\t\t\treturn def;\r\n
\t\t\t}\r\n
\r\n
\t\t\t/* EXTENSIONS */\r\n
\t\t\tvar that = this;\r\n
\r\n
\t\t\t// color extensions\r\n
\t\t\tthis.Color = {\r\n
\t\t\t\t// augment the current color value with the opacity\r\n
\t\t\t\taddOpacity: function(opacity) {\r\n
\t\t\t\t\tvar newValue = that.value;\r\n
\t\t\t\t\tif (opacity != null && opacity != \'\') {\r\n
\t\t\t\t\t\tvar color = new RGBColor(that.value);\r\n
\t\t\t\t\t\tif (color.ok) {\r\n
\t\t\t\t\t\t\tnewValue = \'rgba(\' + color.r + \', \' + color.g + \', \' + color.b + \', \' + opacity + \')\';\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn new svg.Property(that.name, newValue);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\t// definition extensions\r\n
\t\t\tthis.Definition = {\r\n
\t\t\t\t// get the definition from the definitions table\r\n
\t\t\t\tgetDefinition: function() {\r\n
\t\t\t\t\tvar name = that.value.replace(/^(url\\()?#([^\\)]+)\\)?$/, \'$2\');\r\n
\t\t\t\t\treturn svg.Definitions[name];\r\n
\t\t\t\t},\r\n
\r\n
\t\t\t\tisUrl: function() {\r\n
\t\t\t\t\treturn that.value.indexOf(\'url(\') == 0\r\n
\t\t\t\t},\r\n
\r\n
\t\t\t\tgetFillStyle: function(e) {\r\n
\t\t\t\t\tvar def = this.getDefinition();\r\n
\r\n
\t\t\t\t\t// gradient\r\n
\t\t\t\t\tif (def != null && def.createGradient) {\r\n
\t\t\t\t\t\treturn def.createGradient(svg.ctx, e);\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\t// pattern\r\n
\t\t\t\t\tif (def != null && def.createPattern) {\r\n
\t\t\t\t\t\treturn def.createPattern(svg.ctx, e);\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\treturn null;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\t// length extensions\r\n
\t\t\tthis.Length = {\r\n
\t\t\t\tDPI: function(viewPort) {\r\n
\t\t\t\t\treturn 96.0; // TODO: compute?\r\n
\t\t\t\t},\r\n
\r\n
\t\t\t\tEM: function(viewPort) {\r\n
\t\t\t\t\tvar em = 12;\r\n
\r\n
\t\t\t\t\tvar fontSize = new svg.Property(\'fontSize\', svg.Font.Parse(svg.ctx.font).fontSize);\r\n
\t\t\t\t\tif (fontSize.hasValue()) em = fontSize.Length.toPixels(viewPort);\r\n
\r\n
\t\t\t\t\treturn em;\r\n
\t\t\t\t},\r\n
\r\n
\t\t\t\t// get the length as pixels\r\n
\t\t\t\ttoPixels: function(viewPort) {\r\n
\t\t\t\t\tif (!that.hasValue()) return 0;\r\n
\t\t\t\t\tvar s = that.value+\'\';\r\n
\t\t\t\t\tif (s.match(/em$/)) return that.numValue() * this.EM(viewPort);\r\n
\t\t\t\t\tif (s.match(/ex$/)) return that.numValue() * this.EM(viewPort) / 2.0;\r\n
\t\t\t\t\tif (s.match(/px$/)) return that.numValue();\r\n
\t\t\t\t\tif (s.match(/pt$/)) return that.numValue() * 1.25;\r\n
\t\t\t\t\tif (s.match(/pc$/)) return that.numValue() * 15;\r\n
\t\t\t\t\tif (s.match(/cm$/)) return that.numValue() * this.DPI(viewPort) / 2.54;\r\n
\t\t\t\t\tif (s.match(/mm$/)) return that.numValue() * this.DPI(viewPort) / 25.4;\r\n
\t\t\t\t\tif (s.match(/in$/)) return that.numValue() * this.DPI(viewPort);\r\n
\t\t\t\t\tif (s.match(/%$/)) return that.numValue() * svg.ViewPort.ComputeSize(viewPort);\r\n
\t\t\t\t\treturn that.numValue();\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\t// time extensions\r\n
\t\t\tthis.Time = {\r\n
\t\t\t\t// get the time as milliseconds\r\n
\t\t\t\ttoMilliseconds: function() {\r\n
\t\t\t\t\tif (!that.hasValue()) return 0;\r\n
\t\t\t\t\tvar s = that.value+\'\';\r\n
\t\t\t\t\tif (s.match(/s$/)) return that.numValue() * 1000;\r\n
\t\t\t\t\tif (s.match(/ms$/)) return that.numValue();\r\n
\t\t\t\t\treturn that.numValue();\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\t// angle extensions\r\n
\t\t\tthis.Angle = {\r\n
\t\t\t\t// get the angle as radians\r\n
\t\t\t\ttoRadians: function() {\r\n
\t\t\t\t\tif (!that.hasValue()) return 0;\r\n
\t\t\t\t\tvar s = that.value+\'\';\r\n
\t\t\t\t\tif (s.match(/deg$/)) return that.numValue() * (Math.PI / 180.0);\r\n
\t\t\t\t\tif (s.match(/grad$/)) return that.numValue() * (Math.PI / 200.0);\r\n
\t\t\t\t\tif (s.match(/rad$/)) return that.numValue();\r\n
\t\t\t\t\treturn that.numValue() * (Math.PI / 180.0);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
\r\n
\t\t// fonts\r\n
\t\tsvg.Font = new (function() {\r\n
\t\t\tthis.Styles = [\'normal\',\'italic\',\'oblique\',\'inherit\'];\r\n
\t\t\tthis.Variants = [\'normal\',\'small-caps\',\'inherit\'];\r\n
\t\t\tthis.Weights = [\'normal\',\'bold\',\'bolder\',\'lighter\',\'100\',\'200\',\'300\',\'400\',\'500\',\'600\',\'700\',\'800\',\'900\',\'inherit\'];\r\n
\r\n
\t\t\tthis.CreateFont = function(fontStyle, fontVariant, fontWeight, fontSize, fontFamily, inherit) {\r\n
\t\t\t\tvar f = inherit != null ? this.Parse(inherit) : this.CreateFont(\'\', \'\', \'\', \'\', \'\', svg.ctx.font);\r\n
\t\t\t\treturn {\r\n
\t\t\t\t\tfontFamily: fontFamily || f.fontFamily,\r\n
\t\t\t\t\tfontSize: fontSize || f.fontSize,\r\n
\t\t\t\t\tfontStyle: fontStyle || f.fontStyle,\r\n
\t\t\t\t\tfontWeight: fontWeight || f.fontWeight,\r\n
\t\t\t\t\tfontVariant: fontVariant || f.fontVariant,\r\n
\t\t\t\t\ttoString: function () { return [this.fontStyle, this.fontVariant, this.fontWeight, this.fontSize, this.fontFamily].join(\' \') }\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tvar that = this;\r\n
\t\t\tthis.Parse = function(s) {\r\n
\t\t\t\tvar f = {};\r\n
\t\t\t\tvar d = svg.trim(svg.compressSpaces(s || \'\')).split(\' \');\r\n
\t\t\t\tvar set = { fontSize: false, fontStyle: false, fontWeight: false, fontVariant: false }\r\n
\t\t\t\tvar ff = \'\';\r\n
\t\t\t\tfor (var i=0; i<d.length; i++) {\r\n
\t\t\t\t\tif (!set.fontStyle && that.Styles.indexOf(d[i]) != -1) { if (d[i] != \'inherit\') f.fontStyle = d[i]; set.fontStyle = true; }\r\n
\t\t\t\t\telse if (!set.fontVariant && that.Variants.indexOf(d[i]) != -1) { if (d[i] != \'inherit\') f.fontVariant = d[i]; set.fontStyle = set.fontVariant = true;\t}\r\n
\t\t\t\t\telse if (!set.fontWeight && that.Weights.indexOf(d[i]) != -1) {\tif (d[i] != \'inherit\') f.fontWeight = d[i]; set.fontStyle = set.fontVariant = set.fontWeight = true; }\r\n
\t\t\t\t\telse if (!set.fontSize) { if (d[i] != \'inherit\') f.fontSize = d[i].split(\'/\')[0]; set.fontStyle = set.fontVariant = set.fontWeight = set.fontSize = true; }\r\n
\t\t\t\t\telse { if (d[i] != \'inherit\') ff += d[i]; }\r\n
\t\t\t\t} if (ff != \'\') f.fontFamily = ff;\r\n
\t\t\t\treturn f;\r\n
\t\t\t}\r\n
\t\t});\r\n
\r\n
\t\t// points and paths\r\n
\t\tsvg.ToNumberArray = function(s) {\r\n
\t\t\tvar a = svg.trim(svg.compressSpaces((s || \'\').replace(/,/g, \' \'))).split(\' \');\r\n
\t\t\tfor (var i=0; i<a.length; i++) {\r\n
\t\t\t\ta[i] = parseFloat(a[i]);\r\n
\t\t\t}\r\n
\t\t\treturn a;\r\n
\t\t}\r\n
\t\tsvg.Point = function(x, y) {\r\n
\t\t\tthis.x = x;\r\n
\t\t\tthis.y = y;\r\n
\r\n
\t\t\tthis.angleTo = function(p) {\r\n
\t\t\t\treturn Math.atan2(p.y - this.y, p.x - this.x);\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.applyTransform = function(v) {\r\n
\t\t\t\tvar xp = this.x * v[0] + this.y * v[2] + v[4];\r\n
\t\t\t\tvar yp = this.x * v[1] + this.y * v[3] + v[5];\r\n
\t\t\t\tthis.x = xp;\r\n
\t\t\t\tthis.y = yp;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.CreatePoint = function(s) {\r\n
\t\t\tvar a = svg.ToNumberArray(s);\r\n
\t\t\treturn new svg.Point(a[0], a[1]);\r\n
\t\t}\r\n
\t\tsvg.CreatePath = function(s) {\r\n
\t\t\tvar a = svg.ToNumberArray(s);\r\n
\t\t\tvar path = [];\r\n
\t\t\tfor (var i=0; i<a.length; i+=2) {\r\n
\t\t\t\tpath.push(new svg.Point(a[i], a[i+1]));\r\n
\t\t\t}\r\n
\t\t\treturn path;\r\n
\t\t}\r\n
\r\n
\t\t// bounding box\r\n
\t\tsvg.BoundingBox = function(x1, y1, x2, y2) { // pass in initial points if you want\r\n
\t\t\tthis.x1 = Number.NaN;\r\n
\t\t\tthis.y1 = Number.NaN;\r\n
\t\t\tthis.x2 = Number.NaN;\r\n
\t\t\tthis.y2 = Number.NaN;\r\n
\r\n
\t\t\tthis.x = function() { return this.x1; }\r\n
\t\t\tthis.y = function() { return this.y1; }\r\n
\t\t\tthis.width = function() { return this.x2 - this.x1; }\r\n
\t\t\tthis.height = function() { return this.y2 - this.y1; }\r\n
\r\n
\t\t\tthis.addPoint = function(x, y) {\r\n
\t\t\t\tif (x != null) {\r\n
\t\t\t\t\tif (isNaN(this.x1) || isNaN(this.x2)) {\r\n
\t\t\t\t\t\tthis.x1 = x;\r\n
\t\t\t\t\t\tthis.x2 = x;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif (x < this.x1) this.x1 = x;\r\n
\t\t\t\t\tif (x > this.x2) this.x2 = x;\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tif (y != null) {\r\n
\t\t\t\t\tif (isNaN(this.y1) || isNaN(this.y2)) {\r\n
\t\t\t\t\t\tthis.y1 = y;\r\n
\t\t\t\t\t\tthis.y2 = y;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif (y < this.y1) this.y1 = y;\r\n
\t\t\t\t\tif (y > this.y2) this.y2 = y;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tthis.addX = function(x) { this.addPoint(x, null); }\r\n
\t\t\tthis.addY = function(y) { this.addPoint(null, y); }\r\n
\r\n
\t\t\tthis.addBoundingBox = function(bb) {\r\n
\t\t\t\tthis.addPoint(bb.x1, bb.y1);\r\n
\t\t\t\tthis.addPoint(bb.x2, bb.y2);\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.addQuadraticCurve = function(p0x, p0y, p1x, p1y, p2x, p2y) {\r\n
\t\t\t\tvar cp1x = p0x + 2/3 * (p1x - p0x); // CP1 = QP0 + 2/3 *(QP1-QP0)\r\n
\t\t\t\tvar cp1y = p0y + 2/3 * (p1y - p0y); // CP1 = QP0 + 2/3 *(QP1-QP0)\r\n
\t\t\t\tvar cp2x = cp1x + 1/3 * (p2x - p0x); // CP2 = CP1 + 1/3 *(QP2-QP0)\r\n
\t\t\t\tvar cp2y = cp1y + 1/3 * (p2y - p0y); // CP2 = CP1 + 1/3 *(QP2-QP0)\r\n
\t\t\t\tthis.addBezierCurve(p0x, p0y, cp1x, cp2x, cp1y,\tcp2y, p2x, p2y);\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.addBezierCurve = function(p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y) {\r\n
\t\t\t\t// from http://blog.hackers-cafe.net/2009/06/how-to-calculate-bezier-curves-bounding.html\r\n
\t\t\t\tvar p0 = [p0x, p0y], p1 = [p1x, p1y], p2 = [p2x, p2y], p3 = [p3x, p3y];\r\n
\t\t\t\tthis.addPoint(p0[0], p0[1]);\r\n
\t\t\t\tthis.addPoint(p3[0], p3[1]);\r\n
\r\n
\t\t\t\tfor (i=0; i<=1; i++) {\r\n
\t\t\t\t\tvar f = function(t) {\r\n
\t\t\t\t\t\treturn Math.pow(1-t, 3) * p0[i]\r\n
\t\t\t\t\t\t+ 3 * Math.pow(1-t, 2) * t * p1[i]\r\n
\t\t\t\t\t\t+ 3 * (1-t) * Math.pow(t, 2) * p2[i]\r\n
\t\t\t\t\t\t+ Math.pow(t, 3) * p3[i];\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\tvar b = 6 * p0[i] - 12 * p1[i] + 6 * p2[i];\r\n
\t\t\t\t\tvar a = -3 * p0[i] + 9 * p1[i] - 9 * p2[i] + 3 * p3[i];\r\n
\t\t\t\t\tvar c = 3 * p1[i] - 3 * p0[i];\r\n
\r\n
\t\t\t\t\tif (a == 0) {\r\n
\t\t\t\t\t\tif (b == 0) continue;\r\n
\t\t\t\t\t\tvar t = -c / b;\r\n
\t\t\t\t\t\tif (0 < t && t < 1) {\r\n
\t\t\t\t\t\t\tif (i == 0) this.addX(f(t));\r\n
\t\t\t\t\t\t\tif (i == 1) this.addY(f(t));\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tcontinue;\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\tvar b2ac = Math.pow(b, 2) - 4 * c * a;\r\n
\t\t\t\t\tif (b2ac < 0) continue;\r\n
\t\t\t\t\tvar t1 = (-b + Math.sqrt(b2ac)) / (2 * a);\r\n
\t\t\t\t\tif (0 < t1 && t1 < 1) {\r\n
\t\t\t\t\t\tif (i == 0) this.addX(f(t1));\r\n
\t\t\t\t\t\tif (i == 1) this.addY(f(t1));\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tvar t2 = (-b - Math.sqrt(b2ac)) / (2 * a);\r\n
\t\t\t\t\tif (0 < t2 && t2 < 1) {\r\n
\t\t\t\t\t\tif (i == 0) this.addX(f(t2));\r\n
\t\t\t\t\t\tif (i == 1) this.addY(f(t2));\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.isPointInBox = function(x, y) {\r\n
\t\t\t\treturn (this.x1 <= x && x <= this.x2 && this.y1 <= y && y <= this.y2);\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.addPoint(x1, y1);\r\n
\t\t\tthis.addPoint(x2, y2);\r\n
\t\t}\r\n
\r\n
\t\t// transforms\r\n
\t\tsvg.Transform = function(v) {\r\n
\t\t\tvar that = this;\r\n
\t\t\tthis.Type = {}\r\n
\r\n
\t\t\t// translate\r\n
\t\t\tthis.Type.translate = function(s) {\r\n
\t\t\t\tthis.p = svg.CreatePoint(s);\r\n
\t\t\t\tthis.apply = function(ctx) {\r\n
\t\t\t\t\tctx.translate(this.p.x || 0.0, this.p.y || 0.0);\r\n
\t\t\t\t}\r\n
\t\t\t\tthis.applyToPoint = function(p) {\r\n
\t\t\t\t\tp.applyTransform([1, 0, 0, 1, this.p.x || 0.0, this.p.y || 0.0]);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\t// rotate\r\n
\t\t\tthis.Type.rotate = function(s) {\r\n
\t\t\t\tvar a = svg.ToNumberArray(s);\r\n
\t\t\t\tthis.angle = new svg.Property(\'angle\', a[0]);\r\n
\t\t\t\tthis.cx = a[1] || 0;\r\n
\t\t\t\tthis.cy = a[2] || 0;\r\n
\t\t\t\tthis.apply = function(ctx) {\r\n
\t\t\t\t\tctx.translate(this.cx, this.cy);\r\n
\t\t\t\t\tctx.rotate(this.angle.Angle.toRadians());\r\n
\t\t\t\t\tctx.translate(-this.cx, -this.cy);\r\n
\t\t\t\t}\r\n
\t\t\t\tthis.applyToPoint = function(p) {\r\n
\t\t\t\t\tvar a = this.angle.Angle.toRadians();\r\n
\t\t\t\t\tp.applyTransform([1, 0, 0, 1, this.p.x || 0.0, this.p.y || 0.0]);\r\n
\t\t\t\t\tp.applyTransform([Math.cos(a), Math.sin(a), -Math.sin(a), Math.cos(a), 0, 0]);\r\n
\t\t\t\t\tp.applyTransform([1, 0, 0, 1, -this.p.x || 0.0, -this.p.y || 0.0]);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.Type.scale = function(s) {\r\n
\t\t\t\tthis.p = svg.CreatePoint(s);\r\n
\t\t\t\tthis.apply = function(ctx) {\r\n
\t\t\t\t\tctx.scale(this.p.x || 1.0, this.p.y || this.p.x || 1.0);\r\n
\t\t\t\t}\r\n
\t\t\t\tthis.applyToPoint = function(p) {\r\n
\t\t\t\t\tp.applyTransform([this.p.x || 0.0, 0, 0, this.p.y || 0.0, 0, 0]);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.Type.matrix = function(s) {\r\n
\t\t\t\tthis.m = svg.ToNumberArray(s);\r\n
\t\t\t\tthis.apply = function(ctx) {\r\n
\t\t\t\t\tctx.transform(this.m[0], this.m[1], this.m[2], this.m[3], this.m[4], this.m[5]);\r\n
\t\t\t\t}\r\n
\t\t\t\tthis.applyToPoint = function(p) {\r\n
\t\t\t\t\tp.applyTransform(this.m);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.Type.SkewBase = function(s) {\r\n
\t\t\t\tthis.base = that.Type.matrix;\r\n
\t\t\t\tthis.base(s);\r\n
\t\t\t\tthis.angle = new svg.Property(\'angle\', s);\r\n
\t\t\t}\r\n
\t\t\tthis.Type.SkewBase.prototype = new this.Type.matrix;\r\n
\r\n
\t\t\tthis.Type.skewX = function(s) {\r\n
\t\t\t\tthis.base = that.Type.SkewBase;\r\n
\t\t\t\tthis.base(s);\r\n
\t\t\t\tthis.m = [1, 0, Math.tan(this.angle.Angle.toRadians()), 1, 0, 0];\r\n
\t\t\t}\r\n
\t\t\tthis.Type.skewX.prototype = new this.Type.SkewBase;\r\n
\r\n
\t\t\tthis.Type.skewY = function(s) {\r\n
\t\t\t\tthis.base = that.Type.SkewBase;\r\n
\t\t\t\tthis.base(s);\r\n
\t\t\t\tthis.m = [1, Math.tan(this.angle.Angle.toRadians()), 0, 1, 0, 0];\r\n
\t\t\t}\r\n
\t\t\tthis.Type.skewY.prototype = new this.Type.SkewBase;\r\n
\r\n
\t\t\tthis.transforms = [];\r\n
\r\n
\t\t\tthis.apply = function(ctx) {\r\n
\t\t\t\tfor (var i=0; i<this.transforms.length; i++) {\r\n
\t\t\t\t\tthis.transforms[i].apply(ctx);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.applyToPoint = function(p) {\r\n
\t\t\t\tfor (var i=0; i<this.transforms.length; i++) {\r\n
\t\t\t\t\tthis.transforms[i].applyToPoint(p);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tvar data = svg.trim(svg.compressSpaces(v)).split(/\\s(?=[a-z])/);\r\n
\t\t\tfor (var i=0; i<data.length; i++) {\r\n
\t\t\t\tvar type = data[i].split(\'(\')[0];\r\n
\t\t\t\tvar s = data[i].split(\'(\')[1].replace(\')\',\'\');\r\n
\t\t\t\tvar transform = new this.Type[type](s);\r\n
\t\t\t\tthis.transforms.push(transform);\r\n
\t\t\t}\r\n
\t\t}\r\n
\r\n
\t\t// aspect ratio\r\n
\t\tsvg.AspectRatio = function(ctx, aspectRatio, width, desiredWidth, height, desiredHeight, minX, minY, refX, refY) {\r\n
\t\t\t// aspect ratio - http://www.w3.org/TR/SVG/coords.html#PreserveAspectRatioAttribute\r\n
\t\t\taspectRatio = svg.compressSpaces(aspectRatio);\r\n
\t\t\taspectRatio = aspectRatio.replace(/^defer\\s/,\'\'); // ignore defer\r\n
\t\t\tvar align = aspectRatio.split(\' \')[0] || \'xMidYMid\';\r\n
\t\t\tvar meetOrSlice = aspectRatio.split(\' \')[1] || \'meet\';\r\n
\r\n
\t\t\t// calculate scale\r\n
\t\t\tvar scaleX = width / desiredWidth;\r\n
\t\t\tvar scaleY = height / desiredHeight;\r\n
\t\t\tvar scaleMin = Math.min(scaleX, scaleY);\r\n
\t\t\tvar scaleMax = Math.max(scaleX, scaleY);\r\n
\t\t\tif (meetOrSlice == \'meet\') { desiredWidth *= scaleMin; desiredHeight *= scaleMin; }\r\n
\t\t\tif (meetOrSlice == \'slice\') { desiredWidth *= scaleMax; desiredHeight *= scaleMax; }\r\n
\r\n
\t\t\trefX = new svg.Property(\'refX\', refX);\r\n
\t\t\trefY = new svg.Property(\'refY\', refY);\r\n
\t\t\tif (refX.hasValue() && refY.hasValue()) {\r\n
\t\t\t\tctx.translate(-scaleMin * refX.Length.toPixels(\'x\'), -scaleMin * refY.Length.toPixels(\'y\'));\r\n
\t\t\t}\r\n
\t\t\telse {\r\n
\t\t\t\t// align\r\n
\t\t\t\tif (align.match(/^xMid/) && ((meetOrSlice == \'meet\' && scaleMin == scaleY) || (meetOrSlice == \'slice\' && scaleMax == scaleY))) ctx.translate(width / 2.0 - desiredWidth / 2.0, 0);\r\n
\t\t\t\tif (align.match(/YMid$/) && ((meetOrSlice == \'meet\' && scaleMin == scaleX) || (meetOrSlice == \'slice\' && scaleMax == scaleX))) ctx.translate(0, height / 2.0 - desiredHeight / 2.0);\r\n
\t\t\t\tif (align.match(/^xMax/) && ((meetOrSlice == \'meet\' && scaleMin == scaleY) || (meetOrSlice == \'slice\' && scaleMax == scaleY))) ctx.translate(width - desiredWidth, 0);\r\n
\t\t\t\tif (align.match(/YMax$/) && ((meetOrSlice == \'meet\' && scaleMin == scaleX) || (meetOrSlice == \'slice\' && scaleMax == scaleX))) ctx.translate(0, height - desiredHeight);\r\n
\t\t\t}\r\n
\r\n
\t\t\t// scale\r\n
\t\t\tif (align == \'none\') ctx.scale(scaleX, scaleY);\r\n
\t\t\telse if (meetOrSlice == \'meet\') ctx.scale(scaleMin, scaleMin);\r\n
\t\t\telse if (meetOrSlice == \'slice\') ctx.scale(scaleMax, scaleMax); \r\n
\r\n
\t\t\t// translate\r\n
\t\t\tctx.translate(minX == null ? 0 : -minX, minY == null ? 0 : -minY);\r\n
\t\t}\r\n
\r\n
\t\t// elements\r\n
\t\tsvg.Element = {}\r\n
\r\n
\t\tsvg.Element.ElementBase = function(node) {\r\n
\t\t\tthis.attributes = {};\r\n
\t\t\tthis.styles = {};\r\n
\t\t\tthis.children = [];\r\n
\r\n
\t\t\t// get or create attribute\r\n
\t\t\tthis.attribute = function(name, createIfNotExists) {\r\n
\t\t\t\tvar a = this.attributes[name];\r\n
\t\t\t\tif (a != null) return a;\r\n
\r\n
\t\t\t\ta = new svg.Property(name, \'\');\r\n
\t\t\t\tif (createIfNotExists == true) this.attributes[name] = a;\r\n
\t\t\t\treturn a;\r\n
\t\t\t}\r\n
\r\n
\t\t\t// get or create style, crawls up node tree\r\n
\t\t\tthis.style = function(name, createIfNotExists) {\r\n
\t\t\t\tvar s = this.styles[name];\r\n
\t\t\t\tif (s != null) return s;\r\n
\r\n
\t\t\t\tvar a = this.attribute(name);\r\n
\t\t\t\tif (a != null && a.hasValue()) {\r\n
\t\t\t\t\treturn a;\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tvar p = this.parent;\r\n
\t\t\t\tif (p != null) {\r\n
\t\t\t\t\tvar ps = p.style(name);\r\n
\t\t\t\t\tif (ps != null && ps.hasValue()) {\r\n
\t\t\t\t\t\treturn ps;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\ts = new svg.Property(name, \'\');\r\n
\t\t\t\tif (createIfNotExists == true) this.styles[name] = s;\r\n
\t\t\t\treturn s;\r\n
\t\t\t}\r\n
\r\n
\t\t\t// base render\r\n
\t\t\tthis.render = function(ctx) {\r\n
\t\t\t\t// don\'t render display=none\r\n
\t\t\t\tif (this.style(\'display\').value == \'none\') return;\r\n
\r\n
\t\t\t\t// don\'t render visibility=hidden\r\n
\t\t\t\tif (this.attribute(\'visibility\').value == \'hidden\') return;\r\n
\r\n
\t\t\t\tctx.save();\r\n
\t\t\t\t\tthis.setContext(ctx);\r\n
\t\t\t\t\t\t// mask\r\n
\t\t\t\t\t\tif (this.attribute(\'mask\').hasValue()) {\r\n
\t\t\t\t\t\t\tvar mask = this.attribute(\'mask\').Definition.getDefinition();\r\n
\t\t\t\t\t\t\tif (mask != null) mask.apply(ctx, this);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\telse if (this.style(\'filter\').hasValue()) {\r\n
\t\t\t\t\t\t\tvar filter = this.style(\'filter\').Definition.getDefinition();\r\n
\t\t\t\t\t\t\tif (filter != null) filter.apply(ctx, this);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\telse this.renderChildren(ctx);\r\n
\t\t\t\t\tthis.clearContext(ctx);\r\n
\t\t\t\tctx.restore();\r\n
\t\t\t}\r\n
\r\n
\t\t\t// base set context\r\n
\t\t\tthis.setContext = function(ctx) {\r\n
\t\t\t\t// OVERRIDE ME!\r\n
\t\t\t}\r\n
\r\n
\t\t\t// base clear context\r\n
\t\t\tthis.clearContext = function(ctx) {\r\n
\t\t\t\t// OVERRIDE ME!\r\n
\t\t\t}\r\n
\r\n
\t\t\t// base render children\r\n
\t\t\tthis.renderChildren = function(ctx) {\r\n
\t\t\t\tfor (var i=0; i<this.children.length; i++) {\r\n
\t\t\t\t\tthis.children[i].render(ctx);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.addChild = function(childNode, create) {\r\n
\t\t\t\tvar child = childNode;\r\n
\t\t\t\tif (create) child = svg.CreateElement(childNode);\r\n
\t\t\t\tchild.parent = this;\r\n
\t\t\t\tthis.children.push(child);\r\n
\t\t\t}\r\n
\r\n
\t\t\tif (node != null && node.nodeType == 1) { //ELEMENT_NODE\r\n
\t\t\t\t// add children\r\n
\t\t\t\tfor (var i=0; i<node.childNodes.length; i++) {\r\n
\t\t\t\t\tvar childNode = node.childNodes[i];\r\n
\t\t\t\t\tif (childNode.nodeType == 1) this.addChild(childNode, true); //ELEMENT_NODE\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// add attributes\r\n
\t\t\t\tfor (var i=0; i<node.attributes.length; i++) {\r\n
\t\t\t\t\tvar attribute = node.attributes[i];\r\n
\t\t\t\t\tthis.attributes[attribute.nodeName] = new svg.Property(attribute.nodeName, attribute.nodeValue);\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// add tag styles\r\n
\t\t\t\tvar styles = svg.Styles[node.nodeName];\r\n
\t\t\t\tif (styles != null) {\r\n
\t\t\t\t\tfor (var name in styles) {\r\n
\t\t\t\t\t\tthis.styles[name] = styles[name];\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// add class styles\r\n
\t\t\t\tif (this.attribute(\'class\').hasValue()) {\r\n
\t\t\t\t\tvar classes = svg.compressSpaces(this.attribute(\'class\').value).split(\' \');\r\n
\t\t\t\t\tfor (var j=0; j<classes.length; j++) {\r\n
\t\t\t\t\t\tstyles = svg.Styles[\'.\'+classes[j]];\r\n
\t\t\t\t\t\tif (styles != null) {\r\n
\t\t\t\t\t\t\tfor (var name in styles) {\r\n
\t\t\t\t\t\t\t\tthis.styles[name] = styles[name];\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tstyles = svg.Styles[node.nodeName+\'.\'+classes[j]];\r\n
\t\t\t\t\t\tif (styles != null) {\r\n
\t\t\t\t\t\t\tfor (var name in styles) {\r\n
\t\t\t\t\t\t\t\tthis.styles[name] = styles[name];\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// add inline styles\r\n
\t\t\t\tif (this.attribute(\'style\').hasValue()) {\r\n
\t\t\t\t\tvar styles = this.attribute(\'style\').value.split(\';\');\r\n
\t\t\t\t\tfor (var i=0; i<styles.length; i++) {\r\n
\t\t\t\t\t\tif (svg.trim(styles[i]) != \'\') {\r\n
\t\t\t\t\t\t\tvar style = styles[i].split(\':\');\r\n
\t\t\t\t\t\t\tvar name = svg.trim(style[0]);\r\n
\t\t\t\t\t\t\tvar value = svg.trim(style[1]);\r\n
\t\t\t\t\t\t\tthis.styles[name] = new svg.Property(name, value);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// add id\r\n
\t\t\t\tif (this.attribute(\'id\').hasValue()) {\r\n
\t\t\t\t\tif (svg.Definitions[this.attribute(\'id\').value] == null) {\r\n
\t\t\t\t\t\tsvg.Definitions[this.attribute(\'id\').value] = this;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
\r\n
\t\tsvg.Element.RenderedElementBase = function(node) {\r\n
\t\t\tthis.base = svg.Element.ElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.setContext = function(ctx) {\r\n
\t\t\t\t// fill\r\n
\t\t\t\tif (this.style(\'fill\').Definition.isUrl()) {\r\n
\t\t\t\t\tvar fs = this.style(\'fill\').Definition.getFillStyle(this);\r\n
\t\t\t\t\tif (fs != null) ctx.fillStyle = fs;\r\n
\t\t\t\t}\r\n
\t\t\t\telse if (this.style(\'fill\').hasValue()) {\r\n
\t\t\t\t\tvar fillStyle = this.style(\'fill\');\r\n
\t\t\t\t\tif (this.style(\'fill-opacity\').hasValue()) fillStyle = fillStyle.Color.addOpacity(this.style(\'fill-opacity\').value);\r\n
\t\t\t\t\tctx.fillStyle = (fillStyle.value == \'none\' ? \'rgba(0,0,0,0)\' : fillStyle.value);\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// stroke\r\n
\t\t\t\tif (this.style(\'stroke\').Definition.isUrl()) {\r\n
\t\t\t\t\tvar fs = this.style(\'stroke\').Definition.getFillStyle(this);\r\n
\t\t\t\t\tif (fs != null) ctx.strokeStyle = fs;\r\n
\t\t\t\t}\r\n
\t\t\t\telse if (this.style(\'stroke\').hasValue()) {\r\n
\t\t\t\t\tvar strokeStyle = this.style(\'stroke\');\r\n
\t\t\t\t\tif (this.style(\'stroke-opacity\').hasValue()) strokeStyle = strokeStyle.Color.addOpacity(this.style(\'stroke-opacity\').value);\r\n
\t\t\t\t\tctx.strokeStyle = (strokeStyle.value == \'none\' ? \'rgba(0,0,0,0)\' : strokeStyle.value);\r\n
\t\t\t\t}\r\n
\t\t\t\tif (this.style(\'stroke-width\').hasValue()) ctx.lineWidth = this.style(\'stroke-width\').Length.toPixels();\r\n
\t\t\t\tif (this.style(\'stroke-linecap\').hasValue()) ctx.lineCap = this.style(\'stroke-linecap\').value;\r\n
\t\t\t\tif (this.style(\'stroke-linejoin\').hasValue()) ctx.lineJoin = this.style(\'stroke-linejoin\').value;\r\n
\t\t\t\tif (this.style(\'stroke-miterlimit\').hasValue()) ctx.miterLimit = this.style(\'stroke-miterlimit\').value;\r\n
\r\n
\t\t\t\t// font\r\n
\t\t\t\tif (typeof(ctx.font) != \'undefined\') {\r\n
\t\t\t\t\tctx.font = svg.Font.CreateFont(\r\n
\t\t\t\t\t\tthis.style(\'font-style\').value,\r\n
\t\t\t\t\t\tthis.style(\'font-variant\').value,\r\n
\t\t\t\t\t\tthis.style(\'font-weight\').value,\r\n
\t\t\t\t\t\tthis.style(\'font-size\').hasValue() ? this.style(\'font-size\').Length.toPixels() + \'px\' : \'\',\r\n
\t\t\t\t\t\tthis.style(\'font-family\').value).toString();\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// transform\r\n
\t\t\t\tif (this.attribute(\'transform\').hasValue()) {\r\n
\t\t\t\t\tvar transform = new svg.Transform(this.attribute(\'transform\').value);\r\n
\t\t\t\t\ttransform.apply(ctx);\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// clip\r\n
\t\t\t\tif (this.attribute(\'clip-path\').hasValue()) {\r\n
\t\t\t\t\tvar clip = this.attribute(\'clip-path\').Definition.getDefinition();\r\n
\t\t\t\t\tif (clip != null) clip.apply(ctx);\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// opacity\r\n
\t\t\t\tif (this.style(\'opacity\').hasValue()) {\r\n
\t\t\t\t\tctx.globalAlpha = this.style(\'opacity\').numValue();\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.RenderedElementBase.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\tsvg.Element.PathElementBase = function(node) {\r\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.path = function(ctx) {\r\n
\t\t\t\tif (ctx != null) ctx.beginPath();\r\n
\t\t\t\treturn new svg.BoundingBox();\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.renderChildren = function(ctx) {\r\n
\t\t\t\tthis.path(ctx);\r\n
\t\t\t\tsvg.Mouse.checkPath(this, ctx);\r\n
\t\t\t\tif (ctx.fillStyle != \'\') ctx.fill();\r\n
\t\t\t\tif (ctx.strokeStyle != \'\') ctx.stroke();\r\n
\r\n
\t\t\t\tvar markers = this.getMarkers();\r\n
\t\t\t\tif (markers != null) {\r\n
\t\t\t\t\tif (this.style(\'marker-start\').Definition.isUrl()) {\r\n
\t\t\t\t\t\tvar marker = this.style(\'marker-start\').Definition.getDefinition();\r\n
\t\t\t\t\t\tmarker.render(ctx, markers[0][0], markers[0][1]);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif (this.style(\'marker-mid\').Definition.isUrl()) {\r\n
\t\t\t\t\t\tvar marker = this.style(\'marker-mid\').Definition.getDefinition();\r\n
\t\t\t\t\t\tfor (var i=1;i<markers.length-1;i++) {\r\n
\t\t\t\t\t\t\tmarker.render(ctx, markers[i][0], markers[i][1]);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif (this.style(\'marker-end\').Definition.isUrl()) {\r\n
\t\t\t\t\t\tvar marker = this.style(\'marker-end\').Definition.getDefinition();\r\n
\t\t\t\t\t\tmarker.render(ctx, markers[markers.length-1][0], markers[markers.length-1][1]);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.getBoundingBox = function() {\r\n
\t\t\t\treturn this.path();\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.getMarkers = function() {\r\n
\t\t\t\treturn null;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.PathElementBase.prototype = new svg.Element.RenderedElementBase;\r\n
\r\n
\t\t// svg element\r\n
\t\tsvg.Element.svg = function(node) {\r\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.baseClearContext = this.clearContext;\r\n
\t\t\tthis.clearContext = function(ctx) {\r\n
\t\t\t\tthis.baseClearContext(ctx);\r\n
\t\t\t\tsvg.ViewPort.RemoveCurrent();\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.baseSetContext = this.setContext;\r\n
\t\t\tthis.setContext = function(ctx) {\r\n
\t\t\t\t// initial values\r\n
\t\t\t\tctx.strokeStyle = \'rgba(0,0,0,0)\';\r\n
\t\t\t\tctx.lineCap = \'butt\';\r\n
\t\t\t\tctx.lineJoin = \'miter\';\r\n
\t\t\t\tctx.miterLimit = 4;\r\n
\r\n
\t\t\t\tthis.baseSetContext(ctx);\r\n
\r\n
\t\t\t\t// create new view port\r\n
\t\t\t\tif (this.attribute(\'x\').hasValue() && this.attribute(\'y\').hasValue()) {\r\n
\t\t\t\t\tctx.translate(this.attribute(\'x\').Length.toPixels(\'x\'), this.attribute(\'y\').Length.toPixels(\'y\'));\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tvar width = svg.ViewPort.width();\r\n
\t\t\t\tvar height = svg.ViewPort.height();\r\n
\t\t\t\tif (typeof(this.root) == \'undefined\' && this.attribute(\'width\').hasValue() && this.attribute(\'height\').hasValue()) {\r\n
\t\t\t\t\twidth = this.attribute(\'width\').Length.toPixels(\'x\');\r\n
\t\t\t\t\theight = this.attribute(\'height\').Length.toPixels(\'y\');\r\n
\r\n
\t\t\t\t\tvar x = 0;\r\n
\t\t\t\t\tvar y = 0;\r\n
\t\t\t\t\tif (this.attribute(\'refX\').hasValue() && this.attribute(\'refY\').hasValue()) {\r\n
\t\t\t\t\t\tx = -this.attribute(\'refX\').Length.toPixels(\'x\');\r\n
\t\t\t\t\t\ty = -this.attribute(\'refY\').Length.toPixels(\'y\');\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\tctx.beginPath();\r\n
\t\t\t\t\tctx.moveTo(x, y);\r\n
\t\t\t\t\tctx.lineTo(width, y);\r\n
\t\t\t\t\tctx.lineTo(width, height);\r\n
\t\t\t\t\tctx.lineTo(x, height);\r\n
\t\t\t\t\tctx.closePath();\r\n
\t\t\t\t\tctx.clip();\r\n
\t\t\t\t}\r\n
\t\t\t\tsvg.ViewPort.SetCurrent(width, height);\r\n
\r\n
\t\t\t\t// viewbox\r\n
\t\t\t\tif (this.attribute(\'viewBox\').hasValue()) {\r\n
\t\t\t\t\tvar viewBox = svg.ToNumberArray(this.attribute(\'viewBox\').value);\r\n
\t\t\t\t\tvar minX = viewBox[0];\r\n
\t\t\t\t\tvar minY = viewBox[1];\r\n
\t\t\t\t\twidth = viewBox[2];\r\n
\t\t\t\t\theight = viewBox[3];\r\n
\r\n
\t\t\t\t\tsvg.AspectRatio(ctx,\r\n
\t\t\t\t\t\t\t\t\tthis.attribute(\'preserveAspectRatio\').value,\r\n
\t\t\t\t\t\t\t\t\tsvg.ViewPort.width(),\r\n
\t\t\t\t\t\t\t\t\twidth,\r\n
\t\t\t\t\t\t\t\t\tsvg.ViewPort.height(),\r\n
\t\t\t\t\t\t\t\t\theight,\r\n
\t\t\t\t\t\t\t\t\tminX,\r\n
\t\t\t\t\t\t\t\t\tminY,\r\n
\t\t\t\t\t\t\t\t\tthis.attribute(\'refX\').value,\r\n
\t\t\t\t\t\t\t\t\tthis.attribute(\'refY\').value);\r\n
\r\n
\t\t\t\t\tsvg.ViewPort.RemoveCurrent();\r\n
\t\t\t\t\tsvg.ViewPort.SetCurrent(viewBox[2], viewBox[3]);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.svg.prototype = new svg.Element.RenderedElementBase;\r\n
\r\n
\t\t// rect element\r\n
\t\tsvg.Element.rect = function(node) {\r\n
\t\t\tthis.base = svg.Element.PathElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.path = function(ctx) {\r\n
\t\t\t\tvar x = this.attribute(\'x\').Length.toPixels(\'x\');\r\n
\t\t\t\tvar y = this.attribute(\'y\').Length.toPixels(\'y\');\r\n
\t\t\t\tvar width = this.attribute(\'width\').Length.toPixels(\'x\');\r\n
\t\t\t\tvar height = this.attribute(\'height\').Length.toPixels(\'y\');\r\n
\t\t\t\tvar rx = this.attribute(\'rx\').Length.toPixels(\'x\');\r\n
\t\t\t\tvar ry = this.attribute(\'ry\').Length.toPixels(\'y\');\r\n
\t\t\t\tif (this.attribute(\'rx\').hasValue() && !this.attribute(\'ry\').hasValue()) ry = rx;\r\n
\t\t\t\tif (this.attribute(\'ry\').hasValue() && !this.attribute(\'rx\').hasValue()) rx = ry;\r\n
\r\n
\t\t\t\tif (ctx != null) {\r\n
\t\t\t\t\tctx.beginPath();\r\n
\t\t\t\t\tctx.moveTo(x + rx, y);\r\n
\t\t\t\t\tctx.lineTo(x + width - rx, y);\r\n
\t\t\t\t\tctx.quadraticCurveTo(x + width, y, x + width, y + ry)\r\n
\t\t\t\t\tctx.lineTo(x + width, y + height - ry);\r\n
\t\t\t\t\tctx.quadraticCurveTo(x + width, y + height, x + width - rx, y + height)\r\n
\t\t\t\t\tctx.lineTo(x + rx, y + height);\r\n
\t\t\t\t\tctx.quadraticCurveTo(x, y + height, x, y + height - ry)\r\n
\t\t\t\t\tctx.lineTo(x, y + ry);\r\n
\t\t\t\t\tctx.quadraticCurveTo(x, y, x + rx, y)\r\n
\t\t\t\t\tctx.closePath();\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\treturn new svg.BoundingBox(x, y, x + width, y + height);\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.rect.prototype = new svg.Element.PathElementBase;\r\n
\r\n
\t\t// circle element\r\n
\t\tsvg.Element.circle = function(node) {\r\n
\t\t\tthis.base = svg.Element.PathElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.path = function(ctx) {\r\n
\t\t\t\tvar cx = this.attribute(\'cx\').Length.toPixels(\'x\');\r\n
\t\t\t\tvar cy = this.attribute(\'cy\').Length.toPixels(\'y\');\r\n
\t\t\t\tvar r = this.attribute(\'r\').Length.toPixels();\r\n
\r\n
\t\t\t\tif (ctx != null) {\r\n
\t\t\t\t\tctx.beginPath();\r\n
\t\t\t\t\tctx.arc(cx, cy, r, 0, Math.PI * 2, true);\r\n
\t\t\t\t\tctx.closePath();\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\treturn new svg.BoundingBox(cx - r, cy - r, cx + r, cy + r);\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.circle.prototype = new svg.Element.PathElementBase;\r\n
\r\n
\t\t// ellipse element\r\n
\t\tsvg.Element.ellipse = function(node) {\r\n
\t\t\tthis.base = svg.Element.PathElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.path = function(ctx) {\r\n
\t\t\t\tvar KAPPA = 4 * ((Math.sqrt(2) - 1) / 3);\r\n
\t\t\t\tvar rx = this.attribute(\'rx\').Length.toPixels(\'x\');\r\n
\t\t\t\tvar ry = this.attribute(\'ry\').Length.toPixels(\'y\');\r\n
\t\t\t\tvar cx = this.attribute(\'cx\').Length.toPixels(\'x\');\r\n
\t\t\t\tvar cy = this.attribute(\'cy\').Length.toPixels(\'y\');\r\n
\r\n
\t\t\t\tif (ctx != null) {\r\n
\t\t\t\t\tctx.beginPath();\r\n
\t\t\t\t\tctx.moveTo(cx, cy - ry);\r\n
\t\t\t\t\tctx.bezierCurveTo(cx + (KAPPA * rx), cy - ry,  cx + rx, cy - (KAPPA * ry), cx + rx, cy);\r\n
\t\t\t\t\tctx.bezierCurveTo(cx + rx, cy + (KAPPA * ry), cx + (KAPPA * rx), cy + ry, cx, cy + ry);\r\n
\t\t\t\t\tctx.bezierCurveTo(cx - (KAPPA * rx), cy + ry, cx - rx, cy + (KAPPA * ry), cx - rx, cy);\r\n
\t\t\t\t\tctx.bezierCurveTo(cx - rx, cy - (KAPPA * ry), cx - (KAPPA * rx), cy - ry, cx, cy - ry);\r\n
\t\t\t\t\tctx.closePath();\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\treturn new svg.BoundingBox(cx - rx, cy - ry, cx + rx, cy + ry);\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.ellipse.prototype = new svg.Element.PathElementBase;\r\n
\r\n
\t\t// line element\r\n
\t\tsvg.Element.line = function(node) {\r\n
\t\t\tthis.base = svg.Element.PathElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.getPoints = function() {\r\n
\t\t\t\treturn [\r\n
\t\t\t\t\tnew svg.Point(this.attribute(\'x1\').Length.toPixels(\'x\'), this.attribute(\'y1\').Length.toPixels(\'y\')),\r\n
\t\t\t\t\tnew svg.Point(this.attribute(\'x2\').Length.toPixels(\'x\'), this.attribute(\'y2\').Length.toPixels(\'y\'))];\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.path = function(ctx) {\r\n
\t\t\t\tvar points = this.getPoints();\r\n
\r\n
\t\t\t\tif (ctx != null) {\r\n
\t\t\t\t\tctx.beginPath();\r\n
\t\t\t\t\tctx.moveTo(points[0].x, points[0].y);\r\n
\t\t\t\t\tctx.lineTo(points[1].x, points[1].y);\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\treturn new svg.BoundingBox(points[0].x, points[0].y, points[1].x, points[1].y);\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.getMarkers = function() {\r\n
\t\t\t\tvar points = this.getPoints();\r\n
\t\t\t\tvar a = points[0].angleTo(points[1]);\r\n
\t\t\t\treturn [[points[0], a], [points[1], a]];\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.line.prototype = new svg.Element.PathElementBase;\r\n
\r\n
\t\t// polyline element\r\n
\t\tsvg.Element.polyline = function(node) {\r\n
\t\t\tthis.base = svg.Element.PathElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.points = svg.CreatePath(this.attribute(\'points\').value);\r\n
\t\t\tthis.path = function(ctx) {\r\n
\t\t\t\tvar bb = new svg.BoundingBox(this.points[0].x, this.points[0].y);\r\n
\t\t\t\tif (ctx != null) {\r\n
\t\t\t\t\tctx.beginPath();\r\n
\t\t\t\t\tctx.moveTo(this.points[0].x, this.points[0].y);\r\n
\t\t\t\t}\r\n
\t\t\t\tfor (var i=1; i<this.points.length; i++) {\r\n
\t\t\t\t\tbb.addPoint(this.points[i].x, this.points[i].y);\r\n
\t\t\t\t\tif (ctx != null) ctx.lineTo(this.points[i].x, this.points[i].y);\r\n
\t\t\t\t}\r\n
\t\t\t\treturn bb;\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.getMarkers = function() {\r\n
\t\t\t\tvar markers = [];\r\n
\t\t\t\tfor (var i=0; i<this.points.length - 1; i++) {\r\n
\t\t\t\t\tmarkers.push([this.points[i], this.points[i].angleTo(this.points[i+1])]);\r\n
\t\t\t\t}\r\n
\t\t\t\tmarkers.push([this.points[this.points.length-1], markers[markers.length-1][1]]);\r\n
\t\t\t\treturn markers;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.polyline.prototype = new svg.Element.PathElementBase;\r\n
\r\n
\t\t// polygon element\r\n
\t\tsvg.Element.polygon = function(node) {\r\n
\t\t\tthis.base = svg.Element.polyline;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.basePath = this.path;\r\n
\t\t\tthis.path = function(ctx) {\r\n
\t\t\t\tvar bb = this.basePath(ctx);\r\n
\t\t\t\tif (ctx != null) {\r\n
\t\t\t\t\tctx.lineTo(this.points[0].x, this.points[0].y);\r\n
\t\t\t\t\tctx.closePath();\r\n
\t\t\t\t}\r\n
\t\t\t\treturn bb;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.polygon.prototype = new svg.Element.polyline;\r\n
\r\n
\t\t// path element\r\n
\t\tsvg.Element.path = function(node) {\r\n
\t\t\tthis.base = svg.Element.PathElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tvar d = this.attribute(\'d\').value;\r\n
\t\t\t// TODO: convert to real lexer based on http://www.w3.org/TR/SVG11/paths.html#PathDataBNF\r\n
\t\t\td = d.replace(/,/gm,\' \'); // get rid of all commas\r\n
\t\t\td = d.replace(/([MmZzLlHhVvCcSsQqTtAa])([MmZzLlHhVvCcSsQqTtAa])/gm,\'$1 $2\'); // separate commands from commands\r\n
\t\t\td = d.replace(/([MmZzLlHhVvCcSsQqTtAa])([MmZzLlHhVvCcSsQqTtAa])/gm,\'$1 $2\'); // separate commands from commands\r\n
\t\t\td = d.replace(/([MmZzLlHhVvCcSsQqTtAa])([^\\s])/gm,\'$1 $2\'); // separate commands from points\r\n
\t\t\td = d.replace(/([^\\s])([MmZzLlHhVvCcSsQqTtAa])/gm,\'$1 $2\'); // separate commands from points\r\n
\t\t\td = d.replace(/([0-9])([+\\-])/gm,\'$1 $2\'); // separate digits when no comma\r\n
\t\t\td = d.replace(/(\\.[0-9]*)(\\.)/gm,\'$1 $2\'); // separate digits when no comma\r\n
\t\t\td = d.replace(/([Aa](\\s+[0-9]+){3})\\s+([01])\\s*([01])/gm,\'$1 $3 $4 \'); // shorthand elliptical arc path syntax\r\n
\t\t\td = svg.compressSpaces(d); // compress multiple spaces\r\n
\t\t\td = svg.trim(d);\r\n
\t\t\tthis.PathParser = new (function(d) {\r\n
\t\t\t\tthis.tokens = d.split(\' \');\r\n
\r\n
\t\t\t\tthis.reset = function() {\r\n
\t\t\t\t\tthis.i = -1;\r\n
\t\t\t\t\tthis.command = \'\';\r\n
\t\t\t\t\tthis.previousCommand = \'\';\r\n
\t\t\t\t\tthis.start = new svg.Point(0, 0);\r\n
\t\t\t\t\tthis.control = new svg.Point(0, 0);\r\n
\t\t\t\t\tthis.current = new svg.Point(0, 0);\r\n
\t\t\t\t\tthis.points = [];\r\n
\t\t\t\t\tthis.angles = [];\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthis.isEnd = function() {\r\n
\t\t\t\t\treturn this.i >= this.tokens.length - 1;\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthis.isCommandOrEnd = function() {\r\n
\t\t\t\t\tif (this.isEnd()) return true;\r\n
\t\t\t\t\treturn this.tokens[this.i + 1].match(/^[A-Za-z]$/) != null;\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthis.isRelativeCommand = function() {\r\n
\t\t\t\t\treturn this.command == this.command.toLowerCase();\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthis.getToken = function() {\r\n
\t\t\t\t\tthis.i = this.i + 1;\r\n
\t\t\t\t\treturn this.tokens[this.i];\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthis.getScalar = function() {\r\n
\t\t\t\t\treturn parseFloat(this.getToken());\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthis.nextCommand = function() {\r\n
\t\t\t\t\tthis.previousCommand = this.command;\r\n
\t\t\t\t\tthis.command = this.getToken();\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthis.getPoint = function() {\r\n
\t\t\t\t\tvar p = new svg.Point(this.getScalar(), this.getScalar());\r\n
\t\t\t\t\treturn this.makeAbsolute(p);\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthis.getAsControlPoint = function() {\r\n
\t\t\t\t\tvar p = this.getPoint();\r\n
\t\t\t\t\tthis.control = p;\r\n
\t\t\t\t\treturn p;\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthis.getAsCurrentPoint = function() {\r\n
\t\t\t\t\tvar p = this.getPoint();\r\n
\t\t\t\t\tthis.current = p;\r\n
\t\t\t\t\treturn p;\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthis.getReflectedControlPoint = function() {\r\n
\t\t\t\t\tif (this.previousCommand.toLowerCase() != \'c\' && this.previousCommand.toLowerCase() != \'s\') {\r\n
\t\t\t\t\t\treturn this.current;\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\t// reflect point\r\n
\t\t\t\t\tvar p = new svg.Point(2 * this.current.x - this.control.x, 2 * this.current.y - this.control.y);\r\n
\t\t\t\t\treturn p;\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthis.makeAbsolute = function(p) {\r\n
\t\t\t\t\tif (this.isRelativeCommand()) {\r\n
\t\t\t\t\t\tp.x = this.current.x + p.x;\r\n
\t\t\t\t\t\tp.y = this.current.y + p.y;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn p;\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthis.addMarker = function(p, from, priorTo) {\r\n
\t\t\t\t\t// if the last angle isn\'t filled in because we didn\'t have this point yet ...\r\n
\t\t\t\t\tif (priorTo != null && this.angles.length > 0 && this.angles[this.angles.length-1] == null) {\r\n
\t\t\t\t\t\tthis.angles[this.angles.length-1] = this.points[this.points.length-1].angleTo(priorTo);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tthis.addMarkerAngle(p, from == null ? null : from.angleTo(p));\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthis.addMarkerAngle = function(p, a) {\r\n
\t\t\t\t\tthis.points.push(p);\r\n
\t\t\t\t\tthis.angles.push(a);\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthis.getMarkerPoints = function() { return this.points; }\r\n
\t\t\t\tthis.getMarkerAngles = function() {\r\n
\t\t\t\t\tfor (var i=0; i<this.angles.length; i++) {\r\n
\t\t\t\t\t\tif (this.angles[i] == null) {\r\n
\t\t\t\t\t\t\tfor (var j=i+1; j<this.angles.length; j++) {\r\n
\t\t\t\t\t\t\t\tif (this.angles[j] != null) {\r\n
\t\t\t\t\t\t\t\t\tthis.angles[i] = this.angles[j];\r\n
\t\t\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn this.angles;\r\n
\t\t\t\t}\r\n
\t\t\t})(d);\r\n
\r\n
\t\t\tthis.path = function(ctx) {\r\n
\t\t\t\tvar pp = this.PathParser;\r\n
\t\t\t\tpp.reset();\r\n
\r\n
\t\t\t\tvar bb = new svg.BoundingBox();\r\n
\t\t\t\tif (ctx != null) ctx.beginPath();\r\n
\t\t\t\twhile (!pp.isEnd()) {\r\n
\t\t\t\t\tpp.nextCommand();\r\n
\t\t\t\t\tswitch (pp.command.toUpperCase()) {\r\n
\t\t\t\t\tcase \'M\':\r\n
\t\t\t\t\t\tvar p = pp.getAsCurrentPoint();\r\n
\t\t\t\t\t\tpp.addMarker(p);\r\n
\t\t\t\t\t\tbb.addPoint(p.x, p.y);\r\n
\t\t\t\t\t\tif (ctx != null) ctx.moveTo(p.x, p.y);\r\n
\t\t\t\t\t\tpp.start = pp.current;\r\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\r\n
\t\t\t\t\t\t\tvar p = pp.getAsCurrentPoint();\r\n
\t\t\t\t\t\t\tpp.addMarker(p, pp.start);\r\n
\t\t\t\t\t\t\tbb.addPoint(p.x, p.y);\r\n
\t\t\t\t\t\t\tif (ctx != null) ctx.lineTo(p.x, p.y);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase \'L\':\r\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\r\n
\t\t\t\t\t\t\tvar c = pp.current;\r\n
\t\t\t\t\t\t\tvar p = pp.getAsCurrentPoint();\r\n
\t\t\t\t\t\t\tpp.addMarker(p, c);\r\n
\t\t\t\t\t\t\tbb.addPoint(p.x, p.y);\r\n
\t\t\t\t\t\t\tif (ctx != null) ctx.lineTo(p.x, p.y);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase \'H\':\r\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\r\n
\t\t\t\t\t\t\tvar newP = new svg.Point((pp.isRelativeCommand() ? pp.current.x : 0) + pp.getScalar(), pp.current.y);\r\n
\t\t\t\t\t\t\tpp.addMarker(newP, pp.current);\r\n
\t\t\t\t\t\t\tpp.current = newP;\r\n
\t\t\t\t\t\t\tbb.addPoint(pp.current.x, pp.current.y);\r\n
\t\t\t\t\t\t\tif (ctx != null) ctx.lineTo(pp.current.x, pp.current.y);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase \'V\':\r\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\r\n
\t\t\t\t\t\t\tvar newP = new svg.Point(pp.current.x, (pp.isRelativeCommand() ? pp.current.y : 0) + pp.getScalar());\r\n
\t\t\t\t\t\t\tpp.addMarker(newP, pp.current);\r\n
\t\t\t\t\t\t\tpp.current = newP;\r\n
\t\t\t\t\t\t\tbb.addPoint(pp.current.x, pp.current.y);\r\n
\t\t\t\t\t\t\tif (ctx != null) ctx.lineTo(pp.current.x, pp.current.y);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase \'C\':\r\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\r\n
\t\t\t\t\t\t\tvar curr = pp.current;\r\n
\t\t\t\t\t\t\tvar p1 = pp.getPoint();\r\n
\t\t\t\t\t\t\tvar cntrl = pp.getAsControlPoint();\r\n
\t\t\t\t\t\t\tvar cp = pp.getAsCurrentPoint();\r\n
\t\t\t\t\t\t\tpp.addMarker(cp, cntrl, p1);\r\n
\t\t\t\t\t\t\tbb.addBezierCurve(curr.x, curr.y, p1.x, p1.y, cntrl.x, cntrl.y, cp.x, cp.y);\r\n
\t\t\t\t\t\t\tif (ctx != null) ctx.bezierCurveTo(p1.x, p1.y, cntrl.x, cntrl.y, cp.x, cp.y);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase \'S\':\r\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\r\n
\t\t\t\t\t\t\tvar curr = pp.current;\r\n
\t\t\t\t\t\t\tvar p1 = pp.getReflectedControlPoint();\r\n
\t\t\t\t\t\t\tvar cntrl = pp.getAsControlPoint();\r\n
\t\t\t\t\t\t\tvar cp = pp.getAsCurrentPoint();\r\n
\t\t\t\t\t\t\tpp.addMarker(cp, cntrl, p1);\r\n
\t\t\t\t\t\t\tbb.addBezierCurve(curr.x, curr.y, p1.x, p1.y, cntrl.x, cntrl.y, cp.x, cp.y);\r\n
\t\t\t\t\t\t\tif (ctx != null) ctx.bezierCurveTo(p1.x, p1.y, cntrl.x, cntrl.y, cp.x, cp.y);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase \'Q\':\r\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\r\n
\t\t\t\t\t\t\tvar curr = pp.current;\r\n
\t\t\t\t\t\t\tvar cntrl = pp.getAsControlPoint();\r\n
\t\t\t\t\t\t\tvar cp = pp.getAsCurrentPoint();\r\n
\t\t\t\t\t\t\tpp.addMarker(cp, cntrl, cntrl);\r\n
\t\t\t\t\t\t\tbb.addQuadraticCurve(curr.x, curr.y, cntrl.x, cntrl.y, cp.x, cp.y);\r\n
\t\t\t\t\t\t\tif (ctx != null) ctx.quadraticCurveTo(cntrl.x, cntrl.y, cp.x, cp.y);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase \'T\':\r\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\r\n
\t\t\t\t\t\t\tvar curr = pp.current;\r\n
\t\t\t\t\t\t\tvar cntrl = pp.getReflectedControlPoint();\r\n
\t\t\t\t\t\t\tpp.control = cntrl;\r\n
\t\t\t\t\t\t\tvar cp = pp.getAsCurrentPoint();\r\n
\t\t\t\t\t\t\tpp.addMarker(cp, cntrl, cntrl);\r\n
\t\t\t\t\t\t\tbb.addQuadraticCurve(curr.x, curr.y, cntrl.x, cntrl.y, cp.x, cp.y);\r\n
\t\t\t\t\t\t\tif (ctx != null) ctx.quadraticCurveTo(cntrl.x, cntrl.y, cp.x, cp.y);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase \'A\':\r\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\r\n
\t\t\t\t\t\t\tvar curr = pp.current;\r\n
\t\t\t\t\t\t\tvar rx = pp.getScalar();\r\n
\t\t\t\t\t\t\tvar ry = pp.getScalar();\r\n
\t\t\t\t\t\t\tvar xAxisRotation = pp.getScalar() * (Math.PI / 180.0);\r\n
\t\t\t\t\t\t\tvar largeArcFlag = pp.getScalar();\r\n
\t\t\t\t\t\t\tvar sweepFlag = pp.getScalar();\r\n
\t\t\t\t\t\t\tvar cp = pp.getAsCurrentPoint();\r\n
\r\n
\t\t\t\t\t\t\t// Conversion from endpoint to center parameterization\r\n
\t\t\t\t\t\t\t// http://www.w3.org/TR/SVG11/implnote.html#ArcImplementationNotes\r\n
\t\t\t\t\t\t\t// x1\', y1\'\r\n
\t\t\t\t\t\t\tvar currp = new svg.Point(\r\n
\t\t\t\t\t\t\t\tMath.cos(xAxisRotation) * (curr.x - cp.x) / 2.0 + Math.sin(xAxisRotation) * (curr.y - cp.y) / 2.0,\r\n
\t\t\t\t\t\t\t\t-Math.sin(xAxisRotation) * (curr.x - cp.x) / 2.0 + Math.cos(xAxisRotation) * (curr.y - cp.y) / 2.0\r\n
\t\t\t\t\t\t\t);\r\n
\t\t\t\t\t\t\t// adjust radii\r\n
\t\t\t\t\t\t\tvar l = Math.pow(currp.x,2)/Math.pow(rx,2)+Math.pow(currp.y,2)/Math.pow(ry,2);\r\n
\t\t\t\t\t\t\tif (l > 1) {\r\n
\t\t\t\t\t\t\t\trx *= Math.sqrt(l);\r\n
\t\t\t\t\t\t\t\try *= Math.sqrt(l);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t// cx\', cy\'\r\n
\t\t\t\t\t\t\tvar s = (largeArcFlag == sweepFlag ? -1 : 1) * Math.sqrt(\r\n
\t\t\t\t\t\t\t\t((Math.pow(rx,2)*Math.pow(ry,2))-(Math.pow(rx,2)*Math.pow(currp.y,2))-(Math.pow(ry,2)*Math.pow(currp.x,2))) /\r\n
\t\t\t\t\t\t\t\t(Math.pow(rx,2)*Math.pow(currp.y,2)+Math.pow(ry,2)*Math.pow(currp.x,2))\r\n
\t\t\t\t\t\t\t);\r\n
\t\t\t\t\t\t\tif (isNaN(s)) s = 0;\r\n
\t\t\t\t\t\t\tvar cpp = new svg.Point(s * rx * currp.y / ry, s * -ry * currp.x / rx);\r\n
\t\t\t\t\t\t\t// cx, cy\r\n
\t\t\t\t\t\t\tvar centp = new svg.Point(\r\n
\t\t\t\t\t\t\t\t(curr.x + cp.x) / 2.0 + Math.cos(xAxisRotation) * cpp.x - Math.sin(xAxisRotation) * cpp.y,\r\n
\t\t\t\t\t\t\t\t(curr.y + cp.y) / 2.0 + Math.sin(xAxisRotation) * cpp.x + Math.cos(xAxisRotation) * cpp.y\r\n
\t\t\t\t\t\t\t);\r\n
\t\t\t\t\t\t\t// vector magnitude\r\n
\t\t\t\t\t\t\tvar m = function(v) { return Math.sqrt(Math.pow(v[0],2) + Math.pow(v[1],2)); }\r\n
\t\t\t\t\t\t\t// ratio between two vectors\r\n
\t\t\t\t\t\t\tvar r = function(u, v) { return (u[0]*v[0]+u[1]*v[1]) / (m(u)*m(v)) }\r\n
\t\t\t\t\t\t\t// angle between two vectors\r\n
\t\t\t\t\t\t\tvar a = function(u, v) { return (u[0]*v[1] < u[1]*v[0] ? -1 : 1) * Math.acos(r(u,v)); }\r\n
\t\t\t\t\t\t\t// initial angle\r\n
\t\t\t\t\t\t\tvar a1 = a([1,0], [(currp.x-cpp.x)/rx,(currp.y-cpp.y)/ry]);\r\n
\t\t\t\t\t\t\t// angle delta\r\n
\t\t\t\t\t\t\tvar u = [(currp.x-cpp.x)/rx,(currp.y-cpp.y)/ry];\r\n
\t\t\t\t\t\t\tvar v = [(-currp.x-cpp.x)/rx,(-currp.y-cpp.y)/ry];\r\n
\t\t\t\t\t\t\tvar ad = a(u, v);\r\n
\t\t\t\t\t\t\tif (r(u,v) <= -1) ad = Math.PI;\r\n
\t\t\t\t\t\t\tif (r(u,v) >= 1) ad = 0;\r\n
\r\n
\t\t\t\t\t\t\tif (sweepFlag == 0 && ad > 0) ad = ad - 2 * Math.PI;\r\n
\t\t\t\t\t\t\tif (sweepFlag == 1 && ad < 0) ad = ad + 2 * Math.PI;\r\n
\r\n
\t\t\t\t\t\t\t// for markers\r\n
\t\t\t\t\t\t\tvar halfWay = new svg.Point(\r\n
\t\t\t\t\t\t\t\tcentp.x - rx * Math.cos((a1 + ad) / 2),\r\n
\t\t\t\t\t\t\t\tcentp.y - ry * Math.sin((a1 + ad) / 2)\r\n
\t\t\t\t\t\t\t);\r\n
\t\t\t\t\t\t\tpp.addMarkerAngle(halfWay, (a1 + ad) / 2 + (sweepFlag == 0 ? 1 : -1) * Math.PI / 2);\r\n
\t\t\t\t\t\t\tpp.addMarkerAngle(cp, ad + (sweepFlag == 0 ? 1 : -1) * Math.PI / 2);\r\n
\r\n
\t\t\t\t\t\t\tbb.addPoint(cp.x, cp.y); // TODO: this is too naive, make it better\r\n
\t\t\t\t\t\t\tif (ctx != null) {\r\n
\t\t\t\t\t\t\t\tvar r = rx > ry ? rx : ry;\r\n
\t\t\t\t\t\t\t\tvar sx = rx > ry ? 1 : rx / ry;\r\n
\t\t\t\t\t\t\t\tvar sy = rx > ry ? ry / rx : 1;\r\n
\r\n
\t\t\t\t\t\t\t\tctx.translate(centp.x, centp.y);\r\n
\t\t\t\t\t\t\t\tctx.rotate(xAxisRotation);\r\n
\t\t\t\t\t\t\t\tctx.scale(sx, sy);\r\n
\t\t\t\t\t\t\t\tctx.arc(0, 0, r, a1, a1 + ad, 1 - sweepFlag);\r\n
\t\t\t\t\t\t\t\tctx.scale(1/sx, 1/sy);\r\n
\t\t\t\t\t\t\t\tctx.rotate(-xAxisRotation);\r\n
\t\t\t\t\t\t\t\tctx.translate(-centp.x, -centp.y);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase \'Z\':\r\n
\t\t\t\t\t\tif (ctx != null) ctx.closePath();\r\n
\t\t\t\t\t\tpp.current = pp.start;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\treturn bb;\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.getMarkers = function() {\r\n
\t\t\t\tvar points = this.PathParser.getMarkerPoints();\r\n
\t\t\t\tvar angles = this.PathParser.getMarkerAngles();\r\n
\r\n
\t\t\t\tvar markers = [];\r\n
\t\t\t\tfor (var i=0; i<points.length; i++) {\r\n
\t\t\t\t\tmarkers.push([points[i], angles[i]]);\r\n
\t\t\t\t}\r\n
\t\t\t\treturn markers;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.path.prototype = new svg.Element.PathElementBase;\r\n
\r\n
\t\t// pattern element\r\n
\t\tsvg.Element.pattern = function(node) {\r\n
\t\t\tthis.base = svg.Element.ElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.createPattern = function(ctx, element) {\r\n
\t\t\t\t// render me using a temporary svg element\r\n
\t\t\t\tvar tempSvg = new svg.Element.svg();\r\n
\t\t\t\ttempSvg.attributes[\'viewBox\'] = new svg.Property(\'viewBox\', this.attribute(\'viewBox\').value);\r\n
\t\t\t\ttempSvg.attributes[\'x\'] = new svg.Property(\'x\', this.attribute(\'x\').value);\r\n
\t\t\t\ttempSvg.attributes[\'y\'] = new svg.Property(\'y\', this.attribute(\'y\').value);\r\n
\t\t\t\ttempSvg.attributes[\'width\'] = new svg.Property(\'width\', this.attribute(\'width\').value);\r\n
\t\t\t\ttempSvg.attributes[\'height\'] = new svg.Property(\'height\', this.attribute(\'height\').value);\r\n
\t\t\t\ttempSvg.children = this.children;\r\n
\r\n
\t\t\t\tvar c = document.createElement(\'canvas\');\r\n
\t\t\t\tc.width = this.attribute(\'width\').Length.toPixels(\'x\');\r\n
\t\t\t\tc.height = this.attribute(\'height\').Length.toPixels(\'y\');\r\n
\t\t\t\ttempSvg.render(c.getContext(\'2d\'));\r\n
\t\t\t\treturn ctx.createPattern(c, \'repeat\');\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.pattern.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\t// marker element\r\n
\t\tsvg.Element.marker = function(node) {\r\n
\t\t\tthis.base = svg.Element.ElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.baseRender = this.render;\r\n
\t\t\tthis.render = function(ctx, point, angle) {\r\n
\t\t\t\tctx.translate(point.x, point.y);\r\n
\t\t\t\tif (this.attribute(\'orient\').valueOrDefault(\'auto\') == \'auto\') ctx.rotate(angle);\r\n
\t\t\t\tif (this.attribute(\'markerUnits\').valueOrDefault(\'strokeWidth\') == \'strokeWidth\') ctx.scale(ctx.lineWidth, ctx.lineWidth);\r\n
\t\t\t\tctx.save();\r\n
\r\n
\t\t\t\t// render me using a temporary svg element\r\n
\t\t\t\tvar tempSvg = new svg.Element.svg();\r\n
\t\t\t\ttempSvg.attributes[\'viewBox\'] = new svg.Property(\'viewBox\', this.attribute(\'viewBox\').value);\r\n
\t\t\t\ttempSvg.attributes[\'refX\'] = new svg.Property(\'refX\', this.attribute(\'refX\').value);\r\n
\t\t\t\ttempSvg.attributes[\'refY\'] = new svg.Property(\'refY\', this.attribute(\'refY\').value);\r\n
\t\t\t\ttempSvg.attributes[\'width\'] = new svg.Property(\'width\', this.attribute(\'markerWidth\').value);\r\n
\t\t\t\ttempSvg.attributes[\'height\'] = new svg.Property(\'height\', this.attribute(\'markerHeight\').value);\r\n
\t\t\t\ttempSvg.attributes[\'fill\'] = new svg.Property(\'fill\', this.attribute(\'fill\').valueOrDefault(\'black\'));\r\n
\t\t\t\ttempSvg.attributes[\'stroke\'] = new svg.Property(\'stroke\', this.attribute(\'stroke\').valueOrDefault(\'none\'));\r\n
\t\t\t\ttempSvg.children = this.children;\r\n
\t\t\t\ttempSvg.render(ctx);\r\n
\r\n
\t\t\t\tctx.restore();\r\n
\t\t\t\tif (this.attribute(\'markerUnits\').valueOrDefault(\'strokeWidth\') == \'strokeWidth\') ctx.scale(1/ctx.lineWidth, 1/ctx.lineWidth);\r\n
\t\t\t\tif (this.attribute(\'orient\').valueOrDefault(\'auto\') == \'auto\') ctx.rotate(-angle);\r\n
\t\t\t\tctx.translate(-point.x, -point.y);\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.marker.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\t// definitions element\r\n
\t\tsvg.Element.defs = function(node) {\r\n
\t\t\tthis.base = svg.Element.ElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.render = function(ctx) {\r\n
\t\t\t\t// NOOP\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.defs.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\t// base for gradients\r\n
\t\tsvg.Element.GradientBase = function(node) {\r\n
\t\t\tthis.base = svg.Element.ElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.gradientUnits = this.attribute(\'gradientUnits\').valueOrDefault(\'objectBoundingBox\');\r\n
\r\n
\t\t\tthis.stops = [];\r\n
\t\t\tfor (var i=0; i<this.children.length; i++) {\r\n
\t\t\t\tvar child = this.children[i];\r\n
\t\t\t\tthis.stops.push(child);\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.getGradient = function() {\r\n
\t\t\t\t// OVERRIDE ME!\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.createGradient = function(ctx, element) {\r\n
\t\t\t\tvar stopsContainer = this;\r\n
\t\t\t\tif (this.attribute(\'xlink:href\').hasValue()) {\r\n
\t\t\t\t\tstopsContainer = this.attribute(\'xlink:href\').Definition.getDefinition();\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tvar g = this.getGradient(ctx, element);\r\n
\t\t\t\tfor (var i=0; i<stopsContainer.stops.length; i++) {\r\n
\t\t\t\t\tg.addColorStop(stopsContainer.stops[i].offset, stopsContainer.stops[i].color);\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tif (this.attribute(\'gradientTransform\').hasValue()) {\r\n
\t\t\t\t\t// render as transformed pattern on temporary canvas\r\n
\t\t\t\t\tvar rootView = svg.ViewPort.viewPorts[0];\r\n
\r\n
\t\t\t\t\tvar rect = new svg.Element.rect();\r\n
\t\t\t\t\trect.attributes[\'x\'] = new svg.Property(\'x\', -svg.MAX_VIRTUAL_PIXELS/3.0);\r\n
\t\t\t\t\trect.attributes[\'y\'] = new svg.Property(\'y\', -svg.MAX_VIRTUAL_PIXELS/3.0);\r\n
\t\t\t\t\trect.attributes[\'width\'] = new svg.Property(\'width\', svg.MAX_VIRTUAL_PIXELS);\r\n
\t\t\t\t\trect.attributes[\'height\'] = new svg.Property(\'height\', svg.MAX_VIRTUAL_PIXELS);\r\n
\r\n
\t\t\t\t\tvar group = new svg.Element.g();\r\n
\t\t\t\t\tgroup.attributes[\'transform\'] = new svg.Property(\'transform\', this.attribute(\'gradientTransform\').value);\r\n
\t\t\t\t\tgroup.children = [ rect ];\r\n
\r\n
\t\t\t\t\tvar tempSvg = new svg.Element.svg();\r\n
\t\t\t\t\ttempSvg.attributes[\'x\'] = new svg.Property(\'x\', 0);\r\n
\t\t\t\t\ttempSvg.attributes[\'y\'] = new svg.Property(\'y\', 0);\r\n
\t\t\t\t\ttempSvg.attributes[\'width\'] = new svg.Property(\'width\', rootView.width);\r\n
\t\t\t\t\ttempSvg.attributes[\'height\'] = new svg.Property(\'height\', rootView.height);\r\n
\t\t\t\t\ttempSvg.children = [ group ];\r\n
\r\n
\t\t\t\t\tvar c = document.createElement(\'canvas\');\r\n
\t\t\t\t\tc.width = rootView.width;\r\n
\t\t\t\t\tc.height = rootView.height;\r\n
\t\t\t\t\tvar tempCtx = c.getContext(\'2d\');\r\n
\t\t\t\t\ttempCtx.fillStyle = g;\r\n
\t\t\t\t\ttempSvg.render(tempCtx);\r\n
\t\t\t\t\treturn tempCtx.createPattern(c, \'no-repeat\');\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\treturn g;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.GradientBase.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\t// linear gradient element\r\n
\t\tsvg.Element.linearGradient = function(node) {\r\n
\t\t\tthis.base = svg.Element.GradientBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.getGradient = function(ctx, element) {\r\n
\t\t\t\tvar bb = element.getBoundingBox();\r\n
\r\n
\t\t\t\tvar x1 = (this.gradientUnits == \'objectBoundingBox\'\r\n
\t\t\t\t\t? bb.x() + bb.width() * this.attribute(\'x1\').numValue()\r\n
\t\t\t\t\t: this.attribute(\'x1\').Length.toPixels(\'x\'));\r\n
\t\t\t\tvar y1 = (this.gradientUnits == \'objectBoundingBox\'\r\n
\t\t\t\t\t? bb.y() + bb.height() * this.attribute(\'y1\').numValue()\r\n
\t\t\t\t\t: this.attribute(\'y1\').Length.toPixels(\'y\'));\r\n
\t\t\t\tvar x2 = (this.gradientUnits == \'objectBoundingBox\'\r\n
\t\t\t\t\t? bb.x() + bb.width() * this.attribute(\'x2\').numValue()\r\n
\t\t\t\t\t: this.attribute(\'x2\').Length.toPixels(\'x\'));\r\n
\t\t\t\tvar y2 = (this.gradientUnits == \'objectBoundingBox\'\r\n
\t\t\t\t\t? bb.y() + bb.height() * this.attribute(\'y2\').numValue()\r\n
\t\t\t\t\t: this.attribute(\'y2\').Length.toPixels(\'y\'));\r\n
\r\n
\t\t\t\treturn ctx.createLinearGradient(x1, y1, x2, y2);\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.linearGradient.prototype = new svg.Element.GradientBase;\r\n
\r\n
\t\t// radial gradient element\r\n
\t\tsvg.Element.radialGradient = function(node) {\r\n
\t\t\tthis.base = svg.Element.GradientBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.getGradient = function(ctx, element) {\r\n
\t\t\t\tvar bb = element.getBoundingBox();\r\n
\r\n
\t\t\t\tvar cx = (this.gradientUnits == \'objectBoundingBox\'\r\n
\t\t\t\t\t? bb.x() + bb.width() * this.attribute(\'cx\').numValue()\r\n
\t\t\t\t\t: this.attribute(\'cx\').Length.toPixels(\'x\'));\r\n
\t\t\t\tvar cy = (this.gradientUnits == \'objectBoundingBox\'\r\n
\t\t\t\t\t? bb.y() + bb.height() * this.attribute(\'cy\').numValue()\r\n
\t\t\t\t\t: this.attribute(\'cy\').Length.toPixels(\'y\'));\r\n
\r\n
\t\t\t\tvar fx = cx;\r\n
\t\t\t\tvar fy = cy;\r\n
\t\t\t\tif (this.attribute(\'fx\').hasValue()) {\r\n
\t\t\t\t\tfx = (this.gradientUnits == \'objectBoundingBox\'\r\n
\t\t\t\t\t? bb.x() + bb.width() * this.attribute(\'fx\').numValue()\r\n
\t\t\t\t\t: this.attribute(\'fx\').Length.toPixels(\'x\'));\r\n
\t\t\t\t}\r\n
\t\t\t\tif (this.attribute(\'fy\').hasValue()) {\r\n
\t\t\t\t\tfy = (this.gradientUnits == \'objectBoundingBox\'\r\n
\t\t\t\t\t? bb.y() + bb.height() * this.attribute(\'fy\').numValue()\r\n
\t\t\t\t\t: this.attribute(\'fy\').Length.toPixels(\'y\'));\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tvar r = (this.gradientUnits == \'objectBoundingBox\'\r\n
\t\t\t\t\t? (bb.width() + bb.height()) / 2.0 * this.attribute(\'r\').numValue()\r\n
\t\t\t\t\t: this.attribute(\'r\').Length.toPixels());\r\n
\r\n
\t\t\t\treturn ctx.createRadialGradient(fx, fy, 0, cx, cy, r);\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.radialGradient.prototype = new svg.Element.GradientBase;\r\n
\r\n
\t\t// gradient stop element\r\n
\t\tsvg.Element.stop = function(node) {\r\n
\t\t\tthis.base = svg.Element.ElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.offset = this.attribute(\'offset\').numValue();\r\n
\r\n
\t\t\tvar stopColor = this.style(\'stop-color\');\r\n
\t\t\tif (this.style(\'stop-opacity\').hasValue()) stopColor = stopColor.Color.addOpacity(this.style(\'stop-opacity\').value);\r\n
\t\t\tthis.color = stopColor.value;\r\n
\t\t}\r\n
\t\tsvg.Element.stop.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\t// animation base element\r\n
\t\tsvg.Element.AnimateBase = function(node) {\r\n
\t\t\tthis.base = svg.Element.ElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tsvg.Animations.push(this);\r\n
\r\n
\t\t\tthis.duration = 0.0;\r\n
\t\t\tthis.begin = this.attribute(\'begin\').Time.toMilliseconds();\r\n
\t\t\tthis.maxDuration = this.begin + this.attribute(\'dur\').Time.toMilliseconds();\r\n
\r\n
\t\t\tthis.getProperty = function() {\r\n
\t\t\t\tvar attributeType = this.attribute(\'attributeType\').value;\r\n
\t\t\t\tvar attributeName = this.attribute(\'attributeName\').value;\r\n
\r\n
\t\t\t\tif (attributeType == \'CSS\') {\r\n
\t\t\t\t\treturn this.parent.style(attributeName, true);\r\n
\t\t\t\t}\r\n
\t\t\t\treturn this.parent.attribute(attributeName, true);\r\n
\t\t\t};\r\n
\r\n
\t\t\tthis.initialValue = null;\r\n
\t\t\tthis.removed = false;\r\n
\r\n
\t\t\tthis.calcValue = function() {\r\n
\t\t\t\t// OVERRIDE ME!\r\n
\t\t\t\treturn \'\';\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.update = function(delta) {\r\n
\t\t\t\t// set initial value\r\n
\t\t\t\tif (this.initialValue == null) {\r\n
\t\t\t\t\tthis.initialValue = this.getProperty().value;\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// if we\'re past the end time\r\n
\t\t\t\tif (this.duration > this.maxDuration) {\r\n
\t\t\t\t\t// loop for indefinitely repeating animations\r\n
\t\t\t\t\tif (this.attribute(\'repeatCount\').value == \'indefinite\') {\r\n
\t\t\t\t\t\tthis.duration = 0.0\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\telse if (this.attribute(\'fill\').valueOrDefault(\'remove\') == \'remove\' && !this.removed) {\r\n
\t\t\t\t\t\tthis.removed = true;\r\n
\t\t\t\t\t\tthis.getProperty().value = this.initialValue;\r\n
\t\t\t\t\t\treturn true;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\telse {\r\n
\t\t\t\t\t\treturn false; // no updates made\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tthis.duration = this.duration + delta;\r\n
\r\n
\t\t\t\t// if we\'re past the begin time\r\n
\t\t\t\tvar updated = false;\r\n
\t\t\t\tif (this.begin < this.duration) {\r\n
\t\t\t\t\tvar newValue = this.calcValue(); // tween\r\n
\r\n
\t\t\t\t\tif (this.attribute(\'type\').hasValue()) {\r\n
\t\t\t\t\t\t// for transform, etc.\r\n
\t\t\t\t\t\tvar type = this.attribute(\'type\').value;\r\n
\t\t\t\t\t\tnewValue = type + \'(\' + newValue + \')\';\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\tthis.getProperty().value = newValue;\r\n
\t\t\t\t\tupdated = true;\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\treturn updated;\r\n
\t\t\t}\r\n
\r\n
\t\t\t// fraction of duration we\'ve covered\r\n
\t\t\tthis.progress = function() {\r\n
\t\t\t\treturn ((this.duration - this.begin) / (this.maxDuration - this.begin));\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.AnimateBase.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\t// animate element\r\n
\t\tsvg.Element.animate = function(node) {\r\n
\t\t\tthis.base = svg.Element.AnimateBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.calcValue = function() {\r\n
\t\t\t\tvar from = this.attribute(\'from\').numValue();\r\n
\t\t\t\tvar to = this.attribute(\'to\').numValue();\r\n
\r\n
\t\t\t\t// tween value linearly\r\n
\t\t\t\treturn from + (to - from) * this.progress();\r\n
\t\t\t};\r\n
\t\t}\r\n
\t\tsvg.Element.animate.prototype = new svg.Element.AnimateBase;\r\n
\r\n
\t\t// animate color element\r\n
\t\tsvg.Element.animateColor = function(node) {\r\n
\t\t\tthis.base = svg.Element.AnimateBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.calcValue = function() {\r\n
\t\t\t\tvar from = new RGBColor(this.attribute(\'from\').value);\r\n
\t\t\t\tvar to = new RGBColor(this.attribute(\'to\').value);\r\n
\r\n
\t\t\t\tif (from.ok && to.ok) {\r\n
\t\t\t\t\t// tween color linearly\r\n
\t\t\t\t\tvar r = from.r + (to.r - from.r) * this.progress();\r\n
\t\t\t\t\tvar g = from.g + (to.g - from.g) * this.progress();\r\n
\t\t\t\t\tvar b = from.b + (to.b - from.b) * this.progress();\r\n
\t\t\t\t\treturn \'rgb(\'+parseInt(r,10)+\',\'+parseInt(g,10)+\',\'+parseInt(b,10)+\')\';\r\n
\t\t\t\t}\r\n
\t\t\t\treturn this.attribute(\'from\').value;\r\n
\t\t\t};\r\n
\t\t}\r\n
\t\tsvg.Element.animateColor.prototype = new svg.Element.AnimateBase;\r\n
\r\n
\t\t// animate transform element\r\n
\t\tsvg.Element.animateTransform = function(node) {\r\n
\t\t\tthis.base = svg.Element.animate;\r\n
\t\t\tthis.base(node);\r\n
\t\t}\r\n
\t\tsvg.Element.animateTransform.prototype = new svg.Element.animate;\r\n
\r\n
\t\t// font element\r\n
\t\tsvg.Element.font = function(node) {\r\n
\t\t\tthis.base = svg.Element.ElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.horizAdvX = this.attribute(\'horiz-adv-x\').numValue();\r\n
\r\n
\t\t\tthis.isRTL = false;\r\n
\t\t\tthis.isArabic = false;\r\n
\t\t\tthis.fontFace = null;\r\n
\t\t\tthis.missingGlyph = null;\r\n
\t\t\tthis.glyphs = [];\r\n
\t\t\tfor (var i=0; i<this.children.length; i++) {\r\n
\t\t\t\tvar child = this.children[i];\r\n
\t\t\t\tif (child.type == \'font-face\') {\r\n
\t\t\t\t\tthis.fontFace = child;\r\n
\t\t\t\t\tif (child.style(\'font-family\').hasValue()) {\r\n
\t\t\t\t\t\tsvg.Definitions[child.style(\'font-family\').value] = this;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\telse if (child.type == \'missing-glyph\') this.missingGlyph = child;\r\n
\t\t\t\telse if (child.type == \'glyph\') {\r\n
\t\t\t\t\tif (child.arabicForm != \'\') {\r\n
\t\t\t\t\t\tthis.isRTL = true;\r\n
\t\t\t\t\t\tthis.isArabic = true;\r\n
\t\t\t\t\t\tif (typeof(this.glyphs[child.unicode]) == \'undefined\') this.glyphs[child.unicode] = [];\r\n
\t\t\t\t\t\tthis.glyphs[child.unicode][child.arabicForm] = child;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\telse {\r\n
\t\t\t\t\t\tthis.glyphs[child.unicode] = child;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.font.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\t// font-face element\r\n
\t\tsvg.Element.fontface = function(node) {\r\n
\t\t\tthis.base = svg.Element.ElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.ascent = this.attribute(\'ascent\').value;\r\n
\t\t\tthis.descent = this.attribute(\'descent\').value;\r\n
\t\t\tthis.unitsPerEm = this.attribute(\'units-per-em\').numValue();\r\n
\t\t}\r\n
\t\tsvg.Element.fontface.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\t// missing-glyph element\r\n
\t\tsvg.Element.missingglyph = function(node) {\r\n
\t\t\tthis.base = svg.Element.path;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.horizAdvX = 0;\r\n
\t\t}\r\n
\t\tsvg.Element.missingglyph.prototype = new svg.Element.path;\r\n
\r\n
\t\t// glyph element\r\n
\t\tsvg.Element.glyph = function(node) {\r\n
\t\t\tthis.base = svg.Element.path;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.horizAdvX = this.attribute(\'horiz-adv-x\').numValue();\r\n
\t\t\tthis.unicode = this.attribute(\'unicode\').value;\r\n
\t\t\tthis.arabicForm = this.attribute(\'arabic-form\').value;\r\n
\t\t}\r\n
\t\tsvg.Element.glyph.prototype = new svg.Element.path;\r\n
\r\n
\t\t// text element\r\n
\t\tsvg.Element.text = function(node) {\r\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tif (node != null) {\r\n
\t\t\t\t// add children\r\n
\t\t\t\tthis.children = [];\r\n
\t\t\t\tfor (var i=0; i<node.childNodes.length; i++) {\r\n
\t\t\t\t\tvar childNode = node.childNodes[i];\r\n
\t\t\t\t\tif (childNode.nodeType == 1) { // capture tspan and tref nodes\r\n
\t\t\t\t\t\tthis.addChild(childNode, true);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\telse if (childNode.nodeType == 3) { // capture text\r\n
\t\t\t\t\t\tthis.addChild(new svg.Element.tspan(childNode), false);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.baseSetContext = this.setContext;\r\n
\t\t\tthis.setContext = function(ctx) {\r\n
\t\t\t\tthis.baseSetContext(ctx);\r\n
\t\t\t\tif (this.style(\'dominant-baseline\').hasValue()) ctx.textBaseline = this.style(\'dominant-baseline\').value;\r\n
\t\t\t\tif (this.style(\'alignment-baseline\').hasValue()) ctx.textBaseline = this.style(\'alignment-baseline\').value;\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.renderChildren = function(ctx) {\r\n
\t\t\t\tvar textAnchor = this.style(\'text-anchor\').valueOrDefault(\'start\');\r\n
\t\t\t\tvar x = this.attribute(\'x\').Length.toPixels(\'x\');\r\n
\t\t\t\tvar y = this.attribute(\'y\').Length.toPixels(\'y\');\r\n
\t\t\t\tfor (var i=0; i<this.children.length; i++) {\r\n
\t\t\t\t\tvar child = this.children[i];\r\n
\r\n
\t\t\t\t\tif (child.attribute(\'x\').hasValue()) {\r\n
\t\t\t\t\t\tchild.x = child.attribute(\'x\').Length.toPixels(\'x\');\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\telse {\r\n
\t\t\t\t\t\tif (child.attribute(\'dx\').hasValue()) x += child.attribute(\'dx\').Length.toPixels(\'x\');\r\n
\t\t\t\t\t\tchild.x = x;\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\tvar childLength = child.measureText(ctx);\r\n
\t\t\t\t\tif (textAnchor != \'start\' && (i==0 || child.attribute(\'x\').hasValue())) { // new group?\r\n
\t\t\t\t\t\t// loop through rest of children\r\n
\t\t\t\t\t\tvar groupLength = childLength;\r\n
\t\t\t\t\t\tfor (var j=i+1; j<this.children.length; j++) {\r\n
\t\t\t\t\t\t\tvar childInGroup = this.children[j];\r\n
\t\t\t\t\t\t\tif (childInGroup.attribute(\'x\').hasValue()) break; // new group\r\n
\t\t\t\t\t\t\tgroupLength += childInGroup.measureText(ctx);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tchild.x -= (textAnchor == \'end\' ? groupLength : groupLength / 2.0);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tx = child.x + childLength;\r\n
\r\n
\t\t\t\t\tif (child.attribute(\'y\').hasValue()) {\r\n
\t\t\t\t\t\tchild.y = child.attribute(\'y\').Length.toPixels(\'y\');\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\telse {\r\n
\t\t\t\t\t\tif (child.attribute(\'dy\').hasValue()) y += child.attribute(\'dy\').Length.toPixels(\'y\');\r\n
\t\t\t\t\t\tchild.y = y;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\ty = child.y;\r\n
\r\n
\t\t\t\t\tchild.render(ctx);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.text.prototype = new svg.Element.RenderedElementBase;\r\n
\r\n
\t\t// text base\r\n
\t\tsvg.Element.TextElementBase = function(node) {\r\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.getGlyph = function(font, text, i) {\r\n
\t\t\t\tvar c = text[i];\r\n
\t\t\t\tvar glyph = null;\r\n
\t\t\t\tif (font.isArabic) {\r\n
\t\t\t\t\tvar arabicForm = \'isolated\';\r\n
\t\t\t\t\tif ((i==0 || text[i-1]==\' \') && i<text.length-2 && text[i+1]!=\' \') arabicForm = \'terminal\';\r\n
\t\t\t\t\tif (i>0 && text[i-1]!=\' \' && i<text.length-2 && text[i+1]!=\' \') arabicForm = \'medial\';\r\n
\t\t\t\t\tif (i>0 && text[i-1]!=\' \' && (i == text.length-1 || text[i+1]==\' \')) arabicForm = \'initial\';\r\n
\t\t\t\t\tif (typeof(font.glyphs[c]) != \'undefined\') {\r\n
\t\t\t\t\t\tglyph = font.glyphs[c][arabicForm];\r\n
\t\t\t\t\t\tif (glyph == null && font.glyphs[c].type == \'glyph\') glyph = font.glyphs[c];\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\telse {\r\n
\t\t\t\t\tglyph = font.glyphs[c];\r\n
\t\t\t\t}\r\n
\t\t\t\tif (glyph == null) glyph = font.missingGlyph;\r\n
\t\t\t\treturn glyph;\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.renderChildren = function(ctx) {\r\n
\t\t\t\tvar customFont = this.parent.style(\'font-family\').Definition.getDefinition();\r\n
\t\t\t\tif (customFont != null) {\r\n
\t\t\t\t\tvar fontSize = this.parent.style(\'font-size\').numValueOrDefault(svg.Font.Parse(svg.ctx.font).fontSize);\r\n
\t\t\t\t\tvar fontStyle = this.parent.style(\'font-style\').valueOrDefault(svg.Font.Parse(svg.ctx.font).fontStyle);\r\n
\t\t\t\t\tvar text = this.getText();\r\n
\t\t\t\t\tif (customFont.isRTL) text = text.split("").reverse().join("");\r\n
\r\n
\t\t\t\t\tvar dx = svg.ToNumberArray(this.parent.attribute(\'dx\').value);\r\n
\t\t\t\t\tfor (var i=0; i<text.length; i++) {\r\n
\t\t\t\t\t\tvar glyph = this.getGlyph(customFont, text, i);\r\n
\t\t\t\t\t\tvar scale = fontSize / customFont.fontFace.unitsPerEm;\r\n
\t\t\t\t\t\tctx.translate(this.x, this.y);\r\n
\t\t\t\t\t\tctx.scale(scale, -scale);\r\n
\t\t\t\t\t\tvar lw = ctx.lineWidth;\r\n
\t\t\t\t\t\tctx.lineWidth = ctx.lineWidth * customFont.fontFace.unitsPerEm / fontSize;\r\n
\t\t\t\t\t\tif (fontStyle == \'italic\') ctx.transform(1, 0, .4, 1, 0, 0);\r\n
\t\t\t\t\t\tglyph.render(ctx);\r\n
\t\t\t\t\t\tif (fontStyle == \'italic\') ctx.transform(1, 0, -.4, 1, 0, 0);\r\n
\t\t\t\t\t\tctx.lineWidth = lw;\r\n
\t\t\t\t\t\tctx.scale(1/scale, -1/scale);\r\n
\t\t\t\t\t\tctx.translate(-this.x, -this.y);\r\n
\r\n
\t\t\t\t\t\tthis.x += fontSize * (glyph.horizAdvX || customFont.horizAdvX) / customFont.fontFace.unitsPerEm;\r\n
\t\t\t\t\t\tif (typeof(dx[i]) != \'undefined\' && !isNaN(dx[i])) {\r\n
\t\t\t\t\t\t\tthis.x += dx[i];\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn;\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tif (ctx.strokeStyle != \'\') ctx.strokeText(svg.compressSpaces(this.getText()), this.x, this.y);\r\n
\t\t\t\tif (ctx.fillStyle != \'\') ctx.fillText(svg.compressSpaces(this.getText()), this.x, this.y);\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.getText = function() {\r\n
\t\t\t\t// OVERRIDE ME\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.measureText = function(ctx) {\r\n
\t\t\t\tvar customFont = this.parent.style(\'font-family\').Definition.getDefinition();\r\n
\t\t\t\tif (customFont != null) {\r\n
\t\t\t\t\tvar fontSize = this.parent.style(\'font-size\').numValueOrDefault(svg.Font.Parse(svg.ctx.font).fontSize);\r\n
\t\t\t\t\tvar measure = 0;\r\n
\t\t\t\t\tvar text = this.getText();\r\n
\t\t\t\t\tif (customFont.isRTL) text = text.split("").reverse().join("");\r\n
\t\t\t\t\tvar dx = svg.ToNumberArray(this.parent.attribute(\'dx\').value);\r\n
\t\t\t\t\tfor (var i=0; i<text.length; i++) {\r\n
\t\t\t\t\t\tvar glyph = this.getGlyph(customFont, text, i);\r\n
\t\t\t\t\t\tmeasure += (glyph.horizAdvX || customFont.horizAdvX) * fontSize / customFont.fontFace.unitsPerEm;\r\n
\t\t\t\t\t\tif (typeof(dx[i]) != \'undefined\' && !isNaN(dx[i])) {\r\n
\t\t\t\t\t\t\tmeasure += dx[i];\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn measure;\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tvar textToMeasure = svg.compressSpaces(this.getText());\r\n
\t\t\t\tif (!ctx.measureText) return textToMeasure.length * 10;\r\n
\r\n
\t\t\t\tctx.save();\r\n
\t\t\t\tthis.setContext(ctx);\r\n
\t\t\t\tvar width = ctx.measureText(textToMeasure).width;\r\n
\t\t\t\tctx.restore();\r\n
\t\t\t\treturn width;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.TextElementBase.prototype = new svg.Element.RenderedElementBase;\r\n
\r\n
\t\t// tspan\r\n
\t\tsvg.Element.tspan = function(node) {\r\n
\t\t\tthis.base = svg.Element.TextElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.text = node.nodeType == 3 ? node.nodeValue : // text\r\n
\t\t\t\t\t\tnode.childNodes.length > 0 ? node.childNodes[0].nodeValue : // element\r\n
\t\t\t\t\t\tnode.text;\r\n
\t\t\tthis.getText = function() {\r\n
\t\t\t\treturn this.text;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.tspan.prototype = new svg.Element.TextElementBase;\r\n
\r\n
\t\t// tref\r\n
\t\tsvg.Element.tref = function(node) {\r\n
\t\t\tthis.base = svg.Element.TextElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.getText = function() {\r\n
\t\t\t\tvar element = this.attribute(\'xlink:href\').Definition.getDefinition();\r\n
\t\t\t\tif (element != null) return element.children[0].getText();\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.tref.prototype = new svg.Element.TextElementBase;\r\n
\r\n
\t\t// a element\r\n
\t\tsvg.Element.a = function(node) {\r\n
\t\t\tthis.base = svg.Element.TextElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.hasText = true;\r\n
\t\t\tfor (var i=0; i<node.childNodes.length; i++) {\r\n
\t\t\t\tif (node.childNodes[i].nodeType != 3) this.hasText = false;\r\n
\t\t\t}\r\n
\r\n
\t\t\t// this might contain text\r\n
\t\t\tthis.text = this.hasText ? node.childNodes[0].nodeValue : \'\';\r\n
\t\t\tthis.getText = function() {\r\n
\t\t\t\treturn this.text;\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.baseRenderChildren = this.renderChildren;\r\n
\t\t\tthis.renderChildren = function(ctx) {\r\n
\t\t\t\tif (this.hasText) {\r\n
\t\t\t\t\t// render as text element\r\n
\t\t\t\t\tthis.baseRenderChildren(ctx);\r\n
\t\t\t\t\tvar fontSize = new svg.Property(\'fontSize\', svg.Font.Parse(svg.ctx.font).fontSize);\r\n
\t\t\t\t\tsvg.Mouse.checkBoundingBox(this, new svg.BoundingBox(this.x, this.y - fontSize.Length.toPixels(\'y\'), this.x + this.measureText(ctx), this.y));\r\n
\t\t\t\t}\r\n
\t\t\t\telse {\r\n
\t\t\t\t\t// render as temporary group\r\n
\t\t\t\t\tvar g = new svg.Element.g();\r\n
\t\t\t\t\tg.children = this.children;\r\n
\t\t\t\t\tg.parent = this;\r\n
\t\t\t\t\tg.render(ctx);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.onclick = function() {\r\n
\t\t\t\twindow.open(this.attribute(\'xlink:href\').value);\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.onmousemove = function() {\r\n
\t\t\t\tsvg.ctx.canvas.style.cursor = \'pointer\';\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.a.prototype = new svg.Element.TextElementBase;\r\n
\r\n
\t\t// image element\r\n
\t\tsvg.Element.image = function(node) {\r\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tsvg.Images.push(this);\r\n
\t\t\tthis.img = document.createElement(\'img\');\r\n
\t\t\tthis.loaded = false;\r\n
\t\t\tvar that = this;\r\n
\t\t\tthis.img.onload = function() { that.loaded = true; }\r\n
\t\t\tthis.img.src = this.attribute(\'xlink:href\').value;\r\n
\r\n
\t\t\tthis.renderChildren = function(ctx) {\r\n
\t\t\t\tvar x = this.attribute(\'x\').Length.toPixels(\'x\');\r\n
\t\t\t\tvar y = this.attribute(\'y\').Length.toPixels(\'y\');\r\n
\r\n
\t\t\t\tvar width = this.attribute(\'width\').Length.toPixels(\'x\');\r\n
\t\t\t\tvar height = this.attribute(\'height\').Length.toPixels(\'y\');\r\n
\t\t\t\tif (width == 0 || height == 0) return;\r\n
\r\n
\t\t\t\tctx.save();\r\n
\t\t\t\tctx.translate(x, y);\r\n
\t\t\t\tsvg.AspectRatio(ctx,\r\n
\t\t\t\t\t\t\t\tthis.attribute(\'preserveAspectRatio\').value,\r\n
\t\t\t\t\t\t\t\twidth,\r\n
\t\t\t\t\t\t\t\tthis.img.width,\r\n
\t\t\t\t\t\t\t\theight,\r\n
\t\t\t\t\t\t\t\tthis.img.height,\r\n
\t\t\t\t\t\t\t\t0,\r\n
\t\t\t\t\t\t\t\t0);\r\n
\t\t\t\tctx.drawImage(this.img, 0, 0);\r\n
\t\t\t\tctx.restore();\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.image.prototype = new svg.Element.RenderedElementBase;\r\n
\r\n
\t\t// group element\r\n
\t\tsvg.Element.g = function(node) {\r\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.getBoundingBox = function() {\r\n
\t\t\t\tvar bb = new svg.BoundingBox();\r\n
\t\t\t\tfor (var i=0; i<this.children.length; i++) {\r\n
\t\t\t\t\tbb.addBoundingBox(this.children[i].getBoundingBox());\r\n
\t\t\t\t}\r\n
\t\t\t\treturn bb;\r\n
\t\t\t};\r\n
\t\t}\r\n
\t\tsvg.Element.g.prototype = new svg.Element.RenderedElementBase;\r\n
\r\n
\t\t// symbol element\r\n
\t\tsvg.Element.symbol = function(node) {\r\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.baseSetContext = this.setContext;\r\n
\t\t\tthis.setContext = function(ctx) {\r\n
\t\t\t\tthis.baseSetContext(ctx);\r\n
\r\n
\t\t\t\t// viewbox\r\n
\t\t\t\tif (this.attribute(\'viewBox\').hasValue()) {\r\n
\t\t\t\t\tvar viewBox = svg.ToNumberArray(this.attribute(\'viewBox\').value);\r\n
\t\t\t\t\tvar minX = viewBox[0];\r\n
\t\t\t\t\tvar minY = viewBox[1];\r\n
\t\t\t\t\twidth = viewBox[2];\r\n
\t\t\t\t\theight = viewBox[3];\r\n
\r\n
\t\t\t\t\tsvg.AspectRatio(ctx,\r\n
\t\t\t\t\t\t\t\t\tthis.attribute(\'preserveAspectRatio\').value,\r\n
\t\t\t\t\t\t\t\t\tthis.attribute(\'width\').Length.toPixels(\'x\'),\r\n
\t\t\t\t\t\t\t\t\twidth,\r\n
\t\t\t\t\t\t\t\t\tthis.attribute(\'height\').Length.toPixels(\'y\'),\r\n
\t\t\t\t\t\t\t\t\theight,\r\n
\t\t\t\t\t\t\t\t\tminX,\r\n
\t\t\t\t\t\t\t\t\tminY);\r\n
\r\n
\t\t\t\t\tsvg.ViewPort.SetCurrent(viewBox[2], viewBox[3]);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.symbol.prototype = new svg.Element.RenderedElementBase;\r\n
\r\n
\t\t// style element\r\n
\t\tsvg.Element.style = function(node) {\r\n
\t\t\tthis.base = svg.Element.ElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\t// text, or spaces then CDATA\r\n
\t\t\tvar css = node.childNodes[0].nodeValue + (node.childNodes.length > 1 ? node.childNodes[1].nodeValue : \'\');\r\n
\t\t\tcss = css.replace(/(\\/\\*([^*]|[\\r\\n]|(\\*+([^*\\/]|[\\r\\n])))*\\*+\\/)|(^[\\s]*\\/\\/.*)/gm, \'\'); // remove comments\r\n
\t\t\tcss = svg.compressSpaces(css); // replace whitespace\r\n
\t\t\tvar cssDefs = css.split(\'}\');\r\n
\t\t\tfor (var i=0; i<cssDefs.length; i++) {\r\n
\t\t\t\tif (svg.trim(cssDefs[i]) != \'\') {\r\n
\t\t\t\t\tvar cssDef = cssDefs[i].split(\'{\');\r\n
\t\t\t\t\tvar cssClasses = cssDef[0].split(\',\');\r\n
\t\t\t\t\tvar cssProps = cssDef[1].split(\';\');\r\n
\t\t\t\t\tfor (var j=0; j<cssClasses.length; j++) {\r\n
\t\t\t\t\t\tvar cssClass = svg.trim(cssClasses[j]);\r\n
\t\t\t\t\t\tif (cssClass != \'\') {\r\n
\t\t\t\t\t\t\tvar props = {};\r\n
\t\t\t\t\t\t\tfor (var k=0; k<cssProps.length; k++) {\r\n
\t\t\t\t\t\t\t\tvar prop = cssProps[k].indexOf(\':\');\r\n
\t\t\t\t\t\t\t\tvar name = cssProps[k].substr(0, prop);\r\n
\t\t\t\t\t\t\t\tvar value = cssProps[k].substr(prop + 1, cssProps[k].length - prop);\r\n
\t\t\t\t\t\t\t\tif (name != null && value != null) {\r\n
\t\t\t\t\t\t\t\t\tprops[svg.trim(name)] = new svg.Property(svg.trim(name), svg.trim(value));\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tsvg.Styles[cssClass] = props;\r\n
\t\t\t\t\t\t\tif (cssClass == \'@font-face\') {\r\n
\t\t\t\t\t\t\t\tvar fontFamily = props[\'font-family\'].value.replace(/"/g,\'\');\r\n
\t\t\t\t\t\t\t\tvar srcs = props[\'src\'].value.split(\',\');\r\n
\t\t\t\t\t\t\t\tfor (var s=0; s<srcs.length; s++) {\r\n
\t\t\t\t\t\t\t\t\tif (srcs[s].indexOf(\'format("svg")\') > 0) {\r\n
\t\t\t\t\t\t\t\t\t\tvar urlStart = srcs[s].indexOf(\'url\');\r\n
\t\t\t\t\t\t\t\t\t\tvar urlEnd = srcs[s].indexOf(\')\', urlStart);\r\n
\t\t\t\t\t\t\t\t\t\tvar url = srcs[s].substr(urlStart + 5, urlEnd - urlStart - 6);\r\n
\t\t\t\t\t\t\t\t\t\tvar doc = svg.parseXml(svg.ajax(url));\r\n
\t\t\t\t\t\t\t\t\t\tvar fonts = doc.getElementsByTagName(\'font\');\r\n
\t\t\t\t\t\t\t\t\t\tfor (var f=0; f<fonts.length; f++) {\r\n
\t\t\t\t\t\t\t\t\t\t\tvar font = svg.CreateElement(fonts[f]);\r\n
\t\t\t\t\t\t\t\t\t\t\tsvg.Definitions[fontFamily] = font;\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.style.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\t// use element\r\n
\t\tsvg.Element.use = function(node) {\r\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.baseSetContext = this.setContext;\r\n
\t\t\tthis.setContext = function(ctx) {\r\n
\t\t\t\tthis.baseSetContext(ctx);\r\n
\t\t\t\tif (this.attribute(\'x\').hasValue()) ctx.translate(this.attribute(\'x\').Length.toPixels(\'x\'), 0);\r\n
\t\t\t\tif (this.attribute(\'y\').hasValue()) ctx.translate(0, this.attribute(\'y\').Length.toPixels(\'y\'));\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.getDefinition = function() {\r\n
\t\t\t\tvar element = this.attribute(\'xlink:href\').Definition.getDefinition();\r\n
\t\t\t\tif (this.attribute(\'width\').hasValue()) element.attribute(\'width\', true).value = this.attribute(\'width\').value;\r\n
\t\t\t\tif (this.attribute(\'height\').hasValue()) element.attribute(\'height\', true).value = this.attribute(\'height\').value;\r\n
\t\t\t\treturn element;\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.path = function(ctx) {\r\n
\t\t\t\tvar element = this.getDefinition();\r\n
\t\t\t\tif (element != null) element.path(ctx);\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.renderChildren = function(ctx) {\r\n
\t\t\t\tvar element = this.getDefinition();\r\n
\t\t\t\tif (element != null) element.render(ctx);\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.use.prototype = new svg.Element.RenderedElementBase;\r\n
\r\n
\t\t// mask element\r\n
\t\tsvg.Element.mask = function(node) {\r\n
\t\t\tthis.base = svg.Element.ElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.apply = function(ctx, element) {\r\n
\t\t\t\t// render as temp svg\r\n
\t\t\t\tvar x = this.attribute(\'x\').Length.toPixels(\'x\');\r\n
\t\t\t\tvar y = this.attribute(\'y\').Length.toPixels(\'y\');\r\n
\t\t\t\tvar width = this.attribute(\'width\').Length.toPixels(\'x\');\r\n
\t\t\t\tvar height = this.attribute(\'height\').Length.toPixels(\'y\');\r\n
\r\n
\t\t\t\t// temporarily remove mask to avoid recursion\r\n
\t\t\t\tvar mask = element.attribute(\'mask\').value;\r\n
\t\t\t\telement.attribute(\'mask\').value = \'\';\r\n
\r\n
\t\t\t\t\tvar cMask = document.createElement(\'canvas\');\r\n
\t\t\t\t\tcMask.width = x + width;\r\n
\t\t\t\t\tcMask.height = y + height;\r\n
\t\t\t\t\tvar maskCtx = cMask.getContext(\'2d\');\r\n
\t\t\t\t\tthis.renderChildren(maskCtx);\r\n
\r\n
\t\t\t\t\tvar c = document.createElement(\'canvas\');\r\n
\t\t\t\t\tc.width = x + width;\r\n
\t\t\t\t\tc.height = y + height;\r\n
\t\t\t\t\tvar tempCtx = c.getContext(\'2d\');\r\n
\t\t\t\t\telement.render(tempCtx);\r\n
\t\t\t\t\ttempCtx.globalCompositeOperation = \'destination-in\';\r\n
\t\t\t\t\ttempCtx.fillStyle = maskCtx.createPattern(cMask, \'no-repeat\');\r\n
\t\t\t\t\ttempCtx.fillRect(0, 0, x + width, y + height);\r\n
\r\n
\t\t\t\t\tctx.fillStyle = tempCtx.createPattern(c, \'no-repeat\');\r\n
\t\t\t\t\tctx.fillRect(0, 0, x + width, y + height);\r\n
\r\n
\t\t\t\t// reassign mask\r\n
\t\t\t\telement.attribute(\'mask\').value = mask;\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.render = function(ctx) {\r\n
\t\t\t\t// NO RENDER\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.mask.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\t// clip element\r\n
\t\tsvg.Element.clipPath = function(node) {\r\n
\t\t\tthis.base = svg.Element.ElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.apply = function(ctx) {\r\n
\t\t\t\tfor (var i=0; i<this.children.length; i++) {\r\n
\t\t\t\t\tif (this.children[i].path) {\r\n
\t\t\t\t\t\tthis.children[i].path(ctx);\r\n
\t\t\t\t\t\tctx.clip();\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.render = function(ctx) {\r\n
\t\t\t\t// NO RENDER\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.clipPath.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\t// filters\r\n
\t\tsvg.Element.filter = function(node) {\r\n
\t\t\tthis.base = svg.Element.ElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tthis.apply = function(ctx, element) {\r\n
\t\t\t\t// render as temp svg\r\n
\t\t\t\tvar bb = element.getBoundingBox();\r\n
\t\t\t\tvar x = this.attribute(\'x\').Length.toPixels(\'x\');\r\n
\t\t\t\tvar y = this.attribute(\'y\').Length.toPixels(\'y\');\r\n
\t\t\t\tif (x == 0 || y == 0) {\r\n
\t\t\t\t\tx = bb.x1;\r\n
\t\t\t\t\ty = bb.y1;\r\n
\t\t\t\t}\r\n
\t\t\t\tvar width = this.attribute(\'width\').Length.toPixels(\'x\');\r\n
\t\t\t\tvar height = this.attribute(\'height\').Length.toPixels(\'y\');\r\n
\t\t\t\tif (width == 0 || height == 0) {\r\n
\t\t\t\t\twidth = bb.width();\r\n
\t\t\t\t\theight = bb.height();\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// temporarily remove filter to avoid recursion\r\n
\t\t\t\tvar filter = element.style(\'filter\').value;\r\n
\t\t\t\telement.style(\'filter\').value = \'\';\r\n
\r\n
\t\t\t\t// max filter distance\r\n
\t\t\t\tvar extraPercent = .20;\r\n
\t\t\t\tvar px = extraPercent * width;\r\n
\t\t\t\tvar py = extraPercent * height;\r\n
\r\n
\t\t\t\tvar c = document.createElement(\'canvas\');\r\n
\t\t\t\tc.width = width + 2*px;\r\n
\t\t\t\tc.height = height + 2*py;\r\n
\t\t\t\tvar tempCtx = c.getContext(\'2d\');\r\n
\t\t\t\ttempCtx.translate(-x + px, -y + py);\r\n
\t\t\t\telement.render(tempCtx);\r\n
\r\n
\t\t\t\t// apply filters\r\n
\t\t\t\tfor (var i=0; i<this.children.length; i++) {\r\n
\t\t\t\t\tthis.children[i].apply(tempCtx, 0, 0, width + 2*px, height + 2*py);\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// render on me\r\n
\t\t\t\tctx.drawImage(c, 0, 0, width + 2*px, height + 2*py, x - px, y - py, width + 2*px, height + 2*py);\r\n
\r\n
\t\t\t\t// reassign filter\r\n
\t\t\t\telement.style(\'filter\', true).value = filter;\r\n
\t\t\t};\r\n
\r\n
\t\t\tthis.render = function(ctx) {\r\n
\t\t\t\t// NO RENDER\r\n
\t\t\t};\r\n
\t\t}\r\n
\t\tsvg.Element.filter.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\tsvg.Element.feGaussianBlur = function(node) {\r\n
\t\t\tthis.base = svg.Element.ElementBase;\r\n
\t\t\tthis.base(node);\r\n
\r\n
\t\t\tfunction make_fgauss(sigma) {\r\n
\t\t\t\tsigma = Math.max(sigma, 0.01);\r\n
\t\t\t\tvar len = Math.ceil(sigma * 4.0) + 1;\r\n
\t\t\t\tmask = [];\r\n
\t\t\t\tfor (var i = 0; i < len; i++) {\r\n
\t\t\t\t\tmask[i] = Math.exp(-0.5 * (i / sigma) * (i / sigma));\r\n
\t\t\t\t}\r\n
\t\t\t\treturn mask;\r\n
\t\t\t}\r\n
\r\n
\t\t\tfunction normalize(mask) {\r\n
\t\t\t\tvar sum = 0;\r\n
\t\t\t\tfor (var i = 1; i < mask.length; i++) {\r\n
\t\t\t\t\tsum += Math.abs(mask[i]);\r\n
\t\t\t\t}\r\n
\t\t\t\tsum = 2 * sum + Math.abs(mask[0]);\r\n
\t\t\t\tfor (var i = 0; i < mask.length; i++) {\r\n
\t\t\t\t\tmask[i] /= sum;\r\n
\t\t\t\t}\r\n
\t\t\t\treturn mask;\r\n
\t\t\t}\r\n
\r\n
\t\t\tfunction convolve_even(src, dst, mask, width, height) {\r\n
\t\t\t  for (var y = 0; y < height; y++) {\r\n
\t\t\t\tfor (var x = 0; x < width; x++) {\r\n
\t\t\t\t  var a = imGet(src, x, y, width, height, 3)/255;\r\n
\t\t\t\t  for (var rgba = 0; rgba < 4; rgba++) {\r\n
\t\t\t\t\t  var sum = mask[0] * (a==0?255:imGet(src, x, y, width, height, rgba)) * (a==0||rgba==3?1:a);\r\n
\t\t\t\t\t  for (var i = 1; i < mask.length; i++) {\r\n
\t\t\t\t\t\tvar a1 = imGet(src, Math.max(x-i,0), y, width, height, 3)/255;\r\n
\t\t\t\t\t\tvar a2 = imGet(src, Math.min(x+i, width-1), y, width, height, 3)/255;\r\n
\t\t\t\t\t\tsum += mask[i] *\r\n
\t\t\t\t\t\t  ((a1==0?255:imGet(src, Math.max(x-i,0), y, width, height, rgba)) * (a1==0||rgba==3?1:a1) +\r\n
\t\t\t\t\t\t   (a2==0?255:imGet(src, Math.min(x+i, width-1), y, width, height, rgba)) * (a2==0||rgba==3?1:a2));\r\n
\t\t\t\t\t  }\r\n
\t\t\t\t\t  imSet(dst, y, x, height, width, rgba, sum);\r\n
\t\t\t\t  }\r\n
\t\t\t\t}\r\n
\t\t\t  }\r\n
\t\t\t}\r\n
\r\n
\t\t\tfunction imGet(img, x, y, width, height, rgba) {\r\n
\t\t\t\treturn img[y*width*4 + x*4 + rgba];\r\n
\t\t\t}\r\n
\r\n
\t\t\tfunction imSet(img, x, y, width, height, rgba, val) {\r\n
\t\t\t\timg[y*width*4 + x*4 + rgba] = val;\r\n
\t\t\t}\r\n
\r\n
\t\t\tfunction blur(ctx, width, height, sigma)\r\n
\t\t\t{\r\n
\t\t\t\tvar srcData = ctx.getImageData(0, 0, width, height);\r\n
\t\t\t\tvar mask = make_fgauss(sigma);\r\n
\t\t\t\tmask = normalize(mask);\r\n
\t\t\t\ttmp = [];\r\n
\t\t\t\tconvolve_even(srcData.data, tmp, mask, width, height);\r\n
\t\t\t\tconvolve_even(tmp, srcData.data, mask, height, width);\r\n
\t\t\t\tctx.clearRect(0, 0, width, height);\r\n
\t\t\t\tctx.putImageData(srcData, 0, 0);\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.apply = function(ctx, x, y, width, height) {\r\n
\t\t\t\t// assuming x==0 && y==0 for now\r\n
\t\t\t\tblur(ctx, width, height, this.attribute(\'stdDeviation\').numValue());\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tsvg.Element.filter.prototype = new svg.Element.feGaussianBlur;\r\n
\r\n
\t\t// title element, do nothing\r\n
\t\tsvg.Element.title = function(node) {\r\n
\t\t}\r\n
\t\tsvg.Element.title.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\t// desc element, do nothing\r\n
\t\tsvg.Element.desc = function(node) {\r\n
\t\t}\r\n
\t\tsvg.Element.desc.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\tsvg.Element.MISSING = function(node) {\r\n
\t\t\tconsole.log(\'ERROR: Element \\\'\' + node.nodeName + \'\\\' not yet implemented.\');\r\n
\t\t}\r\n
\t\tsvg.Element.MISSING.prototype = new svg.Element.ElementBase;\r\n
\r\n
\t\t// element factory\r\n
\t\tsvg.CreateElement = function(node) {\r\n
\t\t\tvar className = node.nodeName.replace(/^[^:]+:/,\'\'); // remove namespace\r\n
\t\t\tclassName = className.replace(/\\-/g,\'\'); // remove dashes\r\n
\t\t\tvar e = null;\r\n
\t\t\tif (typeof(svg.Element[className]) != \'undefined\') {\r\n
\t\t\t\te = new svg.Element[className](node);\r\n
\t\t\t}\r\n
\t\t\telse {\r\n
\t\t\t\te = new svg.Element.MISSING(node);\r\n
\t\t\t}\r\n
\r\n
\t\t\te.type = node.nodeName;\r\n
\t\t\treturn e;\r\n
\t\t}\r\n
\r\n
\t\t// load from url\r\n
\t\tsvg.load = function(ctx, url) {\r\n
\t\t\tsvg.loadXml(ctx, svg.ajax(url));\r\n
\t\t}\r\n
\r\n
\t\t// load from xml\r\n
\t\tsvg.loadXml = function(ctx, xml) {\r\n
\t\t\tsvg.loadXmlDoc(ctx, svg.parseXml(xml));\r\n
\t\t}\r\n
\r\n
\t\tsvg.loadXmlDoc = function(ctx, dom) {\r\n
\t\t\tsvg.init(ctx);\r\n
\r\n
\t\t\tvar mapXY = function(p) {\r\n
\t\t\t\tvar e = ctx.canvas;\r\n
\t\t\t\twhile (e) {\r\n
\t\t\t\t\tp.x -= e.offsetLeft;\r\n
\t\t\t\t\tp.y -= e.offsetTop;\r\n
\t\t\t\t\te = e.offsetParent;\r\n
\t\t\t\t}\r\n
\t\t\t\tif (window.scrollX) p.x += window.scrollX;\r\n
\t\t\t\tif (window.scrollY) p.y += window.scrollY;\r\n
\t\t\t\treturn p;\r\n
\t\t\t}\r\n
\r\n
\t\t\t// bind mouse\r\n
\t\t\tif (svg.opts[\'ignoreMouse\'] != true) {\r\n
\t\t\t\tctx.canvas.onclick = function(e) {\r\n
\t\t\t\t\tvar p = mapXY(new svg.Point(e != null ? e.clientX : event.clientX, e != null ? e.clientY : event.clientY));\r\n
\t\t\t\t\tsvg.Mouse.onclick(p.x, p.y);\r\n
\t\t\t\t};\r\n
\t\t\t\tctx.canvas.onmousemove = function(e) {\r\n
\t\t\t\t\tvar p = mapXY(new svg.Point(e != null ? e.clientX : event.clientX, e != null ? e.clientY : event.clientY));\r\n
\t\t\t\t\tsvg.Mouse.onmousemove(p.x, p.y);\r\n
\t\t\t\t};\r\n
\t\t\t}\r\n
\r\n
\t\t\tvar e = svg.CreateElement(dom.documentElement);\r\n
\t\t\te.root = true;\r\n
\r\n
\t\t\t// render loop\r\n
\t\t\tvar isFirstRender = true;\r\n
\t\t\tvar draw = function() {\r\n
\t\t\t\tsvg.ViewPort.Clear();\r\n
\t\t\t\tif (ctx.canvas.parentNode) svg.ViewPort.SetCurrent(ctx.canvas.parentNode.clientWidth, ctx.canvas.parentNode.clientHeight);\r\n
\r\n
\t\t\t\tif (svg.opts[\'ignoreDimensions\'] != true) {\r\n
\t\t\t\t\t// set canvas size\r\n
\t\t\t\t\tif (e.style(\'width\').hasValue()) {\r\n
\t\t\t\t\t\tctx.canvas.width = e.style(\'width\').Length.toPixels(\'x\');\r\n
\t\t\t\t\t\tctx.canvas.style.width = ctx.canvas.width + \'px\';\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif (e.style(\'height\').hasValue()) {\r\n
\t\t\t\t\t\tctx.canvas.height = e.style(\'height\').Length.toPixels(\'y\');\r\n
\t\t\t\t\t\tctx.canvas.style.height = ctx.canvas.height + \'px\';\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tvar cWidth = ctx.canvas.clientWidth || ctx.canvas.width;\r\n
\t\t\t\tvar cHeight = ctx.canvas.clientHeight || ctx.canvas.height;\r\n
\t\t\t\tsvg.ViewPort.SetCurrent(cWidth, cHeight);\r\n
\r\n
\t\t\t\tif (svg.opts != null && svg.opts[\'offsetX\'] != null) e.attribute(\'x\', true).value = svg.opts[\'offsetX\'];\r\n
\t\t\t\tif (svg.opts != null && svg.opts[\'offsetY\'] != null) e.attribute(\'y\', true).value = svg.opts[\'offsetY\'];\r\n
\t\t\t\tif (svg.opts != null && svg.opts[\'scaleWidth\'] != null && svg.opts[\'scaleHeight\'] != null) {\r\n
\t\t\t\t\tvar xRatio = 1, yRatio = 1;\r\n
\t\t\t\t\tif (e.attribute(\'width\').hasValue()) xRatio = e.attribute(\'width\').Length.toPixels(\'x\') / svg.opts[\'scaleWidth\'];\r\n
\t\t\t\t\tif (e.attribute(\'height\').hasValue()) yRatio = e.attribute(\'height\').Length.toPixels(\'y\') / svg.opts[\'scaleHeight\'];\r\n
\r\n
\t\t\t\t\te.attribute(\'width\', true).value = svg.opts[\'scaleWidth\'];\r\n
\t\t\t\t\te.attribute(\'height\', true).value = svg.opts[\'scaleHeight\'];\r\n
\t\t\t\t\te.attribute(\'viewBox\', true).value = \'0 0 \' + (cWidth * xRatio) + \' \' + (cHeight * yRatio);\r\n
\t\t\t\t\te.attribute(\'preserveAspectRatio\', true).value = \'none\';\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// clear and render\r\n
\t\t\t\tif (svg.opts[\'ignoreClear\'] != true) {\r\n
\t\t\t\t\tctx.clearRect(0, 0, cWidth, cHeight);\r\n
\t\t\t\t}\r\n
\t\t\t\te.render(ctx);\r\n
\t\t\t\tif (isFirstRender) {\r\n
\t\t\t\t\tisFirstRender = false;\r\n
\t\t\t\t\tif (svg.opts != null && typeof(svg.opts[\'renderCallback\']) == \'function\') svg.opts[\'renderCallback\']();\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tvar waitingForImages = true;\r\n
\t\t\tif (svg.ImagesLoaded()) {\r\n
\t\t\t\twaitingForImages = false;\r\n
\t\t\t\tdraw();\r\n
\t\t\t}\r\n
\t\t\tsvg.intervalID = setInterval(function() {\r\n
\t\t\t\tvar needUpdate = false;\r\n
\r\n
\t\t\t\tif (waitingForImages && svg.ImagesLoaded()) {\r\n
\t\t\t\t\twaitingForImages = false;\r\n
\t\t\t\t\tneedUpdate = true;\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// need update from mouse events?\r\n
\t\t\t\tif (svg.opts[\'ignoreMouse\'] != true) {\r\n
\t\t\t\t\tneedUpdate = needUpdate | svg.Mouse.hasEvents();\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// need update from animations?\r\n
\t\t\t\tif (svg.opts[\'ignoreAnimation\'] != true) {\r\n
\t\t\t\t\tfor (var i=0; i<svg.Animations.length; i++) {\r\n
\t\t\t\t\t\tneedUpdate = needUpdate | svg.Animations[i].update(1000 / svg.FRAMERATE);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// need update from redraw?\r\n
\t\t\t\tif (svg.opts != null && typeof(svg.opts[\'forceRedraw\']) == \'function\') {\r\n
\t\t\t\t\tif (svg.opts[\'forceRedraw\']() == true) needUpdate = true;\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// render if needed\r\n
\t\t\t\tif (needUpdate) {\r\n
\t\t\t\t\tdraw();\r\n
\t\t\t\t\tsvg.Mouse.runEvents(); // run and clear our events\r\n
\t\t\t\t}\r\n
\t\t\t}, 1000 / svg.FRAMERATE);\r\n
\t\t}\r\n
\r\n
\t\tsvg.stop = function() {\r\n
\t\t\tif (svg.intervalID) {\r\n
\t\t\t\tclearInterval(svg.intervalID);\r\n
\t\t\t}\r\n
\t\t}\r\n
\r\n
\t\tsvg.Mouse = new (function() {\r\n
\t\t\tthis.events = [];\r\n
\t\t\tthis.hasEvents = function() { return this.events.length != 0; }\r\n
\r\n
\t\t\tthis.onclick = function(x, y) {\r\n
\t\t\t\tthis.events.push({ type: \'onclick\', x: x, y: y,\r\n
\t\t\t\t\trun: function(e) { if (e.onclick) e.onclick(); }\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.onmousemove = function(x, y) {\r\n
\t\t\t\tthis.events.push({ type: \'onmousemove\', x: x, y: y,\r\n
\t\t\t\t\trun: function(e) { if (e.onmousemove) e.onmousemove(); }\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.eventElements = [];\r\n
\r\n
\t\t\tthis.checkPath = function(element, ctx) {\r\n
\t\t\t\tfor (var i=0; i<this.events.length; i++) {\r\n
\t\t\t\t\tvar e = this.events[i];\r\n
\t\t\t\t\tif (ctx.isPointInPath && ctx.isPointInPath(e.x, e.y)) this.eventElements[i] = element;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.checkBoundingBox = function(element, bb) {\r\n
\t\t\t\tfor (var i=0; i<this.events.length; i++) {\r\n
\t\t\t\t\tvar e = this.events[i];\r\n
\t\t\t\t\tif (bb.isPointInBox(e.x, e.y)) this.eventElements[i] = element;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.runEvents = function() {\r\n
\t\t\t\tsvg.ctx.canvas.style.cursor = \'\';\r\n
\r\n
\t\t\t\tfor (var i=0; i<this.events.length; i++) {\r\n
\t\t\t\t\tvar e = this.events[i];\r\n
\t\t\t\t\tvar element = this.eventElements[i];\r\n
\t\t\t\t\twhile (element) {\r\n
\t\t\t\t\t\te.run(element);\r\n
\t\t\t\t\t\telement = element.parent;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\t// done running, clear\r\n
\t\t\t\tthis.events = [];\r\n
\t\t\t\tthis.eventElements = [];\r\n
\t\t\t}\r\n
\t\t});\r\n
\r\n
\t\treturn svg;\r\n
\t}\r\n
})();\r\n
\r\n
if (CanvasRenderingContext2D) {\r\n
\tCanvasRenderingContext2D.prototype.drawSvg = function(s, dx, dy, dw, dh) {\r\n
\t\tcanvg(this.canvas, s, {\r\n
\t\t\tignoreMouse: true,\r\n
\t\t\tignoreAnimation: true,\r\n
\t\t\tignoreDimensions: true,\r\n
\t\t\tignoreClear: true,\r\n
\t\t\toffsetX: dx,\r\n
\t\t\toffsetY: dy,\r\n
\t\t\tscaleWidth: dw,\r\n
\t\t\tscaleHeight: dh\r\n
\t\t});\r\n
\t}\r\n
}

]]></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
