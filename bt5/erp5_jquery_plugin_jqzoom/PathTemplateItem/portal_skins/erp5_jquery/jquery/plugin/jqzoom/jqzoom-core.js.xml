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
            <value> <string>ts58795626.09</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jqzoom-core.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*!\r\n
 * jQzoom Evolution Library v2.3  - Javascript Image magnifier\r\n
 * http://www.mind-projects.it\r\n
 *\r\n
 * Copyright 2011, Engineer Marco Renzi\r\n
 * Licensed under the BSD license.\r\n
 *\r\n
 * Redistribution and use in source and binary forms, with or without\r\n
 * modification, are permitted provided that the following conditions are met:\r\n
 *     * Redistributions of source code must retain the above copyright\r\n
 *       notice, this list of conditions and the following disclaimer.\r\n
 *     * Redistributions in binary form must reproduce the above copyright\r\n
 *       notice, this list of conditions and the following disclaimer in the\r\n
 *       documentation and/or other materials provided with the distribution.\r\n
 *     * Neither the name of the organization nor the\r\n
 *       names of its contributors may be used to endorse or promote products\r\n
 *       derived from this software without specific prior written permission.\r\n
 *\r\n
 * Date: 03 May 2011 22:16:00\r\n
 */\r\n
(function ($) {\r\n
    //GLOBAL VARIABLES\r\n
    var isIE6 = ($.browser.msie && $.browser.version < 7);\r\n
    var body = $(document.body);\r\n
    var window = $(window);\r\n
    var jqzoompluging_disabled = false; //disabilita globalmente il plugin\r\n
    $.fn.jqzoom = function (options) {\r\n
        return this.each(function () {\r\n
            var node = this.nodeName.toLowerCase();\r\n
            if (node == \'a\') {\r\n
                new jqzoom(this, options);\r\n
            }\r\n
        });\r\n
    };\r\n
    jqzoom = function (el, options) {\r\n
        var api = null;\r\n
        api = $(el).data("jqzoom");\r\n
        if (api) return api;\r\n
        var obj = this;\r\n
        var settings = $.extend({}, $.jqzoom.defaults, options || {});\r\n
        obj.el = el;\r\n
        el.rel = $(el).attr(\'rel\');\r\n
        //ANCHOR ELEMENT\r\n
        el.zoom_active = false;\r\n
        el.zoom_disabled = false; //to disable single zoom instance\r\n
        el.largeimageloading = false; //tell us if large image is loading\r\n
        el.largeimageloaded = false; //tell us if large image is loaded\r\n
        el.scale = {};\r\n
        el.timer = null;\r\n
        el.mousepos = {};\r\n
        el.mouseDown = false;\r\n
        $(el).css({\r\n
            \'outline-style\': \'none\',\r\n
            \'text-decoration\': \'none\'\r\n
        });\r\n
        //BASE IMAGE\r\n
        var img = $("img:eq(0)", el);\r\n
        el.title = $(el).attr(\'title\');\r\n
        el.imagetitle = img.attr(\'title\');\r\n
        var zoomtitle = ($.trim(el.title).length > 0) ? el.title : el.imagetitle;\r\n
        var smallimage = new Smallimage(img);\r\n
        var lens = new Lens();\r\n
        var stage = new Stage();\r\n
        var largeimage = new Largeimage();\r\n
        var loader = new Loader();\r\n
        //preventing default click,allowing the onclick event [exmple: lightbox]\r\n
        $(el).bind(\'click\', function (e) {\r\n
            e.preventDefault();\r\n
            return false;\r\n
        });\r\n
        //setting the default zoomType if not in settings\r\n
        var zoomtypes = [\'standard\', \'drag\', \'innerzoom\', \'reverse\'];\r\n
        if ($.inArray($.trim(settings.zoomType), zoomtypes) < 0) {\r\n
            settings.zoomType = \'standard\';\r\n
        }\r\n
        $.extend(obj, {\r\n
            create: function () { //create the main objects\r\n
                //create ZoomPad\r\n
                if ($(".zoomPad", el).length == 0) {\r\n
                    el.zoomPad = $(\'<div/>\').addClass(\'zoomPad\');\r\n
                    img.wrap(el.zoomPad);\r\n
                }\r\n
                if(settings.zoomType == \'innerzoom\'){\r\n
                    settings.zoomWidth  = smallimage.w;\r\n
                    settings.zoomHeight  =   smallimage.h;\r\n
                }\r\n
                //creating ZoomPup\r\n
                if ($(".zoomPup", el).length == 0) {\r\n
                    lens.append();\r\n
                }\r\n
                //creating zoomWindow\r\n
                if ($(".zoomWindow", el).length == 0) {\r\n
                    stage.append();\r\n
                }\r\n
                //creating Preload\r\n
                if ($(".zoomPreload", el).length == 0) {\r\n
                    loader.append();\r\n
                }\r\n
                //preloading images\r\n
                if (settings.preloadImages || settings.zoomType == \'drag\' || settings.alwaysOn) {\r\n
                    obj.load();\r\n
                }\r\n
                obj.init();\r\n
            },\r\n
            init: function () {\r\n
                //drag option\r\n
                if (settings.zoomType == \'drag\') {\r\n
                    $(".zoomPad", el).mousedown(function () {\r\n
                        el.mouseDown = true;\r\n
                    });\r\n
                    $(".zoomPad", el).mouseup(function () {\r\n
                        el.mouseDown = false;\r\n
                    });\r\n
                    document.body.ondragstart = function () {\r\n
                        return false;\r\n
                    };\r\n
                    $(".zoomPad", el).css({\r\n
                        cursor: \'default\'\r\n
                    });\r\n
                    $(".zoomPup", el).css({\r\n
                        cursor: \'move\'\r\n
                    });\r\n
                }\r\n
                if (settings.zoomType == \'innerzoom\') {\r\n
                    $(".zoomWrapper", el).css({\r\n
                        cursor: \'crosshair\'\r\n
                    });\r\n
                }\r\n
                $(".zoomPad", el).bind(\'mouseenter mouseover\', function (event) {\r\n
                    img.attr(\'title\', \'\');\r\n
                    $(el).attr(\'title\', \'\');\r\n
                    el.zoom_active = true;\r\n
                    //if loaded then activate else load large image\r\n
                    smallimage.fetchdata();\r\n
                    if (el.largeimageloaded) {\r\n
                        obj.activate(event);\r\n
                    } else {\r\n
                        obj.load();\r\n
                    }\r\n
                });\r\n
                $(".zoomPad", el).bind(\'mouseleave\', function (event) {\r\n
                    obj.deactivate();\r\n
                });\r\n
                $(".zoomPad", el).bind(\'mousemove\', function (e) {\r\n
\r\n
                    //prevent fast mouse mevements not to fire the mouseout event\r\n
                    if (e.pageX > smallimage.pos.r || e.pageX < smallimage.pos.l || e.pageY < smallimage.pos.t || e.pageY > smallimage.pos.b) {\r\n
                        lens.setcenter();\r\n
                        return false;\r\n
                    }\r\n
                    el.zoom_active = true;\r\n
                    if (el.largeimageloaded && !$(\'.zoomWindow\', el).is(\':visible\')) {\r\n
                        obj.activate(e);\r\n
                    }\r\n
                    if (el.largeimageloaded && (settings.zoomType != \'drag\' || (settings.zoomType == \'drag\' && el.mouseDown))) {\r\n
                        lens.setposition(e);\r\n
                    }\r\n
                });\r\n
                var thumb_preload = new Array();\r\n
                var i = 0;\r\n
                //binding click event on thumbnails\r\n
                var thumblist = new Array();\r\n
                thumblist = $(\'a\').filter(function () {\r\n
                    var regex = new RegExp("gallery[\\\\s]*:[\\\\s]*\'" + $.trim(el.rel) + "\'", "i");\r\n
                    var rel = $(this).attr(\'rel\');\r\n
                    if (regex.test(rel)) {\r\n
                        return this;\r\n
                    }\r\n
                });\r\n
                if (thumblist.length > 0) {\r\n
                    //getting the first to the last\r\n
                    var first = thumblist.splice(0, 1);\r\n
                    thumblist.push(first);\r\n
                }\r\n
                thumblist.each(function () {\r\n
                    //preloading thumbs\r\n
                    if (settings.preloadImages) {\r\n
                        var thumb_options = $.extend({}, eval("(" + $.trim($(this).attr(\'rel\')) + ")"));\r\n
                        thumb_preload[i] = new Image();\r\n
                        thumb_preload[i].src = thumb_options.largeimage;\r\n
                        i++;\r\n
                    }\r\n
                    $(this).click(function (e) {\r\n
                        if($(this).hasClass(\'zoomThumbActive\')){\r\n
                          return false;\r\n
                        }\r\n
                        thumblist.each(function () {\r\n
                            $(this).removeClass(\'zoomThumbActive\');\r\n
                        });\r\n
                        e.preventDefault();\r\n
                        obj.swapimage(this);\r\n
                        return false;\r\n
                    });\r\n
                });\r\n
            },\r\n
            load: function () {\r\n
                if (el.largeimageloaded == false && el.largeimageloading == false) {\r\n
                    var url = $(el).attr(\'href\');\r\n
                    el.largeimageloading = true;\r\n
                    largeimage.loadimage(url);\r\n
                }\r\n
            },\r\n
            activate: function (e) {\r\n
                clearTimeout(el.timer);\r\n
                //show lens and zoomWindow\r\n
                lens.show();\r\n
                stage.show();\r\n
            },\r\n
            deactivate: function (e) {\r\n
                switch (settings.zoomType) {\r\n
                case \'drag\':\r\n
                    //nothing or lens.setcenter();\r\n
                    break;\r\n
                default:\r\n
                    img.attr(\'title\', el.imagetitle);\r\n
                    $(el).attr(\'title\', el.title);\r\n
                    if (settings.alwaysOn) {\r\n
                        lens.setcenter();\r\n
                    } else {\r\n
                        stage.hide();\r\n
                        lens.hide();\r\n
                    }\r\n
                    break;\r\n
                }\r\n
                el.zoom_active = false;\r\n
            },\r\n
            swapimage: function (link) {\r\n
                el.largeimageloading = false;\r\n
                el.largeimageloaded = false;\r\n
                var options = new Object();\r\n
                options = $.extend({}, eval("(" + $.trim($(link).attr(\'rel\')) + ")"));\r\n
                if (options.smallimage && options.largeimage) {\r\n
                    var smallimage = options.smallimage;\r\n
                    var largeimage = options.largeimage;\r\n
                    $(link).addClass(\'zoomThumbActive\');\r\n
                    $(el).attr(\'href\', largeimage);\r\n
                    img.attr(\'src\', smallimage);\r\n
                    lens.hide();\r\n
                    stage.hide();\r\n
                    obj.load();\r\n
                } else {\r\n
                    alert(\'ERROR :: Missing parameter for largeimage or smallimage.\');\r\n
                    throw \'ERROR :: Missing parameter for largeimage or smallimage.\';\r\n
                }\r\n
                return false;\r\n
            }\r\n
        });\r\n
        //sometimes image is already loaded and onload will not fire\r\n
        if (img[0].complete) {\r\n
            //fetching data from sallimage if was previously loaded\r\n
            smallimage.fetchdata();\r\n
            if ($(".zoomPad", el).length == 0) obj.create();\r\n
        }\r\n
/*========================================================,\r\n
|   Smallimage\r\n
|---------------------------------------------------------:\r\n
|   Base image into the anchor element\r\n
`========================================================*/\r\n
\r\n
        function Smallimage(image) {\r\n
            var $obj = this;\r\n
            this.node = image[0];\r\n
            this.findborder = function () {\r\n
                var bordertop = 0;\r\n
                bordertop = image.css(\'border-top-width\');\r\n
                btop = \'\';\r\n
                var borderleft = 0;\r\n
                borderleft = image.css(\'border-left-width\');\r\n
                bleft = \'\';\r\n
                if (bordertop) {\r\n
                    for (i = 0; i < 3; i++) {\r\n
                        var x = [];\r\n
                        x = bordertop.substr(i, 1);\r\n
                        if (isNaN(x) == false) {\r\n
                            btop = btop + \'\' + bordertop.substr(i, 1);\r\n
                        } else {\r\n
                            break;\r\n
                        }\r\n
                    }\r\n
                }\r\n
                if (borderleft) {\r\n
                    for (i = 0; i < 3; i++) {\r\n
                        if (!isNaN(borderleft.substr(i, 1))) {\r\n
                            bleft = bleft + borderleft.substr(i, 1)\r\n
                        } else {\r\n
                            break;\r\n
                        }\r\n
                    }\r\n
                }\r\n
                $obj.btop = (btop.length > 0) ? eval(btop) : 0;\r\n
                $obj.bleft = (bleft.length > 0) ? eval(bleft) : 0;\r\n
            };\r\n
            this.fetchdata = function () {\r\n
                $obj.findborder();\r\n
                $obj.w = image.width();\r\n
                $obj.h = image.height();\r\n
                $obj.ow = image.outerWidth();\r\n
                $obj.oh = image.outerHeight();\r\n
                $obj.pos = image.offset();\r\n
                $obj.pos.l = image.offset().left + $obj.bleft;\r\n
                $obj.pos.t = image.offset().top + $obj.btop;\r\n
                $obj.pos.r = $obj.w + $obj.pos.l;\r\n
                $obj.pos.b = $obj.h + $obj.pos.t;\r\n
                $obj.rightlimit = image.offset().left + $obj.ow;\r\n
                $obj.bottomlimit = image.offset().top + $obj.oh;\r\n
                \r\n
            };\r\n
            this.node.onerror = function () {\r\n
                alert(\'Problems while loading image.\');\r\n
                throw \'Problems while loading image.\';\r\n
            };\r\n
            this.node.onload = function () {\r\n
                $obj.fetchdata();\r\n
                if ($(".zoomPad", el).length == 0) obj.create();\r\n
            };\r\n
            return $obj;\r\n
        };\r\n
/*========================================================,\r\n
|  Loader\r\n
|---------------------------------------------------------:\r\n
|  Show that the large image is loading\r\n
`========================================================*/\r\n
\r\n
        function Loader() {\r\n
            var $obj = this;\r\n
            this.append = function () {\r\n
                this.node = $(\'<div/>\').addClass(\'zoomPreload\').css(\'visibility\', \'hidden\').html(settings.preloadText);\r\n
                $(\'.zoomPad\', el).append(this.node);\r\n
            };\r\n
            this.show = function () {\r\n
                this.node.top = (smallimage.oh - this.node.height()) / 2;\r\n
                this.node.left = (smallimage.ow - this.node.width()) / 2;\r\n
                //setting position\r\n
                this.node.css({\r\n
                    top: this.node.top,\r\n
                    left: this.node.left,\r\n
                    position: \'absolute\',\r\n
                    visibility: \'visible\'\r\n
                });\r\n
            };\r\n
            this.hide = function () {\r\n
                this.node.css(\'visibility\', \'hidden\');\r\n
            };\r\n
            return this;\r\n
        }\r\n
/*========================================================,\r\n
|   Lens\r\n
|---------------------------------------------------------:\r\n
|   Lens over the image\r\n
`========================================================*/\r\n
\r\n
        function Lens() {\r\n
            var $obj = this;\r\n
            this.node = $(\'<div/>\').addClass(\'zoomPup\');\r\n
            //this.nodeimgwrapper = $("<div/>").addClass(\'zoomPupImgWrapper\');\r\n
            this.append = function () {\r\n
                $(\'.zoomPad\', el).append($(this.node).hide());\r\n
                if (settings.zoomType == \'reverse\') {\r\n
                    this.image = new Image();\r\n
                    this.image.src = smallimage.node.src; // fires off async\r\n
                    $(this.node).empty().append(this.image);\r\n
                }\r\n
            };\r\n
            this.setdimensions = function () {\r\n
                this.node.w = (parseInt((settings.zoomWidth) / el.scale.x) > smallimage.w ) ? smallimage.w : (parseInt(settings.zoomWidth / el.scale.x)); \r\n
                this.node.h = (parseInt((settings.zoomHeight) / el.scale.y) > smallimage.h ) ? smallimage.h : (parseInt(settings.zoomHeight / el.scale.y)); \r\n
                this.node.top = (smallimage.oh - this.node.h - 2) / 2;\r\n
                this.node.left = (smallimage.ow - this.node.w - 2) / 2;\r\n
                //centering lens\r\n
                this.node.css({\r\n
                    top: 0,\r\n
                    left: 0,\r\n
                    width: this.node.w + \'px\',\r\n
                    height: this.node.h + \'px\',\r\n
                    position: \'absolute\',\r\n
                    display: \'none\',\r\n
                    borderWidth: 1 + \'px\'\r\n
                });\r\n
\r\n
\r\n
\r\n
                if (settings.zoomType == \'reverse\') {\r\n
                    this.image.src = smallimage.node.src;\r\n
                    $(this.node).css({\r\n
                        \'opacity\': 1\r\n
                    });\r\n
\r\n
                    $(this.image).css({\r\n
                        position: \'absolute\',\r\n
                        display: \'block\',\r\n
                        left: -(this.node.left + 1 - smallimage.bleft) + \'px\',\r\n
                        top: -(this.node.top + 1 - smallimage.btop) + \'px\'\r\n
                    });\r\n
\r\n
                }\r\n
            };\r\n
            this.setcenter = function () {\r\n
                //calculating center position\r\n
                this.node.top = (smallimage.oh - this.node.h - 2) / 2;\r\n
                this.node.left = (smallimage.ow - this.node.w - 2) / 2;\r\n
                //centering lens\r\n
                this.node.css({\r\n
                    top: this.node.top,\r\n
                    left: this.node.left\r\n
                });\r\n
                if (settings.zoomType == \'reverse\') {\r\n
                    $(this.image).css({\r\n
                        position: \'absolute\',\r\n
                        display: \'block\',\r\n
                        left: -(this.node.left + 1 - smallimage.bleft) + \'px\',\r\n
                        top: -(this.node.top + 1 - smallimage.btop) + \'px\'\r\n
                    });\r\n
\r\n
                }\r\n
                //centering large image\r\n
                largeimage.setposition();\r\n
            };\r\n
            this.setposition = function (e) {\r\n
                el.mousepos.x = e.pageX;\r\n
                el.mousepos.y = e.pageY;\r\n
                var lensleft = 0;\r\n
                var lenstop = 0;\r\n
\r\n
                function overleft(lens) {\r\n
                    return el.mousepos.x - (lens.w) / 2 < smallimage.pos.l; \r\n
                }\r\n
\r\n
                function overright(lens) {\r\n
                    return el.mousepos.x + (lens.w) / 2 > smallimage.pos.r; \r\n
                   \r\n
                }\r\n
\r\n
                function overtop(lens) {\r\n
                    return el.mousepos.y - (lens.h) / 2 < smallimage.pos.t; \r\n
                }\r\n
\r\n
                function overbottom(lens) {\r\n
                    return el.mousepos.y + (lens.h) / 2 > smallimage.pos.b; \r\n
                }\r\n
                \r\n
                lensleft = el.mousepos.x + smallimage.bleft - smallimage.pos.l - (this.node.w + 2) / 2;\r\n
                lenstop = el.mousepos.y + smallimage.btop - smallimage.pos.t - (this.node.h + 2) / 2;\r\n
                if (overleft(this.node)) {\r\n
                    lensleft = smallimage.bleft - 1;\r\n
                } else if (overright(this.node)) {\r\n
                    lensleft = smallimage.w + smallimage.bleft - this.node.w - 1;\r\n
                }\r\n
                if (overtop(this.node)) {\r\n
                    lenstop = smallimage.btop - 1;\r\n
                } else if (overbottom(this.node)) {\r\n
                    lenstop = smallimage.h + smallimage.btop - this.node.h - 1;\r\n
                }\r\n
                \r\n
                this.node.left = lensleft;\r\n
                this.node.top = lenstop;\r\n
                this.node.css({\r\n
                    \'left\': lensleft + \'px\',\r\n
                    \'top\': lenstop + \'px\'\r\n
                });\r\n
                if (settings.zoomType == \'reverse\') {\r\n
                    if ($.browser.msie && $.browser.version > 7) {\r\n
                        $(this.node).empty().append(this.image);\r\n
                    }\r\n
\r\n
                    $(this.image).css({\r\n
                        position: \'absolute\',\r\n
                        display: \'block\',\r\n
                        left: -(this.node.left + 1 - smallimage.bleft) + \'px\',\r\n
                        top: -(this.node.top + 1 - smallimage.btop) + \'px\'\r\n
                    });\r\n
                }\r\n
               \r\n
                largeimage.setposition();\r\n
            };\r\n
            this.hide = function () {\r\n
                img.css({\r\n
                    \'opacity\': 1\r\n
                });\r\n
                this.node.hide();\r\n
            };\r\n
            this.show = function () {  \r\n
                \r\n
                if (settings.zoomType != \'innerzoom\' && (settings.lens || settings.zoomType == \'drag\')) {\r\n
                    this.node.show();\r\n
                }       \r\n
\r\n
                if (settings.zoomType == \'reverse\') {\r\n
                    img.css({\r\n
                        \'opacity\': settings.imageOpacity\r\n
                    });\r\n
                }\r\n
            };\r\n
            this.getoffset = function () {\r\n
                var o = {};\r\n
                o.left = $obj.node.left;\r\n
                o.top = $obj.node.top;\r\n
                return o;\r\n
            };\r\n
            return this;\r\n
        };\r\n
/*========================================================,\r\n
|   Stage\r\n
|---------------------------------------------------------:\r\n
|   Window area that contains the large image\r\n
`========================================================*/\r\n
\r\n
        function Stage() {\r\n
            var $obj = this;\r\n
            this.node = $("<div class=\'zoomWindow\'><div class=\'zoomWrapper\'><div class=\'zoomWrapperTitle\'></div><div class=\'zoomWrapperImage\'></div></div></div>");\r\n
            this.ieframe = $(\'<iframe class="zoomIframe" src="javascript:\\\'\\\';" marginwidth="0" marginheight="0" align="bottom" scrolling="no" frameborder="0" ></iframe>\');\r\n
            this.setposition = function () {\r\n
                this.node.leftpos = 0;\r\n
                this.node.toppos = 0;\r\n
                if (settings.zoomType != \'innerzoom\') {\r\n
                    //positioning\r\n
                    switch (settings.position) {\r\n
                    case "left":\r\n
                        this.node.leftpos = (smallimage.pos.l - smallimage.bleft - Math.abs(settings.xOffset) - settings.zoomWidth > 0) ? (0 - settings.zoomWidth - Math.abs(settings.xOffset)) : (smallimage.ow + Math.abs(settings.xOffset));\r\n
                        this.node.toppos = Math.abs(settings.yOffset);\r\n
                        break;\r\n
                    case "top":\r\n
                        this.node.leftpos = Math.abs(settings.xOffset);\r\n
                        this.node.toppos = (smallimage.pos.t - smallimage.btop - Math.abs(settings.yOffset) - settings.zoomHeight > 0) ? (0 - settings.zoomHeight - Math.abs(settings.yOffset)) : (smallimage.oh + Math.abs(settings.yOffset));\r\n
                        break;\r\n
                    case "bottom":\r\n
                        this.node.leftpos = Math.abs(settings.xOffset);\r\n
                        this.node.toppos = (smallimage.pos.t - smallimage.btop + smallimage.oh + Math.abs(settings.yOffset) + settings.zoomHeight < screen.height) ? (smallimage.oh + Math.abs(settings.yOffset)) : (0 - settings.zoomHeight - Math.abs(settings.yOffset));\r\n
                        break;\r\n
                    default:\r\n
                        this.node.leftpos = (smallimage.rightlimit + Math.abs(settings.xOffset) + settings.zoomWidth < screen.width) ? (smallimage.ow + Math.abs(settings.xOffset)) : (0 - settings.zoomWidth - Math.abs(settings.xOffset));\r\n
                        this.node.toppos = Math.abs(settings.yOffset);\r\n
                        break;\r\n
                    }\r\n
                }\r\n
                this.node.css({\r\n
                    \'left\': this.node.leftpos + \'px\',\r\n
                    \'top\': this.node.toppos + \'px\'\r\n
                });\r\n
                return this;\r\n
            };\r\n
            this.append = function () {\r\n
                $(\'.zoomPad\', el).append(this.node);\r\n
                this.node.css({\r\n
                    position: \'absolute\',\r\n
                    display: \'none\',\r\n
                    zIndex: 5001\r\n
                });\r\n
                if (settings.zoomType == \'innerzoom\') {\r\n
                    this.node.css({\r\n
                        cursor: \'default\'\r\n
                    });\r\n
                    var thickness = (smallimage.bleft == 0) ? 1 : smallimage.bleft;\r\n
                    $(\'.zoomWrapper\', this.node).css({\r\n
                        borderWidth: thickness + \'px\'\r\n
                    });    \r\n
                }\r\n
                \r\n
                  $(\'.zoomWrapper\', this.node).css({\r\n
                      width: Math.round(settings.zoomWidth) + \'px\' ,\r\n
                      borderWidth: thickness + \'px\'\r\n
                  });\r\n
                  $(\'.zoomWrapperImage\', this.node).css({\r\n
                      width: \'100%\',\r\n
                      height: Math.round(settings.zoomHeight) + \'px\'\r\n
                  });\r\n
                  //zoom title\r\n
                 $(\'.zoomWrapperTitle\', this.node).css({\r\n
                        width: \'100%\',\r\n
                        position: \'absolute\'\r\n
                  });  \r\n
              \r\n
                $(\'.zoomWrapperTitle\', this.node).hide();\r\n
                if (settings.title && zoomtitle.length > 0) {\r\n
                    $(\'.zoomWrapperTitle\', this.node).html(zoomtitle).show();\r\n
                }\r\n
                $obj.setposition();\r\n
            };\r\n
            this.hide = function () {\r\n
                switch (settings.hideEffect) {\r\n
                case \'fadeout\':\r\n
                    this.node.fadeOut(settings.fadeoutSpeed, function () {});\r\n
                    break;\r\n
                default:\r\n
                    this.node.hide();\r\n
                    break;\r\n
                }\r\n
                this.ieframe.hide();\r\n
            };\r\n
            this.show = function () {\r\n
                switch (settings.showEffect) {\r\n
                case \'fadein\':\r\n
                    this.node.fadeIn();\r\n
                    this.node.fadeIn(settings.fadeinSpeed, function () {});\r\n
                    break;\r\n
                default:\r\n
                    this.node.show();\r\n
                    break;\r\n
                }\r\n
                if (isIE6 && settings.zoomType != \'innerzoom\') {\r\n
                    this.ieframe.width = this.node.width();\r\n
                    this.ieframe.height = this.node.height();\r\n
                    this.ieframe.left = this.node.leftpos;\r\n
                    this.ieframe.top = this.node.toppos;\r\n
                    this.ieframe.css({\r\n
                        display: \'block\',\r\n
                        position: "absolute",\r\n
                        left: this.ieframe.left,\r\n
                        top: this.ieframe.top,\r\n
                        zIndex: 99,\r\n
                        width: this.ieframe.width + \'px\',\r\n
                        height: this.ieframe.height + \'px\'\r\n
                    });\r\n
                    $(\'.zoomPad\', el).append(this.ieframe);\r\n
                    this.ieframe.show();\r\n
                };\r\n
            };\r\n
        };\r\n
/*========================================================,\r\n
|   LargeImage\r\n
|---------------------------------------------------------:\r\n
|   The large detailed image\r\n
`========================================================*/\r\n
\r\n
        function Largeimage() {\r\n
            var $obj = this;\r\n
            this.node = new Image();\r\n
            this.loadimage = function (url) {\r\n
                //showing preload\r\n
                loader.show();\r\n
                this.url = url;\r\n
                this.node.style.position = \'absolute\';\r\n
                this.node.style.border = \'0px\';\r\n
                this.node.style.display = \'none\';\r\n
                this.node.style.left = \'-5000px\';\r\n
                this.node.style.top = \'0px\';\r\n
                document.body.appendChild(this.node);\r\n
                this.node.src = url; // fires off async\r\n
            };\r\n
            this.fetchdata = function () {\r\n
                var image = $(this.node);\r\n
                var scale = {};\r\n
                this.node.style.display = \'block\';\r\n
                $obj.w = image.width();\r\n
                $obj.h = image.height();\r\n
                $obj.pos = image.offset();\r\n
                $obj.pos.l = image.offset().left;\r\n
                $obj.pos.t = image.offset().top;\r\n
                $obj.pos.r = $obj.w + $obj.pos.l;\r\n
                $obj.pos.b = $obj.h + $obj.pos.t;\r\n
                scale.x = ($obj.w / smallimage.w);\r\n
                scale.y = ($obj.h / smallimage.h);\r\n
                el.scale = scale;\r\n
                document.body.removeChild(this.node);\r\n
                $(\'.zoomWrapperImage\', el).empty().append(this.node);\r\n
                //setting lens dimensions;\r\n
                lens.setdimensions();\r\n
            };\r\n
            this.node.onerror = function () {\r\n
                alert(\'Problems while loading the big image.\');\r\n
                throw \'Problems while loading the big image.\';\r\n
            };\r\n
            this.node.onload = function () {\r\n
                //fetching data\r\n
                $obj.fetchdata();\r\n
                loader.hide();\r\n
                el.largeimageloading = false;\r\n
                el.largeimageloaded = true;\r\n
                if (settings.zoomType == \'drag\' || settings.alwaysOn) {\r\n
                    lens.show();\r\n
                    stage.show();\r\n
                    lens.setcenter();\r\n
                }\r\n
            };\r\n
            this.setposition = function () {\r\n
                var left = -el.scale.x * (lens.getoffset().left - smallimage.bleft + 1);\r\n
                var top = -el.scale.y * (lens.getoffset().top - smallimage.btop + 1);\r\n
                $(this.node).css({\r\n
                    \'left\': left + \'px\',\r\n
                    \'top\': top + \'px\'\r\n
                });\r\n
            };\r\n
            return this;\r\n
        };\r\n
        $(el).data("jqzoom", obj);\r\n
    };\r\n
    //es. $.jqzoom.disable(\'#jqzoom1\');\r\n
    $.jqzoom = {\r\n
        defaults: {\r\n
            zoomType: \'standard\',\r\n
            //innerzoom/standard/reverse/drag\r\n
            zoomWidth: 300,\r\n
            //zoomWindow  default width\r\n
            zoomHeight: 300,\r\n
            //zoomWindow  default height\r\n
            xOffset: 10,\r\n
            //zoomWindow x offset, can be negative(more on the left) or positive(more on the right)\r\n
            yOffset: 0,\r\n
            //zoomWindow y offset, can be negative(more on the left) or positive(more on the right)\r\n
            position: "right",\r\n
            //zoomWindow default position\r\n
            preloadImages: true,\r\n
            //image preload\r\n
            preloadText: \'Loading zoom\',\r\n
            title: true,\r\n
            lens: true,\r\n
            imageOpacity: 0.4,\r\n
            alwaysOn: false,\r\n
            showEffect: \'show\',\r\n
            //show/fadein\r\n
            hideEffect: \'hide\',\r\n
            //hide/fadeout\r\n
            fadeinSpeed: \'slow\',\r\n
            //fast/slow/number\r\n
            fadeoutSpeed: \'2000\' //fast/slow/number\r\n
        },\r\n
        disable: function (el) {\r\n
            var api = $(el).data(\'jqzoom\');\r\n
            api.disable();\r\n
            return false;\r\n
        },\r\n
        enable: function (el) {\r\n
            var api = $(el).data(\'jqzoom\');\r\n
            api.enable();\r\n
            return false;\r\n
        },\r\n
        disableAll: function (el) {\r\n
            jqzoompluging_disabled = true;\r\n
        },\r\n
        enableAll: function (el) {\r\n
            jqzoompluging_disabled = false;\r\n
        }\r\n
    };\r\n
})(jQuery);

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>31322</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>jquery.jqzoom-core.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
