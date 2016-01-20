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
            <value> <string>ts52850941.32</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.svgicons.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

﻿/*\n
 * SVG Icon Loader 2.0\n
 *\n
 * jQuery Plugin for loading SVG icons from a single file\n
 *\n
 * Copyright (c) 2009 Alexis Deveria\n
 * http://a.deveria.com\n
 *\n
 * Apache 2 License\n
\n
How to use:\n
\n
1. Create the SVG master file that includes all icons:\n
\n
The master SVG icon-containing file is an SVG file that contains \n
<g> elements. Each <g> element should contain the markup of an SVG\n
icon. The <g> element has an ID that should \n
correspond with the ID of the HTML element used on the page that should contain \n
or optionally be replaced by the icon. Additionally, one empty element should be\n
added at the end with id "svg_eof".\n
\n
2. Optionally create fallback raster images for each SVG icon.\n
\n
3. Include the jQuery and the SVG Icon Loader scripts on your page.\n
\n
4. Run $.svgIcons() when the document is ready:\n
\n
$.svgIcons( file [string], options [object literal]);\n
\n
File is the location of a local SVG or SVGz file.\n
\n
All options are optional and can include:\n
\n
- \'w (number)\': The icon widths\n
\n
- \'h (number)\': The icon heights\n
\n
- \'fallback (object literal)\': List of raster images with each\n
  key being the SVG icon ID to replace, and the value the image file name.\n
  \n
- \'fallback_path (string)\': The path to use for all images\n
  listed under "fallback"\n
  \n
- \'replace (boolean)\': If set to true, HTML elements will be replaced by,\n
  rather than include the SVG icon.\n
\n
- \'placement (object literal)\': List with selectors for keys and SVG icon ids\n
  as values. This provides a custom method of adding icons.\n
\n
- \'resize (object literal)\': List with selectors for keys and numbers\n
  as values. This allows an easy way to resize specific icons.\n
  \n
- \'callback (function)\': A function to call when all icons have been loaded. \n
  Includes an object literal as its argument with as keys all icon IDs and the \n
  icon as a jQuery object as its value.\n
\n
- \'id_match (boolean)\': Automatically attempt to match SVG icon ids with\n
  corresponding HTML id (default: true)\n
  \n
- \'no_img (boolean)\': Prevent attempting to convert the icon into an <img>\n
  element (may be faster, help for browser consistency)\n
\n
- \'svgz (boolean)\': Indicate that the file is an SVGZ file, and thus not to\n
  parse as XML. SVGZ files add compression benefits, but getting data from\n
  them fails in Firefox 2 and older.\n
\n
5. To access an icon at a later point without using the callback, use this:\n
  $.getSvgIcon(id (string));\n
\n
This will return the icon (as jQuery object) with a given ID.\n
  \n
6. To resize icons at a later point without using the callback, use this:\n
  $.resizeSvgIcons(resizeOptions) (use the same way as the "resize" parameter)\n
\n
\n
Example usage #1:\n
\n
$(function() {\n
  $.svgIcons(\'my_icon_set.svg\'); // The SVG file that contains all icons\n
  // No options have been set, so all icons will automatically be inserted \n
  // into HTML elements that match the same IDs. \n
});\n
\n
Example usage #2:\n
\n
$(function() {\n
  $.svgIcons(\'my_icon_set.svg\', { // The SVG file that contains all icons\n
    callback: function(icons) { // Custom callback function that sets click\n
                  // events for each icon\n
      $.each(icons, function(id, icon) {\n
        icon.click(function() {\n
          alert(\'You clicked on the icon with id \' + id);\n
        });\n
      });\n
    }\n
  }); //The SVG file that contains all icons\n
});\n
\n
Example usage #3:\n
\n
$(function() {\n
  $.svgIcons(\'my_icon_set.svgz\', { // The SVGZ file that contains all icons\n
    w: 32,  // All icons will be 32px wide\n
    h: 32,  // All icons will be 32px high\n
    fallback_path: \'icons/\',  // All fallback files can be found here\n
    fallback: {\n
      \'#open_icon\': \'open.png\',  // The "open.png" will be appended to the\n
                     // HTML element with ID "open_icon"\n
      \'#close_icon\': \'close.png\',\n
      \'#save_icon\': \'save.png\'\n
    },\n
    placement: {\'.open_icon\',\'open\'}, // The "open" icon will be added\n
                      // to all elements with class "open_icon"\n
    resize: function() {\n
      \'#save_icon .svg_icon\': 64  // The "save" icon will be resized to 64 x 64px\n
    },\n
    \n
    callback: function(icons) { // Sets background color for "close" icon \n
      icons[\'close\'].css(\'background\',\'red\');\n
    },\n
    \n
    svgz: true // Indicates that an SVGZ file is being used\n
    \n
  })\n
});\n
\n
*/\n
\n
\n
(function($) {\n
  var svg_icons = {}, fixIDs;\n
\n
  $.svgIcons = function(file, opts) {\n
    var svgns = "http://www.w3.org/2000/svg",\n
      xlinkns = "http://www.w3.org/1999/xlink",\n
      icon_w = opts.w?opts.w : 24,\n
      icon_h = opts.h?opts.h : 24,\n
      elems, svgdoc, testImg,\n
      icons_made = false, data_loaded = false, load_attempts = 0,\n
      ua = navigator.userAgent, isOpera = !!window.opera, isSafari = (ua.indexOf(\'Safari/\') > -1 && ua.indexOf(\'Chrome/\')==-1),\n
      data_pre = \'data:image/svg+xml;charset=utf-8;base64,\';\n
      \n
      if(opts.svgz) {\n
        var data_el = $(\'<object data="\' + file + \'" type=image/svg+xml>\').appendTo(\'body\').hide();\n
        try {\n
          svgdoc = data_el[0].contentDocument;\n
          data_el.load(getIcons);\n
          getIcons(0, true); // Opera will not run "load" event if file is already cached\n
        } catch(err1) {\n
          useFallback();\n
        }\n
      } else {\n
        var parser = new DOMParser();\n
        $.ajax({\n
          url: file,\n
          dataType: \'string\',\n
          success: function(data) {\n
            if(!data) {\n
              $(useFallback);\n
              return;\n
            }\n
            svgdoc = parser.parseFromString(data, "text/xml");\n
            $(function() {\n
              getIcons(\'ajax\');\n
            });\n
          },\n
          error: function(err) {\n
            // TODO: Fix Opera widget icon bug\n
            if(window.opera) {\n
              $(function() {\n
                useFallback();\n
              });\n
            } else {\n
              if(err.responseText) {\n
                svgdoc = parser.parseFromString(err.responseText, "text/xml");\n
                if(!svgdoc.childNodes.length) {\n
                  $(useFallback);                 \n
                }\n
                $(function() {\n
                  getIcons(\'ajax\');\n
                });             \n
              } else {\n
                $(useFallback);\n
              }\n
            }\n
          }\n
        });\n
      }\n
      \n
    function getIcons(evt, no_wait) {\n
      if(evt !== \'ajax\') {\n
        if(data_loaded) return;\n
        // Webkit sometimes says svgdoc is undefined, other times\n
        // it fails to load all nodes. Thus we must make sure the "eof" \n
        // element is loaded.\n
        svgdoc = data_el[0].contentDocument; // Needed again for Webkit\n
        var isReady = (svgdoc && svgdoc.getElementById(\'svg_eof\'));\n
        if(!isReady && !(no_wait && isReady)) {\n
          load_attempts++;\n
          if(load_attempts < 50) {\n
            setTimeout(getIcons, 20);\n
          } else {\n
            useFallback();\n
            data_loaded = true;\n
          }\n
          return;\n
        }\n
        data_loaded = true;\n
      }\n
      \n
      elems = $(svgdoc.firstChild).children(); //.getElementsByTagName(\'foreignContent\');\n
      \n
      if(!opts.no_img) {\n
        var testSrc = data_pre + \'PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNzUiIGhlaWdodD0iMjc1Ij48L3N2Zz4%3D\';\n
        \n
        testImg = $(new Image()).attr({\n
          src: testSrc,\n
          width: 0,\n
          height: 0\n
        }).appendTo(\'body\')\n
        .load(function () {\n
          // Safari 4 crashes, Opera and Chrome don\'t\n
          makeIcons(true);\n
        }).error(function () {\n
          makeIcons();\n
        });\n
      } else {\n
        setTimeout(function() {\n
          if(!icons_made) makeIcons();\n
        },500);\n
      }\n
    }\n
    \n
    var setIcon = function(target, icon, id, setID) {\n
      if(isOpera) icon.css(\'visibility\',\'hidden\');\n
      if(opts.replace) {\n
        if(setID) icon.attr(\'id\',id);\n
        var cl = target.attr(\'class\');\n
        if(cl) icon.attr(\'class\',\'svg_icon \'+cl);\n
        target.replaceWith(icon);\n
      } else {\n
        \n
        target.append(icon);\n
      }\n
      if(isOpera) {\n
        setTimeout(function() {\n
          icon.removeAttr(\'style\');\n
        },1);\n
      }\n
    }\n
    \n
    var addIcon = function(icon, id) {\n
      if(opts.id_match === undefined || opts.id_match !== false) {\n
        setIcon(holder, icon, id, true);\n
      }\n
      svg_icons[id] = icon;\n
    }\n
    \n
    function makeIcons(toImage, fallback) {\n
      if(icons_made) return;\n
      if(opts.no_img) toImage = false;\n
      var holder;\n
      \n
      if(toImage) {\n
        var temp_holder = $(document.createElement(\'div\'));\n
        temp_holder.hide().appendTo(\'body\');\n
      } \n
      if(fallback) {\n
        var path = opts.fallback_path?opts.fallback_path:\'\';\n
        $.each(fallback, function(id, imgsrc) {\n
          holder = $(\'#\' + id);\n
          var icon = $(new Image())\n
            .attr({\n
              \'class\':\'svg_icon\',\n
              src: path + imgsrc,\n
              \'width\': icon_w,\n
              \'height\': icon_h,\n
              \'alt\': \'icon\'\n
            });\n
          \n
          addIcon(icon, id);\n
        });\n
      } else {\n
        var len = elems.length;\n
        for(var i = 0; i < len; i++) {\n
          var elem = elems[i];\n
          var id = elem.id;\n
          if(id === \'svg_eof\') break;\n
          holder = $(\'#\' + id);\n
          var svg = elem.getElementsByTagNameNS(svgns, \'svg\')[0];\n
          var svgroot = document.createElementNS(svgns, "svg");\n
          svgroot.setAttributeNS(svgns, \'viewBox\', [0,0,icon_w,icon_h].join(\' \'));\n
          // Make flexible by converting width/height to viewBox\n
          var w = svg.getAttribute(\'width\');\n
          var h = svg.getAttribute(\'height\');\n
          svg.removeAttribute(\'width\');\n
          svg.removeAttribute(\'height\');\n
          \n
          var vb = svg.getAttribute(\'viewBox\');\n
          if(!vb) {\n
            svg.setAttribute(\'viewBox\', [0,0,w,h].join(\' \'));\n
          }\n
          \n
          // Not using jQuery to be a bit faster\n
          svgroot.setAttribute(\'xmlns\', svgns);\n
          svgroot.setAttribute(\'width\', icon_w);\n
          svgroot.setAttribute(\'height\', icon_h);\n
          svgroot.setAttribute("xmlns:xlink", xlinkns);\n
          svgroot.setAttribute("class", \'svg_icon\');\n
\n
          // Without cloning, Firefox will make another GET request.\n
          // With cloning, causes issue in Opera/Win/Non-EN\n
          if(!isOpera) svg = svg.cloneNode(true);\n
          \n
          svgroot.appendChild(svg);\n
      \n
          if(toImage) {\n
            // Without cloning, Safari will crash\n
            // With cloning, causes issue in Opera/Win/Non-EN\n
            var svgcontent = isOpera?svgroot:svgroot.cloneNode(true);\n
            temp_holder.empty().append(svgroot);\n
            var str = data_pre + encode64(temp_holder.html());\n
            var icon = $(new Image())\n
              .attr({\'class\':\'svg_icon\', src:str});\n
          } else {\n
            var icon = fixIDs($(svgroot), i);\n
          }\n
          addIcon(icon, id);\n
        }\n
\n
      }\n
      \n
      if(opts.placement) {\n
        $.each(opts.placement, function(sel, id) {\n
          if(!svg_icons[id]) return;\n
          $(sel).each(function(i) {\n
            var copy = svg_icons[id].clone();\n
            if(i > 0 && !toImage) copy = fixIDs(copy, i, true);\n
            setIcon($(this), copy, id);\n
          })\n
        });\n
      }\n
      if(!fallback) {\n
        if(toImage) temp_holder.remove();\n
        if(data_el) data_el.remove();\n
        if(testImg) testImg.remove();\n
      }\n
      if(opts.resize) $.resizeSvgIcons(opts.resize);\n
      icons_made = true;\n
\n
      if(opts.callback) opts.callback(svg_icons);\n
    }\n
    \n
    fixIDs = function(svg_el, svg_num, force) {\n
      var defs = svg_el.find(\'defs\');\n
      if(!defs.length) return svg_el;\n
      \n
      if(isOpera) {\n
        var id_elems = defs.find(\'*\').filter(function() {\n
          return !!this.id;\n
        });\n
      } else {\n
        var id_elems = defs.find(\'[id]\');\n
      }\n
      \n
      var all_elems = svg_el[0].getElementsByTagName(\'*\'), len = all_elems.length;\n
      \n
      id_elems.each(function(i) {\n
        var id = this.id;\n
        var no_dupes = ($(svgdoc).find(\'#\' + id).length <= 1);\n
        if(isOpera) no_dupes = false; // Opera didn\'t clone svg_el, so not reliable\n
        // if(!force && no_dupes) return;\n
        var new_id = \'x\' + id + svg_num + i;\n
        this.id = new_id;\n
        \n
        var old_val = \'url(#\' + id + \')\';\n
        var new_val = \'url(#\' + new_id + \')\';\n
\n
        for(var i = 0; i < len; i++) {\n
          var elem = all_elems[i];\n
          if(elem.getAttribute(\'fill\') === old_val) {\n
            elem.setAttribute(\'fill\', new_val);\n
          }\n
          if(elem.getAttribute(\'stroke\') === old_val) {\n
            elem.setAttribute(\'stroke\', new_val);\n
          }\n
          if(elem.getAttribute(\'filter\') === old_val) {\n
            elem.setAttribute(\'filter\', new_val);\n
          }\n
        }\n
      });\n
      return svg_el;\n
    }\n
    \n
    function useFallback() {\n
      if(file.indexOf(\'.svgz\') != -1) {\n
        var reg_file = file.replace(\'.svgz\',\'.svg\');\n
        if(window.console) {\n
          console.log(\'.svgz failed, trying with .svg\');\n
        }\n
        $.svgIcons(reg_file, opts);\n
      } else if(opts.fallback) {\n
        makeIcons(false, opts.fallback);\n
      }\n
    }\n
        \n
    function encode64(input) {\n
      // base64 strings are 4/3 larger than the original string\n
      if(window.btoa) return window.btoa(input);\n
      var _keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";\n
      var output = new Array( Math.floor( (input.length + 2) / 3 ) * 4 );\n
      var chr1, chr2, chr3;\n
      var enc1, enc2, enc3, enc4;\n
      var i = 0, p = 0;\n
    \n
      do {\n
        chr1 = input.charCodeAt(i++);\n
        chr2 = input.charCodeAt(i++);\n
        chr3 = input.charCodeAt(i++);\n
    \n
        enc1 = chr1 >> 2;\n
        enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);\n
        enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);\n
        enc4 = chr3 & 63;\n
    \n
        if (isNaN(chr2)) {\n
          enc3 = enc4 = 64;\n
        } else if (isNaN(chr3)) {\n
          enc4 = 64;\n
        }\n
    \n
        output[p++] = _keyStr.charAt(enc1);\n
        output[p++] = _keyStr.charAt(enc2);\n
        output[p++] = _keyStr.charAt(enc3);\n
        output[p++] = _keyStr.charAt(enc4);\n
      } while (i < input.length);\n
    \n
      return output.join(\'\');\n
    }\n
  }\n
  \n
  $.getSvgIcon = function(id, uniqueClone) { \n
    var icon = svg_icons[id];\n
    if(uniqueClone && icon) {\n
      icon = fixIDs(icon, 0, true).clone(true);\n
    }\n
    return icon; \n
  }\n
  \n
  $.resizeSvgIcons = function(obj) {\n
    // FF2 and older don\'t detect .svg_icon, so we change it detect svg elems instead\n
    var change_sel = !$(\'.svg_icon:first\').length;\n
    $.each(obj, function(sel, size) {\n
      var arr = $.isArray(size);\n
      var w = arr?size[0]:size,\n
        h = arr?size[1]:size;\n
      if(change_sel) {\n
        sel = sel.replace(/\\.svg_icon/g,\'svg\');\n
      }\n
      $(sel).each(function() {\n
        this.setAttribute(\'width\', w);\n
        this.setAttribute(\'height\', h);\n
        if(window.opera && window.widget) {\n
          this.parentNode.style.width = w + \'px\';\n
          this.parentNode.style.height = h + \'px\';\n
        }\n
      });\n
    });\n
  }\n
  \n
})(jQuery);

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>15111</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
