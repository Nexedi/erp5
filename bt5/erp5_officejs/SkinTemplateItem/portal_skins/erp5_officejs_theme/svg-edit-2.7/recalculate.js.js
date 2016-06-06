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
            <value> <string>recalculate.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals $*/\n
/*jslint vars: true, eqeq: true, continue: true*/\n
/**\n
 * Recalculate.\n
 *\n
 * Licensed under the MIT License\n
 *\n
 */\n
\n
// Dependencies:\n
// 1) jquery\n
// 2) jquery-svg.js\n
// 3) svgedit.js\n
// 4) browser.js\n
// 5) math.js\n
// 6) history.js\n
// 7) units.js\n
// 8) svgtransformlist.js\n
// 9) svgutils.js\n
// 10) coords.js\n
\n
var svgedit = svgedit || {};\n
\n
(function() {\n
\n
if (!svgedit.recalculate) {\n
  svgedit.recalculate = {};\n
}\n
\n
var NS = svgedit.NS;\n
var context_;\n
\n
// Function: svgedit.recalculate.init\n
svgedit.recalculate.init = function(editorContext) {\n
  context_ = editorContext;\n
};\n
\n
\n
// Function: svgedit.recalculate.updateClipPath\n
// Updates a <clipPath>s values based on the given translation of an element\n
//\n
// Parameters:\n
// attr - The clip-path attribute value with the clipPath\'s ID\n
// tx - The translation\'s x value\n
// ty - The translation\'s y value\n
svgedit.recalculate.updateClipPath = function(attr, tx, ty) {\n
  var path = getRefElem(attr).firstChild;\n
  var cp_xform = svgedit.transformlist.getTransformList(path);\n
  var newxlate = context_.getSVGRoot().createSVGTransform();\n
  newxlate.setTranslate(tx, ty);\n
\n
  cp_xform.appendItem(newxlate);\n
\n
  // Update clipPath\'s dimensions\n
  svgedit.recalculate.recalculateDimensions(path);\n
};\n
\n
\n
// Function: svgedit.recalculate.recalculateDimensions\n
// Decides the course of action based on the element\'s transform list\n
//\n
// Parameters:\n
// selected - The DOM element to recalculate\n
//\n
// Returns: \n
// Undo command object with the resulting change\n
svgedit.recalculate.recalculateDimensions = function(selected) {\n
  if (selected == null) {return null;}\n
\n
  // Firefox Issue - 1081\n
  if (selected.nodeName == "svg" && navigator.userAgent.indexOf("Firefox/20") >= 0) {\n
    return null;\n
  }\n
\n
  var svgroot = context_.getSVGRoot();\n
  var tlist = svgedit.transformlist.getTransformList(selected);\n
  var k;\n
  // remove any unnecessary transforms\n
  if (tlist && tlist.numberOfItems > 0) {\n
    k = tlist.numberOfItems;\n
    while (k--) {\n
      var xform = tlist.getItem(k);\n
      if (xform.type === 0) {\n
        tlist.removeItem(k);\n
      }\n
      // remove identity matrices\n
      else if (xform.type === 1) {\n
        if (svgedit.math.isIdentity(xform.matrix)) {\n
          tlist.removeItem(k);\n
        }\n
      }\n
      // remove zero-degree rotations\n
      else if (xform.type === 4) {\n
        if (xform.angle === 0) {\n
          tlist.removeItem(k);\n
        }\n
      }\n
    }\n
    // End here if all it has is a rotation\n
    if (tlist.numberOfItems === 1 &&\n
        svgedit.utilities.getRotationAngle(selected)) {return null;}\n
  }\n
\n
  // if this element had no transforms, we are done\n
  if (!tlist || tlist.numberOfItems == 0) {\n
    // Chrome has a bug that requires clearing the attribute first.\n
    selected.setAttribute(\'transform\', \'\');\n
    selected.removeAttribute(\'transform\');\n
    return null;\n
  }\n
\n
  // TODO: Make this work for more than 2\n
  if (tlist) {\n
    k = tlist.numberOfItems;\n
    var mxs = [];\n
    while (k--) {\n
      var xform = tlist.getItem(k);\n
      if (xform.type === 1) {\n
        mxs.push([xform.matrix, k]);\n
      } else if (mxs.length) {\n
        mxs = [];\n
      }\n
    }\n
    if (mxs.length === 2) {\n
      var m_new = svgroot.createSVGTransformFromMatrix(svgedit.math.matrixMultiply(mxs[1][0], mxs[0][0]));\n
      tlist.removeItem(mxs[0][1]);\n
      tlist.removeItem(mxs[1][1]);\n
      tlist.insertItemBefore(m_new, mxs[1][1]);\n
    }\n
\n
    // combine matrix + translate\n
    k = tlist.numberOfItems;\n
    if (k >= 2 && tlist.getItem(k-2).type === 1 && tlist.getItem(k-1).type === 2) {\n
      var mt = svgroot.createSVGTransform();\n
\n
      var m = svgedit.math.matrixMultiply(\n
          tlist.getItem(k-2).matrix, \n
          tlist.getItem(k-1).matrix);   \n
      mt.setMatrix(m);\n
      tlist.removeItem(k-2);\n
      tlist.removeItem(k-2);\n
      tlist.appendItem(mt);\n
    }\n
  }\n
\n
  // If it still has a single [M] or [R][M], return null too (prevents BatchCommand from being returned).\n
  switch ( selected.tagName ) {\n
    // Ignore these elements, as they can absorb the [M]\n
    case \'line\':\n
    case \'polyline\':\n
    case \'polygon\':\n
    case \'path\':\n
      break;\n
    default:\n
      if ((tlist.numberOfItems === 1 && tlist.getItem(0).type === 1) ||\n
          (tlist.numberOfItems === 2 && tlist.getItem(0).type === 1 && tlist.getItem(0).type === 4)) {\n
        return null;\n
      }\n
  }\n
\n
  // Grouped SVG element \n
  var gsvg = $(selected).data(\'gsvg\');\n
\n
  // we know we have some transforms, so set up return variable   \n
  var batchCmd = new svgedit.history.BatchCommand(\'Transform\');\n
\n
  // store initial values that will be affected by reducing the transform list\n
  var changes = {}, initial = null, attrs = [];\n
  switch (selected.tagName) {\n
    case \'line\':\n
      attrs = [\'x1\', \'y1\', \'x2\', \'y2\'];\n
      break;\n
    case \'circle\':\n
      attrs = [\'cx\', \'cy\', \'r\'];\n
      break;\n
    case \'ellipse\':\n
      attrs = [\'cx\', \'cy\', \'rx\', \'ry\'];\n
      break;\n
    case \'foreignObject\':\n
    case \'rect\':\n
    case \'image\':\n
      attrs = [\'width\', \'height\', \'x\', \'y\'];\n
      break;\n
    case \'use\':\n
    case \'text\':\n
    case \'tspan\':\n
      attrs = [\'x\', \'y\'];\n
      break;\n
    case \'polygon\':\n
    case \'polyline\':\n
      initial = {};\n
      initial.points = selected.getAttribute(\'points\');\n
      var list = selected.points;\n
      var len = list.numberOfItems;\n
      changes.points = new Array(len);\n
\t  var i;\n
      for (i = 0; i < len; ++i) {\n
        var pt = list.getItem(i);\n
        changes.points[i] = {x:pt.x, y:pt.y};\n
      }\n
      break;\n
    case \'path\':\n
      initial = {};\n
      initial.d = selected.getAttribute(\'d\');\n
      changes.d = selected.getAttribute(\'d\');\n
      break;\n
    } // switch on element type to get initial values\n
\n
    if (attrs.length) {\n
      changes = $(selected).attr(attrs);\n
      $.each(changes, function(attr, val) {\n
        changes[attr] = svgedit.units.convertToNum(attr, val);\n
      });\n
    } else if (gsvg) {\n
      // GSVG exception\n
      changes = {\n
        x: $(gsvg).attr(\'x\') || 0,\n
        y: $(gsvg).attr(\'y\') || 0\n
      };\n
    }\n
\n
  // if we haven\'t created an initial array in polygon/polyline/path, then \n
  // make a copy of initial values and include the transform\n
  if (initial == null) {\n
    initial = $.extend(true, {}, changes);\n
    $.each(initial, function(attr, val) {\n
      initial[attr] = svgedit.units.convertToNum(attr, val);\n
    });\n
  }\n
  // save the start transform value too\n
  initial.transform = context_.getStartTransform() || \'\';\n
\n
  // if it\'s a regular group, we have special processing to flatten transforms\n
  if ((selected.tagName == \'g\' && !gsvg) || selected.tagName == \'a\') {\n
    var box = svgedit.utilities.getBBox(selected),\n
      oldcenter = {x: box.x+box.width/2, y: box.y+box.height/2},\n
      newcenter = svgedit.math.transformPoint(box.x+box.width/2,\n
        box.y+box.height/2,\n
        svgedit.math.transformListToTransform(tlist).matrix),\n
      m = svgroot.createSVGMatrix();\n
\n
    // temporarily strip off the rotate and save the old center\n
    var gangle = svgedit.utilities.getRotationAngle(selected);\n
    if (gangle) {\n
      var a = gangle * Math.PI / 180;\n
      if ( Math.abs(a) > (1.0e-10) ) {\n
        var s = Math.sin(a)/(1 - Math.cos(a));\n
      } else {\n
        // FIXME: This blows up if the angle is exactly 0!\n
        var s = 2/a;\n
      }\n
\t  var i;\n
      for (i = 0; i < tlist.numberOfItems; ++i) {\n
        var xform = tlist.getItem(i);\n
        if (xform.type == 4) {\n
          // extract old center through mystical arts\n
          var rm = xform.matrix;\n
          oldcenter.y = (s*rm.e + rm.f)/2;\n
          oldcenter.x = (rm.e - s*rm.f)/2;\n
          tlist.removeItem(i);\n
          break;\n
        }\n
      }\n
    }\n
    var tx = 0, ty = 0,\n
      operation = 0,\n
      N = tlist.numberOfItems;\n
\n
    if (N) {\n
      var first_m = tlist.getItem(0).matrix;\n
    }\n
\n
    // first, if it was a scale then the second-last transform will be it\n
    if (N >= 3 && tlist.getItem(N-2).type == 3 && \n
      tlist.getItem(N-3).type == 2 && tlist.getItem(N-1).type == 2) \n
    {\n
      operation = 3; // scale\n
    \n
      // if the children are unrotated, pass the scale down directly\n
      // otherwise pass the equivalent matrix() down directly\n
      var tm = tlist.getItem(N-3).matrix,\n
        sm = tlist.getItem(N-2).matrix,\n
        tmn = tlist.getItem(N-1).matrix;\n
    \n
      var children = selected.childNodes;\n
      var c = children.length;\n
      while (c--) {\n
        var child = children.item(c);\n
        tx = 0;\n
        ty = 0;\n
        if (child.nodeType == 1) {\n
          var childTlist = svgedit.transformlist.getTransformList(child);\n
\n
          // some children might not have a transform (<metadata>, <defs>, etc)\n
          if (!childTlist) {continue;}\n
\n
          var m = svgedit.math.transformListToTransform(childTlist).matrix;\n
\n
          // Convert a matrix to a scale if applicable\n
//          if (svgedit.math.hasMatrixTransform(childTlist) && childTlist.numberOfItems == 1) {\n
//            if (m.b==0 && m.c==0 && m.e==0 && m.f==0) {\n
//              childTlist.removeItem(0);\n
//              var translateOrigin = svgroot.createSVGTransform(),\n
//                scale = svgroot.createSVGTransform(),\n
//                translateBack = svgroot.createSVGTransform();\n
//              translateOrigin.setTranslate(0, 0);\n
//              scale.setScale(m.a, m.d);\n
//              translateBack.setTranslate(0, 0);\n
//              childTlist.appendItem(translateBack);\n
//              childTlist.appendItem(scale);\n
//              childTlist.appendItem(translateOrigin);\n
//            }\n
//          }\n
        \n
          var angle = svgedit.utilities.getRotationAngle(child);\n
          var oldStartTransform = context_.getStartTransform();\n
          var childxforms = [];\n
          context_.setStartTransform(child.getAttribute(\'transform\'));\n
          if (angle || svgedit.math.hasMatrixTransform(childTlist)) {\n
            var e2t = svgroot.createSVGTransform();\n
            e2t.setMatrix(svgedit.math.matrixMultiply(tm, sm, tmn, m));\n
            childTlist.clear();\n
            childTlist.appendItem(e2t);\n
            childxforms.push(e2t);\n
          }\n
          // if not rotated or skewed, push the [T][S][-T] down to the child\n
          else {\n
            // update the transform list with translate,scale,translate\n
            \n
            // slide the [T][S][-T] from the front to the back\n
            // [T][S][-T][M] = [M][T2][S2][-T2]\n
            \n
            // (only bringing [-T] to the right of [M])\n
            // [T][S][-T][M] = [T][S][M][-T2]\n
            // [-T2] = [M_inv][-T][M]\n
            var t2n = svgedit.math.matrixMultiply(m.inverse(), tmn, m);\n
            // [T2] is always negative translation of [-T2]\n
            var t2 = svgroot.createSVGMatrix();\n
            t2.e = -t2n.e;\n
            t2.f = -t2n.f;\n
            \n
            // [T][S][-T][M] = [M][T2][S2][-T2]\n
            // [S2] = [T2_inv][M_inv][T][S][-T][M][-T2_inv]\n
            var s2 = svgedit.math.matrixMultiply(t2.inverse(), m.inverse(), tm, sm, tmn, m, t2n.inverse());\n
\n
            var translateOrigin = svgroot.createSVGTransform(),\n
              scale = svgroot.createSVGTransform(),\n
              translateBack = svgroot.createSVGTransform();\n
            translateOrigin.setTranslate(t2n.e, t2n.f);\n
            scale.setScale(s2.a, s2.d);\n
            translateBack.setTranslate(t2.e, t2.f);\n
            childTlist.appendItem(translateBack);\n
            childTlist.appendItem(scale);\n
            childTlist.appendItem(translateOrigin);\n
            childxforms.push(translateBack);\n
            childxforms.push(scale);\n
            childxforms.push(translateOrigin);\n
//            logMatrix(translateBack.matrix);\n
//            logMatrix(scale.matrix);\n
          } // not rotated\n
          batchCmd.addSubCommand( svgedit.recalculate.recalculateDimensions(child) );\n
          // TODO: If any <use> have this group as a parent and are \n
          // referencing this child, then we need to impose a reverse \n
          // scale on it so that when it won\'t get double-translated\n
//            var uses = selected.getElementsByTagNameNS(NS.SVG, \'use\');\n
//            var href = \'#\' + child.id;\n
//            var u = uses.length;\n
//            while (u--) {\n
//              var useElem = uses.item(u);\n
//              if (href == svgedit.utilities.getHref(useElem)) {\n
//                var usexlate = svgroot.createSVGTransform();\n
//                usexlate.setTranslate(-tx,-ty);\n
//                svgedit.transformlist.getTransformList(useElem).insertItemBefore(usexlate,0);\n
//                batchCmd.addSubCommand( svgedit.recalculate.recalculateDimensions(useElem) );\n
//              }\n
//            }\n
          context_.setStartTransform(oldStartTransform);\n
        } // element\n
      } // for each child\n
      // Remove these transforms from group\n
      tlist.removeItem(N-1);\n
      tlist.removeItem(N-2);\n
      tlist.removeItem(N-3);\n
    } else if (N >= 3 && tlist.getItem(N-1).type == 1) {\n
      operation = 3; // scale\n
      m = svgedit.math.transformListToTransform(tlist).matrix;\n
      var e2t = svgroot.createSVGTransform();\n
      e2t.setMatrix(m);\n
      tlist.clear();\n
      tlist.appendItem(e2t);\n
    }     \n
    // next, check if the first transform was a translate \n
    // if we had [ T1 ] [ M ] we want to transform this into [ M ] [ T2 ]\n
    // therefore [ T2 ] = [ M_inv ] [ T1 ] [ M ]\n
    else if ( (N == 1 || (N > 1 && tlist.getItem(1).type != 3)) && \n
      tlist.getItem(0).type == 2) \n
    {\n
      operation = 2; // translate\n
      var T_M = svgedit.math.transformListToTransform(tlist).matrix;\n
      tlist.removeItem(0);\n
      var M_inv = svgedit.math.transformListToTransform(tlist).matrix.inverse();\n
      var M2 = svgedit.math.matrixMultiply( M_inv, T_M );\n
      \n
      tx = M2.e;\n
      ty = M2.f;\n
\n
      if (tx != 0 || ty != 0) {\n
        // we pass the translates down to the individual children\n
        var children = selected.childNodes;\n
        var c = children.length;\n
        \n
        var clipPaths_done = [];\n
        \n
        while (c--) {\n
          var child = children.item(c);\n
          if (child.nodeType == 1) {\n
          \n
            // Check if child has clip-path\n
            if (child.getAttribute(\'clip-path\')) {\n
              // tx, ty\n
              var attr = child.getAttribute(\'clip-path\');\n
              if (clipPaths_done.indexOf(attr) === -1) {\n
                svgedit.recalculate.updateClipPath(attr, tx, ty);\n
                clipPaths_done.push(attr);\n
              }             \n
            }\n
\n
            var oldStartTransform = context_.getStartTransform();\n
            context_.setStartTransform(child.getAttribute(\'transform\'));\n
            \n
            var childTlist = svgedit.transformlist.getTransformList(child);\n
            // some children might not have a transform (<metadata>, <defs>, etc)\n
            if (childTlist) {\n
              var newxlate = svgroot.createSVGTransform();\n
              newxlate.setTranslate(tx, ty);\n
              if (childTlist.numberOfItems) {\n
                childTlist.insertItemBefore(newxlate, 0);\n
              } else {\n
                childTlist.appendItem(newxlate);\n
              }\n
              batchCmd.addSubCommand(svgedit.recalculate.recalculateDimensions(child));\n
              // If any <use> have this group as a parent and are \n
              // referencing this child, then impose a reverse translate on it\n
              // so that when it won\'t get double-translated\n
              var uses = selected.getElementsByTagNameNS(NS.SVG, \'use\');\n
              var href = \'#\' + child.id;\n
              var u = uses.length;\n
              while (u--) {\n
                var useElem = uses.item(u);\n
                if (href == svgedit.utilities.getHref(useElem)) {\n
                  var usexlate = svgroot.createSVGTransform();\n
                  usexlate.setTranslate(-tx,-ty);\n
                  svgedit.transformlist.getTransformList(useElem).insertItemBefore(usexlate, 0);\n
                  batchCmd.addSubCommand( svgedit.recalculate.recalculateDimensions(useElem) );\n
                }\n
              }\n
              context_.setStartTransform(oldStartTransform);\n
            }\n
          }\n
        }\n
        \n
        clipPaths_done = [];\n
        context_.setStartTransform(oldStartTransform);\n
      }\n
    }\n
    // else, a matrix imposition from a parent group\n
    // keep pushing it down to the children\n
    else if (N == 1 && tlist.getItem(0).type == 1 && !gangle) {\n
      operation = 1;\n
      var m = tlist.getItem(0).matrix,\n
        children = selected.childNodes,\n
        c = children.length;\n
      while (c--) {\n
        var child = children.item(c);\n
        if (child.nodeType == 1) {\n
          var oldStartTransform = context_.getStartTransform();\n
          context_.setStartTransform(child.getAttribute(\'transform\'));\n
          var childTlist = svgedit.transformlist.getTransformList(child);\n
          \n
          if (!childTlist) {continue;}\n
          \n
          var em = svgedit.math.matrixMultiply(m, svgedit.math.transformListToTransform(childTlist).matrix);\n
          var e2m = svgroot.createSVGTransform();\n
          e2m.setMatrix(em);\n
          childTlist.clear();\n
          childTlist.appendItem(e2m, 0);\n
          \n
          batchCmd.addSubCommand( svgedit.recalculate.recalculateDimensions(child) );\n
          context_.setStartTransform(oldStartTransform);\n
          \n
          // Convert stroke\n
          // TODO: Find out if this should actually happen somewhere else\n
          var sw = child.getAttribute(\'stroke-width\');\n
          if (child.getAttribute(\'stroke\') !== \'none\' && !isNaN(sw)) {\n
            var avg = (Math.abs(em.a) + Math.abs(em.d)) / 2;\n
            child.setAttribute(\'stroke-width\', sw * avg);\n
          }\n
\n
        }\n
      }\n
      tlist.clear();\n
    }\n
    // else it was just a rotate\n
    else {\n
      if (gangle) {\n
        var newRot = svgroot.createSVGTransform();\n
        newRot.setRotate(gangle, newcenter.x, newcenter.y);\n
        if (tlist.numberOfItems) {\n
          tlist.insertItemBefore(newRot, 0);\n
        } else {\n
          tlist.appendItem(newRot);\n
        }\n
      }\n
      if (tlist.numberOfItems == 0) {\n
        selected.removeAttribute(\'transform\');\n
      }\n
      return null;      \n
    }\n
    \n
    // if it was a translate, put back the rotate at the new center\n
    if (operation == 2) {\n
      if (gangle) {\n
        newcenter = {\n
          x: oldcenter.x + first_m.e,\n
          y: oldcenter.y + first_m.f\n
        };\n
      \n
        var newRot = svgroot.createSVGTransform();\n
        newRot.setRotate(gangle, newcenter.x, newcenter.y);\n
        if (tlist.numberOfItems) {\n
          tlist.insertItemBefore(newRot, 0);\n
        } else {\n
          tlist.appendItem(newRot);\n
        }\n
      }\n
    }\n
    // if it was a resize\n
    else if (operation == 3) {\n
      var m = svgedit.math.transformListToTransform(tlist).matrix;\n
      var roldt = svgroot.createSVGTransform();\n
      roldt.setRotate(gangle, oldcenter.x, oldcenter.y);\n
      var rold = roldt.matrix;\n
      var rnew = svgroot.createSVGTransform();\n
      rnew.setRotate(gangle, newcenter.x, newcenter.y);\n
      var rnew_inv = rnew.matrix.inverse(),\n
        m_inv = m.inverse(),\n
        extrat = svgedit.math.matrixMultiply(m_inv, rnew_inv, rold, m);\n
\n
      tx = extrat.e;\n
      ty = extrat.f;\n
\n
      if (tx != 0 || ty != 0) {\n
        // now push this transform down to the children\n
        // we pass the translates down to the individual children\n
        var children = selected.childNodes;\n
        var c = children.length;\n
        while (c--) {\n
          var child = children.item(c);\n
          if (child.nodeType == 1) {\n
            var oldStartTransform = context_.getStartTransform();\n
            context_.setStartTransform(child.getAttribute(\'transform\'));\n
            var childTlist = svgedit.transformlist.getTransformList(child);\n
            var newxlate = svgroot.createSVGTransform();\n
            newxlate.setTranslate(tx, ty);\n
            if (childTlist.numberOfItems) {\n
              childTlist.insertItemBefore(newxlate, 0);\n
            } else {\n
              childTlist.appendItem(newxlate);\n
            }\n
\n
            batchCmd.addSubCommand( svgedit.recalculate.recalculateDimensions(child) );\n
            context_.setStartTransform(oldStartTransform);\n
          }\n
        }\n
      }\n
      \n
      if (gangle) {\n
        if (tlist.numberOfItems) {\n
          tlist.insertItemBefore(rnew, 0);\n
        } else {\n
          tlist.appendItem(rnew);\n
        }\n
      }\n
    }\n
  }\n
  // else, it\'s a non-group\n
  else {\n
\n
    // FIXME: box might be null for some elements (<metadata> etc), need to handle this\n
    var box = svgedit.utilities.getBBox(selected);\n
\n
    // Paths (and possbly other shapes) will have no BBox while still in <defs>,\n
    // but we still may need to recalculate them (see issue 595).\n
    // TODO: Figure out how to get BBox from these elements in case they\n
    // have a rotation transform\n
    \n
    if (!box && selected.tagName != \'path\') return null;\n
    \n
\n
    var m = svgroot.createSVGMatrix(),\n
      // temporarily strip off the rotate and save the old center\n
      angle = svgedit.utilities.getRotationAngle(selected);\n
    if (angle) {\n
      var oldcenter = {x: box.x+box.width/2, y: box.y+box.height/2},\n
      newcenter = svgedit.math.transformPoint(box.x+box.width/2, box.y+box.height/2,\n
              svgedit.math.transformListToTransform(tlist).matrix);\n
    \n
      var a = angle * Math.PI / 180;\n
      if ( Math.abs(a) > (1.0e-10) ) {\n
        var s = Math.sin(a)/(1 - Math.cos(a));\n
      } else {\n
        // FIXME: This blows up if the angle is exactly 0!\n
        var s = 2/a;\n
      }\n
      for (var i = 0; i < tlist.numberOfItems; ++i) {\n
        var xform = tlist.getItem(i);\n
        if (xform.type == 4) {\n
          // extract old center through mystical arts\n
          var rm = xform.matrix;\n
          oldcenter.y = (s*rm.e + rm.f)/2;\n
          oldcenter.x = (rm.e - s*rm.f)/2;\n
          tlist.removeItem(i);\n
          break;\n
        }\n
      }\n
    }\n
    \n
    // 2 = translate, 3 = scale, 4 = rotate, 1 = matrix imposition\n
    var operation = 0;\n
    var N = tlist.numberOfItems;\n
    \n
    // Check if it has a gradient with userSpaceOnUse, in which case\n
    // adjust it by recalculating the matrix transform.\n
    // TODO: Make this work in Webkit using svgedit.transformlist.SVGTransformList\n
    if (!svgedit.browser.isWebkit()) {\n
      var fill = selected.getAttribute(\'fill\');\n
      if (fill && fill.indexOf(\'url(\') === 0) {\n
        var paint = getRefElem(fill);\n
        var type = \'pattern\';\n
        if (paint.tagName !== type) type = \'gradient\';\n
        var attrVal = paint.getAttribute(type + \'Units\');\n
        if (attrVal === \'userSpaceOnUse\') {\n
          //Update the userSpaceOnUse element\n
          m = svgedit.math.transformListToTransform(tlist).matrix;\n
          var gtlist = svgedit.transformlist.getTransformList(paint);\n
          var gmatrix = svgedit.math.transformListToTransform(gtlist).matrix;\n
          m = svgedit.math.matrixMultiply(m, gmatrix);\n
          var m_str = \'matrix(\' + [m.a, m.b, m.c, m.d, m.e, m.f].join(\',\') + \')\';\n
          paint.setAttribute(type + \'Transform\', m_str);\n
        }\n
      }\n
    }\n
\n
    // first, if it was a scale of a non-skewed element, then the second-last  \n
    // transform will be the [S]\n
    // if we had [M][T][S][T] we want to extract the matrix equivalent of\n
    // [T][S][T] and push it down to the element\n
    if (N >= 3 && tlist.getItem(N-2).type == 3 && \n
      tlist.getItem(N-3).type == 2 && tlist.getItem(N-1).type == 2) \n
      \n
      // Removed this so a <use> with a given [T][S][T] would convert to a matrix. \n
      // Is that bad?\n
      //  && selected.nodeName != \'use\'\n
    {\n
      operation = 3; // scale\n
      m = svgedit.math.transformListToTransform(tlist, N-3, N-1).matrix;\n
      tlist.removeItem(N-1);\n
      tlist.removeItem(N-2);\n
      tlist.removeItem(N-3);\n
    } // if we had [T][S][-T][M], then this was a skewed element being resized\n
    // Thus, we simply combine it all into one matrix\n
    else if (N == 4 && tlist.getItem(N-1).type == 1) {\n
      operation = 3; // scale\n
      m = svgedit.math.transformListToTransform(tlist).matrix;\n
      var e2t = svgroot.createSVGTransform();\n
      e2t.setMatrix(m);\n
      tlist.clear();\n
      tlist.appendItem(e2t);\n
      // reset the matrix so that the element is not re-mapped\n
      m = svgroot.createSVGMatrix();\n
    } // if we had [R][T][S][-T][M], then this was a rotated matrix-element  \n
    // if we had [T1][M] we want to transform this into [M][T2]\n
    // therefore [ T2 ] = [ M_inv ] [ T1 ] [ M ] and we can push [T2] \n
    // down to the element\n
    else if ( (N == 1 || (N > 1 && tlist.getItem(1).type != 3)) && \n
      tlist.getItem(0).type == 2) \n
    {\n
      operation = 2; // translate\n
      var oldxlate = tlist.getItem(0).matrix,\n
        meq = svgedit.math.transformListToTransform(tlist,1).matrix,\n
        meq_inv = meq.inverse();\n
      m = svgedit.math.matrixMultiply( meq_inv, oldxlate, meq );\n
      tlist.removeItem(0);\n
    }\n
    // else if this child now has a matrix imposition (from a parent group)\n
    // we might be able to simplify\n
    else if (N == 1 && tlist.getItem(0).type == 1 && !angle) {\n
      // Remap all point-based elements\n
      m = svgedit.math.transformListToTransform(tlist).matrix;\n
      switch (selected.tagName) {\n
        case \'line\':\n
          changes = $(selected).attr([\'x1\', \'y1\', \'x2\', \'y2\']);\n
        case \'polyline\':\n
        case \'polygon\':\n
          changes.points = selected.getAttribute(\'points\');\n
          if (changes.points) {\n
            var list = selected.points;\n
            var len = list.numberOfItems;\n
            changes.points = new Array(len);\n
            for (var i = 0; i < len; ++i) {\n
              var pt = list.getItem(i);\n
              changes.points[i] = {x:pt.x, y:pt.y};\n
            }\n
          }\n
        case \'path\':\n
          changes.d = selected.getAttribute(\'d\');\n
          operation = 1;\n
          tlist.clear();\n
          break;\n
        default:\n
          break;\n
      }\n
    }\n
    // if it was a rotation, put the rotate back and return without a command\n
    // (this function has zero work to do for a rotate())\n
    else {\n
      operation = 4; // rotation\n
      if (angle) {\n
        var newRot = svgroot.createSVGTransform();\n
        newRot.setRotate(angle, newcenter.x, newcenter.y);\n
        \n
        if (tlist.numberOfItems) {\n
          tlist.insertItemBefore(newRot, 0);\n
        } else {\n
          tlist.appendItem(newRot);\n
        }\n
      }\n
      if (tlist.numberOfItems == 0) {\n
        selected.removeAttribute(\'transform\');\n
      }\n
      return null;\n
    }\n
    \n
    // if it was a translate or resize, we need to remap the element and absorb the xform\n
    if (operation == 1 || operation == 2 || operation == 3) {\n
      svgedit.coords.remapElement(selected, changes, m);\n
    } // if we are remapping\n
    \n
    // if it was a translate, put back the rotate at the new center\n
    if (operation == 2) {\n
      if (angle) {\n
        if (!svgedit.math.hasMatrixTransform(tlist)) {\n
          newcenter = {\n
            x: oldcenter.x + m.e,\n
            y: oldcenter.y + m.f\n
          };\n
        }\n
        var newRot = svgroot.createSVGTransform();\n
        newRot.setRotate(angle, newcenter.x, newcenter.y);\n
        if (tlist.numberOfItems) {\n
          tlist.insertItemBefore(newRot, 0);\n
        } else {\n
          tlist.appendItem(newRot);\n
        }\n
      }\n
      // We have special processing for tspans:  Tspans are not transformable\n
      // but they can have x,y coordinates (sigh).  Thus, if this was a translate,\n
      // on a text element, also translate any tspan children.\n
      if (selected.tagName == \'text\') {\n
        var children = selected.childNodes;\n
        var c = children.length;\n
        while (c--) {\n
          var child = children.item(c);\n
          if (child.tagName == \'tspan\') {\n
            var tspanChanges = {\n
              x: $(child).attr(\'x\') || 0,\n
              y: $(child).attr(\'y\') || 0\n
            };\n
            svgedit.coords.remapElement(child, tspanChanges, m);\n
          }\n
        }\n
      }\n
    }\n
    // [Rold][M][T][S][-T] became [Rold][M]\n
    // we want it to be [Rnew][M][Tr] where Tr is the\n
    // translation required to re-center it\n
    // Therefore, [Tr] = [M_inv][Rnew_inv][Rold][M]\n
    else if (operation == 3 && angle) {\n
      var m = svgedit.math.transformListToTransform(tlist).matrix;\n
      var roldt = svgroot.createSVGTransform();\n
      roldt.setRotate(angle, oldcenter.x, oldcenter.y);\n
      var rold = roldt.matrix;\n
      var rnew = svgroot.createSVGTransform();\n
      rnew.setRotate(angle, newcenter.x, newcenter.y);\n
      var rnew_inv = rnew.matrix.inverse();\n
      var m_inv = m.inverse();\n
      var extrat = svgedit.math.matrixMultiply(m_inv, rnew_inv, rold, m);\n
    \n
      svgedit.coords.remapElement(selected, changes, extrat);\n
      if (angle) {\n
        if (tlist.numberOfItems) {\n
          tlist.insertItemBefore(rnew, 0);\n
        } else {\n
          tlist.appendItem(rnew);\n
        }\n
      }\n
    }\n
  } // a non-group\n
\n
  // if the transform list has been emptied, remove it\n
  if (tlist.numberOfItems == 0) {\n
    selected.removeAttribute(\'transform\');\n
  }\n
\n
  batchCmd.addSubCommand(new svgedit.history.ChangeElementCommand(selected, initial));\n
\n
  return batchCmd;\n
};\n
})();\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>29154</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
