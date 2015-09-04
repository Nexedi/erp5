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
            <value> <string>ts40515059.55</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>math.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals svgedit*/\n
/*jslint vars: true, eqeq: true */\n
/**\n
 * Package: svedit.math\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Alexis Deveria\n
 * Copyright(c) 2010 Jeff Schiller\n
 */\n
\n
// Dependencies:\n
// None.\n
 \n
/**\n
* @typedef AngleCoord45\n
* @type {object}\n
* @property {number} x - The angle-snapped x value\n
* @property {number} y - The angle-snapped y value\n
* @property {number} a - The angle at which to snap\n
*/\n
\n
(function() {\'use strict\';\n
\n
if (!svgedit.math) {\n
\tsvgedit.math = {};\n
}\n
\n
// Constants\n
var NEAR_ZERO = 1e-14;\n
\n
// Throw away SVGSVGElement used for creating matrices/transforms.\n
var svg = document.createElementNS(svgedit.NS.SVG, \'svg\');\n
\n
/**\n
 * A (hopefully) quicker function to transform a point by a matrix\n
 * (this function avoids any DOM calls and just does the math)\n
 * @param {number} x - Float representing the x coordinate\n
 * @param {number} y - Float representing the y coordinate\n
 * @param {SVGMatrix} m - Matrix object to transform the point with\n
 * @returns {object} An x, y object representing the transformed point\n
*/\n
svgedit.math.transformPoint = function (x, y, m) {\n
\treturn { x: m.a * x + m.c * y + m.e, y: m.b * x + m.d * y + m.f};\n
};\n
\n
\n
/**\n
 * Helper function to check if the matrix performs no actual transform \n
 * (i.e. exists for identity purposes)\n
 * @param {SVGMatrix} m - The matrix object to check\n
 * @returns {boolean} Indicates whether or not the matrix is 1,0,0,1,0,0\n
*/\n
svgedit.math.isIdentity = function (m) {\n
\treturn (m.a === 1 && m.b === 0 && m.c === 0 && m.d === 1 && m.e === 0 && m.f === 0);\n
};\n
\n
\n
/**\n
 * This function tries to return a SVGMatrix that is the multiplication m1*m2.\n
 * We also round to zero when it\'s near zero\n
 * @param {...SVGMatrix} matr - Two or more matrix objects to multiply\n
 * @returns {SVGMatrix} The matrix object resulting from the calculation\n
*/\n
svgedit.math.matrixMultiply = function (matr) {\n
\tvar args = arguments, i = args.length, m = args[i-1];\n
\n
\twhile (i-- > 1) {\n
\t\tvar m1 = args[i-1];\n
\t\tm = m1.multiply(m);\n
\t}\n
\tif (Math.abs(m.a) < NEAR_ZERO) {m.a = 0;}\n
\tif (Math.abs(m.b) < NEAR_ZERO) {m.b = 0;}\n
\tif (Math.abs(m.c) < NEAR_ZERO) {m.c = 0;}\n
\tif (Math.abs(m.d) < NEAR_ZERO) {m.d = 0;}\n
\tif (Math.abs(m.e) < NEAR_ZERO) {m.e = 0;}\n
\tif (Math.abs(m.f) < NEAR_ZERO) {m.f = 0;}\n
\n
\treturn m;\n
};\n
\n
/**\n
 * See if the given transformlist includes a non-indentity matrix transform\n
 * @param {object} [tlist] - The transformlist to check\n
 * @returns {boolean} Whether or not a matrix transform was found\n
*/\n
svgedit.math.hasMatrixTransform = function (tlist) {\n
\tif (!tlist) {return false;}\n
\tvar num = tlist.numberOfItems;\n
\twhile (num--) {\n
\t\tvar xform = tlist.getItem(num);\n
\t\tif (xform.type == 1 && !svgedit.math.isIdentity(xform.matrix)) {return true;}\n
\t}\n
\treturn false;\n
};\n
\n
/**\n
 * Transforms a rectangle based on the given matrix\n
 * @param {number} l - Float with the box\'s left coordinate\n
 * @param {number} t - Float with the box\'s top coordinate\n
 * @param {number} w - Float with the box width\n
 * @param {number} h - Float with the box height\n
 * @param {SVGMatrix} m - Matrix object to transform the box by\n
 * @returns {object} An object with the following values:\n
 * tl - The top left coordinate (x,y object)\n
 * tr - The top right coordinate (x,y object)\n
 * bl - The bottom left coordinate (x,y object)\n
 * br - The bottom right coordinate (x,y object)\n
 * aabox - Object with the following values:\n
 * x - Float with the axis-aligned x coordinate\n
 * y - Float with the axis-aligned y coordinate\n
 * width - Float with the axis-aligned width coordinate\n
 * height - Float with the axis-aligned height coordinate\n
*/\n
svgedit.math.transformBox = function (l, t, w, h, m) {\n
\tvar transformPoint = svgedit.math.transformPoint,\n
\n
\t\ttl = transformPoint(l, t, m),\n
\t\ttr = transformPoint((l + w), t, m),\n
\t\tbl = transformPoint(l, (t + h), m),\n
\t\tbr = transformPoint((l + w), (t + h), m),\n
\n
\t\tminx = Math.min(tl.x, tr.x, bl.x, br.x),\n
\t\tmaxx = Math.max(tl.x, tr.x, bl.x, br.x),\n
\t\tminy = Math.min(tl.y, tr.y, bl.y, br.y),\n
\t\tmaxy = Math.max(tl.y, tr.y, bl.y, br.y);\n
\n
\treturn {\n
\t\ttl: tl,\n
\t\ttr: tr,\n
\t\tbl: bl,\n
\t\tbr: br,\n
\t\taabox: {\n
\t\t\tx: minx,\n
\t\t\ty: miny,\n
\t\t\twidth: (maxx - minx),\n
\t\t\theight: (maxy - miny)\n
\t\t}\n
\t};\n
};\n
\n
/**\n
 * This returns a single matrix Transform for a given Transform List\n
 * (this is the equivalent of SVGTransformList.consolidate() but unlike\n
 * that method, this one does not modify the actual SVGTransformList)\n
 * This function is very liberal with its min, max arguments\n
 * @param {object} tlist - The transformlist object\n
 * @param {integer} [min=0] - Optional integer indicating start transform position\n
 * @param {integer} [max] - Optional integer indicating end transform position;\n
 *   defaults to one less than the tlist\'s numberOfItems\n
 * @returns {object} A single matrix transform object\n
*/\n
svgedit.math.transformListToTransform = function (tlist, min, max) {\n
\tif (tlist == null) {\n
\t\t// Or should tlist = null have been prevented before this?\n
\t\treturn svg.createSVGTransformFromMatrix(svg.createSVGMatrix());\n
\t}\n
\tmin = min || 0;\n
\tmax = max || (tlist.numberOfItems - 1);\n
\tmin = parseInt(min, 10);\n
\tmax = parseInt(max, 10);\n
\tif (min > max) { var temp = max; max = min; min = temp; }\n
\tvar m = svg.createSVGMatrix();\n
\tvar i;\n
\tfor (i = min; i <= max; ++i) {\n
\t\t// if our indices are out of range, just use a harmless identity matrix\n
\t\tvar mtom = (i >= 0 && i < tlist.numberOfItems ? \n
\t\t\t\t\t\ttlist.getItem(i).matrix :\n
\t\t\t\t\t\tsvg.createSVGMatrix());\n
\t\tm = svgedit.math.matrixMultiply(m, mtom);\n
\t}\n
\treturn svg.createSVGTransformFromMatrix(m);\n
};\n
\n
\n
/**\n
 * Get the matrix object for a given element\n
 * @param {Element} elem - The DOM element to check\n
 * @returns {SVGMatrix} The matrix object associated with the element\'s transformlist\n
*/\n
svgedit.math.getMatrix = function (elem) {\n
\tvar tlist = svgedit.transformlist.getTransformList(elem);\n
\treturn svgedit.math.transformListToTransform(tlist).matrix;\n
};\n
\n
\n
/**\n
 * Returns a 45 degree angle coordinate associated with the two given\n
 * coordinates\n
 * @param {number} x1 - First coordinate\'s x value\n
 * @param {number} x2 - Second coordinate\'s x value\n
 * @param {number} y1 - First coordinate\'s y value\n
 * @param {number} y2 - Second coordinate\'s y value\n
 * @returns {AngleCoord45}\n
*/\n
svgedit.math.snapToAngle = function (x1, y1, x2, y2) {\n
\tvar snap = Math.PI / 4; // 45 degrees\n
\tvar dx = x2 - x1;\n
\tvar dy = y2 - y1;\n
\tvar angle = Math.atan2(dy, dx);\n
\tvar dist = Math.sqrt(dx * dx + dy * dy);\n
\tvar snapangle = Math.round(angle / snap) * snap;\n
\n
\treturn {\n
\t\tx: x1 + dist * Math.cos(snapangle),\n
\t\ty: y1 + dist * Math.sin(snapangle),\n
\t\ta: snapangle\n
\t};\n
};\n
\n
\n
/**\n
 * Check if two rectangles (BBoxes objects) intersect each other\n
 * @param {SVGRect} r1 - The first BBox-like object\n
 * @param {SVGRect} r2 - The second BBox-like object\n
 * @returns {boolean} True if rectangles intersect\n
 */\n
svgedit.math.rectsIntersect = function (r1, r2) {\n
\treturn r2.x < (r1.x + r1.width) &&\n
\t\t(r2.x + r2.width) > r1.x &&\n
\t\tr2.y < (r1.y + r1.height) &&\n
\t\t(r2.y + r2.height) > r1.y;\n
};\n
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
            <value> <int>6987</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
