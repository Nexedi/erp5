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
            <value> <string>ts44314541.5</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>megapix-image.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/**\n
 * Mega pixel image rendering library for iOS6 Safari\n
 *\n
 * Fixes iOS6 Safari\'s image file rendering issue for large size image (over mega-pixel),\n
 * which causes unexpected subsampling when drawing it in canvas.\n
 * By using this library, you can safely render the image with proper stretching.\n
 *\n
 * Copyright (c) 2012 Shinichi Tomita <shinichi.tomita@gmail.com>\n
 * Released under the MIT license\n
 */\n
(function() {\n
\n
  /**\n
   * Detect subsampling in loaded image.\n
   * In iOS, larger images than 2M pixels may be subsampled in rendering.\n
   */\n
  function detectSubsampling(img) {\n
    var iw = img.naturalWidth, ih = img.naturalHeight;\n
    if (iw * ih > 1024 * 1024) { // subsampling may happen over megapixel image\n
      var canvas = document.createElement(\'canvas\');\n
      canvas.width = canvas.height = 1;\n
      var ctx = canvas.getContext(\'2d\');\n
      ctx.drawImage(img, -iw + 1, 0);\n
      // subsampled image becomes half smaller in rendering size.\n
      // check alpha channel value to confirm image is covering edge pixel or not.\n
      // if alpha value is 0 image is not covering, hence subsampled.\n
      return ctx.getImageData(0, 0, 1, 1).data[3] === 0;\n
    } else {\n
      return false;\n
    }\n
  }\n
\n
  /**\n
   * Detecting vertical squash in loaded image.\n
   * Fixes a bug which squash image vertically while drawing into canvas for some images.\n
   */\n
  function detectVerticalSquash(img, iw, ih) {\n
    var canvas = document.createElement(\'canvas\');\n
    canvas.width = 1;\n
    canvas.height = ih;\n
    var ctx = canvas.getContext(\'2d\');\n
    ctx.drawImage(img, 0, 0);\n
    var data = ctx.getImageData(0, 0, 1, ih).data;\n
    // search image edge pixel position in case it is squashed vertically.\n
    var sy = 0;\n
    var ey = ih;\n
    var py = ih;\n
    while (py > sy) {\n
      var alpha = data[(py - 1) * 4 + 3];\n
      if (alpha === 0) {\n
        ey = py;\n
      } else {\n
        sy = py;\n
      }\n
      py = (ey + sy) >> 1;\n
    }\n
    var ratio = (py / ih);\n
    return (ratio===0)?1:ratio;\n
  }\n
\n
  /**\n
   * Rendering image element (with resizing) and get its data URL\n
   */\n
  function renderImageToDataURL(img, options) {\n
    var canvas = document.createElement(\'canvas\');\n
    renderImageToCanvas(img, canvas, options);\n
    return canvas.toDataURL("image/jpeg", options.quality || 0.8);\n
  }\n
\n
  /**\n
   * Rendering image element (with resizing) into the canvas element\n
   */\n
  function renderImageToCanvas(img, canvas, options) {\n
    var iw = img.naturalWidth, ih = img.naturalHeight;\n
    var width = options.width, height = options.height;\n
    var ctx = canvas.getContext(\'2d\');\n
    ctx.save();\n
    transformCoordinate(canvas, width, height, options.orientation);\n
    var subsampled = detectSubsampling(img);\n
    if (subsampled) {\n
      iw /= 2;\n
      ih /= 2;\n
    }\n
    var d = 1024; // size of tiling canvas\n
    var tmpCanvas = document.createElement(\'canvas\');\n
    tmpCanvas.width = tmpCanvas.height = d;\n
    var tmpCtx = tmpCanvas.getContext(\'2d\');\n
    var vertSquashRatio = detectVerticalSquash(img, iw, ih);\n
    var sy = 0;\n
    while (sy < ih) {\n
      var sh = sy + d > ih ? ih - sy : d;\n
      var sx = 0;\n
      while (sx < iw) {\n
        var sw = sx + d > iw ? iw - sx : d;\n
        tmpCtx.clearRect(0, 0, d, d);\n
        tmpCtx.drawImage(img, -sx, -sy);\n
        var dx = (sx * width / iw) << 0;\n
        var dw = Math.ceil(sw * width / iw);\n
        var dy = (sy * height / ih / vertSquashRatio) << 0;\n
        var dh = Math.ceil(sh * height / ih / vertSquashRatio);\n
        ctx.drawImage(tmpCanvas, 0, 0, sw, sh, dx, dy, dw, dh);\n
        sx += d;\n
      }\n
      sy += d;\n
    }\n
    ctx.restore();\n
    tmpCanvas = tmpCtx = null;\n
  }\n
\n
  /**\n
   * Transform canvas coordination according to specified frame size and orientation\n
   * Orientation value is from EXIF tag\n
   */\n
  function transformCoordinate(canvas, width, height, orientation) {\n
    switch (orientation) {\n
      case 5:\n
      case 6:\n
      case 7:\n
      case 8:\n
        canvas.width = height;\n
        canvas.height = width;\n
        break;\n
      default:\n
        canvas.width = width;\n
        canvas.height = height;\n
    }\n
    var ctx = canvas.getContext(\'2d\');\n
    switch (orientation) {\n
      case 2:\n
        // horizontal flip\n
        ctx.translate(width, 0);\n
        ctx.scale(-1, 1);\n
        break;\n
      case 3:\n
        // 180 rotate left\n
        ctx.translate(width, height);\n
        ctx.rotate(Math.PI);\n
        break;\n
      case 4:\n
        // vertical flip\n
        ctx.translate(0, height);\n
        ctx.scale(1, -1);\n
        break;\n
      case 5:\n
        // vertical flip + 90 rotate right\n
        ctx.rotate(0.5 * Math.PI);\n
        ctx.scale(1, -1);\n
        break;\n
      case 6:\n
        // 90 rotate right\n
        ctx.rotate(0.5 * Math.PI);\n
        ctx.translate(0, -height);\n
        break;\n
      case 7:\n
        // horizontal flip + 90 rotate right\n
        ctx.rotate(0.5 * Math.PI);\n
        ctx.translate(width, -height);\n
        ctx.scale(-1, 1);\n
        break;\n
      case 8:\n
        // 90 rotate left\n
        ctx.rotate(-0.5 * Math.PI);\n
        ctx.translate(-width, 0);\n
        break;\n
      default:\n
        break;\n
    }\n
  }\n
\n
\n
  /**\n
   * MegaPixImage class\n
   */\n
  function MegaPixImage(srcImage) {\n
    if (srcImage instanceof Blob) {\n
      var img = new Image();\n
      var URL = window.URL && window.URL.createObjectURL ? window.URL :\n
                window.webkitURL && window.webkitURL.createObjectURL ? window.webkitURL :\n
                null;\n
      if (!URL) { throw Error("No createObjectURL function found to create blob url"); }\n
      img.src = URL.createObjectURL(srcImage);\n
      srcImage = img;\n
    }\n
    if (!srcImage.naturalWidth && !srcImage.naturalHeight) {\n
      var _this = this;\n
      srcImage.onload = function() {\n
        var listeners = _this.imageLoadListeners;\n
        if (listeners) {\n
          _this.imageLoadListeners = null;\n
          for (var i=0, len=listeners.length; i<len; i++) {\n
            listeners[i]();\n
          }\n
        }\n
      };\n
      this.imageLoadListeners = [];\n
    }\n
    this.srcImage = srcImage;\n
  }\n
\n
  /**\n
   * Rendering megapix image into specified target element\n
   */\n
  MegaPixImage.prototype.render = function(target, options) {\n
    if (this.imageLoadListeners) {\n
      var _this = this;\n
      this.imageLoadListeners.push(function() { _this.render(target, options) });\n
      return;\n
    }\n
    options = options || {};\n
    var imgWidth = this.srcImage.naturalWidth, imgHeight = this.srcImage.naturalHeight,\n
        width = options.width, height = options.height,\n
        maxWidth = options.maxWidth, maxHeight = options.maxHeight;\n
    if (width && !height) {\n
      height = (imgHeight * width / imgWidth) << 0;\n
    } else if (height && !width) {\n
      width = (imgWidth * height / imgHeight) << 0;\n
    } else {\n
      width = imgWidth;\n
      height = imgHeight;\n
    }\n
    if (maxWidth && width > maxWidth) {\n
      width = maxWidth;\n
      height = (imgHeight * width / imgWidth) << 0;\n
    }\n
    if (maxHeight && height > maxHeight) {\n
      height = maxHeight;\n
      width = (imgWidth * height / imgHeight) << 0;\n
    }\n
    var opt = { width : width, height : height };\n
    for (var k in options) opt[k] = options[k];\n
\n
    var tagName = target.tagName.toLowerCase();\n
    if (tagName === \'img\') {\n
      target.src = renderImageToDataURL(this.srcImage, opt);\n
    } else if (tagName === \'canvas\') {\n
      renderImageToCanvas(this.srcImage, target, opt);\n
    }\n
    if (typeof this.onrender === \'function\') {\n
      this.onrender(target);\n
    }\n
  };\n
\n
  MegaPixImage.prototype.getUrl = function() {\n
    return renderImageToDataURL(this.srcImage, {});\n
  };\n
\n
  /**\n
   * Export class to global\n
   */\n
  if (typeof define === \'function\' && define.amd) {\n
    define([], function() { return MegaPixImage; }); // for AMD loader\n
  } else {\n
    this.MegaPixImage = MegaPixImage;\n
  }\n
\n
})();\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>7791</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
