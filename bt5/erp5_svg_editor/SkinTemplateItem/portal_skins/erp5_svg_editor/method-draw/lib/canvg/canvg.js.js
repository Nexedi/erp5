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
            <value> <string>ts53288356.18</string> </value>
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
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * canvg.js - Javascript SVG parser and renderer on Canvas\n
 * MIT Licensed \n
 * Gabe Lerner (gabelerner@gmail.com)\n
 * http://code.google.com/p/canvg/\n
 *\n
 * Requires: rgbcolor.js - http://www.phpied.com/rgb-color-parser-in-javascript/\n
 */\n
if(!window.console) {\n
\twindow.console = {};\n
\twindow.console.log = function(str) {};\n
\twindow.console.dir = function(str) {};\n
}\n
\n
if(!Array.prototype.indexOf){\n
\tArray.prototype.indexOf = function(obj){\n
\t\tfor(var i=0; i<this.length; i++){\n
\t\t\tif(this[i]==obj){\n
\t\t\t\treturn i;\n
\t\t\t}\n
\t\t}\n
\t\treturn -1;\n
\t}\n
}\n
\n
(function(){\n
\t// canvg(target, s)\n
\t// empty parameters: replace all \'svg\' elements on page with \'canvas\' elements\n
\t// target: canvas element or the id of a canvas element\n
\t// s: svg string, url to svg file, or xml document\n
\t// opts: optional hash of options\n
\t//\t\t ignoreMouse: true => ignore mouse events\n
\t//\t\t ignoreAnimation: true => ignore animations\n
\t//\t\t ignoreDimensions: true => does not try to resize canvas\n
\t//\t\t ignoreClear: true => does not clear canvas\n
\t//\t\t offsetX: int => draws at a x offset\n
\t//\t\t offsetY: int => draws at a y offset\n
\t//\t\t scaleWidth: int => scales horizontally to width\n
\t//\t\t scaleHeight: int => scales vertically to height\n
\t//\t\t renderCallback: function => will call the function after the first render is completed\n
\t//\t\t forceRedraw: function => will call the function on every frame, if it returns true, will redraw\n
\tthis.canvg = function (target, s, opts) {\n
\t\t// no parameters\n
\t\tif (target == null && s == null && opts == null) {\n
\t\t\tvar svgTags = document.getElementsByTagName(\'svg\');\n
\t\t\tfor (var i=0; i<svgTags.length; i++) {\n
\t\t\t\tvar svgTag = svgTags[i];\n
\t\t\t\tvar c = document.createElement(\'canvas\');\n
\t\t\t\tc.width = svgTag.clientWidth;\n
\t\t\t\tc.height = svgTag.clientHeight;\n
\t\t\t\tsvgTag.parentNode.insertBefore(c, svgTag);\n
\t\t\t\tsvgTag.parentNode.removeChild(svgTag);\n
\t\t\t\tvar div = document.createElement(\'div\');\n
\t\t\t\tdiv.appendChild(svgTag);\n
\t\t\t\tcanvg(c, div.innerHTML);\n
\t\t\t}\n
\t\t\treturn;\n
\t\t}\t\n
\t\topts = opts || {};\n
\t\n
\t\tif (typeof target == \'string\') {\n
\t\t\ttarget = document.getElementById(target);\n
\t\t}\n
\t\t\n
\t\t// reuse class per canvas\n
\t\tvar svg;\n
\t\tif (target.svg == null) {\n
\t\t\tsvg = build();\n
\t\t\ttarget.svg = svg;\n
\t\t}\n
\t\telse {\n
\t\t\tsvg = target.svg;\n
\t\t\tsvg.stop();\n
\t\t}\n
\t\tsvg.opts = opts;\n
\t\t\n
\t\tvar ctx = target.getContext(\'2d\');\n
\t\tif (typeof(s.documentElement) != \'undefined\') {\n
\t\t\t// load from xml doc\n
\t\t\tsvg.loadXmlDoc(ctx, s);\n
\t\t}\n
\t\telse if (s.substr(0,1) == \'<\') {\n
\t\t\t// load from xml string\n
\t\t\tsvg.loadXml(ctx, s);\n
\t\t}\n
\t\telse {\n
\t\t\t// load from url\n
\t\t\tsvg.load(ctx, s);\n
\t\t}\n
\t}\n
\n
\tfunction build() {\n
\t\tvar svg = { };\n
\t\t\n
\t\tsvg.FRAMERATE = 30;\n
\t\tsvg.MAX_VIRTUAL_PIXELS = 30000;\n
\t\t\n
\t\t// globals\n
\t\tsvg.init = function(ctx) {\n
\t\t\tsvg.Definitions = {};\n
\t\t\tsvg.Styles = {};\n
\t\t\tsvg.Animations = [];\n
\t\t\tsvg.Images = [];\n
\t\t\tsvg.ctx = ctx;\n
\t\t\tsvg.ViewPort = new (function () {\n
\t\t\t\tthis.viewPorts = [];\n
\t\t\t\tthis.Clear = function() { this.viewPorts = []; }\n
\t\t\t\tthis.SetCurrent = function(width, height) { this.viewPorts.push({ width: width, height: height }); }\n
\t\t\t\tthis.RemoveCurrent = function() { this.viewPorts.pop(); }\n
\t\t\t\tthis.Current = function() { return this.viewPorts[this.viewPorts.length - 1]; }\n
\t\t\t\tthis.width = function() { return this.Current().width; }\n
\t\t\t\tthis.height = function() { return this.Current().height; }\n
\t\t\t\tthis.ComputeSize = function(d) {\n
\t\t\t\t\tif (d != null && typeof(d) == \'number\') return d;\n
\t\t\t\t\tif (d == \'x\') return this.width();\n
\t\t\t\t\tif (d == \'y\') return this.height();\n
\t\t\t\t\treturn Math.sqrt(Math.pow(this.width(), 2) + Math.pow(this.height(), 2)) / Math.sqrt(2);\t\t\t\n
\t\t\t\t}\n
\t\t\t});\n
\t\t}\n
\t\tsvg.init();\n
\t\t\n
\t\t// images loaded\n
\t\tsvg.ImagesLoaded = function() { \n
\t\t\tfor (var i=0; i<svg.Images.length; i++) {\n
\t\t\t\tif (!svg.Images[i].loaded) return false;\n
\t\t\t}\n
\t\t\treturn true;\n
\t\t}\n
\n
\t\t// trim\n
\t\tsvg.trim = function(s) { return s.replace(/^\\s+|\\s+$/g, \'\'); }\n
\t\t\n
\t\t// compress spaces\n
\t\tsvg.compressSpaces = function(s) { return s.replace(/[\\s\\r\\t\\n]+/gm,\' \'); }\n
\t\t\n
\t\t// ajax\n
\t\tsvg.ajax = function(url) {\n
\t\t\tvar AJAX;\n
\t\t\tif(window.XMLHttpRequest){AJAX=new XMLHttpRequest();}\n
\t\t\telse{AJAX=new ActiveXObject(\'Microsoft.XMLHTTP\');}\n
\t\t\tif(AJAX){\n
\t\t\t   AJAX.open(\'GET\',url,false);\n
\t\t\t   AJAX.send(null);\n
\t\t\t   return AJAX.responseText;\n
\t\t\t}\n
\t\t\treturn null;\n
\t\t} \n
\t\t\n
\t\t// parse xml\n
\t\tsvg.parseXml = function(xml) {\n
\t\t\tif (window.DOMParser)\n
\t\t\t{\n
\t\t\t\tvar parser = new DOMParser();\n
\t\t\t\treturn parser.parseFromString(xml, \'text/xml\');\n
\t\t\t}\n
\t\t\telse \n
\t\t\t{\n
\t\t\t\txml = xml.replace(/<!DOCTYPE svg[^>]*>/, \'\');\n
\t\t\t\tvar xmlDoc = new ActiveXObject(\'Microsoft.XMLDOM\');\n
\t\t\t\txmlDoc.async = \'false\';\n
\t\t\t\txmlDoc.loadXML(xml); \n
\t\t\t\treturn xmlDoc;\n
\t\t\t}\t\t\n
\t\t}\n
\t\t\n
\t\tsvg.Property = function(name, value) {\n
\t\t\tthis.name = name;\n
\t\t\tthis.value = value;\n
\t\t\t\n
\t\t\tthis.hasValue = function() {\n
\t\t\t\treturn (this.value != null && this.value !== \'\');\n
\t\t\t}\n
\t\t\t\t\t\t\t\n
\t\t\t// return the numerical value of the property\n
\t\t\tthis.numValue = function() {\n
\t\t\t\tif (!this.hasValue()) return 0;\n
\t\t\t\t\n
\t\t\t\tvar n = parseFloat(this.value);\n
\t\t\t\tif ((this.value + \'\').match(/%$/)) {\n
\t\t\t\t\tn = n / 100.0;\n
\t\t\t\t}\n
\t\t\t\treturn n;\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.valueOrDefault = function(def) {\n
\t\t\t\tif (this.hasValue()) return this.value;\n
\t\t\t\treturn def;\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.numValueOrDefault = function(def) {\n
\t\t\t\tif (this.hasValue()) return this.numValue();\n
\t\t\t\treturn def;\n
\t\t\t}\n
\t\t\t\n
\t\t\t/* EXTENSIONS */\n
\t\t\tvar that = this;\n
\t\t\t\n
\t\t\t// color extensions\n
\t\t\tthis.Color = {\n
\t\t\t\t// augment the current color value with the opacity\n
\t\t\t\taddOpacity: function(opacity) {\n
\t\t\t\t\tvar newValue = that.value;\n
\t\t\t\t\tif (opacity != null && opacity != \'\') {\n
\t\t\t\t\t\tvar color = new RGBColor(that.value);\n
\t\t\t\t\t\tif (color.ok) {\n
\t\t\t\t\t\t\tnewValue = \'rgba(\' + color.r + \', \' + color.g + \', \' + color.b + \', \' + opacity + \')\';\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\treturn new svg.Property(that.name, newValue);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\t// definition extensions\n
\t\t\tthis.Definition = {\n
\t\t\t\t// get the definition from the definitions table\n
\t\t\t\tgetDefinition: function() {\n
\t\t\t\t\tvar name = that.value.replace(/^(url\\()?#([^\\)]+)\\)?$/, \'$2\');\n
\t\t\t\t\treturn svg.Definitions[name];\n
\t\t\t\t},\n
\t\t\t\t\n
\t\t\t\tisUrl: function() {\n
\t\t\t\t\treturn that.value.indexOf(\'url(\') == 0\n
\t\t\t\t},\n
\t\t\t\t\n
\t\t\t\tgetFillStyle: function(e) {\n
\t\t\t\t\tvar def = this.getDefinition();\n
\t\t\t\t\t\n
\t\t\t\t\t// gradient\n
\t\t\t\t\tif (def != null && def.createGradient) {\n
\t\t\t\t\t\treturn def.createGradient(svg.ctx, e);\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\t// pattern\n
\t\t\t\t\tif (def != null && def.createPattern) {\n
\t\t\t\t\t\treturn def.createPattern(svg.ctx, e);\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\treturn null;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\t// length extensions\n
\t\t\tthis.Length = {\n
\t\t\t\tDPI: function(viewPort) {\n
\t\t\t\t\treturn 96.0; // TODO: compute?\n
\t\t\t\t},\n
\t\t\t\t\n
\t\t\t\tEM: function(viewPort) {\n
\t\t\t\t\tvar em = 12;\n
\t\t\t\t\t\n
\t\t\t\t\tvar fontSize = new svg.Property(\'fontSize\', svg.Font.Parse(svg.ctx.font).fontSize);\n
\t\t\t\t\tif (fontSize.hasValue()) em = fontSize.Length.toPixels(viewPort);\n
\t\t\t\t\t\n
\t\t\t\t\treturn em;\n
\t\t\t\t},\n
\t\t\t\n
\t\t\t\t// get the length as pixels\n
\t\t\t\ttoPixels: function(viewPort) {\n
\t\t\t\t\tif (!that.hasValue()) return 0;\n
\t\t\t\t\tvar s = that.value+\'\';\n
\t\t\t\t\tif (s.match(/em$/)) return that.numValue() * this.EM(viewPort);\n
\t\t\t\t\tif (s.match(/ex$/)) return that.numValue() * this.EM(viewPort) / 2.0;\n
\t\t\t\t\tif (s.match(/px$/)) return that.numValue();\n
\t\t\t\t\tif (s.match(/pt$/)) return that.numValue() * 1.25;\n
\t\t\t\t\tif (s.match(/pc$/)) return that.numValue() * 15;\n
\t\t\t\t\tif (s.match(/cm$/)) return that.numValue() * this.DPI(viewPort) / 2.54;\n
\t\t\t\t\tif (s.match(/mm$/)) return that.numValue() * this.DPI(viewPort) / 25.4;\n
\t\t\t\t\tif (s.match(/in$/)) return that.numValue() * this.DPI(viewPort);\n
\t\t\t\t\tif (s.match(/%$/)) return that.numValue() * svg.ViewPort.ComputeSize(viewPort);\n
\t\t\t\t\treturn that.numValue();\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\t// time extensions\n
\t\t\tthis.Time = {\n
\t\t\t\t// get the time as milliseconds\n
\t\t\t\ttoMilliseconds: function() {\n
\t\t\t\t\tif (!that.hasValue()) return 0;\n
\t\t\t\t\tvar s = that.value+\'\';\n
\t\t\t\t\tif (s.match(/s$/)) return that.numValue() * 1000;\n
\t\t\t\t\tif (s.match(/ms$/)) return that.numValue();\n
\t\t\t\t\treturn that.numValue();\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\t// angle extensions\n
\t\t\tthis.Angle = {\n
\t\t\t\t// get the angle as radians\n
\t\t\t\ttoRadians: function() {\n
\t\t\t\t\tif (!that.hasValue()) return 0;\n
\t\t\t\t\tvar s = that.value+\'\';\n
\t\t\t\t\tif (s.match(/deg$/)) return that.numValue() * (Math.PI / 180.0);\n
\t\t\t\t\tif (s.match(/grad$/)) return that.numValue() * (Math.PI / 200.0);\n
\t\t\t\t\tif (s.match(/rad$/)) return that.numValue();\n
\t\t\t\t\treturn that.numValue() * (Math.PI / 180.0);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t\t\n
\t\t// fonts\n
\t\tsvg.Font = new (function() {\n
\t\t\tthis.Styles = [\'normal\',\'italic\',\'oblique\',\'inherit\'];\n
\t\t\tthis.Variants = [\'normal\',\'small-caps\',\'inherit\'];\n
\t\t\tthis.Weights = [\'normal\',\'bold\',\'bolder\',\'lighter\',\'100\',\'200\',\'300\',\'400\',\'500\',\'600\',\'700\',\'800\',\'900\',\'inherit\'];\n
\t\t\t\n
\t\t\tthis.CreateFont = function(fontStyle, fontVariant, fontWeight, fontSize, fontFamily, inherit) { \n
\t\t\t\tvar f = inherit != null ? this.Parse(inherit) : this.CreateFont(\'\', \'\', \'\', \'\', \'\', svg.ctx.font);\n
\t\t\t\treturn { \n
\t\t\t\t\tfontFamily: fontFamily || f.fontFamily, \n
\t\t\t\t\tfontSize: fontSize || f.fontSize, \n
\t\t\t\t\tfontStyle: fontStyle || f.fontStyle, \n
\t\t\t\t\tfontWeight: fontWeight || f.fontWeight, \n
\t\t\t\t\tfontVariant: fontVariant || f.fontVariant,\n
\t\t\t\t\ttoString: function () { return [this.fontStyle, this.fontVariant, this.fontWeight, this.fontSize, this.fontFamily].join(\' \') } \n
\t\t\t\t} \n
\t\t\t}\n
\t\t\t\n
\t\t\tvar that = this;\n
\t\t\tthis.Parse = function(s) {\n
\t\t\t\tvar f = {};\n
\t\t\t\tvar d = svg.trim(svg.compressSpaces(s || \'\')).split(\' \');\n
\t\t\t\tvar set = { fontSize: false, fontStyle: false, fontWeight: false, fontVariant: false }\n
\t\t\t\tvar ff = \'\';\n
\t\t\t\tfor (var i=0; i<d.length; i++) {\n
\t\t\t\t\tif (!set.fontStyle && that.Styles.indexOf(d[i]) != -1) { if (d[i] != \'inherit\') f.fontStyle = d[i]; set.fontStyle = true; }\n
\t\t\t\t\telse if (!set.fontVariant && that.Variants.indexOf(d[i]) != -1) { if (d[i] != \'inherit\') f.fontVariant = d[i]; set.fontStyle = set.fontVariant = true;\t}\n
\t\t\t\t\telse if (!set.fontWeight && that.Weights.indexOf(d[i]) != -1) {\tif (d[i] != \'inherit\') f.fontWeight = d[i]; set.fontStyle = set.fontVariant = set.fontWeight = true; }\n
\t\t\t\t\telse if (!set.fontSize) { if (d[i] != \'inherit\') f.fontSize = d[i].split(\'/\')[0]; set.fontStyle = set.fontVariant = set.fontWeight = set.fontSize = true; }\n
\t\t\t\t\telse { if (d[i] != \'inherit\') ff += d[i]; }\n
\t\t\t\t} if (ff != \'\') f.fontFamily = ff;\n
\t\t\t\treturn f;\n
\t\t\t}\n
\t\t});\n
\t\t\n
\t\t// points and paths\n
\t\tsvg.ToNumberArray = function(s) {\n
\t\t\tvar a = svg.trim(svg.compressSpaces((s || \'\').replace(/,/g, \' \'))).split(\' \');\n
\t\t\tfor (var i=0; i<a.length; i++) {\n
\t\t\t\ta[i] = parseFloat(a[i]);\n
\t\t\t}\n
\t\t\treturn a;\n
\t\t}\t\t\n
\t\tsvg.Point = function(x, y) {\n
\t\t\tthis.x = x;\n
\t\t\tthis.y = y;\n
\t\t\t\n
\t\t\tthis.angleTo = function(p) {\n
\t\t\t\treturn Math.atan2(p.y - this.y, p.x - this.x);\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.applyTransform = function(v) {\n
\t\t\t\tvar xp = this.x * v[0] + this.y * v[2] + v[4];\n
\t\t\t\tvar yp = this.x * v[1] + this.y * v[3] + v[5];\n
\t\t\t\tthis.x = xp;\n
\t\t\t\tthis.y = yp;\n
\t\t\t}\n
\t\t}\n
\t\tsvg.CreatePoint = function(s) {\n
\t\t\tvar a = svg.ToNumberArray(s);\n
\t\t\treturn new svg.Point(a[0], a[1]);\n
\t\t}\n
\t\tsvg.CreatePath = function(s) {\n
\t\t\tvar a = svg.ToNumberArray(s);\n
\t\t\tvar path = [];\n
\t\t\tfor (var i=0; i<a.length; i+=2) {\n
\t\t\t\tpath.push(new svg.Point(a[i], a[i+1]));\n
\t\t\t}\n
\t\t\treturn path;\n
\t\t}\n
\t\t\n
\t\t// bounding box\n
\t\tsvg.BoundingBox = function(x1, y1, x2, y2) { // pass in initial points if you want\n
\t\t\tthis.x1 = Number.NaN;\n
\t\t\tthis.y1 = Number.NaN;\n
\t\t\tthis.x2 = Number.NaN;\n
\t\t\tthis.y2 = Number.NaN;\n
\t\t\t\n
\t\t\tthis.x = function() { return this.x1; }\n
\t\t\tthis.y = function() { return this.y1; }\n
\t\t\tthis.width = function() { return this.x2 - this.x1; }\n
\t\t\tthis.height = function() { return this.y2 - this.y1; }\n
\t\t\t\n
\t\t\tthis.addPoint = function(x, y) {\t\n
\t\t\t\tif (x != null) {\n
\t\t\t\t\tif (isNaN(this.x1) || isNaN(this.x2)) {\n
\t\t\t\t\t\tthis.x1 = x;\n
\t\t\t\t\t\tthis.x2 = x;\n
\t\t\t\t\t}\n
\t\t\t\t\tif (x < this.x1) this.x1 = x;\n
\t\t\t\t\tif (x > this.x2) this.x2 = x;\n
\t\t\t\t}\n
\t\t\t\n
\t\t\t\tif (y != null) {\n
\t\t\t\t\tif (isNaN(this.y1) || isNaN(this.y2)) {\n
\t\t\t\t\t\tthis.y1 = y;\n
\t\t\t\t\t\tthis.y2 = y;\n
\t\t\t\t\t}\n
\t\t\t\t\tif (y < this.y1) this.y1 = y;\n
\t\t\t\t\tif (y > this.y2) this.y2 = y;\n
\t\t\t\t}\n
\t\t\t}\t\t\t\n
\t\t\tthis.addX = function(x) { this.addPoint(x, null); }\n
\t\t\tthis.addY = function(y) { this.addPoint(null, y); }\n
\t\t\t\n
\t\t\tthis.addBoundingBox = function(bb) {\n
\t\t\t\tthis.addPoint(bb.x1, bb.y1);\n
\t\t\t\tthis.addPoint(bb.x2, bb.y2);\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.addQuadraticCurve = function(p0x, p0y, p1x, p1y, p2x, p2y) {\n
\t\t\t\tvar cp1x = p0x + 2/3 * (p1x - p0x); // CP1 = QP0 + 2/3 *(QP1-QP0)\n
\t\t\t\tvar cp1y = p0y + 2/3 * (p1y - p0y); // CP1 = QP0 + 2/3 *(QP1-QP0)\n
\t\t\t\tvar cp2x = cp1x + 1/3 * (p2x - p0x); // CP2 = CP1 + 1/3 *(QP2-QP0)\n
\t\t\t\tvar cp2y = cp1y + 1/3 * (p2y - p0y); // CP2 = CP1 + 1/3 *(QP2-QP0)\n
\t\t\t\tthis.addBezierCurve(p0x, p0y, cp1x, cp2x, cp1y,\tcp2y, p2x, p2y);\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.addBezierCurve = function(p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y) {\n
\t\t\t\t// from http://blog.hackers-cafe.net/2009/06/how-to-calculate-bezier-curves-bounding.html\n
\t\t\t\tvar p0 = [p0x, p0y], p1 = [p1x, p1y], p2 = [p2x, p2y], p3 = [p3x, p3y];\n
\t\t\t\tthis.addPoint(p0[0], p0[1]);\n
\t\t\t\tthis.addPoint(p3[0], p3[1]);\n
\t\t\t\t\n
\t\t\t\tfor (i=0; i<=1; i++) {\n
\t\t\t\t\tvar f = function(t) { \n
\t\t\t\t\t\treturn Math.pow(1-t, 3) * p0[i]\n
\t\t\t\t\t\t+ 3 * Math.pow(1-t, 2) * t * p1[i]\n
\t\t\t\t\t\t+ 3 * (1-t) * Math.pow(t, 2) * p2[i]\n
\t\t\t\t\t\t+ Math.pow(t, 3) * p3[i];\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\tvar b = 6 * p0[i] - 12 * p1[i] + 6 * p2[i];\n
\t\t\t\t\tvar a = -3 * p0[i] + 9 * p1[i] - 9 * p2[i] + 3 * p3[i];\n
\t\t\t\t\tvar c = 3 * p1[i] - 3 * p0[i];\n
\t\t\t\t\t\n
\t\t\t\t\tif (a == 0) {\n
\t\t\t\t\t\tif (b == 0) continue;\n
\t\t\t\t\t\tvar t = -c / b;\n
\t\t\t\t\t\tif (0 < t && t < 1) {\n
\t\t\t\t\t\t\tif (i == 0) this.addX(f(t));\n
\t\t\t\t\t\t\tif (i == 1) this.addY(f(t));\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tcontinue;\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\tvar b2ac = Math.pow(b, 2) - 4 * c * a;\n
\t\t\t\t\tif (b2ac < 0) continue;\n
\t\t\t\t\tvar t1 = (-b + Math.sqrt(b2ac)) / (2 * a);\n
\t\t\t\t\tif (0 < t1 && t1 < 1) {\n
\t\t\t\t\t\tif (i == 0) this.addX(f(t1));\n
\t\t\t\t\t\tif (i == 1) this.addY(f(t1));\n
\t\t\t\t\t}\n
\t\t\t\t\tvar t2 = (-b - Math.sqrt(b2ac)) / (2 * a);\n
\t\t\t\t\tif (0 < t2 && t2 < 1) {\n
\t\t\t\t\t\tif (i == 0) this.addX(f(t2));\n
\t\t\t\t\t\tif (i == 1) this.addY(f(t2));\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.isPointInBox = function(x, y) {\n
\t\t\t\treturn (this.x1 <= x && x <= this.x2 && this.y1 <= y && y <= this.y2);\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.addPoint(x1, y1);\n
\t\t\tthis.addPoint(x2, y2);\n
\t\t}\n
\t\t\n
\t\t// transforms\n
\t\tsvg.Transform = function(v) {\t\n
\t\t\tvar that = this;\n
\t\t\tthis.Type = {}\n
\t\t\n
\t\t\t// translate\n
\t\t\tthis.Type.translate = function(s) {\n
\t\t\t\tthis.p = svg.CreatePoint(s);\t\t\t\n
\t\t\t\tthis.apply = function(ctx) {\n
\t\t\t\t\tctx.translate(this.p.x || 0.0, this.p.y || 0.0);\n
\t\t\t\t}\n
\t\t\t\tthis.applyToPoint = function(p) {\n
\t\t\t\t\tp.applyTransform([1, 0, 0, 1, this.p.x || 0.0, this.p.y || 0.0]);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\t// rotate\n
\t\t\tthis.Type.rotate = function(s) {\n
\t\t\t\tvar a = svg.ToNumberArray(s);\n
\t\t\t\tthis.angle = new svg.Property(\'angle\', a[0]);\n
\t\t\t\tthis.cx = a[1] || 0;\n
\t\t\t\tthis.cy = a[2] || 0;\n
\t\t\t\tthis.apply = function(ctx) {\n
\t\t\t\t\tctx.translate(this.cx, this.cy);\n
\t\t\t\t\tctx.rotate(this.angle.Angle.toRadians());\n
\t\t\t\t\tctx.translate(-this.cx, -this.cy);\n
\t\t\t\t}\n
\t\t\t\tthis.applyToPoint = function(p) {\n
\t\t\t\t\tvar a = this.angle.Angle.toRadians();\n
\t\t\t\t\tp.applyTransform([1, 0, 0, 1, this.p.x || 0.0, this.p.y || 0.0]);\n
\t\t\t\t\tp.applyTransform([Math.cos(a), Math.sin(a), -Math.sin(a), Math.cos(a), 0, 0]);\n
\t\t\t\t\tp.applyTransform([1, 0, 0, 1, -this.p.x || 0.0, -this.p.y || 0.0]);\n
\t\t\t\t}\t\t\t\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.Type.scale = function(s) {\n
\t\t\t\tthis.p = svg.CreatePoint(s);\n
\t\t\t\tthis.apply = function(ctx) {\n
\t\t\t\t\tctx.scale(this.p.x || 1.0, this.p.y || this.p.x || 1.0);\n
\t\t\t\t}\n
\t\t\t\tthis.applyToPoint = function(p) {\n
\t\t\t\t\tp.applyTransform([this.p.x || 0.0, 0, 0, this.p.y || 0.0, 0, 0]);\n
\t\t\t\t}\t\t\t\t\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.Type.matrix = function(s) {\n
\t\t\t\tthis.m = svg.ToNumberArray(s);\n
\t\t\t\tthis.apply = function(ctx) {\n
\t\t\t\t\tctx.transform(this.m[0], this.m[1], this.m[2], this.m[3], this.m[4], this.m[5]);\n
\t\t\t\t}\n
\t\t\t\tthis.applyToPoint = function(p) {\n
\t\t\t\t\tp.applyTransform(this.m);\n
\t\t\t\t}\t\t\t\t\t\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.Type.SkewBase = function(s) {\n
\t\t\t\tthis.base = that.Type.matrix;\n
\t\t\t\tthis.base(s);\n
\t\t\t\tthis.angle = new svg.Property(\'angle\', s);\n
\t\t\t}\n
\t\t\tthis.Type.SkewBase.prototype = new this.Type.matrix;\n
\t\t\t\n
\t\t\tthis.Type.skewX = function(s) {\n
\t\t\t\tthis.base = that.Type.SkewBase;\n
\t\t\t\tthis.base(s);\n
\t\t\t\tthis.m = [1, 0, Math.tan(this.angle.Angle.toRadians()), 1, 0, 0];\n
\t\t\t}\n
\t\t\tthis.Type.skewX.prototype = new this.Type.SkewBase;\n
\t\t\t\n
\t\t\tthis.Type.skewY = function(s) {\n
\t\t\t\tthis.base = that.Type.SkewBase;\n
\t\t\t\tthis.base(s);\n
\t\t\t\tthis.m = [1, Math.tan(this.angle.Angle.toRadians()), 0, 1, 0, 0];\n
\t\t\t}\n
\t\t\tthis.Type.skewY.prototype = new this.Type.SkewBase;\n
\t\t\n
\t\t\tthis.transforms = [];\n
\t\t\t\n
\t\t\tthis.apply = function(ctx) {\n
\t\t\t\tfor (var i=0; i<this.transforms.length; i++) {\n
\t\t\t\t\tthis.transforms[i].apply(ctx);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.applyToPoint = function(p) {\n
\t\t\t\tfor (var i=0; i<this.transforms.length; i++) {\n
\t\t\t\t\tthis.transforms[i].applyToPoint(p);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\tvar data = svg.trim(svg.compressSpaces(v)).split(/\\s(?=[a-z])/);\n
\t\t\tfor (var i=0; i<data.length; i++) {\n
\t\t\t\tvar type = data[i].split(\'(\')[0];\n
\t\t\t\tvar s = data[i].split(\'(\')[1].replace(\')\',\'\');\n
\t\t\t\tvar transform = new this.Type[type](s);\n
\t\t\t\tthis.transforms.push(transform);\n
\t\t\t}\n
\t\t}\n
\t\t\n
\t\t// aspect ratio\n
\t\tsvg.AspectRatio = function(ctx, aspectRatio, width, desiredWidth, height, desiredHeight, minX, minY, refX, refY) {\n
\t\t\t// aspect ratio - http://www.w3.org/TR/SVG/coords.html#PreserveAspectRatioAttribute\n
\t\t\taspectRatio = svg.compressSpaces(aspectRatio);\n
\t\t\taspectRatio = aspectRatio.replace(/^defer\\s/,\'\'); // ignore defer\n
\t\t\tvar align = aspectRatio.split(\' \')[0] || \'xMidYMid\';\n
\t\t\tvar meetOrSlice = aspectRatio.split(\' \')[1] || \'meet\';\t\t\t\t\t\n
\t\n
\t\t\t// calculate scale\n
\t\t\tvar scaleX = width / desiredWidth;\n
\t\t\tvar scaleY = height / desiredHeight;\n
\t\t\tvar scaleMin = Math.min(scaleX, scaleY);\n
\t\t\tvar scaleMax = Math.max(scaleX, scaleY);\n
\t\t\tif (meetOrSlice == \'meet\') { desiredWidth *= scaleMin; desiredHeight *= scaleMin; }\n
\t\t\tif (meetOrSlice == \'slice\') { desiredWidth *= scaleMax; desiredHeight *= scaleMax; }\t\n
\t\t\t\n
\t\t\trefX = new svg.Property(\'refX\', refX);\n
\t\t\trefY = new svg.Property(\'refY\', refY);\n
\t\t\tif (refX.hasValue() && refY.hasValue()) {\t\t\t\t\n
\t\t\t\tctx.translate(-scaleMin * refX.Length.toPixels(\'x\'), -scaleMin * refY.Length.toPixels(\'y\'));\n
\t\t\t} \n
\t\t\telse {\t\t\t\t\t\n
\t\t\t\t// align\n
\t\t\t\tif (align.match(/^xMid/) && ((meetOrSlice == \'meet\' && scaleMin == scaleY) || (meetOrSlice == \'slice\' && scaleMax == scaleY))) ctx.translate(width / 2.0 - desiredWidth / 2.0, 0); \n
\t\t\t\tif (align.match(/YMid$/) && ((meetOrSlice == \'meet\' && scaleMin == scaleX) || (meetOrSlice == \'slice\' && scaleMax == scaleX))) ctx.translate(0, height / 2.0 - desiredHeight / 2.0); \n
\t\t\t\tif (align.match(/^xMax/) && ((meetOrSlice == \'meet\' && scaleMin == scaleY) || (meetOrSlice == \'slice\' && scaleMax == scaleY))) ctx.translate(width - desiredWidth, 0); \n
\t\t\t\tif (align.match(/YMax$/) && ((meetOrSlice == \'meet\' && scaleMin == scaleX) || (meetOrSlice == \'slice\' && scaleMax == scaleX))) ctx.translate(0, height - desiredHeight); \n
\t\t\t}\n
\t\t\t\n
\t\t\t// scale\n
\t\t\tif (align == \'none\') ctx.scale(scaleX, scaleY);\n
\t\t\telse if (meetOrSlice == \'meet\') ctx.scale(scaleMin, scaleMin); \n
\t\t\telse if (meetOrSlice == \'slice\') ctx.scale(scaleMax, scaleMax); \t\n
\t\t\t\n
\t\t\t// translate\n
\t\t\tctx.translate(minX == null ? 0 : -minX, minY == null ? 0 : -minY);\t\t\t\n
\t\t}\n
\t\t\n
\t\t// elements\n
\t\tsvg.Element = {}\n
\t\t\n
\t\tsvg.Element.ElementBase = function(node) {\t\n
\t\t\tthis.attributes = {};\n
\t\t\tthis.styles = {};\n
\t\t\tthis.children = [];\n
\t\t\t\n
\t\t\t// get or create attribute\n
\t\t\tthis.attribute = function(name, createIfNotExists) {\n
\t\t\t\tvar a = this.attributes[name];\n
\t\t\t\tif (a != null) return a;\n
\t\t\t\t\t\t\t\n
\t\t\t\ta = new svg.Property(name, \'\');\n
\t\t\t\tif (createIfNotExists == true) this.attributes[name] = a;\n
\t\t\t\treturn a;\n
\t\t\t}\n
\t\t\t\n
\t\t\t// get or create style, crawls up node tree\n
\t\t\tthis.style = function(name, createIfNotExists) {\n
\t\t\t\tvar s = this.styles[name];\n
\t\t\t\tif (s != null) return s;\n
\t\t\t\t\n
\t\t\t\tvar a = this.attribute(name);\n
\t\t\t\tif (a != null && a.hasValue()) {\n
\t\t\t\t\treturn a;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tvar p = this.parent;\n
\t\t\t\tif (p != null) {\n
\t\t\t\t\tvar ps = p.style(name);\n
\t\t\t\t\tif (ps != null && ps.hasValue()) {\n
\t\t\t\t\t\treturn ps;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\ts = new svg.Property(name, \'\');\n
\t\t\t\tif (createIfNotExists == true) this.styles[name] = s;\n
\t\t\t\treturn s;\n
\t\t\t}\n
\t\t\t\n
\t\t\t// base render\n
\t\t\tthis.render = function(ctx) {\n
\t\t\t\t// don\'t render display=none\n
\t\t\t\tif (this.style(\'display\').value == \'none\') return;\n
\t\t\t\t\n
\t\t\t\t// don\'t render visibility=hidden\n
\t\t\t\tif (this.attribute(\'visibility\').value == \'hidden\') return;\n
\t\t\t\n
\t\t\t\tctx.save();\n
\t\t\t\t\tthis.setContext(ctx);\n
\t\t\t\t\t\t// mask\n
\t\t\t\t\t\tif (this.attribute(\'mask\').hasValue()) {\n
\t\t\t\t\t\t\tvar mask = this.attribute(\'mask\').Definition.getDefinition();\n
\t\t\t\t\t\t\tif (mask != null) mask.apply(ctx, this);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\telse if (this.style(\'filter\').hasValue()) {\n
\t\t\t\t\t\t\tvar filter = this.style(\'filter\').Definition.getDefinition();\n
\t\t\t\t\t\t\tif (filter != null) filter.apply(ctx, this);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\telse this.renderChildren(ctx);\t\t\t\t\n
\t\t\t\t\tthis.clearContext(ctx);\n
\t\t\t\tctx.restore();\n
\t\t\t}\n
\t\t\t\n
\t\t\t// base set context\n
\t\t\tthis.setContext = function(ctx) {\n
\t\t\t\t// OVERRIDE ME!\n
\t\t\t}\n
\t\t\t\n
\t\t\t// base clear context\n
\t\t\tthis.clearContext = function(ctx) {\n
\t\t\t\t// OVERRIDE ME!\n
\t\t\t}\t\t\t\n
\t\t\t\n
\t\t\t// base render children\n
\t\t\tthis.renderChildren = function(ctx) {\n
\t\t\t\tfor (var i=0; i<this.children.length; i++) {\n
\t\t\t\t\tthis.children[i].render(ctx);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.addChild = function(childNode, create) {\n
\t\t\t\tvar child = childNode;\n
\t\t\t\tif (create) child = svg.CreateElement(childNode);\n
\t\t\t\tchild.parent = this;\n
\t\t\t\tthis.children.push(child);\t\t\t\n
\t\t\t}\n
\t\t\t\t\n
\t\t\tif (node != null && node.nodeType == 1) { //ELEMENT_NODE\n
\t\t\t\t// add children\n
\t\t\t\tfor (var i=0; i<node.childNodes.length; i++) {\n
\t\t\t\t\tvar childNode = node.childNodes[i];\n
\t\t\t\t\tif (childNode.nodeType == 1) this.addChild(childNode, true); //ELEMENT_NODE\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t// add attributes\n
\t\t\t\tfor (var i=0; i<node.attributes.length; i++) {\n
\t\t\t\t\tvar attribute = node.attributes[i];\n
\t\t\t\t\tthis.attributes[attribute.nodeName] = new svg.Property(attribute.nodeName, attribute.nodeValue);\n
\t\t\t\t}\n
\t\t\t\t\t\t\t\t\t\t\n
\t\t\t\t// add tag styles\n
\t\t\t\tvar styles = svg.Styles[node.nodeName];\n
\t\t\t\tif (styles != null) {\n
\t\t\t\t\tfor (var name in styles) {\n
\t\t\t\t\t\tthis.styles[name] = styles[name];\n
\t\t\t\t\t}\n
\t\t\t\t}\t\t\t\t\t\n
\t\t\t\t\n
\t\t\t\t// add class styles\n
\t\t\t\tif (this.attribute(\'class\').hasValue()) {\n
\t\t\t\t\tvar classes = svg.compressSpaces(this.attribute(\'class\').value).split(\' \');\n
\t\t\t\t\tfor (var j=0; j<classes.length; j++) {\n
\t\t\t\t\t\tstyles = svg.Styles[\'.\'+classes[j]];\n
\t\t\t\t\t\tif (styles != null) {\n
\t\t\t\t\t\t\tfor (var name in styles) {\n
\t\t\t\t\t\t\t\tthis.styles[name] = styles[name];\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tstyles = svg.Styles[node.nodeName+\'.\'+classes[j]];\n
\t\t\t\t\t\tif (styles != null) {\n
\t\t\t\t\t\t\tfor (var name in styles) {\n
\t\t\t\t\t\t\t\tthis.styles[name] = styles[name];\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t// add inline styles\n
\t\t\t\tif (this.attribute(\'style\').hasValue()) {\n
\t\t\t\t\tvar styles = this.attribute(\'style\').value.split(\';\');\n
\t\t\t\t\tfor (var i=0; i<styles.length; i++) {\n
\t\t\t\t\t\tif (svg.trim(styles[i]) != \'\') {\n
\t\t\t\t\t\t\tvar style = styles[i].split(\':\');\n
\t\t\t\t\t\t\tvar name = svg.trim(style[0]);\n
\t\t\t\t\t\t\tvar value = svg.trim(style[1]);\n
\t\t\t\t\t\t\tthis.styles[name] = new svg.Property(name, value);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\t\n
\n
\t\t\t\t// add id\n
\t\t\t\tif (this.attribute(\'id\').hasValue()) {\n
\t\t\t\t\tif (svg.Definitions[this.attribute(\'id\').value] == null) {\n
\t\t\t\t\t\tsvg.Definitions[this.attribute(\'id\').value] = this;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t\t\n
\t\tsvg.Element.RenderedElementBase = function(node) {\n
\t\t\tthis.base = svg.Element.ElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.setContext = function(ctx) {\n
\t\t\t\t// fill\n
\t\t\t\tif (this.style(\'fill\').Definition.isUrl()) {\n
\t\t\t\t\tvar fs = this.style(\'fill\').Definition.getFillStyle(this);\n
\t\t\t\t\tif (fs != null) ctx.fillStyle = fs;\n
\t\t\t\t}\n
\t\t\t\telse if (this.style(\'fill\').hasValue()) {\n
\t\t\t\t\tvar fillStyle = this.style(\'fill\');\n
\t\t\t\t\tif (this.style(\'fill-opacity\').hasValue()) fillStyle = fillStyle.Color.addOpacity(this.style(\'fill-opacity\').value);\n
\t\t\t\t\tctx.fillStyle = (fillStyle.value == \'none\' ? \'rgba(0,0,0,0)\' : fillStyle.value);\n
\t\t\t\t}\n
\t\t\t\t\t\t\t\t\t\n
\t\t\t\t// stroke\n
\t\t\t\tif (this.style(\'stroke\').Definition.isUrl()) {\n
\t\t\t\t\tvar fs = this.style(\'stroke\').Definition.getFillStyle(this);\n
\t\t\t\t\tif (fs != null) ctx.strokeStyle = fs;\n
\t\t\t\t}\n
\t\t\t\telse if (this.style(\'stroke\').hasValue()) {\n
\t\t\t\t\tvar strokeStyle = this.style(\'stroke\');\n
\t\t\t\t\tif (this.style(\'stroke-opacity\').hasValue()) strokeStyle = strokeStyle.Color.addOpacity(this.style(\'stroke-opacity\').value);\n
\t\t\t\t\tctx.strokeStyle = (strokeStyle.value == \'none\' ? \'rgba(0,0,0,0)\' : strokeStyle.value);\n
\t\t\t\t}\n
\t\t\t\tif (this.style(\'stroke-width\').hasValue()) ctx.lineWidth = this.style(\'stroke-width\').Length.toPixels();\n
\t\t\t\tif (this.style(\'stroke-linecap\').hasValue()) ctx.lineCap = this.style(\'stroke-linecap\').value;\n
\t\t\t\tif (this.style(\'stroke-linejoin\').hasValue()) ctx.lineJoin = this.style(\'stroke-linejoin\').value;\n
\t\t\t\tif (this.style(\'stroke-miterlimit\').hasValue()) ctx.miterLimit = this.style(\'stroke-miterlimit\').value;\n
\n
\t\t\t\t// font\n
\t\t\t\tif (typeof(ctx.font) != \'undefined\') {\n
\t\t\t\t\tctx.font = svg.Font.CreateFont( \n
\t\t\t\t\t\tthis.style(\'font-style\').value, \n
\t\t\t\t\t\tthis.style(\'font-variant\').value, \n
\t\t\t\t\t\tthis.style(\'font-weight\').value, \n
\t\t\t\t\t\tthis.style(\'font-size\').hasValue() ? this.style(\'font-size\').Length.toPixels() + \'px\' : \'\', \n
\t\t\t\t\t\tthis.style(\'font-family\').value).toString();\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t// transform\n
\t\t\t\tif (this.attribute(\'transform\').hasValue()) { \n
\t\t\t\t\tvar transform = new svg.Transform(this.attribute(\'transform\').value);\n
\t\t\t\t\ttransform.apply(ctx);\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t// clip\n
\t\t\t\tif (this.attribute(\'clip-path\').hasValue()) {\n
\t\t\t\t\tvar clip = this.attribute(\'clip-path\').Definition.getDefinition();\n
\t\t\t\t\tif (clip != null) clip.apply(ctx);\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t// opacity\n
\t\t\t\tif (this.style(\'opacity\').hasValue()) {\n
\t\t\t\t\tctx.globalAlpha = this.style(\'opacity\').numValue();\n
\t\t\t\t}\n
\t\t\t}\t\t\n
\t\t}\n
\t\tsvg.Element.RenderedElementBase.prototype = new svg.Element.ElementBase;\n
\t\t\n
\t\tsvg.Element.PathElementBase = function(node) {\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.path = function(ctx) {\n
\t\t\t\tif (ctx != null) ctx.beginPath();\n
\t\t\t\treturn new svg.BoundingBox();\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.renderChildren = function(ctx) {\n
\t\t\t\tthis.path(ctx);\n
\t\t\t\tsvg.Mouse.checkPath(this, ctx);\n
\t\t\t\tif (ctx.fillStyle != \'\') ctx.fill();\n
\t\t\t\tif (ctx.strokeStyle != \'\') ctx.stroke();\n
\t\t\t\t\n
\t\t\t\tvar markers = this.getMarkers();\n
\t\t\t\tif (markers != null) {\n
\t\t\t\t\tif (this.style(\'marker-start\').Definition.isUrl()) {\n
\t\t\t\t\t\tvar marker = this.style(\'marker-start\').Definition.getDefinition();\n
\t\t\t\t\t\tmarker.render(ctx, markers[0][0], markers[0][1]);\n
\t\t\t\t\t}\n
\t\t\t\t\tif (this.style(\'marker-mid\').Definition.isUrl()) {\n
\t\t\t\t\t\tvar marker = this.style(\'marker-mid\').Definition.getDefinition();\n
\t\t\t\t\t\tfor (var i=1;i<markers.length-1;i++) {\n
\t\t\t\t\t\t\tmarker.render(ctx, markers[i][0], markers[i][1]);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\tif (this.style(\'marker-end\').Definition.isUrl()) {\n
\t\t\t\t\t\tvar marker = this.style(\'marker-end\').Definition.getDefinition();\n
\t\t\t\t\t\tmarker.render(ctx, markers[markers.length-1][0], markers[markers.length-1][1]);\n
\t\t\t\t\t}\n
\t\t\t\t}\t\t\t\t\t\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.getBoundingBox = function() {\n
\t\t\t\treturn this.path();\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.getMarkers = function() {\n
\t\t\t\treturn null;\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.PathElementBase.prototype = new svg.Element.RenderedElementBase;\n
\t\t\n
\t\t// svg element\n
\t\tsvg.Element.svg = function(node) {\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.baseClearContext = this.clearContext;\n
\t\t\tthis.clearContext = function(ctx) {\n
\t\t\t\tthis.baseClearContext(ctx);\n
\t\t\t\tsvg.ViewPort.RemoveCurrent();\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.baseSetContext = this.setContext;\n
\t\t\tthis.setContext = function(ctx) {\n
\t\t\t\t// initial values\n
\t\t\t\tctx.strokeStyle = \'rgba(0,0,0,0)\';\n
\t\t\t\tctx.lineCap = \'butt\';\n
\t\t\t\tctx.lineJoin = \'miter\';\n
\t\t\t\tctx.miterLimit = 4;\t\t\t\n
\t\t\t\n
\t\t\t\tthis.baseSetContext(ctx);\n
\t\t\t\t\n
\t\t\t\t// create new view port\n
\t\t\t\tif (this.attribute(\'x\').hasValue() && this.attribute(\'y\').hasValue()) {\n
\t\t\t\t\tctx.translate(this.attribute(\'x\').Length.toPixels(\'x\'), this.attribute(\'y\').Length.toPixels(\'y\'));\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tvar width = svg.ViewPort.width();\n
\t\t\t\tvar height = svg.ViewPort.height();\n
\t\t\t\tif (typeof(this.root) == \'undefined\' && this.attribute(\'width\').hasValue() && this.attribute(\'height\').hasValue()) {\n
\t\t\t\t\twidth = this.attribute(\'width\').Length.toPixels(\'x\');\n
\t\t\t\t\theight = this.attribute(\'height\').Length.toPixels(\'y\');\n
\t\t\t\t\t\n
\t\t\t\t\tvar x = 0;\n
\t\t\t\t\tvar y = 0;\n
\t\t\t\t\tif (this.attribute(\'refX\').hasValue() && this.attribute(\'refY\').hasValue()) {\n
\t\t\t\t\t\tx = -this.attribute(\'refX\').Length.toPixels(\'x\');\n
\t\t\t\t\t\ty = -this.attribute(\'refY\').Length.toPixels(\'y\');\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\tctx.beginPath();\n
\t\t\t\t\tctx.moveTo(x, y);\n
\t\t\t\t\tctx.lineTo(width, y);\n
\t\t\t\t\tctx.lineTo(width, height);\n
\t\t\t\t\tctx.lineTo(x, height);\n
\t\t\t\t\tctx.closePath();\n
\t\t\t\t\tctx.clip();\n
\t\t\t\t}\n
\t\t\t\tsvg.ViewPort.SetCurrent(width, height);\t\n
\t\t\t\t\t\t\n
\t\t\t\t// viewbox\n
\t\t\t\tif (this.attribute(\'viewBox\').hasValue()) {\t\t\t\t\n
\t\t\t\t\tvar viewBox = svg.ToNumberArray(this.attribute(\'viewBox\').value);\n
\t\t\t\t\tvar minX = viewBox[0];\n
\t\t\t\t\tvar minY = viewBox[1];\n
\t\t\t\t\twidth = viewBox[2];\n
\t\t\t\t\theight = viewBox[3];\n
\t\t\t\t\t\n
\t\t\t\t\tsvg.AspectRatio(ctx,\n
\t\t\t\t\t\t\t\t\tthis.attribute(\'preserveAspectRatio\').value, \n
\t\t\t\t\t\t\t\t\tsvg.ViewPort.width(), \n
\t\t\t\t\t\t\t\t\twidth,\n
\t\t\t\t\t\t\t\t\tsvg.ViewPort.height(),\n
\t\t\t\t\t\t\t\t\theight,\n
\t\t\t\t\t\t\t\t\tminX,\n
\t\t\t\t\t\t\t\t\tminY,\n
\t\t\t\t\t\t\t\t\tthis.attribute(\'refX\').value,\n
\t\t\t\t\t\t\t\t\tthis.attribute(\'refY\').value);\n
\t\t\t\t\t\t\t\t\t\t\n
\t\t\t\t\tsvg.ViewPort.RemoveCurrent();\t\n
\t\t\t\t\tsvg.ViewPort.SetCurrent(viewBox[2], viewBox[3]);\t\t\t\t\t\t\n
\t\t\t\t}\t\t\t\t\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.svg.prototype = new svg.Element.RenderedElementBase;\n
\n
\t\t// rect element\n
\t\tsvg.Element.rect = function(node) {\n
\t\t\tthis.base = svg.Element.PathElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.path = function(ctx) {\n
\t\t\t\tvar x = this.attribute(\'x\').Length.toPixels(\'x\');\n
\t\t\t\tvar y = this.attribute(\'y\').Length.toPixels(\'y\');\n
\t\t\t\tvar width = this.attribute(\'width\').Length.toPixels(\'x\');\n
\t\t\t\tvar height = this.attribute(\'height\').Length.toPixels(\'y\');\n
\t\t\t\tvar rx = this.attribute(\'rx\').Length.toPixels(\'x\');\n
\t\t\t\tvar ry = this.attribute(\'ry\').Length.toPixels(\'y\');\n
\t\t\t\tif (this.attribute(\'rx\').hasValue() && !this.attribute(\'ry\').hasValue()) ry = rx;\n
\t\t\t\tif (this.attribute(\'ry\').hasValue() && !this.attribute(\'rx\').hasValue()) rx = ry;\n
\t\t\t\t\n
\t\t\t\tif (ctx != null) {\n
\t\t\t\t\tctx.beginPath();\n
\t\t\t\t\tctx.moveTo(x + rx, y);\n
\t\t\t\t\tctx.lineTo(x + width - rx, y);\n
\t\t\t\t\tctx.quadraticCurveTo(x + width, y, x + width, y + ry)\n
\t\t\t\t\tctx.lineTo(x + width, y + height - ry);\n
\t\t\t\t\tctx.quadraticCurveTo(x + width, y + height, x + width - rx, y + height)\n
\t\t\t\t\tctx.lineTo(x + rx, y + height);\n
\t\t\t\t\tctx.quadraticCurveTo(x, y + height, x, y + height - ry)\n
\t\t\t\t\tctx.lineTo(x, y + ry);\n
\t\t\t\t\tctx.quadraticCurveTo(x, y, x + rx, y)\n
\t\t\t\t\tctx.closePath();\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\treturn new svg.BoundingBox(x, y, x + width, y + height);\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.rect.prototype = new svg.Element.PathElementBase;\n
\t\t\n
\t\t// circle element\n
\t\tsvg.Element.circle = function(node) {\n
\t\t\tthis.base = svg.Element.PathElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.path = function(ctx) {\n
\t\t\t\tvar cx = this.attribute(\'cx\').Length.toPixels(\'x\');\n
\t\t\t\tvar cy = this.attribute(\'cy\').Length.toPixels(\'y\');\n
\t\t\t\tvar r = this.attribute(\'r\').Length.toPixels();\n
\t\t\t\n
\t\t\t\tif (ctx != null) {\n
\t\t\t\t\tctx.beginPath();\n
\t\t\t\t\tctx.arc(cx, cy, r, 0, Math.PI * 2, true); \n
\t\t\t\t\tctx.closePath();\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\treturn new svg.BoundingBox(cx - r, cy - r, cx + r, cy + r);\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.circle.prototype = new svg.Element.PathElementBase;\t\n
\n
\t\t// ellipse element\n
\t\tsvg.Element.ellipse = function(node) {\n
\t\t\tthis.base = svg.Element.PathElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.path = function(ctx) {\n
\t\t\t\tvar KAPPA = 4 * ((Math.sqrt(2) - 1) / 3);\n
\t\t\t\tvar rx = this.attribute(\'rx\').Length.toPixels(\'x\');\n
\t\t\t\tvar ry = this.attribute(\'ry\').Length.toPixels(\'y\');\n
\t\t\t\tvar cx = this.attribute(\'cx\').Length.toPixels(\'x\');\n
\t\t\t\tvar cy = this.attribute(\'cy\').Length.toPixels(\'y\');\n
\t\t\t\t\n
\t\t\t\tif (ctx != null) {\n
\t\t\t\t\tctx.beginPath();\n
\t\t\t\t\tctx.moveTo(cx, cy - ry);\n
\t\t\t\t\tctx.bezierCurveTo(cx + (KAPPA * rx), cy - ry,  cx + rx, cy - (KAPPA * ry), cx + rx, cy);\n
\t\t\t\t\tctx.bezierCurveTo(cx + rx, cy + (KAPPA * ry), cx + (KAPPA * rx), cy + ry, cx, cy + ry);\n
\t\t\t\t\tctx.bezierCurveTo(cx - (KAPPA * rx), cy + ry, cx - rx, cy + (KAPPA * ry), cx - rx, cy);\n
\t\t\t\t\tctx.bezierCurveTo(cx - rx, cy - (KAPPA * ry), cx - (KAPPA * rx), cy - ry, cx, cy - ry);\n
\t\t\t\t\tctx.closePath();\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\treturn new svg.BoundingBox(cx - rx, cy - ry, cx + rx, cy + ry);\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.ellipse.prototype = new svg.Element.PathElementBase;\t\t\t\n
\t\t\n
\t\t// line element\n
\t\tsvg.Element.line = function(node) {\n
\t\t\tthis.base = svg.Element.PathElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.getPoints = function() {\n
\t\t\t\treturn [\n
\t\t\t\t\tnew svg.Point(this.attribute(\'x1\').Length.toPixels(\'x\'), this.attribute(\'y1\').Length.toPixels(\'y\')),\n
\t\t\t\t\tnew svg.Point(this.attribute(\'x2\').Length.toPixels(\'x\'), this.attribute(\'y2\').Length.toPixels(\'y\'))];\n
\t\t\t}\n
\t\t\t\t\t\t\t\t\n
\t\t\tthis.path = function(ctx) {\n
\t\t\t\tvar points = this.getPoints();\n
\t\t\t\t\n
\t\t\t\tif (ctx != null) {\n
\t\t\t\t\tctx.beginPath();\n
\t\t\t\t\tctx.moveTo(points[0].x, points[0].y);\n
\t\t\t\t\tctx.lineTo(points[1].x, points[1].y);\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\treturn new svg.BoundingBox(points[0].x, points[0].y, points[1].x, points[1].y);\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.getMarkers = function() {\n
\t\t\t\tvar points = this.getPoints();\t\n
\t\t\t\tvar a = points[0].angleTo(points[1]);\n
\t\t\t\treturn [[points[0], a], [points[1], a]];\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.line.prototype = new svg.Element.PathElementBase;\t\t\n
\t\t\t\t\n
\t\t// polyline element\n
\t\tsvg.Element.polyline = function(node) {\n
\t\t\tthis.base = svg.Element.PathElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.points = svg.CreatePath(this.attribute(\'points\').value);\n
\t\t\tthis.path = function(ctx) {\n
\t\t\t\tvar bb = new svg.BoundingBox(this.points[0].x, this.points[0].y);\n
\t\t\t\tif (ctx != null) {\n
\t\t\t\t\tctx.beginPath();\n
\t\t\t\t\tctx.moveTo(this.points[0].x, this.points[0].y);\n
\t\t\t\t}\n
\t\t\t\tfor (var i=1; i<this.points.length; i++) {\n
\t\t\t\t\tbb.addPoint(this.points[i].x, this.points[i].y);\n
\t\t\t\t\tif (ctx != null) ctx.lineTo(this.points[i].x, this.points[i].y);\n
\t\t\t\t}\n
\t\t\t\treturn bb;\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.getMarkers = function() {\n
\t\t\t\tvar markers = [];\n
\t\t\t\tfor (var i=0; i<this.points.length - 1; i++) {\n
\t\t\t\t\tmarkers.push([this.points[i], this.points[i].angleTo(this.points[i+1])]);\n
\t\t\t\t}\n
\t\t\t\tmarkers.push([this.points[this.points.length-1], markers[markers.length-1][1]]);\n
\t\t\t\treturn markers;\n
\t\t\t}\t\t\t\n
\t\t}\n
\t\tsvg.Element.polyline.prototype = new svg.Element.PathElementBase;\t\t\t\t\n
\t\t\t\t\n
\t\t// polygon element\n
\t\tsvg.Element.polygon = function(node) {\n
\t\t\tthis.base = svg.Element.polyline;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.basePath = this.path;\n
\t\t\tthis.path = function(ctx) {\n
\t\t\t\tvar bb = this.basePath(ctx);\n
\t\t\t\tif (ctx != null) {\n
\t\t\t\t\tctx.lineTo(this.points[0].x, this.points[0].y);\n
\t\t\t\t\tctx.closePath();\n
\t\t\t\t}\n
\t\t\t\treturn bb;\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.polygon.prototype = new svg.Element.polyline;\n
\n
\t\t// path element\n
\t\tsvg.Element.path = function(node) {\n
\t\t\tthis.base = svg.Element.PathElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\t\t\n
\t\t\tvar d = this.attribute(\'d\').value;\n
\t\t\t// TODO: convert to real lexer based on http://www.w3.org/TR/SVG11/paths.html#PathDataBNF\n
\t\t\td = d.replace(/,/gm,\' \'); // get rid of all commas\n
\t\t\td = d.replace(/([MmZzLlHhVvCcSsQqTtAa])([MmZzLlHhVvCcSsQqTtAa])/gm,\'$1 $2\'); // separate commands from commands\n
\t\t\td = d.replace(/([MmZzLlHhVvCcSsQqTtAa])([MmZzLlHhVvCcSsQqTtAa])/gm,\'$1 $2\'); // separate commands from commands\n
\t\t\td = d.replace(/([MmZzLlHhVvCcSsQqTtAa])([^\\s])/gm,\'$1 $2\'); // separate commands from points\n
\t\t\td = d.replace(/([^\\s])([MmZzLlHhVvCcSsQqTtAa])/gm,\'$1 $2\'); // separate commands from points\n
\t\t\td = d.replace(/([0-9])([+\\-])/gm,\'$1 $2\'); // separate digits when no comma\n
\t\t\td = d.replace(/(\\.[0-9]*)(\\.)/gm,\'$1 $2\'); // separate digits when no comma\n
\t\t\td = d.replace(/([Aa](\\s+[0-9]+){3})\\s+([01])\\s*([01])/gm,\'$1 $3 $4 \'); // shorthand elliptical arc path syntax\n
\t\t\td = svg.compressSpaces(d); // compress multiple spaces\n
\t\t\td = svg.trim(d);\n
\t\t\tthis.PathParser = new (function(d) {\n
\t\t\t\tthis.tokens = d.split(\' \');\n
\t\t\t\t\n
\t\t\t\tthis.reset = function() {\n
\t\t\t\t\tthis.i = -1;\n
\t\t\t\t\tthis.command = \'\';\n
\t\t\t\t\tthis.previousCommand = \'\';\n
\t\t\t\t\tthis.start = new svg.Point(0, 0);\n
\t\t\t\t\tthis.control = new svg.Point(0, 0);\n
\t\t\t\t\tthis.current = new svg.Point(0, 0);\n
\t\t\t\t\tthis.points = [];\n
\t\t\t\t\tthis.angles = [];\n
\t\t\t\t}\n
\t\t\t\t\t\t\t\t\n
\t\t\t\tthis.isEnd = function() {\n
\t\t\t\t\treturn this.i >= this.tokens.length - 1;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tthis.isCommandOrEnd = function() {\n
\t\t\t\t\tif (this.isEnd()) return true;\n
\t\t\t\t\treturn this.tokens[this.i + 1].match(/^[A-Za-z]$/) != null;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tthis.isRelativeCommand = function() {\n
\t\t\t\t\treturn this.command == this.command.toLowerCase();\n
\t\t\t\t}\n
\t\t\t\t\t\t\t\n
\t\t\t\tthis.getToken = function() {\n
\t\t\t\t\tthis.i = this.i + 1;\n
\t\t\t\t\treturn this.tokens[this.i];\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tthis.getScalar = function() {\n
\t\t\t\t\treturn parseFloat(this.getToken());\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tthis.nextCommand = function() {\n
\t\t\t\t\tthis.previousCommand = this.command;\n
\t\t\t\t\tthis.command = this.getToken();\n
\t\t\t\t}\t\t\t\t\n
\t\t\t\t\n
\t\t\t\tthis.getPoint = function() {\n
\t\t\t\t\tvar p = new svg.Point(this.getScalar(), this.getScalar());\n
\t\t\t\t\treturn this.makeAbsolute(p);\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tthis.getAsControlPoint = function() {\n
\t\t\t\t\tvar p = this.getPoint();\n
\t\t\t\t\tthis.control = p;\n
\t\t\t\t\treturn p;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tthis.getAsCurrentPoint = function() {\n
\t\t\t\t\tvar p = this.getPoint();\n
\t\t\t\t\tthis.current = p;\n
\t\t\t\t\treturn p;\t\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tthis.getReflectedControlPoint = function() {\n
\t\t\t\t\tif (this.previousCommand.toLowerCase() != \'c\' && this.previousCommand.toLowerCase() != \'s\') {\n
\t\t\t\t\t\treturn this.current;\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\t// reflect point\n
\t\t\t\t\tvar p = new svg.Point(2 * this.current.x - this.control.x, 2 * this.current.y - this.control.y);\t\t\t\t\t\n
\t\t\t\t\treturn p;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tthis.makeAbsolute = function(p) {\n
\t\t\t\t\tif (this.isRelativeCommand()) {\n
\t\t\t\t\t\tp.x = this.current.x + p.x;\n
\t\t\t\t\t\tp.y = this.current.y + p.y;\n
\t\t\t\t\t}\n
\t\t\t\t\treturn p;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tthis.addMarker = function(p, from, priorTo) {\n
\t\t\t\t\t// if the last angle isn\'t filled in because we didn\'t have this point yet ...\n
\t\t\t\t\tif (priorTo != null && this.angles.length > 0 && this.angles[this.angles.length-1] == null) {\n
\t\t\t\t\t\tthis.angles[this.angles.length-1] = this.points[this.points.length-1].angleTo(priorTo);\n
\t\t\t\t\t}\n
\t\t\t\t\tthis.addMarkerAngle(p, from == null ? null : from.angleTo(p));\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tthis.addMarkerAngle = function(p, a) {\n
\t\t\t\t\tthis.points.push(p);\n
\t\t\t\t\tthis.angles.push(a);\n
\t\t\t\t}\t\t\t\t\n
\t\t\t\t\n
\t\t\t\tthis.getMarkerPoints = function() { return this.points; }\n
\t\t\t\tthis.getMarkerAngles = function() {\n
\t\t\t\t\tfor (var i=0; i<this.angles.length; i++) {\n
\t\t\t\t\t\tif (this.angles[i] == null) {\n
\t\t\t\t\t\t\tfor (var j=i+1; j<this.angles.length; j++) {\n
\t\t\t\t\t\t\t\tif (this.angles[j] != null) {\n
\t\t\t\t\t\t\t\t\tthis.angles[i] = this.angles[j];\n
\t\t\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\treturn this.angles;\n
\t\t\t\t}\n
\t\t\t})(d);\n
\n
\t\t\tthis.path = function(ctx) {\n
\t\t\t\tvar pp = this.PathParser;\n
\t\t\t\tpp.reset();\n
\n
\t\t\t\tvar bb = new svg.BoundingBox();\n
\t\t\t\tif (ctx != null) ctx.beginPath();\n
\t\t\t\twhile (!pp.isEnd()) {\n
\t\t\t\t\tpp.nextCommand();\n
\t\t\t\t\tswitch (pp.command.toUpperCase()) {\n
\t\t\t\t\tcase \'M\':\n
\t\t\t\t\t\tvar p = pp.getAsCurrentPoint();\n
\t\t\t\t\t\tpp.addMarker(p);\n
\t\t\t\t\t\tbb.addPoint(p.x, p.y);\n
\t\t\t\t\t\tif (ctx != null) ctx.moveTo(p.x, p.y);\n
\t\t\t\t\t\tpp.start = pp.current;\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\n
\t\t\t\t\t\t\tvar p = pp.getAsCurrentPoint();\n
\t\t\t\t\t\t\tpp.addMarker(p, pp.start);\n
\t\t\t\t\t\t\tbb.addPoint(p.x, p.y);\n
\t\t\t\t\t\t\tif (ctx != null) ctx.lineTo(p.x, p.y);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'L\':\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\n
\t\t\t\t\t\t\tvar c = pp.current;\n
\t\t\t\t\t\t\tvar p = pp.getAsCurrentPoint();\n
\t\t\t\t\t\t\tpp.addMarker(p, c);\n
\t\t\t\t\t\t\tbb.addPoint(p.x, p.y);\n
\t\t\t\t\t\t\tif (ctx != null) ctx.lineTo(p.x, p.y);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'H\':\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\n
\t\t\t\t\t\t\tvar newP = new svg.Point((pp.isRelativeCommand() ? pp.current.x : 0) + pp.getScalar(), pp.current.y);\n
\t\t\t\t\t\t\tpp.addMarker(newP, pp.current);\n
\t\t\t\t\t\t\tpp.current = newP;\n
\t\t\t\t\t\t\tbb.addPoint(pp.current.x, pp.current.y);\n
\t\t\t\t\t\t\tif (ctx != null) ctx.lineTo(pp.current.x, pp.current.y);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'V\':\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\n
\t\t\t\t\t\t\tvar newP = new svg.Point(pp.current.x, (pp.isRelativeCommand() ? pp.current.y : 0) + pp.getScalar());\n
\t\t\t\t\t\t\tpp.addMarker(newP, pp.current);\n
\t\t\t\t\t\t\tpp.current = newP;\n
\t\t\t\t\t\t\tbb.addPoint(pp.current.x, pp.current.y);\n
\t\t\t\t\t\t\tif (ctx != null) ctx.lineTo(pp.current.x, pp.current.y);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'C\':\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\n
\t\t\t\t\t\t\tvar curr = pp.current;\n
\t\t\t\t\t\t\tvar p1 = pp.getPoint();\n
\t\t\t\t\t\t\tvar cntrl = pp.getAsControlPoint();\n
\t\t\t\t\t\t\tvar cp = pp.getAsCurrentPoint();\n
\t\t\t\t\t\t\tpp.addMarker(cp, cntrl, p1);\n
\t\t\t\t\t\t\tbb.addBezierCurve(curr.x, curr.y, p1.x, p1.y, cntrl.x, cntrl.y, cp.x, cp.y);\n
\t\t\t\t\t\t\tif (ctx != null) ctx.bezierCurveTo(p1.x, p1.y, cntrl.x, cntrl.y, cp.x, cp.y);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'S\':\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\n
\t\t\t\t\t\t\tvar curr = pp.current;\n
\t\t\t\t\t\t\tvar p1 = pp.getReflectedControlPoint();\n
\t\t\t\t\t\t\tvar cntrl = pp.getAsControlPoint();\n
\t\t\t\t\t\t\tvar cp = pp.getAsCurrentPoint();\n
\t\t\t\t\t\t\tpp.addMarker(cp, cntrl, p1);\n
\t\t\t\t\t\t\tbb.addBezierCurve(curr.x, curr.y, p1.x, p1.y, cntrl.x, cntrl.y, cp.x, cp.y);\n
\t\t\t\t\t\t\tif (ctx != null) ctx.bezierCurveTo(p1.x, p1.y, cntrl.x, cntrl.y, cp.x, cp.y);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'Q\':\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\n
\t\t\t\t\t\t\tvar curr = pp.current;\n
\t\t\t\t\t\t\tvar cntrl = pp.getAsControlPoint();\n
\t\t\t\t\t\t\tvar cp = pp.getAsCurrentPoint();\n
\t\t\t\t\t\t\tpp.addMarker(cp, cntrl, cntrl);\n
\t\t\t\t\t\t\tbb.addQuadraticCurve(curr.x, curr.y, cntrl.x, cntrl.y, cp.x, cp.y);\n
\t\t\t\t\t\t\tif (ctx != null) ctx.quadraticCurveTo(cntrl.x, cntrl.y, cp.x, cp.y);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'T\':\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\n
\t\t\t\t\t\t\tvar curr = pp.current;\n
\t\t\t\t\t\t\tvar cntrl = pp.getReflectedControlPoint();\n
\t\t\t\t\t\t\tpp.control = cntrl;\n
\t\t\t\t\t\t\tvar cp = pp.getAsCurrentPoint();\n
\t\t\t\t\t\t\tpp.addMarker(cp, cntrl, cntrl);\n
\t\t\t\t\t\t\tbb.addQuadraticCurve(curr.x, curr.y, cntrl.x, cntrl.y, cp.x, cp.y);\n
\t\t\t\t\t\t\tif (ctx != null) ctx.quadraticCurveTo(cntrl.x, cntrl.y, cp.x, cp.y);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'A\':\n
\t\t\t\t\t\twhile (!pp.isCommandOrEnd()) {\n
\t\t\t\t\t\t    var curr = pp.current;\n
\t\t\t\t\t\t\tvar rx = pp.getScalar();\n
\t\t\t\t\t\t\tvar ry = pp.getScalar();\n
\t\t\t\t\t\t\tvar xAxisRotation = pp.getScalar() * (Math.PI / 180.0);\n
\t\t\t\t\t\t\tvar largeArcFlag = pp.getScalar();\n
\t\t\t\t\t\t\tvar sweepFlag = pp.getScalar();\n
\t\t\t\t\t\t\tvar cp = pp.getAsCurrentPoint();\n
\n
\t\t\t\t\t\t\t// Conversion from endpoint to center parameterization\n
\t\t\t\t\t\t\t// http://www.w3.org/TR/SVG11/implnote.html#ArcImplementationNotes\n
\t\t\t\t\t\t\t// x1\', y1\'\n
\t\t\t\t\t\t\tvar currp = new svg.Point(\n
\t\t\t\t\t\t\t\tMath.cos(xAxisRotation) * (curr.x - cp.x) / 2.0 + Math.sin(xAxisRotation) * (curr.y - cp.y) / 2.0,\n
\t\t\t\t\t\t\t\t-Math.sin(xAxisRotation) * (curr.x - cp.x) / 2.0 + Math.cos(xAxisRotation) * (curr.y - cp.y) / 2.0\n
\t\t\t\t\t\t\t);\n
\t\t\t\t\t\t\t// adjust radii\n
\t\t\t\t\t\t\tvar l = Math.pow(currp.x,2)/Math.pow(rx,2)+Math.pow(currp.y,2)/Math.pow(ry,2);\n
\t\t\t\t\t\t\tif (l > 1) {\n
\t\t\t\t\t\t\t\trx *= Math.sqrt(l);\n
\t\t\t\t\t\t\t\try *= Math.sqrt(l);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t// cx\', cy\'\n
\t\t\t\t\t\t\tvar s = (largeArcFlag == sweepFlag ? -1 : 1) * Math.sqrt(\n
\t\t\t\t\t\t\t\t((Math.pow(rx,2)*Math.pow(ry,2))-(Math.pow(rx,2)*Math.pow(currp.y,2))-(Math.pow(ry,2)*Math.pow(currp.x,2))) /\n
\t\t\t\t\t\t\t\t(Math.pow(rx,2)*Math.pow(currp.y,2)+Math.pow(ry,2)*Math.pow(currp.x,2))\n
\t\t\t\t\t\t\t);\n
\t\t\t\t\t\t\tif (isNaN(s)) s = 0;\n
\t\t\t\t\t\t\tvar cpp = new svg.Point(s * rx * currp.y / ry, s * -ry * currp.x / rx);\n
\t\t\t\t\t\t\t// cx, cy\n
\t\t\t\t\t\t\tvar centp = new svg.Point(\n
\t\t\t\t\t\t\t\t(curr.x + cp.x) / 2.0 + Math.cos(xAxisRotation) * cpp.x - Math.sin(xAxisRotation) * cpp.y,\n
\t\t\t\t\t\t\t\t(curr.y + cp.y) / 2.0 + Math.sin(xAxisRotation) * cpp.x + Math.cos(xAxisRotation) * cpp.y\n
\t\t\t\t\t\t\t);\n
\t\t\t\t\t\t\t// vector magnitude\n
\t\t\t\t\t\t\tvar m = function(v) { return Math.sqrt(Math.pow(v[0],2) + Math.pow(v[1],2)); }\n
\t\t\t\t\t\t\t// ratio between two vectors\n
\t\t\t\t\t\t\tvar r = function(u, v) { return (u[0]*v[0]+u[1]*v[1]) / (m(u)*m(v)) }\n
\t\t\t\t\t\t\t// angle between two vectors\n
\t\t\t\t\t\t\tvar a = function(u, v) { return (u[0]*v[1] < u[1]*v[0] ? -1 : 1) * Math.acos(r(u,v)); }\n
\t\t\t\t\t\t\t// initial angle\n
\t\t\t\t\t\t\tvar a1 = a([1,0], [(currp.x-cpp.x)/rx,(currp.y-cpp.y)/ry]);\n
\t\t\t\t\t\t\t// angle delta\n
\t\t\t\t\t\t\tvar u = [(currp.x-cpp.x)/rx,(currp.y-cpp.y)/ry];\n
\t\t\t\t\t\t\tvar v = [(-currp.x-cpp.x)/rx,(-currp.y-cpp.y)/ry];\n
\t\t\t\t\t\t\tvar ad = a(u, v);\n
\t\t\t\t\t\t\tif (r(u,v) <= -1) ad = Math.PI;\n
\t\t\t\t\t\t\tif (r(u,v) >= 1) ad = 0;\n
\n
\t\t\t\t\t\t\tif (sweepFlag == 0 && ad > 0) ad = ad - 2 * Math.PI;\n
\t\t\t\t\t\t\tif (sweepFlag == 1 && ad < 0) ad = ad + 2 * Math.PI;\n
\n
\t\t\t\t\t\t\t// for markers\n
\t\t\t\t\t\t\tvar halfWay = new svg.Point(\n
\t\t\t\t\t\t\t\tcentp.x - rx * Math.cos((a1 + ad) / 2),\n
\t\t\t\t\t\t\t\tcentp.y - ry * Math.sin((a1 + ad) / 2)\n
\t\t\t\t\t\t\t);\n
\t\t\t\t\t\t\tpp.addMarkerAngle(halfWay, (a1 + ad) / 2 + (sweepFlag == 0 ? 1 : -1) * Math.PI / 2);\n
\t\t\t\t\t\t\tpp.addMarkerAngle(cp, ad + (sweepFlag == 0 ? 1 : -1) * Math.PI / 2);\n
\n
\t\t\t\t\t\t\tbb.addPoint(cp.x, cp.y); // TODO: this is too naive, make it better\n
\t\t\t\t\t\t\tif (ctx != null) {\n
\t\t\t\t\t\t\t\tvar r = rx > ry ? rx : ry;\n
\t\t\t\t\t\t\t\tvar sx = rx > ry ? 1 : rx / ry;\n
\t\t\t\t\t\t\t\tvar sy = rx > ry ? ry / rx : 1;\n
\n
\t\t\t\t\t\t\t\tctx.translate(centp.x, centp.y);\n
\t\t\t\t\t\t\t\tctx.rotate(xAxisRotation);\n
\t\t\t\t\t\t\t\tctx.scale(sx, sy);\n
\t\t\t\t\t\t\t\tctx.arc(0, 0, r, a1, a1 + ad, 1 - sweepFlag);\n
\t\t\t\t\t\t\t\tctx.scale(1/sx, 1/sy);\n
\t\t\t\t\t\t\t\tctx.rotate(-xAxisRotation);\n
\t\t\t\t\t\t\t\tctx.translate(-centp.x, -centp.y);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'Z\':\n
\t\t\t\t\t\tif (ctx != null) ctx.closePath();\n
\t\t\t\t\t\tpp.current = pp.start;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\treturn bb;\n
\t\t\t}\n
\n
\t\t\tthis.getMarkers = function() {\n
\t\t\t\tvar points = this.PathParser.getMarkerPoints();\n
\t\t\t\tvar angles = this.PathParser.getMarkerAngles();\n
\t\t\t\t\n
\t\t\t\tvar markers = [];\n
\t\t\t\tfor (var i=0; i<points.length; i++) {\n
\t\t\t\t\tmarkers.push([points[i], angles[i]]);\n
\t\t\t\t}\n
\t\t\t\treturn markers;\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.path.prototype = new svg.Element.PathElementBase;\n
\t\t\n
\t\t// pattern element\n
\t\tsvg.Element.pattern = function(node) {\n
\t\t\tthis.base = svg.Element.ElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.createPattern = function(ctx, element) {\n
\t\t\t\t// render me using a temporary svg element\n
\t\t\t\tvar tempSvg = new svg.Element.svg();\n
\t\t\t\ttempSvg.attributes[\'viewBox\'] = new svg.Property(\'viewBox\', this.attribute(\'viewBox\').value);\n
\t\t\t\ttempSvg.attributes[\'x\'] = new svg.Property(\'x\', this.attribute(\'x\').value);\n
\t\t\t\ttempSvg.attributes[\'y\'] = new svg.Property(\'y\', this.attribute(\'y\').value);\n
\t\t\t\ttempSvg.attributes[\'width\'] = new svg.Property(\'width\', this.attribute(\'width\').value);\n
\t\t\t\ttempSvg.attributes[\'height\'] = new svg.Property(\'height\', this.attribute(\'height\').value);\n
\t\t\t\ttempSvg.children = this.children;\n
\t\t\t\t\n
\t\t\t\tvar c = document.createElement(\'canvas\');\n
\t\t\t\tc.width = this.attribute(\'width\').Length.toPixels(\'x\');\n
\t\t\t\tc.height = this.attribute(\'height\').Length.toPixels(\'y\');\n
\t\t\t\ttempSvg.render(c.getContext(\'2d\'));\t\t\n
\t\t\t\treturn ctx.createPattern(c, \'repeat\');\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.pattern.prototype = new svg.Element.ElementBase;\n
\t\t\n
\t\t// marker element\n
\t\tsvg.Element.marker = function(node) {\n
\t\t\tthis.base = svg.Element.ElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.baseRender = this.render;\n
\t\t\tthis.render = function(ctx, point, angle) {\n
\t\t\t\tctx.translate(point.x, point.y);\n
\t\t\t\tif (this.attribute(\'orient\').valueOrDefault(\'auto\') == \'auto\') ctx.rotate(angle);\n
\t\t\t\tif (this.attribute(\'markerUnits\').valueOrDefault(\'strokeWidth\') == \'strokeWidth\') ctx.scale(ctx.lineWidth, ctx.lineWidth);\n
\t\t\t\tctx.save();\n
\t\t\t\t\t\t\t\n
\t\t\t\t// render me using a temporary svg element\n
\t\t\t\tvar tempSvg = new svg.Element.svg();\n
\t\t\t\ttempSvg.attributes[\'viewBox\'] = new svg.Property(\'viewBox\', this.attribute(\'viewBox\').value);\n
\t\t\t\ttempSvg.attributes[\'refX\'] = new svg.Property(\'refX\', this.attribute(\'refX\').value);\n
\t\t\t\ttempSvg.attributes[\'refY\'] = new svg.Property(\'refY\', this.attribute(\'refY\').value);\n
\t\t\t\ttempSvg.attributes[\'width\'] = new svg.Property(\'width\', this.attribute(\'markerWidth\').value);\n
\t\t\t\ttempSvg.attributes[\'height\'] = new svg.Property(\'height\', this.attribute(\'markerHeight\').value);\n
\t\t\t\ttempSvg.attributes[\'fill\'] = new svg.Property(\'fill\', this.attribute(\'fill\').valueOrDefault(\'black\'));\n
\t\t\t\ttempSvg.attributes[\'stroke\'] = new svg.Property(\'stroke\', this.attribute(\'stroke\').valueOrDefault(\'none\'));\n
\t\t\t\ttempSvg.children = this.children;\n
\t\t\t\ttempSvg.render(ctx);\n
\t\t\t\t\n
\t\t\t\tctx.restore();\n
\t\t\t\tif (this.attribute(\'markerUnits\').valueOrDefault(\'strokeWidth\') == \'strokeWidth\') ctx.scale(1/ctx.lineWidth, 1/ctx.lineWidth);\n
\t\t\t\tif (this.attribute(\'orient\').valueOrDefault(\'auto\') == \'auto\') ctx.rotate(-angle);\n
\t\t\t\tctx.translate(-point.x, -point.y);\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.marker.prototype = new svg.Element.ElementBase;\n
\t\t\n
\t\t// definitions element\n
\t\tsvg.Element.defs = function(node) {\n
\t\t\tthis.base = svg.Element.ElementBase;\n
\t\t\tthis.base(node);\t\n
\t\t\t\n
\t\t\tthis.render = function(ctx) {\n
\t\t\t\t// NOOP\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.defs.prototype = new svg.Element.ElementBase;\n
\t\t\n
\t\t// base for gradients\n
\t\tsvg.Element.GradientBase = function(node) {\n
\t\t\tthis.base = svg.Element.ElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.gradientUnits = this.attribute(\'gradientUnits\').valueOrDefault(\'objectBoundingBox\');\n
\t\t\t\n
\t\t\tthis.stops = [];\t\t\t\n
\t\t\tfor (var i=0; i<this.children.length; i++) {\n
\t\t\t\tvar child = this.children[i];\n
\t\t\t\tthis.stops.push(child);\n
\t\t\t}\t\n
\t\t\t\n
\t\t\tthis.getGradient = function() {\n
\t\t\t\t// OVERRIDE ME!\n
\t\t\t}\t\t\t\n
\n
\t\t\tthis.createGradient = function(ctx, element) {\n
\t\t\t\tvar stopsContainer = this;\n
\t\t\t\tif (this.attribute(\'xlink:href\').hasValue()) {\n
\t\t\t\t\tstopsContainer = this.attribute(\'xlink:href\').Definition.getDefinition();\n
\t\t\t\t}\n
\t\t\t\n
\t\t\t\tvar g = this.getGradient(ctx, element);\n
\t\t\t\tfor (var i=0; i<stopsContainer.stops.length; i++) {\n
\t\t\t\t\tg.addColorStop(stopsContainer.stops[i].offset, stopsContainer.stops[i].color);\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tif (this.attribute(\'gradientTransform\').hasValue()) {\n
\t\t\t\t\t// render as transformed pattern on temporary canvas\n
\t\t\t\t\tvar rootView = svg.ViewPort.viewPorts[0];\n
\t\t\t\t\t\n
\t\t\t\t\tvar rect = new svg.Element.rect();\n
\t\t\t\t\trect.attributes[\'x\'] = new svg.Property(\'x\', -svg.MAX_VIRTUAL_PIXELS/3.0);\n
\t\t\t\t\trect.attributes[\'y\'] = new svg.Property(\'y\', -svg.MAX_VIRTUAL_PIXELS/3.0);\n
\t\t\t\t\trect.attributes[\'width\'] = new svg.Property(\'width\', svg.MAX_VIRTUAL_PIXELS);\n
\t\t\t\t\trect.attributes[\'height\'] = new svg.Property(\'height\', svg.MAX_VIRTUAL_PIXELS);\n
\t\t\t\t\t\n
\t\t\t\t\tvar group = new svg.Element.g();\n
\t\t\t\t\tgroup.attributes[\'transform\'] = new svg.Property(\'transform\', this.attribute(\'gradientTransform\').value);\n
\t\t\t\t\tgroup.children = [ rect ];\n
\t\t\t\t\t\n
\t\t\t\t\tvar tempSvg = new svg.Element.svg();\n
\t\t\t\t\ttempSvg.attributes[\'x\'] = new svg.Property(\'x\', 0);\n
\t\t\t\t\ttempSvg.attributes[\'y\'] = new svg.Property(\'y\', 0);\n
\t\t\t\t\ttempSvg.attributes[\'width\'] = new svg.Property(\'width\', rootView.width);\n
\t\t\t\t\ttempSvg.attributes[\'height\'] = new svg.Property(\'height\', rootView.height);\n
\t\t\t\t\ttempSvg.children = [ group ];\n
\t\t\t\t\t\n
\t\t\t\t\tvar c = document.createElement(\'canvas\');\n
\t\t\t\t\tc.width = rootView.width;\n
\t\t\t\t\tc.height = rootView.height;\n
\t\t\t\t\tvar tempCtx = c.getContext(\'2d\');\n
\t\t\t\t\ttempCtx.fillStyle = g;\n
\t\t\t\t\ttempSvg.render(tempCtx);\t\t\n
\t\t\t\t\treturn tempCtx.createPattern(c, \'no-repeat\');\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\treturn g;\t\t\t\t\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.GradientBase.prototype = new svg.Element.ElementBase;\n
\t\t\n
\t\t// linear gradient element\n
\t\tsvg.Element.linearGradient = function(node) {\n
\t\t\tthis.base = svg.Element.GradientBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.getGradient = function(ctx, element) {\n
\t\t\t\tvar bb = element.getBoundingBox();\n
\t\t\t\t\n
\t\t\t\tvar x1 = (this.gradientUnits == \'objectBoundingBox\' \n
\t\t\t\t\t? bb.x() + bb.width() * this.attribute(\'x1\').numValue() \n
\t\t\t\t\t: this.attribute(\'x1\').Length.toPixels(\'x\'));\n
\t\t\t\tvar y1 = (this.gradientUnits == \'objectBoundingBox\' \n
\t\t\t\t\t? bb.y() + bb.height() * this.attribute(\'y1\').numValue()\n
\t\t\t\t\t: this.attribute(\'y1\').Length.toPixels(\'y\'));\n
\t\t\t\tvar x2 = (this.gradientUnits == \'objectBoundingBox\' \n
\t\t\t\t\t? bb.x() + bb.width() * this.attribute(\'x2\').numValue()\n
\t\t\t\t\t: this.attribute(\'x2\').Length.toPixels(\'x\'));\n
\t\t\t\tvar y2 = (this.gradientUnits == \'objectBoundingBox\' \n
\t\t\t\t\t? bb.y() + bb.height() * this.attribute(\'y2\').numValue()\n
\t\t\t\t\t: this.attribute(\'y2\').Length.toPixels(\'y\'));\n
\n
\t\t\t\treturn ctx.createLinearGradient(x1, y1, x2, y2);\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.linearGradient.prototype = new svg.Element.GradientBase;\n
\t\t\n
\t\t// radial gradient element\n
\t\tsvg.Element.radialGradient = function(node) {\n
\t\t\tthis.base = svg.Element.GradientBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.getGradient = function(ctx, element) {\n
\t\t\t\tvar bb = element.getBoundingBox();\n
\t\t\t\t\n
\t\t\t\tvar cx = (this.gradientUnits == \'objectBoundingBox\' \n
\t\t\t\t\t? bb.x() + bb.width() * this.attribute(\'cx\').numValue() \n
\t\t\t\t\t: this.attribute(\'cx\').Length.toPixels(\'x\'));\n
\t\t\t\tvar cy = (this.gradientUnits == \'objectBoundingBox\' \n
\t\t\t\t\t? bb.y() + bb.height() * this.attribute(\'cy\').numValue() \n
\t\t\t\t\t: this.attribute(\'cy\').Length.toPixels(\'y\'));\n
\t\t\t\t\n
\t\t\t\tvar fx = cx;\n
\t\t\t\tvar fy = cy;\n
\t\t\t\tif (this.attribute(\'fx\').hasValue()) {\n
\t\t\t\t\tfx = (this.gradientUnits == \'objectBoundingBox\' \n
\t\t\t\t\t? bb.x() + bb.width() * this.attribute(\'fx\').numValue() \n
\t\t\t\t\t: this.attribute(\'fx\').Length.toPixels(\'x\'));\n
\t\t\t\t}\n
\t\t\t\tif (this.attribute(\'fy\').hasValue()) {\n
\t\t\t\t\tfy = (this.gradientUnits == \'objectBoundingBox\' \n
\t\t\t\t\t? bb.y() + bb.height() * this.attribute(\'fy\').numValue() \n
\t\t\t\t\t: this.attribute(\'fy\').Length.toPixels(\'y\'));\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tvar r = (this.gradientUnits == \'objectBoundingBox\' \n
\t\t\t\t\t? (bb.width() + bb.height()) / 2.0 * this.attribute(\'r\').numValue()\n
\t\t\t\t\t: this.attribute(\'r\').Length.toPixels());\n
\t\t\t\t\n
\t\t\t\treturn ctx.createRadialGradient(fx, fy, 0, cx, cy, r);\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.radialGradient.prototype = new svg.Element.GradientBase;\n
\t\t\n
\t\t// gradient stop element\n
\t\tsvg.Element.stop = function(node) {\n
\t\t\tthis.base = svg.Element.ElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.offset = this.attribute(\'offset\').numValue();\n
\t\t\t\n
\t\t\tvar stopColor = this.style(\'stop-color\');\n
\t\t\tif (this.style(\'stop-opacity\').hasValue()) stopColor = stopColor.Color.addOpacity(this.style(\'stop-opacity\').value);\n
\t\t\tthis.color = stopColor.value;\n
\t\t}\n
\t\tsvg.Element.stop.prototype = new svg.Element.ElementBase;\n
\t\t\n
\t\t// animation base element\n
\t\tsvg.Element.AnimateBase = function(node) {\n
\t\t\tthis.base = svg.Element.ElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tsvg.Animations.push(this);\n
\t\t\t\n
\t\t\tthis.duration = 0.0;\n
\t\t\tthis.begin = this.attribute(\'begin\').Time.toMilliseconds();\n
\t\t\tthis.maxDuration = this.begin + this.attribute(\'dur\').Time.toMilliseconds();\n
\t\t\t\n
\t\t\tthis.getProperty = function() {\n
\t\t\t\tvar attributeType = this.attribute(\'attributeType\').value;\n
\t\t\t\tvar attributeName = this.attribute(\'attributeName\').value;\n
\t\t\t\t\n
\t\t\t\tif (attributeType == \'CSS\') {\n
\t\t\t\t\treturn this.parent.style(attributeName, true);\n
\t\t\t\t}\n
\t\t\t\treturn this.parent.attribute(attributeName, true);\t\t\t\n
\t\t\t};\n
\t\t\t\n
\t\t\tthis.initialValue = null;\n
\t\t\tthis.removed = false;\t\t\t\n
\n
\t\t\tthis.calcValue = function() {\n
\t\t\t\t// OVERRIDE ME!\n
\t\t\t\treturn \'\';\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.update = function(delta) {\t\n
\t\t\t\t// set initial value\n
\t\t\t\tif (this.initialValue == null) {\n
\t\t\t\t\tthis.initialValue = this.getProperty().value;\n
\t\t\t\t}\n
\t\t\t\n
\t\t\t\t// if we\'re past the end time\n
\t\t\t\tif (this.duration > this.maxDuration) {\n
\t\t\t\t\t// loop for indefinitely repeating animations\n
\t\t\t\t\tif (this.attribute(\'repeatCount\').value == \'indefinite\') {\n
\t\t\t\t\t\tthis.duration = 0.0\n
\t\t\t\t\t}\n
\t\t\t\t\telse if (this.attribute(\'fill\').valueOrDefault(\'remove\') == \'remove\' && !this.removed) {\n
\t\t\t\t\t\tthis.removed = true;\n
\t\t\t\t\t\tthis.getProperty().value = this.initialValue;\n
\t\t\t\t\t\treturn true;\n
\t\t\t\t\t}\n
\t\t\t\t\telse {\n
\t\t\t\t\t\treturn false; // no updates made\n
\t\t\t\t\t}\n
\t\t\t\t}\t\t\t\n
\t\t\t\tthis.duration = this.duration + delta;\n
\t\t\t\n
\t\t\t\t// if we\'re past the begin time\n
\t\t\t\tvar updated = false;\n
\t\t\t\tif (this.begin < this.duration) {\n
\t\t\t\t\tvar newValue = this.calcValue(); // tween\n
\t\t\t\t\t\n
\t\t\t\t\tif (this.attribute(\'type\').hasValue()) {\n
\t\t\t\t\t\t// for transform, etc.\n
\t\t\t\t\t\tvar type = this.attribute(\'type\').value;\n
\t\t\t\t\t\tnewValue = type + \'(\' + newValue + \')\';\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\tthis.getProperty().value = newValue;\n
\t\t\t\t\tupdated = true;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\treturn updated;\n
\t\t\t}\n
\t\t\t\n
\t\t\t// fraction of duration we\'ve covered\n
\t\t\tthis.progress = function() {\n
\t\t\t\treturn ((this.duration - this.begin) / (this.maxDuration - this.begin));\n
\t\t\t}\t\t\t\n
\t\t}\n
\t\tsvg.Element.AnimateBase.prototype = new svg.Element.ElementBase;\n
\t\t\n
\t\t// animate element\n
\t\tsvg.Element.animate = function(node) {\n
\t\t\tthis.base = svg.Element.AnimateBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.calcValue = function() {\n
\t\t\t\tvar from = this.attribute(\'from\').numValue();\n
\t\t\t\tvar to = this.attribute(\'to\').numValue();\n
\t\t\t\t\n
\t\t\t\t// tween value linearly\n
\t\t\t\treturn from + (to - from) * this.progress(); \n
\t\t\t};\n
\t\t}\n
\t\tsvg.Element.animate.prototype = new svg.Element.AnimateBase;\n
\t\t\t\n
\t\t// animate color element\n
\t\tsvg.Element.animateColor = function(node) {\n
\t\t\tthis.base = svg.Element.AnimateBase;\n
\t\t\tthis.base(node);\n
\n
\t\t\tthis.calcValue = function() {\n
\t\t\t\tvar from = new RGBColor(this.attribute(\'from\').value);\n
\t\t\t\tvar to = new RGBColor(this.attribute(\'to\').value);\n
\t\t\t\t\n
\t\t\t\tif (from.ok && to.ok) {\n
\t\t\t\t\t// tween color linearly\n
\t\t\t\t\tvar r = from.r + (to.r - from.r) * this.progress();\n
\t\t\t\t\tvar g = from.g + (to.g - from.g) * this.progress();\n
\t\t\t\t\tvar b = from.b + (to.b - from.b) * this.progress();\n
\t\t\t\t\treturn \'rgb(\'+parseInt(r,10)+\',\'+parseInt(g,10)+\',\'+parseInt(b,10)+\')\';\n
\t\t\t\t}\n
\t\t\t\treturn this.attribute(\'from\').value;\n
\t\t\t};\n
\t\t}\n
\t\tsvg.Element.animateColor.prototype = new svg.Element.AnimateBase;\n
\t\t\n
\t\t// animate transform element\n
\t\tsvg.Element.animateTransform = function(node) {\n
\t\t\tthis.base = svg.Element.animate;\n
\t\t\tthis.base(node);\n
\t\t}\n
\t\tsvg.Element.animateTransform.prototype = new svg.Element.animate;\n
\t\t\n
\t\t// font element\n
\t\tsvg.Element.font = function(node) {\n
\t\t\tthis.base = svg.Element.ElementBase;\n
\t\t\tthis.base(node);\n
\n
\t\t\tthis.horizAdvX = this.attribute(\'horiz-adv-x\').numValue();\t\t\t\n
\t\t\t\n
\t\t\tthis.isRTL = false;\n
\t\t\tthis.isArabic = false;\n
\t\t\tthis.fontFace = null;\n
\t\t\tthis.missingGlyph = null;\n
\t\t\tthis.glyphs = [];\t\t\t\n
\t\t\tfor (var i=0; i<this.children.length; i++) {\n
\t\t\t\tvar child = this.children[i];\n
\t\t\t\tif (child.type == \'font-face\') {\n
\t\t\t\t\tthis.fontFace = child;\n
\t\t\t\t\tif (child.style(\'font-family\').hasValue()) {\n
\t\t\t\t\t\tsvg.Definitions[child.style(\'font-family\').value] = this;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\telse if (child.type == \'missing-glyph\') this.missingGlyph = child;\n
\t\t\t\telse if (child.type == \'glyph\') {\n
\t\t\t\t\tif (child.arabicForm != \'\') {\n
\t\t\t\t\t\tthis.isRTL = true;\n
\t\t\t\t\t\tthis.isArabic = true;\n
\t\t\t\t\t\tif (typeof(this.glyphs[child.unicode]) == \'undefined\') this.glyphs[child.unicode] = [];\n
\t\t\t\t\t\tthis.glyphs[child.unicode][child.arabicForm] = child;\n
\t\t\t\t\t}\n
\t\t\t\t\telse {\n
\t\t\t\t\t\tthis.glyphs[child.unicode] = child;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\t\n
\t\t}\n
\t\tsvg.Element.font.prototype = new svg.Element.ElementBase;\n
\t\t\n
\t\t// font-face element\n
\t\tsvg.Element.fontface = function(node) {\n
\t\t\tthis.base = svg.Element.ElementBase;\n
\t\t\tthis.base(node);\t\n
\t\t\t\n
\t\t\tthis.ascent = this.attribute(\'ascent\').value;\n
\t\t\tthis.descent = this.attribute(\'descent\').value;\n
\t\t\tthis.unitsPerEm = this.attribute(\'units-per-em\').numValue();\t\t\t\t\n
\t\t}\n
\t\tsvg.Element.fontface.prototype = new svg.Element.ElementBase;\n
\t\t\n
\t\t// missing-glyph element\n
\t\tsvg.Element.missingglyph = function(node) {\n
\t\t\tthis.base = svg.Element.path;\n
\t\t\tthis.base(node);\t\n
\t\t\t\n
\t\t\tthis.horizAdvX = 0;\n
\t\t}\n
\t\tsvg.Element.missingglyph.prototype = new svg.Element.path;\n
\t\t\n
\t\t// glyph element\n
\t\tsvg.Element.glyph = function(node) {\n
\t\t\tthis.base = svg.Element.path;\n
\t\t\tthis.base(node);\t\n
\t\t\t\n
\t\t\tthis.horizAdvX = this.attribute(\'horiz-adv-x\').numValue();\n
\t\t\tthis.unicode = this.attribute(\'unicode\').value;\n
\t\t\tthis.arabicForm = this.attribute(\'arabic-form\').value;\n
\t\t}\n
\t\tsvg.Element.glyph.prototype = new svg.Element.path;\n
\t\t\n
\t\t// text element\n
\t\tsvg.Element.text = function(node) {\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tif (node != null) {\n
\t\t\t\t// add children\n
\t\t\t\tthis.children = [];\n
\t\t\t\tfor (var i=0; i<node.childNodes.length; i++) {\n
\t\t\t\t\tvar childNode = node.childNodes[i];\n
\t\t\t\t\tif (childNode.nodeType == 1) { // capture tspan and tref nodes\n
\t\t\t\t\t\tthis.addChild(childNode, true);\n
\t\t\t\t\t}\n
\t\t\t\t\telse if (childNode.nodeType == 3) { // capture text\n
\t\t\t\t\t\tthis.addChild(new svg.Element.tspan(childNode), false);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.baseSetContext = this.setContext;\n
\t\t\tthis.setContext = function(ctx) {\n
\t\t\t\tthis.baseSetContext(ctx);\n
\t\t\t\tif (this.style(\'dominant-baseline\').hasValue()) ctx.textBaseline = this.style(\'dominant-baseline\').value;\n
\t\t\t\tif (this.style(\'alignment-baseline\').hasValue()) ctx.textBaseline = this.style(\'alignment-baseline\').value;\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.renderChildren = function(ctx) {\n
\t\t\t\tvar textAnchor = this.style(\'text-anchor\').valueOrDefault(\'start\');\n
\t\t\t\tvar x = this.attribute(\'x\').Length.toPixels(\'x\');\n
\t\t\t\tvar y = this.attribute(\'y\').Length.toPixels(\'y\');\n
\t\t\t\tfor (var i=0; i<this.children.length; i++) {\n
\t\t\t\t\tvar child = this.children[i];\n
\t\t\t\t\n
\t\t\t\t\tif (child.attribute(\'x\').hasValue()) {\n
\t\t\t\t\t\tchild.x = child.attribute(\'x\').Length.toPixels(\'x\');\n
\t\t\t\t\t}\n
\t\t\t\t\telse {\n
\t\t\t\t\t\tif (child.attribute(\'dx\').hasValue()) x += child.attribute(\'dx\').Length.toPixels(\'x\');\n
\t\t\t\t\t\tchild.x = x;\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\tvar childLength = child.measureText(ctx);\n
\t\t\t\t\tif (textAnchor != \'start\' && (i==0 || child.attribute(\'x\').hasValue())) { // new group?\n
\t\t\t\t\t\t// loop through rest of children\n
\t\t\t\t\t\tvar groupLength = childLength;\n
\t\t\t\t\t\tfor (var j=i+1; j<this.children.length; j++) {\n
\t\t\t\t\t\t\tvar childInGroup = this.children[j];\n
\t\t\t\t\t\t\tif (childInGroup.attribute(\'x\').hasValue()) break; // new group\n
\t\t\t\t\t\t\tgroupLength += childInGroup.measureText(ctx);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tchild.x -= (textAnchor == \'end\' ? groupLength : groupLength / 2.0);\n
\t\t\t\t\t}\n
\t\t\t\t\tx = child.x + childLength;\n
\t\t\t\t\t\n
\t\t\t\t\tif (child.attribute(\'y\').hasValue()) {\n
\t\t\t\t\t\tchild.y = child.attribute(\'y\').Length.toPixels(\'y\');\n
\t\t\t\t\t}\n
\t\t\t\t\telse {\n
\t\t\t\t\t\tif (child.attribute(\'dy\').hasValue()) y += child.attribute(\'dy\').Length.toPixels(\'y\');\n
\t\t\t\t\t\tchild.y = y;\n
\t\t\t\t\t}\t\n
\t\t\t\t\ty = child.y;\n
\t\t\t\t\t\n
\t\t\t\t\tchild.render(ctx);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.text.prototype = new svg.Element.RenderedElementBase;\n
\t\t\n
\t\t// text base\n
\t\tsvg.Element.TextElementBase = function(node) {\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.getGlyph = function(font, text, i) {\n
\t\t\t\tvar c = text[i];\n
\t\t\t\tvar glyph = null;\n
\t\t\t\tif (font.isArabic) {\n
\t\t\t\t\tvar arabicForm = \'isolated\';\n
\t\t\t\t\tif ((i==0 || text[i-1]==\' \') && i<text.length-2 && text[i+1]!=\' \') arabicForm = \'terminal\'; \n
\t\t\t\t\tif (i>0 && text[i-1]!=\' \' && i<text.length-2 && text[i+1]!=\' \') arabicForm = \'medial\';\n
\t\t\t\t\tif (i>0 && text[i-1]!=\' \' && (i == text.length-1 || text[i+1]==\' \')) arabicForm = \'initial\';\n
\t\t\t\t\tif (typeof(font.glyphs[c]) != \'undefined\') {\n
\t\t\t\t\t\tglyph = font.glyphs[c][arabicForm];\n
\t\t\t\t\t\tif (glyph == null && font.glyphs[c].type == \'glyph\') glyph = font.glyphs[c];\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\telse {\n
\t\t\t\t\tglyph = font.glyphs[c];\n
\t\t\t\t}\n
\t\t\t\tif (glyph == null) glyph = font.missingGlyph;\n
\t\t\t\treturn glyph;\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.renderChildren = function(ctx) {\n
\t\t\t\tvar customFont = this.parent.style(\'font-family\').Definition.getDefinition();\n
\t\t\t\tif (customFont != null) {\n
\t\t\t\t\tvar fontSize = this.parent.style(\'font-size\').numValueOrDefault(svg.Font.Parse(svg.ctx.font).fontSize);\n
\t\t\t\t\tvar fontStyle = this.parent.style(\'font-style\').valueOrDefault(svg.Font.Parse(svg.ctx.font).fontStyle);\n
\t\t\t\t\tvar text = this.getText();\n
\t\t\t\t\tif (customFont.isRTL) text = text.split("").reverse().join("");\n
\t\t\t\t\t\n
\t\t\t\t\tvar dx = svg.ToNumberArray(this.parent.attribute(\'dx\').value);\n
\t\t\t\t\tfor (var i=0; i<text.length; i++) {\n
\t\t\t\t\t\tvar glyph = this.getGlyph(customFont, text, i);\n
\t\t\t\t\t\tvar scale = fontSize / customFont.fontFace.unitsPerEm;\n
\t\t\t\t\t\tctx.translate(this.x, this.y);\n
\t\t\t\t\t\tctx.scale(scale, -scale);\n
\t\t\t\t\t\tvar lw = ctx.lineWidth;\n
\t\t\t\t\t\tctx.lineWidth = ctx.lineWidth * customFont.fontFace.unitsPerEm / fontSize;\n
\t\t\t\t\t\tif (fontStyle == \'italic\') ctx.transform(1, 0, .4, 1, 0, 0);\n
\t\t\t\t\t\tglyph.render(ctx);\n
\t\t\t\t\t\tif (fontStyle == \'italic\') ctx.transform(1, 0, -.4, 1, 0, 0);\n
\t\t\t\t\t\tctx.lineWidth = lw;\n
\t\t\t\t\t\tctx.scale(1/scale, -1/scale);\n
\t\t\t\t\t\tctx.translate(-this.x, -this.y);\t\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tthis.x += fontSize * (glyph.horizAdvX || customFont.horizAdvX) / customFont.fontFace.unitsPerEm;\n
\t\t\t\t\t\tif (typeof(dx[i]) != \'undefined\' && !isNaN(dx[i])) {\n
\t\t\t\t\t\t\tthis.x += dx[i];\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\t\t\t\n
\t\t\t\tif (ctx.strokeStyle != \'\') ctx.strokeText(svg.compressSpaces(this.getText()), this.x, this.y);\n
\t\t\t\tif (ctx.fillStyle != \'\') ctx.fillText(svg.compressSpaces(this.getText()), this.x, this.y);\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.getText = function() {\n
\t\t\t\t// OVERRIDE ME\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.measureText = function(ctx) {\n
\t\t\t\tvar customFont = this.parent.style(\'font-family\').Definition.getDefinition();\n
\t\t\t\tif (customFont != null) {\n
\t\t\t\t\tvar fontSize = this.parent.style(\'font-size\').numValueOrDefault(svg.Font.Parse(svg.ctx.font).fontSize);\n
\t\t\t\t\tvar measure = 0;\n
\t\t\t\t\tvar text = this.getText();\n
\t\t\t\t\tif (customFont.isRTL) text = text.split("").reverse().join("");\n
\t\t\t\t\tvar dx = svg.ToNumberArray(this.parent.attribute(\'dx\').value);\n
\t\t\t\t\tfor (var i=0; i<text.length; i++) {\n
\t\t\t\t\t\tvar glyph = this.getGlyph(customFont, text, i);\n
\t\t\t\t\t\tmeasure += (glyph.horizAdvX || customFont.horizAdvX) * fontSize / customFont.fontFace.unitsPerEm;\n
\t\t\t\t\t\tif (typeof(dx[i]) != \'undefined\' && !isNaN(dx[i])) {\n
\t\t\t\t\t\t\tmeasure += dx[i];\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\treturn measure;\n
\t\t\t\t}\n
\t\t\t\n
\t\t\t\tvar textToMeasure = svg.compressSpaces(this.getText());\n
\t\t\t\tif (!ctx.measureText) return textToMeasure.length * 10;\n
\t\t\t\t\n
\t\t\t\tctx.save();\n
\t\t\t\tthis.setContext(ctx);\n
\t\t\t\tvar width = ctx.measureText(textToMeasure).width;\n
\t\t\t\tctx.restore();\n
\t\t\t\treturn width;\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.TextElementBase.prototype = new svg.Element.RenderedElementBase;\n
\t\t\n
\t\t// tspan \n
\t\tsvg.Element.tspan = function(node) {\n
\t\t\tthis.base = svg.Element.TextElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.text = node.nodeType == 3 ? node.nodeValue : // text\n
\t\t\t\t\t\tnode.childNodes.length > 0 ? node.childNodes[0].nodeValue : // element\n
\t\t\t\t\t\tnode.text;\n
\t\t\tthis.getText = function() {\n
\t\t\t\treturn this.text;\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.tspan.prototype = new svg.Element.TextElementBase;\n
\t\t\n
\t\t// tref\n
\t\tsvg.Element.tref = function(node) {\n
\t\t\tthis.base = svg.Element.TextElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.getText = function() {\n
\t\t\t\tvar element = this.attribute(\'xlink:href\').Definition.getDefinition();\n
\t\t\t\tif (element != null) return element.children[0].getText();\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.tref.prototype = new svg.Element.TextElementBase;\t\t\n
\t\t\n
\t\t// a element\n
\t\tsvg.Element.a = function(node) {\n
\t\t\tthis.base = svg.Element.TextElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.hasText = true;\n
\t\t\tfor (var i=0; i<node.childNodes.length; i++) {\n
\t\t\t\tif (node.childNodes[i].nodeType != 3) this.hasText = false;\n
\t\t\t}\n
\t\t\t\n
\t\t\t// this might contain text\n
\t\t\tthis.text = this.hasText ? node.childNodes[0].nodeValue : \'\';\n
\t\t\tthis.getText = function() {\n
\t\t\t\treturn this.text;\n
\t\t\t}\t\t\n
\n
\t\t\tthis.baseRenderChildren = this.renderChildren;\n
\t\t\tthis.renderChildren = function(ctx) {\n
\t\t\t\tif (this.hasText) {\n
\t\t\t\t\t// render as text element\n
\t\t\t\t\tthis.baseRenderChildren(ctx);\n
\t\t\t\t\tvar fontSize = new svg.Property(\'fontSize\', svg.Font.Parse(svg.ctx.font).fontSize);\n
\t\t\t\t\tsvg.Mouse.checkBoundingBox(this, new svg.BoundingBox(this.x, this.y - fontSize.Length.toPixels(\'y\'), this.x + this.measureText(ctx), this.y));\t\t\t\t\t\n
\t\t\t\t}\n
\t\t\t\telse {\n
\t\t\t\t\t// render as temporary group\n
\t\t\t\t\tvar g = new svg.Element.g();\n
\t\t\t\t\tg.children = this.children;\n
\t\t\t\t\tg.parent = this;\n
\t\t\t\t\tg.render(ctx);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.onclick = function() {\n
\t\t\t\twindow.open(this.attribute(\'xlink:href\').value);\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.onmousemove = function() {\n
\t\t\t\tsvg.ctx.canvas.style.cursor = \'pointer\';\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.a.prototype = new svg.Element.TextElementBase;\t\t\n
\t\t\n
\t\t// image element\n
\t\tsvg.Element.image = function(node) {\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tsvg.Images.push(this);\n
\t\t\tthis.img = document.createElement(\'img\');\n
\t\t\tthis.loaded = false;\n
\t\t\tvar that = this;\n
\t\t\tthis.img.onload = function() { that.loaded = true; }\n
\t\t\tthis.img.src = this.attribute(\'xlink:href\').value;\n
\t\t\t\n
\t\t\tthis.renderChildren = function(ctx) {\n
\t\t\t\tvar x = this.attribute(\'x\').Length.toPixels(\'x\');\n
\t\t\t\tvar y = this.attribute(\'y\').Length.toPixels(\'y\');\n
\t\t\t\t\n
\t\t\t\tvar width = this.attribute(\'width\').Length.toPixels(\'x\');\n
\t\t\t\tvar height = this.attribute(\'height\').Length.toPixels(\'y\');\t\t\t\n
\t\t\t\tif (width == 0 || height == 0) return;\n
\t\t\t\n
\t\t\t\tctx.save();\n
\t\t\t\tctx.translate(x, y);\n
\t\t\t\tsvg.AspectRatio(ctx,\n
\t\t\t\t\t\t\t\tthis.attribute(\'preserveAspectRatio\').value,\n
\t\t\t\t\t\t\t\twidth,\n
\t\t\t\t\t\t\t\tthis.img.width,\n
\t\t\t\t\t\t\t\theight,\n
\t\t\t\t\t\t\t\tthis.img.height,\n
\t\t\t\t\t\t\t\t0,\n
\t\t\t\t\t\t\t\t0);\t\n
\t\t\t\tctx.drawImage(this.img, 0, 0);\t\t\t\n
\t\t\t\tctx.restore();\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.image.prototype = new svg.Element.RenderedElementBase;\n
\t\t\n
\t\t// group element\n
\t\tsvg.Element.g = function(node) {\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.getBoundingBox = function() {\n
\t\t\t\tvar bb = new svg.BoundingBox();\n
\t\t\t\tfor (var i=0; i<this.children.length; i++) {\n
\t\t\t\t\tbb.addBoundingBox(this.children[i].getBoundingBox());\n
\t\t\t\t}\n
\t\t\t\treturn bb;\n
\t\t\t};\n
\t\t}\n
\t\tsvg.Element.g.prototype = new svg.Element.RenderedElementBase;\n
\n
\t\t// symbol element\n
\t\tsvg.Element.symbol = function(node) {\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.baseSetContext = this.setContext;\n
\t\t\tthis.setContext = function(ctx) {\t\t\n
\t\t\t\tthis.baseSetContext(ctx);\n
\t\t\t\t\n
\t\t\t\t// viewbox\n
\t\t\t\tif (this.attribute(\'viewBox\').hasValue()) {\t\t\t\t\n
\t\t\t\t\tvar viewBox = svg.ToNumberArray(this.attribute(\'viewBox\').value);\n
\t\t\t\t\tvar minX = viewBox[0];\n
\t\t\t\t\tvar minY = viewBox[1];\n
\t\t\t\t\twidth = viewBox[2];\n
\t\t\t\t\theight = viewBox[3];\n
\t\t\t\t\t\n
\t\t\t\t\tsvg.AspectRatio(ctx,\n
\t\t\t\t\t\t\t\t\tthis.attribute(\'preserveAspectRatio\').value, \n
\t\t\t\t\t\t\t\t\tthis.attribute(\'width\').Length.toPixels(\'x\'),\n
\t\t\t\t\t\t\t\t\twidth,\n
\t\t\t\t\t\t\t\t\tthis.attribute(\'height\').Length.toPixels(\'y\'),\n
\t\t\t\t\t\t\t\t\theight,\n
\t\t\t\t\t\t\t\t\tminX,\n
\t\t\t\t\t\t\t\t\tminY);\n
\n
\t\t\t\t\tsvg.ViewPort.SetCurrent(viewBox[2], viewBox[3]);\t\t\t\t\t\t\n
\t\t\t\t}\n
\t\t\t}\t\t\t\n
\t\t}\n
\t\tsvg.Element.symbol.prototype = new svg.Element.RenderedElementBase;\t\t\n
\t\t\t\n
\t\t// style element\n
\t\tsvg.Element.style = function(node) { \n
\t\t\tthis.base = svg.Element.ElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\t// text, or spaces then CDATA\n
\t\t\tvar css = node.childNodes[0].nodeValue + (node.childNodes.length > 1 ? node.childNodes[1].nodeValue : \'\');\n
\t\t\tcss = css.replace(/(\\/\\*([^*]|[\\r\\n]|(\\*+([^*\\/]|[\\r\\n])))*\\*+\\/)|(^[\\s]*\\/\\/.*)/gm, \'\'); // remove comments\n
\t\t\tcss = svg.compressSpaces(css); // replace whitespace\n
\t\t\tvar cssDefs = css.split(\'}\');\n
\t\t\tfor (var i=0; i<cssDefs.length; i++) {\n
\t\t\t\tif (svg.trim(cssDefs[i]) != \'\') {\n
\t\t\t\t\tvar cssDef = cssDefs[i].split(\'{\');\n
\t\t\t\t\tvar cssClasses = cssDef[0].split(\',\');\n
\t\t\t\t\tvar cssProps = cssDef[1].split(\';\');\n
\t\t\t\t\tfor (var j=0; j<cssClasses.length; j++) {\n
\t\t\t\t\t\tvar cssClass = svg.trim(cssClasses[j]);\n
\t\t\t\t\t\tif (cssClass != \'\') {\n
\t\t\t\t\t\t\tvar props = {};\n
\t\t\t\t\t\t\tfor (var k=0; k<cssProps.length; k++) {\n
\t\t\t\t\t\t\t\tvar prop = cssProps[k].indexOf(\':\');\n
\t\t\t\t\t\t\t\tvar name = cssProps[k].substr(0, prop);\n
\t\t\t\t\t\t\t\tvar value = cssProps[k].substr(prop + 1, cssProps[k].length - prop);\n
\t\t\t\t\t\t\t\tif (name != null && value != null) {\n
\t\t\t\t\t\t\t\t\tprops[svg.trim(name)] = new svg.Property(svg.trim(name), svg.trim(value));\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tsvg.Styles[cssClass] = props;\n
\t\t\t\t\t\t\tif (cssClass == \'@font-face\') {\n
\t\t\t\t\t\t\t\tvar fontFamily = props[\'font-family\'].value.replace(/"/g,\'\');\n
\t\t\t\t\t\t\t\tvar srcs = props[\'src\'].value.split(\',\');\n
\t\t\t\t\t\t\t\tfor (var s=0; s<srcs.length; s++) {\n
\t\t\t\t\t\t\t\t\tif (srcs[s].indexOf(\'format("svg")\') > 0) {\n
\t\t\t\t\t\t\t\t\t\tvar urlStart = srcs[s].indexOf(\'url\');\n
\t\t\t\t\t\t\t\t\t\tvar urlEnd = srcs[s].indexOf(\')\', urlStart);\n
\t\t\t\t\t\t\t\t\t\tvar url = srcs[s].substr(urlStart + 5, urlEnd - urlStart - 6);\n
\t\t\t\t\t\t\t\t\t\tvar doc = svg.parseXml(svg.ajax(url));\n
\t\t\t\t\t\t\t\t\t\tvar fonts = doc.getElementsByTagName(\'font\');\n
\t\t\t\t\t\t\t\t\t\tfor (var f=0; f<fonts.length; f++) {\n
\t\t\t\t\t\t\t\t\t\t\tvar font = svg.CreateElement(fonts[f]);\n
\t\t\t\t\t\t\t\t\t\t\tsvg.Definitions[fontFamily] = font;\n
\t\t\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.style.prototype = new svg.Element.ElementBase;\n
\t\t\n
\t\t// use element \n
\t\tsvg.Element.use = function(node) {\n
\t\t\tthis.base = svg.Element.RenderedElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.baseSetContext = this.setContext;\n
\t\t\tthis.setContext = function(ctx) {\n
\t\t\t\tthis.baseSetContext(ctx);\n
\t\t\t\tif (this.attribute(\'x\').hasValue()) ctx.translate(this.attribute(\'x\').Length.toPixels(\'x\'), 0);\n
\t\t\t\tif (this.attribute(\'y\').hasValue()) ctx.translate(0, this.attribute(\'y\').Length.toPixels(\'y\'));\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.getDefinition = function() {\n
\t\t\t\tvar element = this.attribute(\'xlink:href\').Definition.getDefinition();\n
\t\t\t\tif (this.attribute(\'width\').hasValue()) element.attribute(\'width\', true).value = this.attribute(\'width\').value;\n
\t\t\t\tif (this.attribute(\'height\').hasValue()) element.attribute(\'height\', true).value = this.attribute(\'height\').value;\n
\t\t\t\treturn element;\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.path = function(ctx) {\n
\t\t\t\tvar element = this.getDefinition();\n
\t\t\t\tif (element != null) element.path(ctx);\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.renderChildren = function(ctx) {\n
\t\t\t\tvar element = this.getDefinition();\n
\t\t\t\tif (element != null) element.render(ctx);\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.use.prototype = new svg.Element.RenderedElementBase;\n
\t\t\n
\t\t// mask element\n
\t\tsvg.Element.mask = function(node) {\n
\t\t\tthis.base = svg.Element.ElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\t\t\t\n
\t\t\tthis.apply = function(ctx, element) {\n
\t\t\t\t// render as temp svg\t\n
\t\t\t\tvar x = this.attribute(\'x\').Length.toPixels(\'x\');\n
\t\t\t\tvar y = this.attribute(\'y\').Length.toPixels(\'y\');\n
\t\t\t\tvar width = this.attribute(\'width\').Length.toPixels(\'x\');\n
\t\t\t\tvar height = this.attribute(\'height\').Length.toPixels(\'y\');\n
\t\t\t\t\n
\t\t\t\t// temporarily remove mask to avoid recursion\n
\t\t\t\tvar mask = element.attribute(\'mask\').value;\n
\t\t\t\telement.attribute(\'mask\').value = \'\';\n
\t\t\t\t\n
\t\t\t\t\tvar cMask = document.createElement(\'canvas\');\n
\t\t\t\t\tcMask.width = x + width;\n
\t\t\t\t\tcMask.height = y + height;\n
\t\t\t\t\tvar maskCtx = cMask.getContext(\'2d\');\n
\t\t\t\t\tthis.renderChildren(maskCtx);\n
\t\t\t\t\n
\t\t\t\t\tvar c = document.createElement(\'canvas\');\n
\t\t\t\t\tc.width = x + width;\n
\t\t\t\t\tc.height = y + height;\n
\t\t\t\t\tvar tempCtx = c.getContext(\'2d\');\n
\t\t\t\t\telement.render(tempCtx);\n
\t\t\t\t\ttempCtx.globalCompositeOperation = \'destination-in\';\n
\t\t\t\t\ttempCtx.fillStyle = maskCtx.createPattern(cMask, \'no-repeat\');\n
\t\t\t\t\ttempCtx.fillRect(0, 0, x + width, y + height);\n
\t\t\t\t\t\n
\t\t\t\t\tctx.fillStyle = tempCtx.createPattern(c, \'no-repeat\');\n
\t\t\t\t\tctx.fillRect(0, 0, x + width, y + height);\n
\t\t\t\t\t\n
\t\t\t\t// reassign mask\n
\t\t\t\telement.attribute(\'mask\').value = mask;\t\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.render = function(ctx) {\n
\t\t\t\t// NO RENDER\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.mask.prototype = new svg.Element.ElementBase;\n
\t\t\n
\t\t// clip element\n
\t\tsvg.Element.clipPath = function(node) {\n
\t\t\tthis.base = svg.Element.ElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\n
\t\t\tthis.apply = function(ctx) {\n
\t\t\t\tfor (var i=0; i<this.children.length; i++) {\n
\t\t\t\t\tif (this.children[i].path) {\n
\t\t\t\t\t\tthis.children[i].path(ctx);\n
\t\t\t\t\t\tctx.clip();\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.render = function(ctx) {\n
\t\t\t\t// NO RENDER\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.clipPath.prototype = new svg.Element.ElementBase;\n
\n
\t\t// filters\n
\t\tsvg.Element.filter = function(node) {\n
\t\t\tthis.base = svg.Element.ElementBase;\n
\t\t\tthis.base(node);\n
\t\t\t\t\t\t\n
\t\t\tthis.apply = function(ctx, element) {\n
\t\t\t\t// render as temp svg\t\n
\t\t\t\tvar bb = element.getBoundingBox();\n
\t\t\t\tvar x = this.attribute(\'x\').Length.toPixels(\'x\');\n
\t\t\t\tvar y = this.attribute(\'y\').Length.toPixels(\'y\');\n
\t\t\t\tif (x == 0 || y == 0) {\n
\t\t\t\t\tx = bb.x1;\n
\t\t\t\t\ty = bb.y1;\n
\t\t\t\t}\n
\t\t\t\tvar width = this.attribute(\'width\').Length.toPixels(\'x\');\n
\t\t\t\tvar height = this.attribute(\'height\').Length.toPixels(\'y\');\n
\t\t\t\tif (width == 0 || height == 0) {\n
\t\t\t\t\twidth = bb.width();\n
\t\t\t\t\theight = bb.height();\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t// temporarily remove filter to avoid recursion\n
\t\t\t\tvar filter = element.style(\'filter\').value;\n
\t\t\t\telement.style(\'filter\').value = \'\';\n
\t\t\t\t\n
\t\t\t\t// max filter distance\n
\t\t\t\tvar extraPercent = .20;\n
\t\t\t\tvar px = extraPercent * width;\n
\t\t\t\tvar py = extraPercent * height;\n
\t\t\t\t\n
\t\t\t\tvar c = document.createElement(\'canvas\');\n
\t\t\t\tc.width = width + 2*px;\n
\t\t\t\tc.height = height + 2*py;\n
\t\t\t\tvar tempCtx = c.getContext(\'2d\');\n
\t\t\t\ttempCtx.translate(-x + px, -y + py);\n
\t\t\t\telement.render(tempCtx);\n
\t\t\t\n
\t\t\t\t// apply filters\n
\t\t\t\tfor (var i=0; i<this.children.length; i++) {\n
\t\t\t\t\tthis.children[i].apply(tempCtx, 0, 0, width + 2*px, height + 2*py);\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t// render on me\n
\t\t\t\tctx.drawImage(c, 0, 0, width + 2*px, height + 2*py, x - px, y - py, width + 2*px, height + 2*py);\n
\t\t\t\t\n
\t\t\t\t// reassign filter\n
\t\t\t\telement.style(\'filter\', true).value = filter;\t\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.render = function(ctx) {\n
\t\t\t\t// NO RENDER\n
\t\t\t}\t\t\n
\t\t}\n
\t\tsvg.Element.filter.prototype = new svg.Element.ElementBase;\n
\t\t\n
\t\tsvg.Element.feGaussianBlur = function(node) {\n
\t\t\tthis.base = svg.Element.ElementBase;\n
\t\t\tthis.base(node);\t\n
\t\t\t\n
\t\t\tfunction make_fgauss(sigma) {\n
\t\t\t\tsigma = Math.max(sigma, 0.01);\t\t\t      \n
\t\t\t\tvar len = Math.ceil(sigma * 4.0) + 1;                     \n
\t\t\t\tmask = [];                               \n
\t\t\t\tfor (var i = 0; i < len; i++) {                             \n
\t\t\t\t\tmask[i] = Math.exp(-0.5 * (i / sigma) * (i / sigma));                                           \n
\t\t\t\t}                                                           \n
\t\t\t\treturn mask; \n
\t\t\t}\n
\t\t\t\n
\t\t\tfunction normalize(mask) {\n
\t\t\t\tvar sum = 0;\n
\t\t\t\tfor (var i = 1; i < mask.length; i++) {\n
\t\t\t\t\tsum += Math.abs(mask[i]);\n
\t\t\t\t}\n
\t\t\t\tsum = 2 * sum + Math.abs(mask[0]);\n
\t\t\t\tfor (var i = 0; i < mask.length; i++) {\n
\t\t\t\t\tmask[i] /= sum;\n
\t\t\t\t}\n
\t\t\t\treturn mask;\n
\t\t\t}\n
\t\t\t\n
\t\t\tfunction convolve_even(src, dst, mask, width, height) {\n
\t\t\t  for (var y = 0; y < height; y++) {\n
\t\t\t\tfor (var x = 0; x < width; x++) {\n
\t\t\t\t  var a = imGet(src, x, y, width, height, 3)/255;\n
\t\t\t\t  for (var rgba = 0; rgba < 4; rgba++) {\t\t\t\t\t  \n
\t\t\t\t\t  var sum = mask[0] * (a==0?255:imGet(src, x, y, width, height, rgba)) * (a==0||rgba==3?1:a);\n
\t\t\t\t\t  for (var i = 1; i < mask.length; i++) {\n
\t\t\t\t\t\tvar a1 = imGet(src, Math.max(x-i,0), y, width, height, 3)/255;\n
\t\t\t\t\t    var a2 = imGet(src, Math.min(x+i, width-1), y, width, height, 3)/255;\n
\t\t\t\t\t\tsum += mask[i] * \n
\t\t\t\t\t\t  ((a1==0?255:imGet(src, Math.max(x-i,0), y, width, height, rgba)) * (a1==0||rgba==3?1:a1) + \n
\t\t\t\t\t\t   (a2==0?255:imGet(src, Math.min(x+i, width-1), y, width, height, rgba)) * (a2==0||rgba==3?1:a2));\n
\t\t\t\t\t  }\n
\t\t\t\t\t  imSet(dst, y, x, height, width, rgba, sum);\n
\t\t\t\t  }\t\t\t  \n
\t\t\t\t}\n
\t\t\t  }\n
\t\t\t}\t\t\n
\n
\t\t\tfunction imGet(img, x, y, width, height, rgba) {\n
\t\t\t\treturn img[y*width*4 + x*4 + rgba];\n
\t\t\t}\n
\t\t\t\n
\t\t\tfunction imSet(img, x, y, width, height, rgba, val) {\n
\t\t\t\timg[y*width*4 + x*4 + rgba] = val;\n
\t\t\t}\n
\t\t\t\t\t\t\n
\t\t\tfunction blur(ctx, width, height, sigma)\n
\t\t\t{\n
\t\t\t\tvar srcData = ctx.getImageData(0, 0, width, height);\n
\t\t\t\tvar mask = make_fgauss(sigma);\n
\t\t\t\tmask = normalize(mask);\n
\t\t\t\ttmp = [];\n
\t\t\t\tconvolve_even(srcData.data, tmp, mask, width, height);\n
\t\t\t\tconvolve_even(tmp, srcData.data, mask, height, width);\n
\t\t\t\tctx.clearRect(0, 0, width, height);\n
\t\t\t\tctx.putImageData(srcData, 0, 0);\n
\t\t\t}\t\t\t\n
\t\t\n
\t\t\tthis.apply = function(ctx, x, y, width, height) {\n
\t\t\t\t// assuming x==0 && y==0 for now\n
\t\t\t\tblur(ctx, width, height, this.attribute(\'stdDeviation\').numValue());\n
\t\t\t}\n
\t\t}\n
\t\tsvg.Element.filter.prototype = new svg.Element.feGaussianBlur;\n
\t\t\n
\t\t// title element, do nothing\n
\t\tsvg.Element.title = function(node) {\n
\t\t}\n
\t\tsvg.Element.title.prototype = new svg.Element.ElementBase;\n
\n
\t\t// desc element, do nothing\n
\t\tsvg.Element.desc = function(node) {\n
\t\t}\n
\t\tsvg.Element.desc.prototype = new svg.Element.ElementBase;\t\t\n
\t\t\n
\t\tsvg.Element.MISSING = function(node) {\n
\t\t\tconsole.log(\'ERROR: Element \\\'\' + node.nodeName + \'\\\' not yet implemented.\');\n
\t\t}\n
\t\tsvg.Element.MISSING.prototype = new svg.Element.ElementBase;\n
\t\t\n
\t\t// element factory\n
\t\tsvg.CreateElement = function(node) {\t\n
\t\t\tvar className = node.nodeName.replace(/^[^:]+:/,\'\'); // remove namespace\n
\t\t\tclassName = className.replace(/\\-/g,\'\'); // remove dashes\n
\t\t\tvar e = null;\n
\t\t\tif (typeof(svg.Element[className]) != \'undefined\') {\n
\t\t\t\te = new svg.Element[className](node);\n
\t\t\t}\n
\t\t\telse {\n
\t\t\t\te = new svg.Element.MISSING(node);\n
\t\t\t}\n
\n
\t\t\te.type = node.nodeName;\n
\t\t\treturn e;\n
\t\t}\n
\t\t\t\t\n
\t\t// load from url\n
\t\tsvg.load = function(ctx, url) {\n
\t\t\tsvg.loadXml(ctx, svg.ajax(url));\n
\t\t}\n
\t\t\n
\t\t// load from xml\n
\t\tsvg.loadXml = function(ctx, xml) {\n
\t\t\tsvg.loadXmlDoc(ctx, svg.parseXml(xml));\n
\t\t}\n
\t\t\n
\t\tsvg.loadXmlDoc = function(ctx, dom) {\n
\t\t\tsvg.init(ctx);\n
\t\t\t\n
\t\t\tvar mapXY = function(p) {\n
\t\t\t\tvar e = ctx.canvas;\n
\t\t\t\twhile (e) {\n
\t\t\t\t\tp.x -= e.offsetLeft;\n
\t\t\t\t\tp.y -= e.offsetTop;\n
\t\t\t\t\te = e.offsetParent;\n
\t\t\t\t}\n
\t\t\t\tif (window.scrollX) p.x += window.scrollX;\n
\t\t\t\tif (window.scrollY) p.y += window.scrollY;\n
\t\t\t\treturn p;\n
\t\t\t}\n
\t\t\t\n
\t\t\t// bind mouse\n
\t\t\tif (svg.opts[\'ignoreMouse\'] != true) {\n
\t\t\t\tctx.canvas.onclick = function(e) {\n
\t\t\t\t\tvar p = mapXY(new svg.Point(e != null ? e.clientX : event.clientX, e != null ? e.clientY : event.clientY));\n
\t\t\t\t\tsvg.Mouse.onclick(p.x, p.y);\n
\t\t\t\t};\n
\t\t\t\tctx.canvas.onmousemove = function(e) {\n
\t\t\t\t\tvar p = mapXY(new svg.Point(e != null ? e.clientX : event.clientX, e != null ? e.clientY : event.clientY));\n
\t\t\t\t\tsvg.Mouse.onmousemove(p.x, p.y);\n
\t\t\t\t};\n
\t\t\t}\n
\t\t\n
\t\t\tvar e = svg.CreateElement(dom.documentElement);\n
\t\t\te.root = true;\n
\t\t\t\t\t\n
\t\t\t// render loop\n
\t\t\tvar isFirstRender = true;\n
\t\t\tvar draw = function() {\n
\t\t\t\tsvg.ViewPort.Clear();\n
\t\t\t\tif (ctx.canvas.parentNode) svg.ViewPort.SetCurrent(ctx.canvas.parentNode.clientWidth, ctx.canvas.parentNode.clientHeight);\n
\t\t\t\n
\t\t\t\tif (svg.opts[\'ignoreDimensions\'] != true) {\n
\t\t\t\t\t// set canvas size\n
\t\t\t\t\tif (e.style(\'width\').hasValue()) {\n
\t\t\t\t\t\tctx.canvas.width = e.style(\'width\').Length.toPixels(\'x\');\n
\t\t\t\t\t\tctx.canvas.style.width = ctx.canvas.width + \'px\';\n
\t\t\t\t\t}\n
\t\t\t\t\tif (e.style(\'height\').hasValue()) {\n
\t\t\t\t\t\tctx.canvas.height = e.style(\'height\').Length.toPixels(\'y\');\n
\t\t\t\t\t\tctx.canvas.style.height = ctx.canvas.height + \'px\';\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\tvar cWidth = ctx.canvas.clientWidth || ctx.canvas.width;\n
\t\t\t\tvar cHeight = ctx.canvas.clientHeight || ctx.canvas.height;\n
\t\t\t\tsvg.ViewPort.SetCurrent(cWidth, cHeight);\t\t\n
\t\t\t\t\n
\t\t\t\tif (svg.opts != null && svg.opts[\'offsetX\'] != null) e.attribute(\'x\', true).value = svg.opts[\'offsetX\'];\n
\t\t\t\tif (svg.opts != null && svg.opts[\'offsetY\'] != null) e.attribute(\'y\', true).value = svg.opts[\'offsetY\'];\n
\t\t\t\tif (svg.opts != null && svg.opts[\'scaleWidth\'] != null && svg.opts[\'scaleHeight\'] != null) {\n
\t\t\t\t\tvar xRatio = 1, yRatio = 1;\n
\t\t\t\t\tif (e.attribute(\'width\').hasValue()) xRatio = e.attribute(\'width\').Length.toPixels(\'x\') / svg.opts[\'scaleWidth\'];\n
\t\t\t\t\tif (e.attribute(\'height\').hasValue()) yRatio = e.attribute(\'height\').Length.toPixels(\'y\') / svg.opts[\'scaleHeight\'];\n
\t\t\t\t\n
\t\t\t\t\te.attribute(\'width\', true).value = svg.opts[\'scaleWidth\'];\n
\t\t\t\t\te.attribute(\'height\', true).value = svg.opts[\'scaleHeight\'];\t\t\t\n
\t\t\t\t\te.attribute(\'viewBox\', true).value = \'0 0 \' + (cWidth * xRatio) + \' \' + (cHeight * yRatio);\n
\t\t\t\t\te.attribute(\'preserveAspectRatio\', true).value = \'none\';\n
\t\t\t\t}\n
\t\t\t\n
\t\t\t\t// clear and render\n
\t\t\t\tif (svg.opts[\'ignoreClear\'] != true) {\n
\t\t\t\t\tctx.clearRect(0, 0, cWidth, cHeight);\n
\t\t\t\t}\n
\t\t\t\te.render(ctx);\n
\t\t\t\tif (isFirstRender) {\n
\t\t\t\t\tisFirstRender = false;\n
\t\t\t\t\tif (svg.opts != null && typeof(svg.opts[\'renderCallback\']) == \'function\') svg.opts[\'renderCallback\']();\n
\t\t\t\t}\t\t\t\n
\t\t\t}\n
\t\t\t\n
\t\t\tvar waitingForImages = true;\n
\t\t\tif (svg.ImagesLoaded()) {\n
\t\t\t\twaitingForImages = false;\n
\t\t\t\tdraw();\n
\t\t\t}\n
\t\t\tsvg.intervalID = setInterval(function() { \n
\t\t\t\tvar needUpdate = false;\n
\t\t\t\t\n
\t\t\t\tif (waitingForImages && svg.ImagesLoaded()) {\n
\t\t\t\t\twaitingForImages = false;\n
\t\t\t\t\tneedUpdate = true;\n
\t\t\t\t}\n
\t\t\t\n
\t\t\t\t// need update from mouse events?\n
\t\t\t\tif (svg.opts[\'ignoreMouse\'] != true) {\n
\t\t\t\t\tneedUpdate = needUpdate | svg.Mouse.hasEvents();\n
\t\t\t\t}\n
\t\t\t\n
\t\t\t\t// need update from animations?\n
\t\t\t\tif (svg.opts[\'ignoreAnimation\'] != true) {\n
\t\t\t\t\tfor (var i=0; i<svg.Animations.length; i++) {\n
\t\t\t\t\t\tneedUpdate = needUpdate | svg.Animations[i].update(1000 / svg.FRAMERATE);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t// need update from redraw?\n
\t\t\t\tif (svg.opts != null && typeof(svg.opts[\'forceRedraw\']) == \'function\') {\n
\t\t\t\t\tif (svg.opts[\'forceRedraw\']() == true) needUpdate = true;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t// render if needed\n
\t\t\t\tif (needUpdate) {\n
\t\t\t\t\tdraw();\t\t\t\t\n
\t\t\t\t\tsvg.Mouse.runEvents(); // run and clear our events\n
\t\t\t\t}\n
\t\t\t}, 1000 / svg.FRAMERATE);\n
\t\t}\n
\t\t\n
\t\tsvg.stop = function() {\n
\t\t\tif (svg.intervalID) {\n
\t\t\t\tclearInterval(svg.intervalID);\n
\t\t\t}\n
\t\t}\n
\t\t\n
\t\tsvg.Mouse = new (function() {\n
\t\t\tthis.events = [];\n
\t\t\tthis.hasEvents = function() { return this.events.length != 0; }\n
\t\t\n
\t\t\tthis.onclick = function(x, y) {\n
\t\t\t\tthis.events.push({ type: \'onclick\', x: x, y: y, \n
\t\t\t\t\trun: function(e) { if (e.onclick) e.onclick(); }\n
\t\t\t\t});\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.onmousemove = function(x, y) {\n
\t\t\t\tthis.events.push({ type: \'onmousemove\', x: x, y: y,\n
\t\t\t\t\trun: function(e) { if (e.onmousemove) e.onmousemove(); }\n
\t\t\t\t});\n
\t\t\t}\t\t\t\n
\t\t\t\n
\t\t\tthis.eventElements = [];\n
\t\t\t\n
\t\t\tthis.checkPath = function(element, ctx) {\n
\t\t\t\tfor (var i=0; i<this.events.length; i++) {\n
\t\t\t\t\tvar e = this.events[i];\n
\t\t\t\t\tif (ctx.isPointInPath && ctx.isPointInPath(e.x, e.y)) this.eventElements[i] = element;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.checkBoundingBox = function(element, bb) {\n
\t\t\t\tfor (var i=0; i<this.events.length; i++) {\n
\t\t\t\t\tvar e = this.events[i];\n
\t\t\t\t\tif (bb.isPointInBox(e.x, e.y)) this.eventElements[i] = element;\n
\t\t\t\t}\t\t\t\n
\t\t\t}\n
\t\t\t\n
\t\t\tthis.runEvents = function() {\n
\t\t\t\tsvg.ctx.canvas.style.cursor = \'\';\n
\t\t\t\t\n
\t\t\t\tfor (var i=0; i<this.events.length; i++) {\n
\t\t\t\t\tvar e = this.events[i];\n
\t\t\t\t\tvar element = this.eventElements[i];\n
\t\t\t\t\twhile (element) {\n
\t\t\t\t\t\te.run(element);\n
\t\t\t\t\t\telement = element.parent;\n
\t\t\t\t\t}\n
\t\t\t\t}\t\t\n
\t\t\t\n
\t\t\t\t// done running, clear\n
\t\t\t\tthis.events = []; \n
\t\t\t\tthis.eventElements = [];\n
\t\t\t}\n
\t\t});\n
\t\t\n
\t\treturn svg;\n
\t}\n
})();\n
\n
if (CanvasRenderingContext2D) {\n
\tCanvasRenderingContext2D.prototype.drawSvg = function(s, dx, dy, dw, dh) {\n
\t\tcanvg(this.canvas, s, { \n
\t\t\tignoreMouse: true, \n
\t\t\tignoreAnimation: true, \n
\t\t\tignoreDimensions: true, \n
\t\t\tignoreClear: true, \n
\t\t\toffsetX: dx, \n
\t\t\toffsetY: dy, \n
\t\t\tscaleWidth: dw, \n
\t\t\tscaleHeight: dh\n
\t\t});\n
\t}\n
}

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>85700</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
