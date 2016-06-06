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
            <value> <string>coords.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals $, svgroot */\n
/*jslint vars: true, eqeq: true, forin: true*/\n
/**\n
 * Coords.\n
 *\n
 * Licensed under the MIT License\n
 *\n
 */\n
\n
// Dependencies:\n
// 1) jquery.js\n
// 2) math.js\n
// 3) browser.js\n
// 4) svgutils.js\n
// 5) units.js\n
// 6) svgtransformlist.js\n
\n
var svgedit = svgedit || {};\n
\n
(function() {\'use strict\';\n
\n
if (!svgedit.coords) {\n
  svgedit.coords = {};\n
}\n
\n
// this is how we map paths to our preferred relative segment types\n
var pathMap = [0, \'z\', \'M\', \'m\', \'L\', \'l\', \'C\', \'c\', \'Q\', \'q\', \'A\', \'a\', \n
    \'H\', \'h\', \'V\', \'v\', \'S\', \'s\', \'T\', \'t\'];\n
\n
/**\n
 * @typedef editorContext\n
 * @type {?object}\n
 * @property {function} getGridSnapping\n
 * @property {function} getDrawing\n
*/\n
var editorContext_ = null;\n
\n
/**\n
* @param {editorContext} editorContext\n
*/\n
svgedit.coords.init = function(editorContext) {\n
  editorContext_ = editorContext;\n
};\n
\n
/**\n
 * Applies coordinate changes to an element based on the given matrix\n
 * @param {Element} selected - DOM element to be changed\n
 * @param {object} changes - Object with changes to be remapped\n
 * @param {SVGMatrix} m - Matrix object to use for remapping coordinates\n
*/\n
svgedit.coords.remapElement = function(selected, changes, m) {\n
  var i, type,\n
    remap = function(x, y) { return svgedit.math.transformPoint(x, y, m); },\n
    scalew = function(w) { return m.a * w; },\n
    scaleh = function(h) { return m.d * h; },\n
    doSnapping = editorContext_.getGridSnapping() && selected.parentNode.parentNode.localName === \'svg\',\n
    finishUp = function() {\n
      var o;\n
      if (doSnapping) {\n
        for (o in changes) {\n
          changes[o] = svgedit.utilities.snapToGrid(changes[o]);\n
        }\n
      }\n
      svgedit.utilities.assignAttributes(selected, changes, 1000, true);\n
    },\n
    box = svgedit.utilities.getBBox(selected);\n
\n
  for (i = 0; i < 2; i++) {\n
    type = i === 0 ? \'fill\' : \'stroke\';\n
    var attrVal = selected.getAttribute(type);\n
    if (attrVal && attrVal.indexOf(\'url(\') === 0) {\n
      if (m.a < 0 || m.d < 0) {\n
        var grad = svgedit.utilities.getRefElem(attrVal);\n
        var newgrad = grad.cloneNode(true);\n
        if (m.a < 0) {\n
          // flip x\n
          var x1 = newgrad.getAttribute(\'x1\');\n
          var x2 = newgrad.getAttribute(\'x2\');\n
          newgrad.setAttribute(\'x1\', -(x1 - 1));\n
          newgrad.setAttribute(\'x2\', -(x2 - 1));\n
        } \n
\n
        if (m.d < 0) {\n
          // flip y\n
          var y1 = newgrad.getAttribute(\'y1\');\n
          var y2 = newgrad.getAttribute(\'y2\');\n
          newgrad.setAttribute(\'y1\', -(y1 - 1));\n
          newgrad.setAttribute(\'y2\', -(y2 - 1));\n
        }\n
        newgrad.id = editorContext_.getDrawing().getNextId();\n
        svgedit.utilities.findDefs().appendChild(newgrad);\n
        selected.setAttribute(type, \'url(#\' + newgrad.id + \')\');\n
      }\n
\n
      // Not really working :(\n
//      if (selected.tagName === \'path\') {\n
//        reorientGrads(selected, m);\n
//      }\n
    }\n
  }\n
\n
  var elName = selected.tagName;\n
  var chlist, mt;\n
  if (elName === \'g\' || elName === \'text\' || elName == \'tspan\' || elName === \'use\') {\n
    // if it was a translate, then just update x,y\n
    if (m.a == 1 && m.b == 0 && m.c == 0 && m.d == 1 && (m.e != 0 || m.f != 0) ) {\n
      // [T][M] = [M][T\']\n
      // therefore [T\'] = [M_inv][T][M]\n
      var existing = svgedit.math.transformListToTransform(selected).matrix,\n
          t_new = svgedit.math.matrixMultiply(existing.inverse(), m, existing);\n
      changes.x = parseFloat(changes.x) + t_new.e;\n
      changes.y = parseFloat(changes.y) + t_new.f;\n
    } else {\n
      // we just absorb all matrices into the element and don\'t do any remapping\n
      chlist = svgedit.transformlist.getTransformList(selected);\n
      mt = svgroot.createSVGTransform();\n
      mt.setMatrix(svgedit.math.matrixMultiply(svgedit.math.transformListToTransform(chlist).matrix, m));\n
      chlist.clear();\n
      chlist.appendItem(mt);\n
    }\n
  }\n
  var c, pt, pt1, pt2, len;\n
  // now we have a set of changes and an applied reduced transform list\n
  // we apply the changes directly to the DOM\n
  switch (elName) {\n
    case \'foreignObject\':\n
    case \'rect\':\n
    case \'image\':\n
      // Allow images to be inverted (give them matrix when flipped)\n
      if (elName === \'image\' && (m.a < 0 || m.d < 0)) {\n
        // Convert to matrix\n
        chlist = svgedit.transformlist.getTransformList(selected);\n
        mt = svgroot.createSVGTransform();\n
        mt.setMatrix(svgedit.math.matrixMultiply(svgedit.math.transformListToTransform(chlist).matrix, m));\n
        chlist.clear();\n
        chlist.appendItem(mt);\n
      } else {\n
        pt1 = remap(changes.x, changes.y);\n
        changes.width = scalew(changes.width);\n
        changes.height = scaleh(changes.height);\n
        changes.x = pt1.x + Math.min(0, changes.width);\n
        changes.y = pt1.y + Math.min(0, changes.height);\n
        changes.width = Math.abs(changes.width);\n
        changes.height = Math.abs(changes.height);\n
      }\n
      finishUp();\n
      break;\n
    case \'ellipse\':\n
      c = remap(changes.cx, changes.cy);\n
      changes.cx = c.x;\n
      changes.cy = c.y;\n
      changes.rx = scalew(changes.rx);\n
      changes.ry = scaleh(changes.ry);\n
      changes.rx = Math.abs(changes.rx);\n
      changes.ry = Math.abs(changes.ry);\n
      finishUp();\n
      break;\n
    case \'circle\':\n
      c = remap(changes.cx,changes.cy);\n
      changes.cx = c.x;\n
      changes.cy = c.y;\n
      // take the minimum of the new selected box\'s dimensions for the new circle radius\n
      var tbox = svgedit.math.transformBox(box.x, box.y, box.width, box.height, m);\n
      var w = tbox.tr.x - tbox.tl.x, h = tbox.bl.y - tbox.tl.y;\n
      changes.r = Math.min(w/2, h/2);\n
\n
      if (changes.r) {changes.r = Math.abs(changes.r);}\n
      finishUp();\n
      break;\n
    case \'line\':\n
      pt1 = remap(changes.x1, changes.y1);\n
      pt2 = remap(changes.x2, changes.y2);\n
      changes.x1 = pt1.x;\n
      changes.y1 = pt1.y;\n
      changes.x2 = pt2.x;\n
      changes.y2 = pt2.y;\n
      // deliberately fall through here\n
    case \'text\':\n
    case \'tspan\':\n
    case \'use\':\n
      finishUp();\n
      break;\n
    case \'g\':\n
      var gsvg = $(selected).data(\'gsvg\');\n
      if (gsvg) {\n
          svgedit.utilities.assignAttributes(gsvg, changes, 1000, true);\n
      }\n
      break;\n
    case \'polyline\':\n
    case \'polygon\':\n
      len = changes.points.length;\n
      for (i = 0; i < len; ++i) {\n
        pt = changes.points[i];\n
        pt = remap(pt.x, pt.y);\n
        changes.points[i].x = pt.x;\n
        changes.points[i].y = pt.y;\n
      }\n
\n
      len = changes.points.length;\n
      var pstr = \'\';\n
      for (i = 0; i < len; ++i) {\n
        pt = changes.points[i];\n
        pstr += pt.x + \',\' + pt.y + \' \';\n
      }\n
      selected.setAttribute(\'points\', pstr);\n
      break;\n
    case \'path\':\n
      var seg;\n
      var segList = selected.pathSegList;\n
      len = segList.numberOfItems;\n
      changes.d = [];\n
      for (i = 0; i < len; ++i) {\n
          seg = segList.getItem(i);\n
          changes.d[i] = {\n
              type: seg.pathSegType,\n
              x: seg.x,\n
              y: seg.y,\n
              x1: seg.x1,\n
              y1: seg.y1,\n
              x2: seg.x2,\n
              y2: seg.y2,\n
              r1: seg.r1,\n
              r2: seg.r2,\n
              angle: seg.angle,\n
              largeArcFlag: seg.largeArcFlag,\n
              sweepFlag: seg.sweepFlag\n
          };\n
      }\n
\n
      len = changes.d.length;\n
      var firstseg = changes.d[0],\n
          currentpt = remap(firstseg.x, firstseg.y);\n
      changes.d[0].x = currentpt.x;\n
      changes.d[0].y = currentpt.y;\n
      for (i = 1; i < len; ++i) {\n
        seg = changes.d[i];\n
        type = seg.type;\n
        // if absolute or first segment, we want to remap x, y, x1, y1, x2, y2\n
        // if relative, we want to scalew, scaleh\n
        if (type % 2 == 0) { // absolute\n
          var thisx = (seg.x != undefined) ? seg.x : currentpt.x, // for V commands\n
              thisy = (seg.y != undefined) ? seg.y : currentpt.y; // for H commands\n
          pt = remap(thisx,thisy);\n
          pt1 = remap(seg.x1, seg.y1);\n
          pt2 = remap(seg.x2, seg.y2);\n
          seg.x = pt.x;\n
          seg.y = pt.y;\n
          seg.x1 = pt1.x;\n
          seg.y1 = pt1.y;\n
          seg.x2 = pt2.x;\n
          seg.y2 = pt2.y;\n
          seg.r1 = scalew(seg.r1);\n
          seg.r2 = scaleh(seg.r2);\n
        }\n
        else { // relative\n
          seg.x = scalew(seg.x);\n
          seg.y = scaleh(seg.y);\n
          seg.x1 = scalew(seg.x1);\n
          seg.y1 = scaleh(seg.y1);\n
          seg.x2 = scalew(seg.x2);\n
          seg.y2 = scaleh(seg.y2);\n
          seg.r1 = scalew(seg.r1);\n
          seg.r2 = scaleh(seg.r2);\n
        }\n
      } // for each segment\n
\n
      var dstr = \'\';\n
      len = changes.d.length;\n
      for (i = 0; i < len; ++i) {\n
        seg = changes.d[i];\n
        type = seg.type;\n
        dstr += pathMap[type];\n
        switch (type) {\n
            case 13: // relative horizontal line (h)\n
            case 12: // absolute horizontal line (H)\n
                dstr += seg.x + \' \';\n
                break;\n
            case 15: // relative vertical line (v)\n
            case 14: // absolute vertical line (V)\n
                dstr += seg.y + \' \';\n
                break;\n
            case 3: // relative move (m)\n
            case 5: // relative line (l)\n
            case 19: // relative smooth quad (t)\n
            case 2: // absolute move (M)\n
            case 4: // absolute line (L)\n
            case 18: // absolute smooth quad (T)\n
                dstr += seg.x + \',\' + seg.y + \' \';\n
                break;\n
            case 7: // relative cubic (c)\n
            case 6: // absolute cubic (C)\n
                dstr += seg.x1 + \',\' + seg.y1 + \' \' + seg.x2 + \',\' + seg.y2 + \' \' +\n
                     seg.x + \',\' + seg.y + \' \';\n
                break;\n
            case 9: // relative quad (q) \n
            case 8: // absolute quad (Q)\n
                dstr += seg.x1 + \',\' + seg.y1 + \' \' + seg.x + \',\' + seg.y + \' \';\n
                break;\n
            case 11: // relative elliptical arc (a)\n
            case 10: // absolute elliptical arc (A)\n
                dstr += seg.r1 + \',\' + seg.r2 + \' \' + seg.angle + \' \' + (+seg.largeArcFlag) +\n
                    \' \' + (+seg.sweepFlag) + \' \' + seg.x + \',\' + seg.y + \' \';\n
                break;\n
            case 17: // relative smooth cubic (s)\n
            case 16: // absolute smooth cubic (S)\n
                dstr += seg.x2 + \',\' + seg.y2 + \' \' + seg.x + \',\' + seg.y + \' \';\n
                break;\n
          }\n
      }\n
\n
      selected.setAttribute(\'d\', dstr);\n
      break;\n
    }\n
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
            <value> <int>10447</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
