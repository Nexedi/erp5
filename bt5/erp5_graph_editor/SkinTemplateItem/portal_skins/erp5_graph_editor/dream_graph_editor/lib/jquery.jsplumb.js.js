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
            <value> <string>ts25570731.08</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.jsplumb.js</string> </value>
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
            <value> <int>444768</int> </value>
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

/**\n
* jsBezier-0.6\n
*\n
* Copyright (c) 2010 - 2013 Simon Porritt (simon.porritt@gmail.com)\n
*\n
* licensed under the MIT license.\n
* \n
* a set of Bezier curve functions that deal with Beziers, used by jsPlumb, and perhaps useful for other people.  These functions work with Bezier\n
* curves of arbitrary degree.\n
*\n
* - functions are all in the \'jsBezier\' namespace.  \n
* \n
* - all input points should be in the format {x:.., y:..}. all output points are in this format too.\n
* \n
* - all input curves should be in the format [ {x:.., y:..}, {x:.., y:..}, {x:.., y:..}, {x:.., y:..} ]\n
* \n
* - \'location\' as used as an input here refers to a decimal in the range 0-1 inclusive, which indicates a point some proportion along the length\n
* of the curve.  location as output has the same format and meaning.\n
* \n
* \n
* Function List:\n
* --------------\n
* \n
* distanceFromCurve(point, curve)\n
* \n
* \tCalculates the distance that the given point lies from the given Bezier.  Note that it is computed relative to the center of the Bezier,\n
* so if you have stroked the curve with a wide pen you may wish to take that into account!  The distance returned is relative to the values \n
* of the curve and the point - it will most likely be pixels.\n
* \n
* gradientAtPoint(curve, location)\n
* \n
* \tCalculates the gradient to the curve at the given location, as a decimal between 0 and 1 inclusive.\n
*\n
* gradientAtPointAlongCurveFrom (curve, location)\n
*\n
*\tCalculates the gradient at the point on the given curve that is \'distance\' units from location. \n
* \n
* nearestPointOnCurve(point, curve) \n
* \n
*\tCalculates the nearest point to the given point on the given curve.  The return value of this is a JS object literal, containing both the\n
*point\'s coordinates and also the \'location\' of the point (see above), for example:  { point:{x:551,y:150}, location:0.263365 }.\n
* \n
* pointOnCurve(curve, location)\n
* \n
* \tCalculates the coordinates of the point on the given Bezier curve at the given location.  \n
* \t\t\n
* pointAlongCurveFrom(curve, location, distance)\n
* \n
* \tCalculates the coordinates of the point on the given curve that is \'distance\' units from location.  \'distance\' should be in the same coordinate\n
* space as that used to construct the Bezier curve.  For an HTML Canvas usage, for example, distance would be a measure of pixels.\n
*\n
* locationAlongCurveFrom(curve, location, distance)\n
* \n
* \tCalculates the location on the given curve that is \'distance\' units from location.  \'distance\' should be in the same coordinate\n
* space as that used to construct the Bezier curve.  For an HTML Canvas usage, for example, distance would be a measure of pixels.\n
* \n
* perpendicularToCurveAt(curve, location, length, distance)\n
* \n
* \tCalculates the perpendicular to the given curve at the given location.  length is the length of the line you wish for (it will be centered\n
* on the point at \'location\'). distance is optional, and allows you to specify a point along the path from the given location as the center of\n
* the perpendicular returned.  The return value of this is an array of two points: [ {x:...,y:...}, {x:...,y:...} ].  \n
*  \n
* \n
*/\n
\n
(function() {\n
\t\n
\tif(typeof Math.sgn == "undefined") {\n
\t\tMath.sgn = function(x) { return x == 0 ? 0 : x > 0 ? 1 :-1; };\n
\t}\n
\t\n
\tvar Vectors = {\n
\t\t\tsubtract \t: \tfunction(v1, v2) { return {x:v1.x - v2.x, y:v1.y - v2.y }; },\n
\t\t\tdotProduct\t: \tfunction(v1, v2) { return (v1.x * v2.x)  + (v1.y * v2.y); },\n
\t\t\tsquare\t\t:\tfunction(v) { return Math.sqrt((v.x * v.x) + (v.y * v.y)); },\n
\t\t\tscale\t\t:\tfunction(v, s) { return {x:v.x * s, y:v.y * s }; }\n
\t\t},\n
\t\t\n
\t\tmaxRecursion = 64, \n
\t\tflatnessTolerance = Math.pow(2.0,-maxRecursion-1);\n
\n
\t/**\n
\t * Calculates the distance that the point lies from the curve.\n
\t * \n
\t * @param point a point in the form {x:567, y:3342}\n
\t * @param curve a Bezier curve in the form [{x:..., y:...}, {x:..., y:...}, {x:..., y:...}, {x:..., y:...}].  note that this is currently\n
\t * hardcoded to assume cubiz beziers, but would be better off supporting any degree. \n
\t * @return a JS object literal containing location and distance, for example: {location:0.35, distance:10}.  Location is analogous to the location\n
\t * argument you pass to the pointOnPath function: it is a ratio of distance travelled along the curve.  Distance is the distance in pixels from\n
\t * the point to the curve. \n
\t */\n
\tvar _distanceFromCurve = function(point, curve) {\n
\t\tvar candidates = [],     \n
\t    \tw = _convertToBezier(point, curve),\n
\t    \tdegree = curve.length - 1, higherDegree = (2 * degree) - 1,\n
\t    \tnumSolutions = _findRoots(w, higherDegree, candidates, 0),\n
\t\t\tv = Vectors.subtract(point, curve[0]), dist = Vectors.square(v), t = 0.0;\n
\n
\t    for (var i = 0; i < numSolutions; i++) {\n
\t\t\tv = Vectors.subtract(point, _bezier(curve, degree, candidates[i], null, null));\n
\t    \tvar newDist = Vectors.square(v);\n
\t    \tif (newDist < dist) {\n
\t            dist = newDist;\n
\t        \tt = candidates[i];\n
\t\t    }\n
\t    }\n
\t    v = Vectors.subtract(point, curve[degree]);\n
\t\tnewDist = Vectors.square(v);\n
\t    if (newDist < dist) {\n
\t        dist = newDist;\n
\t    \tt = 1.0;\n
\t    }\n
\t\treturn {location:t, distance:dist};\n
\t};\n
\t/**\n
\t * finds the nearest point on the curve to the given point.\n
\t */\n
\tvar _nearestPointOnCurve = function(point, curve) {    \n
\t\tvar td = _distanceFromCurve(point, curve);\n
\t    return {point:_bezier(curve, curve.length - 1, td.location, null, null), location:td.location};\n
\t};\n
\tvar _convertToBezier = function(point, curve) {\n
\t\tvar degree = curve.length - 1, higherDegree = (2 * degree) - 1,\n
\t    \tc = [], d = [], cdTable = [], w = [],\n
\t    \tz = [ [1.0, 0.6, 0.3, 0.1], [0.4, 0.6, 0.6, 0.4], [0.1, 0.3, 0.6, 1.0] ];\t\n
\t    \t\n
\t    for (var i = 0; i <= degree; i++) c[i] = Vectors.subtract(curve[i], point);\n
\t    for (var i = 0; i <= degree - 1; i++) { \n
\t\t\td[i] = Vectors.subtract(curve[i+1], curve[i]);\n
\t\t\td[i] = Vectors.scale(d[i], 3.0);\n
\t    }\n
\t    for (var row = 0; row <= degree - 1; row++) {\n
\t\t\tfor (var column = 0; column <= degree; column++) {\n
\t\t\t\tif (!cdTable[row]) cdTable[row] = [];\n
\t\t    \tcdTable[row][column] = Vectors.dotProduct(d[row], c[column]);\n
\t\t\t}\n
\t    }\n
\t    for (i = 0; i <= higherDegree; i++) {\n
\t\t\tif (!w[i]) w[i] = [];\n
\t\t\tw[i].y = 0.0;\n
\t\t\tw[i].x = parseFloat(i) / higherDegree;\n
\t    }\n
\t    var n = degree, m = degree-1;\n
\t    for (var k = 0; k <= n + m; k++) {\n
\t\t\tvar lb = Math.max(0, k - m),\n
\t\t\t\tub = Math.min(k, n);\n
\t\t\tfor (i = lb; i <= ub; i++) {\n
\t\t    \tj = k - i;\n
\t\t    \tw[i+j].y += cdTable[j][i] * z[j][i];\n
\t\t\t}\n
\t    }\n
\t    return w;\n
\t};\n
\t/**\n
\t * counts how many roots there are.\n
\t */\n
\tvar _findRoots = function(w, degree, t, depth) {  \n
\t    var left = [], right = [],\t\n
\t    \tleft_count, right_count,\t\n
\t    \tleft_t = [], right_t = [];\n
\t    \t\n
\t    switch (_getCrossingCount(w, degree)) {\n
\t       \tcase 0 : {\t\n
\t       \t\treturn 0;\t\n
\t       \t}\n
\t       \tcase 1 : {\t\n
\t       \t\tif (depth >= maxRecursion) {\n
\t       \t\t\tt[0] = (w[0].x + w[degree].x) / 2.0;\n
\t       \t\t\treturn 1;\n
\t       \t\t}\n
\t       \t\tif (_isFlatEnough(w, degree)) {\n
\t       \t\t\tt[0] = _computeXIntercept(w, degree);\n
\t       \t\t\treturn 1;\n
\t       \t\t}\n
\t       \t\tbreak;\n
\t       \t}\n
\t    }\n
\t    _bezier(w, degree, 0.5, left, right);\n
\t    left_count  = _findRoots(left,  degree, left_t, depth+1);\n
\t    right_count = _findRoots(right, degree, right_t, depth+1);\n
\t    for (var i = 0; i < left_count; i++) t[i] = left_t[i];\n
\t    for (var i = 0; i < right_count; i++) t[i+left_count] = right_t[i];    \n
\t\treturn (left_count+right_count);\n
\t};\n
\tvar _getCrossingCount = function(curve, degree) {\n
\t    var n_crossings = 0, sign, old_sign;\t\t    \t\n
\t    sign = old_sign = Math.sgn(curve[0].y);\n
\t    for (var i = 1; i <= degree; i++) {\n
\t\t\tsign = Math.sgn(curve[i].y);\n
\t\t\tif (sign != old_sign) n_crossings++;\n
\t\t\told_sign = sign;\n
\t    }\n
\t    return n_crossings;\n
\t};\n
\tvar _isFlatEnough = function(curve, degree) {\n
\t    var  error,\n
\t    \tintercept_1, intercept_2, left_intercept, right_intercept,\n
\t    \ta, b, c, det, dInv, a1, b1, c1, a2, b2, c2;\n
\t    a = curve[0].y - curve[degree].y;\n
\t    b = curve[degree].x - curve[0].x;\n
\t    c = curve[0].x * curve[degree].y - curve[degree].x * curve[0].y;\n
\t\n
\t    var max_distance_above = max_distance_below = 0.0;\n
\t    \n
\t    for (var i = 1; i < degree; i++) {\n
\t        var value = a * curve[i].x + b * curve[i].y + c;       \n
\t        if (value > max_distance_above)\n
\t            max_distance_above = value;\n
\t        else if (value < max_distance_below)\n
\t        \tmax_distance_below = value;\n
\t    }\n
\t    \n
\t    a1 = 0.0; b1 = 1.0; c1 = 0.0; a2 = a; b2 = b;\n
\t    c2 = c - max_distance_above;\n
\t    det = a1 * b2 - a2 * b1;\n
\t    dInv = 1.0/det;\n
\t    intercept_1 = (b1 * c2 - b2 * c1) * dInv;\n
\t    a2 = a; b2 = b; c2 = c - max_distance_below;\n
\t    det = a1 * b2 - a2 * b1;\n
\t    dInv = 1.0/det;\n
\t    intercept_2 = (b1 * c2 - b2 * c1) * dInv;\n
\t    left_intercept = Math.min(intercept_1, intercept_2);\n
\t    right_intercept = Math.max(intercept_1, intercept_2);\n
\t    error = right_intercept - left_intercept;\n
\t    return (error < flatnessTolerance)? 1 : 0;\n
\t};\n
\tvar _computeXIntercept = function(curve, degree) {\n
\t    var XLK = 1.0, YLK = 0.0,\n
\t    \tXNM = curve[degree].x - curve[0].x, YNM = curve[degree].y - curve[0].y,\n
\t    \tXMK = curve[0].x - 0.0, YMK = curve[0].y - 0.0,\n
\t    \tdet = XNM*YLK - YNM*XLK, detInv = 1.0/det,\n
\t    \tS = (XNM*YMK - YNM*XMK) * detInv; \n
\t    return 0.0 + XLK * S;\n
\t};\n
\tvar _bezier = function(curve, degree, t, left, right) {\n
\t    var temp = [[]];\n
\t    for (var j =0; j <= degree; j++) temp[0][j] = curve[j];\n
\t    for (var i = 1; i <= degree; i++) {\t\n
\t\t\tfor (var j =0 ; j <= degree - i; j++) {\n
\t\t\t\tif (!temp[i]) temp[i] = [];\n
\t\t\t\tif (!temp[i][j]) temp[i][j] = {};\n
\t\t    \ttemp[i][j].x = (1.0 - t) * temp[i-1][j].x + t * temp[i-1][j+1].x;\n
\t\t    \ttemp[i][j].y = (1.0 - t) * temp[i-1][j].y + t * temp[i-1][j+1].y;\n
\t\t\t}\n
\t    }    \n
\t    if (left != null) \n
\t    \tfor (j = 0; j <= degree; j++) left[j]  = temp[j][0];\n
\t    if (right != null)\n
\t\t\tfor (j = 0; j <= degree; j++) right[j] = temp[degree-j][j];\n
\t    \n
\t    return (temp[degree][0]);\n
\t};\n
\t\n
\tvar _curveFunctionCache = {};\n
\tvar _getCurveFunctions = function(order) {\n
\t\tvar fns = _curveFunctionCache[order];\n
\t\tif (!fns) {\n
\t\t\tfns = [];\t\t\t\n
\t\t\tvar f_term = function() { return function(t) { return Math.pow(t, order); }; },\n
\t\t\t\tl_term = function() { return function(t) { return Math.pow((1-t), order); }; },\n
\t\t\t\tc_term = function(c) { return function(t) { return c; }; },\n
\t\t\t\tt_term = function() { return function(t) { return t; }; },\n
\t\t\t\tone_minus_t_term = function() { return function(t) { return 1-t; }; },\n
\t\t\t\t_termFunc = function(terms) {\n
\t\t\t\t\treturn function(t) {\n
\t\t\t\t\t\tvar p = 1;\n
\t\t\t\t\t\tfor (var i = 0; i < terms.length; i++) p = p * terms[i](t);\n
\t\t\t\t\t\treturn p;\n
\t\t\t\t\t};\n
\t\t\t\t};\n
\t\t\t\n
\t\t\tfns.push(new f_term());  // first is t to the power of the curve order\t\t\n
\t\t\tfor (var i = 1; i < order; i++) {\n
\t\t\t\tvar terms = [new c_term(order)];\n
\t\t\t\tfor (var j = 0 ; j < (order - i); j++) terms.push(new t_term());\n
\t\t\t\tfor (var j = 0 ; j < i; j++) terms.push(new one_minus_t_term());\n
\t\t\t\tfns.push(new _termFunc(terms));\n
\t\t\t}\n
\t\t\tfns.push(new l_term());  // last is (1-t) to the power of the curve order\n
\t\t\n
\t\t\t_curveFunctionCache[order] = fns;\n
\t\t}\n
\t\t\t\n
\t\treturn fns;\n
\t};\n
\t\n
\t\n
\t/**\n
\t * calculates a point on the curve, for a Bezier of arbitrary order.\n
\t * @param curve an array of control points, eg [{x:10,y:20}, {x:50,y:50}, {x:100,y:100}, {x:120,y:100}].  For a cubic bezier this should have four points.\n
\t * @param location a decimal indicating the distance along the curve the point should be located at.  this is the distance along the curve as it travels, taking the way it bends into account.  should be a number from 0 to 1, inclusive.\n
\t */\n
\tvar _pointOnPath = function(curve, location) {\t\t\n
\t\tvar cc = _getCurveFunctions(curve.length - 1),\n
\t\t\t_x = 0, _y = 0;\n
\t\tfor (var i = 0; i < curve.length ; i++) {\n
\t\t\t_x = _x + (curve[i].x * cc[i](location));\n
\t\t\t_y = _y + (curve[i].y * cc[i](location));\n
\t\t}\n
\t\t\n
\t\treturn {x:_x, y:_y};\n
\t};\n
\t\n
\tvar _dist = function(p1,p2) {\n
\t\treturn Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2));\n
\t};\n
\n
\tvar _isPoint = function(curve) {\n
\t\treturn curve[0].x == curve[1].x && curve[0].y == curve[1].y;\n
\t};\n
\t\n
\t/**\n
\t * finds the point that is \'distance\' along the path from \'location\'.  this method returns both the x,y location of the point and also\n
\t * its \'location\' (proportion of travel along the path); the method below - _pointAlongPathFrom - calls this method and just returns the\n
\t * point.\n
\t */\n
\tvar _pointAlongPath = function(curve, location, distance) {\n
\n
\t\tif (_isPoint(curve)) {\n
\t\t\treturn {\n
\t\t\t\tpoint:curve[0],\n
\t\t\t\tlocation:location\n
\t\t\t};\n
\t\t}\n
\n
\t\tvar prev = _pointOnPath(curve, location), \n
\t\t\ttally = 0, \n
\t\t\tcurLoc = location, \n
\t\t\tdirection = distance > 0 ? 1 : -1, \n
\t\t\tcur = null;\n
\t\t\t\n
\t\twhile (tally < Math.abs(distance)) {\n
\t\t\tcurLoc += (0.005 * direction);\n
\t\t\tcur = _pointOnPath(curve, curLoc);\n
\t\t\ttally += _dist(cur, prev);\t\n
\t\t\tprev = cur;\n
\t\t}\n
\t\treturn {point:cur, location:curLoc};        \t\n
\t};\n
\t\n
\tvar _length = function(curve) {\n
\t\tif (_isPoint(curve)) return 0;\n
\n
\t\tvar prev = _pointOnPath(curve, 0),\n
\t\t\ttally = 0,\n
\t\t\tcurLoc = 0,\n
\t\t\tdirection = 1,\n
\t\t\tcur = null;\n
\t\t\t\n
\t\twhile (curLoc < 1) {\n
\t\t\tcurLoc += (0.005 * direction);\n
\t\t\tcur = _pointOnPath(curve, curLoc);\n
\t\t\ttally += _dist(cur, prev);\t\n
\t\t\tprev = cur;\n
\t\t}\n
\t\treturn tally;\n
\t};\n
\t\n
\t/**\n
\t * finds the point that is \'distance\' along the path from \'location\'.  \n
\t */\n
\tvar _pointAlongPathFrom = function(curve, location, distance) {\n
\t\treturn _pointAlongPath(curve, location, distance).point;\n
\t};\n
\n
\t/**\n
\t * finds the location that is \'distance\' along the path from \'location\'.  \n
\t */\n
\tvar _locationAlongPathFrom = function(curve, location, distance) {\n
\t\treturn _pointAlongPath(curve, location, distance).location;\n
\t};\n
\t\n
\t/**\n
\t * returns the gradient of the curve at the given location, which is a decimal between 0 and 1 inclusive.\n
\t * \n
\t * thanks // http://bimixual.org/AnimationLibrary/beziertangents.html\n
\t */\n
\tvar _gradientAtPoint = function(curve, location) {\n
\t\tvar p1 = _pointOnPath(curve, location),\t\n
\t\t\tp2 = _pointOnPath(curve.slice(0, curve.length - 1), location),\n
\t\t\tdy = p2.y - p1.y, dx = p2.x - p1.x;\n
\t\treturn dy == 0 ? Infinity : Math.atan(dy / dx);\t\t\n
\t};\n
\t\n
\t/**\n
\treturns the gradient of the curve at the point which is \'distance\' from the given location.\n
\tif this point is greater than location 1, the gradient at location 1 is returned.\n
\tif this point is less than location 0, the gradient at location 0 is returned.\n
\t*/\n
\tvar _gradientAtPointAlongPathFrom = function(curve, location, distance) {\n
\t\tvar p = _pointAlongPath(curve, location, distance);\n
\t\tif (p.location > 1) p.location = 1;\n
\t\tif (p.location < 0) p.location = 0;\t\t\n
\t\treturn _gradientAtPoint(curve, p.location);\t\t\n
\t};\n
\n
\t/**\n
\t * calculates a line that is \'length\' pixels long, perpendicular to, and centered on, the path at \'distance\' pixels from the given location.\n
\t * if distance is not supplied, the perpendicular for the given location is computed (ie. we set distance to zero).\n
\t */\n
\tvar _perpendicularToPathAt = function(curve, location, length, distance) {\n
\t\tdistance = distance == null ? 0 : distance;\n
\t\tvar p = _pointAlongPath(curve, location, distance),\n
\t\t\tm = _gradientAtPoint(curve, p.location),\n
\t\t\t_theta2 = Math.atan(-1 / m),\n
\t\t\ty =  length / 2 * Math.sin(_theta2),\n
\t\t\tx =  length / 2 * Math.cos(_theta2);\n
\t\treturn [{x:p.point.x + x, y:p.point.y + y}, {x:p.point.x - x, y:p.point.y - y}];\n
\t};\n
\t\n
\tvar jsBezier = window.jsBezier = {\n
\t\tdistanceFromCurve : _distanceFromCurve,\n
\t\tgradientAtPoint : _gradientAtPoint,\n
\t\tgradientAtPointAlongCurveFrom : _gradientAtPointAlongPathFrom,\n
\t\tnearestPointOnCurve : _nearestPointOnCurve,\n
\t\tpointOnCurve : _pointOnPath,\t\t\n
\t\tpointAlongCurveFrom : _pointAlongPathFrom,\n
\t\tperpendicularToCurveAt : _perpendicularToPathAt,\n
\t\tlocationAlongCurveFrom:_locationAlongPathFrom,\n
\t\tgetLength:_length\n
\t};\n
})();\n
\n
/**\n
 * Biltong v0.2\n
 *\n
 * Various geometry functions written as part of jsPlumb and perhaps useful for others.\n
 *\n
 * Copyright (c) 2014 Simon Porritt\n
 *\n
 * Permission is hereby granted, free of charge, to any person\n
 * obtaining a copy of this software and associated documentation\n
 * files (the "Software"), to deal in the Software without\n
 * restriction, including without limitation the rights to use,\n
 * copy, modify, merge, publish, distribute, sublicense, and/or sell\n
 * copies of the Software, and to permit persons to whom the\n
 * Software is furnished to do so, subject to the following\n
 * conditions:\n
 *\n
 * The above copyright notice and this permission notice shall be\n
 * included in all copies or substantial portions of the Software.\n
 *\n
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,\n
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES\n
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND\n
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT\n
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,\n
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING\n
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR\n
 * OTHER DEALINGS IN THE SOFTWARE.\n
 */\n
;(function() {\n
\n
\t\n
\t"use strict";\n
\n
\tvar Biltong = this.Biltong = {};\n
\n
\tvar _isa = function(a) { return Object.prototype.toString.call(a) === "[object Array]"; },\n
\t\t_pointHelper = function(p1, p2, fn) {\n
\t\t    p1 = _isa(p1) ? p1 : [p1.x, p1.y];\n
\t\t    p2 = _isa(p2) ? p2 : [p2.x, p2.y];    \n
\t\t    return fn(p1, p2);\n
\t\t},\n
\t\t/**\n
\t\t* @name Biltong.gradient\n
\t\t* @function\n
\t\t* @desc Calculates the gradient of a line between the two points.\n
\t\t* @param {Point} p1 First point, either as a 2 entry array or object with `left` and `top` properties.\n
\t\t* @param {Point} p2 Second point, either as a 2 entry array or object with `left` and `top` properties.\n
\t\t* @return {Float} The gradient of a line between the two points.\n
\t\t*/\n
\t\t_gradient = Biltong.gradient = function(p1, p2) {\n
\t\t    return _pointHelper(p1, p2, function(_p1, _p2) { \n
\t\t        if (_p2[0] == _p1[0])\n
\t\t            return _p2[1] > _p1[1] ? Infinity : -Infinity;\n
\t\t        else if (_p2[1] == _p1[1]) \n
\t\t            return _p2[0] > _p1[0] ? 0 : -0;\n
\t\t        else \n
\t\t            return (_p2[1] - _p1[1]) / (_p2[0] - _p1[0]); \n
\t\t    });\t\t\n
\t\t},\n
\t\t/**\n
\t\t* @name Biltong.normal\n
\t\t* @function\n
\t\t* @desc Calculates the gradient of a normal to a line between the two points.\n
\t\t* @param {Point} p1 First point, either as a 2 entry array or object with `left` and `top` properties.\n
\t\t* @param {Point} p2 Second point, either as a 2 entry array or object with `left` and `top` properties.\n
\t\t* @return {Float} The gradient of a normal to a line between the two points.\n
\t\t*/\n
\t\t_normal = Biltong.normal = function(p1, p2) {\n
\t\t    return -1 / _gradient(p1, p2);\n
\t\t},\n
\t\t/**\n
\t\t* @name Biltong.lineLength\n
\t\t* @function\n
\t\t* @desc Calculates the length of a line between the two points.\n
\t\t* @param {Point} p1 First point, either as a 2 entry array or object with `left` and `top` properties.\n
\t\t* @param {Point} p2 Second point, either as a 2 entry array or object with `left` and `top` properties.\n
\t\t* @return {Float} The length of a line between the two points.\n
\t\t*/\n
\t\t_lineLength = Biltong.lineLength = function(p1, p2) {\n
\t\t    return _pointHelper(p1, p2, function(_p1, _p2) {\n
\t\t        return Math.sqrt(Math.pow(_p2[1] - _p1[1], 2) + Math.pow(_p2[0] - _p1[0], 2));\t\t\t\n
\t\t    });\n
\t\t},\n
\t\t/**\n
\t\t* @name Biltong.quadrant\n
\t\t* @function\n
\t\t* @desc Calculates the quadrant in which the angle between the two points lies. \n
\t\t* @param {Point} p1 First point, either as a 2 entry array or object with `left` and `top` properties.\n
\t\t* @param {Point} p2 Second point, either as a 2 entry array or object with `left` and `top` properties.\n
\t\t* @return {Integer} The quadrant - 1 for upper right, 2 for lower right, 3 for lower left, 4 for upper left.\n
\t\t*/\n
\t\t_quadrant = Biltong.quadrant = function(p1, p2) {\n
\t\t    return _pointHelper(p1, p2, function(_p1, _p2) {\n
\t\t        if (_p2[0] > _p1[0]) {\n
\t\t            return (_p2[1] > _p1[1]) ? 2 : 1;\n
\t\t        }\n
\t\t        else if (_p2[0] == _p1[0]) {\n
\t\t            return _p2[1] > _p1[1] ? 2 : 1;    \n
\t\t        }\n
\t\t        else {\n
\t\t            return (_p2[1] > _p1[1]) ? 3 : 4;\n
\t\t        }\n
\t\t    });\n
\t\t},\n
\t\t/**\n
\t\t* @name Biltong.theta\n
\t\t* @function\n
\t\t* @desc Calculates the angle between the two points. \n
\t\t* @param {Point} p1 First point, either as a 2 entry array or object with `left` and `top` properties.\n
\t\t* @param {Point} p2 Second point, either as a 2 entry array or object with `left` and `top` properties.\n
\t\t* @return {Float} The angle between the two points.\n
\t\t*/\n
\t\t_theta = Biltong.theta = function(p1, p2) {\n
\t\t    return _pointHelper(p1, p2, function(_p1, _p2) {\n
\t\t        var m = _gradient(_p1, _p2),\n
\t\t            t = Math.atan(m),\n
\t\t            s = _quadrant(_p1, _p2);\n
\t\t        if ((s == 4 || s== 3)) t += Math.PI;\n
\t\t        if (t < 0) t += (2 * Math.PI);\n
\t\t    \n
\t\t        return t;\n
\t\t    });\n
\t\t},\n
\t\t/**\n
\t\t* @name Biltong.intersects\n
\t\t* @function\n
\t\t* @desc Calculates whether or not the two rectangles intersect.\n
\t\t* @param {Rectangle} r1 First rectangle, as a js object in the form `{x:.., y:.., w:.., h:..}`\n
\t\t* @param {Rectangle} r2 Second rectangle, as a js object in the form `{x:.., y:.., w:.., h:..}`\n
\t\t* @return {Boolean} True if the rectangles intersect, false otherwise.\n
\t\t*/\n
\t\t_intersects = Biltong.intersects = function(r1, r2) {\n
\t\t    var x1 = r1.x, x2 = r1.x + r1.w, y1 = r1.y, y2 = r1.y + r1.h,\n
\t\t        a1 = r2.x, a2 = r2.x + r2.w, b1 = r2.y, b2 = r2.y + r2.h;\n
\t\t\n
\t\t\treturn  ( (x1 <= a1 && a1 <= x2) && (y1 <= b1 && b1 <= y2) ) ||\n
\t\t\t        ( (x1 <= a2 && a2 <= x2) && (y1 <= b1 && b1 <= y2) ) ||\n
\t\t\t        ( (x1 <= a1 && a1 <= x2) && (y1 <= b2 && b2 <= y2) ) ||\n
\t\t\t        ( (x1 <= a2 && a1 <= x2) && (y1 <= b2 && b2 <= y2) ) ||\t\n
\t\t\t        ( (a1 <= x1 && x1 <= a2) && (b1 <= y1 && y1 <= b2) ) ||\n
\t\t\t        ( (a1 <= x2 && x2 <= a2) && (b1 <= y1 && y1 <= b2) ) ||\n
\t\t\t        ( (a1 <= x1 && x1 <= a2) && (b1 <= y2 && y2 <= b2) ) ||\n
\t\t\t        ( (a1 <= x2 && x1 <= a2) && (b1 <= y2 && y2 <= b2) );\n
\t\t},\n
\t\t/**\n
\t\t* @name Biltong.encloses\n
\t\t* @function\n
\t\t* @desc Calculates whether or not r2 is completely enclosed by r1.\n
\t\t* @param {Rectangle} r1 First rectangle, as a js object in the form `{x:.., y:.., w:.., h:..}`\n
\t\t* @param {Rectangle} r2 Second rectangle, as a js object in the form `{x:.., y:.., w:.., h:..}`\n
\t\t* @param {Boolean} [allowSharedEdges=false] If true, the concept of enclosure allows for one or more edges to be shared by the two rectangles.\n
\t\t* @return {Boolean} True if r1 encloses r2, false otherwise.\n
\t\t*/\n
\t\t_encloses = Biltong.encloses = function(r1, r2, allowSharedEdges) {\n
\t\t\tvar x1 = r1.x, x2 = r1.x + r1.w, y1 = r1.y, y2 = r1.y + r1.h,\n
\t\t        a1 = r2.x, a2 = r2.x + r2.w, b1 = r2.y, b2 = r2.y + r2.h,\n
\t\t\t\tc = function(v1, v2, v3, v4) { return allowSharedEdges ? v1 <= v2 && v3>= v4 : v1 < v2 && v3 > v4; };\n
\t\t\t\t\n
\t\t\treturn c(x1,a1,x2,a2) && c(y1,b1,y2,b2);\n
\t\t},\n
\t\t_segmentMultipliers = [null, [1, -1], [1, 1], [-1, 1], [-1, -1] ],\n
\t\t_inverseSegmentMultipliers = [null, [-1, -1], [-1, 1], [1, 1], [1, -1] ],\n
\t\t/**\n
\t\t* @name Biltong.pointOnLine\n
\t\t* @function\n
\t\t* @desc Calculates a point on the line from `fromPoint` to `toPoint` that is `distance` units along the length of the line.\n
\t\t* @param {Point} p1 First point, either as a 2 entry array or object with `left` and `top` properties.\n
\t\t* @param {Point} p2 Second point, either as a 2 entry array or object with `left` and `top` properties.\n
\t\t* @return {Point} Point on the line, in the form `{ x:..., y:... }`.\n
\t\t*/\n
\t\t_pointOnLine = Biltong.pointOnLine = function(fromPoint, toPoint, distance) {\n
\t\t    var m = _gradient(fromPoint, toPoint),\n
\t\t        s = _quadrant(fromPoint, toPoint),\n
\t\t        segmentMultiplier = distance > 0 ? _segmentMultipliers[s] : _inverseSegmentMultipliers[s],\n
\t\t        theta = Math.atan(m),\n
\t\t        y = Math.abs(distance * Math.sin(theta)) * segmentMultiplier[1],\n
\t\t        x =  Math.abs(distance * Math.cos(theta)) * segmentMultiplier[0];\n
\t\t    return { x:fromPoint.x + x, y:fromPoint.y + y };\n
\t\t},\n
\t\t/**\n
\t\t* @name Biltong.perpendicularLineTo\n
\t\t* @function\n
\t\t* @desc Calculates a line of length `length` that is perpendicular to the line from `fromPoint` to `toPoint` and passes through `toPoint`.\n
\t\t* @param {Point} p1 First point, either as a 2 entry array or object with `left` and `top` properties.\n
\t\t* @param {Point} p2 Second point, either as a 2 entry array or object with `left` and `top` properties.\n
\t\t* @return {Line} Perpendicular line, in the form `[ { x:..., y:... }, { x:..., y:... } ]`.\n
\t\t*/        \n
\t\t_perpendicularLineTo = Biltong.perpendicularLineTo = function(fromPoint, toPoint, length) {\n
\t\t    var m = _gradient(fromPoint, toPoint),\n
\t\t        theta2 = Math.atan(-1 / m),\n
\t\t        y =  length / 2 * Math.sin(theta2),\n
\t\t        x =  length / 2 * Math.cos(theta2);\n
\t\t    return [{x:toPoint.x + x, y:toPoint.y + y}, {x:toPoint.x - x, y:toPoint.y - y}];\n
\t\t};\t\n
}).call(this);\n
/*\n
 * jsPlumb\n
 * \n
 * Title:jsPlumb 1.6.2\n
 * \n
 * Provides a way to visually connect elements on an HTML page, using SVG or VML.  \n
 * \n
 * This file contains the utility functions.\n
 *\n
 * Copyright (c) 2010 - 2014 Simon Porritt (simon@jsplumbtoolkit.com)\n
 * \n
 * http://jsplumbtoolkit.com\n
 * http://github.com/sporritt/jsplumb\n
 * \n
 * Dual licensed under the MIT and GPL2 licenses.\n
 */\n
;(function() {\n
\n
\n
    var _isa = function(a) { return Object.prototype.toString.call(a) === "[object Array]"; },\n
        _isnum = function(n) { return Object.prototype.toString.call(n) === "[object Number]"; },\n
        _iss = function(s) { return typeof s === "string"; },\n
        _isb = function(s) { return typeof s === "boolean"; },\n
        _isnull = function(s) { return s == null; },  \n
        _iso = function(o) { return o == null ? false : Object.prototype.toString.call(o) === "[object Object]"; },\n
        _isd = function(o) { return Object.prototype.toString.call(o) === "[object Date]"; },\n
        _isf = function(o) { return Object.prototype.toString.call(o) === "[object Function]"; },\n
        _ise = function(o) {\n
            for (var i in o) { if (o.hasOwnProperty(i)) return false; }\n
            return true;\n
        },\n
        pointHelper = function(p1, p2, fn) {\n
            p1 = _isa(p1) ? p1 : [p1.x, p1.y];\n
            p2 = _isa(p2) ? p2 : [p2.x, p2.y];    \n
            return fn(p1, p2);\n
        };\n
    \n
    jsPlumbUtil = {        \n
        isArray : _isa,        \n
        isString : _iss,        \n
        isBoolean: _isb,        \n
        isNull : _isnull,        \n
        isObject : _iso,\n
        isDate : _isd,\n
        isFunction: _isf,\n
        isEmpty:_ise,\n
        isNumber:_isnum,\n
        clone : function(a) {\n
            if (_iss(a)) return "" + a;\n
            else if (_isb(a)) return !!a;\n
            else if (_isd(a)) return new Date(a.getTime());\n
            else if (_isf(a)) return a;\n
            else if (_isa(a)) {\n
                var b = [];\n
                for (var i = 0; i < a.length; i++)\n
                    b.push(this.clone(a[i]));\n
                return b;\n
            }\n
            else if (_iso(a)) {\n
                var c = {};\n
                for (var j in a)\n
                    c[j] = this.clone(a[j]);\n
                return c;\n
            }\n
            else return a;\n
        },\n
        matchesSelector : function(el, selector, ctx) {\n
            ctx = ctx || el.parentNode;\n
            var possibles = ctx.querySelectorAll(selector);\n
            for (var i = 0; i < possibles.length; i++) {\n
                if (possibles[i] === el)\n
                    return true;\n
            }\n
            return false;\n
        },\n
        merge : function(a, b) {\n
            var c = this.clone(a);\n
            for (var i in b) {\n
                if (c[i] == null || _iss(b[i]) || _isb(b[i]))\n
                    c[i] = b[i];\n
                else {\n
                    if (_isa(b[i])) {\n
                        var ar = [];\n
                        // if c\'s object is also an array we can keep its values.\n
                        if (_isa(c[i])) ar.push.apply(ar, c[i]);\n
                        ar.push.apply(ar, b[i]);\n
                        c[i] = ar;\n
                    }\n
                    else if(_iso(b[i])) {\n
                        // overwite c\'s value with an object if it is not already one.\n
                        if (!_iso(c[i])) \n
                            c[i] = {};\n
                        for (var j in b[i])\n
                            c[i][j] = b[i][j];\n
                    }\n
                }\n
            }\n
            return c;\n
        },\n
        replace:function(inObj, path, value) {\n
            var q = inObj, t = q;\n
            path.replace(/([^\\.])+/g, function(term, lc, pos, str) {             \n
                var array = term.match(/([^\\[0-9]+){1}(\\[)([0-9+])/),\n
                    last = pos + term.length >= str.length,\n
                    _getArray = function() {\n
                        return t[array[1]] || (function() {  t[array[1]] = []; return t[array[1]]; })();\n
                    };\n
                \n
                if (last) {\n
                    // set term = value on current t, creating term as array if necessary.\n
                    if (array)\n
                        _getArray()[array[3]] = value;\n
                    else\n
                        t[term] = value;\n
                }\n
                else {\n
                    // set to current t[term], creating t[term] if necessary.\n
                    if (array) {\n
                        var a = _getArray();\n
                        t = a[array[3]] || (function() { a[array[3]] = {}; return a[array[3]]; })();\n
                    }\n
                    else\n
                        t = t[term] || (function() { t[term] = {}; return t[term]; })();\n
                }\n
            });\n
\n
            return inObj;\n
        },\n
        //\n
        // chain a list of functions, supplied by [ object, method name, args ], and return on the first\n
        // one that returns the failValue. if none return the failValue, return the successValue.\n
        //\n
        functionChain : function(successValue, failValue, fns) {\n
            for (var i = 0; i < fns.length; i++) {\n
                var o = fns[i][0][fns[i][1]].apply(fns[i][0], fns[i][2]);\n
                if (o === failValue) {\n
                    return o;\n
                }\n
            }\n
            return successValue;\n
        },\n
        // take the given model and expand out any parameters.\n
        populate : function(model, values) {\n
            // for a string, see if it has parameter matches, and if so, try to make the substitutions.\n
            var getValue = function(fromString) {\n
                    var matches = fromString.match(/(\\${.*?})/g);\n
                    if (matches != null) {\n
                        for (var i = 0; i < matches.length; i++) {\n
                            var val = values[matches[i].substring(2, matches[i].length - 1)];\n
                            if (val != null) {\n
                                fromString = fromString.replace(matches[i], val);\n
                            }\n
                        }\n
                    }\n
                    return fromString;\n
                },\t\t\n
                // process one entry.\n
                _one = function(d) {\n
                    if (d != null) {\n
                        if (_iss(d)) {\n
                            return getValue(d);\n
                        }\n
                        else if (_isa(d)) {\n
                            var r = [];\t\n
                            for (var i = 0; i < d.length; i++)\n
                                r.push(_one(d[i]));\n
                            return r;\n
                        }\n
                        else if (_iso(d)) {\n
                            var s = {};\n
                            for (var j in d) {\n
                                s[j] = _one(d[j]);\n
                            }\n
                            return s;\n
                        }\n
                        else {\n
                            return d;\n
                        }\n
                    }\n
                };\n
            \n
            return _one(model);\t\n
        },\n
        convertStyle : function(s, ignoreAlpha) {\n
            // TODO: jsPlumb should support a separate \'opacity\' style member.\n
            if ("transparent" === s) return s;\n
            var o = s,\n
                pad = function(n) { return n.length == 1 ? "0" + n : n; },\n
                hex = function(k) { return pad(Number(k).toString(16)); },\n
                pattern = /(rgb[a]?\\()(.*)(\\))/;\n
            if (s.match(pattern)) {\n
                var parts = s.match(pattern)[2].split(",");\n
                o = "#" + hex(parts[0]) + hex(parts[1]) + hex(parts[2]);\n
                if (!ignoreAlpha && parts.length == 4) \n
                    o = o + hex(parts[3]);\n
            }\n
            return o;\n
        },\n
        findWithFunction : function(a, f) {\n
            if (a)\n
                for (var i = 0; i < a.length; i++) if (f(a[i])) return i;\n
            return -1;\n
\t\t},\n
\t\tindexOf : function(l, v) {\n
\t\t\treturn l.indexOf ? l.indexOf(v) : jsPlumbUtil.findWithFunction(l, function(_v) { return _v == v; });\n
\t\t},\n
\t\tremoveWithFunction : function(a, f) {\n
\t\t\tvar idx = jsPlumbUtil.findWithFunction(a, f);\n
\t\t\tif (idx > -1) a.splice(idx, 1);\n
\t\t\treturn idx != -1;\n
\t\t},\n
\t\tremove : function(l, v) {\n
\t\t\tvar idx = jsPlumbUtil.indexOf(l, v);\n
\t\t\tif (idx > -1) l.splice(idx, 1);\n
\t\t\treturn idx != -1;\n
\t\t},\n
        // TODO support insert index\n
        addWithFunction : function(list, item, hashFunction) {\n
            if (jsPlumbUtil.findWithFunction(list, hashFunction) == -1) list.push(item);\n
        },\n
        addToList : function(map, key, value, insertAtStart) {\n
            var l = map[key];\n
            if (l == null) {\n
                l = []; \n
\t\t\t\tmap[key] = l;\n
            }\n
            l[insertAtStart ? "unshift" : "push"](value);\n
            return l;\n
        },\n
        consume : function(e, doNotPreventDefault) {\n
            if (e.stopPropagation)\n
                e.stopPropagation();\n
            else \n
                e.returnValue = false;\n
            \n
            if (!doNotPreventDefault && e.preventDefault)\n
                 e.preventDefault();\n
        },\n
        //\n
        // extends the given obj (which can be an array) with the given constructor function, prototype functions, and\n
        // class members, any of which may be null.\n
        //\n
        extend : function(child, parent, _protoFn) {\n
\t\t\tvar i;\n
            parent = _isa(parent) ? parent : [ parent ];\n
\n
            for (i = 0; i < parent.length; i++) {\n
                for (var j in parent[i].prototype) {\n
                    if(parent[i].prototype.hasOwnProperty(j)) {\n
                        child.prototype[j] = parent[i].prototype[j];\n
                    }\n
                }\n
            }\n
\n
            var _makeFn = function(name, protoFn) {\n
                return function() {\n
                    for (i = 0; i < parent.length; i++) {\n
                        if (parent[i].prototype[name])\n
                            parent[i].prototype[name].apply(this, arguments);\n
                    }                    \n
                    return protoFn.apply(this, arguments);\n
                };\n
            };\n
\t\t\t\n
\t\t\tvar _oneSet = function(fns) {\n
\t\t\t\tfor (var k in fns) {\n
\t\t\t\t\tchild.prototype[k] = _makeFn(k, fns[k]);\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tif (arguments.length > 2) {\n
\t\t\t\tfor (i = 2; i < arguments.length; i++)\n
\t\t\t\t\t_oneSet(arguments[i]);\n
\t\t\t}\n
\n
            return child;\n
        },\n
        uuid : function() {\n
            return (\'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx\'.replace(/[xy]/g, function(c) {\n
                var r = Math.random()*16|0, v = c == \'x\' ? r : (r&0x3|0x8);\n
                return v.toString(16);\n
            }));\n
        },\n
        logEnabled : true,\n
        log : function() {\n
            if (jsPlumbUtil.logEnabled && typeof console != "undefined") {\n
                try {\n
                    var msg = arguments[arguments.length - 1];\n
                    console.log(msg);\n
                }\n
                catch (e) {} \n
            }\n
        },\n
        /*\n
         * Function: sizeElement \n
         * Helper to size and position an element. You would typically use\n
         * this when writing your own Connector or Endpoint implementation.\n
         * \n
         * Parameters: \n
         *  x - [int] x position for the element origin \n
         *  y - [int] y position for the element origin \n
         *  w - [int] width of the element \n
         *  h - [int] height of the element\n
         *  \n
         */\n
        sizeElement : function(el, x, y, w, h) {\n
            if (el) {\n
                el.style.height = h + "px";\n
                el.height = h;\n
                el.style.width = w + "px";\n
                el.width = w;\n
                el.style.left = x + "px";\n
                el.style.top = y + "px";\n
            }\n
        },\n
        /**\n
        * Wraps one function with another, creating a placeholder for the\n
        * wrapped function if it was null. this is used to wrap the various\n
        * drag/drop event functions - to allow jsPlumb to be notified of\n
        * important lifecycle events without imposing itself on the user\'s\n
        * drag/drop functionality. \n
        * @method jsPlumbUtil.wrap\n
        * @param {Function} wrappedFunction original function to wrap; may be null.\n
        * @param {Function} newFunction function to wrap the original with.\n
        * @param {Object} [returnOnThisValue] Optional. Indicates that the wrappedFunction should \n
        * not be executed if the newFunction returns a value matching \'returnOnThisValue\'.\n
        * note that this is a simple comparison and only works for primitives right now.\n
        */        \n
        wrap : function(wrappedFunction, newFunction, returnOnThisValue) {\n
            wrappedFunction = wrappedFunction || function() { };\n
            newFunction = newFunction || function() { };\n
            return function() {\n
                var r = null;\n
                //try {\n
                    r = newFunction.apply(this, arguments);\n
                //} catch (e) {\n
                //    jsPlumbUtil.log("jsPlumb function failed : " + e);\n
                //}\n
                if (returnOnThisValue == null || (r !== returnOnThisValue)) {\n
                    //try {\n
                        r = wrappedFunction.apply(this, arguments);\n
                    //} catch (e) {\n
                    //    jsPlumbUtil.log("wrapped function failed : " + e);\n
                    //}\n
                }\n
                return r;\n
            };\n
        },\n
        ieVersion : /MSIE\\s([\\d.]+)/.test(navigator.userAgent) ? (new Number(RegExp.$1)) : -1\n
    };\n
\n
    jsPlumbUtil.oldIE = jsPlumbUtil.ieVersion > -1 && jsPlumbUtil.ieVersion < 9;\n
\n
\tjsPlumbUtil.EventGenerator = function() {\n
\t\tvar _listeners = {}, \n
\t\t\teventsSuspended = false,\n
\t\t\t// this is a list of events that should re-throw any errors that occur during their dispatch. it is current private.\n
\t\t\teventsToDieOn = { "ready":true };\n
\n
\t\tthis.bind = function(event, listener, insertAtStart) {\n
\t\t\tjsPlumbUtil.addToList(_listeners, event, listener, insertAtStart);\n
\t\t\treturn this;\n
\t\t};\n
\n
\t\tthis.fire = function(event, value, originalEvent) {\n
\t\t\tif (!eventsSuspended && _listeners[event]) {\n
\t\t\t\tvar l = _listeners[event].length, i = 0, _gone = false, ret = null;\n
\t\t\t\tif (!this.shouldFireEvent || this.shouldFireEvent(event, value, originalEvent)) {\n
\t\t\t\t\twhile (!_gone && i < l && ret !== false) {\n
\t\t\t\t\t\t// doing it this way rather than catching and then possibly re-throwing means that an error propagated by this\n
\t\t\t\t\t\t// method will have the whole call stack available in the debugger.\n
\t\t\t\t\t\tif (eventsToDieOn[event]) \n
\t\t\t\t\t\t\t_listeners[event][i].apply(this, [ value, originalEvent]);\n
\t\t\t\t\t\telse {\n
\t\t\t\t\t\t\ttry {\n
\t\t\t\t\t\t\t\tret = _listeners[event][i].apply(this, [ value, originalEvent ]);\n
\t\t\t\t\t\t\t} catch (e) {\n
\t\t\t\t\t\t\t\tjsPlumbUtil.log("jsPlumb: fire failed for event " + event + " : " + e);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\ti++;\n
\t\t\t\t\t\tif (_listeners == null || _listeners[event] == null) \n
\t\t\t\t\t\t\t_gone = true;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\treturn this;\n
\t\t};\n
\n
\t\tthis.unbind = function(event) {\n
\t\t\tif (event)\n
\t\t\t\tdelete _listeners[event];\n
\t\t\telse {\n
\t\t\t\t_listeners = {};\n
\t\t\t}\n
\t\t\treturn this;\n
\t\t};\n
\n
\t\tthis.getListener = function(forEvent) { return _listeners[forEvent]; };\n
\t\tthis.setSuspendEvents = function(val) { eventsSuspended = val; };\n
\t\tthis.isSuspendEvents = function() { return eventsSuspended; };\n
\t\tthis.cleanupListeners = function() {\n
\t\t\tfor (var i in _listeners) {\n
\t\t\t\t_listeners[i] = null;\n
\t\t\t}\n
\t\t};\n
\t};\n
\n
\tjsPlumbUtil.EventGenerator.prototype = {\n
\t\tcleanup:function() {\n
\t\t\tthis.cleanupListeners();\n
\t\t}\n
\t};\n
\n
    // thanks MDC\n
    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/bind?redirectlocale=en-US&redirectslug=JavaScript%2FReference%2FGlobal_Objects%2FFunction%2Fbind\n
    if (!Function.prototype.bind) {\n
      Function.prototype.bind = function (oThis) {\n
        if (typeof this !== "function") {\n
          // closest thing possible to the ECMAScript 5 internal IsCallable function\n
          throw new TypeError("Function.prototype.bind - what is trying to be bound is not callable");\n
        }\n
\n
        var aArgs = Array.prototype.slice.call(arguments, 1), \n
            fToBind = this, \n
            fNOP = function () {},\n
            fBound = function () {\n
              return fToBind.apply(this instanceof fNOP && oThis ? this : oThis,\n
                                   aArgs.concat(Array.prototype.slice.call(arguments)));\n
            };\n
\n
        fNOP.prototype = this.prototype;\n
        fBound.prototype = new fNOP();\n
\n
        return fBound;\n
      };\n
    }\n
\n
})();\n
/*\n
 * jsPlumb\n
 * \n
 * Title:jsPlumb 1.6.2\n
 * \n
 * Provides a way to visually connect elements on an HTML page, using SVG or VML.  \n
 * \n
 * This file contains the base functionality for DOM type adapters. \n
 *\n
 * Copyright (c) 2010 - 2014 Simon Porritt (simon@jsplumbtoolkit.com)\n
 * \n
 * http://jsplumbtoolkit.com\n
 * http://github.com/sporritt/jsplumb\n
 * \n
 * Dual licensed under the MIT and GPL2 licenses.\n
 */\n
;(function() {\n
    \n
\tvar svgAvailable = !!window.SVGAngle || document.implementation.hasFeature("http://www.w3.org/TR/SVG11/feature#BasicStructure", "1.1"),\n
\t\tvmlAvailable = function() {\t\t    \n
\t        if (vmlAvailable.vml === undefined) { \n
\t            var a = document.body.appendChild(document.createElement(\'div\'));\n
\t        \ta.innerHTML = \'<v:shape id="vml_flag1" adj="1" />\';\n
\t        \tvar b = a.firstChild;\n
\t        \tif (b != null && b.style != null) {\n
\t            \tb.style.behavior = "url(#default#VML)";\n
\t            \tvmlAvailable.vml = b ? typeof b.adj == "object": true;\n
\t            }\n
\t            else\n
\t            \tvmlAvailable.vml = false;\n
\t        \ta.parentNode.removeChild(a);\n
\t        }\n
\t        return vmlAvailable.vml;\n
\t\t},\n
\t\t// TODO: remove this once we remove all library adapter versions and have only vanilla jsplumb: this functionality\n
\t\t// comes from Mottle.\n
\t\tiev = (function() {\n
\t\t\tvar rv = -1; \n
\t\t\tif (navigator.appName == \'Microsoft Internet Explorer\') {\n
\t\t\t\tvar ua = navigator.userAgent,\n
\t\t\t\t\tre = new RegExp("MSIE ([0-9]{1,}[\\.0-9]{0,})");\n
\t\t\t\tif (re.exec(ua) != null)\n
\t\t\t\t\trv = parseFloat(RegExp.$1);\n
\t\t\t}\n
\t\t\treturn rv;\n
\t\t})(),\n
\t\tisIELT9 = iev > -1 && iev < 9, \n
\t\t_genLoc = function(e, prefix) {\n
\t\t\tif (e == null) return [ 0, 0 ];\n
\t\t\tvar ts = _touches(e), t = _getTouch(ts, 0);\n
\t\t\treturn [t[prefix + "X"], t[prefix + "Y"]];\n
\t\t},\n
\t\t_pageLocation = function(e) {\n
\t\t\tif (e == null) return [ 0, 0 ];\n
\t\t\tif (isIELT9) {\n
\t\t\t\treturn [ e.clientX + document.documentElement.scrollLeft, e.clientY + document.documentElement.scrollTop ];\n
\t\t\t}\n
\t\t\telse {\n
\t\t\t\treturn _genLoc(e, "page");\n
\t\t\t}\n
\t\t},\n
\t\t_screenLocation = function(e) {\n
\t\t\treturn _genLoc(e, "screen");\n
\t\t},\n
\t\t_clientLocation = function(e) {\n
\t\t\treturn _genLoc(e, "client");\n
\t\t},\n
\t\t_getTouch = function(touches, idx) { return touches.item ? touches.item(idx) : touches[idx]; },\n
\t\t_touches = function(e) {\n
\t\t\treturn e.touches && e.touches.length > 0 ? e.touches : \n
\t\t\t\t   e.changedTouches && e.changedTouches.length > 0 ? e.changedTouches :\n
\t\t\t\t   e.targetTouches && e.targetTouches.length > 0 ? e.targetTouches :\n
\t\t\t\t   [ e ];\n
\t\t};\n
        \n
    /**\n
\t\tManages dragging for some instance of jsPlumb.\n
\t*/\n
\tvar DragManager = function(_currentInstance) {\t\t\n
\t\tvar _draggables = {}, _dlist = [], _delements = {}, _elementsWithEndpoints = {},\t\t\t\n
\t\t\t// elementids mapped to the draggable to which they belong.\n
\t\t\t_draggablesForElements = {};\t\t\t\n
\n
        /**\n
            register some element as draggable.  right now the drag init stuff is done elsewhere, and it is\n
            possible that will continue to be the case.\n
        */\n
\t\tthis.register = function(el) {\n
            var id = _currentInstance.getId(el),\n
                parentOffset = jsPlumbAdapter.getOffset(el, _currentInstance);\n
                    \n
            if (!_draggables[id]) {\n
                _draggables[id] = el;\n
                _dlist.push(el);\n
                _delements[id] = {};\n
            }\n
\t\t\t\t\n
\t\t\t// look for child elements that have endpoints and register them against this draggable.\n
\t\t\tvar _oneLevel = function(p, startOffset) {\n
\t\t\t\tif (p) {\n
\t\t\t\t\tfor (var i = 0; i < p.childNodes.length; i++) {\n
\t\t\t\t\t\tif (p.childNodes[i].nodeType != 3 && p.childNodes[i].nodeType != 8) {\n
\t\t\t\t\t\t\tvar cEl = jsPlumb.getElementObject(p.childNodes[i]),\n
\t\t\t\t\t\t\t\tcid = _currentInstance.getId(p.childNodes[i], null, true);\n
\t\t\t\t\t\t\tif (cid && _elementsWithEndpoints[cid] && _elementsWithEndpoints[cid] > 0) {\n
\t\t\t\t\t\t\t\tvar cOff = jsPlumbAdapter.getOffset(cEl, _currentInstance);\n
\t\t\t\t\t\t\t\t_delements[id][cid] = {\n
\t\t\t\t\t\t\t\t\tid:cid,\n
\t\t\t\t\t\t\t\t\toffset:{\n
\t\t\t\t\t\t\t\t\t\tleft:cOff.left - parentOffset.left,\n
\t\t\t\t\t\t\t\t\t\ttop:cOff.top - parentOffset.top\n
\t\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\t};\n
\t\t\t\t\t\t\t\t_draggablesForElements[cid] = id;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t_oneLevel(p.childNodes[i]);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\t_oneLevel(el);\n
\t\t};\n
\t\t\n
\t\t// refresh the offsets for child elements of this element. \n
\t\tthis.updateOffsets = function(elId) {\n
\t\t\tif (elId != null) {\n
\t\t\t\tvar domEl = jsPlumb.getDOMElement(elId),\n
\t\t\t\t\tid = _currentInstance.getId(domEl),\n
\t\t\t\t\tchildren = _delements[id],\n
\t\t\t\t\tparentOffset = jsPlumbAdapter.getOffset(domEl, _currentInstance);\n
\t\t\t\t\t\n
\t\t\t\tif (children) {\n
\t\t\t\t\tfor (var i in children) {\n
\t\t\t\t\t\tvar cel = jsPlumb.getElementObject(i),\n
\t\t\t\t\t\t\tcOff = jsPlumbAdapter.getOffset(cel, _currentInstance);\n
\t\t\t\t\t\t\t\n
\t\t\t\t\t\t_delements[id][i] = {\n
\t\t\t\t\t\t\tid:i,\n
\t\t\t\t\t\t\toffset:{\n
\t\t\t\t\t\t\t\tleft:cOff.left - parentOffset.left,\n
\t\t\t\t\t\t\t\ttop:cOff.top - parentOffset.top\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t};\n
\t\t\t\t\t\t_draggablesForElements[i] = id;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t};\n
\n
\t\t/**\n
\t\t\tnotification that an endpoint was added to the given el.  we go up from that el\'s parent\n
\t\t\tnode, looking for a parent that has been registered as a draggable. if we find one, we add this\n
\t\t\tel to that parent\'s list of elements to update on drag (if it is not there already)\n
\t\t*/\n
\t\tthis.endpointAdded = function(el) {\n
\t\t\tvar b = document.body, id = _currentInstance.getId(el), \n
\t\t\t\tcLoc = jsPlumbAdapter.getOffset(el, _currentInstance),\n
\t\t\t\tp = el.parentNode, done = p == b;\n
\n
\t\t\t_elementsWithEndpoints[id] = _elementsWithEndpoints[id] ? _elementsWithEndpoints[id] + 1 : 1;\n
\n
\t\t\twhile (p != null && p != b) {\n
\t\t\t\tvar pid = _currentInstance.getId(p, null, true);\n
\t\t\t\tif (pid && _draggables[pid]) {\n
\t\t\t\t\tvar idx = -1, pLoc = jsPlumbAdapter.getOffset(p, _currentInstance);\n
\t\t\t\t\t\n
\t\t\t\t\tif (_delements[pid][id] == null) {\t\t\t\t\t\t\n
\t\t\t\t\t\t_delements[pid][id] = {\n
\t\t\t\t\t\t\tid:id,\n
\t\t\t\t\t\t\toffset:{\n
\t\t\t\t\t\t\t\tleft:cLoc.left - pLoc.left,\n
\t\t\t\t\t\t\t\ttop:cLoc.top - pLoc.top\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t};\n
\t\t\t\t\t\t_draggablesForElements[id] = pid;\n
\t\t\t\t\t}\n
\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\t\t\t\tp = p.parentNode;\n
\t\t\t}\t\n
\t\t};\n
\n
\t\tthis.endpointDeleted = function(endpoint) {\n
\t\t\tif (_elementsWithEndpoints[endpoint.elementId]) {\n
\t\t\t\t_elementsWithEndpoints[endpoint.elementId]--;\n
\t\t\t\tif (_elementsWithEndpoints[endpoint.elementId] <= 0) {\n
\t\t\t\t\tfor (var i in _delements) {\n
\t\t\t\t\t\tif (_delements[i]) {\n
                            delete _delements[i][endpoint.elementId];\n
                            delete _draggablesForElements[endpoint.elementId];\n
                        }\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\t\t\n
\t\t};\t\n
\t\t\n
\t\tthis.changeId = function(oldId, newId) {\t\t\t\t\n
\t\t\t_delements[newId] = _delements[oldId];\t\t\t\n
\t\t\t_delements[oldId] = {};\n
\t\t\t_draggablesForElements[newId] = _draggablesForElements[oldId];\n
\t\t\t_draggablesForElements[oldId] = null;\t\t\t\n
\t\t};\n
\n
\t\tthis.getElementsForDraggable = function(id) {\n
\t\t\treturn _delements[id];\t\n
\t\t};\n
\n
\t\tthis.elementRemoved = function(elementId) {\n
\t\t\tvar elId = _draggablesForElements[elementId];\n
\t\t\tif (elId) {\n
\t\t\t\tdelete _delements[elId][elementId];\n
\t\t\t\tdelete _draggablesForElements[elementId];\n
\t\t\t}\n
\t\t};\n
\n
\t\tthis.reset = function() {\n
\t\t\t_draggables = {};\n
\t\t\t_dlist = [];\n
\t\t\t_delements = {};\n
\t\t\t_elementsWithEndpoints = {};\n
\t\t};\n
\n
\t\t//\n
\t\t// notification drag ended. We check automatically if need to update some\n
\t\t// ancestor\'s offsets.\n
\t\t//\n
\t\tthis.dragEnded = function(el) {\t\t\t\n
\t\t\tvar id = _currentInstance.getId(el),\n
\t\t\t\tancestor = _draggablesForElements[id];\n
\n
\t\t\tif (ancestor) this.updateOffsets(ancestor);\n
\t\t};\n
\n
\t\tthis.setParent = function(el, elId, p, pId) {\n
\t\t\tvar current = _draggablesForElements[elId];\n
\t\t\tif (current) {\n
\t\t\t\tif (!_delements[pId])\n
\t\t\t\t\t_delements[pId] = {};\n
\t\t\t\t_delements[pId][elId] = _delements[current][elId];\n
\t\t\t\tdelete _delements[current][elId];\n
\t\t\t\tvar pLoc = jsPlumbAdapter.getOffset(p, _currentInstance),\n
\t\t\t\t\tcLoc = jsPlumbAdapter.getOffset(el, _currentInstance);\n
\t\t\t\t_delements[pId][elId].offset = {\n
\t\t\t\t\tleft:cLoc.left - pLoc.left,\n
\t\t\t\t\ttop:cLoc.top - pLoc.top\n
\t\t\t\t};\t\t\t\t\n
\t\t\t\t_draggablesForElements[elId] = pId;\n
\t\t\t}\t\t\t\n
\t\t};\n
\t\t\n
\t};\n
        \n
    // for those browsers that dont have it.  they still don\'t have it! but at least they won\'t crash.\n
\tif (!window.console)\n
\t\twindow.console = { time:function(){}, timeEnd:function(){}, group:function(){}, groupEnd:function(){}, log:function(){} };\n
\t\t\n
\t\t\n
\t// TODO: katavorio default helper uses this stuff.  should i extract to a support lib?\t\n
\tvar trim = function(str) {\n
\t\t\treturn str == null ? null : (str.replace(/^\\s\\s*/, \'\').replace(/\\s\\s*$/, \'\'));\n
\t\t},\n
\t\t_setClassName = function(el, cn) {\n
\t\t\tcn = trim(cn);\n
\t\t\tif (typeof el.className.baseVal != "undefined")  // SVG\n
\t\t\t\tel.className.baseVal = cn;\n
\t\t\telse\n
\t\t\t\tel.className = cn;\n
\t\t},\n
\t\t_getClassName = function(el) {\n
\t\t\treturn (typeof el.className.baseVal == "undefined") ? el.className : el.className.baseVal;\t\n
\t\t},\n
\t\t_classManip = function(el, add, clazz) {\n
\t\t\t\n
\t\t\t// TODO if classList exists, use it.\n
\t\t\t\n
\t\t\tvar classesToAddOrRemove = clazz.split(/\\s+/),\n
\t\t\t\tclassName = _getClassName(el),\n
\t\t\t\tcurClasses = className.split(/\\s+/);\n
\t\t\t\t\n
\t\t\tfor (var i = 0; i < classesToAddOrRemove.length; i++) {\n
\t\t\t\tif (add) {\n
\t\t\t\t\tif (jsPlumbUtil.indexOf(curClasses, classesToAddOrRemove[i]) == -1)\n
\t\t\t\t\t\tcurClasses.push(classesToAddOrRemove[i]);\n
\t\t\t\t}\n
\t\t\t\telse {\n
\t\t\t\t\tvar idx = jsPlumbUtil.indexOf(curClasses, classesToAddOrRemove[i]);\n
\t\t\t\t\tif (idx != -1)\n
\t\t\t\t\t\tcurClasses.splice(idx, 1);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t_setClassName(el, curClasses.join(" "));\n
\t\t},\n
\t\t_each = function(spec, fn) {\n
\t\t\tif (spec == null) return;\n
\t\t\tif (typeof spec === "string") \n
\t\t\t\tfn(jsPlumb.getDOMElement(spec));\n
\t\t\telse if (spec.length != null) {\n
\t\t\t\tfor (var i = 0; i < spec.length; i++)\n
\t\t\t\t\tfn(jsPlumb.getDOMElement(spec[i]));\n
\t\t\t}\n
\t\t\telse\n
\t\t\t\tfn(spec); // assume it\'s an element.\n
\t\t};\n
\n
    window.jsPlumbAdapter = {\n
        \n
        headless:false,\n
\n
        pageLocation:_pageLocation,\n
        screenLocation:_screenLocation,\n
        clientLocation:_clientLocation,\n
\n
        getAttribute:function(el, attName) {\n
        \treturn el.getAttribute(attName);\n
        },\n
\n
        setAttribute:function(el, a, v) {\n
        \tel.setAttribute(a, v);\n
        },\n
        \n
        appendToRoot : function(node) {\n
            document.body.appendChild(node);\n
        },\n
        getRenderModes : function() {\n
            return [ "svg", "vml" ];\n
        },\n
        isRenderModeAvailable : function(m) {\n
            return {\n
                "svg":svgAvailable,\n
                "vml":vmlAvailable()\n
            }[m];\n
        },\n
        getDragManager : function(_jsPlumb) {\n
            return new DragManager(_jsPlumb);\n
        },\n
        setRenderMode : function(mode) {\n
            var renderMode;\n
            \n
            if (mode) {\n
\t\t\t\tmode = mode.toLowerCase();            \n
\t\t\t            \n
                var svgAvailable = this.isRenderModeAvailable("svg"),\n
                    vmlAvailable = this.isRenderModeAvailable("vml");\n
                \n
                // now test we actually have the capability to do this.\n
                if (mode === "svg") {\n
                    if (svgAvailable) renderMode = "svg";\n
                    else if (vmlAvailable) renderMode = "vml";\n
                }\n
                else if (vmlAvailable) renderMode = "vml";\n
            }\n
\n
\t\t\treturn renderMode;\n
        },\n
\t\taddClass:function(el, clazz) {\n
\t\t\t_each(el, function(e) {\n
\t\t\t\t_classManip(e, true, clazz);\n
\t\t\t});\n
\t\t},\n
\t\thasClass:function(el, clazz) {\n
\t\t\tel = jsPlumb.getDOMElement(el);\n
\t\t\tif (el.classList) return el.classList.contains(clazz);\n
\t\t\telse {\n
\t\t\t\treturn _getClassName(el).indexOf(clazz) != -1;\n
\t\t\t}\n
\t\t},\n
\t\tremoveClass:function(el, clazz) {\n
\t\t\t_each(el, function(e) {\n
\t\t\t\t_classManip(e, false, clazz);\n
\t\t\t});\n
\t\t},\n
\t\tsetClass:function(el, clazz) {\n
\t\t\t_each(el, function(e) {\n
\t\t\t\t_setClassName(e, clazz);\n
\t\t\t});\n
\t\t},\n
\t\tsetPosition:function(el, p) {\n
\t\t\tel.style.left = p.left + "px";\n
\t\t\tel.style.top = p.top + "px";\n
\t\t},\n
\t\tgetPosition:function(el) {\n
\t\t\tvar _one = function(prop) {\n
\t\t\t\tvar v = el.style[prop];\n
\t\t\t\treturn v ? v.substring(0, v.length - 2) : 0;\n
\t\t\t};\n
\t\t\treturn {\n
\t\t\t\tleft:_one("left"),\n
\t\t\t\ttop:_one("top")\n
\t\t\t};\n
\t\t},\n
\t\tgetOffset:function(el, _instance, relativeToRoot) {\n
\t\t\tel = jsPlumb.getDOMElement(el);\n
\t\t\tvar container = _instance.getContainer();\n
\t\t\tvar l = el.offsetLeft, t = el.offsetTop, op = (relativeToRoot  || (container != null && el.offsetParent != container)) ?  el.offsetParent : null;\n
\t\t\twhile (op != null) {\n
\t\t\t\tl += op.offsetLeft;\n
\t\t\t\tt += op.offsetTop;\n
\t\t\t\top = relativeToRoot ? op.offsetParent : \n
\t\t\t\t\top.offsetParent == container ? null : op.offsetParent;\n
\t\t\t}\n
\t\t\treturn {\n
\t\t\t\tleft:l, top:t\n
\t\t\t};\n
\t\t},\n
\t\t//\n
\t\t// return x+y proportion of the given element\'s size corresponding to the location of the given event.\n
\t\t//\n
\t\tgetPositionOnElement:function(evt, el, zoom) {\n
\t\t\tvar box = typeof el.getBoundingClientRect !== "undefined" ? el.getBoundingClientRect() : { left:0, top:0, width:0, height:0 },\n
\t\t\t\tbody = document.body,\n
    \t\t\tdocElem = document.documentElement,\n
    \t\t\toffPar = el.offsetParent,\n
    \t\t\tscrollTop = window.pageYOffset || docElem.scrollTop || body.scrollTop,\n
\t\t\t\tscrollLeft = window.pageXOffset || docElem.scrollLeft || body.scrollLeft,\n
\t\t\t\tclientTop = docElem.clientTop || body.clientTop || 0,\n
\t\t\t\tclientLeft = docElem.clientLeft || body.clientLeft || 0,\n
\t\t\t\tpst = 0,//offPar ? offPar.scrollTop : 0,\n
\t\t\t\tpsl = 0,//offPar ? offPar.scrollLeft : 0,\n
\t\t\t\ttop  = box.top +  scrollTop - clientTop + (pst * zoom),\n
\t\t\t\tleft = box.left + scrollLeft - clientLeft + (psl * zoom),\n
\t\t\t\tcl = jsPlumbAdapter.pageLocation(evt),\n
\t\t\t\tw = box.width || (el.offsetWidth * zoom),\n
\t\t\t\th = box.height || (el.offsetHeight * zoom),\n
\t\t\t\tx = (cl[0] - left) / w,\n
\t\t\t\ty = (cl[1] - top) / h;\n
\n
\t\t\treturn [ x, y ];\n
\t\t}\n
    };\n
   \n
})();\n
/*\n
 * jsPlumb\n
 * \n
 * Title:jsPlumb 1.6.2\n
 * \n
 * Provides a way to visually connect elements on an HTML page, using SVG or VML.  \n
 * \n
 * This file contains the core code.\n
 *\n
 * Copyright (c) 2010 - 2014 Simon Porritt (simon@jsplumbtoolkit.com)\n
 * \n
 * http://jsplumbtoolkit.com\n
 * http://github.com/sporritt/jsplumb\n
 * \n
 * Dual licensed under the MIT and GPL2 licenses.\n
 */\n
;(function() {\n
\t\n
\t"use strict";\n
\t\t\t\n
    var _ju = jsPlumbUtil,\n
    \t_getOffset = function(el, _instance, relativeToRoot) {\n
            return jsPlumbAdapter.getOffset(el, _instance, relativeToRoot);\n
        },\n
\t\t\n
\t\t/**\n
\t\t * creates a timestamp, using milliseconds since 1970, but as a string.\n
\t\t */\n
\t\t_timestamp = function() { return "" + (new Date()).getTime(); },\n
\n
\t\t// helper method to update the hover style whenever it, or paintStyle, changes.\n
\t\t// we use paintStyle as the foundation and merge hoverPaintStyle over the\n
\t\t// top.\n
\t\t_updateHoverStyle = function(component) {\n
\t\t\tif (component._jsPlumb.paintStyle && component._jsPlumb.hoverPaintStyle) {\n
\t\t\t\tvar mergedHoverStyle = {};\n
\t\t\t\tjsPlumb.extend(mergedHoverStyle, component._jsPlumb.paintStyle);\n
\t\t\t\tjsPlumb.extend(mergedHoverStyle, component._jsPlumb.hoverPaintStyle);\n
\t\t\t\tdelete component._jsPlumb.hoverPaintStyle;\n
\t\t\t\t// we want the fillStyle of paintStyle to override a gradient, if possible.\n
\t\t\t\tif (mergedHoverStyle.gradient && component._jsPlumb.paintStyle.fillStyle)\n
\t\t\t\t\tdelete mergedHoverStyle.gradient;\n
\t\t\t\tcomponent._jsPlumb.hoverPaintStyle = mergedHoverStyle;\n
\t\t\t}\n
\t\t},\t\t\n
\t\tevents = [ "click", "dblclick", "mouseenter", "mouseout", "mousemove", "mousedown", "mouseup", "contextmenu" ],\n
\t\teventFilters = { "mouseout":"mouseleave", "mouseexit":"mouseleave" },\n
\t\t_updateAttachedElements = function(component, state, timestamp, sourceElement) {\n
\t\t\tvar affectedElements = component.getAttachedElements();\n
\t\t\tif (affectedElements) {\n
\t\t\t\tfor (var i = 0, j = affectedElements.length; i < j; i++) {\n
\t\t\t\t\tif (!sourceElement || sourceElement != affectedElements[i])\n
\t\t\t\t\t\taffectedElements[i].setHover(state, true, timestamp);\t\t\t// tell the attached elements not to inform their own attached elements.\n
\t\t\t\t}\n
\t\t\t}\n
\t\t},\n
\t\t_splitType = function(t) { return t == null ? null : t.split(" "); },\t\t\n
\t\t_applyTypes = function(component, params, doNotRepaint) {\n
\t\t\tif (component.getDefaultType) {\n
\t\t\t\tvar td = component.getTypeDescriptor();\n
\t\t\t\t\t\n
\t\t\t\tvar o = _ju.merge({}, component.getDefaultType());\n
\t\t\t\tfor (var i = 0, j = component._jsPlumb.types.length; i < j; i++)\n
\t\t\t\t\to = _ju.merge(o, component._jsPlumb.instance.getType(component._jsPlumb.types[i], td));\t\t\t\t\t\t\n
\t\t\t\t\t\n
\t\t\t\tif (params) {\n
\t\t\t\t\to = _ju.populate(o, params);\n
\t\t\t\t}\n
\t\t\t\n
\t\t\t\tcomponent.applyType(o, doNotRepaint);\t\t\t\t\t\n
\t\t\t\tif (!doNotRepaint) component.repaint();\n
\t\t\t}\n
\t\t},\t\t\n
\n
// ------------------------------ BEGIN jsPlumbUIComponent --------------------------------------------\n
\n
\t\tjsPlumbUIComponent = window.jsPlumbUIComponent = function(params) {\n
\n
\t\t\tjsPlumbUtil.EventGenerator.apply(this, arguments);\n
\n
\t\t\tvar self = this, \n
\t\t\t\ta = arguments, \t\t\t\t \t\t\t\t\n
\t\t\t\tidPrefix = self.idPrefix,\n
\t\t\t\tid = idPrefix + (new Date()).getTime();\n
\n
\t\t\tthis._jsPlumb = { \n
\t\t\t\tinstance: params._jsPlumb,\n
\t\t\t\tparameters:params.parameters || {},\n
\t\t\t\tpaintStyle:null,\n
\t\t\t\thoverPaintStyle:null,\n
\t\t\t\tpaintStyleInUse:null,\n
\t\t\t\thover:false,\n
\t\t\t\tbeforeDetach:params.beforeDetach,\n
\t\t\t\tbeforeDrop:params.beforeDrop,\n
\t\t\t\toverlayPlacements : [],\n
\t\t\t\thoverClass: params.hoverClass || params._jsPlumb.Defaults.HoverClass,\n
\t\t\t\ttypes:[]\n
\t\t\t};\n
\n
\t\t\tthis.getId = function() { return id; };\t\n
\t\t\t\n
\t\t\t// all components can generate events\n
\t\t\t\n
\t\t\tif (params.events) {\n
\t\t\t\tfor (var i in params.events)\n
\t\t\t\t\tself.bind(i, params.events[i]);\n
\t\t\t}\n
\n
\t\t\t// all components get this clone function.\n
\t\t\t// TODO issue 116 showed a problem with this - it seems \'a\' that is in\n
\t\t\t// the clone function\'s scope is shared by all invocations of it, the classic\n
\t\t\t// JS closure problem.  for now, jsPlumb does a version of this inline where \n
\t\t\t// it used to call clone.  but it would be nice to find some time to look\n
\t\t\t// further at this.\n
\t\t\tthis.clone = function() {\n
\t\t\t\tvar o = {};//new Object();\n
\t\t\t\tthis.constructor.apply(o, a);\n
\t\t\t\treturn o;\n
\t\t\t}.bind(this);\t\t\t\t\n
\t\t\t\t\t\t\n
\t\t\t// user can supply a beforeDetach callback, which will be executed before a detach\n
\t\t\t// is performed; returning false prevents the detach.\t\t\t\n
\t\t\tthis.isDetachAllowed = function(connection) {\n
\t\t\t\tvar r = true;\n
\t\t\t\tif (this._jsPlumb.beforeDetach) {\n
\t\t\t\t\ttry { \n
\t\t\t\t\t\tr = this._jsPlumb.beforeDetach(connection); \n
\t\t\t\t\t}\n
\t\t\t\t\tcatch (e) { _ju.log("jsPlumb: beforeDetach callback failed", e); }\n
\t\t\t\t}\n
\t\t\t\treturn r;\n
\t\t\t};\n
\t\t\t\n
\t\t\t// user can supply a beforeDrop callback, which will be executed before a dropped\n
\t\t\t// connection is confirmed. user can return false to reject connection.\t\t\t\n
\t\t\tthis.isDropAllowed = function(sourceId, targetId, scope, connection, dropEndpoint, source, target) {\n
\t\t\t\t\tvar r = this._jsPlumb.instance.checkCondition("beforeDrop", { \n
\t\t\t\t\t\tsourceId:sourceId, \n
\t\t\t\t\t\ttargetId:targetId, \n
\t\t\t\t\t\tscope:scope,\n
\t\t\t\t\t\tconnection:connection,\n
\t\t\t\t\t\tdropEndpoint:dropEndpoint,\n
\t\t\t\t\t\tsource:source, target:target\n
\t\t\t\t\t});\n
\t\t\t\t\tif (this._jsPlumb.beforeDrop) {\n
\t\t\t\t\t\ttry { \n
\t\t\t\t\t\t\tr = this._jsPlumb.beforeDrop({ \n
\t\t\t\t\t\t\t\tsourceId:sourceId, \n
\t\t\t\t\t\t\t\ttargetId:targetId, \n
\t\t\t\t\t\t\t\tscope:scope, \n
\t\t\t\t\t\t\t\tconnection:connection,\n
\t\t\t\t\t\t\t\tdropEndpoint:dropEndpoint,\n
\t\t\t\t\t\t\t\tsource:source, target:target\n
\t\t\t\t\t\t\t}); \n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tcatch (e) { _ju.log("jsPlumb: beforeDrop callback failed", e); }\n
\t\t\t\t\t}\n
\t\t\t\t\treturn r;\n
\t\t\t\t};\t\t\t\t\t\t\t\t\t\t\t\t\t\n
\n
\t\t    var boundListeners = [],\n
\t\t    \tbindAListener = function(obj, type, fn) {\n
\t\t\t    \tboundListeners.push([obj, type, fn]);\n
\t\t\t    \tobj.bind(type, fn);\n
\t\t\t    },\n
\t\t    \tdomListeners = [],\n
            \tbindOne = function(o, c, evt, override) {\n
\t\t\t\t\tvar filteredEvent = eventFilters[evt] || evt,\n
\t\t\t\t\t\tfn = function(ee) {\n
\t\t\t\t\t\t\tif (override && override(ee) === false) return;\n
\t\t\t\t\t\t\tc.fire(filteredEvent, c, ee);\n
\t\t\t\t\t\t};\n
\t\t\t\t\tdomListeners.push([o, evt, fn, c]);\n
\t\t\t\t\tc._jsPlumb.instance.on(o, evt, fn);\n
\t\t\t\t},\n
\t\t\t\tunbindOne = function(o, evt, fn, c) {\n
\t\t\t\t\tvar filteredEvent = eventFilters[evt] || evt;\n
\t\t\t\t\tc._jsPlumb.instance.off(o, evt, fn);\n
\t\t\t\t};\n
\n
            this.bindListeners = function(obj, _self, _hoverFunction) {\n
                bindAListener(obj, "click", function(ep, e) { _self.fire("click", _self, e); });             \n
             \tbindAListener(obj, "dblclick", function(ep, e) { _self.fire("dblclick", _self, e); });\n
                bindAListener(obj, "contextmenu", function(ep, e) { _self.fire("contextmenu", _self, e); });\n
                bindAListener(obj, "mouseleave", function(ep, e) {\n
                    if (_self.isHover()) {\n
                        _hoverFunction(false);\n
                        _self.fire("mouseleave", _self, e);\n
                    }\n
                });\n
                bindAListener(obj, "mouseenter", function(ep, e) {\n
                    if (!_self.isHover()) {\n
                        _hoverFunction(true);\n
                        _self.fire("mouseenter", _self, e);\n
                    }\n
                });\n
                bindAListener(obj, "mousedown", function(ep, e) { _self.fire("mousedown", _self, e); });\n
                bindAListener(obj, "mouseup", function(ep, e) { _self.fire("mouseup", _self, e); });\n
            };\n
\n
            this.unbindListeners = function() {\n
            \tfor (var i = 0; i < boundListeners.length; i++) {\n
            \t\tvar o = boundListeners[i];\n
            \t\to[0].unbind(o[1], o[2]);\n
            \t}            \t\n
            \tboundListeners = null;\n
            };            \n
\t\t    \n
\t\t    this.attachListeners = function(o, c, overrides) {\n
\t\t\t\toverrides = overrides || {};\n
\t\t\t\tfor (var i = 0, j = events.length; i < j; i++) {\n
\t\t\t\t\tbindOne(o, c, events[i], overrides[events[i]]); \t\t\t\n
\t\t\t\t}\n
\t\t\t};\t\n
\t\t\tthis.detachListeners = function() {\n
\t\t\t\tfor (var i = 0; i < domListeners.length; i++) {\n
\t\t\t\t\tunbindOne(domListeners[i][0], domListeners[i][1], domListeners[i][2], domListeners[i][3]);\n
\t\t\t\t}\n
\t\t\t\tdomListeners = null;\n
\t\t\t};\t   \t\t    \n
\t\t    \n
\t\t    this.reattachListenersForElement = function(o) {\n
\t\t\t    if (arguments.length > 1) {\n
\t\t    \t\tfor (var i = 0, j = events.length; i < j; i++)\n
\t\t    \t\t\tunbindOne(o, events[i]);\n
\t\t\t    \tfor (i = 1, j = arguments.length; i < j; i++)\n
\t\t    \t\t\tthis.attachListeners(o, arguments[i]);\n
\t\t    \t}\n
\t\t    };\t\t    \t    \t\t\t                      \n
\t\t};\n
\n
\t\tjsPlumbUtil.extend(jsPlumbUIComponent, jsPlumbUtil.EventGenerator, {\n
\t\t\t\n
\t\t\tgetParameter : function(name) { \n
\t\t\t\treturn this._jsPlumb.parameters[name]; \n
\t\t\t},\n
\t\t\t\n
\t\t\tsetParameter : function(name, value) { \n
\t\t\t\tthis._jsPlumb.parameters[name] = value; \n
\t\t\t},\n
\t\t\t\n
\t\t\tgetParameters : function() { \n
\t\t\t\treturn this._jsPlumb.parameters; \n
\t\t\t},\t\t\t\n
\t\t\t\n
\t\t\tsetParameters : function(p) { \n
\t\t\t\tthis._jsPlumb.parameters = p; \n
\t\t\t},\t\t\t\n
\t\t\t\n
\t\t\taddClass : function(clazz) {\n
\t\t\t    jsPlumbAdapter.addClass(this.canvas, clazz);\n
\t\t\t},\n
\t\t\t\t\t\t\n
\t\t\tremoveClass : function(clazz) {\n
\t\t\t    jsPlumbAdapter.removeClass(this.canvas, clazz);\n
\t\t\t},\n
\t\t\t\n
\t\t\tsetType : function(typeId, params, doNotRepaint) {\t\t\t\t\n
\t\t\t\tthis._jsPlumb.types = _splitType(typeId) || [];\n
\t\t\t\t_applyTypes(this, params, doNotRepaint);\t\t\t\t\t\t\t\t\t\n
\t\t\t},\n
\t\t\t\n
\t\t\tgetType : function() {\n
\t\t\t\treturn this._jsPlumb.types;\n
\t\t\t},\n
\t\t\t\n
\t\t\treapplyTypes : function(params, doNotRepaint) {\n
\t\t\t\t_applyTypes(this, params, doNotRepaint);\n
\t\t\t},\n
\t\t\t\n
\t\t\thasType : function(typeId) {\n
\t\t\t\treturn jsPlumbUtil.indexOf(this._jsPlumb.types, typeId) != -1;\n
\t\t\t},\n
\t\t\t\n
\t\t\taddType : function(typeId, params, doNotRepaint) {\n
\t\t\t\tvar t = _splitType(typeId), _cont = false;\n
\t\t\t\tif (t != null) {\n
\t\t\t\t\tfor (var i = 0, j = t.length; i < j; i++) {\n
\t\t\t\t\t\tif (!this.hasType(t[i])) {\n
\t\t\t\t\t\t\tthis._jsPlumb.types.push(t[i]);\n
\t\t\t\t\t\t\t_cont = true;\t\t\t\t\t\t\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\tif (_cont) _applyTypes(this, params, doNotRepaint);\n
\t\t\t\t}\n
\t\t\t},\n
\t\t\t\n
\t\t\tremoveType : function(typeId, doNotRepaint) {\n
\t\t\t\tvar t = _splitType(typeId), _cont = false, _one = function(tt) {\n
\t\t\t\t\t\tvar idx = _ju.indexOf(this._jsPlumb.types, tt);\n
\t\t\t\t\t\tif (idx != -1) {\n
\t\t\t\t\t\t\tthis._jsPlumb.types.splice(idx, 1);\n
\t\t\t\t\t\t\treturn true;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\treturn false;\n
\t\t\t\t\t}.bind(this);\n
\t\t\t\t\n
\t\t\t\tif (t != null) {\n
\t\t\t\t\tfor (var i = 0,j = t.length; i < j; i++) {\n
\t\t\t\t\t\t_cont = _one(t[i]) || _cont;\n
\t\t\t\t\t}\n
\t\t\t\t\tif (_cont) _applyTypes(this, null, doNotRepaint);\n
\t\t\t\t}\n
\t\t\t},\n
\t\t\t\n
\t\t\ttoggleType : function(typeId, params, doNotRepaint) {\n
\t\t\t\tvar t = _splitType(typeId);\n
\t\t\t\tif (t != null) {\n
\t\t\t\t\tfor (var i = 0, j = t.length; i < j; i++) {\n
\t\t\t\t\t\tvar idx = jsPlumbUtil.indexOf(this._jsPlumb.types, t[i]);\n
\t\t\t\t\t\tif (idx != -1)\n
\t\t\t\t\t\t\tthis._jsPlumb.types.splice(idx, 1);\n
\t\t\t\t\t\telse\n
\t\t\t\t\t\t\tthis._jsPlumb.types.push(t[i]);\n
\t\t\t\t\t}\n
\t\t\t\t\t\t\n
\t\t\t\t\t_applyTypes(this, params, doNotRepaint);\n
\t\t\t\t}\n
\t\t\t},\n
\t\t\tapplyType : function(t, doNotRepaint) {\n
\t\t\t\tthis.setPaintStyle(t.paintStyle, doNotRepaint);\t\t\t\t\n
\t\t\t\tthis.setHoverPaintStyle(t.hoverPaintStyle, doNotRepaint);\n
\t\t\t\tif (t.parameters){\n
\t\t\t\t\tfor (var i in t.parameters)\n
\t\t\t\t\t\tthis.setParameter(i, t.parameters[i]);\n
\t\t\t\t}\n
\t\t\t},\n
\t\t\tsetPaintStyle : function(style, doNotRepaint) {\n
//\t\t    \tthis._jsPlumb.paintStyle = jsPlumb.extend({}, style);\n
// TODO figure out if we want components to clone paintStyle so as not to share it.\n
\t\t\t\tthis._jsPlumb.paintStyle = style;\n
\t\t    \tthis._jsPlumb.paintStyleInUse = this._jsPlumb.paintStyle;\n
\t\t    \t_updateHoverStyle(this);\n
\t\t    \tif (!doNotRepaint) this.repaint();\n
\t\t    },\n
\t\t    getPaintStyle : function() {\n
\t\t    \treturn this._jsPlumb.paintStyle;\n
\t\t    },\n
\t\t    setHoverPaintStyle : function(style, doNotRepaint) {\t\t    \t\n
\t\t    \t//this._jsPlumb.hoverPaintStyle = jsPlumb.extend({}, style);\n
// TODO figure out if we want components to clone paintStyle so as not to share it.\t\t    \t\n
\t\t    \tthis._jsPlumb.hoverPaintStyle = style;\n
\t\t    \t_updateHoverStyle(this);\n
\t\t    \tif (!doNotRepaint) this.repaint();\n
\t\t    },\n
\t\t    getHoverPaintStyle : function() {\n
\t\t    \treturn this._jsPlumb.hoverPaintStyle;\n
\t\t    },\n
\t\t\tcleanup:function() {\n
\t\t\t\tthis.unbindListeners();\n
\t\t\t\tthis.detachListeners();\n
\t\t\t},\n
\t\t\tdestroy:function() {\n
\t\t\t\tthis.cleanupListeners();\n
\t\t\t\tthis.clone = null;\n
\t\t\t\tthis._jsPlumb = null;\n
\t\t\t},\n
\t\t\t\n
\t\t\tisHover : function() { return this._jsPlumb.hover; },\n
\t\t\t\n
\t\t\tsetHover : function(hover, ignoreAttachedElements, timestamp) {\n
\t\t\t\t// while dragging, we ignore these events.  this keeps the UI from flashing and\n
\t\t    \t// swishing and whatevering.\n
\t\t\t\tif (this._jsPlumb && !this._jsPlumb.instance.currentlyDragging && !this._jsPlumb.instance.isHoverSuspended()) {\n
\t\t    \n
\t\t\t    \tthis._jsPlumb.hover = hover;\n
                        \n
                    if (this.canvas != null) {\n
                        if (this._jsPlumb.instance.hoverClass != null) {\n
                        \tvar method = hover ? "addClass" : "removeClass";\n
\t\t\t\t\t\t\tthis._jsPlumb.instance[method](this.canvas, this._jsPlumb.instance.hoverClass);\n
                        }\n
                        if (this._jsPlumb.hoverClass != null) {\n
\t\t\t\t\t\t\tthis._jsPlumb.instance[method](this.canvas, this._jsPlumb.hoverClass);\n
                        }\n
                    }\n
\t\t   \t\t \tif (this._jsPlumb.hoverPaintStyle != null) {\n
\t\t\t\t\t\tthis._jsPlumb.paintStyleInUse = hover ? this._jsPlumb.hoverPaintStyle : this._jsPlumb.paintStyle;\n
\t\t\t\t\t\tif (!this._jsPlumb.instance.isSuspendDrawing()) {\n
\t\t\t\t\t\t\ttimestamp = timestamp || _timestamp();\n
\t\t\t\t\t\t\tthis.repaint({timestamp:timestamp, recalc:false});\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\t// get the list of other affected elements, if supported by this component.\n
\t\t\t\t\t// for a connection, its the endpoints.  for an endpoint, its the connections! surprise.\n
\t\t\t\t\tif (this.getAttachedElements && !ignoreAttachedElements)\n
\t\t\t\t\t\t_updateAttachedElements(this, hover, _timestamp(), this);\n
\t\t\t\t}\n
\t\t    }\n
\t\t});\n
\n
// ------------------------------ END jsPlumbUIComponent --------------------------------------------\n
\n
// ------------------------------ BEGIN OverlayCapablejsPlumbUIComponent --------------------------------------------\n
\n
\t\tvar _internalLabelOverlayId = "__label",\n
\t\t\t// helper to get the index of some overlay\n
\t\t\t_getOverlayIndex = function(component, id) {\n
\t\t\t\tvar idx = -1;\n
\t\t\t\tfor (var i = 0, j = component._jsPlumb.overlays.length; i < j; i++) {\n
\t\t\t\t\tif (id === component._jsPlumb.overlays[i].id) {\n
\t\t\t\t\t\tidx = i;\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\treturn idx;\n
\t\t\t},\n
\t\t\t// this is a shortcut helper method to let people add a label as\n
\t\t\t// overlay.\n
\t\t\t_makeLabelOverlay = function(component, params) {\n
\n
\t\t\t\tvar _params = {\n
\t\t\t\t\tcssClass:params.cssClass,\n
\t\t\t\t\tlabelStyle : component.labelStyle,\n
\t\t\t\t\tid:_internalLabelOverlayId,\n
\t\t\t\t\tcomponent:component,\n
\t\t\t\t\t_jsPlumb:component._jsPlumb.instance  // TODO not necessary, since the instance can be accessed through the component.\n
\t\t\t\t},\n
\t\t\t\tmergedParams = jsPlumb.extend(_params, params);\n
\n
\t\t\t\treturn new jsPlumb.Overlays[component._jsPlumb.instance.getRenderMode()].Label( mergedParams );\n
\t\t\t},\n
\t\t\t_processOverlay = function(component, o) {\n
\t\t\t\tvar _newOverlay = null;\n
\t\t\t\tif (_ju.isArray(o)) {\t// this is for the shorthand ["Arrow", { width:50 }] syntax\n
\t\t\t\t\t// there\'s also a three arg version:\n
\t\t\t\t\t// ["Arrow", { width:50 }, {location:0.7}] \n
\t\t\t\t\t// which merges the 3rd arg into the 2nd.\n
\t\t\t\t\tvar type = o[0],\n
\t\t\t\t\t\t// make a copy of the object so as not to mess up anyone else\'s reference...\n
\t\t\t\t\t\tp = jsPlumb.extend({component:component, _jsPlumb:component._jsPlumb.instance}, o[1]);\n
\t\t\t\t\tif (o.length == 3) jsPlumb.extend(p, o[2]);\n
\t\t\t\t\t_newOverlay = new jsPlumb.Overlays[component._jsPlumb.instance.getRenderMode()][type](p);\t\t\t\t\t\n
\t\t\t\t} else if (o.constructor == String) {\n
\t\t\t\t\t_newOverlay = new jsPlumb.Overlays[component._jsPlumb.instance.getRenderMode()][o]({component:component, _jsPlumb:component._jsPlumb.instance});\n
\t\t\t\t} else {\n
\t\t\t\t\t_newOverlay = o;\n
\t\t\t\t}\t\t\t\t\t\t\t\t\t\t\n
\t\t\t\t\t\n
\t\t\t\tcomponent._jsPlumb.overlays.push(_newOverlay);\n
\t\t\t},\n
\t\t\t_calculateOverlaysToAdd = function(component, params) {\n
\t\t\t\tvar defaultKeys = component.defaultOverlayKeys || [], o = params.overlays,\n
\t\t\t\t\tcheckKey = function(k) {\n
\t\t\t\t\t\treturn component._jsPlumb.instance.Defaults[k] || jsPlumb.Defaults[k] || [];\n
\t\t\t\t\t};\n
\t\t\t\t\n
\t\t\t\tif (!o) o = [];\n
\n
\t\t\t\tfor (var i = 0, j = defaultKeys.length; i < j; i++)\n
\t\t\t\t\to.unshift.apply(o, checkKey(defaultKeys[i]));\n
\t\t\t\t\n
\t\t\t\treturn o;\n
\t\t\t},\t\t\n
\t\t\tOverlayCapableJsPlumbUIComponent = window.OverlayCapableJsPlumbUIComponent = function(params) {\n
\n
\t\t\t\tjsPlumbUIComponent.apply(this, arguments);\n
\t\t\t\tthis._jsPlumb.overlays = [];\t\t\t\n
\n
\t\t\t\tvar _overlays = _calculateOverlaysToAdd(this, params);\n
\t\t\t\tif (_overlays) {\n
\t\t\t\t\tfor (var i = 0, j = _overlays.length; i < j; i++) {\n
\t\t\t\t\t\t_processOverlay(this, _overlays[i]);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tif (params.label) {\n
\t\t\t\t\tvar loc = params.labelLocation || this.defaultLabelLocation || 0.5,\n
\t\t\t\t\t\tlabelStyle = params.labelStyle || this._jsPlumb.instance.Defaults.LabelStyle;\n
\n
\t\t\t\t\tthis._jsPlumb.overlays.push(_makeLabelOverlay(this, {\n
\t\t\t\t\t\tlabel:params.label,\n
\t\t\t\t\t\tlocation:loc,\n
\t\t\t\t\t\tlabelStyle:labelStyle\n
\t\t\t\t\t}));\n
\t\t\t\t}\t\t\t                                  \n
\t\t\t};\n
\n
\t\tjsPlumbUtil.extend(OverlayCapableJsPlumbUIComponent, jsPlumbUIComponent, {\n
\t\t\tapplyType : function(t, doNotRepaint) {\t\t\t\n
\t\t\t\tthis.removeAllOverlays(doNotRepaint);\n
\t\t\t\tif (t.overlays) {\n
\t\t\t\t\tfor (var i = 0, j = t.overlays.length; i < j; i++)\n
\t\t\t\t\t\tthis.addOverlay(t.overlays[i], true);\n
\t\t\t\t}\n
\t\t\t},\n
\t\t\tsetHover : function(hover, ignoreAttachedElements, timestamp) {            \n
\t\t\t\tif (this._jsPlumb && !this._jsPlumb.instance.isConnectionBeingDragged()) {\n
\t                for (var i = 0, j = this._jsPlumb.overlays.length; i < j; i++) {\n
\t\t\t\t\t\tthis._jsPlumb.overlays[i][hover ? "addClass":"removeClass"](this._jsPlumb.instance.hoverClass);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
            },\n
            addOverlay : function(overlay, doNotRepaint) { \n
\t\t\t\t_processOverlay(this, overlay); \n
\t\t\t\tif (!doNotRepaint) this.repaint();\n
\t\t\t},\n
\t\t\tgetOverlay : function(id) {\n
\t\t\t\tvar idx = _getOverlayIndex(this, id);\n
\t\t\t\treturn idx >= 0 ? this._jsPlumb.overlays[idx] : null;\n
\t\t\t},\t\t\t\n
\t\t\tgetOverlays : function() {\n
\t\t\t\treturn this._jsPlumb.overlays;\n
\t\t\t},\t\t\t\n
\t\t\thideOverlay : function(id) {\n
\t\t\t\tvar o = this.getOverlay(id);\n
\t\t\t\tif (o) o.hide();\n
\t\t\t},\n
\t\t\thideOverlays : function() {\n
\t\t\t\tfor (var i = 0, j = this._jsPlumb.overlays.length; i < j; i++)\n
\t\t\t\t\tthis._jsPlumb.overlays[i].hide();\n
\t\t\t},\n
\t\t\tshowOverlay : function(id) {\n
\t\t\t\tvar o = this.getOverlay(id);\n
\t\t\t\tif (o) o.show();\n
\t\t\t},\n
\t\t\tshowOverlays : function() {\n
\t\t\t\tfor (var i = 0, j = this._jsPlumb.overlays.length; i < j; i++)\n
\t\t\t\t\tthis._jsPlumb.overlays[i].show();\n
\t\t\t},\n
\t\t\tremoveAllOverlays : function(doNotRepaint) {\n
\t\t\t\tfor (var i = 0, j = this._jsPlumb.overlays.length; i < j; i++) {\n
\t\t\t\t\tif (this._jsPlumb.overlays[i].cleanup) this._jsPlumb.overlays[i].cleanup();\n
\t\t\t\t}\n
\n
\t\t\t\tthis._jsPlumb.overlays.splice(0, this._jsPlumb.overlays.length);\n
\t\t\t\tthis._jsPlumb.overlayPositions = null;\n
\t\t\t\tif (!doNotRepaint)\n
\t\t\t\t\tthis.repaint();\n
\t\t\t},\n
\t\t\tremoveOverlay : function(overlayId) {\n
\t\t\t\tvar idx = _getOverlayIndex(this, overlayId);\n
\t\t\t\tif (idx != -1) {\n
\t\t\t\t\tvar o = this._jsPlumb.overlays[idx];\n
\t\t\t\t\tif (o.cleanup) o.cleanup();\n
\t\t\t\t\tthis._jsPlumb.overlays.splice(idx, 1);\n
\t\t\t\t\tif (this._jsPlumb.overlayPositions)  \n
\t\t\t\t\t\tdelete this._jsPlumb.overlayPositions[overlayId];\n
\t\t\t\t}\n
\t\t\t},\n
\t\t\tremoveOverlays : function() {\n
\t\t\t\tfor (var i = 0, j = arguments.length; i < j; i++)\n
\t\t\t\t\tthis.removeOverlay(arguments[i]);\n
\t\t\t},\n
\t\t\tmoveParent:function(newParent) {\n
\t\t\t\tif (this.bgCanvas) {\n
\t\t\t\t    this.bgCanvas.parentNode.removeChild(this.bgCanvas);\n
\t\t\t\t    newParent.appendChild(this.bgCanvas);\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tthis.canvas.parentNode.removeChild(this.canvas);\n
\t\t\t\tnewParent.appendChild(this.canvas);\n
\n
\t\t\t\tfor (var i = 0; i < this._jsPlumb.overlays.length; i++) {\n
\t\t\t\t    if (this._jsPlumb.overlays[i].isAppendedAtTopLevel) {\n
\t\t\t\t        this._jsPlumb.overlays[i].canvas.parentNode.removeChild(this._jsPlumb.overlays[i].canvas);\n
\t\t\t\t        newParent.appendChild(this._jsPlumb.overlays[i].canvas);  \n
\t\t\t\t    }\n
\t\t\t\t}\n
\t\t\t},\n
\t\t\tgetLabel : function() {\n
\t\t\t\tvar lo = this.getOverlay(_internalLabelOverlayId);\n
\t\t\t\treturn lo != null ? lo.getLabel() : null;\n
\t\t\t},\t\t\n
\t\t\tgetLabelOverlay : function() {\n
\t\t\t\treturn this.getOverlay(_internalLabelOverlayId);\n
\t\t\t},\n
\t\t\tsetLabel : function(l) {\n
\t\t\t\tvar lo = this.getOverlay(_internalLabelOverlayId);\n
\t\t\t\tif (!lo) {\n
\t\t\t\t\tvar params = l.constructor == String || l.constructor == Function ? { label:l } : l;\n
\t\t\t\t\tlo = _makeLabelOverlay(this, params);\t\n
\t\t\t\t\tthis._jsPlumb.overlays.push(lo);\n
\t\t\t\t}\n
\t\t\t\telse {\n
\t\t\t\t\tif (l.constructor == String || l.constructor == Function) lo.setLabel(l);\n
\t\t\t\t\telse {\n
\t\t\t\t\t\tif (l.label) lo.setLabel(l.label);\n
\t\t\t\t\t\tif (l.location) lo.setLocation(l.location);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tif (!this._jsPlumb.instance.isSuspendDrawing()) \n
\t\t\t\t\tthis.repaint();\n
\t\t\t},\n
\t\t\tcleanup:function() {\n
\t\t\t\tfor (var i = 0; i < this._jsPlumb.overlays.length; i++) {\n
\t\t\t\t\tthis._jsPlumb.overlays[i].cleanup();\n
\t\t\t\t\tthis._jsPlumb.overlays[i].destroy();\n
\t\t\t\t}\n
\t\t\t\tthis._jsPlumb.overlays.splice(0);\n
\t\t\t\tthis._jsPlumb.overlayPositions = null;\n
\t\t\t},\n
\t\t\tsetVisible:function(v) {\n
\t\t\t\tthis[v ? "showOverlays" : "hideOverlays"]();\n
\t\t\t},\n
\t\t\tsetAbsoluteOverlayPosition:function(overlay, xy) {\n
\t\t\t\tthis._jsPlumb.overlayPositions = this._jsPlumb.overlayPositions || {};\n
\t\t\t\tthis._jsPlumb.overlayPositions[overlay.id] = xy;\n
\t\t\t},\n
\t\t\tgetAbsoluteOverlayPosition:function(overlay) {\n
\t\t\t\treturn this._jsPlumb.overlayPositions ? this._jsPlumb.overlayPositions[overlay.id] : null;\n
\t\t\t}\n
\t\t});\t\t\n
\n
// ------------------------------ END OverlayCapablejsPlumbUIComponent --------------------------------------------\n
\t\t\n
\t\tvar _jsPlumbInstanceIndex = 0,\n
\t\t\tgetInstanceIndex = function() {\n
\t\t\t\tvar i = _jsPlumbInstanceIndex + 1;\n
\t\t\t\t_jsPlumbInstanceIndex++;\n
\t\t\t\treturn i;\n
\t\t\t};\n
\n
\t\tvar jsPlumbInstance = window.jsPlumbInstance = function(_defaults) {\n
\t\t\t\t\n
\t\t\tthis.Defaults = {\n
\t\t\t\tAnchor : "BottomCenter",\n
\t\t\t\tAnchors : [ null, null ],\n
\t            ConnectionsDetachable : true,\n
\t            ConnectionOverlays : [ ],\n
\t            Connector : "Bezier",\n
\t\t\t\tContainer : null,\n
\t\t\t\tDoNotThrowErrors:false,\n
\t\t\t\tDragOptions : { },\n
\t\t\t\tDropOptions : { },\n
\t\t\t\tEndpoint : "Dot",\n
\t\t\t\tEndpointOverlays : [ ],\n
\t\t\t\tEndpoints : [ null, null ],\n
\t\t\t\tEndpointStyle : { fillStyle : "#456" },\n
\t\t\t\tEndpointStyles : [ null, null ],\n
\t\t\t\tEndpointHoverStyle : null,\n
\t\t\t\tEndpointHoverStyles : [ null, null ],\n
\t\t\t\tHoverPaintStyle : null,\n
\t\t\t\tLabelStyle : { color : "black" },\n
\t\t\t\tLogEnabled : false,\n
\t\t\t\tOverlays : [ ],\n
\t\t\t\tMaxConnections : 1, \n
\t\t\t\tPaintStyle : { lineWidth : 8, strokeStyle : "#456" },            \n
\t\t\t\tReattachConnections:false,\n
\t\t\t\tRenderMode : "svg",\n
\t\t\t\tScope : "jsPlumb_DefaultScope"\n
\t\t\t};\n
\t\t\tif (_defaults) jsPlumb.extend(this.Defaults, _defaults);\n
\t\t\n
\t\t\tthis.logEnabled = this.Defaults.LogEnabled;\n
\t\t\tthis._connectionTypes = {};\n
\t\t\tthis._endpointTypes = {};\n
\n
\t\t\tjsPlumbUtil.EventGenerator.apply(this);\n
\n
\t\t\tvar _currentInstance = this,\n
\t\t\t\t_instanceIndex = getInstanceIndex(),\n
\t\t\t\t_bb = _currentInstance.bind,\n
\t\t\t\t_initialDefaults = {},\n
\t            _zoom = 1,\n
\t            _info = function(el) {\n
\t            \tvar _el = _currentInstance.getDOMElement(el);\t\n
\t            \treturn { el:_el, id:(jsPlumbUtil.isString(el) && _el == null) ? el : _getId(_el) };\n
\t            };\n
            \n
\t        this.getInstanceIndex = function() { return _instanceIndex; };\n
\n
        \tthis.setZoom = function(z, repaintEverything) {\n
        \t\tif (!jsPlumbUtil.oldIE) {\n
\t            \t_zoom = z;\n
\t\t\t\t\t_currentInstance.fire("zoom", _zoom);\n
\t            \tif (repaintEverything) _currentInstance.repaintEverything();\n
\t            }\n
\t            return !jsPlumbUtil.oldIE;\n
\n
        \t};\n
        \tthis.getZoom = function() { return _zoom; };\n
                        \n
\t\t\tfor (var i in this.Defaults)\n
\t\t\t\t_initialDefaults[i] = this.Defaults[i];\n
\n
\t\t\tvar _container;\n
\t\t\tthis.setContainer = function(c) {\n
\t\t\t\tc = this.getDOMElement(c);\n
\t\t\t\tthis.select().each(function(conn) {\n
\t\t\t\t\tconn.moveParent(c);\n
\t\t\t\t});\n
\t\t\t\tthis.selectEndpoints().each(function(ep) {\n
\t\t\t\t\tep.moveParent(c);\n
\t\t\t\t});\n
\t\t\t\t_container = c;\n
\t\t\t};\n
\t\t\tthis.getContainer = function() {\n
\t\t\t\treturn _container;\n
\t\t\t};\n
\t\t\t\n
\t\t\tthis.bind = function(event, fn) {\t\t\n
\t\t\t\tif ("ready" === event && initialized) fn();\n
\t\t\t\telse _bb.apply(_currentInstance,[event, fn]);\n
\t\t\t};\n
\n
\t\t\t_currentInstance.importDefaults = function(d) {\n
\t\t\t\tfor (var i in d) {\n
\t\t\t\t\t_currentInstance.Defaults[i] = d[i];\n
\t\t\t\t}\n
\t\t\t\tif (d.Container)\n
\t\t\t\t\tthis.setContainer(d.Container);\n
\n
\t\t\t\treturn _currentInstance;\n
\t\t\t};\t\t\n
\t\t\t\n
\t\t\t_currentInstance.restoreDefaults = function() {\n
\t\t\t\t_currentInstance.Defaults = jsPlumb.extend({}, _initialDefaults);\n
\t\t\t\treturn _currentInstance;\n
\t\t\t};\n
\t\t\n
\t\t    var log = null,\n
\t\t        resizeTimer = null,\n
\t\t        initialized = false,\n
\t\t        // TODO remove from window scope       \n
\t\t        connections = [],\n
\t\t        // map of element id -> endpoint lists. an element can have an arbitrary\n
\t\t        // number of endpoints on it, and not all of them have to be connected\n
\t\t        // to anything.         \n
\t\t        endpointsByElement = {},\n
\t\t        endpointsByUUID = {},\n
\t\t        offsets = {},\n
\t\t        offsetTimestamps = {},\n
\t\t        floatingConnections = {},\n
\t\t        draggableStates = {},\t\t\n
\t\t        connectionBeingDragged = false,\n
\t\t        sizes = [],\n
\t\t        _suspendDrawing = false,\n
\t\t        _suspendedAt = null,\n
\t\t        DEFAULT_SCOPE = this.Defaults.Scope,\n
\t\t        renderMode = null,  // will be set in init()\t\t\n
\t\t        _curIdStamp = 1,\n
\t\t        _idstamp = function() { return "" + _curIdStamp++; },\t\t\t\t\t\t\t\n
\t\t\n
\t\t\t\t//\n
\t\t\t\t// appends an element to some other element, which is calculated as follows:\n
\t\t\t\t// \n
\t\t\t\t// 1. if Container exists, use that element.\n
\t\t\t\t// 2. if the \'parent\' parameter exists, use that.\n
\t\t\t\t// 3. otherwise just use the root element (for DOM usage, the document body).\n
\t\t\t\t// \n
\t\t\t\t//\n
\t\t\t\t_appendElement = function(el, parent) {\n
\t\t\t\t\tif (_container)\n
\t\t\t\t\t\t_container.appendChild(el);\n
\t\t\t\t\telse if (!parent)\n
\t\t\t\t\t\t_currentInstance.appendToRoot(el);\n
\t\t\t\t\telse\n
\t\t\t\t\t\tjsPlumb.getDOMElement(parent).appendChild(el);\n
\t\t\t\t},\t\t\n
\t\t\t\t\n
\t\t\t\t//\n
\t\t\t\t// YUI, for some reason, put the result of a Y.all call into an object that contains\n
\t\t\t\t// a \'_nodes\' array, instead of handing back an array-like object like the other\n
\t\t\t\t// libraries do.\n
\t\t\t\t//\n
\t\t\t\t_convertYUICollection = function(c) {\n
\t\t\t\t\treturn c._nodes ? c._nodes : c;\n
\t\t\t\t},                \n
\n
\t\t\t//\n
\t\t\t// Draws an endpoint and its connections. this is the main entry point into drawing connections as well\n
\t\t\t// as endpoints, since jsPlumb is endpoint-centric under the hood.\n
\t\t\t// \n
\t\t\t// @param element element to draw (of type library specific element object)\n
\t\t\t// @param ui UI object from current library\'s event system. optional.\n
\t\t\t// @param timestamp timestamp for this paint cycle. used to speed things up a little by cutting down the amount of offset calculations we do.\n
\t\t\t// @param clearEdits defaults to false; indicates that mouse edits for connectors should be cleared\n
\t\t\t///\n
\t\t\t_draw = function(element, ui, timestamp, clearEdits) {\n
\n
\t\t\t\t// TODO is it correct to filter by headless at this top level? how would a headless adapter ever repaint?\n
\t            if (!jsPlumbAdapter.headless && !_suspendDrawing) {\n
\t\t\t\t    var id = _getId(element),\n
\t\t\t\t    \trepaintEls = _currentInstance.dragManager.getElementsForDraggable(id);\t\t\t    \n
\n
\t\t\t\t    if (timestamp == null) timestamp = _timestamp();\n
\n
\t\t\t\t    // update the offset of everything _before_ we try to draw anything.\n
\t\t\t\t    var o = _updateOffset( { elId : id, offset : ui, recalc : false, timestamp : timestamp });\n
\n
\t\t\t        if (repaintEls) {\n
\t\t\t    \t    for (var i in repaintEls) {\n
\t\t\t    \t    \t// TODO this seems to cause a lag, but we provide the offset, so in theory it \n
\t\t\t    \t    \t// should not.  is the timestamp failing?\n
\t\t\t\t    \t\t_updateOffset( { \n
\t\t\t\t    \t\t\telId : repaintEls[i].id, \n
\t\t\t\t    \t\t\toffset : {\n
\t\t\t\t\t\t\t\t\tleft:o.o.left + repaintEls[i].offset.left,\n
\t\t\t\t\t    \t\t\ttop:o.o.top + repaintEls[i].offset.top\n
\t\t\t\t\t    \t\t}, \n
\t\t\t\t    \t\t\trecalc : false, \n
\t\t\t\t    \t\t\ttimestamp : timestamp \n
\t\t\t\t    \t\t});\n
\t\t\t\t    \t}\n
\t\t\t\t    }\t\n
\t\t\t\t    \t\t          \n
\n
\t\t\t\t    _currentInstance.anchorManager.redraw(id, ui, timestamp, null, clearEdits);\n
\t\t\t\t    \n
\t\t\t\t    if (repaintEls) {\n
\t\t\t\t\t    for (var j in repaintEls) {\n
\t\t\t\t\t\t\t_currentInstance.anchorManager.redraw(repaintEls[j].id, ui, timestamp, repaintEls[j].offset, clearEdits, true);\t\t\t    \t\n
\t\t\t\t\t    }\n
\t\t\t\t\t}\t\t\n
\t            }\n
\t\t\t},\n
\n
\t\t\t//\n
\t\t\t// executes the given function against the given element if the first\n
\t\t\t// argument is an object, or the list of elements, if the first argument\n
\t\t\t// is a list. the function passed in takes (element, elementId) as\n
\t\t\t// arguments.\n
\t\t\t//\n
\t\t\t_elementProxy = function(element, fn) {\n
\t\t\t\tvar retVal = null, el, id, del;\n
\t\t\t\tif (_ju.isArray(element)) {\n
\t\t\t\t\tretVal = [];\n
\t\t\t\t\tfor ( var i = 0, j = element.length; i < j; i++) {\n
\t\t\t\t\t\tel = _currentInstance.getElementObject(element[i]);\n
\t\t\t\t\t\tdel = _currentInstance.getDOMElement(el);\n
\t\t\t\t\t\tid = _currentInstance.getAttribute(del, "id");\n
\t\t\t\t\t\t//retVal.push(fn(el, id)); // append return values to what we will return\n
\t\t\t\t\t\tretVal.push(fn.apply(_currentInstance, [del, id])); // append return values to what we will return\n
\t\t\t\t\t}\n
\t\t\t\t} else {\n
\t\t\t\t\tel = _currentInstance.getDOMElement(element);\n
\t\t\t\t\tid = _currentInstance.getId(el);\n
\t\t\t\t\tretVal = fn.apply(_currentInstance, [el, id]);\n
\t\t\t\t}\n
\t\t\t\treturn retVal;\n
\t\t\t},\t\t\t\t\n
\n
\t\t\t//\n
\t\t\t// gets an Endpoint by uuid.\n
\t\t\t//\n
\t\t\t_getEndpoint = function(uuid) { return endpointsByUUID[uuid]; },\n
\n
\t\t/**\n
\t\t * inits a draggable if it\'s not already initialised.\n
\t\t * TODO: somehow abstract this to the adapter, because the concept of "draggable" has no\n
\t\t * place on the server.\n
\t\t */\n
\t\t_initDraggableIfNecessary = function(element, isDraggable, dragOptions) {\n
\t\t\t// TODO move to DragManager?\n
\t\t\tif (!jsPlumbAdapter.headless) {\n
\t\t\t\tvar _draggable = isDraggable == null ? false : isDraggable;\n
\t\t\t\tif (_draggable) {\n
\t\t\t\t\tif (jsPlumb.isDragSupported(element, _currentInstance) && !jsPlumb.isAlreadyDraggable(element, _currentInstance)) {\n
\t\t\t\t\t\tvar options = dragOptions || _currentInstance.Defaults.DragOptions;\n
\t\t\t\t\t\toptions = jsPlumb.extend( {}, options); // make a copy.\n
\t\t\t\t\t\tvar dragEvent = jsPlumb.dragEvents.drag,\n
\t\t\t\t\t\t\tstopEvent = jsPlumb.dragEvents.stop,\n
\t\t\t\t\t\t\tstartEvent = jsPlumb.dragEvents.start;\n
\t\n
\t\t\t\t\t\toptions[startEvent] = _ju.wrap(options[startEvent], function() {\n
\t\t\t\t\t\t\t_currentInstance.setHoverSuspended(true);\t\t\t\t\t\t\t\n
\t\t\t\t\t\t\t_currentInstance.select({source:element}).addClass(_currentInstance.elementDraggingClass + " " + _currentInstance.sourceElementDraggingClass, true);\n
\t\t\t\t\t\t\t_currentInstance.select({target:element}).addClass(_currentInstance.elementDraggingClass + " " + _currentInstance.targetElementDraggingClass, true);\n
\t\t\t\t\t\t\t_currentInstance.setConnectionBeingDragged(true);\n
\t\t\t\t\t\t\tif (options.canDrag) return dragOptions.canDrag();\n
\t\t\t\t\t\t}, false);\n
\t\n
\t\t\t\t\t\toptions[dragEvent] = _ju.wrap(options[dragEvent], function() {\n
\t\t\t\t\t\t\t// TODO: here we could actually use getDragObject, and then compute it ourselves,\n
\t\t\t\t\t\t\t// since every adapter does the same thing. but i\'m not sure why YUI\'s getDragObject\n
\t\t\t\t\t\t\t// differs from getUIPosition so much\n
\t\t\t\t\t\t\tvar ui = _currentInstance.getUIPosition(arguments, _currentInstance.getZoom());\n
\t\t\t\t\t\t\t_draw(element, ui, null, true);\n
\t\t\t\t\t\t\t_currentInstance.addClass(element, "jsPlumb_dragged");\n
\t\t\t\t\t\t});\n
\t\t\t\t\t\toptions[stopEvent] = _ju.wrap(options[stopEvent], function() {\n
\t\t\t\t\t\t\tvar ui = _currentInstance.getUIPosition(arguments, _currentInstance.getZoom(), true);\n
\t\t\t\t\t\t\t_draw(element, ui);\n
\t\t\t\t\t\t\t_currentInstance.removeClass(element, "jsPlumb_dragged");\n
\t\t\t\t\t\t\t_currentInstance.setHoverSuspended(false);\t\t\t\t\t\t\t\n
\t\t\t\t\t\t\t_currentInstance.select({source:element}).removeClass(_currentInstance.elementDraggingClass + " " + _currentInstance.sourceElementDraggingClass, true);\n
\t\t\t\t\t\t\t_currentInstance.select({target:element}).removeClass(_currentInstance.elementDraggingClass + " " + _currentInstance.targetElementDraggingClass, true);\n
\t\t\t\t\t\t\t_currentInstance.setConnectionBeingDragged(false);\n
\t\t\t\t\t\t\t_currentInstance.dragManager.dragEnded(element);\n
\t\t\t\t\t\t});\n
\t\t\t\t\t\tvar elId = _getId(element); // need ID\n
\t\t\t\t\t\tdraggableStates[elId] = true;  \n
\t\t\t\t\t\tvar draggable = draggableStates[elId];\n
\t\t\t\t\t\toptions.disabled = draggable == null ? false : !draggable;\n
\t\t\t\t\t\t_currentInstance.initDraggable(element, options, false);\n
\t\t\t\t\t\t_currentInstance.dragManager.register(element);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t},\n
\t\t\n
\t\t/*\n
\t\t* prepares a final params object that can be passed to _newConnection, taking into account defaults, events, etc.\n
\t\t*/\n
\t\t_prepareConnectionParams = function(params, referenceParams) {\n
\t\t\tvar _p = jsPlumb.extend( { }, params);\n
\t\t\tif (referenceParams) jsPlumb.extend(_p, referenceParams);\n
\t\t\t\n
\t\t\t// hotwire endpoints passed as source or target to sourceEndpoint/targetEndpoint, respectively.\n
\t\t\tif (_p.source) {\n
\t\t\t\tif (_p.source.endpoint) \n
\t\t\t\t\t_p.sourceEndpoint = _p.source;\n
\t\t\t\telse\n
\t\t\t\t\t_p.source = _currentInstance.getDOMElement(_p.source);\n
\t\t\t}\n
\t\t\tif (_p.target) {\n
\t\t\t\tif (_p.target.endpoint) \n
\t\t\t\t\t_p.targetEndpoint = _p.target;\n
\t\t\t\telse\n
\t\t\t\t\t_p.target = _currentInstance.getDOMElement(_p.target);\n
\t\t\t}\n
\t\t\t\n
\t\t\t// test for endpoint uuids to connect\n
\t\t\tif (params.uuids) {\n
\t\t\t\t_p.sourceEndpoint = _getEndpoint(params.uuids[0]);\n
\t\t\t\t_p.targetEndpoint = _getEndpoint(params.uuids[1]);\n
\t\t\t}\t\t\t\t\t\t\n
\n
\t\t\t// now ensure that if we do have Endpoints already, they\'re not full.\n
\t\t\t// source:\n
\t\t\tif (_p.sourceEndpoint && _p.sourceEndpoint.isFull()) {\n
\t\t\t\t_ju.log(_currentInstance, "could not add connection; source endpoint is full");\n
\t\t\t\treturn;\n
\t\t\t}\n
\n
\t\t\t// target:\n
\t\t\tif (_p.targetEndpoint && _p.targetEndpoint.isFull()) {\n
\t\t\t\t_ju.log(_currentInstance, "could not add connection; target endpoint is full");\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\t\n
\t\t\t// if source endpoint mandates connection type and nothing specified in our params, use it.\n
\t\t\tif (!_p.type && _p.sourceEndpoint)\n
\t\t\t\t_p.type = _p.sourceEndpoint.connectionType;\n
\t\t\t\n
\t\t\t// copy in any connectorOverlays that were specified on the source endpoint.\n
\t\t\t// it doesnt copy target endpoint overlays.  i\'m not sure if we want it to or not.\n
\t\t\tif (_p.sourceEndpoint && _p.sourceEndpoint.connectorOverlays) {\n
\t\t\t\t_p.overlays = _p.overlays || [];\n
\t\t\t\tfor (var i = 0, j = _p.sourceEndpoint.connectorOverlays.length; i < j; i++) {\n
\t\t\t\t\t_p.overlays.push(_p.sourceEndpoint.connectorOverlays[i]);\n
\t\t\t\t}\n
\t\t\t}\t\t\n
            \n
            // pointer events\n
            if (!_p["pointer-events"] && _p.sourceEndpoint && _p.sourceEndpoint.connectorPointerEvents)\n
                _p["pointer-events"] = _p.sourceEndpoint.connectorPointerEvents;\n
\t\t\t\t\t\t\t\t\t\n
\t\t\t// if there\'s a target specified (which of course there should be), and there is no\n
\t\t\t// target endpoint specified, and \'newConnection\' was not set to true, then we check to\n
\t\t\t// see if a prior call to makeTarget has provided us with the specs for the target endpoint, and\n
\t\t\t// we use those if so.  additionally, if the makeTarget call was specified with \'uniqueEndpoint\' set\n
\t\t\t// to true, then if that target endpoint has already been created, we re-use it.\n
\n
\t\t\tvar tid, tep, existingUniqueEndpoint, newEndpoint;\n
\n
\t\t\t// TODO: this code can be refactored to be a little dry.\n
\t\t\tif (_p.target && !_p.target.endpoint && !_p.targetEndpoint && !_p.newConnection) {\n
\t\t\t\ttid = _getId(_p.target);\n
\t\t\t\ttep = this.targetEndpointDefinitions[tid];\n
\n
\t\t\t\tif (tep) {\n
\t\t\t\t\t\n
\t\t\t\t\t// if target not enabled, return.\n
\t\t\t\t\tif (!tep.enabled) return;\n
\n
\t\t\t\t\t// TODO this is dubious. i think it is there so that the endpoint can subsequently\n
\t\t\t\t\t// be dragged (ie it kicks off the draggable registration). but it is dubious.\n
\t\t\t\t\ttep.isTarget = true;\n
\n
\t\t\t\t\t// check for max connections??\t\t\t\t\t\t\n
\t\t\t\t\tnewEndpoint = tep.endpoint != null && tep.endpoint._jsPlumb ? tep.endpoint : _currentInstance.addEndpoint(_p.target, tep.def);\n
\t\t\t\t\tif (tep.uniqueEndpoint) tep.endpoint = newEndpoint;\n
\t\t\t\t\t _p.targetEndpoint = newEndpoint;\n
\t\t\t\t\t // TODO test options to makeTarget to see if we should do this?\n
\t\t\t\t\t newEndpoint._doNotDeleteOnDetach = false; // reset.\n
\t\t\t\t\t newEndpoint._deleteOnDetach = true;\t\t\t\t\t \n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t// same thing, but for source.\n
\t\t\tif (_p.source && !_p.source.endpoint && !_p.sourceEndpoint && !_p.newConnection) {\n
\t\t\t\ttid = _getId(_p.source);\n
\t\t\t\ttep = this.sourceEndpointDefinitions[tid];\n
\n
\t\t\t\tif (tep) {\n
\t\t\t\t\t// if source not enabled, return.\t\t\t\t\t\n
\t\t\t\t\tif (!tep.enabled) return;\n
\n
\t\t\t\t\t// TODO this is dubious. i think it is there so that the endpoint can subsequently\n
\t\t\t\t\t// be dragged (ie it kicks off the draggable registration). but it is dubious.\n
\t\t\t\t\t//tep.isSource = true;\n
\t\t\t\t\n
\t\t\t\t\tnewEndpoint = tep.endpoint != null && tep.endpoint._jsPlumb ? tep.endpoint : _currentInstance.addEndpoint(_p.source, tep.def);\n
\t\t\t\t\tif (tep.uniqueEndpoint) tep.endpoint = newEndpoint;\n
\t\t\t\t\t _p.sourceEndpoint = newEndpoint;\n
\t\t\t\t\t // TODO test options to makeSource to see if we should do this?\n
\t\t\t\t\t newEndpoint._doNotDeleteOnDetach = false; // reset.\n
\t\t\t\t\t newEndpoint._deleteOnDetach = true;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\treturn _p;\n
\t\t}.bind(_currentInstance),\n
\t\t\n
\t\t_newConnection = function(params) {\n
\t\t\tvar connectionFunc = _currentInstance.Defaults.ConnectionType || _currentInstance.getDefaultConnectionType(),\n
\t\t\t    endpointFunc = _currentInstance.Defaults.EndpointType || jsPlumb.Endpoint;\t\t\t    \t\t\t\n
\t\t\t\n
\t\t\tparams._jsPlumb = _currentInstance;\n
            params.newConnection = _newConnection;\n
            params.newEndpoint = _newEndpoint;\n
            params.endpointsByUUID = endpointsByUUID;             \n
            params.endpointsByElement = endpointsByElement;  \n
            params.finaliseConnection = _finaliseConnection;\n
\t\t\tvar con = new connectionFunc(params);\n
\t\t\tcon.id = "con_" + _idstamp();\n
\t\t\t_eventFireProxy("click", "click", con);\n
\t\t\t_eventFireProxy("dblclick", "dblclick", con);\n
            _eventFireProxy("contextmenu", "contextmenu", con);\n
\n
            // if the connection is draggable, then maybe we need to tell the target endpoint to init the\n
            // dragging code. it won\'t run again if it already configured to be draggable.\n
            if (con.isDetachable()) {\n
            \tcon.endpoints[0].initDraggable();\n
            \tcon.endpoints[1].initDraggable();\n
            }\n
\n
\t\t\treturn con;\n
\t\t},\n
\t\t\n
\t\t//\n
\t\t// adds the connection to the backing model, fires an event if necessary and then redraws\n
\t\t//\n
\t\t_finaliseConnection = function(jpc, params, originalEvent, doInformAnchorManager) {\n
            params = params || {};\n
\t\t\t// add to list of connections (by scope).\n
            if (!jpc.suspendedEndpoint)\n
\t\t\t    connections.push(jpc);\n
\t\t\t\n
            // always inform the anchor manager\n
            // except that if jpc has a suspended endpoint it\'s not true to say the\n
            // connection is new; it has just (possibly) moved. the question is whether\n
            // to make that call here or in the anchor manager.  i think perhaps here.\n
            if (jpc.suspendedEndpoint == null || doInformAnchorManager)\n
            \t_currentInstance.anchorManager.newConnection(jpc);\n
\n
\t\t\t// force a paint\n
\t\t\t_draw(jpc.source);\n
\t\t\t\n
\t\t\t// fire an event\n
\t\t\tif (!params.doNotFireConnectionEvent && params.fireEvent !== false) {\n
\t\t\t\n
\t\t\t\tvar eventArgs = {\n
\t\t\t\t\tconnection:jpc,\n
\t\t\t\t\tsource : jpc.source, target : jpc.target,\n
\t\t\t\t\tsourceId : jpc.sourceId, targetId : jpc.targetId,\n
\t\t\t\t\tsourceEndpoint : jpc.endpoints[0], targetEndpoint : jpc.endpoints[1]\n
\t\t\t\t};\n
\t\t\t\n
\t\t\t\t_currentInstance.fire("connection", eventArgs, originalEvent);\n
\t\t\t}\n
\t\t},\n
\t\t\n
\t\t_eventFireProxy = function(event, proxyEvent, obj) {\n
\t\t\tobj.bind(event, function(originalObject, originalEvent) {\n
\t\t\t\t_currentInstance.fire(proxyEvent, obj, originalEvent);\n
\t\t\t});\n
\t\t},\n
\t\t\n
\t\t\n
\t\t/*\n
\t\t\tfactory method to prepare a new endpoint.  this should always be used instead of creating Endpoints\n
\t\t\tmanually, since this method attaches event listeners and an id.\n
\t\t*/\n
\t\t_newEndpoint = function(params) {\n
\t\t\t\tvar endpointFunc = _currentInstance.Defaults.EndpointType || jsPlumb.Endpoint;\n
\t\t\t\tvar _p = jsPlumb.extend({}, params);\n
\t\t\t\t_p._jsPlumb = _currentInstance;\n
                _p.newConnection = _newConnection;\n
                _p.newEndpoint = _newEndpoint;                \n
                _p.endpointsByUUID = endpointsByUUID;             \n
                _p.endpointsByElement = endpointsByElement;  \n
                _p.finaliseConnection = _finaliseConnection;\n
                _p.fireDetachEvent = fireDetachEvent;\n
                _p.fireMoveEvent = fireMoveEvent;\n
                _p.floatingConnections = floatingConnections;\n
                _p.elementId = _getId(_p.source);                \n
\t\t\t\tvar ep = new endpointFunc(_p);\t\t\t\n
\t\t\t\tep.id = "ep_" + _idstamp();\n
\t\t\t\t_eventFireProxy("click", "endpointClick", ep);\n
\t\t\t\t_eventFireProxy("dblclick", "endpointDblClick", ep);\n
\t\t\t\t_eventFireProxy("contextmenu", "contextmenu", ep);\n
\t\t\t\tif (!jsPlumbAdapter.headless)\n
\t\t\t\t\t_currentInstance.dragManager.endpointAdded(_p.source);\n
\t\t\treturn ep;\n
\t\t},\n
\t\t\n
\t\t/*\n
\t\t * performs the given function operation on all the connections found\n
\t\t * for the given element id; this means we find all the endpoints for\n
\t\t * the given element, and then for each endpoint find the connectors\n
\t\t * connected to it. then we pass each connection in to the given\n
\t\t * function.\t\t \n
\t\t */\n
\t\t_operation = function(elId, func, endpointFunc) {\n
\t\t\tvar endpoints = endpointsByElement[elId];\n
\t\t\tif (endpoints && endpoints.length) {\n
\t\t\t\tfor ( var i = 0, ii = endpoints.length; i < ii; i++) {\n
\t\t\t\t\tfor ( var j = 0, jj = endpoints[i].connections.length; j < jj; j++) {\n
\t\t\t\t\t\tvar retVal = func(endpoints[i].connections[j]);\n
\t\t\t\t\t\t// if the function passed in returns true, we exit.\n
\t\t\t\t\t\t// most functions return false.\n
\t\t\t\t\t\tif (retVal) return;\n
\t\t\t\t\t}\n
\t\t\t\t\tif (endpointFunc) endpointFunc(endpoints[i]);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t},\t\n
\t\t\n
\t\t_setDraggable = function(element, draggable) {\n
\t\t\treturn _elementProxy(element, function(el, id) {\n
\t\t\t\tdraggableStates[id] = draggable;\n
\t\t\t\tif (this.isDragSupported(el)) {\n
\t\t\t\t\tthis.setElementDraggable(el, draggable);\n
\t\t\t\t}\n
\t\t\t});\n
\t\t},\n
\t\t/*\n
\t\t * private method to do the business of hiding/showing.\n
\t\t * \n
\t\t * @param el\n
\t\t *            either Id of the element in question or a library specific\n
\t\t *            object for the element.\n
\t\t * @param state\n
\t\t *            String specifying a value for the css \'display\' property\n
\t\t *            (\'block\' or \'none\').\n
\t\t */\n
\t\t_setVisible = function(el, state, alsoChangeEndpoints) {\n
\t\t\tstate = state === "block";\n
\t\t\tvar endpointFunc = null;\n
\t\t\tif (alsoChangeEndpoints) {\n
\t\t\t\tif (state) endpointFunc = function(ep) {\n
\t\t\t\t\tep.setVisible(true, true, true);\n
\t\t\t\t};\n
\t\t\t\telse endpointFunc = function(ep) {\n
\t\t\t\t\tep.setVisible(false, true, true);\n
\t\t\t\t};\n
\t\t\t}\n
\t\t\tvar info = _info(el);\n
\t\t\t_operation(info.id, function(jpc) {\n
\t\t\t\tif (state && alsoChangeEndpoints) {\t\t\n
\t\t\t\t\t// this test is necessary because this functionality is new, and i wanted to maintain backwards compatibility.\n
\t\t\t\t\t// this block will only set a connection to be visible if the other endpoint in the connection is also visible.\n
\t\t\t\t\tvar oidx = jpc.sourceId === info.id ? 1 : 0;\n
\t\t\t\t\tif (jpc.endpoints[oidx].isVisible()) jpc.setVisible(true);\n
\t\t\t\t}\n
\t\t\t\telse  // the default behaviour for show, and what always happens for hide, is to just set the visibility without getting clever.\n
\t\t\t\t\tjpc.setVisible(state);\n
\t\t\t}, endpointFunc);\n
\t\t},\n
\t\t/*\n
\t\t * toggles the draggable state of the given element(s).\n
\t\t * el is either an id, or an element object, or a list of ids/element objects.\n
\t\t */\n
\t\t_toggleDraggable = function(el) {\n
\t\t\treturn _elementProxy(el, function(el, elId) {\n
\t\t\t\tvar state = draggableStates[elId] == null ? false : draggableStates[elId];\n
\t\t\t\tstate = !state;\n
\t\t\t\tdraggableStates[elId] = state;\n
\t\t\t\tthis.setDraggable(el, state);\n
\t\t\t\treturn state;\n
\t\t\t});\n
\t\t},\n
\t\t/**\n
\t\t * private method to do the business of toggling hiding/showing.\n
\t\t */\n
\t\t_toggleVisible = function(elId, changeEndpoints) {\n
\t\t\tvar endpointFunc = null;\n
\t\t\tif (changeEndpoints) {\n
\t\t\t\tendpointFunc = function(ep) {\n
\t\t\t\t\tvar state = ep.isVisible();\n
\t\t\t\t\tep.setVisible(!state);\n
\t\t\t\t};\n
\t\t\t}\n
\t\t\t_operation(elId, function(jpc) {\n
\t\t\t\tvar state = jpc.isVisible();\n
\t\t\t\tjpc.setVisible(!state);\t\t\t\t\n
\t\t\t}, endpointFunc);\n
\t\t\t// todo this should call _elementProxy, and pass in the\n
\t\t\t// _operation(elId, f) call as a function. cos _toggleDraggable does\n
\t\t\t// that.\n
\t\t},\n
\t\t/**\n
\t\t * updates the offset and size for a given element, and stores the\n
\t\t * values. if \'offset\' is not null we use that (it would have been\n
\t\t * passed in from a drag call) because it\'s faster; but if it is null,\n
\t\t * or if \'recalc\' is true in order to force a recalculation, we get the current values.\n
\t\t */\n
\t\t_updateOffset = this.updateOffset = function(params) {\n
\t\t\tvar timestamp = params.timestamp, recalc = params.recalc, offset = params.offset, elId = params.elId, s;\n
\t\t\tif (_suspendDrawing && !timestamp) timestamp = _suspendedAt;\n
\t\t\tif (!recalc) {\n
\t\t\t\tif (timestamp && timestamp === offsetTimestamps[elId]) {\t\t\t\n
\t\t\t\t\treturn {o:params.offset || offsets[elId], s:sizes[elId]};\n
\t\t\t\t}\n
\t\t\t}\t\t\t\n
\t\t\tif (recalc || !offset) { // if forced repaint or no offset available, we recalculate.\n
\t\t\t\t// get the current size and offset, and store them\n
\t\t\t\ts = document.getElementById(elId);\n
\t\t\t\tif (s != null) {\t\t\t\t\t\t\n
\t\t\t\t\tsizes[elId] = _currentInstance.getSize(s);\n
\t\t\t\t\toffsets[elId] = _getOffset(s, _currentInstance);\n
\t\t\t\t\toffsetTimestamps[elId] = timestamp;\n
\t\t\t\t}\n
\t\t\t} else {\n
\t\t\t\toffsets[elId] = offset;\n
                if (sizes[elId] == null) {\n
                    s = document.getElementById(elId);\n
                    if (s != null) sizes[elId] = _currentInstance.getSize(s);\n
                }\n
                offsetTimestamps[elId] = timestamp;\n
            }\n
\t\t\t\n
\t\t\tif(offsets[elId] && !offsets[elId].right) {\n
\t\t\t\toffsets[elId].right = offsets[elId].left + sizes[elId][0];\n
\t\t\t\toffsets[elId].bottom = offsets[elId].top + sizes[elId][1];\t\n
\t\t\t\toffsets[elId].width = sizes[elId][0];\n
\t\t\t\toffsets[elId].height = sizes[elId][1];\t\n
\t\t\t\toffsets[elId].centerx = offsets[elId].left + (offsets[elId].width / 2);\n
\t\t\t\toffsets[elId].centery = offsets[elId].top + (offsets[elId].height / 2);\t\t\t\t\n
\t\t\t}\n
\t\t\treturn {o:offsets[elId], s:sizes[elId]};\n
\t\t},\n
\n
\t\t// TODO comparison performance\n
\t\t_getCachedData = function(elId) {\n
\t\t\tvar o = offsets[elId];\n
\t\t\tif (!o) \n
                return _updateOffset({elId:elId});\n
\t\t\telse\n
                return {o:o, s:sizes[elId]};\n
\t\t},\n
\n
\t\t/**\n
\t\t * gets an id for the given element, creating and setting one if\n
\t\t * necessary.  the id is of the form\n
\t\t *\n
\t\t *\tjsPlumb_<instance index>_<index in instance>\n
\t\t *\n
\t\t * where "index in instance" is a monotonically increasing integer that starts at 0,\n
\t\t * for each instance.  this method is used not only to assign ids to elements that do not\n
\t\t * have them but also to connections and endpoints.\n
\t\t */\n
\t\t_getId = function(element, uuid, doNotCreateIfNotFound) {\n
\t\t\tif (jsPlumbUtil.isString(element)) return element;\t\t\t\n
\t\t\tif (element == null) return null;\t\t\t\n
\t\t\tvar id = _currentInstance.getAttribute(element, "id");\n
\t\t\tif (!id || id === "undefined") {\n
\t\t\t\t// check if fixed uuid parameter is given\n
\t\t\t\tif (arguments.length == 2 && arguments[1] !== undefined)\n
\t\t\t\t\tid = uuid;\n
\t\t\t\telse if (arguments.length == 1 || (arguments.length == 3 && !arguments[2]))\n
\t\t\t\t\tid = "jsPlumb_" + _instanceIndex + "_" + _idstamp();\n
\t\t\t\t\n
                if (!doNotCreateIfNotFound) _currentInstance.setAttribute(element, "id", id);\n
\t\t\t}\n
\t\t\treturn id;\n
\t\t};\n
\n
\t\tthis.setConnectionBeingDragged = function(v) {\n
\t\t\tconnectionBeingDragged = v;\n
\t\t};\n
\t\tthis.isConnectionBeingDragged = function() {\n
\t\t\treturn connectionBeingDragged;\n
\t\t};\n
    \n
\t\tthis.connectorClass = "_jsPlumb_connector";            \t\t\n
\t\tthis.hoverClass = "_jsPlumb_hover";            \t\t\n
\t\tthis.endpointClass = "_jsPlumb_endpoint";\t\t\n
\t\tthis.endpointConnectedClass = "_jsPlumb_endpoint_connected";\t\t\n
\t\tthis.endpointFullClass = "_jsPlumb_endpoint_full";\t\t\n
\t\tthis.endpointDropAllowedClass = "_jsPlumb_endpoint_drop_allowed";\t\t\n
\t\tthis.endpointDropForbiddenClass = "_jsPlumb_endpoint_drop_forbidden";\t\t\n
\t\tthis.overlayClass = "_jsPlumb_overlay";\t\t\t\t\n
\t\tthis.draggingClass = "_jsPlumb_dragging";\t\t\n
\t\tthis.elementDraggingClass = "_jsPlumb_element_dragging";\t\t\t\n
\t\tthis.sourceElementDraggingClass = "_jsPlumb_source_element_dragging";\n
\t\tthis.targetElementDraggingClass = "_jsPlumb_target_element_dragging";\n
\t\tthis.endpointAnchorClassPrefix = "_jsPlumb_endpoint_anchor";\n
\t\tthis.hoverSourceClass = "_jsPlumb_source_hover";\t\n
\t\tthis.hoverTargetClass = "_jsPlumb_target_hover";\n
\t\tthis.dragSelectClass = "_jsPlumb_drag_select";\n
\n
\t\tthis.Anchors = {};\t\t\n
\t\tthis.Connectors = {  "svg":{}, "vml":{} };\t\t\t\t\n
\t\tthis.Endpoints = { "svg":{}, "vml":{} };\n
\t\tthis.Overlays = { "svg":{}, "vml":{}};\t\t\n
\t\tthis.ConnectorRenderers = {};\t\t\t\t\n
\t\tthis.SVG = "svg";\n
\t\tthis.VML = "vml";\t\t\t\t\n
\n
// --------------------------- jsPLumbInstance public API ---------------------------------------------------------\n
\t\t\t\t\t\n
\t\t\n
\t\tthis.addEndpoint = function(el, params, referenceParams) {\n
\t\t\treferenceParams = referenceParams || {};\n
\t\t\tvar p = jsPlumb.extend({}, referenceParams);\n
\t\t\tjsPlumb.extend(p, params);\n
\t\t\tp.endpoint = p.endpoint || _currentInstance.Defaults.Endpoint;\n
\t\t\tp.paintStyle = p.paintStyle || _currentInstance.Defaults.EndpointStyle;\n
            // YUI wrapper\n
\t\t\tel = _convertYUICollection(el);\t\t\t\t\t\t\t\n
\n
\t\t\tvar results = [], \n
\t\t\t\tinputs = (_ju.isArray(el) || (el.length != null && !_ju.isString(el))) ? el : [ el ];\n
\t\t\t\t\t\t\n
\t\t\tfor (var i = 0, j = inputs.length; i < j; i++) {\n
\t\t\t\tvar _el = _currentInstance.getDOMElement(inputs[i]), id = _getId(_el);\n
\t\t\t\tp.source = _el;\n
\n
\t\t\t\t_ensureContainer(p.source);\n
                _updateOffset({ elId : id, timestamp:_suspendedAt });\n
\t\t\t\tvar e = _newEndpoint(p);\n
\t\t\t\tif (p.parentAnchor) e.parentAnchor = p.parentAnchor;\n
\t\t\t\t_ju.addToList(endpointsByElement, id, e);\n
\t\t\t\tvar myOffset = offsets[id], \n
\t\t\t\t\tmyWH = sizes[id],\n
\t\t\t\t\tanchorLoc = e.anchor.compute( { xy : [ myOffset.left, myOffset.top ], wh : myWH, element : e, timestamp:_suspendedAt }),\n
\t\t\t\t\tendpointPaintParams = { anchorLoc : anchorLoc, timestamp:_suspendedAt };\n
\t\t\t\t\n
\t\t\t\tif (_suspendDrawing) endpointPaintParams.recalc = false;\n
\t\t\t\tif (!_suspendDrawing) e.paint(endpointPaintParams);\n
\t\t\t\t\n
\t\t\t\tresults.push(e);\n
\t\t\t\te._doNotDeleteOnDetach = true; // mark this as being added via addEndpoint.\t\t\t\t\n
\t\t\t}\n
\t\t\t\n
\t\t\treturn results.length == 1 ? results[0] : results;\n
\t\t};\n
\t\t\n
\t\t\n
\t\tthis.addEndpoints = function(el, endpoints, referenceParams) {\n
\t\t\tvar results = [];\n
\t\t\tfor ( var i = 0, j = endpoints.length; i < j; i++) {\n
\t\t\t\tvar e = _currentInstance.addEndpoint(el, endpoints[i], referenceParams);\n
\t\t\t\tif (_ju.isArray(e))\n
\t\t\t\t\tArray.prototype.push.apply(results, e);\n
\t\t\t\telse results.push(e);\n
\t\t\t}\n
\t\t\treturn results;\n
\t\t};\n
\t\t\n
\t\tthis.animate = function(el, properties, options) {\n
\t\t\toptions = options || {};\n
\t\t\tvar ele = this.getElementObject(el), \n
\t\t\t\tdel = this.getDOMElement(el),\n
\t\t\t\tid = _getId(del),\n
\t\t\t\tstepFunction = jsPlumb.animEvents.step,\n
\t\t\t\tcompleteFunction = jsPlumb.animEvents.complete;\n
\n
\t\t\toptions[stepFunction] = _ju.wrap(options[stepFunction], function() {\n
\t\t\t\t_currentInstance.repaint(id);\n
\t\t\t});\n
\n
\t\t\t// onComplete repaints, just to make sure everything looks good at the end of the animation.\n
\t\t\toptions[completeFunction] = _ju.wrap(options[completeFunction], function() {\n
\t\t\t\t_currentInstance.repaint(id);\n
\t\t\t});\n
\n
\t\t\t_currentInstance.doAnimate(ele, properties, options);\n
\t\t};\n
\t\t\n
\t\t/**\n
\t\t* checks for a listener for the given condition, executing it if found, passing in the given value.\n
\t\t* condition listeners would have been attached using "bind" (which is, you could argue, now overloaded, since\n
\t\t* firing click events etc is a bit different to what this does).  i thought about adding a "bindCondition"\n
\t\t* or something, but decided against it, for the sake of simplicity. jsPlumb will never fire one of these\n
\t\t* condition events anyway.\n
\t\t*/\n
\t\tthis.checkCondition = function(conditionName, value) {\n
\t\t\tvar l = _currentInstance.getListener(conditionName),\n
\t\t\t\tr = true;\n
\t\t\t\t\n
\t\t\tif (l && l.length > 0) {\n
\t\t\t\ttry {\n
\t\t\t\t\tfor (var i = 0, j = l.length; i < j; i++) {\n
\t\t\t\t\t\tr = r && l[i](value); \n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\tcatch (e) { \n
\t\t\t\t\t_ju.log(_currentInstance, "cannot check condition [" + conditionName + "]" + e); \n
\t\t\t\t}\n
\t\t\t}\n
\t\t\treturn r;\n
\t\t};\n
\t\t\n
\t\t/**\n
\t\t * checks a condition asynchronously: fires the event handler and passes the handler\n
\t\t * a \'proceed\' function and a \'stop\' function. The handler MUST execute one or other\n
\t\t * of these once it has made up its mind.\n
\t\t *\n
\t\t * Note that although this reads the listener list for the given condition, it\n
\t\t * does not loop through and hit each listener, because that, with asynchronous\n
\t\t * callbacks, would be messy. so it uses only the first listener registered.\n
\t\t */ \n
\t\tthis.checkASyncCondition = function(conditionName, value, proceed, stop) {\n
\t\t\tvar l = _currentInstance.getListener(conditionName);\n
\t\t\t\t\n
\t\t\tif (l && l.length > 0) {\n
\t\t\t\ttry {\n
\t\t\t\t\tl[0](value, proceed, stop); \t\t\t\t\t\n
\t\t\t\t}\n
\t\t\t\tcatch (e) { \n
\t\t\t\t\t_ju.log(_currentInstance, "cannot asynchronously check condition [" + conditionName + "]" + e); \n
\t\t\t\t}\n
\t\t\t}\t\n
\t\t};\n
\n
\t\t\n
\t\tthis.connect = function(params, referenceParams) {\n
\t\t\t// prepare a final set of parameters to create connection with\n
\t\t\tvar _p = _prepareConnectionParams(params, referenceParams), jpc;\n
\t\t\t// TODO probably a nicer return value if the connection was not made.  _prepareConnectionParams\n
\t\t\t// will return null (and log something) if either endpoint was full.  what would be nicer is to \n
\t\t\t// create a dedicated \'error\' object.\n
\t\t\tif (_p) {\n
\t\t\t\t_ensureContainer(_p.source);\n
\t\t\t\t// create the connection.  it is not yet registered \n
\t\t\t\tjpc = _newConnection(_p);\n
\t\t\t\t// now add it the model, fire an event, and redraw\n
\t\t\t\t_finaliseConnection(jpc, _p);\t\t\t\t\t\t\t\t\t\t\n
\t\t\t}\n
\t\t\treturn jpc;\n
\t\t};\t\t\n
\t\t\n
\t\tvar stTypes = [\n
\t\t\t{ el:"source", elId:"sourceId", epDefs:"sourceEndpointDefinitions" },\n
\t\t\t{ el:"target", elId:"targetId", epDefs:"targetEndpointDefinitions" }\n
\t\t];\n
\t\t\n
\t\tvar _set = function(c, el, idx, doNotRepaint) {\n
\t\t\tvar ep, _st = stTypes[idx], cId = c[_st.elId], cEl = c[_st.el], sid, sep,\n
\t\t\t\toldEndpoint = c.endpoints[idx];\n
\t\t\t\n
\t\t\tvar evtParams = {\n
\t\t\t\tindex:idx,\n
\t\t\t\toriginalSourceId:idx === 0 ? cId : c.sourceId,\n
\t\t\t\tnewSourceId:c.sourceId,\n
\t\t\t\toriginalTargetId:idx == 1 ? cId : c.targetId,\n
\t\t\t\tnewTargetId:c.targetId,\n
\t\t\t\tconnection:c\n
\t\t\t};\n
\n
\t\t\tif (el.constructor == jsPlumb.Endpoint) { // TODO here match the current endpoint class; users can change it {\n
\t\t\t\tep = el;\n
\t\t\t\tep.addConnection(c);\n
\t\t\t}\n
\t\t\telse {\n
\t\t\t\tsid = _getId(el);\n
\t\t\t\tsep = this[_st.epDefs][sid];\n
\n
\t\t\t\tif (sid === c[_st.elId]) \n
\t\t\t\t\tep = null;  // dont change source/target if the element is already the one given.\n
\t\t\t\telse if (sep) {\n
\t\t\t\t\tif (!sep.enabled) return;\n
\t\t\t\t\tep = sep.endpoint != null && sep.endpoint._jsPlumb ? sep.endpoint : this.addEndpoint(el, sep.def);\n
\t\t\t\t\tif (sep.uniqueEndpoint) sep.endpoint = ep;\n
\t\t\t\t\tep._doNotDeleteOnDetach = false;\n
\t\t\t\t\tep._deleteOnDetach = true;\n
\t\t\t\t\tep.addConnection(c);\n
\t\t\t\t}\n
\t\t\t\telse {\n
\t\t\t\t\tep = c.makeEndpoint(idx === 0, el, sid);\n
\t\t\t\t\tep._doNotDeleteOnDetach = false;\n
\t\t\t\t\tep._deleteOnDetach = true;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\tif (ep != null) {\n
\t\t\t\toldEndpoint.detachFromConnection(c);\n
\t\t\t\tc.endpoints[idx] = ep;\n
\t\t\t\tc[_st.el] = ep.element;\n
\t\t\t\tc[_st.elId] = ep.elementId;\t\t\t\n
\t\t\t\tevtParams[idx === 0 ? "newSourceId" : "newTargetId"] = ep.elementId;\n
\n
\t\t\t\tfireMoveEvent(evtParams);\n
\t\t\t\t\n
\t\t\t\tif (!doNotRepaint)\n
\t\t\t\t\tc.repaint();\n
\t\t\t}\n
\n
\t\t\treturn evtParams;\n
\t\t\t\n
\t\t}.bind(this);\n
\n
\t\tthis.setSource = function(connection, el, doNotRepaint) { \n
\t\t\tvar p = _set(connection, el, 0, doNotRepaint); \n
\t\t\tthis.anchorManager.sourceChanged(p.originalSourceId, p.newSourceId, connection);\n
\t\t};\n
\t\tthis.setTarget = function(connection, el, doNotRepaint) { \n
\t\t\tvar p = _set(connection, el, 1, doNotRepaint); \n
\t\t\tthis.anchorManager.updateOtherEndpoint(p.originalSourceId, p.originalTargetId, p.newTargetId, connection);\n
\t\t};\n
\t\t\n
\t\tthis.deleteEndpoint = function(object, doNotRepaintAfterwards) {\n
\t\t\tvar _is = _currentInstance.setSuspendDrawing(true);\n
\t\t\tvar endpoint = (typeof object == "string") ? endpointsByUUID[object] : object;\n
\t\t\tif (endpoint) {\t\t\n
\t\t\t\t_currentInstance.deleteObject({\n
\t\t\t\t\tendpoint:endpoint\n
\t\t\t\t});\n
\t\t\t}\n
\t\t\tif(!_is) _currentInstance.setSuspendDrawing(false, doNotRepaintAfterwards);\n
\t\t\treturn _currentInstance;\n
\t\t};\t\t\n
\t\t\n
\t\tthis.deleteEveryEndpoint = function() {\n
\t\t\tvar _is = _currentInstance.setSuspendDrawing(true);\n
\t\t\tfor ( var id in endpointsByElement) {\n
\t\t\t\tvar endpoints = endpointsByElement[id];\n
\t\t\t\tif (endpoints && endpoints.length) {\n
\t\t\t\t\tfor ( var i = 0, j = endpoints.length; i < j; i++) {\n
\t\t\t\t\t\t_currentInstance.deleteEndpoint(endpoints[i], true);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\t\t\t\n
\t\t\tendpointsByElement = {};\t\t\t\n
\t\t\tendpointsByUUID = {};\n
\t\t\t_currentInstance.anchorManager.reset();\n
\t\t\t_currentInstance.dragManager.reset();\t\t\t\t\t\t\t\n
\t\t\tif(!_is) _currentInstance.setSuspendDrawing(false);\n
\t\t\treturn _currentInstance;\n
\t\t};\n
\n
\t\tvar fireDetachEvent = function(jpc, doFireEvent, originalEvent) {\n
            // may have been given a connection, or in special cases, an object\n
            var connType =  _currentInstance.Defaults.ConnectionType || _currentInstance.getDefaultConnectionType(),\n
                argIsConnection = jpc.constructor == connType,\n
                params = argIsConnection ? {\n
                    connection:jpc,\n
\t\t\t\t    source : jpc.source, target : jpc.target,\n
\t\t\t\t    sourceId : jpc.sourceId, targetId : jpc.targetId,\n
\t\t\t\t    sourceEndpoint : jpc.endpoints[0], targetEndpoint : jpc.endpoints[1]\n
                } : jpc;\n
\n
\t\t\tif (doFireEvent)\n
\t\t\t\t_currentInstance.fire("connectionDetached", params, originalEvent);\n
\t\t\t\n
            _currentInstance.anchorManager.connectionDetached(params);\n
\t\t};\t\n
\n
\t\tvar fireMoveEvent = function(params, evt) {\n
\t\t\t_currentInstance.fire("connectionMoved", params, evt);\n
\t\t};\n
\n
\t\tthis.unregisterEndpoint = function(endpoint) {\n
\t\t\t//if (endpoint._jsPlumb == null) return;\n
\t\t\tif (endpoint._jsPlumb.uuid) endpointsByUUID[endpoint._jsPlumb.uuid] = null;\t\t\t\t\n
\t\t\t_currentInstance.anchorManager.deleteEndpoint(endpoint);\t\t\t\n
\t\t\t// TODO at least replace this with a removeWithFunction call.\t\t\t\n
\t\t\tfor (var e in endpointsByElement) {\n
\t\t\t\tvar endpoints = endpointsByElement[e];\n
\t\t\t\tif (endpoints) {\n
\t\t\t\t\tvar newEndpoints = [];\n
\t\t\t\t\tfor (var i = 0, j = endpoints.length; i < j; i++)\n
\t\t\t\t\t\tif (endpoints[i] != endpoint) newEndpoints.push(endpoints[i]);\n
\t\t\t\t\t\n
\t\t\t\t\tendpointsByElement[e] = newEndpoints;\n
\t\t\t\t}\n
\t\t\t\tif(endpointsByElement[e].length <1){\n
\t\t\t\t\tdelete endpointsByElement[e];\n
\t\t\t\t}\n
\t\t\t}\n
\t\t};\n
\t\t\t\t\n
\t\tthis.detach = function() {\n
\n
            if (arguments.length === 0) return;\n
            var connType =  _currentInstance.Defaults.ConnectionType || _currentInstance.getDefaultConnectionType(),\n
                firstArgIsConnection = arguments[0].constructor == connType,\n
                params = arguments.length == 2 ? firstArgIsConnection ? (arguments[1] || {}) : arguments[0] : arguments[0],\n
                fireEvent = (params.fireEvent !== false),\n
                forceDetach = params.forceDetach,\n
                conn = firstArgIsConnection ? arguments[0] : params.connection;\n
                                                    \n
\t\t\t\tif (conn) {             \n
                    if (forceDetach || jsPlumbUtil.functionChain(true, false, [\n
                            [ conn.endpoints[0], "isDetachAllowed", [ conn ] ],    \n
                            [ conn.endpoints[1], "isDetachAllowed", [ conn ] ],\n
                            [ conn, "isDetachAllowed", [ conn ] ],\n
                            [ _currentInstance, "checkCondition", [ "beforeDetach", conn ] ] ])) {\n
                        \n
                        conn.endpoints[0].detach(conn, false, true, fireEvent); \n
                    }\n
                }\n
                else {\n
\t\t\t\t\tvar _p = jsPlumb.extend( {}, params); // a backwards compatibility hack: source should be thought of as \'params\' in this case.\n
\t\t\t\t\t// test for endpoint uuids to detach\n
\t\t\t\t\tif (_p.uuids) {\n
\t\t\t\t\t\t_getEndpoint(_p.uuids[0]).detachFrom(_getEndpoint(_p.uuids[1]), fireEvent);\n
\t\t\t\t\t} else if (_p.sourceEndpoint && _p.targetEndpoint) {\n
\t\t\t\t\t\t_p.sourceEndpoint.detachFrom(_p.targetEndpoint);\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tvar sourceId = _getId(_currentInstance.getDOMElement(_p.source)),\n
\t\t\t\t\t\t    targetId = _getId(_currentInstance.getDOMElement(_p.target));\n
\t\t\t\t\t\t_operation(sourceId, function(jpc) {\n
\t\t\t\t\t\t    if ((jpc.sourceId == sourceId && jpc.targetId == targetId) || (jpc.targetId == sourceId && jpc.sourceId == targetId)) {\n
\t\t\t\t\t\t\t    if (_currentInstance.checkCondition("beforeDetach", jpc)) {\n
                                    jpc.endpoints[0].detach(jpc, false, true, fireEvent);\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t});\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t};\n
\n
\t\tthis.detachAllConnections = function(el, params) {\n
            params = params || {};\n
            el = _currentInstance.getDOMElement(el);\n
\t\t\tvar id = _getId(el),\n
                endpoints = endpointsByElement[id];\n
\t\t\tif (endpoints && endpoints.length) {\n
\t\t\t\tfor ( var i = 0, j = endpoints.length; i < j; i++) {\n
\t\t\t\t\tendpoints[i].detachAll(params.fireEvent !== false);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\treturn _currentInstance;\n
\t\t};\n
\n
\t\tthis.detachEveryConnection = function(params) {\n
            params = params || {};\n
            _currentInstance.doWhileSuspended(function() {\n
\t\t\t\tfor ( var id in endpointsByElement) {\n
\t\t\t\t\tvar endpoints = endpointsByElement[id];\n
\t\t\t\t\tif (endpoints && endpoints.length) {\n
\t\t\t\t\t\tfor ( var i = 0, j = endpoints.length; i < j; i++) {\n
\t\t\t\t\t\t\tendpoints[i].detachAll(params.fireEvent !== false);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\tconnections.splice(0);\n
\t\t\t});\n
\t\t\treturn _currentInstance;\n
\t\t};\n
\n
\t\t/// not public.  but of course its exposed. how to change this.\n
\t\tthis.deleteObject = function(params) {\n
\t\t\tvar result = {\n
\t\t\t\t\tendpoints : {}, \n
\t\t\t\t\tconnections : {},\n
\t\t\t\t\tendpointCount:0,\n
\t\t\t\t\tconnectionCount:0\n
\t\t\t\t},\n
\t\t\t\tfireEvent = params.fireEvent !== false,\n
\t\t\t\tdeleteAttachedObjects = params.deleteAttachedObjects !== false;\n
\n
\t\t\tvar unravelConnection = function(connection) {\n
\t\t\t\tif(connection != null && resul

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAM=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="3" aka="AAAAAAAAAAM=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

t.connections[connection.id] == null) {\n
\t\t\t\t\tif (connection._jsPlumb != null) connection.setHover(false);\n
\t\t\t\t\tresult.connections[connection.id] = connection;\n
\t\t\t\t\tresult.connectionCount++;\n
\t\t\t\t\tif (deleteAttachedObjects) {\n
\t\t\t\t\t\tfor (var j = 0; j < connection.endpoints.length; j++) {\n
\t\t\t\t\t\t\tif (connection.endpoints[j]._deleteOnDetach)\n
\t\t\t\t\t\t\t\tunravelEndpoint(connection.endpoints[j]);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\t\t\t\t\t\n
\t\t\t\t}\n
\t\t\t};\n
\t\t\tvar unravelEndpoint = function(endpoint) {\n
\t\t\t\tif(endpoint != null && result.endpoints[endpoint.id] == null) {\n
\t\t\t\t\tif (endpoint._jsPlumb != null) endpoint.setHover(false);\n
\t\t\t\t\tresult.endpoints[endpoint.id] = endpoint;\n
\t\t\t\t\tresult.endpointCount++;\n
\n
\t\t\t\t\tif (deleteAttachedObjects) {\n
\t\t\t\t\t\tfor (var i = 0; i < endpoint.connections.length; i++) {\n
\t\t\t\t\t\t\tvar c = endpoint.connections[i];\n
\t\t\t\t\t\t\tunravelConnection(c);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tif (params.connection) \n
\t\t\t\tunravelConnection(params.connection);\n
\t\t\telse unravelEndpoint(params.endpoint);\n
\n
\t\t\t// loop through connections\n
\t\t\tfor (var i in result.connections) {\n
\t\t\t\tvar c = result.connections[i];\n
\t\t\t\tif (c._jsPlumb) {\n
\t\t\t\t\tjsPlumbUtil.removeWithFunction(connections, function(_c) {\n
\t\t\t\t\t\treturn c.id == _c.id;\n
\t\t\t\t\t});\n
\t\t\t\t\tfireDetachEvent(c, fireEvent, params.originalEvent);\n
\t\t\t\t\t\n
\t\t\t\t\tc.endpoints[0].detachFromConnection(c);\n
\t\t\t\t\tc.endpoints[1].detachFromConnection(c);\n
\t\t\t\t\t// sp was ere\n
\t\t\t\t\tc.cleanup();\n
\t\t\t\t\tc.destroy();\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t// loop through endpoints\n
\t\t\tfor (var j in result.endpoints) {\n
\t\t\t\tvar e = result.endpoints[j];\t\n
\t\t\t\tif (e._jsPlumb) {\n
\t\t\t\t\t_currentInstance.unregisterEndpoint(e);\n
\t\t\t\t\t// FIRE some endpoint deleted event?\n
\t\t\t\t\te.cleanup();\n
\t\t\t\t\te.destroy();\n
\t\t\t\t}\n
\t\t\t}\t\n
\n
\t\t\treturn result;\n
\t\t};\n
 \n
\t\tthis.draggable = function(el, options) {\n
\t\t\tvar i,j,ele;\n
\t\t\t// allows for array or jquery/mootools selector\n
\t\t\tif (typeof el == \'object\' && el.length) {\n
\t\t\t\tfor (i = 0, j = el.length; i < j; i++) {\n
\t\t\t\t\tele = _currentInstance.getDOMElement(el[i]);\n
\t\t\t\t\tif (ele) _initDraggableIfNecessary(ele, true, options);\n
\t\t\t\t}\n
\t\t\t} \n
\t\t\t// allows for YUI selector\n
\t\t\telse if (el._nodes) { \t// TODO this is YUI specific; really the logic should be forced\n
\t\t\t\t// into the library adapters (for jquery and mootools aswell)\n
\t\t\t\tfor (i = 0, j = el._nodes.length; i < j; i++) {\n
\t\t\t\t\tele = _currentInstance.getDOMElement(el._nodes[i]);\n
\t\t\t\t\tif (ele) _initDraggableIfNecessary(ele, true, options);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\telse {\t\t\t\t\n
\t\t\t\tele = _currentInstance.getDOMElement(el);\n
\t\t\t\tif (ele) _initDraggableIfNecessary(ele, true, options);\n
\t\t\t}\n
\t\t\treturn _currentInstance;\n
\t\t};\n
\n
\t\t// helpers for select/selectEndpoints\n
\t\tvar _setOperation = function(list, func, args, selector) {\n
\t\t\t\tfor (var i = 0, j = list.length; i < j; i++) {\n
\t\t\t\t\tlist[i][func].apply(list[i], args);\n
\t\t\t\t}\t\n
\t\t\t\treturn selector(list);\n
\t\t\t},\n
\t\t\t_getOperation = function(list, func, args) {\n
\t\t\t\tvar out = [];\n
\t\t\t\tfor (var i = 0, j = list.length; i < j; i++) {\n
\t\t\t\t\tout.push([ list[i][func].apply(list[i], args), list[i] ]);\n
\t\t\t\t}\t\n
\t\t\t\treturn out;\n
\t\t\t},\n
\t\t\tsetter = function(list, func, selector) {\n
\t\t\t\treturn function() {\n
\t\t\t\t\treturn _setOperation(list, func, arguments, selector);\n
\t\t\t\t};\n
\t\t\t},\n
\t\t\tgetter = function(list, func) {\n
\t\t\t\treturn function() {\n
\t\t\t\t\treturn _getOperation(list, func, arguments);\n
\t\t\t\t};\t\n
\t\t\t},\n
\t\t\tprepareList = function(input, doNotGetIds) {\n
\t\t\t\tvar r = [];\n
\t\t\t\tif (input) {\n
\t\t\t\t\tif (typeof input == \'string\') {\n
\t\t\t\t\t\tif (input === "*") return input;\n
\t\t\t\t\t\tr.push(input);\n
\t\t\t\t\t}\n
\t\t\t\t\telse {\n
\t\t\t\t\t\tif (doNotGetIds) r = input;\n
\t\t\t\t\t\telse { \n
\t\t\t\t\t\t\tif (input.length) {\n
\t\t\t\t\t\t\t\t//input = _currentInstance.getElementObject(input);\n
\t\t\t\t\t\t\t\tfor (var i = 0, j = input.length; i < j; i++) \n
\t\t\t\t\t\t\t\t\tr.push(_info(input[i]).id);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\telse\n
\t\t\t\t\t\t\t\tr.push(_info(input).id);\n
\t\t\t\t\t\t}\t\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\treturn r;\n
\t\t\t},\n
\t\t\tfilterList = function(list, value, missingIsFalse) {\n
\t\t\t\tif (list === "*") return true;\n
\t\t\t\treturn list.length > 0 ? jsPlumbUtil.indexOf(list, value) != -1 : !missingIsFalse;\n
\t\t\t};\n
\n
\t\t// get some connections, specifying source/target/scope\n
\t\tthis.getConnections = function(options, flat) {\n
\t\t\tif (!options) {\n
\t\t\t\toptions = {};\n
\t\t\t} else if (options.constructor == String) {\n
\t\t\t\toptions = { "scope": options };\n
\t\t\t}\n
\t\t\tvar scope = options.scope || _currentInstance.getDefaultScope(),\n
\t\t\t\tscopes = prepareList(scope, true),\n
\t\t\t\tsources = prepareList(options.source),\n
\t\t\t\ttargets = prepareList(options.target),\t\t\t\n
\t\t\t\tresults = (!flat && scopes.length > 1) ? {} : [],\n
\t\t\t\t_addOne = function(scope, obj) {\n
\t\t\t\t\tif (!flat && scopes.length > 1) {\n
\t\t\t\t\t\tvar ss = results[scope];\n
\t\t\t\t\t\tif (ss == null) {\n
\t\t\t\t\t\t\tss = results[scope] = [];\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tss.push(obj);\n
\t\t\t\t\t} else results.push(obj);\n
\t\t\t\t};\n
\t\t\t\n
\t\t\tfor ( var j = 0, jj = connections.length; j < jj; j++) {\n
\t\t\t\tvar c = connections[j];\n
\t\t\t\tif (filterList(scopes, c.scope) && filterList(sources, c.sourceId) && filterList(targets, c.targetId))\n
\t\t\t\t\t_addOne(c.scope, c);\n
\t\t\t}\n
\t\t\t\n
\t\t\treturn results;\n
\t\t};\n
\t\t\n
\t\tvar _curryEach = function(list, executor) {\n
\t\t\t\treturn function(f) {\n
\t\t\t\t\tfor (var i = 0, ii = list.length; i < ii; i++) {\n
\t\t\t\t\t\tf(list[i]);\n
\t\t\t\t\t}\n
\t\t\t\t\treturn executor(list);\n
\t\t\t\t};\t\t\n
\t\t\t},\n
\t\t\t_curryGet = function(list) {\n
\t\t\t\treturn function(idx) {\n
\t\t\t\t\treturn list[idx];\n
\t\t\t\t};\n
\t\t\t};\n
\t\t\t\n
\t\tvar _makeCommonSelectHandler = function(list, executor) {\n
            var out = {\n
                    length:list.length,\n
\t\t\t\t    each:_curryEach(list, executor),\n
\t\t\t\t    get:_curryGet(list)\n
                },\n
                setters = ["setHover", "removeAllOverlays", "setLabel", "addClass", "addOverlay", "removeOverlay", \n
                           "removeOverlays", "showOverlay", "hideOverlay", "showOverlays", "hideOverlays", "setPaintStyle",\n
                           "setHoverPaintStyle", "setSuspendEvents", "setParameter", "setParameters", "setVisible", \n
                           "repaint", "addType", "toggleType", "removeType", "removeClass", "setType", "bind", "unbind" ],\n
                \n
                getters = ["getLabel", "getOverlay", "isHover", "getParameter", "getParameters", "getPaintStyle",\n
                           "getHoverPaintStyle", "isVisible", "hasType", "getType", "isSuspendEvents" ],\n
                i, ii;\n
            \n
            for (i = 0, ii = setters.length; i < ii; i++)\n
                out[setters[i]] = setter(list, setters[i], executor);\n
            \n
            for (i = 0, ii = getters.length; i < ii; i++)\n
                out[getters[i]] = getter(list, getters[i]);       \n
            \n
            return out;\n
\t\t};\n
\t\t\n
\t\tvar\t_makeConnectionSelectHandler = function(list) {\n
\t\t\tvar common = _makeCommonSelectHandler(list, _makeConnectionSelectHandler);\n
\t\t\treturn jsPlumb.extend(common, {\n
\t\t\t\t// setters\n
\t\t\t\tsetDetachable:setter(list, "setDetachable", _makeConnectionSelectHandler),\n
\t\t\t\tsetReattach:setter(list, "setReattach", _makeConnectionSelectHandler),\n
\t\t\t\tsetConnector:setter(list, "setConnector", _makeConnectionSelectHandler),\t\t\t\n
\t\t\t\tdetach:function() {\n
\t\t\t\t\tfor (var i = 0, ii = list.length; i < ii; i++)\n
\t\t\t\t\t\t_currentInstance.detach(list[i]);\n
\t\t\t\t},\t\t\t\t\n
\t\t\t\t// getters\n
\t\t\t\tisDetachable:getter(list, "isDetachable"),\n
\t\t\t\tisReattach:getter(list, "isReattach")\n
\t\t\t});\n
\t\t};\n
\t\t\n
\t\tvar\t_makeEndpointSelectHandler = function(list) {\n
\t\t\tvar common = _makeCommonSelectHandler(list, _makeEndpointSelectHandler);\n
\t\t\treturn jsPlumb.extend(common, {\n
\t\t\t\tsetEnabled:setter(list, "setEnabled", _makeEndpointSelectHandler),\t\t\t\t\n
\t\t\t\tsetAnchor:setter(list, "setAnchor", _makeEndpointSelectHandler),\n
\t\t\t\tisEnabled:getter(list, "isEnabled"),\n
\t\t\t\tdetachAll:function() {\n
\t\t\t\t\tfor (var i = 0, ii = list.length; i < ii; i++)\n
\t\t\t\t\t\tlist[i].detachAll();\n
\t\t\t\t},\n
\t\t\t\t"remove":function() {\n
\t\t\t\t\tfor (var i = 0, ii = list.length; i < ii; i++)\n
\t\t\t\t\t\t_currentInstance.deleteObject({endpoint:list[i]});\n
\t\t\t\t}\n
\t\t\t});\n
\t\t};\n
\t\t\t\n
\n
\t\tthis.select = function(params) {\n
\t\t\tparams = params || {};\n
\t\t\tparams.scope = params.scope || "*";\n
\t\t\treturn _makeConnectionSelectHandler(params.connections || _currentInstance.getConnections(params, true));\t\t\t\t\t\t\t\n
\t\t};\t\t\n
\n
\t\tthis.selectEndpoints = function(params) {\n
\t\t\tparams = params || {};\n
\t\t\tparams.scope = params.scope || "*";\n
\t\t\tvar noElementFilters = !params.element && !params.source && !params.target,\t\t\t\n
\t\t\t\telements = noElementFilters ? "*" : prepareList(params.element),\n
\t\t\t\tsources = noElementFilters ? "*" : prepareList(params.source),\n
\t\t\t\ttargets = noElementFilters ? "*" : prepareList(params.target),\n
\t\t\t\tscopes = prepareList(params.scope, true);\n
\t\t\t\n
\t\t\tvar ep = [];\n
\t\t\t\n
\t\t\tfor (var el in endpointsByElement) {\n
\t\t\t\tvar either = filterList(elements, el, true),\n
\t\t\t\t\tsource = filterList(sources, el, true),\n
\t\t\t\t\tsourceMatchExact = sources != "*",\n
\t\t\t\t\ttarget = filterList(targets, el, true),\n
\t\t\t\t\ttargetMatchExact = targets != "*"; \n
\t\t\t\t\t\n
\t\t\t\t// if they requested \'either\' then just match scope. otherwise if they requested \'source\' (not as a wildcard) then we have to match only endpoints that have isSource set to to true, and the same thing with isTarget.  \n
\t\t\t\tif ( either || source  || target ) {\n
\t\t\t\t\tinner:\n
\t\t\t\t\tfor (var i = 0, ii = endpointsByElement[el].length; i < ii; i++) {\n
\t\t\t\t\t\tvar _ep = endpointsByElement[el][i];\n
\t\t\t\t\t\tif (filterList(scopes, _ep.scope, true)) {\n
\t\t\t\t\t\t\n
\t\t\t\t\t\t\tvar noMatchSource = (sourceMatchExact && sources.length > 0 && !_ep.isSource),\n
\t\t\t\t\t\t\t\tnoMatchTarget = (targetMatchExact && targets.length > 0 && !_ep.isTarget);\n
\t\t\t\t\t\t\n
\t\t\t\t\t\t\tif (noMatchSource || noMatchTarget)\t\t\t\t\t\t\t\t  \n
\t\t\t\t\t\t\t\t  continue inner; \n
\t\t\t\t\t\t\t \t\t\t\t\t\t\t\n
\t\t\t\t\t\t\tep.push(_ep);\t\t\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\t\t\t\t\t\n
\t\t\t}\n
\t\t\t\n
\t\t\treturn _makeEndpointSelectHandler(ep);\n
\t\t};\n
\n
\t\t// get all connections managed by the instance of jsplumb.\n
\t\tthis.getAllConnections = function() { return connections; };\n
\t\tthis.getDefaultScope = function() { return DEFAULT_SCOPE; };\n
\t\t// get an endpoint by uuid.\n
\t\tthis.getEndpoint = _getEndpoint;\t\t\t\t\n
\t\t// get endpoints for some element.\n
\t\tthis.getEndpoints = function(el) { return endpointsByElement[_info(el).id]; };\t\t\n
\t\t// gets the default endpoint type. used when subclassing. see wiki.\n
\t\tthis.getDefaultEndpointType = function() { return jsPlumb.Endpoint; };\t\t\n
\t\t// gets the default connection type. used when subclassing.  see wiki.\n
\t\tthis.getDefaultConnectionType = function() { return jsPlumb.Connection; };\n
\t\t/*\n
\t\t * Gets an element\'s id, creating one if necessary. really only exposed\n
\t\t * for the lib-specific functionality to access; would be better to pass\n
\t\t * the current instance into the lib-specific code (even though this is\n
\t\t * a static call. i just don\'t want to expose it to the public API).\n
\t\t */\n
\t\tthis.getId = _getId;\n
\t\tthis.getOffset = function(id) { \n
\t\t\tvar o = offsets[id]; \n
\t\t\treturn _updateOffset({elId:id});\n
\t\t};\n
\t\t\n
\t\tthis.appendElement = _appendElement;\n
\t\t\n
\t\tvar _hoverSuspended = false;\n
\t\tthis.isHoverSuspended = function() { return _hoverSuspended; };\n
\t\tthis.setHoverSuspended = function(s) { _hoverSuspended = s; };\n
\n
\t\tvar _isAvailable = function(m) {\n
\t\t\treturn function() {\n
\t\t\t\treturn jsPlumbAdapter.isRenderModeAvailable(m);\n
\t\t\t};\n
\t\t};\n
\n
\t\tthis.isSVGAvailable = _isAvailable("svg");\n
\t\tthis.isVMLAvailable = _isAvailable("vml");\n
\n
\t\t// set an element\'s connections to be hidden\n
\t\tthis.hide = function(el, changeEndpoints) {\n
\t\t\t_setVisible(el, "none", changeEndpoints);\n
\t\t\treturn _currentInstance;\n
\t\t};\n
\t\t\n
\t\t// exposed for other objects to use to get a unique id.\n
\t\tthis.idstamp = _idstamp;\n
\n
\t\tthis.connectorsInitialized = false;\n
\t\tvar connectorTypes = [], rendererTypes = ["svg", "vml"];\n
\t\tthis.registerConnectorType = function(connector, name) {\n
\t\t\tconnectorTypes.push([connector, name]);\n
\t\t};\n
\t\t\n
\t\t// ensure that, if the current container exists, it is a DOM element and not a selector.\n
\t\t// if it does not exist and `candidate` is supplied, the offset parent of that element will be set as the Container.\n
\t\t// this is used to do a better default behaviour for the case that the user has not set a container:\n
\t\t// addEndpoint, makeSource, makeTarget and connect all call this method with the offsetParent of the \n
\t\t// element in question (for connect it is the source element). So if no container is set, it is inferred\n
\t\t// to be the offsetParent of the first element the user tries to connect.\n
\t\tvar _ensureContainer = function(candidate) {\n
\t\t\tif (!_container && candidate) {\n
\t\t\t\tvar can = _currentInstance.getDOMElement(candidate);\n
\t\t\t\tif (can.offsetParent) _container = can.offsetParent;\n
\t\t\t}\n
\t\t};\n
\n
\t\tvar _getContainerFromDefaults = function() {\n
\t\t\tif (_currentInstance.Defaults.Container)\n
\t\t\t\t_container = _currentInstance.getDOMElement(_currentInstance.Defaults.Container);\n
\t\t};\n
\t\t\n
\t\t/**\n
\t\t * callback from the current library to tell us to prepare ourselves (attach\n
\t\t * mouse listeners etc; can\'t do that until the library has provided a bind method)\t\t \n
\t\t */\n
\t\tthis.init = function() {\n
\t\t\tvar _oneType = function(renderer, name, fn) {\n
\t\t\t\tjsPlumb.Connectors[renderer][name] = function() {\n
\t\t\t\t\tfn.apply(this, arguments);\n
\t\t\t\t\tjsPlumb.ConnectorRenderers[renderer].apply(this, arguments);\t\t\n
\t\t\t\t};\n
\t\t\t\tjsPlumbUtil.extend(jsPlumb.Connectors[renderer][name], [ fn, jsPlumb.ConnectorRenderers[renderer]]);\n
\t\t\t};\n
\n
\t\t\tif (!jsPlumb.connectorsInitialized) {\n
\t\t\t\tfor (var i = 0; i < connectorTypes.length; i++) {\n
\t\t\t\t\tfor (var j = 0; j < rendererTypes.length; j++) {\n
\t\t\t\t\t\t_oneType(rendererTypes[j], connectorTypes[i][1], connectorTypes[i][0]);\t\t\t\t\t\t\t\t\t\t\t\t\n
\t\t\t\t\t}\n
\n
\t\t\t\t}\n
\t\t\t\tjsPlumb.connectorsInitialized = true;\n
\t\t\t}\n
\t\t\t\n
\t\t\tif (!initialized) {                \n
\t\t\t\t_getContainerFromDefaults();\t\n
                _currentInstance.anchorManager = new jsPlumb.AnchorManager({jsPlumbInstance:_currentInstance});                \n
\t\t\t\t_currentInstance.setRenderMode(_currentInstance.Defaults.RenderMode);  // calling the method forces the capability logic to be run.\t\t\t\t\t\t\t\t\t\t\t\t\t\t\n
\t\t\t\tinitialized = true;\n
\t\t\t\t_currentInstance.fire("ready", _currentInstance);\n
\t\t\t}\n
\t\t}.bind(this);\t\t\n
\t\t\n
\t\tthis.log = log;\n
\t\tthis.jsPlumbUIComponent = jsPlumbUIComponent;\t\t\n
\n
\t\t/*\n
\t\t * Creates an anchor with the given params.\n
\t\t * \n
\t\t * \n
\t\t * Returns: The newly created Anchor.\n
\t\t * Throws: an error if a named anchor was not found.\n
\t\t */\n
\t\tthis.makeAnchor = function() {\n
\t\t\tvar pp, _a = function(t, p) {\n
\t\t\t\tif (jsPlumb.Anchors[t]) return new jsPlumb.Anchors[t](p);\n
\t\t\t\tif (!_currentInstance.Defaults.DoNotThrowErrors)\n
\t\t\t\t\tthrow { msg:"jsPlumb: unknown anchor type \'" + t + "\'" };\n
\t\t\t};\n
\t\t\tif (arguments.length === 0) return null;\n
\t\t\tvar specimen = arguments[0], elementId = arguments[1], jsPlumbInstance = arguments[2], newAnchor = null;\t\t\t\n
\t\t\t// if it appears to be an anchor already...\n
\t\t\tif (specimen.compute && specimen.getOrientation) return specimen;  //TODO hazy here about whether it should be added or is already added somehow.\n
\t\t\t// is it the name of an anchor type?\n
\t\t\telse if (typeof specimen == "string") {\n
\t\t\t\tnewAnchor = _a(arguments[0], {elementId:elementId, jsPlumbInstance:_currentInstance});\n
\t\t\t}\n
\t\t\t// is it an array? it will be one of:\n
\t\t\t// \t\tan array of [spec, params] - this defines a single anchor, which may be dynamic, but has parameters.\n
\t\t\t//\t\tan array of arrays - this defines some dynamic anchors\n
\t\t\t//\t\tan array of numbers - this defines a single anchor.\t\t\t\t\n
\t\t\telse if (_ju.isArray(specimen)) {\n
\t\t\t\tif (_ju.isArray(specimen[0]) || _ju.isString(specimen[0])) {\n
\t\t\t\t\t// if [spec, params] format\n
\t\t\t\t\tif (specimen.length == 2 && _ju.isObject(specimen[1])) {\n
\t\t\t\t\t\t// if first arg is a string, its a named anchor with params\n
\t\t\t\t\t\tif (_ju.isString(specimen[0])) {\n
\t\t\t\t\t\t\tpp = jsPlumb.extend({elementId:elementId, jsPlumbInstance:_currentInstance}, specimen[1]);\n
\t\t\t\t\t\t\tnewAnchor = _a(specimen[0], pp);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t// otherwise first arg is array, second is params. we treat as a dynamic anchor, which is fine\n
\t\t\t\t\t\t// even if the first arg has only one entry. you could argue all anchors should be implicitly dynamic in fact.\n
\t\t\t\t\t\telse {\n
\t\t\t\t\t\t\tpp = jsPlumb.extend({elementId:elementId, jsPlumbInstance:_currentInstance, anchors:specimen[0]}, specimen[1]);\n
\t\t\t\t\t\t\tnewAnchor = new jsPlumb.DynamicAnchor(pp);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\telse\n
\t\t\t\t\t\tnewAnchor = new jsPlumb.DynamicAnchor({anchors:specimen, selector:null, elementId:elementId, jsPlumbInstance:jsPlumbInstance});\n
\n
\t\t\t\t}\n
\t\t\t\telse {\n
\t\t\t\t\tvar anchorParams = {\n
\t\t\t\t\t\tx:specimen[0], y:specimen[1],\n
\t\t\t\t\t\torientation : (specimen.length >= 4) ? [ specimen[2], specimen[3] ] : [0,0],\n
\t\t\t\t\t\toffsets : (specimen.length >= 6) ? [ specimen[4], specimen[5] ] : [ 0, 0 ],\n
\t\t\t\t\t\telementId:elementId,\n
                        jsPlumbInstance:jsPlumbInstance,\n
                        cssClass:specimen.length == 7 ? specimen[6] : null\n
\t\t\t\t\t};\t\t\t\t\t\t\n
\t\t\t\t\tnewAnchor = new jsPlumb.Anchor(anchorParams);\n
\t\t\t\t\tnewAnchor.clone = function() { return new jsPlumb.Anchor(anchorParams); };\t\t\t\t\t\t \t\t\t\t\t\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\tif (!newAnchor.id) newAnchor.id = "anchor_" + _idstamp();\n
\t\t\treturn newAnchor;\n
\t\t};\n
\n
\t\t/**\n
\t\t * makes a list of anchors from the given list of types or coords, eg\n
\t\t * ["TopCenter", "RightMiddle", "BottomCenter", [0, 1, -1, -1] ]\n
\t\t */\n
\t\tthis.makeAnchors = function(types, elementId, jsPlumbInstance) {\n
\t\t\tvar r = [];\n
\t\t\tfor ( var i = 0, ii = types.length; i < ii; i++) {\n
\t\t\t\tif (typeof types[i] == "string")\n
\t\t\t\t\tr.push(jsPlumb.Anchors[types[i]]({elementId:elementId, jsPlumbInstance:jsPlumbInstance}));\n
\t\t\t\telse if (_ju.isArray(types[i]))\n
\t\t\t\t\tr.push(_currentInstance.makeAnchor(types[i], elementId, jsPlumbInstance));\n
\t\t\t}\n
\t\t\treturn r;\n
\t\t};\n
\n
\t\t/**\n
\t\t * Makes a dynamic anchor from the given list of anchors (which may be in shorthand notation as strings or dimension arrays, or Anchor\n
\t\t * objects themselves) and the given, optional, anchorSelector function (jsPlumb uses a default if this is not provided; most people will\n
\t\t * not need to provide this - i think). \n
\t\t */\n
\t\tthis.makeDynamicAnchor = function(anchors, anchorSelector) {\n
\t\t\treturn new jsPlumb.DynamicAnchor({anchors:anchors, selector:anchorSelector, elementId:null, jsPlumbInstance:_currentInstance});\n
\t\t};\n
\t\t\n
// --------------------- makeSource/makeTarget ---------------------------------------------- \n
\t\t\n
\t\tthis.targetEndpointDefinitions = {};\n
\t\tvar _setEndpointPaintStylesAndAnchor = function(ep, epIndex, _instance) {\n
\t\t\t\tep.paintStyle = ep.paintStyle ||\n
\t\t\t\t \t\t\t\t_instance.Defaults.EndpointStyles[epIndex] ||\n
\t                            _instance.Defaults.EndpointStyle;\n
\t\t\t\t\t\t\t\t\n
\t\t\t\tep.hoverPaintStyle = ep.hoverPaintStyle ||\n
\t                           _instance.Defaults.EndpointHoverStyles[epIndex] ||\n
\t                           _instance.Defaults.EndpointHoverStyle;                            \n
\n
\t\t\t\tep.anchor = ep.anchor ||\n
\t                      \t_instance.Defaults.Anchors[epIndex] ||\n
\t                      \t_instance.Defaults.Anchor;\n
\t\t\t\t\t\n
\t\t\t\tep.endpoint = ep.endpoint ||\n
\t\t\t\t\t\t\t  _instance.Defaults.Endpoints[epIndex] ||\n
\t\t\t\t\t\t\t  _instance.Defaults.Endpoint;\n
\t\t\t};\n
\t\t\t\n
\t\t\t// TODO put all the source stuff inside one parent, keyed by id.\n
\t\t\tthis.sourceEndpointDefinitions = {};\n
\t\t\t\n
\t\t\tvar selectorFilter = function(evt, _el, selector, _instance, negate) {\n
                var t = evt.target || evt.srcElement, ok = false, \n
                    sel = _instance.getSelector(_el, selector);\n
                for (var j = 0; j < sel.length; j++) {\n
                    if (sel[j] == t) {\n
                        ok = true;\n
                        break;\n
                    }\n
                }\n
                return negate ? !ok : ok;\n
\t        };\n
\n
\t\t// see API docs\n
\t\tthis.makeTarget = function(el, params, referenceParams) {\n
\n
\t\t\t// put jsplumb ref into params without altering the params passed in\n
\t\t\tvar p = jsPlumb.extend({_jsPlumb:this}, referenceParams);\n
\t\t\tjsPlumb.extend(p, params);\n
\n
\t\t\t// calculate appropriate paint styles and anchor from the params given\n
\t\t\t_setEndpointPaintStylesAndAnchor(p, 1, this);\n
\n
\t\t\tvar targetScope = p.scope || _currentInstance.Defaults.Scope,\n
\t\t\t\tdeleteEndpointsOnDetach = !(p.deleteEndpointsOnDetach === false),\n
\t\t\t\tmaxConnections = p.maxConnections || -1,\n
\t\t\t\tonMaxConnections = p.onMaxConnections,\n
\n
\t\t\t\t_doOne = function(el) {\n
\t\t\t\t\t\n
\t\t\t\t\t// get the element\'s id and store the endpoint definition for it.  jsPlumb.connect calls will look for one of these,\n
\t\t\t\t\t// and use the endpoint definition if found.\n
\t\t\t\t\t// decode the info for this element (id and element)\n
\t\t\t\t\tvar elInfo = _info(el), \n
\t\t\t\t\t\telid = elInfo.id,\n
\t\t\t\t\t\tproxyComponent = new jsPlumbUIComponent(p),\n
\t\t\t\t\t\tdropOptions = jsPlumb.extend({}, p.dropOptions || {});\n
\n
\t\t\t\t\t_ensureContainer(elid);\n
\n
\t\t\t\t\t// store the definitions keyed against the element id.\n
\t\t\t\t\t// TODO why not just store inside the element itself?\n
\t\t\t\t\tthis.targetEndpointDefinitions[elid] = {\n
\t\t\t\t\t\tdef:p,\n
\t\t\t\t\t\tuniqueEndpoint:p.uniqueEndpoint,\n
\t\t\t\t\t\tmaxConnections:maxConnections,\n
\t\t\t\t\t\tenabled:true\n
\t\t\t\t\t};\n
\n
\t\t\t\t\tvar _drop = function() {\n
\t\t\t\t\t\tthis.currentlyDragging = false;\n
\t\t\t\t\t\tvar originalEvent = this.getDropEvent(arguments),\n
\t\t\t\t\t\t\ttargetCount = this.select({target:elid}).length,\n
\t\t\t\t\t\t\tdraggable = this.getDOMElement(this.getDragObject(arguments)),\n
\t\t\t\t\t\t\tid = this.getAttribute(draggable, "dragId"),\n
\t\t\t\t\t\t\tscope = this.getAttribute(draggable, "originalScope"),\n
\t\t\t\t\t\t\tjpc = floatingConnections[id],\n
\t\t\t\t\t\t\tidx = jpc.endpoints[0].isFloating() ? 0 : 1,\n
\t\t\t\t\t\t\t// this is not necessarily correct. if the source is being dragged,\n
\t\t\t\t\t\t\t// then the source endpoint is actually the currently suspended endpoint.\n
\t\t\t\t\t\t\tsource = jpc.endpoints[0],\n
\t\t\t\t\t\t\t_endpoint = p.endpoint ? jsPlumb.extend({}, p.endpoint) : {},\n
\t\t\t\t\t\t\tdef = this.targetEndpointDefinitions[elid];\n
\t\t\t\t\t\t\t\n
\t\t\t\t\t\tif (!def.enabled || def.maxConnections > 0 && targetCount >= def.maxConnections){\n
\t\t\t\t\t\t\tif (onMaxConnections) {\n
\t\t\t\t\t\t\t\t// TODO here we still have the id of the floating element, not the\n
\t\t\t\t\t\t\t\t// actual target.\n
\t\t\t\t\t\t\t\tonMaxConnections({\n
\t\t\t\t\t\t\t\t\telement:elInfo.el,\n
\t\t\t\t\t\t\t\t\tconnection:jpc\n
\t\t\t\t\t\t\t\t}, originalEvent);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\treturn false;\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t// unlock the source anchor to allow it to refresh its position if necessary\n
\t\t\t\t\t\tsource.anchor.locked = false;\n
\n
\t\t\t\t\t\t// restore the original scope if necessary (issue 57)\n
\t\t\t\t\t\tif (scope) this.setDragScope(draggable, scope);\t\t\n
\n
\t\t\t\t\t\t// if no suspendedEndpoint and not pending, it is likely there was a drop on two \n
\t\t\t\t\t\t// elements that are on top of each other. abort.\n
\t\t\t\t\t\tif (jpc.suspendedEndpoint == null && !jpc.pending)\n
\t\t\t\t\t\t\treturn false;\n
\t\t\t\t\t\t\n
\t\t\t\t\t\t// check if drop is allowed here.\n
\t\t\t\t\t\t// if the source is being dragged then in fact\n
\t\t\t\t\t\t// the source and target ids to pass into the drop interceptor are\n
\t\t\t\t\t\t// source - elid\n
\t\t\t\t\t\t// target - jpc\'s targetId\n
\t\t\t\t\t\t// \n
\t\t\t\t\t\t// otherwise the ids are\n
\t\t\t\t\t\t// source - jpc.sourceId\n
\t\t\t\t\t\t// target - elid\n
\t\t\t\t\t\t//\n
\t\t\t\t\t\tvar _continue = proxyComponent.isDropAllowed(idx === 0 ? elid : jpc.sourceId, idx === 0 ? jpc.targetId : elid, jpc.scope, jpc, null, idx === 0 ? elInfo.el : jpc.source, idx === 0 ? jpc.target : elInfo.el);\n
\n
\t\t\t\t\t\t// reinstate any suspended endpoint; this just puts the connection back into\n
\t\t\t\t\t\t// a state in which it will report sensible values if someone asks it about\n
\t\t\t\t\t\t// its target.  we\'re going to throw this connection away shortly so it doesnt matter\n
\t\t\t\t\t\t// if we manipulate it a bit.\n
\t\t\t\t\t\tif (jpc.suspendedEndpoint) {\n
\t\t\t\t\t\t\tjpc[idx ? "targetId" : "sourceId"] = jpc.suspendedEndpoint.elementId;\n
\t\t\t\t\t\t\tjpc[idx ? "target" : "source"] = jpc.suspendedEndpoint.element;\n
\t\t\t\t\t\t\tjpc.endpoints[idx] = jpc.suspendedEndpoint;\n
\t\t\t\t\t\t\t\n
\t\t\t\t\t\t\t// TODO this and the normal endpoint drop should\n
\t\t\t\t\t\t\t// be refactored to share more of the common code.\n
\t\t\t\t\t\t\tvar suspendedElement = jpc.suspendedEndpoint.getElement(), suspendedElementId = jpc.suspendedEndpoint.elementId;\n
\t\t\t\t\t\t\tfireMoveEvent({\n
\t\t\t\t\t\t\t\tindex:idx,\n
\t\t\t\t\t\t\t\toriginalSourceId:idx === 0 ? suspendedElementId : jpc.sourceId,\n
\t\t\t\t\t\t\t\tnewSourceId:idx === 0 ? elid : jpc.sourceId,\n
\t\t\t\t\t\t\t\toriginalTargetId:idx == 1 ? suspendedElementId : jpc.targetId,\n
\t\t\t\t\t\t\t\tnewTargetId:idx == 1 ? elid : jpc.targetId,\n
\t\t\t\t\t\t\t\tconnection:jpc\n
\t\t\t\t\t\t\t}, originalEvent);\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tif (_continue) {\n
\t\t\t\t\t\t\t// make a new Endpoint for the target, or get it from the cache if uniqueEndpoint\n
                            // is set.\n
\t\t\t\t\t\t\tvar _el = this.getElementObject(elInfo.el),\n
\t\t\t\t\t\t\t\tnewEndpoint = def.endpoint;\n
\n
                            // if no cached endpoint, or there was one but it has been cleaned up\n
                            // (ie. detached), then create a new one.\n
                            if (newEndpoint == null || newEndpoint._jsPlumb == null)\n
                                newEndpoint = this.addEndpoint(_el, p);\n
\n
\t\t\t\t\t\t\tif (p.uniqueEndpoint) def.endpoint = newEndpoint;  // may of course just store what it just pulled out. that\'s ok.\n
\t\t\t\t\t\t\t// TODO test options to makeTarget to see if we should do this?\n
\t\t\t\t\t\t\tnewEndpoint._doNotDeleteOnDetach = false; // reset.\n
\t\t\t\t\t\t\tnewEndpoint._deleteOnDetach = true;\n
\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\n
\t\t\t\t\t\t\t// if the anchor has a \'positionFinder\' set, then delegate to that function to find\n
\t\t\t\t\t\t\t// out where to locate the anchor.\n
\t\t\t\t\t\t\tif (newEndpoint.anchor.positionFinder != null) {\n
\t\t\t\t\t\t\t\tvar dropPosition = this.getUIPosition(arguments, this.getZoom()),\n
\t\t\t\t\t\t\t\telPosition = _getOffset(_el, this),\n
\t\t\t\t\t\t\t\telSize = this.getSize(_el),\n
\t\t\t\t\t\t\t\tap = newEndpoint.anchor.positionFinder(dropPosition, elPosition, elSize, newEndpoint.anchor.constructorParams);\n
\t\t\t\t\t\t\t\tnewEndpoint.anchor.x = ap[0];\n
\t\t\t\t\t\t\t\tnewEndpoint.anchor.y = ap[1];\n
\t\t\t\t\t\t\t\t// now figure an orientation for it..kind of hard to know what to do actually. probably the best thing i can do is to\n
\t\t\t\t\t\t\t\t// support specifying an orientation in the anchor\'s spec. if one is not supplied then i will make the orientation \n
\t\t\t\t\t\t\t\t// be what will cause the most natural link to the source: it will be pointing at the source, but it needs to be\n
\t\t\t\t\t\t\t\t// specified in one axis only, and so how to make that choice? i think i will use whichever axis is the one in which\n
\t\t\t\t\t\t\t\t// the target is furthest away from the source.\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\n
\t\t\t\t\t\t\t// change the target endpoint and target element information. really this should be \n
\t\t\t\t\t\t\t// done on a method on connection\n
\t\t\t\t\t\t\tjpc[idx ? "target" : "source"] = newEndpoint.element;\n
\t\t\t\t\t\t\tjpc[idx ? "targetId" : "sourceId"] = newEndpoint.elementId;\n
\t\t\t\t\t\t\tjpc.endpoints[idx].detachFromConnection(jpc);\n
\t\t\t\t\t\t\tif (jpc.endpoints[idx]._deleteOnDetach)\n
\t\t\t\t\t\t\t\tjpc.endpoints[idx].deleteAfterDragStop = true; // tell this endpoint to delet itself after drag stop.\n
\t\t\t\t\t\t\t// set new endpoint, and configure the settings for endpoints to delete on detach\n
\t\t\t\t\t\t\tnewEndpoint.addConnection(jpc);\n
\t\t\t\t\t\t\tjpc.endpoints[idx] = newEndpoint;\n
\t\t\t\t\t\t\tjpc.deleteEndpointsOnDetach = deleteEndpointsOnDetach;\n
\n
\t\t\t\t\t\t\t// inform the anchor manager to update its target endpoint for this connection.\n
\t\t\t\t\t\t\t// TODO refactor to make this a single method.\n
\t\t\t\t\t\t\tif (idx == 1)\n
\t\t\t\t\t\t\t\tthis.anchorManager.updateOtherEndpoint(jpc.sourceId, jpc.suspendedElementId, jpc.targetId, jpc);\n
\t\t\t\t\t\t\telse\n
\t\t\t\t\t\t\t\tthis.anchorManager.sourceChanged(jpc.suspendedEndpoint.elementId, jpc.sourceId, jpc);\n
\n
\t\t\t\t\t\t\t_finaliseConnection(jpc, null, originalEvent);\n
\t\t\t\t\t\t\tjpc.pending = false;\n
\n
\t\t\t\t\t\t}\t\t\t\t\n
\t\t\t\t\t\t// if not allowed to drop...\n
\t\t\t\t\t\telse {\n
\t\t\t\t\t\t\t// TODO this code is identical (pretty much) to what happens when a connection\n
\t\t\t\t\t\t\t// dragged from a normal endpoint is in this situation. refactor.\n
\t\t\t\t\t\t\t// is this an existing connection, and will we reattach?\n
\t\t\t\t\t\t\t// TODO also this assumes the source needs to detach - is that always valid?\n
\t\t\t\t\t\t\tif (jpc.suspendedEndpoint) {\n
\t\t\t\t\t\t\t\tif (jpc.isReattach()) {\n
\t\t\t\t\t\t\t\t\tjpc.setHover(false);\n
\t\t\t\t\t\t\t\t\tjpc.floatingAnchorIndex = null;\n
\t\t\t\t\t\t\t\t\tjpc.suspendedEndpoint.addConnection(jpc);\n
\t\t\t\t\t\t\t\t\tthis.repaint(source.elementId);\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\telse\n
\t\t\t\t\t\t\t\t\tsource.detach(jpc, false, true, true, originalEvent);  // otherwise, detach the connection and tell everyone about it.\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}.bind(this);\n
\t\t\t\t\t\n
\t\t\t\t\t// wrap drop events as needed and initialise droppable\n
\t\t\t\t\tvar dropEvent = jsPlumb.dragEvents.drop;\n
\t\t\t\t\tdropOptions.scope = dropOptions.scope || targetScope;\n
\t\t\t\t\tdropOptions[dropEvent] = _ju.wrap(dropOptions[dropEvent], _drop);\t\t\t\t\n
\t\t\t\t\tthis.initDroppable(this.getElementObject(elInfo.el), dropOptions, true);\n
\t\t\t\t}.bind(this);\n
\t\t\t\n
\t\t\t// YUI collection fix\n
\t\t\tel = _convertYUICollection(el);\t\t\t\n
\t\t\t// make an array if only given one element\n
\t\t\tvar inputs = el.length && el.constructor != String ? el : [ el ];\n
\t\t\t\t\t\t\n
\t\t\t// register each one in the list.\n
\t\t\tfor (var i = 0, ii = inputs.length; i < ii; i++) {\t\t\t\t\t\t\t\n
\t\t\t\t_doOne(inputs[i]);\n
\t\t\t}\n
\n
\t\t\treturn this;\n
\t\t};\n
\n
\t\t// see api docs\n
\t\tthis.unmakeTarget = function(el, doNotClearArrays) {\n
\t\t\tvar info = _info(el);\n
\n
\t\t\tjsPlumb.destroyDroppable(info.el);\n
\t\t\t// TODO this is not an exhaustive unmake of a target, since it does not remove the droppable stuff from\n
\t\t\t// the element.  the effect will be to prevent it from behaving as a target, but it\'s not completely purged.\n
\t\t\tif (!doNotClearArrays) {\n
\t\t\t\tdelete this.targetEndpointDefinitions[info.id];\n
\t\t\t}\n
\n
\t\t\treturn this;\n
\t\t};\t\t\t\t\t\t\n
\n
\t    // see api docs\n
\t\tthis.makeSource = function(el, params, referenceParams) {\n
\t\t\tvar p = jsPlumb.extend({}, referenceParams);\n
\t\t\tjsPlumb.extend(p, params);\n
\t\t\t_setEndpointPaintStylesAndAnchor(p, 0, this);\n
\t\t\tvar maxConnections = p.maxConnections || -1,\n
\t\t\t\tonMaxConnections = p.onMaxConnections,\n
\t\t\t\t_doOne = function(elInfo) {\n
\t\t\t\t\t// get the element\'s id and store the endpoint definition for it.  jsPlumb.connect calls will look for one of these,\n
\t\t\t\t\t// and use the endpoint definition if found.\n
\t\t\t\t\tvar elid = elInfo.id,\n
\t\t\t\t\t\t_el = this.getElementObject(elInfo.el),\n
\t\t\t\t\t\t_del = this.getDOMElement(_el),\n
\t\t\t\t\t\tparentElement = function() {\n
\t\t\t\t\t\t\treturn p.parent == null ? null : p.parent === "parent" ? elInfo.el.parentNode : _currentInstance.getDOMElement(p.parent);\n
\t\t\t\t\t\t},\n
\t\t\t\t\t\tidToRegisterAgainst = p.parent != null ? this.getId(parentElement()) : elid;\n
\n
\t\t\t\t\t_ensureContainer(idToRegisterAgainst);\n
\t\t\t\t\t\n
\t\t\t\t\tthis.sourceEndpointDefinitions[idToRegisterAgainst] = {\n
\t\t\t\t\t\tdef:p,\n
\t\t\t\t\t\tuniqueEndpoint:p.uniqueEndpoint,\n
\t\t\t\t\t\tmaxConnections:maxConnections,\n
\t\t\t\t\t\tenabled:true\n
\t\t\t\t\t};\n
\t\t\t\t\tvar stopEvent = jsPlumb.dragEvents.stop,\n
\t\t\t\t\t\tdragEvent = jsPlumb.dragEvents.drag,\n
\t\t\t\t\t\tdragOptions = jsPlumb.extend({ }, p.dragOptions || {}),\n
\t\t\t\t\t\texistingDrag = dragOptions.drag,\n
\t\t\t\t\t\texistingStop = dragOptions.stop,\n
\t\t\t\t\t\tep = null,\n
\t\t\t\t\t\tendpointAddedButNoDragYet = false;\n
\n
\t\t\t\t\t// set scope if its not set in dragOptions but was passed in in params\n
\t\t\t\t\tdragOptions.scope = dragOptions.scope || p.scope;\n
\n
\t\t\t\t\tdragOptions[dragEvent] = _ju.wrap(dragOptions[dragEvent], function() {\n
\t\t\t\t\t\tif (existingDrag) existingDrag.apply(this, arguments);\n
\t\t\t\t\t\tendpointAddedButNoDragYet = false;\n
\t\t\t\t\t});\n
\t\t\t\t\t\n
\t\t\t\t\tdragOptions[stopEvent] = _ju.wrap(dragOptions[stopEvent], function() { \n
\n
\t\t\t\t\t\tif (existingStop) existingStop.apply(this, arguments);\n
\t                    this.currentlyDragging = false;\n
\t\t\t\t\t\tif (ep._jsPlumb != null) { // if not cleaned up...\n
\t\t\t\t\t\t\t\t\t\n
\t\t\t\t\t\t\t// reset the anchor to the anchor that was initially provided. the one we were using to drag\n
\t\t\t\t\t\t\t// the connection was just a placeholder that was located at the place the user pressed the\n
\t\t\t\t\t\t\t// mouse button to initiate the drag.\n
\t\t\t\t\t\t\tvar anchorDef = p.anchor || this.Defaults.Anchor,\n
\t\t\t\t\t\t\t\toldAnchor = ep.anchor,\n
\t\t\t\t\t\t\t\toldConnection = ep.connections[0],\n
\t\t\t\t\t\t\t\tnewAnchor = this.makeAnchor(anchorDef, elid, this),\n
\t\t\t\t\t\t\t\t_el = ep.element;\n
\n
\t\t\t\t\t\t\t// if the anchor has a \'positionFinder\' set, then delegate to that function to find\n
\t\t\t\t\t\t\t// out where to locate the anchor. issue 117.\n
\t\t\t\t\t\t\tif (newAnchor.positionFinder != null) {\n
\t\t\t\t\t\t\t\tvar elPosition = _getOffset(_el, this),\n
\t\t\t\t\t\t\t\t\telSize = this.getSize(_el),\n
\t\t\t\t\t\t\t\t\tdropPosition = { left:elPosition.left + (oldAnchor.x * elSize[0]), top:elPosition.top + (oldAnchor.y * elSize[1]) },\n
\t\t\t\t\t\t\t\t\tap = newAnchor.positionFinder(dropPosition, elPosition, elSize, newAnchor.constructorParams);\n
\n
\t\t\t\t\t\t\t\tnewAnchor.x = ap[0];\n
\t\t\t\t\t\t\t\tnewAnchor.y = ap[1];\n
\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t\tep.setAnchor(newAnchor, true);\n
\t\t\t\t\t\t\t\n
\t\t\t\t\t\t\tif (p.parent) {\n
\t\t\t\t\t\t\t\tvar parent = parentElement();\n
\t\t\t\t\t\t\t\tif (parent) {\t\n
\t\t\t\t\t\t\t\t\tvar potentialParent = p.container || _container;\n
\t\t\t\t\t\t\t\t\tep.setElement(parent, potentialParent);\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\n
\t\t\t\t\t\t\tep.repaint();\n
\t\t\t\t\t\t\tthis.repaint(ep.elementId);\n
\t\t\t\t\t\t\tthis.repaint(oldConnection.targetId);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}.bind(this));\n
\t\t\t\t\t\n
\t\t\t\t\t// when the user presses the mouse, add an Endpoint, if we are enabled.\n
\t\t\t\t\tvar mouseDownListener = function(e) {\n
\t\t\t\t\t\tvar evt = this.getOriginalEvent(e);\n
\t\t\t\t\t\tvar def = this.sourceEndpointDefinitions[idToRegisterAgainst];\n
\t\t\t\t\t\telid = this.getId(this.getDOMElement(_el)); // elid might have changed since this method was called to configure the element.\n
\t\t\t\t\t\t\n
\t\t\t\t\t\t// if disabled, return.\n
\t\t\t\t\t\tif (!def.enabled) return;\n
\t                    \n
\t                    // if a filter was given, run it, and return if it says no.\n
\t\t\t\t\t\tif (p.filter) {\n
\t\t\t\t\t\t\tvar r = jsPlumbUtil.isString(p.filter) ? selectorFilter(evt, _el, p.filter, this, p.filterExclude) : p.filter(evt, _el);\n
\t\t\t\t\t\t\tif (r === false) return;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t\n
\t\t\t\t\t\t// if maxConnections reached\n
\t\t\t\t\t\tvar sourceCount = this.select({source:idToRegisterAgainst}).length;\n
\t\t\t\t\t\tif (def.maxConnections >= 0 && sourceCount >= def.maxConnections) {\n
\t\t\t\t\t\t\tif (onMaxConnections) {\n
\t\t\t\t\t\t\t\tonMaxConnections({\n
\t\t\t\t\t\t\t\t\telement:_el,\n
\t\t\t\t\t\t\t\t\tmaxConnections:maxConnections\n
\t\t\t\t\t\t\t\t}, e);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\treturn false;\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t// find the position on the element at which the mouse was pressed; this is where the endpoint \n
\t\t\t\t\t\t// will be located.\n
\t\t\t\t\t\tvar elxy = jsPlumbAdapter.getPositionOnElement(evt, _del, _zoom), pelxy = elxy;\n
\t\t\t\t\t\t// for mootools/YUI..this parent stuff should be deprecated.\n
\t\t\t\t\t\tif (p.parent) {\n
\t\t\t\t\t\t\tpelxy = jsPlumbAdapter.getPositionOnElement(evt, parentElement(), _zoom);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\n
\t\t\t\t\t\t// we need to override the anchor in here, and force \'isSource\', but we don\'t want to mess with\n
\t\t\t\t\t\t// the params passed in, because after a connection is established we\'re going to reset the endpoint\n
\t\t\t\t\t\t// to have the anchor we were given.\n
\t\t\t\t\t\tvar tempEndpointParams = {};\n
\t\t\t\t\t\tjsPlumb.extend(tempEndpointParams, p);\n
\t\t\t\t\t\ttempEndpointParams.isSource = true;\n
\t\t\t\t\t\ttempEndpointParams.anchor = [ elxy[0], elxy[1] , 0,0];\n
\t\t\t\t\t\ttempEndpointParams.parentAnchor = [ pelxy[0], pelxy[1], 0, 0 ];\n
\t\t\t\t\t\ttempEndpointParams.dragOptions = dragOptions;\n
\t\t\t\t\t\tep = this.addEndpoint(elid, tempEndpointParams);\n
\t\t\t\t\t\tendpointAddedButNoDragYet = true;\n
\t\t\t\t\t\tep.endpointWillMoveTo = p.parent ? parentElement() : null;\n
\t\t\t\t\t\t// TODO test options to makeSource to see if we should do this?\n
\t\t\t\t\t\tep._doNotDeleteOnDetach = false; // reset.\n
\t\t\t\t\t\tep._deleteOnDetach = true;\n
\n
\t                    var _delTempEndpoint = function() {\n
\t\t\t\t\t\t\t// this mouseup event is fired only if no dragging occurred, by jquery and yui, but for mootools\n
\t\t\t\t\t\t\t// it is fired even if dragging has occurred, in which case we would blow away a perfectly\n
\t\t\t\t\t\t\t// legitimate endpoint, were it not for this check.  the flag is set after adding an\n
\t\t\t\t\t\t\t// endpoint and cleared in a drag listener we set in the dragOptions above.\n
\t\t\t\t\t\t\tif(endpointAddedButNoDragYet) {\n
\t\t\t\t\t\t\t\t endpointAddedButNoDragYet = false;\n
\t\t\t\t\t\t\t\t_currentInstance.deleteEndpoint(ep);\n
\t                        }\n
\t\t\t\t\t\t};\n
\n
\t\t\t\t\t\t_currentInstance.registerListener(ep.canvas, "mouseup", _delTempEndpoint);\n
\t                    _currentInstance.registerListener(_el, "mouseup", _delTempEndpoint);\n
\t\t\t\t\t\t\n
\t\t\t\t\t\t// and then trigger its mousedown event, which will kick off a drag, which will start dragging\n
\t\t\t\t\t\t// a new connection from this endpoint.\n
\t\t\t\t\t\t_currentInstance.trigger(ep.canvas, "mousedown", e);\n
\n
\t\t\t\t\t\tjsPlumbUtil.consume(e);\n
\t\t\t\t\t\t\n
\t\t\t\t\t}.bind(this);\n
\t               \n
\t                // register this on jsPlumb so that it can be cleared by a reset.\n
\t                this.registerListener(_el, "mousedown", mouseDownListener);\n
\t                this.sourceEndpointDefinitions[idToRegisterAgainst].trigger = mouseDownListener;\n
\n
\t                // lastly, if a filter was provided, set it as a dragFilter on the element,\n
\t                // to prevent the element drag function from kicking in when we want to\n
\t                // drag a new connection\n
\t                if (p.filter && jsPlumbUtil.isString(p.filter)) {\n
\t                \t_currentInstance.setDragFilter(_el, p.filter);\n
\t                }\n
\t\t\t\t}.bind(this);\n
\t\t\t\n
\t\t\tel = _convertYUICollection(el);\n
\t\t\t\n
\t\t\tvar inputs = el.length && el.constructor != String ? el : [ el ];\n
\t\t\tfor (var i = 0, ii = inputs.length; i < ii; i++) {\n
\t\t\t\t_doOne(_info(inputs[i]));\n
\t\t\t}\n
\n
\t\t\treturn this;\n
\t\t};\n
\t\n
\t\t// see api docs\t\t\n
\t\tthis.unmakeSource = function(el, doNotClearArrays) {\n
\t\t\tvar info = _info(el),\n
\t\t\t\tmouseDownListener = this.sourceEndpointDefinitions[info.id].trigger;\n
\t\t\t\n
\t\t\tif (mouseDownListener) \n
\t\t\t\t_currentInstance.unregisterListener(info.el, "mousedown", mouseDownListener);\n
\n
\t\t\tif (!doNotClearArrays) {\n
\t\t\t\tdelete this.sourceEndpointDefinitions[info.id];\n
\t\t\t}\n
\n
\t\t\treturn this;\n
\t\t};\n
\n
\t\t// see api docs\n
\t\tthis.unmakeEverySource = function() {\n
\t\t\tfor (var i in this.sourceEndpointDefinitions)\n
\t\t\t\t_currentInstance.unmakeSource(i, true);\n
\n
\t\t\tthis.sourceEndpointDefinitions = {};\n
\t\t\treturn this;\n
\t\t};\n
\t\t\n
\t\t// see api docs\n
\t\tthis.unmakeEveryTarget = function() {\n
\t\t\tfor (var i in this.targetEndpointDefinitions)\n
\t\t\t\t_currentInstance.unmakeTarget(i, true);\n
\t\t\t\n
\t\t\tthis.targetEndpointDefinitions = {};\n
\t\t\treturn this;\n
\t\t};\n
\n
\t\t// does the work of setting a source enabled or disabled.\n
\t\tvar _setEnabled = function(type, el, state, toggle) {\n
\t\t\tvar a = type == "source" ? this.sourceEndpointDefinitions : this.targetEndpointDefinitions;\n
\t\t\tel = _convertYUICollection(el);\n
\n
\t\t\tif (_ju.isString(el)) a[el].enabled = toggle ? !a[el].enabled : state;\n
\t\t\telse if (el.length) {\t\t\t\t\n
\t\t\t\tfor (var i = 0, ii = el.length; i < ii; i++) {\n
\t\t\t\t\tvar info = _info(el[i]);\n
\t\t\t\t\tif (a[info.id])\n
\t\t\t\t\t\ta[info.id].enabled = toggle ? !a[info.id].enabled : state;\n
\t\t\t\t}\n
\t\t\t}\t\n
\t\t\t// otherwise a DOM element\n
\t\t\telse {\n
\t\t\t\tvar id = _info(el).id;\n
\t\t\t\ta[id].enabled = toggle ? !a[id].enabled : state;\n
\t\t\t}\n
\t\t\treturn this;\n
\t\t}.bind(this);\n
\t\t\n
\t\tvar _first = function(el, fn) {\n
\t\t\tel = _convertYUICollection(el);\n
\t\t\tif (_ju.isString(el) || !el.length) \n
\t\t\t\treturn fn.apply(this, [ el ]);\n
\t\t\telse if (el.length) \n
\t\t\t\treturn fn.apply(this, [ el[0] ]);\n
\t\t\t\t\n
\t\t}.bind(this);\n
\n
\t\tthis.toggleSourceEnabled = function(el) {\n
\t\t\t_setEnabled("source", el, null, true);\n
\t\t\treturn this.isSourceEnabled(el);\n
\t\t};\n
\n
\t\tthis.setSourceEnabled = function(el, state) { return _setEnabled("source", el, state); };\n
\t\tthis.isSource = function(el) { \n
\t\t\treturn _first(el, function(_el) { \n
\t\t\t\treturn this.sourceEndpointDefinitions[_info(_el).id] != null; \n
\t\t\t});\n
\t\t};\n
\t\tthis.isSourceEnabled = function(el) { \n
\t\t\treturn _first(el, function(_el) {\n
\t\t\t\tvar sep = this.sourceEndpointDefinitions[_info(_el).id];\n
\t\t\t\treturn sep && sep.enabled === true;\n
\t\t\t});\n
\t\t};\n
\n
\t\tthis.toggleTargetEnabled = function(el) {\n
\t\t\t_setEnabled("target", el, null, true);\n
\t\t\treturn this.isTargetEnabled(el);\n
\t\t};\n
\t\t\n
\t\tthis.isTarget = function(el) { \n
\t\t\treturn _first(el, function(_el) {\n
\t\t\t\treturn this.targetEndpointDefinitions[_info(_el).id] != null; \n
\t\t\t});\n
\t\t};\n
\t\tthis.isTargetEnabled = function(el) { \n
\t\t\treturn _first(el, function(_el) {\n
\t\t\t\tvar tep = this.targetEndpointDefinitions[_info(_el).id];\n
\t\t\t\treturn tep && tep.enabled === true;\n
\t\t\t});\n
\t\t};\n
\t\tthis.setTargetEnabled = function(el, state) { return _setEnabled("target", el, state); };\n
\n
// --------------------- end makeSource/makeTarget ---------------------------------------------- \t\t\t\t\n
\t\t\t\t\n
\t\tthis.ready = function(fn) {\n
\t\t\t_currentInstance.bind("ready", fn);\n
\t\t};\n
\n
\t\t// repaint some element\'s endpoints and connections\n
\t\tthis.repaint = function(el, ui, timestamp) {\n
\t\t\t// support both lists...\n
\t\t\tif (typeof el == \'object\' && el.length)\n
\t\t\t\tfor ( var i = 0, ii = el.length; i < ii; i++) {\n
\t\t\t\t\t_draw(el[i], ui, timestamp);\n
\t\t\t\t}\n
\t\t\telse // ...and single strings.\n
\t\t\t\t_draw(el, ui, timestamp);\n
\t\t\t\t\n
\t\t\treturn _currentInstance;\n
\t\t};\n
\n
\t\t// repaint every endpoint and connection.\n
\t\tthis.repaintEverything = function(clearEdits) {\t\n
\t\t\t// TODO this timestamp causes continuous anchors to not repaint properly.\n
\t\t\t// fix this. do not just take out the timestamp. it runs a lot faster with \n
\t\t\t// the timestamp included.\n
\t\t\t//var timestamp = null;\n
\t\t\tvar timestamp = _timestamp();\n
\t\t\tfor ( var elId in endpointsByElement) {\n
\t\t\t\t_draw(elId, null, timestamp, clearEdits);\n
\t\t\t}\n
\t\t\treturn this;\n
\t\t};\n
\n
\t\tthis.removeAllEndpoints = function(el, recurse) {\n
            var _one = function(_el) {\n
                var info = _info(_el),\n
                    ebe = endpointsByElement[info.id],\n
                    i, ii;\n
\n
                if (ebe) {\n
                    for ( i = 0, ii = ebe.length; i < ii; i++) \n
                        _currentInstance.deleteEndpoint(ebe[i]);\n
                }\n
                delete endpointsByElement[info.id];\n
                \n
                if (recurse) {\n
                    if (info.el && info.el.nodeType != 3 && info.el.nodeType != 8 ) {\n
                        for ( i = 0, ii = info.el.childNodes.length; i < ii; i++) {\n
                            _one(info.el.childNodes[i]);\n
                        }\n
                    }\n
                }\n
                \n
            };\n
            _one(el);\n
\t\t\treturn this;\n
\t\t};\n
                    \n
        /**\n
        * Remove the given element, including cleaning up all endpoints registered for it.\n
        * This is exposed in the public API but also used internally by jsPlumb when removing the\n
        * element associated with a connection drag.\n
        */\n
        this.remove = function(el, doNotRepaint) {\n
        \tvar info = _info(el);        \t\n
            _currentInstance.doWhileSuspended(function() {\n
            \t_currentInstance.removeAllEndpoints(info.id, true);\n
            \t_currentInstance.dragManager.elementRemoved(info.id);\n
            \tdelete floatingConnections[info.id];     \n
            \t_currentInstance.anchorManager.clearFor(info.id);\t\t\t\t\t\t\n
            \t_currentInstance.anchorManager.removeFloatingConnection(info.id);\n
            }, doNotRepaint === false);\n
            if (info.el) _currentInstance.removeElement(info.el);\n
\t\t\treturn _currentInstance;\n
        };\n
\n
\t\tvar _registeredListeners = {},\n
\t\t\t_unbindRegisteredListeners = function() {\n
\t\t\t\tfor (var i in _registeredListeners) {\n
\t\t\t\t\tfor (var j = 0, jj = _registeredListeners[i].length; j < jj; j++) {\n
\t\t\t\t\t\tvar info = _registeredListeners[i][j];\n
\t\t\t\t\t\t_currentInstance.off(info.el, info.event, info.listener);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\t_registeredListeners = {};\n
\t\t\t};\n
\n
        // internal register listener method.  gives us a hook to clean things up\n
        // with if the user calls jsPlumb.reset.\n
        this.registerListener = function(el, type, listener) {\n
            _currentInstance.on(el, type, listener);\n
            jsPlumbUtil.addToList(_registeredListeners, type, {el:el, event:type, listener:listener});\n
        };\n
\n
        this.unregisterListener = function(el, type, listener) {\n
        \t_currentInstance.off(el, type, listener);\n
        \tjsPlumbUtil.removeWithFunction(_registeredListeners, function(rl) {\n
        \t\treturn rl.type == type && rl.listener == listener;\n
        \t});\n
        };\n
\t\t\n
\t\tthis.reset = function() {\n
\t\t\t_currentInstance.deleteEveryEndpoint();\n
\t\t\t_currentInstance.unbind();\n
\t\t\tthis.targetEndpointDefinitions = {};\n
\t\t\tthis.sourceEndpointDefinitions = {};\n
\t\t\tconnections.splice(0);\n
\t\t\t_unbindRegisteredListeners();\n
\t\t\t_currentInstance.anchorManager.reset();\n
\t\t\tif (!jsPlumbAdapter.headless)\n
\t\t\t\t_currentInstance.dragManager.reset();\n
\t\t};\n
\t\t\n
\n
\t\tthis.setDefaultScope = function(scope) {\n
\t\t\tDEFAULT_SCOPE = scope;\n
\t\t\treturn _currentInstance;\n
\t\t};\n
\n
\t\t// sets whether or not some element should be currently draggable.\n
\t\tthis.setDraggable = _setDraggable;\n
\n
\t\t// sets the id of some element, changing whatever we need to to keep track.\n
\t\tthis.setId = function(el, newId, doNotSetAttribute) {\n
\t\t\t// \n
\t\t\tvar id;\n
\n
\t\t\tif (jsPlumbUtil.isString(el)) {\n
\t\t\t\tid = el;\n
\t\t\t}\n
\t\t\telse {\n
\t\t\t\tel = this.getDOMElement(el);\n
\t\t\t\tid = this.getId(el);\n
\t\t\t}\n
\n
\t\t\tvar sConns = this.getConnections({source:id, scope:\'*\'}, true),\n
\t\t\t\ttConns = this.getConnections({target:id, scope:\'*\'}, true);\n
\n
\t\t\tnewId = "" + newId;\n
\n
\t\t\tif (!doNotSetAttribute) {\n
\t\t\t\tel = this.getDOMElement(id);\n
\t\t\t\tthis.setAttribute(el, "id", newId);\n
\t\t\t}\n
\t\t\telse\n
\t\t\t\tel = this.getDOMElement(newId);\n
\n
\t\t\tendpointsByElement[newId] = endpointsByElement[id] || [];\n
\t\t\tfor (var i = 0, ii = endpointsByElement[newId].length; i < ii; i++) {\n
\t\t\t\tendpointsByElement[newId][i].setElementId(newId);\n
\t\t\t\tendpointsByElement[newId][i].setReferenceElement(el);\n
\t\t\t}\n
\t\t\tdelete endpointsByElement[id];\n
\n
\t\t\tthis.anchorManager.changeId(id, newId);\n
\t\t\tif (this.dragManager) this.dragManager.changeId(id, newId);\n
\n
\t\t\tvar _conns = function(list, epIdx, type) {\n
\t\t\t\tfor (var i = 0, ii = list.length; i < ii; i++) {\n
\t\t\t\t\tlist[i].endpoints[epIdx].setElementId(newId);\n
\t\t\t\t\tlist[i].endpoints[epIdx].setReferenceElement(el);\n
\t\t\t\t\tlist[i][type + "Id"] = newId;\n
\t\t\t\t\tlist[i][type] = el;\n
\t\t\t\t}\n
\t\t\t};\n
\t\t\t_conns(sConns, 0, "source");\n
\t\t\t_conns(tConns, 1, "target");\n
\n
\t\t\tthis.repaint(newId);\n
\t\t};\n
\n
\t\tthis.setDebugLog = function(debugLog) {\n
\t\t\tlog = debugLog;\n
\t\t};\n
\n
\t\tthis.setSuspendDrawing = function(val, repaintAfterwards) {\n
\t\t\tvar curVal = _suspendDrawing;\n
\t\t    _suspendDrawing = val;\n
\t\t\t\tif (val) _suspendedAt = new Date().getTime(); else _suspendedAt = null;\n
\t\t    if (repaintAfterwards) this.repaintEverything();\n
\t\t    return curVal;\n
\t\t};\n
\n
        // returns whether or not drawing is currently suspended.\n
\t\tthis.isSuspendDrawing = function() {\n
\t\t\treturn _suspendDrawing;\n
\t\t};\n
\n
        // return timestamp for when drawing was suspended.\n
        this.getSuspendedAt = function() { return _suspendedAt; };\n
\n
        this.doWhileSuspended = function(fn, doNotRepaintAfterwards) {\n
        \tvar _wasSuspended = this.isSuspendDrawing();\n
        \tif (!_wasSuspended)\n
\t\t\t\tthis.setSuspendDrawing(true);\n
\t\t\ttry {\n
\t\t\t\tfn();\n
\t\t\t}\n
\t\t\tcatch (e) {\n
\t\t\t\t_ju.log("Function run while suspended failed", e);\n
\t\t\t}\n
\t\t\tif (!_wasSuspended)\n
\t\t\t\tthis.setSuspendDrawing(false, !doNotRepaintAfterwards);\n
\t\t};\n
\n
\t\tthis.getOffset = function(elId) { return offsets[elId]; };\n
\t\tthis.getCachedData = _getCachedData;\n
\t\tthis.timestamp = _timestamp;\n
\t\tthis.setRenderMode = function(mode) {\n
\t\t\tif (mode !== jsPlumb.SVG && mode !== jsPlumb.VML) throw new TypeError("Render mode [" + mode + "] not supported");\n
\t\t\trenderMode = jsPlumbAdapter.setRenderMode(mode);\n
\t\t\treturn renderMode;\n
\t\t};\n
\t\tthis.getRenderMode = function() { return renderMode; };\n
\t\tthis.show = function(el, changeEndpoints) {\n
\t\t\t_setVisible(el, "block", changeEndpoints);\n
\t\t\treturn _currentInstance;\n
\t\t};\n
\n
\t\t// TODO: update this method to return the current state.\n
\t\tthis.toggleVisible = _toggleVisible;\n
\t\tthis.toggleDraggable = _toggleDraggable;\n
\t\tthis.addListener = this.bind;\n
\n
\t\tif (!jsPlumbAdapter.headless) {\n
\t\t\t_currentInstance.dragManager = jsPlumbAdapter.getDragManager(_currentInstance);\n
\t\t\t_currentInstance.recalculateOffsets = _currentInstance.dragManager.updateOffsets;\n
\t\t}\n
\t};\n
\n
    jsPlumbUtil.extend(jsPlumbInstance, jsPlumbUtil.EventGenerator, {\n
    \tsetAttribute : function(el, a, v) {\n
    \t\tthis.setAttribute(el, a, v);\n
    \t},\n
    \tgetAttribute : function(el, a) {\n
    \t\treturn this.getAttribute(jsPlumb.getDOMElement(el), a);\n
    \t},    \t\n
    \tregisterConnectionType : function(id, type) {\n
    \t\tthis._connectionTypes[id] = jsPlumb.extend({}, type);\n
    \t},    \t\n
    \tregisterConnectionTypes : function(types) {\n
    \t\tfor (var i in types)\n
    \t\t\tthis._connectionTypes[i] = jsPlumb.extend({}, types[i]);\n
    \t},\n
    \tregisterEndpointType : function(id, type) {\n
    \t\tthis._endpointTypes[id] = jsPlumb.extend({}, type);\n
    \t},    \t\n
    \tregisterEndpointTypes : function(types) {\n
    \t\tfor (var i in types)\n
    \t\t\tthis._endpointTypes[i] = jsPlumb.extend({}, types[i]);\n
    \t},    \t\n
    \tgetType : function(id, typeDescriptor) {\n
    \t\treturn typeDescriptor ===  "connection" ? this._connectionTypes[id] : this._endpointTypes[id];\n
    \t},\n
    \tsetIdChanged : function(oldId, newId) {\n
    \t\tthis.setId(oldId, newId, true);\n
    \t},\n
    \t// set parent: change the parent for some node and update all the registrations we need to.\n
    \tsetParent : function(el, newParent) {\n
    \t\tvar _el = this.getElementObject(el),\n
    \t\t\t_dom = this.getDOMElement(_el),\n
    \t\t\t_id = this.getId(_dom),\n
    \t\t\t_pel = this.getElementObject(newParent),\n
    \t\t\t_pdom = this.getDOMElement(_pel),\n
    \t\t\t_pid = this.getId(_pdom);\n
\n
    \t\t_dom.parentNode.removeChild(_dom);\n
    \t\t_pdom.appendChild(_dom);\n
    \t\tthis.dragManager.setParent(_el, _id, _pel, _pid);\n
    \t},\n
\t\t/**\n
\t\t * gets the size for the element, in an array : [ width, height ].\n
\t\t */\n
\t\tgetSize : function(el) {\n
\t\t\treturn [ el.offsetWidth, el.offsetHeight ];\n
\t\t},\n
\t\tgetWidth : function(el) {\n
\t\t\treturn el.offsetWidth;\n
\t\t},\n
\t\tgetHeight : function(el) {\n
\t\t\treturn el.offsetHeight;\n
\t\t},\n
\t\textend : function(o1, o2, names) {\n
\t\t\tvar i;\n
\t\t\tif (names) {\n
\t\t\t\tfor (i = 0; i < names.length; i++)\n
\t\t\t\t\to1[names[i]] = o2[names[i]];\n
\t\t\t}\n
\t\t\telse\n
\t\t\t\tfor (i in o2) o1[i] = o2[i];\n
\t\t\treturn o1;\n
\t\t}\n
    }, jsPlumbAdapter);\n
\n
// --------------------- static instance + AMD registration -------------------------------------------\t\n
\t\n
// create static instance and assign to window if window exists.\t\n
\tvar jsPlumb = new jsPlumbInstance();\n
\t// register on window if defined (lets us run on server)\n
\tif (typeof window != \'undefined\') window.jsPlumb = jsPlumb;\t\n
\t// add \'getInstance\' method to static instance\n
\tjsPlumb.getInstance = function(_defaults) {\n
\t\tvar j = new jsPlumbInstance(_defaults);\n
\t\tj.init();\n
\t\treturn j;\n
\t};\n
// maybe register static instance as an AMD module, and getInstance method too.\n
\tif ( typeof define === "function") {\n
\t\tdefine( "jsplumb", [], function () { return jsPlumb; } );\n
\t\tdefine( "jsplumbinstance", [], function () { return jsPlumb.getInstance(); } );\n
\t}\n
 // CommonJS \n
\tif (typeof exports !== \'undefined\') {\n
      exports.jsPlumb = jsPlumb;\n
  \t}\n
\t\n
\t\n
// --------------------- end static instance + AMD registration -------------------------------------------\t\t\n
\t\n
})();\n
\n
/*\n
 * jsPlumb\n
 * \n
 * Title:jsPlumb 1.6.2\n
 * \n
 * Provides a way to visually connect elements on an HTML page, using SVG or VML.  \n
 * \n
 * This file contains the code for Endpoints.\n
 *\n
 * Copyright (c) 2010 - 2014 Simon Porritt (simon@jsplumbtoolkit.com)\n
 * \n
 * http://jsplumbtoolkit.com\n
 * http://github.com/sporritt/jsplumb\n
 * \n
 * Dual licensed under the MIT and GPL2 licenses.\n
 */\n
;(function() {\n
    \n
    "use strict";\n
        \n
    // create the drag handler for a connection\n
    var _makeConnectionDragHandler = function(placeholder, _jsPlumb) {\n
        var stopped = false;\n
        return {\n
            drag : function() {\n
                if (stopped) {\n
                    stopped = false;\n
                    return true;\n
                }\n
                var _ui = jsPlumb.getUIPosition(arguments, _jsPlumb.getZoom());\n
        \n
                if (placeholder.element) {\n
                    jsPlumbAdapter.setPosition(placeholder.element, _ui);                    \n
                    _jsPlumb.repaint(placeholder.element, _ui);\n
                }\n
            },\n
            stopDrag : function() {\n
                stopped = true;\n
            }\n
        };\n
    };\n
        \n
    // creates a placeholder div for dragging purposes, adds it to the DOM, and pre-computes its offset.    \n
    var _makeDraggablePlaceholder = function(placeholder, _jsPlumb) {\n
        var n = document.createElement("div");\n
        n.style.position = "absolute";\n
        var parent = _jsPlumb.getContainer() || document.body;\n
        parent.appendChild(n);\n
        var id = _jsPlumb.getId(n);\n
        _jsPlumb.updateOffset( { elId : id });\n
        // create and assign an id, and initialize the offset.\n
        placeholder.id = id;\n
        placeholder.element = n;\n
    };\n
    \n
    // create a floating endpoint (for drag connections)\n
    var _makeFloatingEndpoint = function(paintStyle, referenceAnchor, endpoint, referenceCanvas, sourceElement, _jsPlumb, _newEndpoint) {\t\t\t\n
        var floatingAnchor = new jsPlumb.FloatingAnchor( { reference : referenceAnchor, referenceCanvas : referenceCanvas, jsPlumbInstance:_jsPlumb });\n
        //setting the scope here should not be the way to fix that mootools issue.  it should be fixed by not\n
        // adding the floating endpoint as a droppable.  that makes more sense anyway!\n
        return _newEndpoint({ paintStyle : paintStyle, endpoint : endpoint, anchor : floatingAnchor, source : sourceElement, scope:"__floating" });\n
    };\n
\n
    var typeParameters = [ "connectorStyle", "connectorHoverStyle", "connectorOverlays",\n
                "connector", "connectionType", "connectorClass", "connectorHoverClass" ];\n
\n
    // a helper function that tries to find a connection to the given element, and returns it if so. if elementWithPrecedence is null,\n
    // or no connection to it is found, we return the first connection in our list.\n
    var findConnectionToUseForDynamicAnchor = function(ep, elementWithPrecedence) {\n
        var idx = 0;\n
        if (elementWithPrecedence != null) {\n
            for (var i = 0; i < ep.connections.length; i++) {\n
                if (ep.connections[i].sourceId == elementWithPrecedence || ep.connections[i].targetId == elementWithPrecedence) {\n
                    idx = i;\n
                    break;\n
                }\n
            }\n
        }\n
        \n
        return ep.connections[idx];\n
    };\n
\n
    var findConnectionIndex = function(conn, ep) {\n
        return jsPlumbUtil.findWithFunction(ep.connections, function(c) { return c.id == conn.id; });\n
    };\n
\n
    jsPlumb.Endpoint = function(params) {\n
        var _jsPlumb = params._jsPlumb,\n
            _att = jsPlumbAdapter.getAttribute,\n
            _gel = jsPlumb.getElementObject,            \n
            _ju = jsPlumbUtil,            \n
            _newConnection = params.newConnection,\n
            _newEndpoint = params.newEndpoint,\n
            _finaliseConnection = params.finaliseConnection,\n
            _fireDetachEvent = params.fireDetachEvent,\n
            _fireMoveEvent = params.fireMoveEvent,\n
            floatingConnections = params.floatingConnections;\n
        \n
        this.idPrefix = "_jsplumb_e_";\t\t\t\n
        this.defaultLabelLocation = [ 0.5, 0.5 ];\n
        this.defaultOverlayKeys = ["Overlays", "EndpointOverlays"];\n
        OverlayCapableJsPlumbUIComponent.apply(this, arguments);        \n
        \n
// TYPE\t\t\n
                \n
        this.getDefaultType = function() {\t\t\t\t\t\t\t\t\n
            return {\n
                parameters:{},\n
                scope:null,\n
                maxConnections:this._jsPlumb.instance.Defaults.MaxConnections,\n
                paintStyle:this._jsPlumb.instance.Defaults.EndpointStyle || jsPlumb.Defaults.EndpointStyle,\n
                endpoint:this._jsPlumb.instance.Defaults.Endpoint || jsPlumb.Defaults.Endpoint,\n
                hoverPaintStyle:this._jsPlumb.instance.Defaults.EndpointHoverStyle || jsPlumb.Defaults.EndpointHoverStyle,\t\t\t\t\n
                overlays:this._jsPlumb.instance.Defaults.EndpointOverlays || jsPlumb.Defaults.EndpointOverlays,\n
                connectorStyle:params.connectorStyle,\t\t\t\t\n
                connectorHoverStyle:params.connectorHoverStyle,\n
                connectorClass:params.connectorClass,\n
                connectorHoverClass:params.connectorHoverClass,\n
                connectorOverlays:params.connectorOverlays,\n
                connector:params.connector,\n
                connectorTooltip:params.connectorTooltip\n
            };\n
        };\n
        \t\t\t\n
// END TYPE\n
            \n
        this._jsPlumb.enabled = !(params.enabled === false);\n
        this._jsPlumb.visible = true;        \n
        this.element = jsPlumb.getDOMElement(params.source);  \n
        this._jsPlumb.uuid = params.uuid;\n
        this._jsPlumb.floatingEndpoint = null;  \n
        var inPlaceCopy = null;\n
        if (this._jsPlumb.uuid) params.endpointsByUUID[this._jsPlumb.uuid] = this;\n
        this.elementId = params.elementId;\n
        \n
        this._jsPlumb.connectionCost = params.connectionCost;\n
        this._jsPlumb.connectionsDirected = params.connectionsDirected;        \n
        this._jsPlumb.currentAnchorClass = "";\n
        this._jsPlumb.events = {};\n
            \n
        var  _updateAnchorClass = function() {\n
            jsPlumbAdapter.removeClass(this.element, _jsPlumb.endpointAnchorClassPrefix + "_" + this._jsPlumb.currentAnchorClass);\n
            this.removeClass(_jsPlumb.endpointAnchorClassPrefix + "_" + this._jsPlumb.currentAnchorClass);\n
            this._jsPlumb.currentAnchorClass = this.anchor.getCssClass();\n
            this.addClass(_jsPlumb.endpointAnchorClassPrefix + "_" + this._jsPlumb.currentAnchorClass);\n
            jsPlumbAdapter.addClass(this.element, _jsPlumb.endpointAnchorClassPrefix + "_" + this._jsPlumb.currentAnchorClass);\n
        }.bind(this);\n
        \n
        this.setAnchor = function(anchorParams, doNotRepaint) {\n
            this._jsPlumb.instance.continuousAnchorFactory.clear(this.elementId);\n
            this.anchor = this._jsPlumb.instance.makeAnchor(anchorParams, this.elementId, _jsPlumb);\n
            _updateAnchorClass();\n
            this.anchor.bind("anchorChanged", function(currentAnchor) {\n
                this.fire("anchorChanged", {endpoint:this, anchor:currentAnchor});\n
                _updateAnchorClass();\n
            }.bind(this));\n
            if (!doNotRepaint)\n
                this._jsPlumb.instance.repaint(this.elementId);\n
            return this;\n
        };\n
\n
        var anchorParamsToUse = params.anchor ? params.anchor : params.anchors ? params.anchors : (_jsPlumb.Defaults.Anchor || "Top");\n
        this.setAnchor(anchorParamsToUse, true);\n
\n
        // endpoint delegates to first connection for hover, if there is one.\n
        var internalHover = function(state) {\n
          if (this.connections.length > 0)\n
            this.connections[0].setHover(state, false);\n
          else\n
            this.setHover(state);\n
        }.bind(this);\n
            \n
        // ANCHOR MANAGER\n
        if (!params._transient) // in place copies, for example, are transient.  they will never need to be retrieved during a paint cycle, because they dont move, and then they are deleted.\n
            this._jsPlumb.instance.anchorManager.add(this, this.elementId);\n
        \n
        this.setEndpoint = function(ep) {\n
\n
            if (this.endpoint != null) {\n
                this.endpoint.cleanup();\n
                this.endpoint.destroy();\n
            }\n
\n
            var _e = function(t, p) {\n
                var rm = _jsPlumb.getRenderMode();\n
                if (jsPlumb.Endpoints[rm][t]) return new jsPlumb.Endpoints[rm][t](p);\n
                if (!_jsPlumb.Defaults.DoNotThrowErrors)\n
                    throw { msg:"jsPlumb: unknown endpoint type \'" + t + "\'" };\n
            };            \n
\n
            var endpointArgs = {\n
                _jsPlumb:this._jsPlumb.instance,\n
                cssClass:params.cssClass,\n
                container:params.container,\n
                tooltip:params.tooltip,\n
                connectorTooltip:params.connectorTooltip,\n
                endpoint:this\n
            };\n
            if (_ju.isString(ep)) \n
                this.endpoint = _e(ep, endpointArgs);\n
            else if (_ju.isArray(ep)) {\n
                endpointArgs = _ju.merge(ep[1], endpointArgs);\n
                this.endpoint = _e(ep[0], endpointArgs);\n
            }\n
            else {\n
                this.endpoint = ep.clone();\n
            }\n
\n
            // assign a clone function using a copy of endpointArgs. this is used when a drag starts: the endpoint that was dragged is cloned,\n
            // and the clone is left in its place while the original one goes off on a magical journey. \n
            // the copy is to get around a closure problem, in which endpointArgs ends up getting shared by\n
            // the whole world.\n
            var argsForClone = jsPlumb.extend({}, endpointArgs);\t\t\t\t\t\t\n
            this.endpoint.clone = function() {\n
                // TODO this, and the code above, can be refactored to be more dry.\n
                if (_ju.isString(ep)) \n
                    return _e(ep, endpointArgs);\n
                else if (_ju.isArray(ep)) {\n
                    endpointArgs = _ju.merge(ep[1], endpointArgs);\n
                    return _e(ep[0], endpointArgs);\n
                }\n
            }.bind(this);\n
\n
            this.type = this.endpoint.type;\n
            // bind listeners from endpoint to self, with the internal hover function defined above.\n
            this.bindListeners(this.endpoint, this, internalHover);\n
        };\n
         \n
        this.setEndpoint(params.endpoint || _jsPlumb.Defaults.Endpoint || jsPlumb.Defaults.Endpoint || "Dot");\t\t\t\t\t\t\t                    \n
        this.setPaintStyle(params.paintStyle || params.style || _jsPlumb.Defaults.EndpointStyle || jsPlumb.Defaults.EndpointStyle, true);\n
        this.setHoverPaintStyle(params.hoverPaintStyle || _jsPlumb.Defaults.EndpointHoverStyle || jsPlumb.Defaults.EndpointHoverStyle, true);\n
        this._jsPlumb.paintStyleInUse = this.getPaintStyle();\n
\n
        jsPlumb.extend(this, params, typeParameters);\n
\n
        this.isSource = params.isSource || false;\n
        this.isTarget = params.isTarget || false;        \n
        this._jsPlumb.maxConnections = params.maxConnections || _jsPlumb.Defaults.MaxConnections; // maximum number of connections this endpoint can be the source of.                \n
        this.canvas = this.endpoint.canvas;\t\t\n
        // add anchor class (need to do this on construction because we set anchor first)\n
        this.addClass(_jsPlumb.endpointAnchorClassPrefix + "_" + this._jsPlumb.currentAnchorClass);\t\n
        jsPlumbAdapter.addClass(this.element, _jsPlumb.endpointAnchorClassPrefix + "_" + this._jsPlumb.currentAnchorClass);\n
        this.connections = params.connections || [];\n
        this.connectorPointerEvents = params["connector-pointer-events"];\n
        \n
        this.scope = params.scope || _jsPlumb.getDefaultScope();        \n
        this.timestamp = null;\n
        this.reattachConnections = params.reattach || _jsPlumb.Defaults.ReattachConnections;\n
        this.connectionsDetachable = _jsPlumb.Defaults.ConnectionsDetachable;\n
        if (params.connectionsDetachable === false || params.detachable === false)\n
            this.connectionsDetachable = false;\n
        this.dragAllowedWhenFull = params.dragAllowedWhenFull || true;\n
        \n
        if (params.onMaxConnections)\n
            this.bind("maxConnections", params.onMaxConnections);        \n
        \n
        //\n
        // add a connection. not part of public API.\n
        //\n
        this.addConnection = function(connection) {\n
            this.connections.push(connection);                  \n
            this[(this.connections.length > 0 ? "add" : "remove") + "Class"](_jsPlumb.endpointConnectedClass);       \n
            this[(this.isFull() ? "add" : "remove") + "Class"](_jsPlumb.endpointFullClass); \n
        };\t\n
\n
        this.detachFromConnection = function(connection, idx, doNotCleanup) {\n
            idx = idx == null ? findConnectionIndex(connection, this) : idx;\n
            if (idx >= 0) {\n
                this.connections.splice(idx, 1);\n
                this[(this.connections.length > 0 ? "add" : "remove") + "Class"](_jsPlumb.endpointConnectedClass);       \n
                this[(this.isFull() ? "add" : "remove") + "Class"](_jsPlumb.endpointFullClass);\n
            }\n
            \n
            if (!doNotCleanup && this._deleteOnDetach && this.connections.length === 0) {\n
                _jsPlumb.deleteObject({\n
                    endpoint:this,\n
                    fireEvent:false,\n
                    deleteAttachedObjects:false\n
                });\n
            }\n
        };\n
\n
        this.detach = function(connection, ignoreTarget, forceDetach, fireEvent, originalEvent, endpointBeingDeleted, connectionIndex) {\n
\n
            var idx = connectionIndex == null ? findConnectionIndex(connection, this) : connectionIndex,\n
                actuallyDetached = false;\n
                fireEvent = (fireEvent !== false);\n
\n
            if (idx >= 0) {\t\t                \n
                if (forceDetach || connection._forceDetach || (connection.isDetachable() && connection.isDetachAllowed(connection) && this.isDetachAllowed(connection) )) {\n
\n
                    _jsPlumb.deleteObject({\n
                        connection:connection, \n
                        fireEvent:(!ignoreTarget && fireEvent), \n
                        originalEvent:originalEvent,\n
                        deleteAttachedObjects:false\n
                    });\n
                    actuallyDetached = true;                       \n
                }\n
            }\n
            return actuallyDetached;\n
        };\t\n
\n
        this.detachAll = function(fireEvent, originalEvent) {\n
            while (this.connections.length > 0) {\n
                // TODO this could pass the index in to the detach method to save some time (index will always be zero in this while loop)\n
                this.detach(this.connections[0], false, true, fireEvent !== false, originalEvent, this, 0);\n
            }\n
            return this;\n
        };                \n
        this.detachFrom = function(targetEndpoint, fireEvent, originalEvent) {\n
            var c = [];\n
            for ( var i = 0; i < this.connections.length; i++) {\n
                if (this.connections[i].endpoints[1] == targetEndpoint || this.connections[i]

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAQ=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="4" aka="AAAAAAAAAAQ=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

.endpoints[0] == targetEndpoint) {\n
                    c.push(this.connections[i]);\n
                }\n
            }\n
            for ( var j = 0; j < c.length; j++) {\n
                this.detach(c[j], false, true, fireEvent, originalEvent);\t\t\t\t\n
            }\n
            return this;\n
        };\t        \n
        \n
        this.getElement = function() {\n
            return this.element;\n
        };\t\t\n
                 \n
        this.setElement = function(el) {\n
            var parentId = this._jsPlumb.instance.getId(el),\n
                curId = this.elementId;\n
            // remove the endpoint from the list for the current endpoint\'s element\n
            _ju.removeWithFunction(params.endpointsByElement[this.elementId], function(e) {\n
                return e.id == this.id;\n
            }.bind(this));\n
            this.element = jsPlumb.getDOMElement(el);\n
            this.elementId = _jsPlumb.getId(this.element);                         \n
            _jsPlumb.anchorManager.rehomeEndpoint(this, curId, this.element);\n
            _jsPlumb.dragManager.endpointAdded(this.element);            \n
            _ju.addToList(params.endpointsByElement, parentId, this);            \n
            return this;\n
        };\n
                \n
        /**\n
         * private but must be exposed.\n
         */\n
        this.makeInPlaceCopy = function() {\n
            var loc = this.anchor.getCurrentLocation({element:this}),\n
                o = this.anchor.getOrientation(this),\n
                acc = this.anchor.getCssClass(),\n
                inPlaceAnchor = {\n
                    bind:function() { },\n
                    compute:function() { return [ loc[0], loc[1] ]; },\n
                    getCurrentLocation : function() { return [ loc[0], loc[1] ]; },\n
                    getOrientation:function() { return o; },\n
                    getCssClass:function() { return acc; }\n
                };\n
\n
            return _newEndpoint( { \n
                dropOptions:params.dropOptions,\n
                anchor : inPlaceAnchor, \n
                source : this.element, \n
                paintStyle : this.getPaintStyle(), \n
                endpoint : params.hideOnDrag ? "Blank" : this.endpoint,\n
                _transient:true,\n
                scope:this.scope\n
            });\n
        };            \n
        \n
        /**\n
         * returns a connection from the pool; used when dragging starts.  just gets the head of the array if it can.\n
         */\n
        this.connectorSelector = function() {\n
            var candidate = this.connections[0];\n
            if (this.isTarget && candidate) return candidate;\n
            else {\n
                return (this.connections.length < this._jsPlumb.maxConnections) || this._jsPlumb.maxConnections == -1 ? null : candidate;\n
            }\n
        };        \n
        \n
        this.setStyle = this.setPaintStyle;        \n
        \n
        this.paint = function(params) {\n
            params = params || {};\n
            var timestamp = params.timestamp, recalc = !(params.recalc === false);\t\t\t\t\t\t\t\t\n
            if (!timestamp || this.timestamp !== timestamp) {\t\t\t\t\t\t\n
                \n
                // TODO check: is this is a safe performance enhancement?\n
                var info = _jsPlumb.updateOffset({ elId:this.elementId, timestamp:timestamp/*, recalc:recalc*/ });                \n
\n
                var xy = params.offset ? params.offset.o : info.o;\n
                if(xy != null) {\n
                    var ap = params.anchorPoint,connectorPaintStyle = params.connectorPaintStyle;\n
                    if (ap == null) {\n
                        var wh = params.dimensions || info.s,                       \n
                            anchorParams = { xy : [ xy.left, xy.top ], wh : wh, element : this, timestamp : timestamp };\n
                        if (recalc && this.anchor.isDynamic && this.connections.length > 0) {\n
                            var c = findConnectionToUseForDynamicAnchor(this, params.elementWithPrecedence),\n
                                oIdx = c.endpoints[0] == this ? 1 : 0,\n
                                oId = oIdx === 0 ? c.sourceId : c.targetId,\n
                                oInfo = _jsPlumb.getCachedData(oId),\n
                                oOffset = oInfo.o, oWH = oInfo.s;\n
                            anchorParams.txy = [ oOffset.left, oOffset.top ];\n
                            anchorParams.twh = oWH;\n
                            anchorParams.tElement = c.endpoints[oIdx];\n
                        }\n
                        ap = this.anchor.compute(anchorParams);\n
                    }\n
                                        \n
                    this.endpoint.compute(ap, this.anchor.getOrientation(this), this._jsPlumb.paintStyleInUse, connectorPaintStyle || this.paintStyleInUse);\n
                    this.endpoint.paint(this._jsPlumb.paintStyleInUse, this.anchor);\t\t\t\t\t\n
                    this.timestamp = timestamp;\n
\n
                    // paint overlays\n
                    for ( var i = 0; i < this._jsPlumb.overlays.length; i++) {\n
                        var o = this._jsPlumb.overlays[i];\n
                        if (o.isVisible()) { \n
                            this._jsPlumb.overlayPlacements[i] = o.draw(this.endpoint, this._jsPlumb.paintStyleInUse);\n
                            o.paint(this._jsPlumb.overlayPlacements[i]);    \n
                        }\n
                    }\n
                }\n
            }\n
        };\n
\n
        this.repaint = this.paint; \n
\n
        var draggingInitialised = false;\n
        this.initDraggable = function() {\n
            // is this a connection source? we make it draggable and have the\n
            // drag listener maintain a connection with a floating endpoint.\n
            if (!draggingInitialised && jsPlumb.isDragSupported(this.element)) {\n
                var placeholderInfo = { id:null, element:null },\n
                    jpc = null,\n
                    existingJpc = false,\n
                    existingJpcParams = null,\n
                    _dragHandler = _makeConnectionDragHandler(placeholderInfo, _jsPlumb);\n
\n
                var start = function() {    \n
                // drag might have started on an endpoint that is not actually a source, but which has\n
                // one or more connections.\n
                    jpc = this.connectorSelector();\n
                    var _continue = true;\n
                    // if not enabled, return\n
                    if (!this.isEnabled()) _continue = false;\n
                    // if no connection and we\'re not a source, return.\n
                    if (jpc == null && !this.isSource) _continue = false;\n
                    // otherwise if we\'re full and not allowed to drag, also return false.\n
                    if (this.isSource && this.isFull() && !this.dragAllowedWhenFull) _continue = false;\n
                    // if the connection was setup as not detachable or one of its endpoints\n
                    // was setup as connectionsDetachable = false, or Defaults.ConnectionsDetachable\n
                    // is set to false...\n
                    if (jpc != null && !jpc.isDetachable()) _continue = false;\n
\n
                    if (_continue === false) {\n
                        // this is for mootools and yui. returning false from this causes jquery to stop drag.\n
                        // the events are wrapped in both mootools and yui anyway, but i don\'t think returning\n
                        // false from the start callback would stop a drag.\n
                        if (_jsPlumb.stopDrag) _jsPlumb.stopDrag(this.canvas);\n
                        _dragHandler.stopDrag();\n
                        return false;\n
                    }\n
\n
                    // clear hover for all connections for this endpoint before continuing.\n
                    for (var i = 0; i < this.connections.length; i++)\n
                        this.connections[i].setHover(false);\n
\n
                    this.addClass("endpointDrag");\n
                    _jsPlumb.setConnectionBeingDragged(true);\n
\n
                    // if we\'re not full but there was a connection, make it null. we\'ll create a new one.\n
                    if (jpc && !this.isFull() && this.isSource) jpc = null;\n
\n
                    _jsPlumb.updateOffset( { elId : this.elementId });\n
                    inPlaceCopy = this.makeInPlaceCopy();\n
                    inPlaceCopy.referenceEndpoint = this;\n
                    inPlaceCopy.paint();                                                                \n
                    \n
                    _makeDraggablePlaceholder(placeholderInfo, _jsPlumb);\n
                    \n
                    // set the offset of this div to be where \'inPlaceCopy\' is, to start with.\n
                    // TODO merge this code with the code in both Anchor and FloatingAnchor, because it\n
                    // does the same stuff.\n
                    var ipcoel = _gel(inPlaceCopy.canvas),\n
                        ipco = jsPlumbAdapter.getOffset(ipcoel, this._jsPlumb.instance),                        \n
                        canvasElement = _gel(this.canvas);                               \n
                        \n
                    jsPlumbAdapter.setPosition(placeholderInfo.element, ipco);\n
                    \n
                    // when using makeSource and a parent, we first draw the source anchor on the source element, then\n
                    // move it to the parent.  note that this happens after drawing the placeholder for the\n
                    // first time.\n
                    if (this.parentAnchor) this.anchor = _jsPlumb.makeAnchor(this.parentAnchor, this.elementId, _jsPlumb);\n
                    \n
                    // store the id of the dragging div and the source element. the drop function will pick these up.                   \n
                    _jsPlumb.setAttribute(this.canvas, "dragId", placeholderInfo.id);\n
                    _jsPlumb.setAttribute(this.canvas, "elId", this.elementId);\n
\n
                    this._jsPlumb.floatingEndpoint = _makeFloatingEndpoint(this.getPaintStyle(), this.anchor, this.endpoint, this.canvas, placeholderInfo.element, _jsPlumb, _newEndpoint);\n
                    // TODO we should not know about DOM here. make the library adapter do this (or the \n
                        // dom adapter)\n
                    this.canvas.style.visibility = "hidden";            \n
                    \n
                    if (jpc == null) {                                                                                                                                                         \n
                        this.anchor.locked = true;\n
                        this.setHover(false, false);                        \n
                        // create a connection. one end is this endpoint, the other is a floating endpoint.                    \n
                        jpc = _newConnection({\n
                            sourceEndpoint : this,\n
                            targetEndpoint : this._jsPlumb.floatingEndpoint,\n
                            source : this.endpointWillMoveTo || this.element,  // for makeSource with parent option.  ensure source element is represented correctly.\n
                            target : placeholderInfo.element,\n
                            anchors : [ this.anchor, this._jsPlumb.floatingEndpoint.anchor ],\n
                            paintStyle : params.connectorStyle, // this can be null. Connection will use the default.\n
                            hoverPaintStyle:params.connectorHoverStyle,\n
                            connector : params.connector, // this can also be null. Connection will use the default.\n
                            overlays : params.connectorOverlays,\n
                            type:this.connectionType,\n
                            cssClass:this.connectorClass,\n
                            hoverClass:this.connectorHoverClass\n
                        });\n
                        jpc.pending = true; // mark this connection as not having been established.\n
                        jpc.addClass(_jsPlumb.draggingClass);\n
                        this._jsPlumb.floatingEndpoint.addClass(_jsPlumb.draggingClass);\n
                        // fire an event that informs that a connection is being dragged\n
                        _jsPlumb.fire("connectionDrag", jpc);\n
\n
                    } else {\n
                        existingJpc = true;\n
                        jpc.setHover(false);\n
                        // new anchor idx\n
                        var anchorIdx = jpc.endpoints[0].id == this.id ? 0 : 1;\n
                        jpc.floatingAnchorIndex = anchorIdx;                    // save our anchor index as the connection\'s floating index.                        \n
                        this.detachFromConnection(jpc, null, true);                         // detach from the connection while dragging is occurring. but dont cleanup automatically.\n
                        \n
                        //*\n
                        // store the original scope (issue 57)\n
                        var dragScope = _jsPlumb.getDragScope(canvasElement);\n
                        _jsPlumb.setAttribute(this.canvas, "originalScope", dragScope);\n
                        // now we want to get this endpoint\'s DROP scope, and set it for now: we can only be dropped on drop zones\n
                        // that have our drop scope (issue 57).\n
                        var dropScope = _jsPlumb.getDropScope(canvasElement);\n
                        _jsPlumb.setDragScope(canvasElement, dropScope);\n
                        //*/\n
\n
                        // fire an event that informs that a connection is being dragged. we do this before\n
                        // replacing the original target with the floating element info.\n
                        _jsPlumb.fire("connectionDrag", jpc);\n
                \n
                        // now we replace ourselves with the temporary div we created above:\n
                        if (anchorIdx === 0) {\n
                            existingJpcParams = [ jpc.source, jpc.sourceId, canvasElement, dragScope ];\n
                            jpc.source = placeholderInfo.element;\n
                            jpc.sourceId = placeholderInfo.id;\n
                        } else {\n
                            existingJpcParams = [ jpc.target, jpc.targetId, canvasElement, dragScope ];\n
                            jpc.target = placeholderInfo.element;\n
                            jpc.targetId = placeholderInfo.id;\n
                        }\n
\n
                        // lock the other endpoint; if it is dynamic it will not move while the drag is occurring.\n
                        jpc.endpoints[anchorIdx === 0 ? 1 : 0].anchor.locked = true;\n
                        // store the original endpoint and assign the new floating endpoint for the drag.\n
                        jpc.suspendedEndpoint = jpc.endpoints[anchorIdx];\n
                        \n
                        // PROVIDE THE SUSPENDED ELEMENT, BE IT A SOURCE OR TARGET (ISSUE 39)\n
                        jpc.suspendedElement = jpc.endpoints[anchorIdx].getElement();\n
                        jpc.suspendedElementId = jpc.endpoints[anchorIdx].elementId;\n
                        jpc.suspendedElementType = anchorIdx === 0 ? "source" : "target";\n
                        \n
                        jpc.suspendedEndpoint.setHover(false);\n
                        this._jsPlumb.floatingEndpoint.referenceEndpoint = jpc.suspendedEndpoint;\n
                        jpc.endpoints[anchorIdx] = this._jsPlumb.floatingEndpoint;\n
\n
                        jpc.addClass(_jsPlumb.draggingClass);\n
                        this._jsPlumb.floatingEndpoint.addClass(_jsPlumb.draggingClass);                    \n
\n
                    }\n
                    // register it and register connection on it.\n
                    floatingConnections[placeholderInfo.id] = jpc;\n
                    _jsPlumb.anchorManager.addFloatingConnection(placeholderInfo.id, jpc);               \n
                    // only register for the target endpoint; we will not be dragging the source at any time\n
                    // before this connection is either discarded or made into a permanent connection.\n
                    _ju.addToList(params.endpointsByElement, placeholderInfo.id, this._jsPlumb.floatingEndpoint);\n
                    // tell jsplumb about it\n
                    _jsPlumb.currentlyDragging = true;\n
                }.bind(this);\n
\n
                var dragOptions = params.dragOptions || {},\n
                    defaultOpts = {},\n
                    startEvent = jsPlumb.dragEvents.start,\n
                    stopEvent = jsPlumb.dragEvents.stop,\n
                    dragEvent = jsPlumb.dragEvents.drag;\n
                \n
                dragOptions = jsPlumb.extend(defaultOpts, dragOptions);\n
                dragOptions.scope = dragOptions.scope || this.scope;\n
                dragOptions[startEvent] = _ju.wrap(dragOptions[startEvent], start, false);\n
                // extracted drag handler function so can be used by makeSource\n
                dragOptions[dragEvent] = _ju.wrap(dragOptions[dragEvent], _dragHandler.drag);\n
                dragOptions[stopEvent] = _ju.wrap(dragOptions[stopEvent],\n
                    function() {        \n
\n
                        _jsPlumb.setConnectionBeingDragged(false);  \n
                        // if no endpoints, jpc already cleaned up.\n
                        if (jpc && jpc.endpoints != null) {          \n
                            // get the actual drop event (decode from library args to stop function)\n
                            var originalEvent = _jsPlumb.getDropEvent(arguments);                                       \n
                            // unlock the other endpoint (if it is dynamic, it would have been locked at drag start)\n
                            var idx = jpc.floatingAnchorIndex == null ? 1 : jpc.floatingAnchorIndex;\n
                            jpc.endpoints[idx === 0 ? 1 : 0].anchor.locked = false;\n
                            // WHY does this need to happen?  i suppose because the connection might not get \n
                            // deleted.  TODO: i dont want to know about css classes inside jsplumb, ideally.\n
                            jpc.removeClass(_jsPlumb.draggingClass);   \n
                        \n
                            // if we have the floating endpoint then the connection has not been dropped\n
                            // on another endpoint.  If it is a new connection we throw it away. If it is an \n
                            // existing connection we check to see if we should reattach it, throwing it away \n
                            // if not.\n
                            if (jpc.endpoints[idx] == this._jsPlumb.floatingEndpoint) {\n
                                // 6a. if the connection was an existing one...\n
                                if (existingJpc && jpc.suspendedEndpoint) {\n
                                    // fix for issue35, thanks Sylvain Gizard: when firing the detach event make sure the\n
                                    // floating endpoint has been replaced.\n
                                    if (idx === 0) {\n
                                        jpc.source = existingJpcParams[0];\n
                                        jpc.sourceId = existingJpcParams[1];\n
                                    } else {\n
                                        jpc.target = existingJpcParams[0];\n
                                        jpc.targetId = existingJpcParams[1];\n
                                    }\n
                                    \n
                                    // restore the original scope (issue 57)\n
                                    _jsPlumb.setDragScope(existingJpcParams[2], existingJpcParams[3]);\n
                                    jpc.endpoints[idx] = jpc.suspendedEndpoint;\n
                                    // IF the connection should be reattached, or the other endpoint refuses detach, then\n
                                    // reset the connection to its original state\n
                                    if (jpc.isReattach() || jpc._forceReattach || jpc._forceDetach || !jpc.endpoints[idx === 0 ? 1 : 0].detach(jpc, false, false, true, originalEvent)) {                                   \n
                                        jpc.setHover(false);\n
                                        jpc.floatingAnchorIndex = null;\n
                                        jpc._forceDetach = null;\n
                                        jpc._forceReattach = null;\n
                                        this._jsPlumb.floatingEndpoint.detachFromConnection(jpc);\n
                                        jpc.suspendedEndpoint.addConnection(jpc);\n
                                        _jsPlumb.repaint(existingJpcParams[1]);\n
                                    }\n
                                    else\n
                                        jpc.suspendedEndpoint.detachFromConnection(jpc);  // confirm we want it to detach; it may decide to self-destruct\n
                                }                                                               \n
                            }\n
\n
                            // remove the element associated with the floating endpoint \n
                            // (and its associated floating endpoint and visual artefacts)                                        \n
                            _jsPlumb.remove(placeholderInfo.element, false);\n
                            // remove the inplace copy\n
                            //_jsPlumb.remove(inPlaceCopy.canvas, false);\n
                            _jsPlumb.deleteObject({endpoint:inPlaceCopy});\n
    \n
                            // makeTargets sets this flag, to tell us we have been replaced and should delete ourself.\n
                            if (this.deleteAfterDragStop) {                        \n
                                _jsPlumb.deleteObject({endpoint:this});\n
                            }\n
                            else {\n
                                if (this._jsPlumb) {\n
                                    this._jsPlumb.floatingEndpoint = null;\n
                                    // repaint this endpoint.\n
                                    // make our canvas visible (TODO: hand off to library; we should not know about DOM)\n
                                    this.canvas.style.visibility = "visible";\n
                                    // unlock our anchor\n
                                    this.anchor.locked = false;\n
                                    this.paint({recalc:false});                        \n
                                }\n
                            }                                                    \n
    \n
                            // although the connection is no longer valid, there are use cases where this is useful.\n
                            _jsPlumb.fire("connectionDragStop", jpc, originalEvent);\n
    \n
                            // tell jsplumb that dragging is finished.\n
                            _jsPlumb.currentlyDragging = false;\n
    \n
                            jpc = null;\n
                        }\n
\n
                    }.bind(this));\n
                \n
                var i = _gel(this.canvas);              \n
                _jsPlumb.initDraggable(i, dragOptions, true);\n
\n
                draggingInitialised = true;\n
            }\n
        };\n
\n
        // if marked as source or target at create time, init the dragging.\n
        if (this.isSource || this.isTarget)\n
            this.initDraggable();        \n
\n
        // pulled this out into a function so we can reuse it for the inPlaceCopy canvas; you can now drop detached connections\n
        // back onto the endpoint you detached it from.\n
        var _initDropTarget = function(canvas, forceInit, isTransient, endpoint) {\n
            if ((this.isTarget || forceInit) && jsPlumb.isDropSupported(this.element)) {\n
                var dropOptions = params.dropOptions || _jsPlumb.Defaults.DropOptions || jsPlumb.Defaults.DropOptions;\n
                dropOptions = jsPlumb.extend( {}, dropOptions);\n
                dropOptions.scope = dropOptions.scope || this.scope;\n
                var dropEvent = jsPlumb.dragEvents.drop,\n
                    overEvent = jsPlumb.dragEvents.over,\n
                    outEvent = jsPlumb.dragEvents.out,\n
                    drop = function() {                        \n
\n
                        this.removeClass(_jsPlumb.endpointDropAllowedClass);\n
                        this.removeClass(_jsPlumb.endpointDropForbiddenClass);\n
                                                    \n
                        var originalEvent = _jsPlumb.getDropEvent(arguments),\n
                            draggable = _jsPlumb.getDOMElement(_jsPlumb.getDragObject(arguments)),\n
                            id = _jsPlumb.getAttribute(draggable, "dragId"),\n
                            elId = _jsPlumb.getAttribute(draggable, "elId"),\t\t\t\t\t\t\n
                            scope = _jsPlumb.getAttribute(draggable, "originalScope"),\n
                            jpc = floatingConnections[id];\n
                            \n
                        if (jpc != null) {\n
                            // if this is a drop back where the connection came from, mark it force rettach and\n
                        // return; the stop handler will reattach. without firing an event.\n
                        var redrop = jpc.suspendedEndpoint && (jpc.suspendedEndpoint.id == this.id ||\n
                                        this.referenceEndpoint && jpc.suspendedEndpoint.id == this.referenceEndpoint.id) ;\t\t\t\t\t\t\t\n
                        if (redrop) {\t\t\t\t\t\t\t\t\n
                            jpc._forceReattach = true;\n
                            return;\n
                        }\n
                            var idx = jpc.floatingAnchorIndex == null ? 1 : jpc.floatingAnchorIndex, oidx = idx === 0 ? 1 : 0;\n
                            \n
                            // restore the original scope if necessary (issue 57)\t\t\t\t\t\t\n
                            if (scope) _jsPlumb.setDragScope(draggable, scope);\t\t\t\t\t\t\t\n
                            \n
                            var endpointEnabled = endpoint != null ? endpoint.isEnabled() : true;\n
                            \n
                            if (this.isFull()) {\n
                                this.fire("maxConnections", { \n
                                    endpoint:this, \n
                                    connection:jpc, \n
                                    maxConnections:this._jsPlumb.maxConnections \n
                                }, originalEvent);\n
                            }\n
                                                            \n
                            if (!this.isFull() && !(idx === 0 && !this.isSource) && !(idx == 1 && !this.isTarget) && endpointEnabled) {\n
                                var _doContinue = true;\n
\n
                                // the second check here is for the case that the user is dropping it back\n
                                // where it came from.\n
                                if (jpc.suspendedEndpoint && jpc.suspendedEndpoint.id != this.id) {\n
                                    if (idx === 0) {\n
                                        jpc.source = jpc.suspendedEndpoint.element;\n
                                        jpc.sourceId = jpc.suspendedEndpoint.elementId;\n
                                    } else {\n
                                        jpc.target = jpc.suspendedEndpoint.element;\n
                                        jpc.targetId = jpc.suspendedEndpoint.elementId;\n
                                    }\n
\n
                                    if (!jpc.isDetachAllowed(jpc) || !jpc.endpoints[idx].isDetachAllowed(jpc) || !jpc.suspendedEndpoint.isDetachAllowed(jpc) || !_jsPlumb.checkCondition("beforeDetach", jpc))\n
                                        _doContinue = false;\t\t\t\t\t\t\t\t\n
                                }\n
            \n
                                // these have to be set before testing for beforeDrop.\n
                                if (idx === 0) {\n
                                    jpc.source = this.element;\n
                                    jpc.sourceId = this.elementId;\n
                                } else {\n
                                    jpc.target = this.element;\n
                                    jpc.targetId = this.elementId;\n
                                }\n
                                                            \n
// ------------ wrap the execution path in a function so we can support asynchronous beforeDrop\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\n
                                    \n
                                // we want to execute this regardless.\n
                                var commonFunction = function() {\n
                                    jpc.floatingAnchorIndex = null;\n
                                };\t\n
                                                                                                \n
                                var continueFunction = function() {\n
                                    jpc.pending = false;\n
\n
                                    // remove this jpc from the current endpoint\n
                                    jpc.endpoints[idx].detachFromConnection(jpc);\n
                                    if (jpc.suspendedEndpoint) jpc.suspendedEndpoint.detachFromConnection(jpc);\n
                                    jpc.endpoints[idx] = this;\n
                                    this.addConnection(jpc);\n
                                    \n
                                    // copy our parameters in to the connection:\n
                                    var params = this.getParameters();\n
                                    for (var aParam in params)\n
                                        jpc.setParameter(aParam, params[aParam]);\n
\n
                                    if (!jpc.suspendedEndpoint) {  \n
                                        // if not an existing connection and\n
                                        if (params.draggable)\n
                                            jsPlumb.initDraggable(this.element, dragOptions, true, _jsPlumb);\n
                                    }\n
                                    else {\n
                                        var suspendedElement = jpc.suspendedEndpoint.getElement(), suspendedElementId = jpc.suspendedEndpoint.elementId;\n
                                        _fireMoveEvent({\n
                                            index:idx,\n
                                            originalSourceId:idx === 0 ? suspendedElementId : jpc.sourceId,\n
                                            newSourceId:idx === 0 ? this.elementId : jpc.sourceId,\n
                                            originalTargetId:idx == 1 ? suspendedElementId : jpc.targetId,\n
                                            newTargetId:idx == 1 ? this.elementId : jpc.targetId,\n
                                            originalSourceEndpoint:idx === 0 ? jpc.suspendedEndpoint : jpc.endpoints[0],\n
                                            newSourceEndpoint:idx === 0 ? this : jpc.endpoints[0],\n
                                            originalTargetEndpoint:idx == 1 ? jpc.suspendedEndpoint : jpc.endpoints[1],\n
                                            newTargetEndpoint:idx == 1 ? this : jpc.endpoints[1],\n
                                            connection:jpc\n
                                        }, originalEvent);\n
                                    }\n
\n
                                    // TODO this is like the makeTarget drop code.\n
                                    if (idx == 1)\n
                                        _jsPlumb.anchorManager.updateOtherEndpoint(jpc.sourceId, jpc.suspendedElementId, jpc.targetId, jpc);\n
                                    else\n
                                        _jsPlumb.anchorManager.sourceChanged(jpc.suspendedEndpoint.elementId, jpc.sourceId, jpc);\n
\n
                                    // finalise will inform the anchor manager and also add to\n
                                    // connectionsByScope if necessary.\n
                                    // TODO if this is not set to true, then dragging a connection\'s target to a new\n
                                    // target causes the connection to be forgotten. however if it IS set to true, then\n
                                    // the opposite happens: dragging by source causes the connection to get forgotten\n
                                    // about and then if you delete it jsplumb breaks.\n
                                    _finaliseConnection(jpc, null, originalEvent/*, true*/);\n
                                    \n
                                    commonFunction();\n
                                }.bind(this);\n
                                \n
                                var dontContinueFunction = function() {\n
                                    // otherwise just put it back on the endpoint it was on before the drag.\n
                                    if (jpc.suspendedEndpoint) {\t\t\t\t\t\t\t\t\t\n
                                        jpc.endpoints[idx] = jpc.suspendedEndpoint;\n
                                        jpc.setHover(false);\n
                                        jpc._forceDetach = true;\n
                                        if (idx === 0) {\n
                                            jpc.source = jpc.suspendedEndpoint.element;\n
                                            jpc.sourceId = jpc.suspendedEndpoint.elementId;\n
                                        } else {\n
                                            jpc.target = jpc.suspendedEndpoint.element;\n
                                            jpc.targetId = jpc.suspendedEndpoint.elementId;\n
                                        }\n
                                        jpc.suspendedEndpoint.addConnection(jpc);\n
\n
                                        jpc.endpoints[0].repaint();\n
                                        jpc.repaint();\n
                                        _jsPlumb.repaint(jpc.sourceId);\n
                                        jpc._forceDetach = false;\n
                                    }\n
                                    \n
                                    commonFunction();\n
                                };\n
                                \n
// --------------------------------------\n
                                // now check beforeDrop.  this will be available only on Endpoints that are setup to\n
                                // have a beforeDrop condition (although, secretly, under the hood all Endpoints and \n
                                // the Connection have them, because they are on jsPlumbUIComponent.  shhh!), because\n
                                // it only makes sense to have it on a target endpoint.\n
                                _doContinue = _doContinue && this.isDropAllowed(jpc.sourceId, jpc.targetId, jpc.scope, jpc, this);\n
                                                                                                                    \n
                                if (_doContinue) {\n
                                    continueFunction();\n
                                }\n
                                else {\n
                                    dontContinueFunction();\n
                                }\n
                            }\n
                            _jsPlumb.currentlyDragging = false;\n
                        }\n
                    }.bind(this);\n
                \n
                dropOptions[dropEvent] = _ju.wrap(dropOptions[dropEvent], drop);\n
                dropOptions[overEvent] = _ju.wrap(dropOptions[overEvent], function() {\t\t\t\t\t\n
                    var draggable = jsPlumb.getDragObject(arguments),\n
                        id = _jsPlumb.getAttribute(jsPlumb.getDOMElement(draggable), "dragId"),\n
                        _jpc = floatingConnections[id];\n
                        \n
                    if (_jpc != null) {\t\t\t\t\t\t\t\t\n
                        var idx = _jpc.floatingAnchorIndex == null ? 1 : _jpc.floatingAnchorIndex;\n
                        // here we should fire the \'over\' event if we are a target and this is a new connection,\n
                        // or we are the same as the floating endpoint.\t\t\t\t\t\t\t\t\n
                        var _cont = (this.isTarget && _jpc.floatingAnchorIndex !== 0) || (_jpc.suspendedEndpoint && this.referenceEndpoint && this.referenceEndpoint.id == _jpc.suspendedEndpoint.id);\n
                        if (_cont) {\n
                            var bb = _jsPlumb.checkCondition("checkDropAllowed", { \n
                                sourceEndpoint:_jpc.endpoints[idx], \n
                                targetEndpoint:this,\n
                                connection:_jpc\n
                            }); \n
                            this[(bb ? "add" : "remove") + "Class"](_jsPlumb.endpointDropAllowedClass);\n
                            this[(bb ? "remove" : "add") + "Class"](_jsPlumb.endpointDropForbiddenClass);\n
                            _jpc.endpoints[idx].anchor.over(this.anchor, this);\n
                        }\n
                    }\t\t\t\t\t\t\n
                }.bind(this));\t\n
\n
                dropOptions[outEvent] = _ju.wrap(dropOptions[outEvent], function() {\t\t\t\t\t\n
                    var draggable = jsPlumb.getDragObject(arguments),\n
                        id = draggable == null ? null : _jsPlumb.getAttribute( jsPlumb.getDOMElement(draggable), "dragId"),\n
                        _jpc = id? floatingConnections[id] : null;\n
                        \n
                    if (_jpc != null) {\n
                        var idx = _jpc.floatingAnchorIndex == null ? 1 : _jpc.floatingAnchorIndex;\n
                        var _cont = (this.isTarget && _jpc.floatingAnchorIndex !== 0) || (_jpc.suspendedEndpoint && this.referenceEndpoint && this.referenceEndpoint.id == _jpc.suspendedEndpoint.id);\n
                        if (_cont) {\n
                            this.removeClass(_jsPlumb.endpointDropAllowedClass);\n
                            this.removeClass(_jsPlumb.endpointDropForbiddenClass);\n
                            _jpc.endpoints[idx].anchor.out();\n
                        }\n
                    }\n
                }.bind(this));\n
                _jsPlumb.initDroppable(canvas, dropOptions, true, isTransient);\n
            }\n
        }.bind(this);\n
        \n
        // initialise the endpoint\'s canvas as a drop target.  this will be ignored if the endpoint is not a target or drag is not supported.\n
        if (!this.anchor.isFloating)\n
            _initDropTarget(_gel(this.canvas), true, !(params._transient || this.anchor.isFloating), this);\n
        \n
         // finally, set type if it was provided\n
         if (params.type)\n
            this.addType(params.type, params.data, _jsPlumb.isSuspendDrawing());\n
\n
        return this;        \t\t\t\t\t\n
    };\n
\n
    jsPlumbUtil.extend(jsPlumb.Endpoint, OverlayCapableJsPlumbUIComponent, {\n
        getTypeDescriptor : function() { return "endpoint"; },        \n
        isVisible : function() { return this._jsPlumb.visible; },\n
        setVisible : function(v, doNotChangeConnections, doNotNotifyOtherEndpoint) {\n
            this._jsPlumb.visible = v;\n
            if (this.canvas) this.canvas.style.display = v ? "block" : "none";\n
            this[v ? "showOverlays" : "hideOverlays"]();\n
            if (!doNotChangeConnections) {\n
                for (var i = 0; i < this.connections.length; i++) {\n
                    this.connections[i].setVisible(v);\n
                    if (!doNotNotifyOtherEndpoint) {\n
                        var oIdx = this === this.connections[i].endpoints[0] ? 1 : 0;\n
                        // only change the other endpoint if this is its only connection.\n
                        if (this.connections[i].endpoints[oIdx].connections.length == 1) this.connections[i].endpoints[oIdx].setVisible(v, true, true);\n
                    }\n
                }\n
            }\n
        },\n
        getAttachedElements : function() {\n
            return this.connections;\n
        },\n
        applyType : function(t, doNotRepaint) {         \n
            if (t.maxConnections != null) this._jsPlumb.maxConnections = t.maxConnections;\n
            if (t.scope) this.scope = t.scope;\n
            jsPlumb.extend(this, t, typeParameters);\n
            if (t.anchor) {\n
                this.anchor = this._jsPlumb.instance.makeAnchor(t.anchor);\n
            }\n
        },\n
        isEnabled : function() { return this._jsPlumb.enabled; },\n
        setEnabled : function(e) { this._jsPlumb.enabled = e; },\n
        cleanup : function() {            \n
            jsPlumbAdapter.removeClass(this.element, this._jsPlumb.instance.endpointAnchorClassPrefix + "_" + this._jsPlumb.currentAnchorClass);            \n
            this.anchor = null;\n
            this.endpoint.cleanup();\n
            this.endpoint.destroy();\n
            this.endpoint = null;\n
            // drag/drop\n
            var i = jsPlumb.getElementObject(this.canvas);              \n
            this._jsPlumb.instance.destroyDraggable(i);\n
            this._jsPlumb.instance.destroyDroppable(i);\n
        },\n
        setHover : function(h) {\n
            if (this.endpoint && this._jsPlumb && !this._jsPlumb.instance.isConnectionBeingDragged())\n
                this.endpoint.setHover(h);            \n
        },\n
        isFull : function() {\n
            return !(this.isFloating() || this._jsPlumb.maxConnections < 1 || this.connections.length < this._jsPlumb.maxConnections);              \n
        },\n
        /**\n
         * private but needs to be exposed.\n
         */\n
        isFloating : function() {\n
            return this.anchor != null && this.anchor.isFloating;\n
        },\n
        getConnectionCost : function() { return this._jsPlumb.connectionCost; },\n
        setConnectionCost : function(c) {\n
            this._jsPlumb.connectionCost = c; \n
        },\n
        areConnectionsDirected : function() { return this._jsPlumb.connectionsDirected; },\n
        setConnectionsDirected : function(b) { this._jsPlumb.connectionsDirected = b; },\n
        setElementId : function(_elId) {\n
            this.elementId = _elId;\n
            this.anchor.elementId = _elId;\n
        },        \n
        setReferenceElement : function(_el) {\n
            this.element = jsPlumb.getDOMElement(_el);\n
        },\n
        setDragAllowedWhenFull : function(allowed) {\n
            this.dragAllowedWhenFull = allowed;\n
        },\n
        equals : function(endpoint) {\n
            return this.anchor.equals(endpoint.anchor);\n
        },\n
        getUuid : function() {\n
            return this._jsPlumb.uuid;\n
        },\n
        computeAnchor : function(params) {\n
            return this.anchor.compute(params);\n
        }\n
    });\n
})();\n
\n
/*\n
 * jsPlumb\n
 * \n
 * Title:jsPlumb 1.6.2\n
 * \n
 * Provides a way to visually connect elements on an HTML page, using SVG or VML.  \n
 * \n
 * This file contains the code for Connections.\n
 *\n
 * Copyright (c) 2010 - 2014 Simon Porritt (simon@jsplumbtoolkit.com)\n
 * \n
 * http://jsplumbtoolkit.com\n
 * http://github.com/sporritt/jsplumb\n
 * \n
 * Dual licensed under the MIT and GPL2 licenses.\n
 */\n
;(function() {\n
    \n
    "use strict";\n
\n
    var makeConnector = function(_jsPlumb, renderMode, connectorName, connectorArgs) {\n
            if (!_jsPlumb.Defaults.DoNotThrowErrors && jsPlumb.Connectors[renderMode][connectorName] == null)\n
                    throw { msg:"jsPlumb: unknown connector type \'" + connectorName + "\'" };\n
\n
            return new jsPlumb.Connectors[renderMode][connectorName](connectorArgs);  \n
        },\n
        _makeAnchor = function(anchorParams, elementId, _jsPlumb) {\n
            return (anchorParams) ? _jsPlumb.makeAnchor(anchorParams, elementId, _jsPlumb) : null;\n
        };\n
    \n
    jsPlumb.Connection = function(params) {\n
        var _newConnection = params.newConnection,\n
            _newEndpoint = params.newEndpoint,\n
            _gel = jsPlumb.getElementObject,\n
            _ju = jsPlumbUtil;\n
\n
        this.connector = null;\n
        this.idPrefix = "_jsplumb_c_";\n
        this.defaultLabelLocation = 0.5;\n
        this.defaultOverlayKeys = ["Overlays", "ConnectionOverlays"];\n
        // if a new connection is the result of moving some existing connection, params.previousConnection\n
        // will have that Connection in it. listeners for the jsPlumbConnection event can look for that\n
        // member and take action if they need to.\n
        this.previousConnection = params.previousConnection;\n
        this.source = jsPlumb.getDOMElement(params.source);\n
        this.target = jsPlumb.getDOMElement(params.target);\n
        // sourceEndpoint and targetEndpoint override source/target, if they are present. but \n
        // source is not overridden if the Endpoint has declared it is not the final target of a connection;\n
        // instead we use the source that the Endpoint declares will be the final source element.\n
        if (params.sourceEndpoint) this.source = params.sourceEndpoint.endpointWillMoveTo || params.sourceEndpoint.getElement();            \n
        if (params.targetEndpoint) this.target = params.targetEndpoint.getElement();        \n
\n
        OverlayCapableJsPlumbUIComponent.apply(this, arguments);\n
\n
        this.sourceId = this._jsPlumb.instance.getId(this.source);\n
        this.targetId = this._jsPlumb.instance.getId(this.target);\n
        this.scope = params.scope; // scope may have been passed in to the connect call. if it wasn\'t, we will pull it from the source endpoint, after having initialised the endpoints.            \n
        this.endpoints = [];\n
        this.endpointStyles = [];\n
            \n
        var _jsPlumb = this._jsPlumb.instance;\n
        this._jsPlumb.visible = true;\n
        this._jsPlumb.editable = params.editable === true;    \n
        this._jsPlumb.params = {\n
            cssClass:params.cssClass,\n
            container:params.container,\n
            "pointer-events":params["pointer-events"],\n
            editorParams:params.editorParams\n
        };   \n
        this._jsPlumb.lastPaintedAt = null;\n
        this.getDefaultType = function() {\n
            return {\n
                parameters:{},\n
                scope:null,\n
                detachable:this._jsPlumb.instance.Defaults.ConnectionsDetachable,\n
                rettach:this._jsPlumb.instance.Defaults.ReattachConnections,\n
                paintStyle:this._jsPlumb.instance.Defaults.PaintStyle || jsPlumb.Defaults.PaintStyle,\n
                connector:this._jsPlumb.instance.Defaults.Connector || jsPlumb.Defaults.Connector,\n
                hoverPaintStyle:this._jsPlumb.instance.Defaults.HoverPaintStyle || jsPlumb.Defaults.HoverPaintStyle,\n
                overlays:this._jsPlumb.instance.Defaults.ConnectorOverlays || jsPlumb.Defaults.ConnectorOverlays\n
            };\n
        };\n
        \n
// INITIALISATION CODE\t\t\t\n
                            \n
        // wrapped the main function to return null if no input given. this lets us cascade defaults properly.\n
        \n
        this.makeEndpoint = function(isSource, el, elId, ep) {\n
            elId = elId ||  this._jsPlumb.instance.getId(el);\n
            return this.prepareEndpoint(_jsPlumb, _newEndpoint, this, ep, isSource ? 0 : 1, params, el, elId);\n
        };\n
        \n
        var eS = this.makeEndpoint(true, this.source, this.sourceId, params.sourceEndpoint),\n
            eT = this.makeEndpoint(false, this.target, this.targetId, params.targetEndpoint);\n
        \n
        if (eS) _ju.addToList(params.endpointsByElement, this.sourceId, eS);\n
        if (eT) _ju.addToList(params.endpointsByElement, this.targetId, eT);\n
        // if scope not set, set it to be the scope for the source endpoint.\n
        if (!this.scope) this.scope = this.endpoints[0].scope;\n
                \n
        // if explicitly told to (or not to) delete endpoints on detach, override endpoint\'s preferences\n
        if (params.deleteEndpointsOnDetach != null) {\n
            this.endpoints[0]._deleteOnDetach = params.deleteEndpointsOnDetach;\n
            this.endpoints[1]._deleteOnDetach = params.deleteEndpointsOnDetach;\n
        }\n
        else {\n
            // otherwise, unless the endpoints say otherwise, mark them for deletion.\n
            if (!this.endpoints[0]._doNotDeleteOnDetach) this.endpoints[0]._deleteOnDetach = true;\n
            if (!this.endpoints[1]._doNotDeleteOnDetach) this.endpoints[1]._deleteOnDetach = true;\n
        }   \n
                    \n
        // TODO these could surely be refactored into some method that tries them one at a time until something exists\n
        this.setConnector(this.endpoints[0].connector || \n
                          this.endpoints[1].connector || \n
                          params.connector || \n
                          _jsPlumb.Defaults.Connector || \n
                          jsPlumb.Defaults.Connector, true);\n
\n
        if (params.path)\n
            this.connector.setPath(params.path);\n
        \n
        this.setPaintStyle(this.endpoints[0].connectorStyle || \n
                           this.endpoints[1].connectorStyle || \n
                           params.paintStyle || \n
                           _jsPlumb.Defaults.PaintStyle || \n
                           jsPlumb.Defaults.PaintStyle, true);\n
                    \n
        this.setHoverPaintStyle(this.endpoints[0].connectorHoverStyle || \n
                                this.endpoints[1].connectorHoverStyle || \n
                                params.hoverPaintStyle || \n
                                _jsPlumb.Defaults.HoverPaintStyle || \n
                                jsPlumb.Defaults.HoverPaintStyle, true);\n
        \n
        this._jsPlumb.paintStyleInUse = this.getPaintStyle();\n
        \n
        var _suspendedAt = _jsPlumb.getSuspendedAt();\n
        _jsPlumb.updateOffset( { elId : this.sourceId, timestamp:_suspendedAt });\n
        _jsPlumb.updateOffset( { elId : this.targetId, timestamp:_suspendedAt });\n
\n
//*\n
        if(!_jsPlumb.isSuspendDrawing()) {                    \n
            // paint the endpoints\n
            var myInfo = _jsPlumb.getCachedData(this.sourceId),\n
                myOffset = myInfo.o, myWH = myInfo.s,\n
                otherInfo = _jsPlumb.getCachedData(this.targetId),\n
                otherOffset = otherInfo.o,\n
                otherWH = otherInfo.s,\n
                initialTimestamp = _suspendedAt || _jsPlumb.timestamp(),\n
                anchorLoc = this.endpoints[0].anchor.compute( {\n
                    xy : [ myOffset.left, myOffset.top ], wh : myWH, element : this.endpoints[0],\n
                    elementId:this.endpoints[0].elementId,\n
                    txy : [ otherOffset.left, otherOffset.top ], twh : otherWH, tElement : this.endpoints[1],\n
                    timestamp:initialTimestamp\n
                });\n
\n
            this.endpoints[0].paint( { anchorLoc : anchorLoc, timestamp:initialTimestamp });\n
\n
            anchorLoc = this.endpoints[1].anchor.compute( {\n
                xy : [ otherOffset.left, otherOffset.top ], wh : otherWH, element : this.endpoints[1],\n
                elementId:this.endpoints[1].elementId,\t\t\t\t\n
                txy : [ myOffset.left, myOffset.top ], twh : myWH, tElement : this.endpoints[0],\n
                timestamp:initialTimestamp\t\t\t\t\n
            });\n
            this.endpoints[1].paint({ anchorLoc : anchorLoc, timestamp:initialTimestamp });\n
        }\n
        //*/\n
                                \n
// END INITIALISATION CODE\t\t\t\n
        \n
// DETACHABLE \t\t\t\t\n
        this._jsPlumb.detachable = _jsPlumb.Defaults.ConnectionsDetachable;\n
        if (params.detachable === false) this._jsPlumb.detachable = false;\n
        if(this.endpoints[0].connectionsDetachable === false) this._jsPlumb.detachable = false;\n
        if(this.endpoints[1].connectionsDetachable === false) this._jsPlumb.detachable = false;                \n
// REATTACH\n
        this._jsPlumb.reattach = params.reattach || this.endpoints[0].reattachConnections || this.endpoints[1].reattachConnections || _jsPlumb.Defaults.ReattachConnections;\n
// COST + DIRECTIONALITY\n
        // if cost not supplied, try to inherit from source endpoint\n
        this._jsPlumb.cost = params.cost || this.endpoints[0].getConnectionCost();\t\t\t        \n
        this._jsPlumb.directed = params.directed;\n
        // inherit directed flag if set no source endpoint\n
        if (params.directed == null) this._jsPlumb.directed = this.endpoints[0].areConnectionsDirected();        \n
// END COST + DIRECTIONALITY\n
                    \n
// PARAMETERS\t\t\t\t\t\t\n
        // merge all the parameters objects into the connection.  parameters set\n
        // on the connection take precedence; then source endpoint params, then\n
        // finally target endpoint params.\n
        // TODO jsPlumb.extend could be made to take more than two args, and it would\n
        // apply the second through nth args in order.\n
        var _p = jsPlumb.extend({}, this.endpoints[1].getParameters());\n
        jsPlumb.extend(_p, this.endpoints[0].getParameters());\n
        jsPlumb.extend(_p, this.getParameters());\n
        this.setParameters(_p);\n
// END PARAMETERS\n
\n
// PAINTING\n
                  \n
        // the very last thing we do is apply types, if there are any.\n
        var _types = [params.type, this.endpoints[0].connectionType, this.endpoints[1].connectionType ].join(" ");\n
        if (/[^\\s]/.test(_types))\n
            this.addType(_types, params.data, true);        \n
\n
        \n
// END PAINTING    \n
    };\n
\n
    jsPlumbUtil.extend(jsPlumb.Connection, OverlayCapableJsPlumbUIComponent, {\n
        applyType : function(t, doNotRepaint) {            \n
            if (t.detachable != null) this.setDetachable(t.detachable);\n
            if (t.reattach != null) this.setReattach(t.reattach);\n
            if (t.scope) this.scope = t.scope;\n
            //editable = t.editable;  // TODO\n
            this.setConnector(t.connector, doNotRepaint);\n
        },\n
        getTypeDescriptor : function() { return "connection"; },\n
        getAttachedElements : function() {\n
            return this.endpoints;\n
        },\n
        addClass : function(c, informEndpoints) {        \n
            if (informEndpoints) {\n
                this.endpoints[0].addClass(c);\n
                this.endpoints[1].addClass(c); \n
                if (this.suspendedEndpoint) this.suspendedEndpoint.addClass(c);                   \n
            }\n
            if (this.connector) {\n
                this.connector.addClass(c);\n
            }\n
        },\n
        removeClass : function(c, informEndpoints) {            \n
            if (informEndpoints) {\n
                this.endpoints[0].removeClass(c);\n
                this.endpoints[1].removeClass(c);                    \n
                if (this.suspendedEndpoint) this.suspendedEndpoint.removeClass(c);\n
            }\n
            if (this.connector) {\n
                this.connector.removeClass(c);\n
            }\n
        },\n
        isVisible : function() { return this._jsPlumb.visible; },\n
        setVisible : function(v) {\n
            this._jsPlumb.visible = v;\n
            if (this.connector) \n
                this.connector.setVisible(v);\n
            this.repaint();\n
        },\n
        cleanup:function() {\n
            this.endpoints = null;\n
            this.source = null;\n
            this.target = null;                    \n
            if (this.connector != null) {\n
                this.connector.cleanup();            \n
                this.connector.destroy();\n
            }\n
            this.connector = null;\n
        },\n
        isDetachable : function() {\n
            return this._jsPlumb.detachable === true;\n
        },\n
        setDetachable : function(detachable) {\n
          this._jsPlumb.detachable = detachable === true;\n
        },\n
        isReattach : function() {\n
            return this._jsPlumb.reattach === true;\n
        },        \n
        setReattach : function(reattach) {\n
          this._jsPlumb.reattach = reattach === true;\n
        },\n
        setHover : function(state) {\n
            if (this.connector && this._jsPlumb && !this._jsPlumb.instance.isConnectionBeingDragged()) {\n
                this.connector.setHover(state);\n
                jsPlumbAdapter[state ? "addClass" : "removeClass"](this.source, this._jsPlumb.instance.hoverSourceClass);\n
                jsPlumbAdapter[state ? "addClass" : "removeClass"](this.target, this._jsPlumb.instance.hoverTargetClass);\n
            }\n
        },\n
        getCost : function() { return this._jsPlumb.cost; },\n
        setCost : function(c) { this._jsPlumb.cost = c; },\n
        isDirected : function() { return this._jsPlumb.directed === true; },\n
        getConnector : function() { return this.connector; },\n
        setConnector : function(connectorSpec, doNotRepaint) {\n
            var _ju = jsPlumbUtil;\n
            if (this.connector != null) {\n
                this.connector.cleanup();\n
                this.connector.destroy();\n
            }\n
\n
            var connectorArgs = { \n
                    _jsPlumb:this._jsPlumb.instance, \n
                    cssClass:this._jsPlumb.params.cssClass, \n
                    container:this._jsPlumb.params.container,                 \n
                    "pointer-events":this._jsPlumb.params["pointer-events"]\n
                },\n
                renderMode = this._jsPlumb.instance.getRenderMode();\n
            \n
            if (_ju.isString(connectorSpec)) \n
                this.connector = makeConnector(this._jsPlumb.instance, renderMode, connectorSpec, connectorArgs); // lets you use a string as shorthand.\n
            else if (_ju.isArray(connectorSpec)) {\n
                if (connectorSpec.length == 1)\n
                    this.connector = makeConnector(this._jsPlumb.instance, renderMode, connectorSpec[0], connectorArgs);\n
                else\n
                    this.connector = makeConnector(this._jsPlumb.instance, renderMode, connectorSpec[0], _ju.merge(connectorSpec[1], connectorArgs));\n
            }\n
            // binds mouse listeners to the current connector.\n
            this.bindListeners(this.connector, this, function(state) {                \n
                this.setHover(state, false);                \n
            }.bind(this));\n
            \n
            this.canvas = this.connector.canvas;\n
            this.bgCanvas = this.connector.bgCanvas;\n
\n
            if (this._jsPlumb.editable && jsPlumb.ConnectorEditors != null && jsPlumb.ConnectorEditors[this.connector.type] && this.connector.isEditable()) {\n
                new jsPlumb.ConnectorEditors[this.connector.type]({\n
                    connector:this.connector,\n
                    connection:this,\n
                    params:this._jsPlumb.params.editorParams || { }\n
                });\n
            }\n
            else {                    \n
                this._jsPlumb.editable = false;\n
            }                \n
                \n
            if (!doNotRepaint) this.repaint();\n
        },\n
        paint : function(params) {\n
                    \n
            if (!this._jsPlumb.instance.isSuspendDrawing() && this._jsPlumb.visible) {\n
                    \n
                params = params || {};\n
                var elId = params.elId, ui = params.ui, recalc = params.recalc, timestamp = params.timestamp,\n
                    // if the moving object is not the source we must transpose the two references.\n
                    swap = false,\n
                    tId = swap ? this.sourceId : this.targetId, sId = swap ? this.targetId : this.sourceId,                    \n
                    tIdx = swap ? 0 : 1, sIdx = swap ? 1 : 0;\n
\n
                if (timestamp == null || timestamp != this._jsPlumb.lastPaintedAt) {                        \n
                    var sourceInfo = this._jsPlumb.instance.updateOffset( { elId : sId, offset : ui, recalc : recalc, timestamp : timestamp }).o,\n
                        targetInfo = this._jsPlumb.instance.updateOffset( { elId : tId, timestamp : timestamp }).o, // update the target if this is a forced repaint. otherwise, only the source has been moved.\n
                        sE = this.endpoints[sIdx], tE = this.endpoints[tIdx];\n
\n
                    if (params.clearEdits) {\n
                        this._jsPlumb.overlayPositions = null;\n
                        sE.anchor.clearUserDefinedLocation();\n
                        tE.anchor.clearUserDefinedLocation();\n
                        this.connector.setEdited(false);\n
                    }\n
                    \n
                    var sAnchorP = sE.anchor.getCurrentLocation({xy:[sourceInfo.left,sourceInfo.top], wh:[sourceInfo.width, sourceInfo.height], element:sE, timestamp:timestamp}),              \n
                        tAnchorP = tE.anchor.getCurrentLocation({xy:[targetInfo.left,targetInfo.top], wh:[targetInfo.width, targetInfo.height], element:tE, timestamp:timestamp});                                                 \n
                        \n
                    this.connector.resetBounds();\n
\n
                    this.connector.compute({\n
                        sourcePos:sAnchorP,\n
                        targetPos:tAnchorP, \n
                        sourceEndpoint:this.endpoints[sIdx],\n
                        targetEndpoint:this.endpoints[tIdx],\n
                        lineWidth:this._jsPlumb.paintStyleInUse.lineWidth,                                          \n
                        sourceInfo:sourceInfo,\n
                        targetInfo:targetInfo,\n
                        clearEdits:params.clearEdits === true\n
                    });                                                                                        \n
\n
                    var overlayExtents = { minX:Infinity, minY:Infinity, maxX:-Infinity, maxY:-Infinity };\n
                                        \n
                    // compute overlays. we do this first so we can get their placements, and adjust the\n
                    // container if needs be (if an overlay would be clipped)\n
                    for ( var i = 0; i < this._jsPlumb.overlays.length; i++) {\n
                        var o = this._jsPlumb.overlays[i];\n
                        if (o.isVisible()) {                            \n
                            this._jsPlumb.overlayPlacements[i] = o.draw(this.connector, this._jsPlumb.paintStyleInUse, this.getAbsoluteOverlayPosition(o));\n
                            overlayExtents.minX = Math.min(overlayExtents.minX, this._jsPlumb.overlayPlacements[i].minX);\n
                            overlayExtents.maxX = Math.max(overlayExtents.maxX, this._jsPlumb.overlayPlacements[i].maxX);\n
                            overlayExtents.minY = Math.min(overlayExtents.minY, this._jsPlumb.overlayPlacements[i].minY);\n
                            overlayExtents.maxY = Math.max(overlayExtents.maxY, this._jsPlumb.overlayPlacements[i].maxY);\n
                        }\n
                    }\n
\n
                    var lineWidth = parseFloat(this._jsPlumb.paintStyleInUse.lineWidth || 1) / 2,\n
                        outlineWidth = parseFloat(this._jsPlumb.paintStyleInUse.lineWidth || 0),\n
                        extents = {\n
                            xmin : Math.min(this.connector.bounds.minX - (lineWidth + outlineWidth), overlayExtents.minX),\n
                            ymin : Math.min(this.connector.bounds.minY - (lineWidth + outlineWidth), overlayExtents.minY),\n
                            xmax : Math.max(this.connector.bounds.maxX + (lineWidth + outlineWidth), overlayExtents.maxX),\n
                            ymax : Math.max(this.connector.bounds.maxY + (lineWidth + outlineWidth), overlayExtents.maxY)\n
                        };\n
\n
                    // paint the connector.\n
                    this.connector.paint(this._jsPlumb.paintStyleInUse, null, extents);  \n
                    // and then the overlays\n
                    for ( var j = 0; j < this._jsPlumb.overlays.length; j++) {\n
                        var p = this._jsPlumb.overlays[j];\n
                        if (p.isVisible()) {\n
                            p.paint(this._jsPlumb.overlayPlacements[j], extents);    \n
                        }\n
                    }\n
                }\n
                this._jsPlumb.lastPaintedAt = timestamp;\n
            }\n
        },\n
        /*\n
         * Function: repaint\n
         * Repaints the Connection. No parameters exposed to public API.\n
         */\n
        repaint : function(params) {\n
            params = params || {};            \n
            this.paint({ elId : this.sourceId, recalc : !(params.recalc === false), timestamp:params.timestamp, clearEdits:params.clearEdits });\n
        },\n
        prepareEndpoint : function(_jsPlumb, _newEndpoint, conn, existing, index, params, element, elementId) {\n
            var e;\n
            if (existing) {\n
                conn.endpoints[index] = existing;\n
                existing.addConnection(conn);                   \n
            } else {\n
                if (!params.endpoints) params.endpoints = [ null, null ];\n
                var ep = params.endpoints[index]  || params.endpoint || _jsPlumb.Defaults.Endpoints[index] || jsPlumb.Defaults.Endpoints[index] || _jsPlumb.Defaults.Endpoint || jsPlumb.Defaults.Endpoint;\n
                if (!params.endpointStyles) params.endpointStyles = [ null, null ];\n
                if (!params.endpointHoverStyles) params.endpointHoverStyles = [ null, null ];\n
                var es = params.endpointStyles[index] || params.endpointStyle || _jsPlumb.Defaults.EndpointStyles[index] || jsPlumb.Defaults.EndpointStyles[index] || _jsPlumb.Defaults.EndpointStyle || jsPlumb.Defaults.EndpointStyle;\n
                // Endpoints derive their fillStyle from the connector\'s strokeStyle, if no fillStyle was specified.\n
                if (es.fillStyle == null && params.paintStyle != null)\n
                    es.fillStyle = params.paintStyle.strokeStyle;\n
                \n
                // TODO: decide if the endpoint should derive the connection\'s outline width and color.  currently it does:\n
                //*\n
                if (es.outlineColor == null && params.paintStyle !

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAU=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="5" aka="AAAAAAAAAAU=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

= null) \n
                    es.outlineColor = params.paintStyle.outlineColor;\n
                if (es.outlineWidth == null && params.paintStyle != null) \n
                    es.outlineWidth = params.paintStyle.outlineWidth;\n
                //*/\n
                \n
                var ehs = params.endpointHoverStyles[index] || params.endpointHoverStyle || _jsPlumb.Defaults.EndpointHoverStyles[index] || jsPlumb.Defaults.EndpointHoverStyles[index] || _jsPlumb.Defaults.EndpointHoverStyle || jsPlumb.Defaults.EndpointHoverStyle;\n
                // endpoint hover fill style is derived from connector\'s hover stroke style.  TODO: do we want to do this by default? for sure?\n
                if (params.hoverPaintStyle != null) {\n
                    if (ehs == null) ehs = {};\n
                    if (ehs.fillStyle == null) {\n
                        ehs.fillStyle = params.hoverPaintStyle.strokeStyle;\n
                    }\n
                }\n
                var a = params.anchors ? params.anchors[index] : \n
                        params.anchor ? params.anchor :\n
                        _makeAnchor(_jsPlumb.Defaults.Anchors[index], elementId, _jsPlumb) || \n
                        _makeAnchor(jsPlumb.Defaults.Anchors[index], elementId,_jsPlumb) || \n
                        _makeAnchor(_jsPlumb.Defaults.Anchor, elementId,_jsPlumb) || \n
                        _makeAnchor(jsPlumb.Defaults.Anchor, elementId, _jsPlumb),                  \n
                    u = params.uuids ? params.uuids[index] : null;\n
                    \n
                e = _newEndpoint({ \n
                    paintStyle : es,  hoverPaintStyle:ehs,  endpoint : ep,  connections : [ conn ], \n
                    uuid : u,  anchor : a,  source : element, scope  : params.scope,\n
                    reattach:params.reattach || _jsPlumb.Defaults.ReattachConnections,\n
                    detachable:params.detachable || _jsPlumb.Defaults.ConnectionsDetachable\n
                });\n
                conn.endpoints[index] = e;\n
                \n
                if (params.drawEndpoints === false) e.setVisible(false, true, true);\n
                                    \n
            }\n
            return e;\n
        }\n
        \n
    }); // END Connection class            \n
})();\n
/*\n
 * jsPlumb\n
 * \n
 * Title:jsPlumb 1.6.2\n
 * \n
 * Provides a way to visually connect elements on an HTML page, using SVG or VML.  \n
 * \n
 * This file contains the code for creating and manipulating anchors.\n
 *\n
 * Copyright (c) 2010 - 2014 Simon Porritt (simon@jsplumbtoolkit.com)\n
 * \n
 * http://jsplumbtoolkit.com\n
 * http://github.com/sporritt/jsplumb\n
 * \n
 * Dual licensed under the MIT and GPL2 licenses.\n
 */\n
;(function() {\t\n
    \n
    //\n
\t// manages anchors for all elements.\n
\t//\n
\tjsPlumb.AnchorManager = function(params) {\n
\t\tvar _amEndpoints = {},\n
            continuousAnchors = {},\n
            continuousAnchorLocations = {},\n
            userDefinedContinuousAnchorLocations = {},        \n
            continuousAnchorOrientations = {},\n
            Orientation = { HORIZONTAL : "horizontal", VERTICAL : "vertical", DIAGONAL : "diagonal", IDENTITY:"identity" },\n
\t\t\tconnectionsByElementId = {},\n
\t\t\tself = this,\n
            anchorLists = {},\n
            jsPlumbInstance = params.jsPlumbInstance,\n
            floatingConnections = {},\n
            // TODO this functions uses a crude method of determining orientation between two elements.\n
            // \'diagonal\' should be chosen when the angle of the line between the two centers is around\n
            // one of 45, 135, 225 and 315 degrees. maybe +- 15 degrees.\n
            // used by AnchorManager.redraw\n
            calculateOrientation = function(sourceId, targetId, sd, td, sourceAnchor, targetAnchor) {\n
        \n
                if (sourceId === targetId) return {\n
                    orientation:Orientation.IDENTITY,\n
                    a:["top", "top"]\n
                };\n
        \n
                var theta = Math.atan2((td.centery - sd.centery) , (td.centerx - sd.centerx)),\n
                    theta2 = Math.atan2((sd.centery - td.centery) , (sd.centerx - td.centerx)),\n
                    h = ((sd.left <= td.left && sd.right >= td.left) || (sd.left <= td.right && sd.right >= td.right) ||\n
                        (sd.left <= td.left && sd.right >= td.right) || (td.left <= sd.left && td.right >= sd.right)),\n
                    v = ((sd.top <= td.top && sd.bottom >= td.top) || (sd.top <= td.bottom && sd.bottom >= td.bottom) ||\n
                        (sd.top <= td.top && sd.bottom >= td.bottom) || (td.top <= sd.top && td.bottom >= sd.bottom)),\n
                    possiblyTranslateEdges = function(edges) {\n
                        // this function checks to see if either anchor is Continuous, and if so, runs the suggested edge\n
                        // through the anchor: Continuous anchors can say which faces they support, and they get to choose \n
                        // whether a certain face is honoured, or, if not, which face to replace it with. the behaviour when\n
                        // choosing an alternate face is to try for the opposite face first, then the next one clockwise, and then\n
                        // the opposite of that one.\n
                        return [\n
                            sourceAnchor.isContinuous ? sourceAnchor.verifyEdge(edges[0]) : edges[0],    \n
                            targetAnchor.isContinuous ? targetAnchor.verifyEdge(edges[1]) : edges[1]\n
                        ];\n
                    },\n
                    out = {\n
                        orientation:Orientation.DIAGONAL,\n
                        theta:theta,\n
                        theta2:theta2\n
                    };                        \n
                \n
                if (! (h || v)) {                    \n
                    if (td.left > sd.left && td.top > sd.top)\n
                        out.a = ["right", "top"];\n
                    else if (td.left > sd.left && sd.top > td.top)\n
                        out.a = [ "top", "left"];\n
                    else if (td.left < sd.left && td.top < sd.top)\n
                        out.a = [ "top", "right"];\n
                    else if (td.left < sd.left && td.top > sd.top)\n
                        out.a = ["left", "top" ];                            \n
                }\n
                else if (h) {\n
                    out.orientation = Orientation.HORIZONTAL;\n
                    out.a = sd.top < td.top ? ["bottom", "top"] : ["top", "bottom"];                    \n
                }\n
                else {\n
                    out.orientation = Orientation.VERTICAL;\n
                    out.a = sd.left < td.left ? ["right", "left"] : ["left", "right"];\n
                }\n
                \n
                out.a = possiblyTranslateEdges(out.a);\n
                return out;\n
            },\n
                // used by placeAnchors function\n
            placeAnchorsOnLine = function(desc, elementDimensions, elementPosition,\n
                            connections, horizontal, otherMultiplier, reverse) {\n
                var a = [], step = elementDimensions[horizontal ? 0 : 1] / (connections.length + 1);\n
        \n
                for (var i = 0; i < connections.length; i++) {\n
                    var val = (i + 1) * step, other = otherMultiplier * elementDimensions[horizontal ? 1 : 0];\n
                    if (reverse)\n
                      val = elementDimensions[horizontal ? 0 : 1] - val;\n
        \n
                    var dx = (horizontal ? val : other), x = elementPosition[0] + dx,  xp = dx / elementDimensions[0],\n
                        dy = (horizontal ? other : val), y = elementPosition[1] + dy, yp = dy / elementDimensions[1];\n
        \n
                    a.push([ x, y, xp, yp, connections[i][1], connections[i][2] ]);\n
                }\n
        \n
                return a;\n
            },\n
            // used by edgeSortFunctions        \n
            currySort = function(reverseAngles) {\n
                return function(a,b) {\n
                    var r = true;\n
                    if (reverseAngles) {\n
                        /*if (a[0][0] < b[0][0])\n
                            r = true;\n
                        else\n
                            r = a[0][1] > b[0][1];*/\n
                        r = a[0][0] < b[0][0];\n
                    }\n
                    else {\n
                        /*if (a[0][0] > b[0][0])\n
                            r= true;\n
                        else\n
                            r =a[0][1] > b[0][1];\n
                        */\n
                        r = a[0][0] > b[0][0];\n
                    }\n
                    return r === false ? -1 : 1;\n
                };\n
            },\n
                // used by edgeSortFunctions\n
            leftSort = function(a,b) {\n
                // first get adjusted values\n
                var p1 = a[0][0] < 0 ? -Math.PI - a[0][0] : Math.PI - a[0][0],\n
                p2 = b[0][0] < 0 ? -Math.PI - b[0][0] : Math.PI - b[0][0];\n
                if (p1 > p2) return 1;\n
                else return a[0][1] > b[0][1] ? 1 : -1;\n
            },\n
                // used by placeAnchors\n
            edgeSortFunctions = {\n
                "top":function(a, b) { return a[0] > b[0] ? 1 : -1; },\n
                "right":currySort(true),\n
                "bottom":currySort(true),\n
                "left":leftSort\n
            },\n
                // used by placeAnchors\n
            _sortHelper = function(_array, _fn) { return _array.sort(_fn); },\n
                // used by AnchorManager.redraw\n
            placeAnchors = function(elementId, _anchorLists) {\t\t\n
                var cd = jsPlumbInstance.getCachedData(elementId), sS = cd.s, sO = cd.o,\n
                placeSomeAnchors = function(desc, elementDimensions, elementPosition, unsortedConnections, isHorizontal, otherMultiplier, orientation) {\n
                    if (unsortedConnections.length > 0) {\n
                        var sc = _sortHelper(unsortedConnections, edgeSortFunctions[desc]), // puts them in order based on the target element\'s pos on screen\n
                            reverse = desc === "right" || desc === "top",\n
                            anchors = placeAnchorsOnLine(desc, elementDimensions,\n
                                                     elementPosition, sc,\n
                                                     isHorizontal, otherMultiplier, reverse );\n
        \n
                        // takes a computed anchor position and adjusts it for parent offset and scroll, then stores it.\n
                        var _setAnchorLocation = function(endpoint, anchorPos) {                            \n
                            continuousAnchorLocations[endpoint.id] = [ anchorPos[0], anchorPos[1], anchorPos[2], anchorPos[3] ];\n
                            continuousAnchorOrientations[endpoint.id] = orientation;\n
                        };\n
        \n
                        for (var i = 0; i < anchors.length; i++) {\n
                            var c = anchors[i][4], weAreSource = c.endpoints[0].elementId === elementId, weAreTarget = c.endpoints[1].elementId === elementId;\n
                            if (weAreSource)\n
                                _setAnchorLocation(c.endpoints[0], anchors[i]);\n
                            else if (weAreTarget)\n
                                _setAnchorLocation(c.endpoints[1], anchors[i]);\n
                        }\n
                    }\n
                };\n
        \n
                placeSomeAnchors("bottom", sS, [sO.left,sO.top], _anchorLists.bottom, true, 1, [0,1]);\n
                placeSomeAnchors("top", sS, [sO.left,sO.top], _anchorLists.top, true, 0, [0,-1]);\n
                placeSomeAnchors("left", sS, [sO.left,sO.top], _anchorLists.left, false, 0, [-1,0]);\n
                placeSomeAnchors("right", sS, [sO.left,sO.top], _anchorLists.right, false, 1, [1,0]);\n
            };\n
\n
        this.reset = function() {\n
            _amEndpoints = {};\n
            connectionsByElementId = {};\n
            anchorLists = {};\n
        };\t\t\t\n
        this.addFloatingConnection = function(key, conn) {\n
            floatingConnections[key] = conn;\n
        };\n
        this.removeFloatingConnection = function(key) {\n
            delete floatingConnections[key];\n
        };                                                 \n
        this.newConnection = function(conn) {\n
\t\t\tvar sourceId = conn.sourceId, targetId = conn.targetId,\n
\t\t\t\tep = conn.endpoints,\n
                doRegisterTarget = true,\n
                registerConnection = function(otherIndex, otherEndpoint, otherAnchor, elId, c) {\n
\t\t\t\t\tif ((sourceId == targetId) && otherAnchor.isContinuous){\n
                       // remove the target endpoint\'s canvas.  we dont need it.\n
                        conn._jsPlumb.instance.removeElement(ep[1].canvas);\n
                        doRegisterTarget = false;\n
                    }\n
\t\t\t\t\tjsPlumbUtil.addToList(connectionsByElementId, elId, [c, otherEndpoint, otherAnchor.constructor == jsPlumb.DynamicAnchor]);\n
\t\t\t    };\n
\n
\t\t\tregisterConnection(0, ep[0], ep[0].anchor, targetId, conn);\n
            if (doRegisterTarget)\n
            \tregisterConnection(1, ep[1], ep[1].anchor, sourceId, conn);\n
\t\t};\n
        var removeEndpointFromAnchorLists = function(endpoint) {\n
            (function(list, eId) {\n
                if (list) {  // transient anchors dont get entries in this list.\n
                    var f = function(e) { return e[4] == eId; };\n
                    jsPlumbUtil.removeWithFunction(list.top, f);\n
                    jsPlumbUtil.removeWithFunction(list.left, f);\n
                    jsPlumbUtil.removeWithFunction(list.bottom, f);\n
                    jsPlumbUtil.removeWithFunction(list.right, f);\n
                }\n
            })(anchorLists[endpoint.elementId], endpoint.id);\n
        };\n
\t\tthis.connectionDetached = function(connInfo) {\n
            var connection = connInfo.connection || connInfo,\n
\t\t\t    sourceId = connInfo.sourceId,\n
                targetId = connInfo.targetId,\n
\t\t\t\tep = connection.endpoints,\n
\t\t\t\tremoveConnection = function(otherIndex, otherEndpoint, otherAnchor, elId, c) {\n
\t\t\t\t\tif (otherAnchor != null && otherAnchor.constructor == jsPlumb.FloatingAnchor) {\n
\t\t\t\t\t\t// no-op\n
\t\t\t\t\t}\n
\t\t\t\t\telse {\n
\t\t\t\t\t\tjsPlumbUtil.removeWithFunction(connectionsByElementId[elId], function(_c) {\n
\t\t\t\t\t\t\treturn _c[0].id == c.id;\n
\t\t\t\t\t\t});\n
\t\t\t\t\t}\n
\t\t\t\t};\n
\t\t\t\t\n
\t\t\tremoveConnection(1, ep[1], ep[1].anchor, sourceId, connection);\n
\t\t\tremoveConnection(0, ep[0], ep[0].anchor, targetId, connection);\n
\n
            // remove from anchorLists            \n
            removeEndpointFromAnchorLists(connection.endpoints[0]);\n
            removeEndpointFromAnchorLists(connection.endpoints[1]);\n
\n
            self.redraw(connection.sourceId);\n
            self.redraw(connection.targetId);\n
\t\t};\n
\t\tthis.add = function(endpoint, elementId) {\n
\t\t\tjsPlumbUtil.addToList(_amEndpoints, elementId, endpoint);\n
\t\t};\n
\t\tthis.changeId = function(oldId, newId) {\n
\t\t\tconnectionsByElementId[newId] = connectionsByElementId[oldId];\n
\t\t\t_amEndpoints[newId] = _amEndpoints[oldId];\n
\t\t\tdelete connectionsByElementId[oldId];\n
\t\t\tdelete _amEndpoints[oldId];\t\n
\t\t};\n
\t\tthis.getConnectionsFor = function(elementId) {\n
\t\t\treturn connectionsByElementId[elementId] || [];\n
\t\t};\n
\t\tthis.getEndpointsFor = function(elementId) {\n
\t\t\treturn _amEndpoints[elementId] || [];\n
\t\t};\n
\t\tthis.deleteEndpoint = function(endpoint) {\n
\t\t\tjsPlumbUtil.removeWithFunction(_amEndpoints[endpoint.elementId], function(e) {\n
\t\t\t\treturn e.id == endpoint.id;\n
\t\t\t});\n
            removeEndpointFromAnchorLists(endpoint);\n
\t\t};\n
\t\tthis.clearFor = function(elementId) {\n
\t\t\tdelete _amEndpoints[elementId];\n
\t\t\t_amEndpoints[elementId] = [];\n
\t\t};\n
        // updates the given anchor list by either updating an existing anchor\'s info, or adding it. this function\n
        // also removes the anchor from its previous list, if the edge it is on has changed.\n
        // all connections found along the way (those that are connected to one of the faces this function\n
        // operates on) are added to the connsToPaint list, as are their endpoints. in this way we know to repaint\n
        // them wthout having to calculate anything else about them.\n
        var _updateAnchorList = function(lists, theta, order, conn, aBoolean, otherElId, idx, reverse, edgeId, elId, connsToPaint, endpointsToPaint) {        \n
            // first try to find the exact match, but keep track of the first index of a matching element id along the way.s\n
            var exactIdx = -1,\n
                firstMatchingElIdx = -1,\n
                endpoint = conn.endpoints[idx],\n
                endpointId = endpoint.id,\n
                oIdx = [1,0][idx],\n
                values = [ [ theta, order ], conn, aBoolean, otherElId, endpointId ],\n
                listToAddTo = lists[edgeId],\n
                listToRemoveFrom = endpoint._continuousAnchorEdge ? lists[endpoint._continuousAnchorEdge] : null;\n
\n
            if (listToRemoveFrom) {\n
                var rIdx = jsPlumbUtil.findWithFunction(listToRemoveFrom, function(e) { return e[4] == endpointId; });\n
                if (rIdx != -1) {\n
                    listToRemoveFrom.splice(rIdx, 1);\n
                    // get all connections from this list\n
                    for (var i = 0; i < listToRemoveFrom.length; i++) {\n
                        jsPlumbUtil.addWithFunction(connsToPaint, listToRemoveFrom[i][1], function(c) { return c.id == listToRemoveFrom[i][1].id; });\n
                        jsPlumbUtil.addWithFunction(endpointsToPaint, listToRemoveFrom[i][1].endpoints[idx], function(e) { return e.id == listToRemoveFrom[i][1].endpoints[idx].id; });\n
                        jsPlumbUtil.addWithFunction(endpointsToPaint, listToRemoveFrom[i][1].endpoints[oIdx], function(e) { return e.id == listToRemoveFrom[i][1].endpoints[oIdx].id; });\n
                    }\n
                }\n
            }\n
\n
            for (i = 0; i < listToAddTo.length; i++) {\n
                if (params.idx == 1 && listToAddTo[i][3] === otherElId && firstMatchingElIdx == -1)\n
                    firstMatchingElIdx = i;\n
                jsPlumbUtil.addWithFunction(connsToPaint, listToAddTo[i][1], function(c) { return c.id == listToAddTo[i][1].id; });                \n
                jsPlumbUtil.addWithFunction(endpointsToPaint, listToAddTo[i][1].endpoints[idx], function(e) { return e.id == listToAddTo[i][1].endpoints[idx].id; });\n
                jsPlumbUtil.addWithFunction(endpointsToPaint, listToAddTo[i][1].endpoints[oIdx], function(e) { return e.id == listToAddTo[i][1].endpoints[oIdx].id; });\n
            }\n
            if (exactIdx != -1) {\n
                listToAddTo[exactIdx] = values;\n
            }\n
            else {\n
                var insertIdx = reverse ? firstMatchingElIdx != -1 ? firstMatchingElIdx : 0 : listToAddTo.length; // of course we will get this from having looked through the array shortly.\n
                listToAddTo.splice(insertIdx, 0, values);\n
            }\n
\n
            // store this for next time.\n
            endpoint._continuousAnchorEdge = edgeId;\n
        };\n
\n
        //\n
        // find the entry in an endpoint\'s list for this connection and update its target endpoint\n
        // with the current target in the connection.\n
        // \n
        //\n
        this.updateOtherEndpoint = function(elId, oldTargetId, newTargetId, connection) {\n
            var sIndex = jsPlumbUtil.findWithFunction(connectionsByElementId[elId], function(i) {\n
                    return i[0].id === connection.id;\n
                }),\n
                tIndex = jsPlumbUtil.findWithFunction(connectionsByElementId[oldTargetId], function(i) {\n
                    return i[0].id === connection.id;\n
                });\n
\n
            // update or add data for source\n
            if (sIndex != -1) {\n
                connectionsByElementId[elId][sIndex][0] = connection;\n
                connectionsByElementId[elId][sIndex][1] = connection.endpoints[1];\n
                connectionsByElementId[elId][sIndex][2] = connection.endpoints[1].anchor.constructor == jsPlumb.DynamicAnchor;\n
            }\n
\n
            // remove entry for previous target (if there)\n
            if (tIndex > -1) {\n
\n
                connectionsByElementId[oldTargetId].splice(tIndex, 1);\n
                // add entry for new target\n
                jsPlumbUtil.addToList(connectionsByElementId, newTargetId, [connection, connection.endpoints[0], connection.endpoints[0].anchor.constructor == jsPlumb.DynamicAnchor]);         \n
            }\n
        };       \n
        \n
        //\n
        // notification that the connection given has changed source from the originalId to the newId.\n
        // This involves:\n
        // 1. removing the connection from the list of connections stored for the originalId\n
        // 2. updating the source information for the target of the connection\n
        // 3. re-registering the connection in connectionsByElementId with the newId\n
        //\n
        this.sourceChanged = function(originalId, newId, connection) {        \n
            if (originalId !== newId) {    \n
                // remove the entry that points from the old source to the target\n
                jsPlumbUtil.removeWithFunction(connectionsByElementId[originalId], function(info) {\n
                    return info[0].id === connection.id;\n
                });\n
                // find entry for target and update it\n
                var tIdx = jsPlumbUtil.findWithFunction(connectionsByElementId[connection.targetId], function(i) {\n
                    return i[0].id === connection.id;\n
                });\n
                if (tIdx > -1) {\n
                    connectionsByElementId[connection.targetId][tIdx][0] = connection;\n
                    connectionsByElementId[connection.targetId][tIdx][1] = connection.endpoints[0];\n
                    connectionsByElementId[connection.targetId][tIdx][2] = connection.endpoints[0].anchor.constructor == jsPlumb.DynamicAnchor;\n
                }\n
                // add entry for new source\n
                jsPlumbUtil.addToList(connectionsByElementId, newId, [connection, connection.endpoints[1], connection.endpoints[1].anchor.constructor == jsPlumb.DynamicAnchor]);         \n
            }\n
        };\n
\n
        //\n
        // moves the given endpoint from `currentId` to `element`.\n
        // This involves:\n
        //\n
        // 1. changing the key in _amEndpoints under which the endpoint is stored\n
        // 2. changing the source or target values in all of the endpoint\'s connections\n
        // 3. changing the array in connectionsByElementId in which the endpoint\'s connections\n
        //    are stored (done by either sourceChanged or updateOtherEndpoint)\n
        //\n
        this.rehomeEndpoint = function(ep, currentId, element) {\n
            var eps = _amEndpoints[currentId] || [], \n
                elementId = jsPlumbInstance.getId(element);\n
                \n
            if (elementId !== currentId) {\n
                var idx = jsPlumbUtil.indexOf(eps, ep);\n
                if (idx > -1) {\n
                    var _ep = eps.splice(idx, 1)[0];\n
                    self.add(_ep, elementId);\n
                }\n
            }\n
\n
            for (var i = 0; i < ep.connections.length; i++) {                \n
                if (ep.connections[i].sourceId == currentId) {\n
                    ep.connections[i].sourceId = ep.elementId;\n
                    ep.connections[i].source = ep.element;                  \n
                    self.sourceChanged(currentId, ep.elementId, ep.connections[i]);\n
                }\n
                else if(ep.connections[i].targetId == currentId) {\n
                    ep.connections[i].targetId = ep.elementId;\n
                    ep.connections[i].target = ep.element;   \n
                    self.updateOtherEndpoint(ep.connections[i].sourceId, currentId, ep.elementId, ep.connections[i]);               \n
                }\n
            }   \n
        };\n
\n
\t\tthis.redraw = function(elementId, ui, timestamp, offsetToUI, clearEdits, doNotRecalcEndpoint) {\n
\t\t\n
\t\t\tif (!jsPlumbInstance.isSuspendDrawing()) {\n
\t\t\t\t// get all the endpoints for this element\n
\t\t\t\tvar ep = _amEndpoints[elementId] || [],\n
\t\t\t\t\tendpointConnections = connectionsByElementId[elementId] || [],\n
\t\t\t\t\tconnectionsToPaint = [],\n
\t\t\t\t\tendpointsToPaint = [],\n
\t                anchorsToUpdate = [];\n
\t            \n
\t\t\t\ttimestamp = timestamp || jsPlumbInstance.timestamp();\n
\t\t\t\t// offsetToUI are values that would have been calculated in the dragManager when registering\n
\t\t\t\t// an endpoint for an element that had a parent (somewhere in the hierarchy) that had been\n
\t\t\t\t// registered as draggable.\n
\t\t\t\toffsetToUI = offsetToUI || {left:0, top:0};\n
\t\t\t\tif (ui) {\n
\t\t\t\t\tui = {\n
\t\t\t\t\t\tleft:ui.left + offsetToUI.left,\n
\t\t\t\t\t\ttop:ui.top + offsetToUI.top\n
\t\t\t\t\t};\n
\t\t\t\t}\n
\t\t\t\t\t\t\t\t\t\n
\t\t\t\t// valid for one paint cycle.\n
\t\t\t\tvar myOffset = jsPlumbInstance.updateOffset( { elId : elementId, offset : ui, recalc : false, timestamp : timestamp }),\n
\t                orientationCache = {};\n
\t\t\t\t\n
\t\t\t\t// actually, first we should compute the orientation of this element to all other elements to which\n
\t\t\t\t// this element is connected with a continuous anchor (whether both ends of the connection have\n
\t\t\t\t// a continuous anchor or just one)\n
\t                        \n
\t            for (var i = 0; i < endpointConnections.length; i++) {\n
\t                var conn = endpointConnections[i][0],\n
\t\t\t\t\t\tsourceId = conn.sourceId,\n
\t                    targetId = conn.targetId,\n
\t                    sourceContinuous = conn.endpoints[0].anchor.isContinuous,\n
\t                    targetContinuous = conn.endpoints[1].anchor.isContinuous;\n
\t\n
\t                if (sourceContinuous || targetContinuous) {\n
\t\t                var oKey = sourceId + "_" + targetId,\n
\t\t                    oKey2 = targetId + "_" + sourceId,\n
\t\t                    o = orientationCache[oKey],\n
\t\t                    oIdx = conn.sourceId == elementId ? 1 : 0;\n
\t\n
\t\t                if (sourceContinuous && !anchorLists[sourceId]) anchorLists[sourceId] = { top:[], right:[], bottom:[], left:[] };\n
\t\t                if (targetContinuous && !anchorLists[targetId]) anchorLists[targetId] = { top:[], right:[], bottom:[], left:[] };\n
\t\n
\t\t                if (elementId != targetId) jsPlumbInstance.updateOffset( { elId : targetId, timestamp : timestamp }); \n
\t\t                if (elementId != sourceId) jsPlumbInstance.updateOffset( { elId : sourceId, timestamp : timestamp }); \n
\t\n
\t\t                var td = jsPlumbInstance.getCachedData(targetId),\n
\t\t\t\t\t\t\tsd = jsPlumbInstance.getCachedData(sourceId);\n
\t\n
\t\t                if (targetId == sourceId && (sourceContinuous || targetContinuous)) {\n
\t\t                    // here we may want to improve this by somehow determining the face we\'d like\n
\t\t\t\t\t\t    // to put the connector on.  ideally, when drawing, the face should be calculated\n
\t\t\t\t\t\t    // by determining which face is closest to the point at which the mouse button\n
\t\t\t\t\t\t\t// was released.  for now, we\'re putting it on the top face.                            \n
\t\t                    _updateAnchorList(\n
                                anchorLists[sourceId], \n
                                -Math.PI / 2, \n
                                0, \n
                                conn, \n
                                false, \n
                                targetId, \n
                                0, false, "top", sourceId, connectionsToPaint, endpointsToPaint);\n
\t\t\t\t\t\t}\n
\t\t                else {\n
\t\t                    if (!o) {\n
\t\t                        o = calculateOrientation(sourceId, targetId, sd.o, td.o, conn.endpoints[0].anchor, conn.endpoints[1].anchor);\n
\t\t                        orientationCache[oKey] = o;\n
\t\t                        // this would be a performance enhancement, but the computed angles need to be clamped to\n
\t\t                        //the (-PI/2 -> PI/2) range in order for the sorting to work properly.\n
\t\t                    /*  orientationCache[oKey2] = {\n
\t\t                            orientation:o.orientation,\n
\t\t                            a:[o.a[1], o.a[0]],\n
\t\t                            theta:o.theta + Math.PI,\n
\t\t                            theta2:o.theta2 + Math.PI\n
\t\t                        };*/\n
\t\t                    }\n
\t\t                    if (sourceContinuous) _updateAnchorList(anchorLists[sourceId], o.theta, 0, conn, false, targetId, 0, false, o.a[0], sourceId, connectionsToPaint, endpointsToPaint);\n
\t\t                    if (targetContinuous) _updateAnchorList(anchorLists[targetId], o.theta2, -1, conn, true, sourceId, 1, true, o.a[1], targetId, connectionsToPaint, endpointsToPaint);\n
\t\t                }\n
\t\n
\t\t                if (sourceContinuous) jsPlumbUtil.addWithFunction(anchorsToUpdate, sourceId, function(a) { return a === sourceId; });\n
\t\t                if (targetContinuous) jsPlumbUtil.addWithFunction(anchorsToUpdate, targetId, function(a) { return a === targetId; });\n
\t\t                jsPlumbUtil.addWithFunction(connectionsToPaint, conn, function(c) { return c.id == conn.id; });\n
\t\t                if ((sourceContinuous && oIdx === 0) || (targetContinuous && oIdx === 1))\n
\t\t                \tjsPlumbUtil.addWithFunction(endpointsToPaint, conn.endpoints[oIdx], function(e) { return e.id == conn.endpoints[oIdx].id; });\n
\t\t            }\n
\t            }\t\t\t\t\n
\t\t\t\t// place Endpoints whose anchors are continuous but have no Connections\n
\t\t\t\tfor (i = 0; i < ep.length; i++) {\n
\t\t\t\t\tif (ep[i].connections.length === 0 && ep[i].anchor.isContinuous) {\n
\t\t\t\t\t\tif (!anchorLists[elementId]) anchorLists[elementId] = { top:[], right:[], bottom:[], left:[] };\n
\t\t\t\t\t\t_updateAnchorList(anchorLists[elementId], -Math.PI / 2, 0, {endpoints:[ep[i], ep[i]], paint:function(){}}, false, elementId, 0, false, "top", elementId, connectionsToPaint, endpointsToPaint);\n
\t\t\t\t\t\tjsPlumbUtil.addWithFunction(anchorsToUpdate, elementId, function(a) { return a === elementId; });\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t            // now place all the continuous anchors we need to;\n
\t            for (i = 0; i < anchorsToUpdate.length; i++) {\n
\t\t\t\t\tplaceAnchors(anchorsToUpdate[i], anchorLists[anchorsToUpdate[i]]);\n
\t\t\t\t}\n
\n
\t\t\t\t// now that continuous anchors have been placed, paint all the endpoints for this element\n
\t            // TODO performance: add the endpoint ids to a temp array, and then when iterating in the next\n
\t            // loop, check that we didn\'t just paint that endpoint. we can probably shave off a few more milliseconds this way.\n
\t\t\t\tfor (i = 0; i < ep.length; i++) {\t\t\t\t\n
                    ep[i].paint( { timestamp : timestamp, offset : myOffset, dimensions : myOffset.s, recalc:doNotRecalcEndpoint !== true });\n
\t\t\t\t}\n
\t            // ... and any other endpoints we came across as a result of the continuous anchors.\n
\t            for (i = 0; i < endpointsToPaint.length; i++) {\n
                    var cd = jsPlumbInstance.getCachedData(endpointsToPaint[i].elementId);\n
                    // dont use timestamp for this endpoint, as it is not for the current element and we may \n
                    // have needed to recalculate anchor position due to the element for the endpoint moving.\n
                    //endpointsToPaint[i].paint( { timestamp : null, offset : cd, dimensions : cd.s });\n
\n
                    endpointsToPaint[i].paint( { timestamp : timestamp, offset : cd, dimensions : cd.s });\n
\t\t\t\t}\n
\n
\t\t\t\t// paint all the standard and "dynamic connections", which are connections whose other anchor is\n
\t\t\t\t// static and therefore does need to be recomputed; we make sure that happens only one time.\n
\t\n
\t\t\t\t// TODO we could have compiled a list of these in the first pass through connections; might save some time.\n
\t\t\t\tfor (i = 0; i < endpointConnections.length; i++) {\n
\t\t\t\t\tvar otherEndpoint = endpointConnections[i][1];\n
\t\t\t\t\tif (otherEndpoint.anchor.constructor == jsPlumb.DynamicAnchor) {\t\t\t \t\t\t\t\t\t\t\n
\t\t\t\t\t\totherEndpoint.paint({ elementWithPrecedence:elementId, timestamp:timestamp });\t\t\t\t\t\t\t\t\n
\t                    jsPlumbUtil.addWithFunction(connectionsToPaint, endpointConnections[i][0], function(c) { return c.id == endpointConnections[i][0].id; });\n
\t\t\t\t\t\t// all the connections for the other endpoint now need to be repainted\n
\t\t\t\t\t\tfor (var k = 0; k < otherEndpoint.connections.length; k++) {\n
\t\t\t\t\t\t\tif (otherEndpoint.connections[k] !== endpointConnections[i][0])\t\t\t\t\t\t\t\n
\t                            jsPlumbUtil.addWithFunction(connectionsToPaint, otherEndpoint.connections[k], function(c) { return c.id == otherEndpoint.connections[k].id; });\n
\t\t\t\t\t\t}\n
\t\t\t\t\t} else if (otherEndpoint.anchor.constructor == jsPlumb.Anchor) {\t\t\t\t\t\n
\t                    jsPlumbUtil.addWithFunction(connectionsToPaint, endpointConnections[i][0], function(c) { return c.id == endpointConnections[i][0].id; });\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\t// paint current floating connection for this element, if there is one.\n
\t\t\t\tvar fc = floatingConnections[elementId];\n
\t\t\t\tif (fc) \n
\t\t\t\t\tfc.paint({timestamp:timestamp, recalc:false, elId:elementId});\n
\t\t\t\t                \n
\t\t\t\t// paint all the connections\n
\t\t\t\tfor (i = 0; i < connectionsToPaint.length; i++) {\n
\t\t\t\t\t// if not a connection between the two elements in question dont use the timestamp.\n
                    var ts  =timestamp;// ((connectionsToPaint[i].sourceId == sourceId && connectionsToPaint[i].targetId == targetId) ||\n
                               //(connectionsToPaint[i].sourceId == targetId && connectionsToPaint[i].targetId == sourceId)) ? timestamp : null;\n
                    connectionsToPaint[i].paint({elId:elementId, timestamp:ts, recalc:false, clearEdits:clearEdits});\n
\t\t\t\t}\n
\t\t\t}\n
\t\t};        \n
        \n
        var ContinuousAnchor = function(anchorParams) {\n
            jsPlumbUtil.EventGenerator.apply(this);\n
            this.type = "Continuous";\n
            this.isDynamic = true;\n
            this.isContinuous = true;\n
            var faces = anchorParams.faces || ["top", "right", "bottom", "left"],\n
                clockwise = !(anchorParams.clockwise === false),\n
                availableFaces = { },\n
                opposites = { "top":"bottom", "right":"left","left":"right","bottom":"top" },\n
                clockwiseOptions = { "top":"right", "right":"bottom","left":"top","bottom":"left" },\n
                antiClockwiseOptions = { "top":"left", "right":"top","left":"bottom","bottom":"right" },\n
                secondBest = clockwise ? clockwiseOptions : antiClockwiseOptions,\n
                lastChoice = clockwise ? antiClockwiseOptions : clockwiseOptions,\n
                cssClass = anchorParams.cssClass || "";\n
            \n
            for (var i = 0; i < faces.length; i++) { availableFaces[faces[i]] = true; }\n
          \n
            // if the given edge is supported, returns it. otherwise looks for a substitute that _is_\n
            // supported. if none supported we also return the request edge.\n
            this.verifyEdge = function(edge) {\n
                if (availableFaces[edge]) return edge;\n
                else if (availableFaces[opposites[edge]]) return opposites[edge];\n
                else if (availableFaces[secondBest[edge]]) return secondBest[edge];\n
                else if (availableFaces[lastChoice[edge]]) return lastChoice[edge];\n
                return edge; // we have to give them something.\n
            };\n
            \n
            this.compute = function(params) {\n
                return userDefinedContinuousAnchorLocations[params.element.id] || continuousAnchorLocations[params.element.id] || [0,0];\n
            };\n
            this.getCurrentLocation = function(params) {\n
                return userDefinedContinuousAnchorLocations[params.element.id] || continuousAnchorLocations[params.element.id] || [0,0];\n
            };\n
            this.getOrientation = function(endpoint) {\n
                return continuousAnchorOrientations[endpoint.id] || [0,0];\n
            };\n
            this.clearUserDefinedLocation = function() { \n
                delete userDefinedContinuousAnchorLocations[anchorParams.elementId]; \n
            };\n
            this.setUserDefinedLocation = function(loc) { \n
                userDefinedContinuousAnchorLocations[anchorParams.elementId] = loc; \n
            };            \n
            this.getCssClass = function() { return cssClass; };\n
            this.setCssClass = function(c) { cssClass = c; };\n
        };        \n
        \n
        // continuous anchors\n
        jsPlumbInstance.continuousAnchorFactory = {\n
            get:function(params) {\n
                var existing = continuousAnchors[params.elementId];\n
                if (!existing) {\n
                    existing = new ContinuousAnchor(params);                    \n
                    continuousAnchors[params.elementId] = existing;\n
                }\n
                return existing;\n
            },\n
            clear:function(elementId) {\n
                delete continuousAnchors[elementId];\n
            }\n
        };\n
\t};\n
    \n
    /**\n
     * Anchors model a position on some element at which an Endpoint may be located.  They began as a first class citizen of jsPlumb, ie. a user\n
     * was required to create these themselves, but over time this has been replaced by the concept of referring to them either by name (eg. "TopMiddle"),\n
     * or by an array describing their coordinates (eg. [ 0, 0.5, 0, -1 ], which is the same as "TopMiddle").  jsPlumb now handles all of the\n
     * creation of Anchors without user intervention.\n
     */\n
    jsPlumb.Anchor = function(params) {       \n
        this.x = params.x || 0;\n
        this.y = params.y || 0;\n
        this.elementId = params.elementId;  \n
        this.cssClass = params.cssClass || "";      \n
        this.userDefinedLocation = null;\n
        this.orientation = params.orientation || [ 0, 0 ];\n
\n
        jsPlumbUtil.EventGenerator.apply(this);\n
        \n
        var jsPlumbInstance = params.jsPlumbInstance;//,\n
            //lastTimestamp = null;//, lastReturnValue = null;\n
        \n
        this.lastReturnValue = null;\n
        this.offsets = params.offsets || [ 0, 0 ];\n
        this.timestamp = null;        \n
        this.compute = function(params) {\n
\n
\t\t\tvar xy = params.xy, wh = params.wh, element = params.element, timestamp = params.timestamp; \n
\n
\t\t\tif(params.clearUserDefinedLocation)\n
\t\t\t\tthis.userDefinedLocation = null;\n
\n
\t\t\tif (timestamp && timestamp === self.timestamp)\n
\t\t\t\treturn this.lastReturnValue;\n
\n
\t\t\tif (this.userDefinedLocation != null) {\n
\t\t\t\tthis.lastReturnValue = this.userDefinedLocation;\n
\t\t\t}\n
\t\t\telse {\n
\t\t\t\tthis.lastReturnValue = [ xy[0] + (this.x * wh[0]) + this.offsets[0], xy[1] + (this.y * wh[1]) + this.offsets[1] ];\n
\t\t\t}\n
\n
\t\t\tthis.timestamp = timestamp;\n
\t\t\treturn this.lastReturnValue;\n
\t\t};\n
\n
        this.getCurrentLocation = function(params) { \n
            return (this.lastReturnValue == null || (params.timestamp != null && this.timestamp != params.timestamp)) ? this.compute(params) : this.lastReturnValue; \n
        };\n
    };\n
    jsPlumbUtil.extend(jsPlumb.Anchor, jsPlumbUtil.EventGenerator, {\n
        equals : function(anchor) {\n
            if (!anchor) return false;\n
            var ao = anchor.getOrientation(),\n
                o = this.getOrientation();\n
            return this.x == anchor.x && this.y == anchor.y && this.offsets[0] == anchor.offsets[0] && this.offsets[1] == anchor.offsets[1] && o[0] == ao[0] && o[1] == ao[1];\n
        },\n
        getUserDefinedLocation : function() { \n
            return this.userDefinedLocation;\n
        },        \n
        setUserDefinedLocation : function(l) {\n
            this.userDefinedLocation = l;\n
        },\n
        clearUserDefinedLocation : function() {\n
            this.userDefinedLocation = null;\n
        },\n
        getOrientation : function(_endpoint) { return this.orientation; },\n
        getCssClass : function() { return this.cssClass; }\n
    });\n
\n
    /**\n
     * An Anchor that floats. its orientation is computed dynamically from\n
     * its position relative to the anchor it is floating relative to.  It is used when creating \n
     * a connection through drag and drop.\n
     * \n
     * TODO FloatingAnchor could totally be refactored to extend Anchor just slightly.\n
     */\n
    jsPlumb.FloatingAnchor = function(params) {\n
        \n
        jsPlumb.Anchor.apply(this, arguments);\n
\n
        // this is the anchor that this floating anchor is referenced to for\n
        // purposes of calculating the orientation.\n
        var ref = params.reference,\n
            jsPlumbInstance = params.jsPlumbInstance,\n
            // the canvas this refers to.\n
            refCanvas = params.referenceCanvas,\n
            size = jsPlumb.getSize(refCanvas),\n
            // these are used to store the current relative position of our\n
            // anchor wrt the reference anchor. they only indicate\n
            // direction, so have a value of 1 or -1 (or, very rarely, 0). these\n
            // values are written by the compute method, and read\n
            // by the getOrientation method.\n
            xDir = 0, yDir = 0,\n
            // temporary member used to store an orientation when the floating\n
            // anchor is hovering over another anchor.\n
            orientation = null,\n
            _lastResult = null;\n
\n
        // clear from parent. we want floating anchor orientation to always be computed.\n
        this.orientation = null;\n
\n
        // set these to 0 each; they are used by certain types of connectors in the loopback case,\n
        // when the connector is trying to clear the element it is on. but for floating anchor it\'s not\n
        // very important.\n
        this.x = 0; this.y = 0;\n
\n
        this.isFloating = true;\n
\n
\t\tthis.compute = function(params) {\n
\t\t\tvar xy = params.xy, element = params.element,\n
\t\t\t\tresult = [ xy[0] + (size[0] / 2), xy[1] + (size[1] / 2) ]; // return origin of the element. we may wish to improve this so that any object can be the drag proxy.\n
\t\t\t_lastResult = result;\n
\t\t\treturn result;\n
\t\t};\n
\n
        this.getOrientation = function(_endpoint) {\n
            if (orientation) return orientation;\n
            else {\n
                var o = ref.getOrientation(_endpoint);\n
                // here we take into account the orientation of the other\n
                // anchor: if it declares zero for some direction, we declare zero too. this might not be the most awesome. perhaps we can come\n
                // up with a better way. it\'s just so that the line we draw looks like it makes sense. maybe this wont make sense.\n
                return [ Math.abs(o[0]) * xDir * -1,\n
                        Math.abs(o[1]) * yDir * -1 ];\n
            }\n
        };\n
\n
        /**\n
         * notification the endpoint associated with this anchor is hovering\n
         * over another anchor; we want to assume that anchor\'s orientation\n
         * for the duration of the hover.\n
         */\n
        this.over = function(anchor, endpoint) { \n
            orientation = anchor.getOrientation(endpoint); \n
        };\n
\n
        /**\n
         * notification the endpoint associated with this anchor is no\n
         * longer hovering over another anchor; we should resume calculating\n
         * orientation as we normally do.\n
         */\n
        this.out = function() { orientation = null; };\n
\n
        this.getCurrentLocation = function(params) { return _lastResult == null ? this.compute(params) : _lastResult; };\n
    };\n
    jsPlumbUtil.extend(jsPlumb.FloatingAnchor, jsPlumb.Anchor);\n
\n
    var _convertAnchor = function(anchor, jsPlumbInstance, elementId) { \n
        return anchor.constructor == jsPlumb.Anchor ? anchor: jsPlumbInstance.makeAnchor(anchor, elementId, jsPlumbInstance); \n
    };\n
\n
    /* \n
     * A DynamicAnchor is an Anchor that contains a list of other Anchors, which it cycles\n
     * through at compute time to find the one that is located closest to\n
     * the center of the target element, and returns that Anchor\'s compute\n
     * method result. this causes endpoints to follow each other with\n
     * respect to the orientation of their target elements, which is a useful\n
     * feature for some applications.\n
     * \n
     */\n
    jsPlumb.DynamicAnchor = function(params) {\n
        jsPlumb.Anchor.apply(this, arguments);\n
        \n
        this.isSelective = true;\n
        this.isDynamic = true;\t\t\t\n
        this.anchors = [];\n
        this.elementId = params.elementId;\n
        this.jsPlumbInstance = params.jsPlumbInstance;\n
\n
        for (var i = 0; i < params.anchors.length; i++) \n
            this.anchors[i] = _convertAnchor(params.anchors[i], this.jsPlumbInstance, this.elementId);\t\t\t\n
        this.addAnchor = function(anchor) { this.anchors.push(_convertAnchor(anchor, this.jsPlumbInstance, this.elementId)); };\n
        this.getAnchors = function() { return this.anchors; };\n
        this.locked = false;\n
        var _curAnchor = this.anchors.length > 0 ? this.anchors[0] : null,\n
            _curIndex = this.anchors.length > 0 ? 0 : -1,\n
            _lastAnchor = _curAnchor,\n
            self = this,\n
        \n
            // helper method to calculate the distance between the centers of the two elements.\n
            _distance = function(anchor, cx, cy, xy, wh) {\n
                var ax = xy[0] + (anchor.x * wh[0]), ay = xy[1] + (anchor.y * wh[1]),\t\t\t\t\n
                    acx = xy[0] + (wh[0] / 2), acy = xy[1] + (wh[1] / 2);\n
                return (Math.sqrt(Math.pow(cx - ax, 2) + Math.pow(cy - ay, 2)) +\n
                        Math.sqrt(Math.pow(acx - ax, 2) + Math.pow(acy - ay, 2)));\n
            },        \n
            // default method uses distance between element centers.  you can provide your own method in the dynamic anchor\n
            // constructor (and also to jsPlumb.makeDynamicAnchor). the arguments to it are four arrays: \n
            // xy - xy loc of the anchor\'s element\n
            // wh - anchor\'s element\'s dimensions\n
            // txy - xy loc of the element of the other anchor in the connection\n
            // twh - dimensions of the element of the other anchor in the connection.\n
            // anchors - the list of selectable anchors\n
            _anchorSelector = params.selector || function(xy, wh, txy, twh, anchors) {\n
                var cx = txy[0] + (twh[0] / 2), cy = txy[1] + (twh[1] / 2);\n
                var minIdx = -1, minDist = Infinity;\n
                for ( var i = 0; i < anchors.length; i++) {\n
                    var d = _distance(anchors[i], cx, cy, xy, wh);\n
                    if (d < minDist) {\n
                        minIdx = i + 0;\n
                        minDist = d;\n
                    }\n
                }\n
                return anchors[minIdx];\n
            };\n
        \n
        this.compute = function(params) {\t\t\t\t\n
            var xy = params.xy, wh = params.wh, timestamp = params.timestamp, txy = params.txy, twh = params.twh;\t\t\t\t\n
            \n
            if(params.clearUserDefinedLocation)\n
                userDefinedLocation = null;\n
\n
            this.timestamp = timestamp;            \n
            \n
            var udl = self.getUserDefinedLocation();\n
            if (udl != null) {\n
                return udl;\n
            }\n
            \n
            // if anchor is locked or an opposite element was not given, we\n
            // maintain our state. anchor will be locked\n
            // if it is the source of a drag and drop.\n
            if (this.locked || txy == null || twh == null)\n
                return _curAnchor.compute(params);\t\t\t\t\n
            else\n
                params.timestamp = null; // otherwise clear this, i think. we want the anchor to compute.\n
            \n
            _curAnchor = _anchorSelector(xy, wh, txy, twh, this.anchors);\n
            this.x = _curAnchor.x;\n
            this.y = _curAnchor.y;        \n
\n
            if (_curAnchor != _lastAnchor)\n
                this.fire("anchorChanged", _curAnchor);\n
\n
            _lastAnchor = _curAnchor;\n
            \n
            return _curAnchor.compute(params);\n
        };\n
\n
        this.getCurrentLocation = function(params) {\n
            return this.getUserDefinedLocation() || (_curAnchor != null ? _curAnchor.getCurrentLocation(params) : null);\n
        };\n
\n
        this.getOrientation = function(_endpoint) { return _curAnchor != null ? _curAnchor.getOrientation(_endpoint) : [ 0, 0 ]; };\n
        this.over = function(anchor, endpoint) { if (_curAnchor != null) _curAnchor.over(anchor, endpoint); };\n
        this.out = function() { if (_curAnchor != null) _curAnchor.out(); };\n
\n
        this.getCssClass = function() { return (_curAnchor && _curAnchor.getCssClass()) || ""; };\n
    };    \n
    jsPlumbUtil.extend(jsPlumb.DynamicAnchor, jsPlumb.Anchor);        \n
    \n
// -------- basic anchors ------------------    \n
    var _curryAnchor = function(x, y, ox, oy, type, fnInit) {\n
        jsPlumb.Anchors[type] = function(params) {\n
            var a = params.jsPlumbInstance.makeAnchor([ x, y, ox, oy, 0, 0 ], params.elementId, params.jsPlumbInstance);\n
            a.type = type;\n
            if (fnInit) fnInit(a, params);\n
            return a;\n
        };\n
    };\n
    \t\n
\t_curryAnchor(0.5, 0, 0,-1, "TopCenter");\n
    _curryAnchor(0.5, 1, 0, 1, "BottomCenter");\n
    _curryAnchor(0, 0.5, -1, 0, "LeftMiddle");\n
    _curryAnchor(1, 0.5, 1, 0, "RightMiddle");\n
    // from 1.4.2: Top, Right, Bottom, Left\n
    _curryAnchor(0.5, 0, 0,-1, "Top");\n
    _curryAnchor(0.5, 1, 0, 1, "Bottom");\n
    _curryAnchor(0, 0.5, -1, 0, "Left");\n
    _curryAnchor(1, 0.5, 1, 0, "Right");\n
    _curryAnchor(0.5, 0.5, 0, 0, "Center");\n
    _curryAnchor(1, 0, 0,-1, "TopRight");\n
    _curryAnchor(1, 1, 0, 1, "BottomRight");\n
    _curryAnchor(0, 0, 0, -1, "TopLeft");\n
    _curryAnchor(0, 1, 0, 1, "BottomLeft");\n
    \n
// ------- dynamic anchors -------------------    \n
\t\t\t\n
    // default dynamic anchors chooses from Top, Right, Bottom, Left\n
\tjsPlumb.Defaults.DynamicAnchors = function(params) {\n
\t\treturn params.jsPlumbInstance.makeAnchors(["TopCenter", "RightMiddle", "BottomCenter", "LeftMiddle"], params.elementId, params.jsPlumbInstance);\n
\t};\n
    \n
    // default dynamic anchors bound to name \'AutoDefault\'\n
\tjsPlumb.Anchors.AutoDefault  = function(params) { \n
\t\tvar a = params.jsPlumbInstance.makeDynamicAnchor(jsPlumb.Defaults.DynamicAnchors(params));\n
\t\ta.type = "AutoDefault";\n
\t\treturn a;\n
\t};\t\n
    \n
// ------- continuous anchors -------------------    \n
    \n
    var _curryContinuousAnchor = function(type, faces) {\n
        jsPlumb.Anchors[type] = function(params) {\n
            var a = params.jsPlumbInstance.makeAnchor(["Continuous", { faces:faces }], params.elementId, params.jsPlumbInstance);\n
            a.type = type;\n
            return a;\n
        };\n
    };\n
    \n
    jsPlumb.Anchors.Continuous = function(params) {\n
\t\treturn params.jsPlumbInstance.continuousAnchorFactory.get(params);\n
\t};\n
                \n
    _curryContinuousAnchor("ContinuousLeft", ["left"]);    \n
    _curryContinuousAnchor("ContinuousTop", ["top"]);                 \n
    _curryContinuousAnchor("ContinuousBottom", ["bottom"]);                 \n
    _curryContinuousAnchor("ContinuousRight", ["right"]); \n
    \n
// ------- position assign anchors -------------------    \n
    \n
    // this anchor type lets you assign the position at connection time.\n
\t_curryAnchor(0, 0, 0, 0, "Assign", function(anchor, params) {\n
\t\t// find what to use as the "position finder". the user may have supplied a String which represents\n
\t\t// the id of a position finder in jsPlumb.AnchorPositionFinders, or the user may have supplied the\n
\t\t// position finder as a function.  we find out what to use and then set it on the anchor.\n
\t\tvar pf = params.position || "Fixed";\n
\t\tanchor.positionFinder = pf.constructor == String ? params.jsPlumbInstance.AnchorPositionFinders[pf] : pf;\n
\t\t// always set the constructor params; the position finder might need them later (the Grid one does,\n
\t\t// for example)\n
\t\tanchor.constructorParams = params;\n
\t});\t\n
\n
    // these are the default anchor positions finders, which are used by the makeTarget function.  supplying\n
    // a position finder argument to that function allows you to specify where the resulting anchor will\n
    // be located\n
\tjsPlumbInstance.prototype.AnchorPositionFinders = {\n
\t\t"Fixed": function(dp, ep, es, params) {\n
\t\t\treturn [ (dp.left - ep.left) / es[0], (dp.top - ep.top) / es[1] ];\t\n
\t\t},\n
\t\t"Grid":function(dp, ep, es, params) {\n
\t\t\tvar dx = dp.left - ep.left, dy = dp.top - ep.top,\n
\t\t\t\tgx = es[0] / (params.grid[0]), gy = es[1] / (params.grid[1]),\n
\t\t\t\tmx = Math.floor(dx / gx), my = Math.floor(dy / gy);\n
\t\t\treturn [ ((mx * gx) + (gx / 2)) / es[0], ((my * gy) + (gy / 2)) / es[1] ];\n
\t\t}\n
\t};\n
    \n
// ------- perimeter anchors -------------------    \n
\t\t\n
\tjsPlumb.Anchors.Perimeter = function(params) {\n
\t\tparams = params || {};\n
\t\tvar anchorCount = params.anchorCount || 60,\n
\t\t\tshape = params.shape;\n
\t\t\n
\t\tif (!shape) throw new Error("no shape supplied to Perimeter Anchor type");\t\t\n
\t\t\n
\t\tvar _circle = function() {\n
                var r = 0.5, step = Math.PI * 2 / anchorCount, current = 0, a = [];\n
                for (var i = 0; i < anchorCount; i++) {\n
                    var x = r + (r * Math.sin(current)),\n
                        y = r + (r * Math.cos(current));                                \n
                    a.push( [ x, y, 0, 0 ] );\n
                    current += step;\n
                }\n
                return a;\t\n
            },\n
            _path = function(segments) {\n
                var anchorsPerFace = anchorCount / segments.length, a = [],\n
                    _computeFace = function(x1, y1, x2, y2, fractionalLength) {\n
                        anchorsPerFace = anchorCount * fractionalLength;\n
                        var dx = (x2 - x1) / anchorsPerFace, dy = (y2 - y1) / anchorsPerFace;\n
                        for (var i = 0; i < anchorsPerFace; i++) {\n
                            a.push( [\n
                                x1 + (dx * i),\n
                                y1 + (dy * i),\n
                                0,\n
                                0\n
                            ]);\n
                        }\n
                    };\n
\t\t\t\t\t\t\t\t\n
                for (var i = 0; i < segments.length; i++)\n
                    _computeFace.apply(null, segments[i]);\n
\t\t\t\t\t\t\t\t\t\t\t\t\t\t\n
                return a;\t\t\t\t\t\n
            },\n
\t\t\t_shape = function(faces) {\t\t\t\t\t\t\t\t\t\t\t\t\n
                var s = [];\n
                for (var i = 0; i < faces.length; i++) {\n
                    s.push([faces[i][0], faces[i][1], faces[i][2], faces[i][3], 1 / faces.length]);\n
                }\n
                return _path(s);\n
\t\t\t},\n
\t\t\t_rectangle = function() {\n
\t\t\t\treturn _shape([\n
\t\t\t\t\t[ 0, 0, 1, 0 ], [ 1, 0, 1, 1 ], [ 1, 1, 0, 1 ], [ 0, 1, 0, 0 ]\n
\t\t\t\t]);\t\t\n
\t\t\t};\n
\t\t\n
\t\tvar _shapes = {\n
\t\t\t"Circle":_circle,\n
\t\t\t"Ellipse":_circle,\n
\t\t\t"Diamond":function() {\n
\t\t\t\treturn _shape([\n
\t\t\t\t\t\t[ 0.5, 0, 1, 0.5 ], [ 1, 0.5, 0.5, 1 ], [ 0.5, 1, 0, 0.5 ], [ 0, 0.5, 0.5, 0 ]\n
\t\t\t\t]);\n
\t\t\t},\n
\t\t\t"Rectangle":_rectangle,\n
\t\t\t"Square":_rectangle,\n
\t\t\t"Triangle":function() {\n
\t\t\t\treturn _shape([\n
\t\t\t\t\t\t[ 0.5, 0, 1, 1 ], [ 1, 1, 0, 1 ], [ 0, 1, 0.5, 0]\n
\t\t\t\t]);\t\n
\t\t\t},\n
\t\t\t"Path":function(params) {\n
                var points = params.points, p = [], tl = 0;\n
\t\t\t\tfor (var i = 0; i < points.length - 1; i++) {\n
                    var l = Math.sqrt(Math.pow(points[i][2] - points[i][0]) + Math.pow(points[i][3] - points[i][1]));\n
                    tl += l;\n
\t\t\t\t\tp.push([points[i][0], points[i][1], points[i+1][0], points[i+1][1], l]);\t\t\t\t\t\t\n
\t\t\t\t}\n
                for (var j = 0; j < p.length; j++) {\n
                    p[j][4] = p[j][4] / tl;\n
                }\n
\t\t\t\treturn _path(p);\n
\t\t\t}\n
\t\t},\n
        _rotate = function(points, amountInDegrees) {\n
            var o = [], theta = amountInDegrees / 180 * Math.PI ;\n
            for (var i = 0; i < points.length; i++) {\n
                var _x = points[i][0] - 0.5,\n
                    _y = points[i][1] - 0.5;\n
                    \n
                o.push([\n
                    0.5 + ((_x * Math.cos(theta)) - (_y * Math.sin(theta))),\n
                    0.5 + ((_x * Math.sin(theta)) + (_y * Math.cos(theta))),\n
                    points[i][2],\n
                    points[i][3]\n
                ]);\n
            }\n
            return o;\n
        };\n
\t\t\n
\t\tif (!_shapes[shape]) throw new Error("Shape [" + shape + "] is unknown by Perimeter Anchor type");\n
\t\t\n
\t\tvar da = _shapes[shape](params);\n
        if (params.rotation) da = _rotate(da, params.rotation);\n
        var a = params.jsPlumbInstance.makeDynamicAnchor(da);\n
\t\ta.type = "Perimeter";\n
\t\treturn a;\n
\t};\n
})();\n
/*\n
 * jsPlumb\n
 * \n
 * Title:jsPlumb 1.6.2\n
 * \n
 * Provides a way to visually connect elements on an HTML page, using SVG or VML.  \n
 * \n
 * This file contains the default Connectors, Endpoint and Overlay definitions.\n
 *\n
 * Copyright (c) 2010 - 2014 Simon Porritt (simon@jsplumbtoolkit.com)\n
 * \n
 * http://jsplumbtoolkit.com\n
 * http://github.com/sporritt/jsplumb\n
 * \n
 * Dual licensed under the MIT and GPL2 licenses.\n
 */  \n
;(function() {\t\n
\n
\t"use strict";\n
\t\t\t\t\n
\t/**\n
\t * \n
\t * Helper class to consume unused mouse events by components that are DOM elements and\n
\t * are used by all of the different rendering modes.\n
\t * \n
\t */\n
\tjsPlumb.DOMElementComponent = jsPlumbUtil.extend(jsPlumb.jsPlumbUIComponent, function(params) {\t\t\n
\t\t// this component is safe to pipe this stuff to /dev/null.\n
\t\tthis.mousemove = \n
\t\tthis.dblclick  = \n
\t\tthis.click = \n
\t\tthis.mousedown = \n
\t\tthis.mouseup = function(e) { };\n
\t});\n
\n
\tjsPlumb.Segments = {\n
\n
        /*\n
         * Class: AbstractSegment\n
         * A Connector is made up of 1..N Segments, each of which has a Type, such as \'Straight\', \'Arc\',\n
         * \'Bezier\'. This is new from 1.4.2, and gives us a lot more flexibility when drawing connections: things such\n
         * as rounded corners for flowchart connectors, for example, or a straight line stub for Bezier connections, are\n
         * much easier to do now.\n
         *\n
         * A Segment is responsible for providing coordinates for painting it, and also must be able to report its length.\n
         * \n
         */ \n
        AbstractSegment : function(params) { \n
            this.params = params;\n
            \n
            /**\n
            * Function: findClosestPointOnPath\n
            * Finds the closest point on this segment to the given [x, y], \n
            * returning both the x and y of the point plus its distance from\n
            * the supplied point, and its location along the length of the\n
            * path inscribed by the segment.  This implementation returns\n
            * Infinity for distance and null values for everything else;\n
            * subclasses are expected to override.\n
            */\n
            this.findClosestPointOnPath = function(x, y) {\n
                return {\n
                    d:Infinity,\n
                    x:null,\n
                    y:null,\n
                    l:null\n
                };\n
            };\n
\n
            this.getBounds = function() {\n
                return {\n
                    minX:Math.min(params.x1, params.x2),\n
                    minY:Math.min(params.y1, params.y2),\n
                    maxX:Math.max(params.x1, params.x2),\n
                    maxY:Math.max(params.y1, params.y2)\n
                };\n
            };\n
        },\n
        Straight : function(params) {\n
            var _super = jsPlumb.Segments.AbstractSegment.apply(this, arguments),\n
                length, m, m2, x1, x2, y1, y2,\n
                _recalc = function() {\n
                    length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));\n
                    m = Biltong.gradient({x:x1, y:y1}, {x:x2, y:y2});\n
                    m2 = -1 / m;                \n
                };\n
                \n
            this.type = "Straight";\n
            \n
            this.getLength = function() { return length; };\n
            this.getGradient = function() { return m; };\n
                \n
            this.getCoordinates = function() {\n
                return { x1:x1,y1:y1,x2:x2,y2:y2 };\n
            };\n
            this.setCoordinates = function(coords) {\n
                x1 = coords.x1; y1 = coords.y1; x2 = coords.x2; y2 = coords.y2;\n
                _recalc();\n
            };\n
            this.setCoordinates({x1:params.x1, y1:params.y1, x2:params.x2, y2:params.y2});\n
\n
            this.getBounds = function() {\n
                return {\n
                    minX:Math.min(x1, x2),\n
                    minY:Math.min(y1, y2),\n
                    maxX:Math.max(x1, x2),\n
                    maxY:Math.max(y1, y2)\n
                };\n
            };\n
            \n
            /**\n
             * returns the point on the segment\'s path that is \'location\' along the length of the path, where \'location\' is a decimal from\n
             * 0 to 1 inclusive. for the straight line segment this is simple maths.\n
             */\n
             this.pointOnPath = function(location, absolute) {\n
                if (location === 0 && !absolute)\n
                    return { x:x1, y:y1 };\n
                else if (location == 1 && !absolute)\n
                    return { x:x2, y:y2 };\n
                else {\n
                    var l = absolute ? location > 0 ? location : length + location : location * length;\n
                    return Biltong.pointOnLine({x:x1, y:y1}, {x:x2, y:y2}, l);\n
                }\n
            };\n
            \n
            /**\n
             * returns the gradient of the segment at the given point - which for us is constant.\n
             */\n
            this.gradientAtPoint = function(_) {\n
                return m;\n
            };\n
            \n
            /**\n
             * returns the point on the segment\'s path that is \'distance\' along the length of the path from \'location\', where \n
             * \'location\' is a decimal from 0 to 1 inclusive, and \'distance\' is a number of pixels.\n
             * this hands off to jsPlumbUtil to do the maths, supplying two points and the distance.\n
             */            \n
            this.pointAlongPathFrom = function(location, distance, absolute) {            \n
                var p = this.pointOnPath(location, absolute),\n
                    farAwayPoint = distance <= 0 ? {x:x1, y:y1} : {x:x2, y:y2 };\n
\n
                /*\n
                location == 1 ? {\n
                                        x:x1 + ((x2 - x1) * 10),\n
                                        y:y1 + ((y1 - y2) * 10)\n
                                    } : \n
                */\n
    \n
                if (distance <= 0 && Math.abs(distance) > 1) distance *= -1;\n
    \n
                return Biltong.pointOnLine(p, farAwayPoint, distance);\n
            };\n
            \n
            // is c between a and b?\n
            var within = function(a,b,c) {\n
                return c >= Math.min(a,b) && c <= Math.max(a,b); \n
            };\n
            // find which of a and b is closest to c\n
            var closest = function(a,b,c) {\n
                return Math.abs(c - a) < Math.abs(c - b) ? a : b;\n
            };\n
            \n
            /**\n
                Function: findClosestPointOnPath\n
                Finds the closest point on this segment to [x,y]. See\n
                notes on this method in AbstractSegment.\n
            */\n
            this.findClosestPointOnPath = function(x, y) {\n
                var out = {\n
                    d:Infinity,\n
                    x:null,\n
                    y:null,\n
                    l:null,\n
                    x1:x1,\n
                    x2:x2,\n
                    y1:y1,\n
                    y2:y2\n
                };\n
\n
                if (m === 0) {                  \n
                    out.y = y1;\n
                    out.x = within(x1, x2, x) ? x : closest(x1, x2, x);\n
                }\n
                else if (m == Infinity || m == -Infinity) {\n
                    out.x = x1;                \n
                    out.y = within(y1, y2, y) ? y : closest(y1, y2, y);\n
                }\n
                else {\n
                    // closest point lies on normal from given point to this line.  \n
                    var b = y1 - (m * x1),\n
                        b2 = y - (m2 * x),                    \n
                    // y1 = m.x1 + b and y1 = m2.x1 + b2\n
                    // so m.x1 + b = m2.x1 + b2\n
                    // x1(m - m2) = b2 - b\n
                    // x1 = (b2 - b) / (m - m2)\n
                        _x1 = (b2 -b) / (m - m2),\n
                        _y1 = (m * _x1) + b;\n
                                        \n
                    out.x = within(x1,x2,_x1) ? _x1 : closest(x1,x2,_x1);//_x1;\n
                    out.y = within(y1,y2,_y1) ? _y1 : closest(y1,y2,_y1);//_y1;                    \n
                }\n
\n
                var fractionInSegment = Biltong.lineLength([ out.x, out.y ], [ x1, y1 ]);\n
                out.d = Biltong.lineLength([x,y], [out.x, out.y]);\n
                out.l = fractionInSegment / length;            \n
                return out;\n
            };        \n
        },\n
\t\n
        /*\n
            Arc Segment. You need to supply:\n
    \n
            r   -   radius\n
            cx  -   center x for the arc\n
            cy  -   center y for the arc\n
            ac  -   whether the arc is anticlockwise or not. default is clockwise.\n
    \n
            and then either:\n
    \n
            startAngle  -   startAngle for the arc.\n
            endAngle    -   endAngle for the arc.\n
    \n
            or:\n
    \n
            x1          -   x for start point\n
            y1          -   y for start point\n
            x2          -   x for end point\n
            y2          -   y for end point\n
    \n
        */\n
        Arc : function(params) {\n
            var _super = jsPlumb.Segments.AbstractSegment.apply(this, arguments),\n
                _calcAngle = function(_x, _y) {\n
                    return Biltong.theta([params.cx, params.cy], [_x, _y]);    \n
                },\n
                _calcAngleForLocation = function(segment, location) {\n
                    if (segment.anticlockwise) {\n
                        var sa = segment.startAngle < segment.endAngle ? segment.startAngle + TWO_PI : segment.startAngle,\n
                            s = Math.abs(sa - segment.endAngle);\n
                        return sa - (s * location);                    \n
                    }\n
                    else {\n
                        var ea = segment.endAngle < segment.startAngle ? segment.endAngle + TWO_PI : segment.endAngle,\n
                            ss = Math.abs (e

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAY=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="6" aka="AAAAAAAAAAY=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

a - segment.startAngle);\n
                    \n
                        return segment.startAngle + (ss * location);\n
                    }\n
                },\n
                TWO_PI = 2 * Math.PI;\n
            \n
            this.radius = params.r;\n
            this.anticlockwise = params.ac;\t\t\t\n
            this.type = "Arc";\n
                \n
            if (params.startAngle && params.endAngle) {\n
                this.startAngle = params.startAngle;\n
                this.endAngle = params.endAngle;            \n
                this.x1 = params.cx + (this.radius * Math.cos(params.startAngle));     \n
                this.y1 = params.cy + (this.radius * Math.sin(params.startAngle));            \n
                this.x2 = params.cx + (this.radius * Math.cos(params.endAngle));     \n
                this.y2 = params.cy + (this.radius * Math.sin(params.endAngle));                        \n
            }\n
            else {\n
                this.startAngle = _calcAngle(params.x1, params.y1);\n
                this.endAngle = _calcAngle(params.x2, params.y2);            \n
                this.x1 = params.x1;\n
                this.y1 = params.y1;\n
                this.x2 = params.x2;\n
                this.y2 = params.y2;            \n
            }\n
            \n
            if (this.endAngle < 0) this.endAngle += TWO_PI;\n
            if (this.startAngle < 0) this.startAngle += TWO_PI;   \n
\n
            // segment is used by vml     \n
            this.segment = Biltong.quadrant([this.x1, this.y1], [this.x2, this.y2]);\n
            \n
            // we now have startAngle and endAngle as positive numbers, meaning the\n
            // absolute difference (|d|) between them is the sweep (s) of this arc, unless the\n
            // arc is \'anticlockwise\' in which case \'s\' is given by 2PI - |d|.\n
            \n
            var ea = this.endAngle < this.startAngle ? this.endAngle + TWO_PI : this.endAngle;\n
            this.sweep = Math.abs (ea - this.startAngle);\n
            if (this.anticlockwise) this.sweep = TWO_PI - this.sweep;\n
            var circumference = 2 * Math.PI * this.radius,\n
                frac = this.sweep / TWO_PI,\n
                length = circumference * frac;\n
            \n
            this.getLength = function() {\n
                return length;\n
            };\n
\n
            this.getBounds = function() {\n
                return {\n
                    minX:params.cx - params.r,\n
                    maxX:params.cx + params.r,\n
                    minY:params.cy - params.r,\n
                    maxY:params.cy + params.r\n
                };\n
            };\n
            \n
            var VERY_SMALL_VALUE = 0.0000000001,\n
                gentleRound = function(n) {\n
                    var f = Math.floor(n), r = Math.ceil(n);\n
                    if (n - f < VERY_SMALL_VALUE) \n
                        return f;    \n
                    else if (r - n < VERY_SMALL_VALUE)\n
                        return r;\n
                    return n;\n
                };\n
            \n
            /**\n
             * returns the point on the segment\'s path that is \'location\' along the length of the path, where \'location\' is a decimal from\n
             * 0 to 1 inclusive. \n
             */\n
            this.pointOnPath = function(location, absolute) {            \n
                \n
                if (location === 0) {\n
                    return { x:this.x1, y:this.y1, theta:this.startAngle };    \n
                }\n
                else if (location == 1) {\n
                    return { x:this.x2, y:this.y2, theta:this.endAngle };                    \n
                }\n
                \n
                if (absolute) {\n
                    location = location / length;\n
                }\n
    \n
                var angle = _calcAngleForLocation(this, location),\n
                    _x = params.cx + (params.r * Math.cos(angle)),\n
                    _y  = params.cy + (params.r * Math.sin(angle));\t\t\t\t\t\n
    \n
                return { x:gentleRound(_x), y:gentleRound(_y), theta:angle };\n
            };\n
            \n
            /**\n
             * returns the gradient of the segment at the given point.\n
             */\n
            this.gradientAtPoint = function(location, absolute) {\n
                var p = this.pointOnPath(location, absolute);\n
                var m = Biltong.normal( [ params.cx, params.cy ], [p.x, p.y ] );\n
                if (!this.anticlockwise && (m == Infinity || m == -Infinity)) m *= -1;\n
                return m;\n
            };\t              \n
                    \n
            this.pointAlongPathFrom = function(location, distance, absolute) {\n
                var p = this.pointOnPath(location, absolute),\n
                    arcSpan = distance / circumference * 2 * Math.PI,\n
                    dir = this.anticlockwise ? -1 : 1,\n
                    startAngle = p.theta + (dir * arcSpan),\t\t\t\t\n
                    startX = params.cx + (this.radius * Math.cos(startAngle)),\n
                    startY = params.cy + (this.radius * Math.sin(startAngle));\t\n
    \n
                return {x:startX, y:startY};\n
            };\t            \n
        },\n
\t\n
        Bezier : function(params) {\n
            var _super = jsPlumb.Segments.AbstractSegment.apply(this, arguments),\n
                curve = [\t\n
                    { x:params.x1, y:params.y1},\n
                    { x:params.cp1x, y:params.cp1y },\n
                    { x:params.cp2x, y:params.cp2y },\n
                    { x:params.x2, y:params.y2 }\n
                ],\n
                // although this is not a strictly rigorous determination of bounds\n
                // of a bezier curve, it works for the types of curves that this segment\n
                // type produces.\n
                bounds = {\n
                    minX:Math.min(params.x1, params.x2, params.cp1x, params.cp2x),\n
                    minY:Math.min(params.y1, params.y2, params.cp1y, params.cp2y),\n
                    maxX:Math.max(params.x1, params.x2, params.cp1x, params.cp2x),\n
                    maxY:Math.max(params.y1, params.y2, params.cp1y, params.cp2y)\n
                };\n
                \n
            this.type = "Bezier";            \n
            \n
            var _translateLocation = function(_curve, location, absolute) {\n
                if (absolute)\n
                    location = jsBezier.locationAlongCurveFrom(_curve, location > 0 ? 0 : 1, location);\n
    \n
                return location;\n
            };\t\t\n
            \n
            /**\n
             * returns the point on the segment\'s path that is \'location\' along the length of the path, where \'location\' is a decimal from\n
             * 0 to 1 inclusive. \n
             */\n
            this.pointOnPath = function(location, absolute) {\n
                location = _translateLocation(curve, location, absolute);                \n
                return jsBezier.pointOnCurve(curve, location);\n
            };\n
            \n
            /**\n
             * returns the gradient of the segment at the given point.\n
             */\n
            this.gradientAtPoint = function(location, absolute) {\n
                location = _translateLocation(curve, location, absolute);\n
                return jsBezier.gradientAtPoint(curve, location);        \t\n
            };\t              \n
            \n
            this.pointAlongPathFrom = function(location, distance, absolute) {\n
                location = _translateLocation(curve, location, absolute);\n
                return jsBezier.pointAlongCurveFrom(curve, location, distance);\n
            };\n
            \n
            this.getLength = function() {\n
                return jsBezier.getLength(curve);\t\t\t\t\n
            };\n
\n
            this.getBounds = function() {\n
                return bounds;\n
            };\n
        }\n
    };\n
\n
\t/*\n
\t\tClass: AbstractComponent\n
\t\tSuperclass for AbstractConnector and AbstractEndpoint.\n
\t*/\n
\tvar AbstractComponent = function() {\n
\t\tthis.resetBounds = function() {\n
\t\t\tthis.bounds = { minX:Infinity, minY:Infinity, maxX:-Infinity, maxY:-Infinity };\n
\t\t};\n
\t\tthis.resetBounds();\n
\t};\n
\n
\t/*\n
\t * Class: AbstractConnector\n
\t * Superclass for all Connectors; here is where Segments are managed.  This is exposed on jsPlumb just so it\n
\t * can be accessed from other files. You should not try to instantiate one of these directly.\n
\t *\n
\t * When this class is asked for a pointOnPath, or gradient etc, it must first figure out which segment to dispatch\n
\t * that request to. This is done by keeping track of the total connector length as segments are added, and also\n
\t * their cumulative ratios to the total length.  Then when the right segment is found it is a simple case of dispatching\n
\t * the request to it (and adjusting \'location\' so that it is relative to the beginning of that segment.)\n
\t */ \n
\tjsPlumb.Connectors.AbstractConnector = function(params) {\n
\t\t\n
\t\tAbstractComponent.apply(this, arguments);\n
\n
\t\tvar segments = [],\n
\t\t\tediting = false,\n
\t\t\ttotalLength = 0,\n
\t\t\tsegmentProportions = [],\n
\t\t\tsegmentProportionalLengths = [],\n
\t\t\tstub = params.stub || 0, \n
\t\t\tsourceStub = jsPlumbUtil.isArray(stub) ? stub[0] : stub,\n
\t\t\ttargetStub = jsPlumbUtil.isArray(stub) ? stub[1] : stub,\n
\t\t\tgap = params.gap || 0,\n
\t\t\tsourceGap = jsPlumbUtil.isArray(gap) ? gap[0] : gap,\n
\t\t\ttargetGap = jsPlumbUtil.isArray(gap) ? gap[1] : gap,\n
\t\t\tuserProvidedSegments = null,\n
\t\t\tedited = false,\n
\t\t\tpaintInfo = null;\n
\n
\t\t// subclasses should override.\n
\t\tthis.isEditable = function() { return false; };\n
\t\tthis.setEdited = function(ed) { edited = ed; };\n
\n
\t\t// to be overridden by subclasses.\n
\t\tthis.getPath = function() { };\n
\t\tthis.setPath = function(path) { };\n
        \n
        /**\n
        * Function: findSegmentForPoint\n
        * Returns the segment that is closest to the given [x,y],\n
        * null if nothing found.  This function returns a JS \n
        * object with:\n
        *\n
        *   d   -   distance from segment\n
        *   l   -   proportional location in segment\n
        *   x   -   x point on the segment\n
        *   y   -   y point on the segment\n
        *   s   -   the segment itself.\n
        */ \n
        this.findSegmentForPoint = function(x, y) {\n
            var out = { d:Infinity, s:null, x:null, y:null, l:null };\n
            for (var i = 0; i < segments.length; i++) {\n
                var _s = segments[i].findClosestPointOnPath(x, y);\n
                if (_s.d < out.d) {\n
                    out.d = _s.d; \n
                    out.l = _s.l; \n
                    out.x = _s.x;\n
                    out.y = _s.y; \n
                    out.s = segments[i];\n
                    out.x1 = _s.x1;\n
                    out.x2 = _s.x2;\n
                    out.y1 = _s.y1;\n
                    out.y2 = _s.y2;\n
                    out.index = i;\n
                }\n
            }\n
            \n
            return out;\n
        };\n
\n
\t\tvar _updateSegmentProportions = function() {\n
                var curLoc = 0;\n
                for (var i = 0; i < segments.length; i++) {\n
                    var sl = segments[i].getLength();\n
                    segmentProportionalLengths[i] = sl / totalLength;\n
                    segmentProportions[i] = [curLoc, (curLoc += (sl / totalLength)) ];\n
                }\n
            },\n
\t\t\n
            /**\n
             * returns [segment, proportion of travel in segment, segment index] for the segment \n
             * that contains the point which is \'location\' distance along the entire path, where \n
             * \'location\' is a decimal between 0 and 1 inclusive. in this connector type, paths \n
             * are made up of a list of segments, each of which contributes some fraction to\n
             * the total length. \n
             * From 1.3.10 this also supports the \'absolute\' property, which lets us specify a location\n
             * as the absolute distance in pixels, rather than a proportion of the total path. \n
             */\n
            _findSegmentForLocation = function(location, absolute) {\n
\t\t\t\tif (absolute) {\n
\t\t\t\t\tlocation = location > 0 ? location / totalLength : (totalLength + location) / totalLength;\n
\t\t\t\t}\n
\t\t\t\tvar idx = segmentProportions.length - 1, inSegmentProportion = 1;\n
\t\t\t\tfor (var i = 0; i < segmentProportions.length; i++) {\n
\t\t\t\t\tif (segmentProportions[i][1] >= location) {\n
\t\t\t\t\t\tidx = i;\n
\t\t\t\t\t\t// todo is this correct for all connector path types?\n
\t\t\t\t\t\tinSegmentProportion = location == 1 ? 1 : location === 0 ? 0 : (location - segmentProportions[i][0]) / segmentProportionalLengths[i];                    \n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\treturn { segment:segments[idx], proportion:inSegmentProportion, index:idx };\n
\t\t\t},\n
\t\t\t_addSegment = function(conn, type, params) {\n
\t\t\t\tif (params.x1 == params.x2 && params.y1 == params.y2) return;\n
\t\t\t\tvar s = new jsPlumb.Segments[type](params);\n
\t\t\t\tsegments.push(s);\n
\t\t\t\ttotalLength += s.getLength();\n
\t\t\t\tconn.updateBounds(s);\n
\t\t\t},\n
\t\t\t_clearSegments = function() {\n
\t\t\t\ttotalLength = segments.length = segmentProportions.length = segmentProportionalLengths.length = 0;\n
\t\t\t};\n
\n
\t\tthis.setSegments = function(_segs) {\n
\t\t\tuserProvidedSegments = [];\n
\t\t\ttotalLength = 0;\n
\t\t\tfor (var i = 0; i < _segs.length; i++) {\n
\t\t\t\tuserProvidedSegments.push(_segs[i]);\n
\t\t\t\ttotalLength += _segs[i].getLength();\n
\t\t\t}\n
\t\t};\n
\n
        var _prepareCompute = function(params) {\n
            this.lineWidth = params.lineWidth;\n
            var segment = Biltong.quadrant(params.sourcePos, params.targetPos),\n
                swapX = params.targetPos[0] < params.sourcePos[0],\n
                swapY = params.targetPos[1] < params.sourcePos[1],\n
                lw = params.lineWidth || 1,       \n
                so = params.sourceEndpoint.anchor.getOrientation(params.sourceEndpoint), \n
                to = params.targetEndpoint.anchor.getOrientation(params.targetEndpoint),\n
                x = swapX ? params.targetPos[0] : params.sourcePos[0], \n
                y = swapY ? params.targetPos[1] : params.sourcePos[1],\n
                w = Math.abs(params.targetPos[0] - params.sourcePos[0]),\n
                h = Math.abs(params.targetPos[1] - params.sourcePos[1]);\n
\t\t\t\n
            // SP: an early attempy at fixing #162; this fix caused #177, so reverted.\t\n
\t\t\t//if (w == 0) w = 1;\n
\t\t\t//if (h == 0) h = 1;\n
            \n
            // if either anchor does not have an orientation set, we derive one from their relative\n
            // positions.  we fix the axis to be the one in which the two elements are further apart, and\n
            // point each anchor at the other element.  this is also used when dragging a new connection.\n
            if (so[0] === 0 && so[1] === 0 || to[0] === 0 && to[1] === 0) {\n
                var index = w > h ? 0 : 1, oIndex = [1,0][index];\n
                so = []; to = [];\n
                so[index] = params.sourcePos[index] > params.targetPos[index] ? -1 : 1;\n
                to[index] = params.sourcePos[index] > params.targetPos[index] ? 1 : -1;\n
                so[oIndex] = 0; to[oIndex] = 0;\n
            }                    \n
            \n
            var sx = swapX ? w + (sourceGap * so[0])  : sourceGap * so[0], \n
                sy = swapY ? h + (sourceGap * so[1])  : sourceGap * so[1], \n
                tx = swapX ? targetGap * to[0] : w + (targetGap * to[0]),\n
                ty = swapY ? targetGap * to[1] : h + (targetGap * to[1]),\n
                oProduct = ((so[0] * to[0]) + (so[1] * to[1]));        \n
            \n
            var result = {\n
                sx:sx, sy:sy, tx:tx, ty:ty, lw:lw, \n
                xSpan:Math.abs(tx - sx),\n
                ySpan:Math.abs(ty - sy),                \n
                mx:(sx + tx) / 2,\n
                my:(sy + ty) / 2,                \n
                so:so, to:to, x:x, y:y, w:w, h:h,\n
                segment : segment,\n
                startStubX : sx + (so[0] * sourceStub), \n
                startStubY : sy + (so[1] * sourceStub),\n
                endStubX : tx + (to[0] * targetStub), \n
                endStubY : ty + (to[1] * targetStub),\n
                isXGreaterThanStubTimes2 : Math.abs(sx - tx) > (sourceStub + targetStub),\n
                isYGreaterThanStubTimes2 : Math.abs(sy - ty) > (sourceStub + targetStub),\n
                opposite:oProduct == -1,\n
                perpendicular:oProduct === 0,\n
                orthogonal:oProduct == 1,\n
                sourceAxis : so[0] === 0 ? "y" : "x",\n
                points:[x, y, w, h, sx, sy, tx, ty ]\n
            };\n
            result.anchorOrientation = result.opposite ? "opposite" : result.orthogonal ? "orthogonal" : "perpendicular";\n
            return result;\n
        };\n
\t\t\n
\t\tthis.getSegments = function() { return segments; };\n
\n
        this.updateBounds = function(segment) {\n
            var segBounds = segment.getBounds();\n
            this.bounds.minX = Math.min(this.bounds.minX, segBounds.minX);\n
            this.bounds.maxX = Math.max(this.bounds.maxX, segBounds.maxX);\n
            this.bounds.minY = Math.min(this.bounds.minY, segBounds.minY);\n
            this.bounds.maxY = Math.max(this.bounds.maxY, segBounds.maxY);              \n
        };\n
        \n
        var dumpSegmentsToConsole = function() {\n
            console.log("SEGMENTS:");\n
            for (var i = 0; i < segments.length; i++) {\n
                console.log(segments[i].type, segments[i].getLength(), segmentProportions[i]);\n
            }\n
        };\n
\n
\t\tthis.pointOnPath = function(location, absolute) {\n
            var seg = _findSegmentForLocation(location, absolute);\n
            return seg.segment && seg.segment.pointOnPath(seg.proportion, false) || [0,0];\n
        };\n
        \n
        this.gradientAtPoint = function(location, absolute) {\n
            var seg = _findSegmentForLocation(location, absolute);          \n
            return seg.segment && seg.segment.gradientAtPoint(seg.proportion, false) || 0;\n
        };\n
        \n
        this.pointAlongPathFrom = function(location, distance, absolute) {\n
            var seg = _findSegmentForLocation(location, absolute);\n
            // TODO what happens if this crosses to the next segment?\n
            return seg.segment && seg.segment.pointAlongPathFrom(seg.proportion, distance, false) || [0,0];\n
        };\n
\t\t\n
\t\tthis.compute = function(params)  {\n
            if (!edited)\n
                paintInfo = _prepareCompute.call(this, params);\n
            \n
            _clearSegments();\n
            this._compute(paintInfo, params);\n
            this.x = paintInfo.points[0];\n
            this.y = paintInfo.points[1];\n
            this.w = paintInfo.points[2];\n
            this.h = paintInfo.points[3];               \n
            this.segment = paintInfo.segment;         \n
            _updateSegmentProportions();            \n
\t\t};\n
\t\t\n
\t\treturn {\n
\t\t\taddSegment:_addSegment,\n
            prepareCompute:_prepareCompute,\n
            sourceStub:sourceStub,\n
            targetStub:targetStub,\n
            maxStub:Math.max(sourceStub, targetStub),            \n
            sourceGap:sourceGap,\n
            targetGap:targetGap,\n
            maxGap:Math.max(sourceGap, targetGap)\n
\t\t};\t\t\n
\t};\n
    jsPlumbUtil.extend(jsPlumb.Connectors.AbstractConnector, AbstractComponent);\n
\t\n
    /**\n
     * Class: Connectors.Straight\n
     * The Straight connector draws a simple straight line between the two anchor points.  It does not have any constructor parameters.\n
     */\n
    var Straight = jsPlumb.Connectors.Straight = function() {\n
    \tthis.type = "Straight";\n
\t\tvar _super =  jsPlumb.Connectors.AbstractConnector.apply(this, arguments);\t\t\n
\n
        this._compute = function(paintInfo, _) {                        \n
            _super.addSegment(this, "Straight", {x1:paintInfo.sx, y1:paintInfo.sy, x2:paintInfo.startStubX, y2:paintInfo.startStubY});                                                \n
            _super.addSegment(this, "Straight", {x1:paintInfo.startStubX, y1:paintInfo.startStubY, x2:paintInfo.endStubX, y2:paintInfo.endStubY});                        \n
            _super.addSegment(this, "Straight", {x1:paintInfo.endStubX, y1:paintInfo.endStubY, x2:paintInfo.tx, y2:paintInfo.ty});                                    \n
        };                    \n
    };\n
    jsPlumbUtil.extend(jsPlumb.Connectors.Straight, jsPlumb.Connectors.AbstractConnector);\n
    jsPlumb.registerConnectorType(Straight, "Straight");\n
\n
\n
 // ********************************* END OF CONNECTOR TYPES *******************************************************************\n
    \n
 // ********************************* ENDPOINT TYPES *******************************************************************\n
    \n
    jsPlumb.Endpoints.AbstractEndpoint = function(params) {\n
        AbstractComponent.apply(this, arguments);\n
        var compute = this.compute = function(anchorPoint, orientation, endpointStyle, connectorPaintStyle) {    \n
            var out = this._compute.apply(this, arguments);\n
            this.x = out[0];\n
            this.y = out[1];\n
            this.w = out[2];\n
            this.h = out[3];\n
            this.bounds.minX = this.x;\n
            this.bounds.minY = this.y;\n
            this.bounds.maxX = this.x + this.w;\n
            this.bounds.maxY = this.y + this.h;\n
            return out;\n
        };\n
        return {\n
            compute:compute,\n
            cssClass:params.cssClass\n
        };\n
    };\n
    jsPlumbUtil.extend(jsPlumb.Endpoints.AbstractEndpoint, AbstractComponent);\n
    \n
    /**\n
     * Class: Endpoints.Dot\n
     * A round endpoint, with default radius 10 pixels.\n
     */    \t\n
    \t\n
\t/**\n
\t * Function: Constructor\n
\t * \n
\t * Parameters:\n
\t * \n
\t * \tradius\t-\tradius of the endpoint.  defaults to 10 pixels.\n
\t */\n
\tjsPlumb.Endpoints.Dot = function(params) {        \n
\t\tthis.type = "Dot";\n
\t\tvar _super = jsPlumb.Endpoints.AbstractEndpoint.apply(this, arguments);\n
\t\tparams = params || {};\t\t\t\t\n
\t\tthis.radius = params.radius || 10;\n
\t\tthis.defaultOffset = 0.5 * this.radius;\n
\t\tthis.defaultInnerRadius = this.radius / 3;\t\t\t\n
\t\t\n
\t\tthis._compute = function(anchorPoint, orientation, endpointStyle, connectorPaintStyle) {\n
\t\t\tthis.radius = endpointStyle.radius || this.radius;\n
\t\t\tvar\tx = anchorPoint[0] - this.radius,\n
\t\t\t\ty = anchorPoint[1] - this.radius,\n
                w = this.radius * 2,\n
                h = this.radius * 2;\n
\n
            if (endpointStyle.strokeStyle) {\n
                var lw = endpointStyle.lineWidth || 1;\n
                x -= lw;\n
                y -= lw;\n
                w += (lw * 2);\n
                h += (lw * 2);\n
            }\n
\t\t\treturn [ x, y, w, h, this.radius ];\n
\t\t};\n
\t};\n
    jsPlumbUtil.extend(jsPlumb.Endpoints.Dot, jsPlumb.Endpoints.AbstractEndpoint);\n
\n
\tjsPlumb.Endpoints.Rectangle = function(params) {\n
\t\tthis.type = "Rectangle";\n
\t\tvar _super = jsPlumb.Endpoints.AbstractEndpoint.apply(this, arguments);\n
\t\tparams = params || {};\n
\t\tthis.width = params.width || 20;\n
\t\tthis.height = params.height || 20;\n
\n
\t\tthis._compute = function(anchorPoint, orientation, endpointStyle, connectorPaintStyle) {\n
\t\t\tvar width = endpointStyle.width || this.width,\n
\t\t\t\theight = endpointStyle.height || this.height,\n
\t\t\t\tx = anchorPoint[0] - (width/2),\n
\t\t\t\ty = anchorPoint[1] - (height/2);\n
\n
\t\t\treturn [ x, y, width, height];\n
\t\t};\n
\t};\n
\tjsPlumbUtil.extend(jsPlumb.Endpoints.Rectangle, jsPlumb.Endpoints.AbstractEndpoint);\n
\n
\tvar DOMElementEndpoint = function(params) {\n
\t\tjsPlumb.DOMElementComponent.apply(this, arguments);\n
\t\tthis._jsPlumb.displayElements = [];\n
\t};\n
\tjsPlumbUtil.extend(DOMElementEndpoint, jsPlumb.DOMElementComponent, {\n
\t\tgetDisplayElements : function() { \n
\t\t\treturn this._jsPlumb.displayElements; \n
\t\t},\n
\t\tappendDisplayElement : function(el) {\n
\t\t\tthis._jsPlumb.displayElements.push(el);\n
\t\t}\n
\t});\n
\n
\t/**\n
\t * Class: Endpoints.Image\n
\t * Draws an image as the Endpoint.\n
\t */\n
\t/**\n
\t * Function: Constructor\n
\t * \n
\t * Parameters:\n
\t * \n
\t * \tsrc\t-\tlocation of the image to use.\n
\n
    TODO: multiple references to self. not sure quite how to get rid of them entirely. perhaps self = null in the cleanup\n
    function will suffice\n
\n
    TODO this class still leaks memory.\n
\n
\t */\n
\tjsPlumb.Endpoints.Image = function(params) {\n
\n
\t\tthis.type = "Image";\n
\t\tDOMElementEndpoint.apply(this, arguments);\n
\t\tjsPlumb.Endpoints.AbstractEndpoint.apply(this, arguments);\n
\n
\t\tvar _onload = params.onload, \n
\t\t\tsrc = params.src || params.url,\n
\t\t\tclazz = params.cssClass ? " " + params.cssClass : "";\n
\n
\t\tthis._jsPlumb.img = new Image();\n
\t\tthis._jsPlumb.ready = false;\n
\t\tthis._jsPlumb.initialized = false;\n
\t\tthis._jsPlumb.deleted = false;\n
\t\tthis._jsPlumb.widthToUse = params.width;\n
\t\tthis._jsPlumb.heightToUse = params.height;\n
\t\tthis._jsPlumb.endpoint = params.endpoint;\n
\n
\t\tthis._jsPlumb.img.onload = function() {\n
\t\t\tif (this._jsPlumb != null) {\n
\t\t\t\tthis._jsPlumb.ready = true;\n
\t\t\t\tthis._jsPlumb.widthToUse = this._jsPlumb.widthToUse || this._jsPlumb.img.width;\n
\t\t\t\tthis._jsPlumb.heightToUse = this._jsPlumb.heightToUse || this._jsPlumb.img.height;\n
\t\t\t\tif (_onload) {\n
\t\t\t\t\t_onload(this);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}.bind(this);\n
\n
        /*\n
            Function: setImage\n
            Sets the Image to use in this Endpoint.  \n
\n
            Parameters:\n
            img         -   may be a URL or an Image object\n
            onload      -   optional; a callback to execute once the image has loaded.\n
        */\n
        this._jsPlumb.endpoint.setImage = function(_img, onload) {\n
            var s = _img.constructor == String ? _img : _img.src;\n
            _onload = onload; \n
            this._jsPlumb.img.src = s;\n
\n
            if (this.canvas != null)\n
                this.canvas.setAttribute("src", this._jsPlumb.img.src);\n
        }.bind(this);\n
\n
\t\tthis._jsPlumb.endpoint.setImage(src, _onload);\n
\t\tthis._compute = function(anchorPoint, orientation, endpointStyle, connectorPaintStyle) {\n
\t\t\tthis.anchorPoint = anchorPoint;\n
\t\t\tif (this._jsPlumb.ready) return [anchorPoint[0] - this._jsPlumb.widthToUse / 2, anchorPoint[1] - this._jsPlumb.heightToUse / 2, \n
\t\t\t\t\t\t\t\t\tthis._jsPlumb.widthToUse, this._jsPlumb.heightToUse];\n
\t\t\telse return [0,0,0,0];\n
\t\t};\n
\t\t\n
\t\tthis.canvas = document.createElement("img");\n
\t\tthis.canvas.style.margin = 0;\n
\t\tthis.canvas.style.padding = 0;\n
\t\tthis.canvas.style.outline = 0;\n
\t\tthis.canvas.style.position = "absolute";\t\t\n
\t\tthis.canvas.className = this._jsPlumb.instance.endpointClass + clazz;\n
\t\tif (this._jsPlumb.widthToUse) this.canvas.setAttribute("width", this._jsPlumb.widthToUse);\n
\t\tif (this._jsPlumb.heightToUse) this.canvas.setAttribute("height", this._jsPlumb.heightToUse);\t\t\n
\t\tthis._jsPlumb.instance.appendElement(this.canvas);\n
\t\tthis.attachListeners(this.canvas, this);\n
\t\t\n
\t\tthis.actuallyPaint = function(d, style, anchor) {\n
\t\t\tif (!this._jsPlumb.deleted) {\n
\t\t\t\tif (!this._jsPlumb.initialized) {\n
\t\t\t\t\tthis.canvas.setAttribute("src", this._jsPlumb.img.src);\n
\t\t\t\t\tthis.appendDisplayElement(this.canvas);\n
\t\t\t\t\tthis._jsPlumb.initialized = true;\n
\t\t\t\t}\n
\t\t\t\tvar x = this.anchorPoint[0] - (this._jsPlumb.widthToUse / 2),\n
\t\t\t\t\ty = this.anchorPoint[1] - (this._jsPlumb.heightToUse / 2);\n
\t\t\t\tjsPlumbUtil.sizeElement(this.canvas, x, y, this._jsPlumb.widthToUse, this._jsPlumb.heightToUse);\n
\t\t\t}\n
\t\t};\n
\t\t\n
\t\tthis.paint = function(style, anchor) {\n
            if (this._jsPlumb != null) {  // may have been deleted\n
    \t\t\tif (this._jsPlumb.ready) {\n
        \t\t\tthis.actuallyPaint(style, anchor);\n
    \t\t\t}\n
    \t\t\telse { \n
    \t\t\t\twindow.setTimeout(function() {\n
    \t\t\t\t\tthis.paint(style, anchor);\n
    \t\t\t\t}.bind(this), 200);\n
    \t\t\t}\n
            }\n
\t\t};\t\t\t\t\n
\t};\n
    jsPlumbUtil.extend(jsPlumb.Endpoints.Image, [ DOMElementEndpoint, jsPlumb.Endpoints.AbstractEndpoint ], {\n
        cleanup : function() {            \n
            this._jsPlumb.deleted = true;\n
            if (this.canvas) this.canvas.parentNode.removeChild(this.canvas);\n
            this.canvas = null;\n
        } \n
    });\n
\t\n
\t/*\n
\t * Class: Endpoints.Blank\n
\t * An Endpoint that paints nothing (visible) on the screen.  Supports cssClass and hoverClass parameters like all Endpoints.\n
\t */\n
\tjsPlumb.Endpoints.Blank = function(params) {\n
\t\tvar _super = jsPlumb.Endpoints.AbstractEndpoint.apply(this, arguments);\n
\t\tthis.type = "Blank";\n
\t\tDOMElementEndpoint.apply(this, arguments);\t\t\n
\t\tthis._compute = function(anchorPoint, orientation, endpointStyle, connectorPaintStyle) {\n
\t\t\treturn [anchorPoint[0], anchorPoint[1],10,0];\n
\t\t};\n
\t\t\n
\t\tthis.canvas = document.createElement("div");\n
\t\tthis.canvas.style.display = "block";\n
\t\tthis.canvas.style.width = "1px";\n
\t\tthis.canvas.style.height = "1px";\n
\t\tthis.canvas.style.background = "transparent";\n
\t\tthis.canvas.style.position = "absolute";\n
\t\tthis.canvas.className = this._jsPlumb.endpointClass;\n
\t\tjsPlumb.appendElement(this.canvas);\n
\t\t\n
\t\tthis.paint = function(style, anchor) {\n
\t\t\tjsPlumbUtil.sizeElement(this.canvas, this.x, this.y, this.w, this.h);\t\n
\t\t};\n
\t};\n
    jsPlumbUtil.extend(jsPlumb.Endpoints.Blank, [jsPlumb.Endpoints.AbstractEndpoint, DOMElementEndpoint], {\n
        cleanup:function() {\n
            if (this.canvas && this.canvas.parentNode) {\n
                this.canvas.parentNode.removeChild(this.canvas);\n
            }\n
        }\n
    });\n
\t\n
\t/*\n
\t * Class: Endpoints.Triangle\n
\t * A triangular Endpoint.  \n
\t */\n
\t/*\n
\t * Function: Constructor\n
\t * \n
\t * Parameters:\n
\t * \n
\t * \twidth\t-\twidth of the triangle\'s base.  defaults to 55 pixels.\n
\t * \theight\t-\theight of the triangle from base to apex.  defaults to 55 pixels.\n
\t */\n
\tjsPlumb.Endpoints.Triangle = function(params) {        \n
\t\tthis.type = "Triangle";\n
        var _super = jsPlumb.Endpoints.AbstractEndpoint.apply(this, arguments);\n
\t\tparams = params || {  };\n
\t\tparams.width = params.width || 55;\n
\t\tparams.height = params.height || 55;\n
\t\tthis.width = params.width;\n
\t\tthis.height = params.height;\n
\t\tthis._compute = function(anchorPoint, orientation, endpointStyle, connectorPaintStyle) {\n
\t\t\tvar width = endpointStyle.width || self.width,\n
\t\t\theight = endpointStyle.height || self.height,\n
\t\t\tx = anchorPoint[0] - (width/2),\n
\t\t\ty = anchorPoint[1] - (height/2);\n
\t\t\treturn [ x, y, width, height ];\n
\t\t};\n
\t};\n
// ********************************* END OF ENDPOINT TYPES *******************************************************************\n
\t\n
\n
// ********************************* OVERLAY DEFINITIONS ***********************************************************************    \n
\n
\tvar AbstractOverlay = jsPlumb.Overlays.AbstractOverlay = function(params) {\n
\t\tthis.visible = true;\n
        this.isAppendedAtTopLevel = true;\n
\t\tthis.component = params.component;\n
\t\tthis.loc = params.location == null ? 0.5 : params.location;\n
        this.endpointLoc = params.endpointLocation == null ? [ 0.5, 0.5] : params.endpointLocation;\t\t\n
\t};\n
    AbstractOverlay.prototype = {\n
        cleanup:function() {  \n
           this.component = null;\n
           this.canvas = null;\n
           this.endpointLoc = null;\n
        },\n
        setVisible : function(val) { \n
            this.visible = val;\n
            this.component.repaint();\n
        },\n
        isVisible : function() { return this.visible; },\n
        hide : function() { this.setVisible(false); },\n
        show : function() { this.setVisible(true); },        \n
        incrementLocation : function(amount) {\n
            this.loc += amount;\n
            this.component.repaint();\n
        },\n
        setLocation : function(l) {\n
            this.loc = l;\n
            this.component.repaint();\n
        },\n
        getLocation : function() {\n
            return this.loc;\n
        }\n
    };\n
\t\n
\t\n
\t/*\n
\t * Class: Overlays.Arrow\n
\t * \n
\t * An arrow overlay, defined by four points: the head, the two sides of the tail, and a \'foldback\' point at some distance along the length\n
\t * of the arrow that lines from each tail point converge into.  The foldback point is defined using a decimal that indicates some fraction\n
\t * of the length of the arrow and has a default value of 0.623.  A foldback point value of 1 would mean that the arrow had a straight line\n
\t * across the tail.  \n
\t */\n
\t/*\n
\t * Function: Constructor\n
\t * \n
\t * Parameters:\n
\t * \n
\t * \tlength - distance in pixels from head to tail baseline. default 20.\n
\t * \twidth - width in pixels of the tail baseline. default 20.\n
\t * \tfillStyle - style to use when filling the arrow.  defaults to "black".\n
\t * \tstrokeStyle - style to use when stroking the arrow. defaults to null, which means the arrow is not stroked.\n
\t * \tlineWidth - line width to use when stroking the arrow. defaults to 1, but only used if strokeStyle is not null.\n
\t * \tfoldback - distance (as a decimal from 0 to 1 inclusive) along the length of the arrow marking the point the tail points should fold back to.  defaults to 0.623.\n
\t * \tlocation - distance (as a decimal from 0 to 1 inclusive) marking where the arrow should sit on the connector. defaults to 0.5.\n
\t * \tdirection - indicates the direction the arrow points in. valid values are -1 and 1; 1 is default.\n
\t */\n
\tjsPlumb.Overlays.Arrow = function(params) {\n
\t\tthis.type = "Arrow";\n
\t\tAbstractOverlay.apply(this, arguments);\n
        this.isAppendedAtTopLevel = false;\n
\t\tparams = params || {};\n
\t\tvar _ju = jsPlumbUtil, _jg = Biltong;\n
\t\t\n
    \tthis.length = params.length || 20;\n
    \tthis.width = params.width || 20;\n
    \tthis.id = params.id;\n
    \tvar direction = (params.direction || 1) < 0 ? -1 : 1,\n
    \t    paintStyle = params.paintStyle || { lineWidth:1 },\n
    \t    // how far along the arrow the lines folding back in come to. default is 62.3%.\n
    \t    foldback = params.foldback || 0.623;\n
    \t    \t\n
    \tthis.computeMaxSize = function() { return self.width * 1.5; };    \t\n
    \t//this.cleanup = function() { };  // nothing to clean up for Arrows    \n
    \tthis.draw = function(component, currentConnectionPaintStyle) {\n
\n
            var hxy, mid, txy, tail, cxy;\n
            if (component.pointAlongPathFrom) {\n
\n
                if (_ju.isString(this.loc) || this.loc > 1 || this.loc < 0) {                    \n
                    var l = parseInt(this.loc, 10),\n
                        fromLoc = this.loc < 0 ? 1 : 0;\n
                    hxy = component.pointAlongPathFrom(fromLoc, l, false);\n
                    mid = component.pointAlongPathFrom(fromLoc, l - (direction * this.length / 2), false);\n
                    txy = _jg.pointOnLine(hxy, mid, this.length);\n
                }\n
                else if (this.loc == 1) {                \n
\t\t\t\t\thxy = component.pointOnPath(this.loc);\t\t\t\t\t           \n
                    mid = component.pointAlongPathFrom(this.loc, -(this.length));\n
\t\t\t\t\ttxy = _jg.pointOnLine(hxy, mid, this.length);\n
\t\t\t\t\t\n
\t\t\t\t\tif (direction == -1) {\n
\t\t\t\t\t\tvar _ = txy;\n
\t\t\t\t\t\ttxy = hxy;\n
\t\t\t\t\t\thxy = _;\n
\t\t\t\t\t}\n
                }\n
                else if (this.loc === 0) {\t\t\t\t\t                    \n
\t\t\t\t\ttxy = component.pointOnPath(this.loc);                    \n
\t\t\t\t\tmid = component.pointAlongPathFrom(this.loc, this.length);                    \n
\t\t\t\t\thxy = _jg.pointOnLine(txy, mid, this.length);                    \n
\t\t\t\t\tif (direction == -1) {\n
\t\t\t\t\t\tvar __ = txy;\n
\t\t\t\t\t\ttxy = hxy;\n
\t\t\t\t\t\thxy = __;\n
\t\t\t\t\t}\n
                }\n
                else {                    \n
    \t\t\t    hxy = component.pointAlongPathFrom(this.loc, direction * this.length / 2);\n
                    mid = component.pointOnPath(this.loc);\n
                    txy = _jg.pointOnLine(hxy, mid, this.length);\n
                }\n
\n
                tail = _jg.perpendicularLineTo(hxy, txy, this.width);\n
                cxy = _jg.pointOnLine(hxy, txy, foldback * this.length);    \t\t\t\n
    \t\t\t\n
    \t\t\tvar d = { hxy:hxy, tail:tail, cxy:cxy },\n
    \t\t\t    strokeStyle = paintStyle.strokeStyle || currentConnectionPaintStyle.strokeStyle,\n
    \t\t\t    fillStyle = paintStyle.fillStyle || currentConnectionPaintStyle.strokeStyle,\n
    \t\t\t    lineWidth = paintStyle.lineWidth || currentConnectionPaintStyle.lineWidth,\n
                    info = {\n
                        component:component, \n
                        d:d, \n
                        lineWidth:lineWidth, \n
                        strokeStyle:strokeStyle, \n
                        fillStyle:fillStyle,\n
                        minX:Math.min(hxy.x, tail[0].x, tail[1].x),\n
                        maxX:Math.max(hxy.x, tail[0].x, tail[1].x),\n
                        minY:Math.min(hxy.y, tail[0].y, tail[1].y),\n
                        maxY:Math.max(hxy.y, tail[0].y, tail[1].y)\n
                    };    \t\t\t\n
\t\t\t\t\t\t    \n
                return info;\n
            }\n
            else return {component:component, minX:0,maxX:0,minY:0,maxY:0};\n
    \t};\n
    };    \n
    jsPlumbUtil.extend(jsPlumb.Overlays.Arrow, AbstractOverlay);      \n
    \n
    /*\n
     * Class: Overlays.PlainArrow\n
\t * \n
\t * A basic arrow.  This is in fact just one instance of the more generic case in which the tail folds back on itself to some\n
\t * point along the length of the arrow: in this case, that foldback point is the full length of the arrow.  so it just does\n
\t * a \'call\' to Arrow with foldback set appropriately.       \n
\t */\n
    /*\n
     * Function: Constructor\n
     * See <Overlays.Arrow> for allowed parameters for this overlay.\n
     */\n
    jsPlumb.Overlays.PlainArrow = function(params) {\n
    \tparams = params || {};    \t\n
    \tvar p = jsPlumb.extend(params, {foldback:1});\n
    \tjsPlumb.Overlays.Arrow.call(this, p);\n
    \tthis.type = "PlainArrow";\n
    };\n
    jsPlumbUtil.extend(jsPlumb.Overlays.PlainArrow, jsPlumb.Overlays.Arrow);\n
        \n
    /*\n
     * Class: Overlays.Diamond\n
     * \n
\t * A diamond. Like PlainArrow, this is a concrete case of the more generic case of the tail points converging on some point...it just\n
\t * happens that in this case, that point is greater than the length of the the arrow.    \n
\t * \n
\t *      this could probably do with some help with positioning...due to the way it reuses the Arrow paint code, what Arrow thinks is the\n
\t *      center is actually 1/4 of the way along for this guy.  but we don\'t have any knowledge of pixels at this point, so we\'re kind of\n
\t *      stuck when it comes to helping out the Arrow class. possibly we could pass in a \'transpose\' parameter or something. the value\n
\t *      would be -l/4 in this case - move along one quarter of the total length.\n
\t */\n
    /*\n
     * Function: Constructor\n
     * See <Overlays.Arrow> for allowed parameters for this overlay.\n
     */\n
    jsPlumb.Overlays.Diamond = function(params) {\n
    \tparams = params || {};    \t\n
    \tvar l = params.length || 40,\n
    \t    p = jsPlumb.extend(params, {length:l/2, foldback:2});\n
    \tjsPlumb.Overlays.Arrow.call(this, p);\n
    \tthis.type = "Diamond";\n
    };\n
    jsPlumbUtil.extend(jsPlumb.Overlays.Diamond, jsPlumb.Overlays.Arrow);\n
\n
    var _getDimensions = function(component) {\n
        if (component._jsPlumb.cachedDimensions == null)\n
            component._jsPlumb.cachedDimensions = component.getDimensions();\n
        return component._jsPlumb.cachedDimensions;\n
    };      \n
\t\n
\t// abstract superclass for overlays that add an element to the DOM.\n
    var AbstractDOMOverlay = function(params) {\n
\t\tjsPlumb.DOMElementComponent.apply(this, arguments);\n
    \tAbstractOverlay.apply(this, arguments);\n
\n
\t\tthis.id = params.id;\n
        this._jsPlumb.div = null;\n
        this._jsPlumb.initialised = false;\n
        this._jsPlumb.component = params.component;\n
        this._jsPlumb.cachedDimensions = null;\n
        this._jsPlumb.create = params.create;\n
\n
\t\tthis.getElement = function() {\n
\t\t\tif (this._jsPlumb.div == null) {\n
                var div = this._jsPlumb.div = jsPlumb.getDOMElement(this._jsPlumb.create(this._jsPlumb.component));\n
                div.style.position   =   "absolute";     \n
                var clazz = this._jsPlumb.instance.overlayClass + " " + \n
                    (this.cssClass ? this.cssClass : \n
                    params.cssClass ? params.cssClass : "");\n
                div.className = clazz;\n
                this._jsPlumb.instance.appendElement(div);\n
                this._jsPlumb.instance.getId(div);\n
                this.attachListeners(div, this);\n
                this.canvas = div;\n
\t\t\t}\n
    \t\treturn this._jsPlumb.div;\n
    \t};\n
\n
\t\tthis.draw = function(component, currentConnectionPaintStyle, absolutePosition) {\n
\t    \tvar td = _getDimensions(this);\n
\t    \tif (td != null && td.length == 2) {\n
\t\t\t\tvar cxy = { x:0,y:0 };\n
\n
                // absolutePosition would have been set by a call to connection.setAbsoluteOverlayPosition.\n
                if (absolutePosition) {\n
                    cxy = { x:absolutePosition[0], y:absolutePosition[1] };\n
                }\n
                else if (component.pointOnPath) {\n
                    var loc = this.loc, absolute = false;\n
                    if (jsPlumbUtil.isString(this.loc) || this.loc < 0 || this.loc > 1) {\n
                        loc = parseInt(this.loc, 10);\n
                        absolute = true;\n
                    }\n
                    cxy = component.pointOnPath(loc, absolute);  // a connection\n
                }\n
                else {\n
                    var locToUse = this.loc.constructor == Array ? this.loc : this.endpointLoc;\n
                    cxy = { x:locToUse[0] * component.w,\n
                            y:locToUse[1] * component.h };\n
                } \n
\n
\t\t\t\tvar minx = cxy.x - (td[0] / 2),\n
\t\t\t\t    miny = cxy.y - (td[1] / 2);\n
\n
                return {\n
                    component:component, \n
                    d:{ minx:minx, miny:miny, td:td, cxy:cxy },\n
                    minX:minx, \n
                    maxX:minx + td[0], \n
                    minY:miny, \n
                    maxY:miny + td[1]\n
                };\n
        \t}\n
\t    \telse return {minX:0,maxX:0,minY:0,maxY:0};\n
\t    };\n
\t};\n
    jsPlumbUtil.extend(AbstractDOMOverlay, [jsPlumb.DOMElementComponent, AbstractOverlay], {\n
        getDimensions : function() {\n
            return jsPlumb.getSize(this.getElement());\n
        },\n
        setVisible : function(state) {\n
            this._jsPlumb.div.style.display = state ? "block" : "none";\n
        },\n
        /*\n
         * Function: clearCachedDimensions\n
         * Clears the cached dimensions for the label. As a performance enhancement, label dimensions are\n
         * cached from 1.3.12 onwards. The cache is cleared when you change the label text, of course, but\n
         * there are other reasons why the text dimensions might change - if you make a change through CSS, for\n
         * example, you might change the font size.  in that case you should explicitly call this method.\n
         */\n
        clearCachedDimensions : function() {\n
            this._jsPlumb.cachedDimensions = null;\n
        },\n
        cleanup : function() {\n
            if (this._jsPlumb.div != null) \n
                this._jsPlumb.instance.removeElement(this._jsPlumb.div);\n
        },\n
        computeMaxSize : function() {\n
            var td = _getDimensions(this);\n
            return Math.max(td[0], td[1]);\n
        },\n
        reattachListeners : function(connector) {\n
            if (this._jsPlumb.div) {\n
                this.reattachListenersForElement(this._jsPlumb.div, this, connector);\n
            }\n
        },\n
        paint : function(p, containerExtents) {\n
            if (!this._jsPlumb.initialised) {\n
                this.getElement();\n
                p.component.appendDisplayElement(this._jsPlumb.div);\n
                this.attachListeners(this._jsPlumb.div, p.component);\n
                this._jsPlumb.initialised = true;\n
            }\n
            this._jsPlumb.div.style.left = (p.component.x + p.d.minx) + "px";\n
            this._jsPlumb.div.style.top = (p.component.y + p.d.miny) + "px";\n
        }\n
    });\n
\t\n
\t/*\n
     * Class: Overlays.Custom\n
     * A Custom overlay. You supply a \'create\' function which returns some DOM element, and jsPlumb positions it.\n
     * The \'create\' function is passed a Connection or Endpoint.\n
     */\n
    /*\n
     * Function: Constructor\n
     * \n
     * Parameters:\n
     * \tcreate - function for jsPlumb to call that returns a DOM element.\n
     * \tlocation - distance (as a decimal from 0 to 1 inclusive) marking where the label should sit on the connector. defaults to 0.5.\n
     * \tid - optional id to use for later retrieval of this overlay.\n
     * \t\n
     */\n
    jsPlumb.Overlays.Custom = function(params) {\n
    \tthis.type = "Custom";    \t\n
    \tAbstractDOMOverlay.apply(this, arguments);\t\t    \t        \t\t    \t    \t\t\n
    };\n
    jsPlumbUtil.extend(jsPlumb.Overlays.Custom, AbstractDOMOverlay);\n
\n
    jsPlumb.Overlays.GuideLines = function() {\n
        var self = this;\n
        self.length = 50;\n
        self.lineWidth = 5;\n
        this.type = "GuideLines";\n
        AbstractOverlay.apply(this, arguments);\n
        jsPlumb.jsPlumbUIComponent.apply(this, arguments);\n
        this.draw = function(connector, currentConnectionPaintStyle) {\n
\n
            var head = connector.pointAlongPathFrom(self.loc, self.length / 2),\n
                mid = connector.pointOnPath(self.loc),\n
                tail = Biltong.pointOnLine(head, mid, self.length),\n
                tailLine = Biltong.perpendicularLineTo(head, tail, 40),\n
                headLine = Biltong.perpendicularLineTo(tail, head, 20);\n
\n
            return {\n
                connector:connector,\n
                head:head,\n
                tail:tail,\n
                headLine:headLine,\n
                tailLine:tailLine,                \n
                minX:Math.min(head.x, tail.x, headLine[0].x, headLine[1].x), \n
                minY:Math.min(head.y, tail.y, headLine[0].y, headLine[1].y), \n
                maxX:Math.max(head.x, tail.x, headLine[0].x, headLine[1].x), \n
                maxY:Math.max(head.y, tail.y, headLine[0].y, headLine[1].y)\n
            };\n
        };\n
\n
       // this.cleanup = function() { };  // nothing to clean up for GuideLines\n
    };\n
    \n
    /*\n
     * Class: Overlays.Label\n
     \n
     */\n
    /*\n
     * Function: Constructor\n
     * \n
     * Parameters:\n
     * \tcssClass - optional css class string to append to css class. This string is appended "as-is", so you can of course have multiple classes\n
     *             defined.  This parameter is preferred to using labelStyle, borderWidth and borderStyle.\n
     * \tlabel - the label to paint.  May be a string or a function that returns a string.  Nothing will be painted if your label is null or your\n
     *         label function returns null.  empty strings _will_ be painted.\n
     * \tlocation - distance (as a decimal from 0 to 1 inclusive) marking where the label should sit on the connector. defaults to 0.5.\n
     * \tid - optional id to use for later retrieval of this overlay.\n
     * \n
     * \t\n
     */\n
    jsPlumb.Overlays.Label =  function(params) {\t\t   \n
\t\tthis.labelStyle = params.labelStyle;\n
        \n
        var labelWidth = null, labelHeight =  null, labelText = null, labelPadding = null;\n
\t\tthis.cssClass = this.labelStyle != null ? this.labelStyle.cssClass : null;\n
\t\tvar p = jsPlumb.extend({\n
            create : function() {\n
                return document.createElement("div");\n
            }}, params);\n
    \tjsPlumb.Overlays.Custom.call(this, p);\n
\t\tthis.type = "Label";    \t\n
        this.label = params.label || "";\n
        this.labelText = null;\n
        if (this.labelStyle) {\n
            var el = this.getElement();            \n
            this.labelStyle.font = this.labelStyle.font || "12px sans-serif";\n
            el.style.font = this.labelStyle.font;\n
            el.style.color = this.labelStyle.color || "black";\n
            if (this.labelStyle.fillStyle) el.style.background = this.labelStyle.fillStyle;\n
            if (this.labelStyle.borderWidth > 0) {\n
                var dStyle = this.labelStyle.borderStyle ? this.labelStyle.borderStyle : "black";\n
                el.style.border = this.labelStyle.borderWidth  + "px solid " + dStyle;\n
            }\n
            if (this.labelStyle.padding) el.style.padding = this.labelStyle.padding;            \n
        }\n
\n
    };\n
    jsPlumbUtil.extend(jsPlumb.Overlays.Label, jsPlumb.Overlays.Custom, {\n
        cleanup:function() {\n
            this.div = null;\n
            this.label = null;\n
            this.labelText = null;\n
            this.cssClass = null;\n
            this.labelStyle = null;\n
        },\n
        getLabel : function() {\n
            return this.label;\n
        },\n
        /*\n
         * Function: setLabel\n
         * sets the label\'s, um, label.  you would think i\'d call this function\n
         * \'setText\', but you can pass either a Function or a String to this, so\n
         * it makes more sense as \'setLabel\'. This uses innerHTML on the label div, so keep\n
         * that in mind if you need escaped HTML.\n
         */\n
        setLabel : function(l) {\n
            this.label = l;\n
            this.labelText = null;\n
            this.clearCachedDimensions();\n
            this.update();\n
            this.component.repaint();\n
        },\n
        getDimensions : function() {                \n
            this.update();\n
            return AbstractDOMOverlay.prototype.getDimensions.apply(this, arguments);\n
        },\n
        update : function() {\n
            if (typeof this.label == "function") {\n
                var lt = this.label(this);\n
                this.getElement().innerHTML = lt.replace(/\\r\\n/g, "<br/>");\n
            }\n
            else {\n
                if (this.labelText == null) {\n
                    this.labelText = this.label;\n
                    this.getElement().innerHTML = this.labelText.replace(/\\r\\n/g, "<br/>");\n
                }\n
            }\n
        }\n
    });\t\t\n
\n
 // ********************************* END OF OVERLAY DEFINITIONS ***********************************************************************\n
    \n
})();\n
/*\n
 * jsPlumb\n
 * \n
 * Title:jsPlumb 1.6.2\n
 * \n
 * Provides a way to visually connect elements on an HTML page, using SVG or VML.  \n
 * \n
 * This file contains the \'flowchart\' connectors, consisting of vertical and horizontal line segments.\n
 *\n
 * Copyright (c) 2010 - 2014 Simon Porritt (simon@jsplumbtoolkit.com)\n
 * \n
 * http://jsplumbtoolkit.com\n
 * http://github.com/sporritt/jsplumb\n
 * \n
 * Dual licensed under the MIT and GPL2 licenses.\n
 */\n
;(function() {\n
    \n
    "use strict";\n
   \n
    /**\n
     * Function: Constructor\n
     * \n
     * Parameters:\n
     * \tstub - minimum length for the stub at each end of the connector. This can be an integer, giving a value for both ends of the connections, \n
     * or an array of two integers, giving separate values for each end. The default is an integer with value 30 (pixels). \n
     *  gap  - gap to leave between the end of the connector and the element on which the endpoint resides. if you make this larger than stub then you will see some odd looking behaviour.  \n
                Like stub, this can be an array or a single value. defaults to 0 pixels for each end.     \n
     * cornerRadius - optional, defines the radius of corners between segments. defaults to 0 (hard edged corners).\n
     * alwaysRespectStubs - defaults to false. whether or not the connectors should always draw the stub, or, if the two elements\n
                            are in close proximity to each other (closer than the sum of the two stubs), to adjust the stubs.\n
     */\n
    var Flowchart = function(params) {\n
        this.type = "Flowchart";\n
        params = params || {};\n
        params.stub = params.stub == null ? 30 : params.stub;\n
        var self = this,\n
            _super =  jsPlumb.Connectors.AbstractConnector.apply(this, arguments),\t\t\n
            midpoint = params.midpoint == null ? 0.5 : params.midpoint,\n
            points = [], segments = [],\n
            grid = params.grid,\n
            alwaysRespectStubs = params.alwaysRespectStubs,\n
            userSuppliedSegments = null,\n
            lastx = null, lasty = null, lastOrientation,\t\n
            cornerRadius = params.cornerRadius != null ? params.cornerRadius : 0,\t\n
            sgn = function(n) { return n < 0 ? -1 : n === 0 ? 0 : 1; },            \n
            /**\n
             * helper method to add a segment.\n
             */\n
            addSegment = function(segments, x, y, paintInfo) {\n
                if (lastx == x && lasty == y) return;\n
                var lx = lastx == null ? paintInfo.sx : lastx,\n
                    ly = lasty == null ? paintInfo.sy : lasty,\n
                    o = lx == x ? "v" : "h",\n
                    sgnx = sgn(x - lx),\n
                    sgny = sgn(y - ly);\n
                    \n
                lastx = x;\n
                lasty = y;\t\t\t\t    \t\t                \n
                segments.push([lx, ly, x, y, o, sgnx, sgny]);\n
            },\n
            segLength = function(s) {\n
                return Math.sqrt(Math.pow(s[0] - s[2], 2) + Math.pow(s[1] - s[3], 2));    \n
            },\n
            _cloneArray = function(a) { var _a = []; _a.push.apply(_a, a); return _a;},\n
            updateMinMax = function(a1) {\n
                self.bounds.minX = Math.min(self.bounds.minX, a1[2]);\n
                self.bounds.maxX = Math.max(self.bounds.maxX, a1[2]);\n
                self.bounds.minY = Math.min(self.bounds.minY, a1[3]);\n
                self.bounds.maxY = Math.max(self.bounds.maxY, a1[3]);    \n
            },\n
            writeSegments = function(conn, segments, paintInfo) {\n
                var current, next;                \n
                for (var i = 0; i < segments.length - 1; i++) {\n
                    \n
                    current = current || _cloneArray(segments[i]);\n
                    next = _cloneArray(segments[i + 1]);\n
                    if (cornerRadius > 0 && current[4] != next[4]) {\n
                        var radiusToUse = Math.min(cornerRadius, segLength(current), segLength(next));\n
                        // right angle. adjust current segment\'s end point, and next segment\'s start point.\n
                        current[2] -= current[5] * radiusToUse;\n
                        current[3] -= current[6] * radiusToUse;\n
                        next[0] += next[5] * radiusToUse;\n
                        next[1] += next[6] * radiusToUse;\t\t\t\t\t\t\t\t\t\t\t\t\t\t                         \t\t\t\n
                        var ac = (current[6] == next[5] && next[5] == 1) ||\n
                                 ((current[6] == next[5] && next[5] === 0) && current[5] != next[6]) ||\n
                                 (current[6] == next[5] && next[5] == -1),\n
                            sgny = next[1] > current[3] ? 1 : -1,\n
                            sgnx = next[0] > current[2] ? 1 : -1,\n
                            sgnEqual = sgny == sgnx,\n
                            cx = (sgnEqual && ac || (!sgnEqual && !ac)) ? next[0] : current[2],\n
                            cy = (sgnEqual && ac || (!sgnEqual && !ac)) ? current[3] : next[1];                                                        \n
                        \n
                        _super.addSegment(conn, "Straight", {\n
                            x1:current[0], y1:current[1], x2:current[2], y2:current[3]\n
                        });\n
                            \n
                        _super.addSegment(conn, "Arc", {\n
                            r:radiusToUse, \n
                            x1:current[2], \n
                            y1:current[3], \n
                            x2:next[0], \n
                            y2:next[1],\n
                            cx:cx,\n
                            cy:cy,\n
                            ac:ac\n
                        });\t                                            \n
                    }\n
                    else {                 \n
                        // dx + dy are used to adjust for line width.\n
                        var dx = (current[2] == current[0]) ? 0 : (current[2] > current[0]) ? (paintInfo.lw / 2) : -(paintInfo.lw / 2),\n
                            dy = (current[3] == current[1]) ? 0 : (current[3] > current[1]) ? (paintInfo.lw / 2) : -(paintInfo.lw / 2);\n
                        _super.addSegment(conn, "Straight", {\n
                            x1:current[0]- dx, y1:current[1]-dy, x2:current[2] + dx, y2:current[3] + dy\n
                        });\n
                    }                    \n
                    current = next;\n
                }\n
                if (next != null) {\n
                    // last segment\n
                    _super.addSegment(conn, "Straight", {\n
                        x1:next[0], y1:next[1], x2:next[2], y2:next[3]\n
                    });                             \n
                }\n
            };\n
        \n
        this.setSegments = function(s) {\n
            userSuppliedSegments = s;\n
        };\n
        \n
        this.isEditable = function() { return true; };\n
        \n
        /*\n
            Function: getOriginalSegments\n
            Gets the segments before the addition of rounded corners. This is used by the flowchart\n
            connector editor, since it only wants to concern itself with the original segments.\n
        */\n
        this.getOriginalSegments = function() {\n
            return userSuppliedSegments || segments;\n
        };\n
        \n
        this._compute = function(paintInfo, params) {\n
            \n
            if (params.clearEdits)\n
                userSuppliedSegments = null;\n
            \n
            if (userSuppliedSegments != null) {\n
                writeSegments(this, userSuppliedSegments, paintInfo);                \n
                return;\n
            }\n
            \n
            segments = [];\n
            lastx = null; lasty = null;\n
            lastOrientation = null;          \n
            \n
            var midx = paintInfo.startStubX + ((paintInfo.endStubX - paintInfo.startStubX) * midpoint),\n
                midy = paintInfo.startStubY + ((paintInfo.endStubY - paintInfo.startStubY) * midpoint);                                                                                                    \n
    \n
            var findClearedLine = function(start, mult, anchorPos, dimension) {\n
                    return start + (mult * (( 1 - anchorPos) * dimension) + _super.maxStub);\n
                },\n
                orientations = { x:[ 0, 1 ], y:[ 1, 0 ] },\n
                commonStubCalculator = function(axis) {\n
                    return [ paintInfo.startStubX, paintInfo.startStubY, paintInfo.endStubX, paintInfo.endStubY ];                    \n
                },\n
                stubCalculators = {\n
                    perpendicular:commonStubCalculator,\n
                    orthogonal:commonStubCalculator,\n
                    opposite:function(axis) {  \n
                        var pi = paintInfo,\n
                            idx = axis == "x" ? 0 : 1, \n
                            areInProximity = {\n
                                "x":function() {                                    \n
                                    return ( (pi.so[idx] == 1 && ( \n
                                        ( (pi.startStubX > pi.endStubX) && (pi.tx > pi.startStubX) ) ||\n
                                        ( (pi.sx > pi.endStubX) && (pi.tx > pi.sx))))) ||\n
\n
                                        ( (pi.so[idx] == -1 && ( \n
                                            ( (pi.startStubX < pi.endStubX) && (pi.tx < pi.startStubX) ) ||\n
                                            ( (pi.sx < pi.endStubX) && (pi.tx < pi.sx)))));\n
                                },\n
                                "y":function() {                                     \n
                                    return ( (pi.so[idx] == 1 && ( \n
                                        ( (pi.startStubY > pi.endStubY) && (pi.ty > pi.startStubY) ) ||\n
                                        ( (pi.sy > pi.endStubY) && (pi.ty > pi.sy))))) ||\n
\n
                                        ( (pi.so[idx] == -1 && ( \n
                                        ( (pi.startStubY < pi.endStubY) && (pi.ty < pi.startStubY) ) ||\n
                                        ( (pi.sy < pi.endStubY) && (pi.ty < pi.sy)))));\n
                                }\n
                            };\n
\n
                        if (!alwaysRespectStubs && areInProximity[axis]()) {                   \n
                            return {\n
                                "x":[(paintInfo.sx + paintInfo.tx) / 2, paintInfo.startStubY, (paintInfo.sx + paintInfo.tx) / 2, paintInfo.endStubY],\n
                                "y":[paintInfo.startStubX, (paintInfo.sy + paintInfo.ty) / 2, paintInfo.endStubX, (paintInfo.sy + paintInfo.ty) / 2]\n
                            }[axis];\n
                        }\n
                        else {\n
                            return [ paintInfo.startStubX, paintInfo.startStubY, paintInfo.endStubX, paintInfo.endStubY ];   \n
                        }\n
                    }\n
                },\n
                lineCalculators = {\n
                    perpendicular : function(axis, ss, oss, es, oes) {\n
                        var pi = paintInfo, \n
                            sis = {\n
                                x:[ [ [ 1,2,3,4 ], null, [ 2,1,4,3 ] ], null, [ [ 4,3,2,1 ], null, [ 3,4,1,2 ] ] ],\n
                                y:[ [ [ 3,2,1,4 ], null, [ 2,3,4,1 ] ], null, [ [ 4,1,2,3 ], null, [ 1,4,3,2 ] ] ]\n
                            },\n
                            stubs = { \n
                                x:[ [ pi.startStubX, pi.endStubX ] , null, [ pi.endStubX, pi.startStubX ] ],\n
                                y:[ [ pi.startStubY, pi.endStubY ] , null, [ pi.endStubY, pi.startStubY ] ]\n
                            },\n
                            midLines = {\n
                                x:[ [ midx, pi.startStubY ], [ midx, pi.endStubY ] ],\n
                                y:[ [ pi.startStubX, midy ], [ pi.endStubX, midy ] ]\n
                            },\n
                            linesToEnd = {\n
                                x:[ [ pi.endStubX, pi.startStubY ] ],\n
                                y:[ [ pi.startStubX, pi.endStubY ] ]\n
                            },\n
                            startToEnd = {\n
                                x:[ [ pi.startStubX, pi.endStubY ], [ pi.endStubX, pi.endStubY ] ],        \n
                                y:[ [ pi.endStubX, pi.startStubY ], [ pi.endStubX, pi.endStubY ] ]\n
                            },\n
                            startToMidToEnd = {\n
                                x:[ [ pi.startStubX, midy ], [ pi.endStubX, midy ], [ pi.endStubX, pi.endStubY ] ],\n
                                y:[ [ midx, pi.startStubY ], [ midx, pi.endStubY ], [ pi.endStubX, pi.endStubY ] ]\n
                            },\n
                            otherStubs = {\n
                                x:[ pi.startStubY, pi.endStubY ],\n
                                y:[ pi.startStubX, pi.endStubX ]                                    \n
                            },\n
                            soIdx = orientations[axis][0], toIdx = orientations[axis][1],\n
                            _so = pi.so[soIdx] + 1,\n
                            _to = pi.to[toIdx] + 1,\n
                            otherFlipped = (pi.to[toIdx] == -1 && (otherStubs[axis][1] < otherStubs[axis][0])) || (pi.to[toIdx] == 1 && (otherStubs[axis][1] > otherStubs[axis][0])),\n
                            stub1 = stubs[axis][_so][0],\n
                            stub2 = stubs[axis][_so][1],\n
                            segmentIndexes = sis[axis][_so][_to];\n
\n
                        if (pi.segment == segmentIndexes[3] || (pi.segment == segmentIndexes[2] && otherFlipped)) {\n
                            return midLines[axis];       \n
                        }\n
                        else if (pi.segment == segmentIndexes[2] && stub2 < stub1) {\n
                            return linesToEnd[axis];\n
                        }\n
                        else if ((pi.segment == segmentIndexes[2] && stub2 >= stub1) || (pi.segment == segmentIndexes[1] && !otherFlipped)) {\n
                            return startToMidToEnd[axis];\n
                        }\n
                        else if (pi.segment == segmentIndexes[0] || (pi.segment == segmentIndexes[1] && otherFlipped)) {\n
                            return startToEnd[axis];  \n
                        }                                \n
                    },\n
                    orthogonal : function(axis, startStub, otherStartStub, endStub, otherEndStub) {                    \n
                        var pi = paintInfo,                                            \n
                            extent = {\n
                                "x":pi.so[0] == -1 ? Math.min(startStub, endStub) : Math.max(startStub, endStub),\n
                                "y":pi.so[1] == -1 ? Math.min(startStub, endStub) : Math.max(startStub, endStub)\n
                            }[axis];\n
                                                \n
                        return {\n
                            "x":[ [ extent, otherStartStub ],[ extent, otherEndStub ], [ endStub, otherEndStub ] ],\n
                            "y":[ [ otherStartStub, extent ], [ otherEndStub, extent ], [ otherEndStub, endStub ] ]\n
                        }[axis];                    \n
                    },\n
                    opposite : function(axis, ss, oss, es, oes) {                                                \n
                        var pi = paintInfo,\n
                            otherAxis = {"x":"y","y":"x"}[axis], \n
                            dim = {"x":"height","y":"width"}[axis],\n
                            comparator = pi["is" + axis.toUpperCase() + "GreaterThanStubTimes2"];\n
\n
                        if (params.sourceEndpoint.elementId == params.targetEndpoint.elementId) {\n
                            var _val = oss + ((1 - params.sourceEndpoint.anchor[otherAxis]) * params.sourceInfo[dim]) + _super.maxStub;\n
                            return {\n
                                "x":[ [ ss, _val ], [ es, _val ] ],\n
                                "y":[ [ _val, ss ], [ _val, es ] ]\n
                            }[axis];\n
                            \n
                        }                                                        \n
                        else if (!comparator || (pi.so[idx] == 1 && ss > es) || (pi.so[idx] == -1 && ss < es)) {                                            \n
                            return {\n
                                "x":[[ ss, midy ], [ es, midy ]],\n
                                "y":[[ midx, ss ], [ midx, es ]]\n
                            }[axis];\n
                        }\n
                        else if ((pi.so[idx] == 1 && ss < es) || (pi.so[idx] == -1 && ss > es)) {\n
                            return {\n
                                "x":[[ midx, pi.sy ], [ midx, pi.ty ]],\n
                                "y":[[ pi.sx, midy ], [ pi.tx, midy ]]\n
                            }[axis

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAc=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="7" aka="AAAAAAAAAAc=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

];\n
                        }                        \n
                    }\n
                };\n
\n
            var stubs = stubCalculators[paintInfo.anchorOrientation](paintInfo.sourceAxis),\n
                idx = paintInfo.sourceAxis == "x" ? 0 : 1,\n
                oidx = paintInfo.sourceAxis == "x" ? 1 : 0,                            \n
                ss = stubs[idx],\n
                oss = stubs[oidx],\n
                es = stubs[idx + 2],\n
                oes = stubs[oidx + 2];\n
\n
            // add the start stub segment.\n
            addSegment(segments, stubs[0], stubs[1], paintInfo);           \n
\n
            // compute the rest of the line\n
            var p = lineCalculators[paintInfo.anchorOrientation](paintInfo.sourceAxis, ss, oss, es, oes);            \n
            if (p) {\n
                for (var i = 0; i < p.length; i++) {                \t\n
                    addSegment(segments, p[i][0], p[i][1], paintInfo);\n
                }\n
            }          \n
            \n
            // line to end stub\n
            addSegment(segments, stubs[2], stubs[3], paintInfo);\n
    \n
            // end stub to end\n
            addSegment(segments, paintInfo.tx, paintInfo.ty, paintInfo);               \n
            \n
            writeSegments(this, segments, paintInfo);                            \n
        };\t\n
\n
        this.getPath = function() {\n
            var _last = null, _lastAxis = null, s = [], segs = userSuppliedSegments || segments;\n
            for (var i = 0; i < segs.length; i++) {\n
                var seg = segs[i], axis = seg[4], axisIndex = (axis == "v" ? 3 : 2);\n
                if (_last != null && _lastAxis === axis) {\n
                    _last[axisIndex] = seg[axisIndex];                            \n
                }\n
                else {\n
                    if (seg[0] != seg[2] || seg[1] != seg[3]) {\n
                        s.push({\n
                            start:[ seg[0], seg[1] ],\n
                            end:[ seg[2], seg[3] ]\n
                        });                    \n
                        _last = seg;\n
                        _lastAxis = seg[4];\n
                    }\n
                }\n
            }\n
            return s;\n
        };\t\n
\n
        this.setPath = function(path) {\n
            userSuppliedSegments = [];\n
            for (var i = 0; i < path.length; i++) {\n
                 var lx = path[i].start[0],\n
                    ly = path[i].start[1],\n
                    x = path[i].end[0],\n
                    y = path[i].end[1],\n
                    o = lx == x ? "v" : "h",\n
                    sgnx = sgn(x - lx),\n
                    sgny = sgn(y - ly);\n
\n
                userSuppliedSegments.push([lx, ly, x, y, o, sgnx, sgny]);\n
            }\n
        };\n
    };\n
\n
    jsPlumbUtil.extend(Flowchart, jsPlumb.Connectors.AbstractConnector);\n
    jsPlumb.registerConnectorType(Flowchart, "Flowchart");\n
})();\n
/*\n
 * jsPlumb\n
 * \n
 * Title:jsPlumb 1.6.2\n
 * \n
 * Provides a way to visually connect elements on an HTML page, using SVG or VML.  \n
 * \n
 * This file contains the state machine connectors.\n
 *\n
 * Copyright (c) 2010 - 2014 Simon Porritt (simon@jsplumbtoolkit.com)\n
 * \n
 * http://jsplumbtoolkit.com\n
 * http://github.com/sporritt/jsplumb\n
 * \n
 * Dual licensed under the MIT and GPL2 licenses.\n
 */\n
 ;(function() {\n
\t \n
\t"use strict";\n
\n
\tvar Line = function(x1, y1, x2, y2) {\n
\n
\t\tthis.m = (y2 - y1) / (x2 - x1);\n
\t\tthis.b = -1 * ((this.m * x1) - y1);\n
\t\n
\t\tthis.rectIntersect = function(x,y,w,h) {\n
\t\t\tvar results = [], xInt, yInt;\n
\t\t\n
\t\t\t// \ttry top face\n
\t\t\t// \tthe equation of the top face is y = (0 * x) + b; y = b.\n
\t\t\txInt = (y - this.b) / this.m;\n
\t\t\t// test that the X value is in the line\'s range.\n
\t\t\tif (xInt >= x && xInt <= (x + w)) results.push([ xInt, (this.m * xInt) + this.b ]);\n
\t\t\n
\t\t\t// try right face\n
\t\t\tyInt = (this.m * (x + w)) + this.b;\n
\t\t\tif (yInt >= y && yInt <= (y + h)) results.push([ (yInt - this.b) / this.m, yInt ]);\n
\t\t\n
\t\t\t// \tbottom face\n
\t\t\txInt = ((y + h) - this.b) / this.m;\n
\t\t\t// test that the X value is in the line\'s range.\n
\t\t\tif (xInt >= x && xInt <= (x + w)) results.push([ xInt, (this.m * xInt) + this.b ]);\n
\t\t\n
\t\t\t// try left face\n
\t\t\tyInt = (this.m * x) + this.b;\n
\t\t\tif (yInt >= y && yInt <= (y + h)) results.push([ (yInt - this.b) / this.m, yInt ]);\n
\n
\t\t\tif (results.length == 2) {\n
\t\t\t\tvar midx = (results[0][0] + results[1][0]) / 2, midy = (results[0][1] + results[1][1]) / 2;\n
\t\t\t\tresults.push([ midx,midy ]);\n
\t\t\t\t// now calculate the segment inside the rectangle where the midpoint lies.\n
\t\t\t\tvar xseg = midx <= x + (w / 2) ? -1 : 1,\n
\t\t\t\t\tyseg = midy <= y + (h / 2) ? -1 : 1;\n
\t\t\t\tresults.push([xseg, yseg]);\n
\t\t\t\treturn results;\n
\t\t\t}\n
\t\t\n
\t\t\treturn null;\n
\n
\t\t};\n
\t},\n
\t_segment = function(x1, y1, x2, y2) {\n
\t\tif (x1 <= x2 && y2 <= y1) return 1;\n
\t\telse if (x1 <= x2 && y1 <= y2) return 2;\n
\t\telse if (x2 <= x1 && y2 >= y1) return 3;\n
\t\treturn 4;\n
\t},\n
\t\t\n
\t\t// the control point we will use depends on the faces to which each end of the connection is assigned, specifically whether or not the\n
\t\t// two faces are parallel or perpendicular.  if they are parallel then the control point lies on the midpoint of the axis in which they\n
\t\t// are parellel and varies only in the other axis; this variation is proportional to the distance that the anchor points lie from the\n
\t\t// center of that face.  if the two faces are perpendicular then the control point is at some distance from both the midpoints; the amount and\n
\t\t// direction are dependent on the orientation of the two elements. \'seg\', passed in to this method, tells you which segment the target element\n
\t\t// lies in with respect to the source: 1 is top right, 2 is bottom right, 3 is bottom left, 4 is top left.\n
\t\t//\n
\t\t// sourcePos and targetPos are arrays of info about where on the source and target each anchor is located.  their contents are:\n
\t\t//\n
\t\t// 0 - absolute x\n
\t\t// 1 - absolute y\n
\t\t// 2 - proportional x in element (0 is left edge, 1 is right edge)\n
\t\t// 3 - proportional y in element (0 is top edge, 1 is bottom edge)\n
\t\t// \t\n
\t_findControlPoint = function(midx, midy, segment, sourceEdge, targetEdge, dx, dy, distance, proximityLimit) {\n
        // TODO (maybe)\n
        // - if anchor pos is 0.5, make the control point take into account the relative position of the elements.\n
        if (distance <= proximityLimit) return [midx, midy];\n
\n
        if (segment === 1) {\n
            if (sourceEdge[3] <= 0 && targetEdge[3] >= 1) return [ midx + (sourceEdge[2] < 0.5 ? -1 * dx : dx), midy ];\n
            else if (sourceEdge[2] >= 1 && targetEdge[2] <= 0) return [ midx, midy + (sourceEdge[3] < 0.5 ? -1 * dy : dy) ];\n
            else return [ midx + (-1 * dx) , midy + (-1 * dy) ];\n
        }\n
        else if (segment === 2) {\n
            if (sourceEdge[3] >= 1 && targetEdge[3] <= 0) return [ midx + (sourceEdge[2] < 0.5 ? -1 * dx : dx), midy ];\n
            else if (sourceEdge[2] >= 1 && targetEdge[2] <= 0) return [ midx, midy + (sourceEdge[3] < 0.5 ? -1 * dy : dy) ];\n
            else return [ midx + (1 * dx) , midy + (-1 * dy) ];\n
        }\n
        else if (segment === 3) {\n
            if (sourceEdge[3] >= 1 && targetEdge[3] <= 0) return [ midx + (sourceEdge[2] < 0.5 ? -1 * dx : dx), midy ];\n
            else if (sourceEdge[2] <= 0 && targetEdge[2] >= 1) return [ midx, midy + (sourceEdge[3] < 0.5 ? -1 * dy : dy) ];\n
            else return [ midx + (-1 * dx) , midy + (-1 * dy) ];\n
        }\n
        else if (segment === 4) {\n
            if (sourceEdge[3] <= 0 && targetEdge[3] >= 1) return [ midx + (sourceEdge[2] < 0.5 ? -1 * dx : dx), midy ];\n
            else if (sourceEdge[2] <= 0 && targetEdge[2] >= 1) return [ midx, midy + (sourceEdge[3] < 0.5 ? -1 * dy : dy) ];\n
            else return [ midx + (1 * dx) , midy + (-1 * dy) ];\n
        }\n
\n
\t};\t\n
\t\n
\t/**\n
     * Class: Connectors.StateMachine\n
     * Provides \'state machine\' connectors.\n
     */\n
\t/*\n
\t * Function: Constructor\n
\t * \n
\t * Parameters:\n
\t * curviness -\tmeasure of how "curvy" the connectors will be.  this is translated as the distance that the\n
     *                Bezier curve\'s control point is from the midpoint of the straight line connecting the two\n
     *              endpoints, and does not mean that the connector is this wide.  The Bezier curve never reaches\n
     *              its control points; they act as gravitational masses. defaults to 10.\n
\t * margin\t-\tdistance from element to start and end connectors, in pixels.  defaults to 5.\n
\t * proximityLimit  -   sets the distance beneath which the elements are consider too close together to bother\n
\t *\t\t\t\t\t\twith fancy curves. by default this is 80 pixels.\n
\t * loopbackRadius\t-\tthe radius of a loopback connector.  optional; defaults to 25.\n
\t * showLoopback   -   If set to false this tells the connector that it is ok to paint connections whose source and target is the same element with a connector running through the element. The default value for this is true; the connector always makes a loopback connection loop around the element rather than passing through it.\n
\t*/\n
\tvar StateMachine = function(params) {\n
\t\tparams = params || {};\n
\t\tthis.type = "StateMachine";\n
\n
\t\tvar self = this,\n
\t\t\t_super =  jsPlumb.Connectors.AbstractConnector.apply(this, arguments),\n
\t\t\tcurviness = params.curviness || 10,\n
\t\t\tmargin = params.margin || 5,\n
\t\t\tproximityLimit = params.proximityLimit || 80,\n
\t\t\tclockwise = params.orientation && params.orientation === "clockwise",\n
\t\t\tloopbackRadius = params.loopbackRadius || 25,\n
\t\t\tshowLoopback = params.showLoopback !== false;\n
\t\t\n
\t\tthis._compute = function(paintInfo, params) {\n
\t\t\tvar w = Math.abs(params.sourcePos[0] - params.targetPos[0]),\n
\t\t\t\th = Math.abs(params.sourcePos[1] - params.targetPos[1]),\n
\t\t\t\tx = Math.min(params.sourcePos[0], params.targetPos[0]),\n
\t\t\t\ty = Math.min(params.sourcePos[1], params.targetPos[1]);\t\t\t\t\n
\t\t\n
\t\t\tif (!showLoopback || (params.sourceEndpoint.elementId !== params.targetEndpoint.elementId)) {                            \n
\t\t\t\tvar _sx = params.sourcePos[0] < params.targetPos[0] ? 0  : w,\n
\t\t\t\t\t_sy = params.sourcePos[1] < params.targetPos[1] ? 0:h,\n
\t\t\t\t\t_tx = params.sourcePos[0] < params.targetPos[0] ? w : 0,\n
\t\t\t\t\t_ty = params.sourcePos[1] < params.targetPos[1] ? h : 0;\n
            \n
\t\t\t\t// now adjust for the margin\n
\t\t\t\tif (params.sourcePos[2] === 0) _sx -= margin;\n
            \tif (params.sourcePos[2] === 1) _sx += margin;\n
            \tif (params.sourcePos[3] === 0) _sy -= margin;\n
            \tif (params.sourcePos[3] === 1) _sy += margin;\n
            \tif (params.targetPos[2] === 0) _tx -= margin;\n
            \tif (params.targetPos[2] === 1) _tx += margin;\n
            \tif (params.targetPos[3] === 0) _ty -= margin;\n
            \tif (params.targetPos[3] === 1) _ty += margin;\n
\n
            \t//\n
\t            // these connectors are quadratic bezier curves, having a single control point. if both anchors \n
    \t        // are located at 0.5 on their respective faces, the control point is set to the midpoint and you\n
        \t    // get a straight line.  this is also the case if the two anchors are within \'proximityLimit\', since\n
           \t \t// it seems to make good aesthetic sense to do that. outside of that, the control point is positioned \n
           \t \t// at \'curviness\' pixels away along the normal to the straight line connecting the two anchors.\n
\t            // \n
   \t        \t// there may be two improvements to this.  firstly, we might actually support the notion of avoiding nodes\n
            \t// in the UI, or at least making a good effort at doing so.  if a connection would pass underneath some node,\n
            \t// for example, we might increase the distance the control point is away from the midpoint in a bid to\n
            \t// steer it around that node.  this will work within limits, but i think those limits would also be the likely\n
            \t// limits for, once again, aesthetic good sense in the layout of a chart using these connectors.\n
            \t//\n
            \t// the second possible change is actually two possible changes: firstly, it is possible we should gradually\n
            \t// decrease the \'curviness\' as the distance between the anchors decreases; start tailing it off to 0 at some\n
            \t// point (which should be configurable).  secondly, we might slightly increase the \'curviness\' for connectors\n
            \t// with respect to how far their anchor is from the center of its respective face. this could either look cool,\n
            \t// or stupid, and may indeed work only in a way that is so subtle as to have been a waste of time.\n
            \t//\n
\n
\t\t\t\tvar _midx = (_sx + _tx) / 2, _midy = (_sy + _ty) / 2, \n
            \t    m2 = (-1 * _midx) / _midy, theta2 = Math.atan(m2),\n
            \t    dy =  (m2 == Infinity || m2 == -Infinity) ? 0 : Math.abs(curviness / 2 * Math.sin(theta2)),\n
\t\t\t\t    dx =  (m2 == Infinity || m2 == -Infinity) ? 0 : Math.abs(curviness / 2 * Math.cos(theta2)),\n
\t\t\t\t    segment = _segment(_sx, _sy, _tx, _ty),\n
\t\t\t\t    distance = Math.sqrt(Math.pow(_tx - _sx, 2) + Math.pow(_ty - _sy, 2)),\t\t\t\n
\t            \t// calculate the control point.  this code will be where we\'ll put in a rudimentary element avoidance scheme; it\n
\t            \t// will work by extending the control point to force the curve to be, um, curvier.\n
\t\t\t\t\t_controlPoint = _findControlPoint(_midx,\n
                                                  _midy,\n
                                                  segment,\n
                                                  params.sourcePos,\n
                                                  params.targetPos,\n
                                                  curviness, curviness,\n
                                                  distance,\n
                                                  proximityLimit);\n
\n
\t\t\t\t_super.addSegment(this, "Bezier", {\n
\t\t\t\t\tx1:_tx, y1:_ty, x2:_sx, y2:_sy,\n
\t\t\t\t\tcp1x:_controlPoint[0], cp1y:_controlPoint[1],\n
\t\t\t\t\tcp2x:_controlPoint[0], cp2y:_controlPoint[1]\n
\t\t\t\t});\t\t\t\t\n
            }\n
            else {\n
            \t// a loopback connector.  draw an arc from one anchor to the other.            \t\n
        \t\tvar x1 = params.sourcePos[0], x2 = params.sourcePos[0], y1 = params.sourcePos[1] - margin, y2 = params.sourcePos[1] - margin, \t\t\t\t\n
\t\t\t\t\tcx = x1, cy = y1 - loopbackRadius,\t\t\t\t\n
\t\t\t\t\t// canvas sizing stuff, to ensure the whole painted area is visible.\n
\t\t\t\t\t_w = 2 * loopbackRadius, \n
\t\t\t\t\t_h = 2 * loopbackRadius,\n
\t\t\t\t\t_x = cx - loopbackRadius, \n
\t\t\t\t\t_y = cy - loopbackRadius;\n
\n
\t\t\t\tpaintInfo.points[0] = _x;\n
\t\t\t\tpaintInfo.points[1] = _y;\n
\t\t\t\tpaintInfo.points[2] = _w;\n
\t\t\t\tpaintInfo.points[3] = _h;\n
\t\t\t\t\n
\t\t\t\t// ADD AN ARC SEGMENT.\n
\t\t\t\t_super.addSegment(this, "Arc", {\n
\t\t\t\t\tloopback:true,\n
\t\t\t\t\tx1:(x1 - _x) + 4,\n
\t\t\t\t\ty1:y1 - _y,\n
\t\t\t\t\tstartAngle:0,\n
\t\t\t\t\tendAngle: 2 * Math.PI,\n
\t\t\t\t\tr:loopbackRadius,\n
\t\t\t\t\tac:!clockwise,\n
\t\t\t\t\tx2:(x1 - _x) - 4,\n
\t\t\t\t\ty2:y1 - _y,\n
\t\t\t\t\tcx:cx - _x,\n
\t\t\t\t\tcy:cy - _y\n
\t\t\t\t});\n
            }                           \n
        };                        \n
\t};\n
\tjsPlumb.registerConnectorType(StateMachine, "StateMachine");\n
})();\n
\n
/*\n
    \t// a possible rudimentary avoidance scheme, old now, perhaps not useful.\n
        //      if (avoidSelector) {\n
\t\t//\t\t    var testLine = new Line(sourcePos[0] + _sx,sourcePos[1] + _sy,sourcePos[0] + _tx,sourcePos[1] + _ty);\n
\t\t//\t\t    var sel = jsPlumb.getSelector(avoidSelector);\n
\t\t//\t\t    for (var i = 0; i < sel.length; i++) {\n
\t\t//\t\t\t    var id = jsPlumb.getId(sel[i]);\n
\t\t//\t\t\t    if (id != sourceEndpoint.elementId && id != targetEndpoint.elementId) {\n
\t\t//\t\t\t\t    o = jsPlumb.getOffset(id), s = jsPlumb.getSize(id);\n
//\n
//\t\t\t\t\t\t    if (o && s) {\n
//\t\t\t\t\t\t\t    var collision = testLine.rectIntersect(o.left,o.top,s[0],s[1]);\n
//\t\t\t\t\t\t\t    if (collision) {\n
\t\t\t\t\t\t\t\t    // set the control point to be a certain distance from the midpoint of the two points that\n
\t\t\t\t\t\t\t\t    // the line crosses on the rectangle.\n
\t\t\t\t\t\t\t\t    // TODO where will this 75 number come from?\n
\t\t\t\t\t//\t\t\t    _controlX = collision[2][0] + (75 * collision[3][0]);\n
\t\t\t\t//\t/\t\t\t    _controlY = collision[2][1] + (75 * collision[3][1]);\n
//\t\t\t\t\t\t\t    }\n
//\t\t\t\t\t\t    }\n
\t\t\t\t\t//  }\n
\t//\t\t\t    }\n
              //}\n
    */\n
/*\n
 * jsPlumb\n
 * \n
 * Title:jsPlumb 1.6.2\n
 * \n
 * Provides a way to visually connect elements on an HTML page, using SVG or VML.  \n
 * \n
 * This file contains the code for the Bezier connector type.\n
 *\n
 * Copyright (c) 2010 - 2014 Simon Porritt (simon@jsplumbtoolkit.com)\n
 * \n
 * http://jsplumbtoolkit.com\n
 * http://github.com/sporritt/jsplumb\n
 * \n
 * Dual licensed under the MIT and GPL2 licenses.\n
 */\n
;(function() {\n
\n
\tvar Bezier = function(params) {\n
\t\tparams = params || {};\n
\n
\t\tvar _super =  jsPlumb.Connectors.AbstractConnector.apply(this, arguments),\n
\t\t\tstub = params.stub || 50,\n
\t\t\tmajorAnchor = params.curviness || 150,\n
\t\t\tminorAnchor = 10;\n
\n
\t\tthis.type = "Bezier";\n
\t\tthis.getCurviness = function() { return majorAnchor; };\n
\n
\t\tthis._findControlPoint = function(point, sourceAnchorPosition, targetAnchorPosition, sourceEndpoint, targetEndpoint) {\n
\t\t\t// determine if the two anchors are perpendicular to each other in their orientation.  we swap the control \n
\t\t\t// points around if so (code could be tightened up)\n
\t\t\tvar soo = sourceEndpoint.anchor.getOrientation(sourceEndpoint), \n
\t\t\t\ttoo = targetEndpoint.anchor.getOrientation(targetEndpoint),\n
\t\t\t\tperpendicular = soo[0] != too[0] || soo[1] == too[1],\n
\t\t\t\tp = [];\n
\n
\t\t\tif (!perpendicular) {\n
\t\t\t\tif (soo[0] === 0) // X\n
\t\t\t\t\tp.push(sourceAnchorPosition[0] < targetAnchorPosition[0] ? point[0] + minorAnchor : point[0] - minorAnchor);\n
\t\t\t\telse p.push(point[0] - (majorAnchor * soo[0]));\n
\n
\t\t\t\tif (soo[1] === 0) // Y\n
\t\t\t\t\tp.push(sourceAnchorPosition[1] < targetAnchorPosition[1] ? point[1] + minorAnchor : point[1] - minorAnchor);\n
\t\t\t\telse p.push(point[1] + (majorAnchor * too[1]));\n
\t\t\t}\n
\t\t\telse {\n
\t\t\t\tif (too[0] === 0) // X\n
\t\t\t\t\tp.push(targetAnchorPosition[0] < sourceAnchorPosition[0] ? point[0] + minorAnchor : point[0] - minorAnchor);\n
\t\t\t\telse p.push(point[0] + (majorAnchor * too[0]));\n
\n
\t\t\t\tif (too[1] === 0) // Y\n
\t\t\t\t\tp.push(targetAnchorPosition[1] < sourceAnchorPosition[1] ? point[1] + minorAnchor : point[1] - minorAnchor);\n
\t\t\t\telse p.push(point[1] + (majorAnchor * soo[1]));\n
\t\t\t}\n
\n
\t\t\treturn p;\n
\t\t};\n
\n
\t\tthis._compute = function(paintInfo, p) {\n
\t\t\tvar sp = p.sourcePos,\n
\t\t\t\ttp = p.targetPos,\n
\t\t\t\t_w = Math.abs(sp[0] - tp[0]),\n
\t\t\t\t_h = Math.abs(sp[1] - tp[1]),\n
\t\t\t\t_sx = sp[0] < tp[0] ? _w : 0,\n
\t\t\t\t_sy = sp[1] < tp[1] ? _h : 0,\n
\t\t\t\t_tx = sp[0] < tp[0] ? 0 : _w,\n
\t\t\t\t_ty = sp[1] < tp[1] ? 0 : _h,\n
\t\t\t\t_CP = this._findControlPoint([_sx, _sy], sp, tp, p.sourceEndpoint, p.targetEndpoint),\n
\t\t\t\t_CP2 = this._findControlPoint([_tx, _ty], tp, sp, p.targetEndpoint, p.sourceEndpoint);\n
\n
\t\t\t_super.addSegment(this, "Bezier", {\n
\t\t\t\tx1:_sx, y1:_sy, x2:_tx, y2:_ty,\n
\t\t\t\tcp1x:_CP[0], cp1y:_CP[1], cp2x:_CP2[0], cp2y:_CP2[1]\n
\t\t\t});\n
\t\t};\n
\t};\n
\n
\tjsPlumbUtil.extend(Bezier, jsPlumb.Connectors.AbstractConnector);\n
\tjsPlumb.registerConnectorType(Bezier, "Bezier");\n
\n
})();\n
/*\n
 * jsPlumb\n
 * \n
 * Title:jsPlumb 1.6.2\n
 * \n
 * Provides a way to visually connect elements on an HTML page, using SVG or VML.  \n
 * \n
 * This file contains the SVG renderers.\n
 *\n
 * Copyright (c) 2010 - 2014 Simon Porritt (simon@jsplumbtoolkit.com)\n
 * \n
 * http://jsplumbtoolkit.com\n
 * http://github.com/sporritt/jsplumb\n
 * \n
 * Dual licensed under the MIT and GPL2 licenses.\n
 */\n
;(function() {\n
\t\n
// ************************** SVG utility methods ********************************************\t\n
\n
\t"use strict";\n
\t\n
\tvar svgAttributeMap = {\n
\t\t"joinstyle":"stroke-linejoin",\n
\t\t"stroke-linejoin":"stroke-linejoin",\t\t\n
\t\t"stroke-dashoffset":"stroke-dashoffset",\n
\t\t"stroke-linecap":"stroke-linecap"\n
\t},\n
\tSTROKE_DASHARRAY = "stroke-dasharray",\n
\tDASHSTYLE = "dashstyle",\n
\tLINEAR_GRADIENT = "linearGradient",\n
\tRADIAL_GRADIENT = "radialGradient",\n
\tDEFS = "defs",\n
\tFILL = "fill",\n
\tSTOP = "stop",\n
\tSTROKE = "stroke",\n
\tSTROKE_WIDTH = "stroke-width",\n
\tSTYLE = "style",\n
\tNONE = "none",\n
\tJSPLUMB_GRADIENT = "jsplumb_gradient_",\n
\tLINE_WIDTH = "lineWidth",\n
\tns = {\n
\t\tsvg:"http://www.w3.org/2000/svg",\n
\t\txhtml:"http://www.w3.org/1999/xhtml"\n
\t},\n
\t_attr = function(node, attributes) {\n
\t\tfor (var i in attributes)\n
\t\t\tnode.setAttribute(i, "" + attributes[i]);\n
\t},\t\n
\t_node = function(name, attributes) {\n
\t\tvar n = document.createElementNS(ns.svg, name);\n
\t\tattributes = attributes || {};\n
\t\tattributes.version = "1.1";\n
\t\tattributes.xmlns = ns.xhtml;\n
\t\t_attr(n, attributes);\n
\t\treturn n;\n
\t},\n
\t_pos = function(d) { return "position:absolute;left:" + d[0] + "px;top:" + d[1] + "px"; },\t\n
\t_clearGradient = function(parent) {\n
\t\tfor (var i = 0; i < parent.childNodes.length; i++) {\n
\t\t\tif (parent.childNodes[i].tagName == DEFS || parent.childNodes[i].tagName == LINEAR_GRADIENT || parent.childNodes[i].tagName == RADIAL_GRADIENT)\n
\t\t\t\tparent.removeChild(parent.childNodes[i]);\n
\t\t}\n
\t},\t\t\n
\t_updateGradient = function(parent, node, style, dimensions, uiComponent) {\n
\t\tvar id = JSPLUMB_GRADIENT + uiComponent._jsPlumb.instance.idstamp();\n
\t\t// first clear out any existing gradient\n
\t\t_clearGradient(parent);\n
\t\t// this checks for an \'offset\' property in the gradient, and in the absence of it, assumes\n
\t\t// we want a linear gradient. if it\'s there, we create a radial gradient.\n
\t\t// it is possible that a more explicit means of defining the gradient type would be\n
\t\t// better. relying on \'offset\' means that we can never have a radial gradient that uses\n
\t\t// some default offset, for instance.\n
\t\t// issue 244 suggested the \'gradientUnits\' attribute; without this, straight/flowchart connectors with gradients would\n
\t\t// not show gradients when the line was perfectly horizontal or vertical.\n
\t\tvar g;\n
\t\tif (!style.gradient.offset) {\n
\t\t\tg = _node(LINEAR_GRADIENT, {id:id, gradientUnits:"userSpaceOnUse"});\n
\t\t}\n
\t\telse {\n
\t\t\tg = _node(RADIAL_GRADIENT, {\n
\t\t\t\tid:id\n
\t\t\t});\t\t\t\n
\t\t}\n
\t\t\n
\t\tvar defs = _node(DEFS);\n
\t\tparent.appendChild(defs);\n
\t\tdefs.appendChild(g);\n
\t\t//parent.appendChild(g);\n
\t\t\n
\t\t// the svg radial gradient seems to treat stops in the reverse \n
\t\t// order to how canvas does it.  so we want to keep all the maths the same, but\n
\t\t// iterate the actual style declarations in reverse order, if the x indexes are not in order.\n
\t\tfor (var i = 0; i < style.gradient.stops.length; i++) {\n
\t\t\tvar styleToUse = uiComponent.segment == 1 ||  uiComponent.segment == 2 ? i: style.gradient.stops.length - 1 - i,\t\t\t\n
\t\t\t\tstopColor = jsPlumbUtil.convertStyle(style.gradient.stops[styleToUse][1], true),\n
\t\t\t\ts = _node(STOP, {"offset":Math.floor(style.gradient.stops[i][0] * 100) + "%", "stop-color":stopColor});\n
\n
\t\t\tg.appendChild(s);\n
\t\t}\n
\t\tvar applyGradientTo = style.strokeStyle ? STROKE : FILL;\n
        //node.setAttribute(STYLE, applyGradientTo + ":url(" + /[^#]+/.exec(document.location.toString()) + "#" + id + ")");\n
\t\t//node.setAttribute(STYLE, applyGradientTo + ":url(#" + id + ")");\n
\t\t//node.setAttribute(applyGradientTo,  "url(" + /[^#]+/.exec(document.location.toString()) + "#" + id + ")");\n
\t\tnode.setAttribute(applyGradientTo,  "url(#" + id + ")");\n
\t},\n
\t_applyStyles = function(parent, node, style, dimensions, uiComponent) {\n
\t\t\n
\t\tnode.setAttribute(FILL, style.fillStyle ? jsPlumbUtil.convertStyle(style.fillStyle, true) : NONE);\n
\t\t\tnode.setAttribute(STROKE, style.strokeStyle ? jsPlumbUtil.convertStyle(style.strokeStyle, true) : NONE);\n
\t\t\t\n
\t\tif (style.gradient) {\n
\t\t\t_updateGradient(parent, node, style, dimensions, uiComponent);\t\t\t\n
\t\t}\n
\t\telse {\n
\t\t\t// make sure we clear any existing gradient\n
\t\t\t_clearGradient(parent);\n
\t\t\tnode.setAttribute(STYLE, "");\n
\t\t}\n
\t\t\n
\t\t\n
\t\tif (style.lineWidth) {\n
\t\t\tnode.setAttribute(STROKE_WIDTH, style.lineWidth);\n
\t\t}\n
\t\n
\t\t// in SVG there is a stroke-dasharray attribute we can set, and its syntax looks like\n
\t\t// the syntax in VML but is actually kind of nasty: values are given in the pixel\n
\t\t// coordinate space, whereas in VML they are multiples of the width of the stroked\n
\t\t// line, which makes a lot more sense.  for that reason, jsPlumb is supporting both\n
\t\t// the native svg \'stroke-dasharray\' attribute, and also the \'dashstyle\' concept from\n
\t\t// VML, which will be the preferred method.  the code below this converts a dashstyle\n
\t\t// attribute given in terms of stroke width into a pixel representation, by using the\n
\t\t// stroke\'s lineWidth. \n
\t\tif (style[DASHSTYLE] && style[LINE_WIDTH] && !style[STROKE_DASHARRAY]) {\n
\t\t\tvar sep = style[DASHSTYLE].indexOf(",") == -1 ? " " : ",",\n
\t\t\tparts = style[DASHSTYLE].split(sep),\n
\t\t\tstyleToUse = "";\n
\t\t\tparts.forEach(function(p) {\n
\t\t\t\tstyleToUse += (Math.floor(p * style.lineWidth) + sep);\n
\t\t\t});\n
\t\t\tnode.setAttribute(STROKE_DASHARRAY, styleToUse);\n
\t\t}\t\t\n
\t\telse if(style[STROKE_DASHARRAY]) {\n
\t\t\tnode.setAttribute(STROKE_DASHARRAY, style[STROKE_DASHARRAY]);\n
\t\t}\n
\t\t\n
\t\t// extra attributes such as join type, dash offset.\n
\t\tfor (var i in svgAttributeMap) {\n
\t\t\tif (style[i]) {\n
\t\t\t\tnode.setAttribute(svgAttributeMap[i], style[i]);\n
\t\t\t}\n
\t\t}\n
\t},\n
\t_decodeFont = function(f) {\n
\t\tvar r = /([0-9].)(p[xt])\\s(.*)/, \n
\t\t\tbits = f.match(r);\n
\n
\t\treturn {size:bits[1] + bits[2], font:bits[3]};\t\t\n
\t},\n
\t_appendAtIndex = function(svg, path, idx) {\n
\t\tif (svg.childNodes.length > idx) {\n
\t\t\tsvg.insertBefore(path, svg.childNodes[idx]);\n
\t\t}\n
\t\telse svg.appendChild(path);\n
\t};\n
\t\n
\t/**\n
\t\tutility methods for other objects to use.\n
\t*/\n
\tjsPlumbUtil.svg = {\n
\t\tnode:_node,\n
\t\tattr:_attr,\n
\t\tpos:_pos\n
\t};\n
\t\n
 // ************************** / SVG utility methods ********************************************\t\n
\t\n
\t/*\n
\t * Base class for SVG components.\n
\t */\t\n
\tvar SvgComponent = function(params) {\n
\t\tvar pointerEventsSpec = params.pointerEventsSpec || "all", renderer = {};\n
\t\t\t\n
\t\tjsPlumb.jsPlumbUIComponent.apply(this, params.originalArgs);\n
\t\tthis.canvas = null;this.path = null;this.svg = null; this.bgCanvas = null;\n
\t\n
\t\tvar clazz = params.cssClass + " " + (params.originalArgs[0].cssClass || ""),\t\t\n
\t\t\tsvgParams = {\n
\t\t\t\t"style":"",\n
\t\t\t\t"width":0,\n
\t\t\t\t"height":0,\n
\t\t\t\t"pointer-events":pointerEventsSpec,\n
\t\t\t\t"position":"absolute"\n
\t\t\t};\t\t\t\t\n
\t\t\n
\t\tthis.svg = _node("svg", svgParams);\n
\t\t\n
\t\tif (params.useDivWrapper) {\n
\t\t\tthis.canvas = document.createElement("div");\n
\t\t\tthis.canvas.style.position = "absolute";\n
\t\t\tjsPlumbUtil.sizeElement(this.canvas,0,0,1,1);\n
\t\t\tthis.canvas.className = clazz;\n
\t\t}\n
\t\telse {\n
\t\t\t_attr(this.svg, { "class":clazz });\n
\t\t\tthis.canvas = this.svg;\n
\t\t}\n
\t\t\t\n
\t\tparams._jsPlumb.appendElement(this.canvas, params.originalArgs[0].parent);\n
\t\tif (params.useDivWrapper) this.canvas.appendChild(this.svg);\n
\t\t\n
\t\t// TODO this displayElement stuff is common between all components, across all\n
\t\t// renderers.  would be best moved to jsPlumbUIComponent.\n
\t\tvar displayElements = [ this.canvas ];\n
\t\tthis.getDisplayElements = function() { \n
\t\t\treturn displayElements; \n
\t\t};\n
\t\t\n
\t\tthis.appendDisplayElement = function(el) {\n
\t\t\tdisplayElements.push(el);\n
\t\t};\t\n
\t\t\n
\t\tthis.paint = function(style, anchor, extents) {\t   \t\t\t\n
\t\t\tif (style != null) {\n
\t\t\t\t\n
\t\t\t\tvar xy = [ this.x, this.y ], wh = [ this.w, this.h ], p;\n
\t\t\t\tif (extents != null) {\n
\t\t\t\t\tif (extents.xmin < 0) xy[0] += extents.xmin;\n
\t\t\t\t\tif (extents.ymin < 0) xy[1] += extents.ymin;\n
\t\t\t\t\twh[0] = extents.xmax + ((extents.xmin < 0) ? -extents.xmin : 0);\n
\t\t\t\t\twh[1] = extents.ymax + ((extents.ymin < 0) ? -extents.ymin : 0);\n
\t\t\t\t}\n
\n
\t\t\t\tif (params.useDivWrapper) {\t\t\t\t\t\n
\t\t\t\t\tjsPlumbUtil.sizeElement(this.canvas, xy[0], xy[1], wh[0], wh[1]);\n
\t\t\t\t\txy[0] = 0; xy[1] = 0;\n
\t\t\t\t\tp = _pos([ 0, 0 ]);\n
\t\t\t\t}\n
\t\t\t\telse\n
\t\t\t\t\tp = _pos([ xy[0], xy[1] ]);\n
                \n
                renderer.paint.apply(this, arguments);\t\t    \t\t\t    \t\n
                \n
\t\t    \t_attr(this.svg, {\n
\t    \t\t\t"style":p,\n
\t    \t\t\t"width": wh[0],\n
\t    \t\t\t"height": wh[1]\n
\t    \t\t});\t\t    \t\t    \t\t    \t\n
\t\t\t}\n
\t    };\n
\t\t\n
\t\treturn {\n
\t\t\trenderer:renderer\n
\t\t};\n
\t};\n
\t\n
\tjsPlumbUtil.extend(SvgComponent, jsPlumb.jsPlumbUIComponent, {\n
\t\tcleanup:function() {\n
\t\t\tif (this.canvas && this.canvas.parentNode) this.canvas.parentNode.removeChild(this.canvas);\n
\t\t\tthis.svg = null;\n
\t\t\tthis.canvas = null;\n
\t\t\tthis.bgCanvas = null;\n
\t\t\tthis.path = null;\t\t\t\n
\t\t\tthis.group = null;\n
\t\t},\n
\t\tsetVisible:function(v) {\n
\t\t\tif (this.canvas) {\n
\t\t\t\tthis.canvas.style.display = v ? "block" : "none";\n
\t\t\t}\n
\t\t\tif (this.bgCanvas) {\n
\t\t\t\tthis.bgCanvas.style.display = v ? "block" : "none";\n
\t\t\t}\n
\t\t}\n
\t});\n
\t\n
\t/*\n
\t * Base class for SVG connectors.\n
\t */ \n
\tvar SvgConnector = jsPlumb.ConnectorRenderers.svg = function(params) {\n
\t\tvar self = this,\n
\t\t\t_super = SvgComponent.apply(this, [ { \n
\t\t\t\tcssClass:params._jsPlumb.connectorClass, \n
\t\t\t\toriginalArgs:arguments, \n
\t\t\t\tpointerEventsSpec:"none", \n
\t\t\t\t_jsPlumb:params._jsPlumb\n
\t\t\t} ]);\t\n
\n
\t\t/*this.pointOnPath = function(location, absolute) {\n
\t\t\tif (!self.path) return [0,0];\n
\t\t\tvar p = absolute ? location : location * self.path.getTotalLength();\n
\t\t\treturn self.path.getPointAtLength(p);\n
\t\t};*/\t\t\t\n
\n
\t\t_super.renderer.paint = function(style, anchor, extents) {\n
\t\t\t\n
\t\t\tvar segments = self.getSegments(), p = "", offset = [0,0];\t\t\t\n
\t\t\tif (extents.xmin < 0) offset[0] = -extents.xmin;\n
\t\t\tif (extents.ymin < 0) offset[1] = -extents.ymin;\t\t\t\n
\n
\t\t\tif (segments.length > 0) {\n
\t\t\t\n
\t\t\t\t// create path from segments.\t\n
\t\t\t\tfor (var i = 0; i < segments.length; i++) {\n
\t\t\t\t\tp += jsPlumb.Segments.svg.SegmentRenderer.getPath(segments[i]);\n
\t\t\t\t\tp += " ";\n
\t\t\t\t}\t\t\t\n
\t\t\t\t\n
\t\t\t\tvar a = { \n
\t\t\t\t\t\td:p,\n
\t\t\t\t\t\ttransform:"translate(" + offset[0] + "," + offset[1] + ")",\n
\t\t\t\t\t\t"pointer-events":params["pointer-events"] || "visibleStroke"\n
\t\t\t\t\t}, \n
\t                outlineStyle = null,\n
\t                d = [self.x,self.y,self.w,self.h];\n
\t\t\t\t\t\n
\t\t\t\tvar mouseInOutFilters = {\n
\t\t\t\t\t"mouseenter":function(e) {\n
\t\t\t\t\t\tvar rt = e.relatedTarget;\n
\t\t\t\t\t\treturn rt == null || (rt != self.path && rt != self.bgPath);\n
\t\t\t\t\t},\n
\t\t\t\t\t"mouseout":function(e) {\n
\t\t\t\t\t\tvar rt = e.relatedTarget;\n
\t\t\t\t\t\treturn rt == null || (rt != self.path && rt != self.bgPath);\n
\t\t\t\t\t}\n
\t\t\t\t};\n
\t\t\t\t\n
\t\t\t\t// outline style.  actually means drawing an svg object underneath the main one.\n
\t\t\t\tif (style.outlineColor) {\n
\t\t\t\t\tvar outlineWidth = style.outlineWidth || 1,\n
\t\t\t\t\t\toutlineStrokeWidth = style.lineWidth + (2 * outlineWidth);\n
\t\t\t\t\toutlineStyle = jsPlumb.extend({}, style);\n
\t\t\t\t\toutlineStyle.strokeStyle = jsPlumbUtil.convertStyle(style.outlineColor);\n
\t\t\t\t\toutlineStyle.lineWidth = outlineStrokeWidth;\n
\t\t\t\t\t\n
\t\t\t\t\tif (self.bgPath == null) {\n
\t\t\t\t\t\tself.bgPath = _node("path", a);\n
\t\t\t\t    \t_appendAtIndex(self.svg, self.bgPath, 0);\n
\t\t\t    \t\tself.attachListeners(self.bgPath, self, mouseInOutFilters);\n
\t\t\t\t\t}\n
\t\t\t\t\telse {\n
\t\t\t\t\t\t_attr(self.bgPath, a);\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\t_applyStyles(self.svg, self.bgPath, outlineStyle, d, self);\n
\t\t\t\t}\t\t\t\n
\t\t\t\t\n
\t\t    \tif (self.path == null) {\n
\t\t\t    \tself.path = _node("path", a);\n
\t\t\t\t\t_appendAtIndex(self.svg, self.path, style.outlineColor ? 1 : 0);\n
\t\t\t    \tself.attachListeners(self.path, self, mouseInOutFilters);\t    \t\t    \t\t\n
\t\t    \t}\n
\t\t    \telse {\n
\t\t    \t\t_attr(self.path, a);\n
\t\t    \t}\n
\t\t    \t\t    \t\n
\t\t    \t_applyStyles(self.svg, self.path, style, d, self);\n
\t\t    }\n
\t\t};\n
\t\t\n
\t\tthis.reattachListeners = function() {\n
\t\t\tif (this.bgPath) this.reattachListenersForElement(this.bgPath, this);\n
\t\t\tif (this.path) this.reattachListenersForElement(this.path, this);\n
\t\t};\n
\t};\n
\tjsPlumbUtil.extend(jsPlumb.ConnectorRenderers.svg, SvgComponent);\n
\n
// ******************************* svg segment renderer *****************************************************\t\n
\t\t\n
\tjsPlumb.Segments.svg = {\n
\t\tSegmentRenderer : {\t\t\n
\t\t\tgetPath : function(segment) {\n
\t\t\t\treturn ({\n
\t\t\t\t\t"Straight":function() {\n
\t\t\t\t\t\tvar d = segment.getCoordinates();\n
\t\t\t\t\t\treturn "M " + d.x1 + " " + d.y1 + " L " + d.x2 + " " + d.y2;\t\n
\t\t\t\t\t},\n
\t\t\t\t\t"Bezier":function() {\n
\t\t\t\t\t\tvar d = segment.params;\n
\t\t\t\t\t\treturn "M " + d.x1 + " " + d.y1 + \n
\t\t\t\t\t\t\t" C " + d.cp1x + " " + d.cp1y + " " + d.cp2x + " " + d.cp2y + " " + d.x2 + " " + d.y2;\t\t\t\n
\t\t\t\t\t},\n
\t\t\t\t\t"Arc":function() {\n
\t\t\t\t\t\tvar d = segment.params,\n
\t\t\t\t\t\t\tlaf = segment.sweep > Math.PI ? 1 : 0,\n
\t\t\t\t\t\t\tsf = segment.anticlockwise ? 0 : 1;\t\t\t\n
\n
\t\t\t\t\t\treturn "M" + segment.x1 + " " + segment.y1 + " A " + segment.radius + " " + d.r + " 0 " + laf + "," + sf + " " + segment.x2 + " " + segment.y2;\n
\t\t\t\t\t}\n
\t\t\t\t})[segment.type]();\t\n
\t\t\t}\n
\t\t}\n
\t};\n
\t\n
// ******************************* /svg segments *****************************************************\n
   \n
    /*\n
\t * Base class for SVG endpoints.\n
\t */\n
\tvar SvgEndpoint = window.SvgEndpoint = function(params) {\n
\t\tvar _super = SvgComponent.apply(this, [ {\n
\t\t\t\tcssClass:params._jsPlumb.endpointClass, \n
\t\t\t\toriginalArgs:arguments, \n
\t\t\t\tpointerEventsSpec:"all",\n
\t\t\t\tuseDivWrapper:true,\n
\t\t\t\t_jsPlumb:params._jsPlumb\n
\t\t\t} ]);\n
\t\t\t\n
\t\t_super.renderer.paint = function(style) {\n
\t\t\tvar s = jsPlumb.extend({}, style);\n
\t\t\tif (s.outlineColor) {\n
\t\t\t\ts.strokeWidth = s.outlineWidth;\n
\t\t\t\ts.strokeStyle = jsPlumbUtil.convertStyle(s.outlineColor, true);\n
\t\t\t}\n
\t\t\t\n
\t\t\tif (this.node == null) {\n
\t\t\t\tthis.node = this.makeNode(s);\n
\t\t\t\tthis.svg.appendChild(this.node);\n
\t\t\t\tthis.attachListeners(this.node, this);\n
\t\t\t}\n
\t\t\telse if (this.updateNode != null) {\n
\t\t\t\tthis.updateNode(this.node);\n
\t\t\t}\n
\t\t\t_applyStyles(this.svg, this.node, s, [ this.x, this.y, this.w, this.h ], this);\n
\t\t\t_pos(this.node, [ this.x, this.y ]);\n
\t\t}.bind(this);\n
\t\t\t\t\n
\t};\n
\tjsPlumbUtil.extend(SvgEndpoint, SvgComponent, {\n
\t\treattachListeners : function() {\n
\t\t\tif (this.node) this.reattachListenersForElement(this.node, this);\n
\t\t}\n
\t});\n
\t\n
\t/*\n
\t * SVG Dot Endpoint\n
\t */\n
\tjsPlumb.Endpoints.svg.Dot = function() {\n
\t\tjsPlumb.Endpoints.Dot.apply(this, arguments);\n
\t\tSvgEndpoint.apply(this, arguments);\t\t\n
\t\tthis.makeNode = function(style) { \n
\t\t\treturn _node("circle", {\n
                "cx"\t:\tthis.w / 2,\n
                "cy"\t:\tthis.h / 2,\n
                "r"\t\t:\tthis.radius\n
            });\t\t\t\n
\t\t};\n
\t\tthis.updateNode = function(node) {\n
\t\t\t_attr(node, {\n
\t\t\t\t"cx":this.w / 2,\n
\t\t\t\t"cy":this.h  / 2,\n
\t\t\t\t"r":this.radius\n
\t\t\t});\n
\t\t};\n
\t};\n
\tjsPlumbUtil.extend(jsPlumb.Endpoints.svg.Dot, [jsPlumb.Endpoints.Dot, SvgEndpoint]);\n
\t\n
\t/*\n
\t * SVG Rectangle Endpoint \n
\t */\n
\tjsPlumb.Endpoints.svg.Rectangle = function() {\n
\t\tjsPlumb.Endpoints.Rectangle.apply(this, arguments);\n
\t\tSvgEndpoint.apply(this, arguments);\t\t\n
\t\tthis.makeNode = function(style) {\n
\t\t\treturn _node("rect", {\n
\t\t\t\t"width"     :   this.w,\n
\t\t\t\t"height"    :   this.h\n
\t\t\t});\n
\t\t};\n
\t\tthis.updateNode = function(node) {\n
\t\t\t_attr(node, {\n
\t\t\t\t"width":this.w,\n
\t\t\t\t"height":this.h\n
\t\t\t});\n
\t\t};\t\t\t\n
\t};\t\t\n
\tjsPlumbUtil.extend(jsPlumb.Endpoints.svg.Rectangle, [jsPlumb.Endpoints.Rectangle, SvgEndpoint]);\n
\t\n
\t/*\n
\t * SVG Image Endpoint is the default image endpoint.\n
\t */\n
\tjsPlumb.Endpoints.svg.Image = jsPlumb.Endpoints.Image;\n
\t/*\n
\t * Blank endpoint in svg renderer is the default Blank endpoint.\n
\t */\n
\tjsPlumb.Endpoints.svg.Blank = jsPlumb.Endpoints.Blank;\t\n
\t/*\n
\t * Label overlay in svg renderer is the default Label overlay.\n
\t */\n
\tjsPlumb.Overlays.svg.Label = jsPlumb.Overlays.Label;\n
\t/*\n
\t * Custom overlay in svg renderer is the default Custom overlay.\n
\t */\n
\tjsPlumb.Overlays.svg.Custom = jsPlumb.Overlays.Custom;\n
\t\t\n
\tvar AbstractSvgArrowOverlay = function(superclass, originalArgs) {\n
    \tsuperclass.apply(this, originalArgs);\n
    \tjsPlumb.jsPlumbUIComponent.apply(this, originalArgs);\n
        this.isAppendedAtTopLevel = false;\n
    \tvar self = this;\n
    \tthis.path = null;\n
    \tthis.paint = function(params, containerExtents) {\n
    \t\t// only draws on connections, not endpoints.\n
    \t\tif (params.component.svg && containerExtents) {\n
\t    \t\tif (this.path == null) {\n
\t    \t\t\tthis.path = _node("path", {\n
\t    \t\t\t\t"pointer-events":"all"\t\n
\t    \t\t\t});\n
\t    \t\t\tparams.component.svg.appendChild(this.path);\n
\t    \t\t\t\n
\t    \t\t\tthis.canvas = params.component.svg; // for the sake of completeness; this behaves the same as other overlays\n
\t    \t\t\tthis.attachListeners(this.path, params.component);\n
\t    \t\t\tthis.attachListeners(this.path, this);\n
\t    \t\t}\n
\t    \t\tvar clazz = originalArgs && (originalArgs.length == 1) ? (originalArgs[0].cssClass || "") : "",\n
\t    \t\t\toffset = [0,0];\n
\n
\t    \t\tif (containerExtents.xmin < 0) offset[0] = -containerExtents.xmin;\n
\t    \t\tif (containerExtents.ymin < 0) offset[1] = -containerExtents.ymin;\n
\t    \t\t\n
\t    \t\t_attr(this.path, { \n
\t    \t\t\t"d"\t\t\t:\tmakePath(params.d),\n
\t    \t\t\t"class" \t:\tclazz,\n
\t    \t\t\tstroke \t\t: \tparams.strokeStyle ? params.strokeStyle : null,\n
\t    \t\t\tfill \t\t: \tparams.fillStyle ? params.fillStyle : null,\n
\t    \t\t\ttransform\t: \t"translate(" + offset[0] + "," + offset[1] + ")"\n
\t    \t\t});    \t\t\n
\t    \t}\n
    \t};\n
    \tvar makePath = function(d) {\n
    \t\treturn "M" + d.hxy.x + "," + d.hxy.y +\n
    \t\t\t\t" L" + d.tail[0].x + "," + d.tail[0].y + \n
    \t\t\t\t" L" + d.cxy.x + "," + d.cxy.y + \n
    \t\t\t\t" L" + d.tail[1].x + "," + d.tail[1].y + \n
    \t\t\t\t" L" + d.hxy.x + "," + d.hxy.y;\n
    \t};\n
    \tthis.reattachListeners = function() {\n
\t\t\tif (this.path) this.reattachListenersForElement(this.path, this);\n
\t\t};\t\t\n
    };\n
    jsPlumbUtil.extend(AbstractSvgArrowOverlay, [jsPlumb.jsPlumbUIComponent, jsPlumb.Overlays.AbstractOverlay], {\n
    \tcleanup : function() {\n
    \t\tif (this.path != null) this._jsPlumb.instance.removeElement(this.path);\n
    \t},\n
    \tsetVisible:function(v) {\n
    \t\tif(this.path != null) (this.path.style.display = (v ? "block" : "none"));\n
    \t}\n
    });\n
    \n
    jsPlumb.Overlays.svg.Arrow = function() {\n
    \tAbstractSvgArrowOverlay.apply(this, [jsPlumb.Overlays.Arrow, arguments]);    \t\n
    };\n
    jsPlumbUtil.extend(jsPlumb.Overlays.svg.Arrow, [ jsPlumb.Overlays.Arrow, AbstractSvgArrowOverlay ]);\n
    \n
    jsPlumb.Overlays.svg.PlainArrow = function() {\n
    \tAbstractSvgArrowOverlay.apply(this, [jsPlumb.Overlays.PlainArrow, arguments]);    \t\n
    };\n
    jsPlumbUtil.extend(jsPlumb.Overlays.svg.PlainArrow, [ jsPlumb.Overlays.PlainArrow, AbstractSvgArrowOverlay ]);\n
    \n
    jsPlumb.Overlays.svg.Diamond = function() {\n
    \tAbstractSvgArrowOverlay.apply(this, [jsPlumb.Overlays.Diamond, arguments]);    \t\n
    };\n
    jsPlumbUtil.extend(jsPlumb.Overlays.svg.Diamond, [ jsPlumb.Overlays.Diamond, AbstractSvgArrowOverlay ]);\n
\n
    // a test\n
    jsPlumb.Overlays.svg.GuideLines = function() {\n
        var path = null, self = this, p1_1, p1_2;        \n
        jsPlumb.Overlays.GuideLines.apply(this, arguments);\n
        this.paint = function(params, containerExtents) {\n
    \t\tif (path == null) {\n
    \t\t\tpath = _node("path");\n
    \t\t\tparams.connector.svg.appendChild(path);\n
    \t\t\tself.attachListeners(path, params.connector);\n
    \t\t\tself.attachListeners(path, self);\n
\n
                p1_1 = _node("path");\n
    \t\t\tparams.connector.svg.appendChild(p1_1);\n
    \t\t\tself.attachListeners(p1_1, params.connector);\n
    \t\t\tself.attachListeners(p1_1, self);\n
\n
                p1_2 = _node("path");\n
    \t\t\tparams.connector.svg.appendChild(p1_2);\n
    \t\t\tself.attachListeners(p1_2, params.connector);\n
    \t\t\tself.attachListeners(p1_2, self);\n
    \t\t}\n
\n
    \t\tvar offset =[0,0];\n
    \t\tif (containerExtents.xmin < 0) offset[0] = -containerExtents.xmin;\n
    \t\tif (containerExtents.ymin < 0) offset[1] = -containerExtents.ymin;\n
\n
    \t\t_attr(path, {\n
    \t\t\t"d"\t\t:\tmakePath(params.head, params.tail),\n
    \t\t\tstroke \t: \t"red",\n
    \t\t\tfill \t: \tnull,\n
    \t\t\ttransform:"translate(" + offset[0] + "," + offset[1] + ")"\n
    \t\t});\n
\n
            _attr(p1_1, {\n
    \t\t\t"d"\t\t:\tmakePath(params.tailLine[0], params.tailLine[1]),\n
    \t\t\tstroke \t: \t"blue",\n
    \t\t\tfill \t: \tnull,\n
    \t\t\ttransform:"translate(" + offset[0] + "," + offset[1] + ")"\n
    \t\t});\n
\n
            _attr(p1_2, {\n
    \t\t\t"d"\t\t:\tmakePath(params.headLine[0], params.headLine[1]),\n
    \t\t\tstroke \t: \t"green",\n
    \t\t\tfill \t: \tnull,\n
    \t\t\ttransform:"translate(" + offset[0] + "," + offset[1] + ")"\n
    \t\t});\n
    \t};\n
\n
        var makePath = function(d1, d2) {\n
            return "M " + d1.x + "," + d1.y +\n
                   " L" + d2.x + "," + d2.y;\n
        };        \n
    };\n
    jsPlumbUtil.extend(jsPlumb.Overlays.svg.GuideLines, jsPlumb.Overlays.GuideLines);\n
})();\n
/*\n
 * jsPlumb\n
 * \n
 * Title:jsPlumb 1.6.2\n
 * \n
 * Provides a way to visually connect elements on an HTML page, using SVG or VML.  \n
 * \n
 * This file contains the VML renderers.\n
 *\n
 * Copyright (c) 2010 - 2014 Simon Porritt (simon@jsplumbtoolkit.com)\n
 * \n
 * http://jsplumbtoolkit.com\n
 * http://github.com/sporritt/jsplumb\n
 * \n
 * Dual licensed under the MIT and GPL2 licenses.\n
 */\n
\n
;(function() {\n
\t\n
\t"use strict";\n
\t\n
\t// http://ajaxian.com/archives/the-vml-changes-in-ie-8\n
\t// http://www.nczonline.net/blog/2010/01/19/internet-explorer-8-document-and-browser-modes/\n
\t// http://www.louisremi.com/2009/03/30/changes-in-vml-for-ie8-or-what-feature-can-the-ie-dev-team-break-for-you-today/\n
\t\n
\tvar vmlAttributeMap = {\n
\t\t"stroke-linejoin":"joinstyle",\n
\t\t"joinstyle":"joinstyle",\t\t\n
\t\t"endcap":"endcap",\n
\t\t"miterlimit":"miterlimit"\n
\t},\n
\tjsPlumbStylesheet = null;\n
\t\n
\tif (document.createStyleSheet && document.namespaces) {\t\t\t\n
\t\t\n
\t\tvar ruleClasses = [\n
\t\t\t\t".jsplumb_vml", "jsplumb\\\\:textbox", "jsplumb\\\\:oval", "jsplumb\\\\:rect", \n
\t\t\t\t"jsplumb\\\\:stroke", "jsplumb\\\\:shape", "jsplumb\\\\:group"\n
\t\t\t],\n
\t\t\trule = "behavior:url(#default#VML);position:absolute;";\n
\n
\t\tjsPlumbStylesheet = document.createStyleSheet();\n
\n
\t\tfor (var i = 0; i < ruleClasses.length; i++)\n
\t\t\tjsPlumbStylesheet.addRule(ruleClasses[i], rule);\n
\n
\t\t// in this page it is also mentioned that IE requires the extra arg to the namespace\n
\t\t// http://www.louisremi.com/2009/03/30/changes-in-vml-for-ie8-or-what-feature-can-the-ie-dev-team-break-for-you-today/\n
\t\t// but someone commented saying they didn\'t need it, and it seems jsPlumb doesnt need it either.\n
\t\t// var iev = document.documentMode;\n
\t\t//if (!iev || iev < 8)\n
\t\t\tdocument.namespaces.add("jsplumb", "urn:schemas-microsoft-com:vml");\n
\t\t//else\n
\t\t//\tdocument.namespaces.add("jsplumb", "urn:schemas-microsoft-com:vml", "#default#VML");\n
\t}\n
\t\n
\tjsPlumb.vml = {};\n
\t\n
\tvar scale = 1000,\n
    \n
\t_atts = function(o, atts) {\n
\t\tfor (var i in atts) { \n
\t\t\t// IE8 fix: setattribute does not work after an element has been added to the dom!\n
\t\t\t// http://www.louisremi.com/2009/03/30/changes-in-vml-for-ie8-or-what-feature-can-the-ie-dev-team-break-for-you-today/\n
\t\t\t//o.setAttribute(i, atts[i]);\n
\n
\t\t\t/*There is an additional problem when accessing VML elements by using get/setAttribute. The simple solution is following:\n
\n
\t\t\tif (document.documentMode==8) {\n
\t\t\tele.opacity=1;\n
\t\t\t} else {\n
\t\t\tele.setAttribute(‘opacity’,1);\n
\t\t\t}\n
\t\t\t*/\n
\n
\t\t\to[i] = atts[i];\n
\t\t}\n
\t},\n
\t_node = function(name, d, atts, parent, _jsPlumb, deferToJsPlumbContainer) {\n
\t\tatts = atts || {};\n
\t\tvar o = document.createElement("jsplumb:" + name);\n
\t\tif (deferToJsPlumbContainer)\n
\t\t\t_jsPlumb.appendElement(o, parent);\n
\t\telse\n
\t\t\t// TODO is this failing? that would be because parent is not a plain DOM element.\n
\t\t\t// IF SO, uncomment the line below this one and remove this one.\n
\t\t\tparent.appendChild(o);\n
\t\t\t//jsPlumb.getDOMElement(parent).appendChild(o);\n
\t\t\t\n
\t\to.className = (atts["class"] ? atts["class"] + " " : "") + "jsplumb_vml";\n
\t\t_pos(o, d);\n
\t\t_atts(o, atts);\n
\t\treturn o;\n
\t},\n
\t_pos = function(o,d, zIndex) {\n
\t\to.style.left = d[0] + "px";\t\t\n
\t\to.style.top =  d[1] + "px";\n
\t\to.style.width= d[2] + "px";\n
\t\to.style.height= d[3] + "px";\n
\t\to.style.position = "absolute";\n
\t\tif (zIndex)\n
\t\t\to.style.zIndex = zIndex;\n
\t},\n
\t_conv = jsPlumb.vml.convertValue = function(v) {\n
\t\treturn Math.floor(v * scale);\n
\t},\t\n
\t// tests if the given style is "transparent" and then sets the appropriate opacity node to 0 if so,\n
\t// or 1 if not.  TODO in the future, support variable opacity.\n
\t_maybeSetOpacity = function(styleToWrite, styleToCheck, type, component) {\n
\t\tif ("transparent" === styleToCheck)\n
\t\t\tcomponent.setOpacity(type, "0.0");\n
\t\telse\n
\t\t\tcomponent.setOpacity(type, "1.0");\n
\t},\n
\t_applyStyles = function(node, style, component, _jsPlumb) {\n
\t\tvar styleToWrite = {};\n
\t\tif (style.strokeStyle) {\n
\t\t\tstyleToWrite.stroked = "true";\n
\t\t\tvar strokeColor = jsPlumbUtil.convertStyle(style.strokeStyle, true);\n
\t\t\tstyleToWrite.strokecolor = strokeColor;\n
\t\t\t_maybeSetOpacity(styleToWrite, strokeColor, "stroke", component);\n
\t\t\tstyleToWrite.strokeweight = style.lineWidth + "px";\n
\t\t}\n
\t\telse styleToWrite.stroked = "false";\n
\t\t\n
\t\tif (style.fillStyle) {\n
\t\t\tstyleToWrite.filled = "true";\n
\t\t\tvar fillColor = jsPlumbUtil.convertStyle(style.fillStyle, true);\n
\t\t\tstyleToWrite.fillcolor = fillColor;\n
\t\t\t_maybeSetOpacity(styleToWrite, fillColor, "fill", component);\n
\t\t}\n
\t\telse styleToWrite.filled = "false";\n
\t\t\n
\t\tif(style.dashstyle) {\n
\t\t\tif (component.strokeNode == null) {\n
\t\t\t\tcomponent.strokeNode = _node("stroke", [0,0,0,0], { dashstyle:style.dashstyle }, node, _jsPlumb);\t\t\t\t\n
\t\t\t}\n
\t\t\telse\n
\t\t\t\tcomponent.strokeNode.dashstyle = style.dashstyle;\n
\t\t}\t\t\t\t\t\n
\t\telse if (style["stroke-dasharray"] && style.lineWidth) {\n
\t\t\tvar sep = style["stroke-dasharray"].indexOf(",") == -1 ? " " : ",",\n
\t\t\tparts = style["stroke-dasharray"].split(sep),\n
\t\t\tstyleToUse = "";\n
\t\t\tfor(var i = 0; i < parts.length; i++) {\n
\t\t\t\tstyleToUse += (Math.floor(parts[i] / style.lineWidth) + sep);\n
\t\t\t}\n
\t\t\tif (component.strokeNode == null) {\n
\t\t\t\tcomponent.strokeNode = _node("stroke", [0,0,0,0], { dashstyle:styleToUse }, node, _jsPlumb);\t\t\t\t\n
\t\t\t}\n
\t\t\telse\n
\t\t\t\tcomponent.strokeNode.dashstyle = styleToUse;\n
\t\t}\n
\t\t\n
\t\t_atts(node, styleToWrite);\n
\t},\n
\t/*\n
\t * Base class for Vml endpoints and connectors. Extends jsPlumbUIComponent. \n
\t */\n
\tVmlComponent = function() {\t\t\t\t\n
\t\tvar self = this, renderer = {};\n
\t\tjsPlumb.jsPlumbUIComponent.apply(this, arguments);\t\n
\n
\t\tthis.opacityNodes = {\n
\t\t\t"stroke":null,\n
\t\t\t"fill":null\n
\t\t};\n
\t\tthis.initOpacityNodes = function(vml) {\n
\t\t\tself.opacityNodes.stroke = _node("stroke", [0,0,1,1], {opacity:"0.0"}, vml, self._jsPlumb.instance);\n
\t\t\tself.opacityNodes.fill = _node("fill", [0,0,1,1], {opacity:"0.0"}, vml, self._jsPlumb.instance);\t\t\t\t\t\t\t\n
\t\t};\n
\t\tthis.setOpacity = function(type, value) {\n
\t\t\tvar node = self.opacityNodes[type];\n
\t\t\tif (node) node.opacity = "" + value;\n
\t\t};\n
\t\tvar displayElements = [ ];\n
\t\tthis.getDisplayElements = function() { \n
\t\t\treturn displayElements; \n
\t\t};\n
\t\t\n
\t\tthis.appendDisplayElement = function(el, doNotAppendToCanvas) {\n
\t\t\tif (!doNotAppendToCanvas) self.canvas.parentNode.appendChild(el);\n
\t\t\tdisplayElements.push(el);\n
\t\t};\n
\t};\n
\tjsPlumbUtil.extend(VmlComponent, jsPlumb.jsPlumbUIComponent, {\n
\t\tcleanup:function() {\t\t\t\n
\t\t\tif (this.bgCanvas) this.bgCanvas.parentNode.removeChild(this.bgCanvas);\n
\t\t\tif (this.canvas) this.canvas.parentNode.removeChild(this.canvas);\n
\t\t}\n
\t});\n
\n
\t/*\n
\t * Base class for Vml connectors. extends VmlComponent.\n
\t */\n
\tvar VmlConnector = jsPlumb.ConnectorRenderers.vml = function(params) {\t\t\n
\t\tthis.strokeNode = null;\n
\t\tthis.canvas = null;\n
\t\tVmlComponent.apply(this, arguments);\n
\t\tvar clazz = this._jsPlumb.instance.connectorClass + (params.cssClass ? (" " + params.cssClass) : "");\n
\t\tthis.paint = function(style) {\t\t\n
\t\t\tif (style !== null) {\t\t\t\n
\n
\t\t\t\t// we need to be at least 1 pixel in each direction, because otherwise coordsize gets set to\n
\t\t\t\t// 0 and overlays cannot paint.\n
\t\t\t\tthis.w = Math.max(this.w, 1);\n
\t\t\t\tthis.h = Math.max(this.h, 1);\n
\n
\t\t\t\tvar segments = this.getSegments(), p = { "path":"" },\n
                    d = [this.x, this.y, this.w, this.h];\n
\t\t\t\t\n
\t\t\t\t// create path from segments.\t\n
\t\t\t\tfor (var i = 0; i < segments.length; i++) {\n
\t\t\t\t\tp.path += jsPlumb.Segments.vml.SegmentRenderer.getPath(segments[i]);\n
\t\t\t\t\tp.path += " ";\n
\t\t\t\t}\n
\n
                //*\n
\t\t\t\tif (style.outlineColor) {\n
\t\t\t\t\tvar outlineWidth = style.outlineWidth || 1,\n
\t\t\t\t\toutlineStrokeWidth = style.lineWidth + (2 * outlineWidth),\n
\t\t\t\t\toutlineStyle = {\n
\t\t\t\t\t\tstrokeStyle : jsPlumbUtil.convertStyle(style.outlineColor),\n
\t\t\t\t\t\tlineWidth : outlineStrokeWidth\n
\t\t\t\t\t};\n
\t\t\t\t\tfor (var aa in vmlAttributeMap) outlineStyle[aa] = style[aa];\n
\t\t\t\t\t\n
\t\t\t\t\tif (this.bgCanvas == null) {\t\t\t\t\t\t\n
\t\t\t\t\t\tp["class"] = clazz;\n
\t\t\t\t\t\tp.coordsize = (d[2] * scale) + "," + (d[3] * scale);\n
\t\t\t\t\t\tthis.bgCanvas = _node("shape", d, p, params.parent, this._jsPlumb.instance, true);\t\t\t\t\t\t\n
\t\t\t\t\t\t_pos(this.bgCanvas, d);\n
\t\t\t\t\t\tthis.appendDisplayElement(this.bgCanvas, true);\t\n
\t\t\t\t\t\tthis.attachListeners(this.bgCanvas, this);\t\t\t\t\t\n
\t\t\t\t\t\tthis.initOpacityNodes(this.bgCanvas, ["stroke"]);\t\t\n
\t\t\t\t\t}\n
\t\t\t\t\telse {\n
\t\t\t\t\t\tp.coordsize = (d[2] * scale) + "," + (d[3] * scale);\n
\t\t\t\t\t\t_pos(this.bgCanvas, d);\n
\t\t\t\t\t\t_atts(this.bgCanvas, p);\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\t_applyStyles(this.bgCanvas, outlineStyle, this);\n
\t\t\t\t}\n
\t\t\t\t//*/\n
\t\t\t\t\n
\t\t\t\tif (this.canvas == null) {\t\t\t\t\t\t\t\t\t\t\n
\t\t\t\t\tp["class"] = clazz;\n
\t\t\t\t\tp.coordsize = (d[2] * scale) + "," + (d[3] * scale);\t\t\t\t\t\n
\t\t\t\t\tthis.canvas = _node("shape", d, p, params.parent, this._jsPlumb.instance, true);\t\t\t\t\t                                    \n
\t\t\t\t\tthis.appendDisplayElement(this.canvas, true);\t\t\t\t\t\t\t\t\t\t\n
\t\t\t\t\tthis.attachListeners(this.canvas, this);\t\t\t\t\t\n
\t\t\t\t\tthis.initOpacityNodes(this.canvas, ["stroke"]);\t\t\n
\t\t\t\t}\n
\t\t\t\telse {\n
\t\t\t\t\tp.coordsize = (d[2] * scale) + "," + (d[3] * scale);\n
\t\t\t\t\t_pos(this.canvas, d);\n
\t\t\t\t\t_atts(this.canvas, p);\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t_applyStyles(this.canvas, style, this, this._jsPlumb.instance);\n
\t\t\t}\n
\t\t};\t\n
\t\t\t\t\n
\t};\n
\tjsPlumbUtil.extend(VmlConnector, VmlComponent, {\n
\t\treattachListeners : function() {\n
\t\t\tif (this.canvas) this.reattachListenersForElement(this.canvas, this);\n
\t\t},\n
\t\tsetVisible:function(v) {\n
\t\t\tif (this.canvas) {\n
\t\t\t\tthis.canvas.style.display = v ? "block" : "none";\n
\t\t\t}\n
\t\t\tif (this.bgCanvas) {\n
\t\t\t\tthis.bgCanvas.style.display = v ? "block" : "none";\n
\t\t\t}\n
\t\t}\n
\t});\t\n
\t\n
\t/*\n
\t * \n
\t * Base class for Vml Endpoints. extends VmlComponent.\n
\t * \n
\t */\n
\tvar VmlEndpoint = window.VmlEndpoint = function(params) {\n
\t\tVmlComponent.apply(this, arguments);\n
\t\tthis._jsPlumb.vml = null;//, opacityStrokeNode = null, opacityFillNode = null;\n
\t\tthis.canvas = document.createElement("div");\n
\t\tthis.canvas.style.position = "absolute";\n
\t\tthis._jsPlumb.clazz = this._jsPlumb.instance.endpointClass + (params.cssClass ? (" " + params.cssClass) : "");\n
\n
\t\t// TODO vml endpoint adds class to VML at constructor time.  but the addClass method adds VML\n
\t\t// to the enclosing DIV. what to do?  seems like it would be better to just target the div.\n
\t\t// HOWEVER...vml connection has no containing div.  why not? it feels like it should.\n
\n
\t\tparams._jsPlumb.appendElement(this.canvas, params.parent);\n
\n
\t\tthis.paint = function(style, anchor) {\n
\t\t\tvar p = { }, vml = this._jsPlumb.vml;\t\t\t\t\n
\t\t\t\n
\t\t\tjsPlumbUtil.sizeElement(this.canvas, this.x, this.y, this.w, this.h);\n
\t\t\tif (this._jsPlumb.vml == null) {\n
\t\t\t\tp["class"] = this._jsPlumb.clazz;\n
\t\t\t\tvml = this._jsPlumb.vml = this.getVml([0,0, this.w, this.h], p, anchor, this.canvas, this._jsPlumb.instance);\t\t\t\t\n
\t\t\t\tthis.attachListeners(vml, this);\n
\n
\t\t\t\tthis.appendDisplayElement(vml, true);\n
\t\t\t\tthis.appendDisplayElement(this.canvas, true);\n
\t\t\t\t\n
\t\t\t\tthis.initOpacityNodes(vml, ["fill"]);\t\t\t\n
\t\t\t}\n
\t\t\telse {\t\t\t\t\n
\t\t\t\t_pos(vml, [0,0, this.w, this.h]);\n
\t\t\t\t_atts(vml, p);\n
\t\t\t}\n
\t\t\t\n
\t\t\t_applyStyles(vml, style, this);\n
\t\t};\t\t\n
\t};\n
\tjsPlumbUtil.extend(VmlEndpoint, VmlComponent, {\n
\t\treattachListeners : function() {\n
\t\t\tif (this._jsPlumb.vml) this.reattachListenersForElement(this._jsPlumb.vml, this);\n
\t\t}\n
\t});\n
\t\n
// ******************************* vml segments *****************************************************\t\n
\t\t\n
\tjsPlumb.Segments.vml = {\n
\t\tSegmentRenderer : {\t\t\n
\t\t\tgetPath : function(segment) {\n
\t\t\t\treturn ({\n
\t\t\t\t\t"Straight":function(segment) {\n
\t\t\t\t\t\tvar d = segment.params;\n
\t\t\t\t\t\treturn "m" + _conv(d.x1) + "," + _conv(d.y1) + " l" + _conv(d.x2) + "," + _conv(d.y2) + " e";\n
\t\t\t\t\t},\n
\t\t\t\t\t"Bezier":function(segment) {\n
\t\t\t\t\t\tvar d = segment.params;\n
\t\t\t\t\t\treturn "m" + _conv(d.x1) + "," + _conv(d.y1) + \n
\t\t\t\t   \t\t\t" c" + _conv(d.cp1x) + "," + _conv(d.cp1y) + "," + _conv(d.cp2x) + "," + _conv(d.cp2y) + "," + _conv(d.x2) + "," + _conv(d.y2) + " e";\n
\t\t\t\t\t},\n
\t\t\t\t\t"Arc":function(segment) {\t\t\t\t\t\n
\t\t\t\t\t\tvar d = segment.params,\n
\t\t\t\t\t\t\txmin = Math.min(d.x1, d.x2),\n
\t\t\t\t\t\t\txmax = Math.max(d.x1, d.x2),\n
\t\t\t\t\t\t\tymin = Math.min(d.y1, d.y2),\n
\t\t\t\t\t\t\tymax = Math.max(d.y1, d.y2),\t\t\t\t\t\t\t\t\t\t\t\t\t\t\n
\t\t\t\t\t\t\tsf = segment.anticlockwise ? 1 : 0,\n
\t\t\t\t\t\t\tpathType = (segment.anticlockwise ? "at " : "wa "),\n
\t\t\t\t\t\t\tmakePosString = function() {\n
\t\t\t\t\t\t\t\tif (d.loopback)\n
\t\t\t\t\t\t\t\t\treturn "0,0," + _conv(2*d.r) + "," + _conv(2 * d.r);\n
\n
\t\t\t\t\t\t\t\tvar xy = [\n
\t\t\t\t\t\t\t\t\t\tnull,\n
\t\t\t\t\t\t\t\t\t\t[ function() { return [xmin, ymin ];}, function() { return [xmin - d.r, ymin - d.r ];}],\n
\t\t\t\t\t\t\t\t\t\t[ function() { return [xmin - d.r, ymin ];}, function() { return [xmin, ymin - d.r ];}],\n
\t\t\t\t\t\t\t\t\t\t[ function() { return [xmin - d.r, ymin - d.r ];}, function() { return [xmin, ymin ];}],\n
\t\t\t\t\t\t\t\t\t\t[ function() { return [xmin, ymin - d.r ];}, function() { return [xmin - d.r, ymin ];}]\n
\t\t\t\t\t\t\t\t\t][segment.segment][sf]();\n
\n
\t\t\t\t\t\t\t\treturn _conv(xy[0]) + "," + _conv(xy[1]) + "," + _conv(xy[0] + (2*d.r)) + "," + _conv(xy[1] + (2*d.r));\n
\t\t\t\t\t\t\t};\n
\n
\t\t\t\t\t\treturn pathType + " " + makePosString() + "," + _conv(d.x1) + "," + _conv(d.y1) + "," + _conv(d.x2) + "," + _conv(d.y2) + " e";\t\t\t\t\t\t\t\t\t\t\t\t\n
\t\t\t\t\t}\n
\t\t\t\t\t\t\n
\t\t\t\t})[segment.type](segment);\t\n
\t\t\t}\n
\t\t}\n
\t};\n
\t\n
// ******************************* /vml segments *****************************************************\t\n
\n
// ******************************* vml endpoints *****************************************************\n
\t\n
\tjsPlumb.Endpoints.vml.Dot = function() {\n
\t\tjsPlumb.Endpoints.Dot.apply(this, arguments);\n
\t\tVmlEndpoint.apply(this, arguments);\n
\t\tthis.getVml = function(d, atts, anchor, parent, _jsPlumb) { return _node("oval", d, atts, parent, _jsPlumb); };\n
\t};\n
\tjsPlumbUtil.extend(jsPlumb.Endpoints.vml.Dot, VmlEndpoint);\n
\t\n
\tjsPlumb.Endpoints.vml.Rectangle = function() {\n
\t\tjsPlumb.Endpoints.Rectangle.apply(this, arguments);\n
\t\tVmlEndpoint.apply(this, arguments);\n
\t\tthis.getVml = function(d, atts, anchor, parent, _jsPlumb) { return _node("rect", d, atts, parent, _jsPlumb); };\n
\t};\n
\tjsPlumbUtil.extend(jsPlumb.Endpoints.vml.Rectangle, VmlEndpoint);\n
\t\n
\t/*\n
\t * VML Image Endpoint is the same as the default image endpoint.\n
\t */\n
\tjsPlumb.Endpoints.vml.Image = jsPlumb.Endpoints.Image;\n
\t\n
\t/**\n
\t * placeholder for Blank endpoint in vml renderer.\n
\t */\n
\tjsPlumb.Endpoints.vml.Blank = jsPlumb.Endpoints.Blank;\n
\t\n
// ******************************* /vml endpoints *****************************************************\t\n
\n
// ******************************* vml overlays *****************************************************\n
\t\n
\t/**\n
\t * VML Label renderer. uses the default label renderer (which adds an element to the DOM)\n
\t */\n
\tjsPlumb.Overlays.vml.Label  = jsPlumb.Overlays.Label;\n
\t\n
\t/**\n
\t * VML Custom renderer. uses the default Custom renderer (which adds an element to the DOM)\n
\t */\n
\tjsPlumb.Overlays.vml.Custom = jsPlumb.Overlays.Custom;\n
\t\n
\t/**\n
\t * Abstract VML arrow superclass\n
\t */\n
\tvar AbstractVmlArrowOverlay = function(superclass, originalArgs) {\n
    \tsuperclass.apply(this, originalArgs);\n
    \tVmlComponent.apply(this, originalArgs);\n
    \tvar self = this, path = null;\n
    \tthis.canvas = null; \n
    \tthis.isAppendedAtTopLevel = true;\n
    \tvar getPath = function(d) {    \t\t\n
    \t\treturn "m " + _conv(d.hxy.x) + "," + _conv(d.hxy.y) +\n
    \t\t       " l " + _conv(d.tail[0].x) + "," + _conv(d.tail[0].y) + \n
    \t\t       " " + _conv(d.cxy.x) + "," + _conv(d.cxy.y) + \n
    \t\t       " " + _conv(d.tail[1].x) + "," + _conv(d.tail[1].y) + \n
    \t\t       " x e";\n
    \t};\n
    \tthis.paint = function(params, containerExtents) {\n
    \t\t// only draws for connectors, not endpoints.\n
    \t\tif (params.component.canvas && containerExtents) {\n
\t    \t\tvar p = {}, d = params.d, connector = params.component;\n
\t\t\t\tif (params.strokeStyle) {\n
\t\t\t\t\tp.stroked = "true";\n
\t\t\t\t\tp.strokecolor = jsPlumbUtil.convertStyle(params.strokeStyle, true);    \t\t\t\t\n
\t\t\t\t}\n
\t\t\t\tif (params.lineWidth) p.strokeweight = params.lineWidth + "px";\n
\t\t\t\tif (params.fillStyle) {\n
\t\t\t\t\tp.filled = "true";\n
\t\t\t\t\tp.fillcolor = params.fillStyle;\n
\t\t\t\t}\t\t\t\n
\n
\t\t\t\tvar xmin = Math.min(d.hxy.x, d.tail[0].x, d.tail[1].x, d.cxy.x),\n
\t\t\t\t\tymin = Math.min(d.hxy.y, d.tail[0].y, d.tail[1].y, d.cxy.y),\n
\t\t\t\t\txmax = Math.max(d.hxy.x, d.tail[0].x, d.tail[1].x, d.cxy.x),\n
\t\t\t\t\tymax = Math.max(d.hxy.y, d.tail[0].y, d.tail[1].y, d.cxy.y),\n
\t\t\t\t\tw = Math.abs(xmax - xmin),\n
\t\t\t\t\th = Math.abs(ymax - ymin),\n
\t\t\t\t\tdim = [xmin, ymin, w, h];\n
\n
\t\t\t\t// for VML, we create overlays using shapes that have the same dimensions and\n
\t\t\t\t// coordsize as their connector - overlays calculate themselves relative to the\n
\t\t\t\t// connector (it\'s how it\'s been done since the original canvas implementation, because\n
\t\t\t\t// for canvas that makes sense).\n
\t\t\t\tp.path = getPath(d);\n
\t\t\t\tp.coordsize = (connector.w * scale) + "," + (connector.h * scale);\t\t\t\n
\t\t\t\t\n
\t\t\t\tdim[0] = connector.x;\n
\t\t\t\tdim[1] = connector.y;\n
\t\t\t\tdim[2] = connector.w;\n
\t\t\t\tdim[3] = connector.h;\n
\t\t\t\t\n
\t    \t\tif (self.canvas == null) {\n
\t    \t\t\tvar overlayClass = connector._jsPlumb.overlayClass || "";\n
\t    \t\t\tvar clazz = originalArgs && (originalArgs.length == 1) ? (originalArgs[0].cssClass || "") : "";\n
\t    \t\t\tp["class"] = clazz + " " + overlayClass;\n
\t\t\t\t\tself.canvas = _node("shape", dim, p, connector.canvas.parentNode, connector._jsPlumb.instance, true);\t\t\t\t\t\t\t\t\n
\t\t\t\t\tconnector.appendDisplayElement(self.canvas, true);\n
\t\t\t\t\tself.attachListeners(self.canvas, connector);\n
\t\t\t\t\tself.attachListeners(self.canvas, self);\n
\t\t\t\t}\n
\t\t\t\telse {\t\t\t\t\n
\t\t\t\t\t_pos(self.canvas, dim);\n
\t\t\t\t\t_atts(self.canvas, p);\n
\t\t\t\t}    \t\t\n
\t\t\t}\n
    \t};\n
    \t\n
    \tthis.reattachListeners = function() {\n
\t\t\tif (this.canvas) this.reattachListenersForElement(self.canvas, this);\n
\t\t};\n
\n
\t\tthis.cleanup = function() {\n
    \t\tif (this.canvas != null) this._jsPlumb.instance.removeElement(this.canvas);\n
    \t};\n
    };\n
    jsPlumbUtil.extend(AbstractVmlArrowOverlay, [VmlComponent, jsPlumb.Overlays.AbstractOverlay], {\n
    \tsetVisible : function(state) {\n
    \t    this.canvas.style.display = state ? "block" : "none";\n
    \t}\n
    });\n
\t\n
\tjsPlumb.Overlays.vml.Arrow = function() {\n
    \tAbstractVmlArrowOverlay.apply(this, [jsPlumb.Overlays.Arrow, arguments]);    \t\n
    };\n
    jsPlumbUtil.extend(jsPlumb.Overlays.vml.Arrow, [ jsPlumb.Overlays.Arrow, AbstractVmlArrowOverlay ]);\n
    \n
    jsPlumb.Overlays.vml.PlainArrow = function() {\n
    \tAbstractVmlArrowOverlay.apply(this, [jsPlumb.Overlays.PlainArrow, arguments]);    \t\n
    };\n
    jsPlumbUtil.extend(jsPlumb.Overlays.vml.PlainArrow, [ jsPlumb.Overlays.PlainArrow, AbstractVmlArrowOverlay ]);\n
    \n
    jsPlumb.Overlays.vml.Diamond = function() {\n
    \tAbstractVmlArrowOverlay.apply(this, [jsPlumb.Overlays.Diamond, arguments]);    \t\n
    };\n
    jsPlumbUtil.extend(jsPlumb.Overlays.vml.Diamond, [ jsPlumb.Overlays.Diamond, AbstractVmlArrowOverlay ]);\n
    \n
// ******************************* /vml overlays *****************************************************    \n
    \n
})();\n
/*\n
 * jsPlumb\n
 * \n
 * Title:jsPlumb 1.6.2\n
 * \n
 * Provides a way to visually connect elements on an HTML page, using SVG or VML.  \n
 * \n
 * This file contains the jQuery adapter.\n
 *\n
 * Copyright (c) 2010 - 2014 Simon Porritt (simon@jsplumbtoolkit.com)\n
 * \n
 * http://jsplumbtoolkit.com\n
 * http://github.com/sporritt/jsplumb\n
 * \n
 * Dual licensed under the MIT and GPL2 licenses.\n
 */  \n
;(function($) {\n
\t\n
\t"use strict";\n
\n
\tvar _getElementObject = function(el) {\n
\t\treturn typeof(el) == "string" ? $("#" + el) : $(el);\n
\t};\n
\n
\t$.extend(jsPlumbInstance.prototype, {\n
\n
// ---------------------------- DOM MANIPULATION ---------------------------------------\t\t\n
\t\t\t\t\n
\t\t\n
\t\t/**\n
\t\t* gets a DOM element from the given input, which might be a string (in which case we just do document.getElementById),\n
\t\t* a selector (in which case we return el[0]), or a DOM element already (we assume this if it\'s not either of the other\n
\t\t* two cases).  this is the opposite of getElementObject below.\n
\t\t*/\n
\t\tgetDOMElement : function(el) {\n
\t\t\tif (el == null) return null;\n
\t\t\tif (typeof(el) == "string") return document.getElementById(el);\n
\t\t\telse if (el.context || el.length != null) return el[0];\n
\t\t\telse return el;\n
\t\t},\n
\t\t\n
\t\t/**\n
\t\t * gets an "element object" from the given input.  this means an object that is used by the\n
\t\t * underlying library on which jsPlumb is running.  \'el\' may already be one of these objects,\n
\t\t * in which case it is returned as-is.  otherwise, \'el\' is a String, the library\'s lookup \n
\t\t * function is used to find the element, using the given String as the element\'s id.\n
\t\t * \n
\t\t */\n
\t\tgetElementObject : _getElementObject,\n
\n
\t\t/**\n
\t\t* removes an element from the DOM.  doing it via the library is\n
\t\t* safer from a memory perspective, as it ix expected that the library\'s \n
\t\t* remove method will unbind any event listeners before removing the element from the DOM.\n
\t\t*/\n
\t\tremoveElement:function(element) {\n
\t\t\t_getElementObject(element).remove();\n
\t\t},\n
\n
// ---------------------------- END DOM MANIPULATION ---------------------------------------\n
\n
// ---------------------------- MISCELLANEOUS ---------------------------------------\n
\n
\t\t/**\n
\t\t * animates the given element.\n
\t\t */\n
\t\tdoAnimate : function(el, properties, options) {\n
\t\t\tel.animate(properties, options);\n
\t\t},\t\n
\t\tgetSelector : function(context, spec) {\n
            if (arguments.length == 2)\n
                return _getElementObject(context).find(spec);\n
            else\n
                return $(context);\n
\t\t},\n
\n
// ---------------------------- END MISCELLANEOUS ---------------------------------------\t\t\n
\n
// -------------------------------------- DRAG/DROP\t---------------------------------\n
\t\t\n
\t\tdestroyDraggable : function(el) {\n
\t\t\tif ($(el).data("draggable"))\n
\t\t\t\t$(el).draggable("destroy");\n
\t\t},\n
\n
\t\tdestroyDroppable : function(el) {\n
\t\t\tif ($(el).data("droppable"))\n
\t\t\t\t$(el).droppable("destroy");\n
\t\t},\n
\t\t/**\n
\t\t * initialises the given element to be draggable.\n
\t\t */\n
\t\tinitDraggable : function(el, options, isPlumbedComponent) {\n
\t\t\toptions = options || {};\n
\t\t\tel = $(el);\n
\n
\t\t\toptions.start = jsPlumbUtil.wrap(options.start, function() {\n
\t\t\t\t$("body").addClass(this.dragSelectClass);\n
\t\t\t}, false);\n
\n
\t\t\toptions.stop = jsPlumbUtil.wrap(options.stop, function() {\n
\t\t\t\t$("body").removeClass(this.dragSelectClass);\n
\t\t\t});\n
\n
\t\t\t// remove helper directive if present and no override\n
\t\t\tif (!options.doNotRemoveHelper)\n
\t\t\t\toptions.helper = null;\n
\t\t\tif (isPlumbedComponent)\n
\t\t\t\toptions.scope = options.scope || jsPlumb.Defaults.Scope;\n
\t\t\tel.draggable(options);\n
\t\t},\n
\t\t\n
\t\t/**\n
\t\t * initialises the given element to be droppable.\n
\t\t */\n
\t\tinitDroppable : function(el, options) {\n
\t\t\toptions.scope = options.scope || jsPlumb.Defaults.Scope;\n
\t\t\t$(el).droppable(options);\n
\t\t},\n
\t\t\n
\t\tisAlreadyDraggable : function(el) {\n
\t\t\treturn $(el).hasClass("ui-draggable");\n
\t\t},\n
\t\t\n
\t\t/**\n
\t\t * returns whether or not drag is supported (by the library, not whether or not it is disabled) for the given element.\n
\t\t */\n
\t\tisDragSupported : function(el, options) {\n
\t\t\treturn $(el).draggable;\n
\t\t},\n
\n
\t\t/**\n
\t\t * returns whether or not drop is supported (by the library, not whether or not it is disabled) for the given element.\n
\t\t */\n
\t\tisDropSupported : function(el, options) {\n
\t\t\treturn $(el).droppable;\n
\t\t},\n
\t\t/**\n
\t\t * takes the args passed to an event function and returns you an object representing that which is being dragged.\n
\t\t */\n
\t\tgetDragObject : function(eventArgs) {\n
\t\t\t//return eventArgs[1].draggable || eventArgs[1].helper;\n
\t\t\treturn eventArgs[1].helper || eventArgs[1].draggable;\n
\t\t},\n
\t\t\n
\t\tgetDragScope : function(el) {\n
\t\t\treturn $(el).draggable("option", "scope");\n
\t\t},\n
\n
\t\tgetDropEvent : function(args) {\n
\t\t\treturn args[0];\n
\t\t},\n
\t\t\n
\t\tgetDropScope : function(el) {\n
\t\t\treturn $(el).droppable("option", "scope");\n
\t\t},\n
\t\t/**\n
\t\t * takes the args passed to an event function and returns you an object that gives the\n
\t\t * position of the object being moved, as a js object with the same params as the result of\n
\t\t * getOffset, ie: { left: xxx, top: xxx }.\n
\t\t * \n
\t\t * different libraries have different signatures for their event callbacks.  \n
\t\t * see getDragObject as well\n
\t\t */\n
\t\tgetUIPosition : function(eventArgs, zoom, dontAdjustHelper) {\n
\t\t\tvar ret;\n
\t\t\tzoom = zoom || 1;\n
\t\t\tif (eventArgs.length == 1) {\n
\t\t\t\tret = { left: eventArgs[0].pageX, top:eventArgs[0].pageY };\n
\t\t\t}\n
\t\t\telse {\n
\t\t\t\tvar ui = eventArgs[1],\n
\t\t\t\t  _offset = ui.position;//ui.offset;\n
\t\t\t\t  \n
\t\t\t\tret = _offset || ui.absolutePosition;\n
\t\t\t\t\n
\t\t\t\t// adjust ui position to account for zoom, because jquery ui does not do this.\n
\t\t\t\tif (!dontAdjustHelper) {\n
\t\t\t\t\tui.position.left /= zoom;\n
\t\t\t\t\tui.position.top /= zoom;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\treturn { left:ret.left, top: ret.top  };\n
\t\t},\n
\t\t\n
\t\tisDragFilterSupported:function() { return true; },\n
\t\t\n
\t\tsetDragFilter : function(el, filter) {\n
\t\t\tif (jsPlumb.isAlreadyDraggable(el))\n
\t\t\t\t$(el).draggable("option", "cancel", filter);\n
\t\t},\n
\t\t\n
\t\tsetElementDraggable : function(el, draggable) {\n
\t\t\t$(el).draggable("option", "disabled", !draggable);\n
\t\t},\n
\t\t\n
\t\tsetDragScope : function(el, scope) {\n
\t\t\t$(el).draggable("option", "scope", scope);\n
\t\t},\n
\t\t/**\n
         * mapping of drag events for jQuery\n
         */\n
\t\tdragEvents : {\n
\t\t\t\'start\':\'start\', \'stop\':\'stop\', \'drag\':\'drag\', \'step\':\'step\',\n
\t\t\t\'over\':\'over\', \'out\':\'out\', \'drop\':\'drop\', \'complete\':\'complete\'\n
\t\t},\n
\t\tanimEvents:{\n
\t\t\t\'step\':"step", \'complete\':\'complete\'\n
\t\t},\n
\t\t\n
// -------------------------------------- END DRAG/DROP\t---------------------------------\t\t\n
\n
// -------------------------------------- EVENTS\t---------------------------------\t\t\n
\n
\t\t/**\n
\t\t * note that jquery ignores the name of the event you wanted to trigger, and figures it out for itself.\n
\t\t * the other libraries do not.  yui, in fact, cannot even pass an original event.  we have to pull out stuff\n
\t\t * from the originalEvent to put in an options object for YUI. \n
\t\t * @param el\n
\t\t * @param event\n
\t\t * @param originalEvent\n
\t\t */\n
\t\ttrigger : function(el, event, originalEvent) {\n
\t\t\tvar h = jQuery._data(_getElementObject(el)[0], "handle");\n
            h(originalEvent);\n
\t\t},\n
\t\tgetOriginalEvent : function(e) {\n
\t\t\treturn e.originalEvent;\n
\t\t},\n
\n
\t\t// note: for jquery we support the delegation stuff here\n
\t\ton : function(el, event, callback) {\n
\t\t\tel = _getElementObject(el);\n
\t\t\tvar a = []; a.push.apply(a, arguments);\n
\t\t\tel.on.apply(el, a.slice(1));\n
\t\t},\t\t\t\t\n
\t\t\n
\t\t// note: for jquery we support the delegation stuff here\n
\t\toff : function(el, event, callback) {\n
\t\t\tel = _getElementObject(el);\n
\t\t\tvar a = []; a.push.apply(a, arguments);\n
\t\t\tel.off.apply(el, a.slice(1));\n
\t\t}\n
\n
// -------------------------------------- END EVENTS\t---------------------------------\t\t\n
\n
\t});\n
\n
\t$(document).ready(jsPlumb.init);\n
\n
})(jQuery);\n
\n


]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <none/>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
