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
            <value> <string>ts58795772.1</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>lightbox-0.5.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/**\r\n
 * jQuery lightBox plugin\r\n
 * This jQuery plugin was inspired and based on Lightbox 2 by Lokesh Dhakar (http://www.huddletogether.com/projects/lightbox2/)\r\n
 * and adapted to me for use like a plugin from jQuery.\r\n
 * @name jquery-lightbox-0.5.js\r\n
 * @author Leandro Vieira Pinho - http://leandrovieira.com\r\n
 * @version 0.5\r\n
 * @date April 11, 2008\r\n
 * @category jQuery plugin\r\n
 * @copyright (c) 2008 Leandro Vieira Pinho (leandrovieira.com)\r\n
 * @license CCAttribution-ShareAlike 2.5 Brazil - http://creativecommons.org/licenses/by-sa/2.5/br/deed.en_US\r\n
 * @example Visit http://leandrovieira.com/projects/jquery/lightbox/ for more informations about this jQuery plugin\r\n
 */\r\n
\r\n
// Offering a Custom Alias suport - More info: http://docs.jquery.com/Plugins/Authoring#Custom_Alias\r\n
(function($) {\r\n
\t/**\r\n
\t * $ is an alias to jQuery object\r\n
\t *\r\n
\t */\r\n
\t$.fn.lightBox = function(settings) {\r\n
\t\t// Settings to configure the jQuery lightBox plugin how you like\r\n
\t\tsettings = jQuery.extend({\r\n
\t\t\t// Configuration related to overlay\r\n
\t\t\toverlayBgColor: \t\t\'#000\',\t\t// (string) Background color to overlay; inform a hexadecimal value like: #RRGGBB. Where RR, GG, and BB are the hexadecimal values for the red, green, and blue values of the color.\r\n
\t\t\toverlayOpacity:\t\t\t0.8,\t\t// (integer) Opacity value to overlay; inform: 0.X. Where X are number from 0 to 9\r\n
\t\t\t// Configuration related to navigation\r\n
\t\t\tfixedNavigation:\t\tfalse,\t\t// (boolean) Boolean that informs if the navigation (next and prev button) will be fixed or not in the interface.\r\n
\t\t\t// Configuration related to images\r\n
\t\t\timageLoading:\t\t\t\'images/lightbox-ico-loading.gif\',\t\t// (string) Path and the name of the loading icon\r\n
\t\t\timageBtnPrev:\t\t\t\'images/lightbox-btn-prev.gif\',\t\t\t// (string) Path and the name of the prev button image\r\n
\t\t\timageBtnNext:\t\t\t\'images/lightbox-btn-next.gif\',\t\t\t// (string) Path and the name of the next button image\r\n
\t\t\timageBtnClose:\t\t\t\'images/lightbox-btn-close.gif\',\t\t// (string) Path and the name of the close btn\r\n
\t\t\timageBlank:\t\t\t\t\'images/lightbox-blank.gif\',\t\t\t// (string) Path and the name of a blank image (one pixel)\r\n
\t\t\t// Configuration related to container image box\r\n
\t\t\tcontainerBorderSize:\t10,\t\t\t// (integer) If you adjust the padding in the CSS for the container, #lightbox-container-image-box, you will need to update this value\r\n
\t\t\tcontainerResizeSpeed:\t400,\t\t// (integer) Specify the resize duration of container image. These number are miliseconds. 400 is default.\r\n
\t\t\t// Configuration related to texts in caption. For example: Image 2 of 8. You can alter either "Image" and "of" texts.\r\n
\t\t\ttxtImage:\t\t\t\t\'Image\',\t// (string) Specify text "Image"\r\n
\t\t\ttxtOf:\t\t\t\t\t\'of\',\t\t// (string) Specify text "of"\r\n
\t\t\t// Configuration related to keyboard navigation\r\n
\t\t\tkeyToClose:\t\t\t\t\'c\',\t\t// (string) (c = close) Letter to close the jQuery lightBox interface. Beyond this letter, the letter X and the SCAPE key is used to.\r\n
\t\t\tkeyToPrev:\t\t\t\t\'p\',\t\t// (string) (p = previous) Letter to show the previous image\r\n
\t\t\tkeyToNext:\t\t\t\t\'n\',\t\t// (string) (n = next) Letter to show the next image.\r\n
\t\t\t// Don\xb4t alter these variables in any way\r\n
\t\t\timageArray:\t\t\t\t[],\r\n
\t\t\tactiveImage:\t\t\t0\r\n
\t\t},settings);\r\n
\t\t// Caching the jQuery object with all elements matched\r\n
\t\tvar jQueryMatchedObj = this; // This, in this context, refer to jQuery object\r\n
\t\t/**\r\n
\t\t * Initializing the plugin calling the start function\r\n
\t\t *\r\n
\t\t * @return boolean false\r\n
\t\t */\r\n
\t\tfunction _initialize() {\r\n
\t\t\t_start(this,jQueryMatchedObj); // This, in this context, refer to object (link) which the user have clicked\r\n
\t\t\treturn false; // Avoid the browser following the link\r\n
\t\t}\r\n
\t\t/**\r\n
\t\t * Start the jQuery lightBox plugin\r\n
\t\t *\r\n
\t\t * @param object objClicked The object (link) whick the user have clicked\r\n
\t\t * @param object jQueryMatchedObj The jQuery object with all elements matched\r\n
\t\t */\r\n
\t\tfunction _start(objClicked,jQueryMatchedObj) {\r\n
\t\t\t// Hime some elements to avoid conflict with overlay in IE. These elements appear above the overlay.\r\n
\t\t\t$(\'embed, object, select\').css({ \'visibility\' : \'hidden\' });\r\n
\t\t\t// Call the function to create the markup structure; style some elements; assign events in some elements.\r\n
\t\t\t_set_interface();\r\n
\t\t\t// Unset total images in imageArray\r\n
\t\t\tsettings.imageArray.length = 0;\r\n
\t\t\t// Unset image active information\r\n
\t\t\tsettings.activeImage = 0;\r\n
\t\t\t// We have an image set? Or just an image? Let\xb4s see it.\r\n
\t\t\tif ( jQueryMatchedObj.length == 1 ) {\r\n
\t\t\t\tsettings.imageArray.push(new Array(objClicked.getAttribute(\'href\'),objClicked.getAttribute(\'title\')));\r\n
\t\t\t} else {\r\n
\t\t\t\t// Add an Array (as many as we have), with href and title atributes, inside the Array that storage the images references\t\t\r\n
\t\t\t\tfor ( var i = 0; i < jQueryMatchedObj.length; i++ ) {\r\n
\t\t\t\t\tsettings.imageArray.push(new Array(jQueryMatchedObj[i].getAttribute(\'href\'),jQueryMatchedObj[i].getAttribute(\'title\')));\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\twhile ( settings.imageArray[settings.activeImage][0] != objClicked.getAttribute(\'href\') ) {\r\n
\t\t\t\tsettings.activeImage++;\r\n
\t\t\t}\r\n
\t\t\t// Call the function that prepares image exibition\r\n
\t\t\t_set_image_to_view();\r\n
\t\t}\r\n
\t\t/**\r\n
\t\t * Create the jQuery lightBox plugin interface\r\n
\t\t *\r\n
\t\t * The HTML markup will be like that:\r\n
\t\t\t<div id="jquery-overlay"></div>\r\n
\t\t\t<div id="jquery-lightbox">\r\n
\t\t\t\t<div id="lightbox-container-image-box">\r\n
\t\t\t\t\t<div id="lightbox-container-image">\r\n
\t\t\t\t\t\t<img src="../fotos/XX.jpg" id="lightbox-image">\r\n
\t\t\t\t\t\t<div id="lightbox-nav">\r\n
\t\t\t\t\t\t\t<a href="#" id="lightbox-nav-btnPrev"></a>\r\n
\t\t\t\t\t\t\t<a href="#" id="lightbox-nav-btnNext"></a>\r\n
\t\t\t\t\t\t</div>\r\n
\t\t\t\t\t\t<div id="lightbox-loading">\r\n
\t\t\t\t\t\t\t<a href="#" id="lightbox-loading-link">\r\n
\t\t\t\t\t\t\t\t<img src="../images/lightbox-ico-loading.gif">\r\n
\t\t\t\t\t\t\t</a>\r\n
\t\t\t\t\t\t</div>\r\n
\t\t\t\t\t</div>\r\n
\t\t\t\t</div>\r\n
\t\t\t\t<div id="lightbox-container-image-data-box">\r\n
\t\t\t\t\t<div id="lightbox-container-image-data">\r\n
\t\t\t\t\t\t<div id="lightbox-image-details">\r\n
\t\t\t\t\t\t\t<span id="lightbox-image-details-caption"></span>\r\n
\t\t\t\t\t\t\t<span id="lightbox-image-details-currentNumber"></span>\r\n
\t\t\t\t\t\t</div>\r\n
\t\t\t\t\t\t<div id="lightbox-secNav">\r\n
\t\t\t\t\t\t\t<a href="#" id="lightbox-secNav-btnClose">\r\n
\t\t\t\t\t\t\t\t<img src="../images/lightbox-btn-close.gif">\r\n
\t\t\t\t\t\t\t</a>\r\n
\t\t\t\t\t\t</div>\r\n
\t\t\t\t\t</div>\r\n
\t\t\t\t</div>\r\n
\t\t\t</div>\r\n
\t\t *\r\n
\t\t */\r\n
\t\tfunction _set_interface() {\r\n
\t\t\t// Apply the HTML markup into body tag\r\n
\t\t\t$(\'body\').append(\'<div id="jquery-overlay"></div><div id="jquery-lightbox"><div id="lightbox-container-image-box"><div id="lightbox-container-image"><img id="lightbox-image"><div style="" id="lightbox-nav"><a href="#" id="lightbox-nav-btnPrev"></a><a href="#" id="lightbox-nav-btnNext"></a></div><div id="lightbox-loading"><a href="#" id="lightbox-loading-link"><img src="\' + settings.imageLoading + \'"></a></div></div></div><div id="lightbox-container-image-data-box"><div id="lightbox-container-image-data"><div id="lightbox-image-details"><span id="lightbox-image-details-caption"></span><span id="lightbox-image-details-currentNumber"></span></div><div id="lightbox-secNav"><a href="#" id="lightbox-secNav-btnClose"><img src="\' + settings.imageBtnClose + \'"></a></div></div></div></div>\');\t\r\n
\t\t\t// Get page sizes\r\n
\t\t\tvar arrPageSizes = ___getPageSize();\r\n
\t\t\t// Style overlay and show it\r\n
\t\t\t$(\'#jquery-overlay\').css({\r\n
\t\t\t\tbackgroundColor:\tsettings.overlayBgColor,\r\n
\t\t\t\topacity:\t\t\tsettings.overlayOpacity,\r\n
\t\t\t\twidth:\t\t\t\tarrPageSizes[0],\r\n
\t\t\t\theight:\t\t\t\tarrPageSizes[1]\r\n
\t\t\t}).fadeIn();\r\n
\t\t\t// Get page scroll\r\n
\t\t\tvar arrPageScroll = ___getPageScroll();\r\n
\t\t\t// Calculate top and left offset for the jquery-lightbox div object and show it\r\n
\t\t\t$(\'#jquery-lightbox\').css({\r\n
\t\t\t\ttop:\tarrPageScroll[1] + (arrPageSizes[3] / 10),\r\n
\t\t\t\tleft:\tarrPageScroll[0]\r\n
\t\t\t}).show();\r\n
\t\t\t// Assigning click events in elements to close overlay\r\n
\t\t\t$(\'#jquery-overlay,#jquery-lightbox\').click(function() {\r\n
\t\t\t\t_finish();\t\t\t\t\t\t\t\t\t\r\n
\t\t\t});\r\n
\t\t\t// Assign the _finish function to lightbox-loading-link and lightbox-secNav-btnClose objects\r\n
\t\t\t$(\'#lightbox-loading-link,#lightbox-secNav-btnClose\').click(function() {\r\n
\t\t\t\t_finish();\r\n
\t\t\t\treturn false;\r\n
\t\t\t});\r\n
\t\t\t// If window was resized, calculate the new overlay dimensions\r\n
\t\t\t$(window).resize(function() {\r\n
\t\t\t\t// Get page sizes\r\n
\t\t\t\tvar arrPageSizes = ___getPageSize();\r\n
\t\t\t\t// Style overlay and show it\r\n
\t\t\t\t$(\'#jquery-overlay\').css({\r\n
\t\t\t\t\twidth:\t\tarrPageSizes[0],\r\n
\t\t\t\t\theight:\t\tarrPageSizes[1]\r\n
\t\t\t\t});\r\n
\t\t\t\t// Get page scroll\r\n
\t\t\t\tvar arrPageScroll = ___getPageScroll();\r\n
\t\t\t\t// Calculate top and left offset for the jquery-lightbox div object and show it\r\n
\t\t\t\t$(\'#jquery-lightbox\').css({\r\n
\t\t\t\t\ttop:\tarrPageScroll[1] + (arrPageSizes[3] / 10),\r\n
\t\t\t\t\tleft:\tarrPageScroll[0]\r\n
\t\t\t\t});\r\n
\t\t\t});\r\n
\t\t}\r\n
\t\t/**\r\n
\t\t * Prepares image exibition; doing a image\xb4s preloader to calculate it\xb4s size\r\n
\t\t *\r\n
\t\t */\r\n
\t\tfunction _set_image_to_view() { // show the loading\r\n
\t\t\t// Show the loading\r\n
\t\t\t$(\'#lightbox-loading\').show();\r\n
\t\t\tif ( settings.fixedNavigation ) {\r\n
\t\t\t\t$(\'#lightbox-image,#lightbox-container-image-data-box,#lightbox-image-details-currentNumber\').hide();\r\n
\t\t\t} else {\r\n
\t\t\t\t// Hide some elements\r\n
\t\t\t\t$(\'#lightbox-image,#lightbox-nav,#lightbox-nav-btnPrev,#lightbox-nav-btnNext,#lightbox-container-image-data-box,#lightbox-image-details-currentNumber\').hide();\r\n
\t\t\t}\r\n
\t\t\t// Image preload process\r\n
\t\t\tvar objImagePreloader = new Image();\r\n
\t\t\tobjImagePreloader.onload = function() {\r\n
\t\t\t\t$(\'#lightbox-image\').attr(\'src\',settings.imageArray[settings.activeImage][0]);\r\n
\t\t\t\t// Perfomance an effect in the image container resizing it\r\n
\t\t\t\t_resize_container_image_box(objImagePreloader.width,objImagePreloader.height);\r\n
\t\t\t\t//\tclear onLoad, IE behaves irratically with animated gifs otherwise\r\n
\t\t\t\tobjImagePreloader.onload=function(){};\r\n
\t\t\t};\r\n
\t\t\tobjImagePreloader.src = settings.imageArray[settings.activeImage][0];\r\n
\t\t};\r\n
\t\t/**\r\n
\t\t * Perfomance an effect in the image container resizing it\r\n
\t\t *\r\n
\t\t * @param integer intImageWidth The image\xb4s width that will be showed\r\n
\t\t * @param integer intImageHeight The image\xb4s height that will be showed\r\n
\t\t */\r\n
\t\tfunction _resize_container_image_box(intImageWidth,intImageHeight) {\r\n
\t\t\t// Get current width and height\r\n
\t\t\tvar intCurrentWidth = $(\'#lightbox-container-image-box\').width();\r\n
\t\t\tvar intCurrentHeight = $(\'#lightbox-container-image-box\').height();\r\n
\t\t\t// Get the width and height of the selected image plus the padding\r\n
\t\t\tvar intWidth = (intImageWidth + (settings.containerBorderSize * 2)); // Plus the image\xb4s width and the left and right padding value\r\n
\t\t\tvar intHeight = (intImageHeight + (settings.containerBorderSize * 2)); // Plus the image\xb4s height and the left and right padding value\r\n
\t\t\t// Diferences\r\n
\t\t\tvar intDiffW = intCurrentWidth - intWidth;\r\n
\t\t\tvar intDiffH = intCurrentHeight - intHeight;\r\n
\t\t\t// Perfomance the effect\r\n
\t\t\t$(\'#lightbox-container-image-box\').animate({ width: intWidth, height: intHeight },settings.containerResizeSpeed,function() { _show_image(); });\r\n
\t\t\tif ( ( intDiffW == 0 ) && ( intDiffH == 0 ) ) {\r\n
\t\t\t\tif ( $.browser.msie ) {\r\n
\t\t\t\t\t___pause(250);\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t___pause(100);\t\r\n
\t\t\t\t}\r\n
\t\t\t} \r\n
\t\t\t$(\'#lightbox-container-image-data-box\').css({ width: intImageWidth });\r\n
\t\t\t$(\'#lightbox-nav-btnPrev,#lightbox-nav-btnNext\').css({ height: intImageHeight + (settings.containerBorderSize * 2) });\r\n
\t\t};\r\n
\t\t/**\r\n
\t\t * Show the prepared image\r\n
\t\t *\r\n
\t\t */\r\n
\t\tfunction _show_image() {\r\n
\t\t\t$(\'#lightbox-loading\').hide();\r\n
\t\t\t$(\'#lightbox-image\').fadeIn(function() {\r\n
\t\t\t\t_show_image_data();\r\n
\t\t\t\t_set_navigation();\r\n
\t\t\t});\r\n
\t\t\t_preload_neighbor_images();\r\n
\t\t};\r\n
\t\t/**\r\n
\t\t * Show the image information\r\n
\t\t *\r\n
\t\t */\r\n
\t\tfunction _show_image_data() {\r\n
\t\t\t$(\'#lightbox-container-image-data-box\').slideDown(\'fast\');\r\n
\t\t\t$(\'#lightbox-image-details-caption\').hide();\r\n
\t\t\tif ( settings.imageArray[settings.activeImage][1] ) {\r\n
\t\t\t\t$(\'#lightbox-image-details-caption\').html(settings.imageArray[settings.activeImage][1]).show();\r\n
\t\t\t}\r\n
\t\t\t// If we have a image set, display \'Image X of X\'\r\n
\t\t\tif ( settings.imageArray.length > 1 ) {\r\n
\t\t\t\t$(\'#lightbox-image-details-currentNumber\').html(settings.txtImage + \' \' + ( settings.activeImage + 1 ) + \' \' + settings.txtOf + \' \' + settings.imageArray.length).show();\r\n
\t\t\t}\t\t\r\n
\t\t}\r\n
\t\t/**\r\n
\t\t * Display the button navigations\r\n
\t\t *\r\n
\t\t */\r\n
\t\tfunction _set_navigation() {\r\n
\t\t\t$(\'#lightbox-nav\').show();\r\n
\r\n
\t\t\t// Instead to define this configuration in CSS file, we define here. And it\xb4s need to IE. Just.\r\n
\t\t\t$(\'#lightbox-nav-btnPrev,#lightbox-nav-btnNext\').css({ \'background\' : \'transparent url(\' + settings.imageBlank + \') no-repeat\' });\r\n
\t\t\t\r\n
\t\t\t// Show the prev button, if not the first image in set\r\n
\t\t\tif ( settings.activeImage != 0 ) {\r\n
\t\t\t\tif ( settings.fixedNavigation ) {\r\n
\t\t\t\t\t$(\'#lightbox-nav-btnPrev\').css({ \'background\' : \'url(\' + settings.imageBtnPrev + \') left 15% no-repeat\' })\r\n
\t\t\t\t\t\t.unbind()\r\n
\t\t\t\t\t\t.bind(\'click\',function() {\r\n
\t\t\t\t\t\t\tsettings.activeImage = settings.activeImage - 1;\r\n
\t\t\t\t\t\t\t_set_image_to_view();\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t// Show the images button for Next buttons\r\n
\t\t\t\t\t$(\'#lightbox-nav-btnPrev\').unbind().hover(function() {\r\n
\t\t\t\t\t\t$(this).css({ \'background\' : \'url(\' + settings.imageBtnPrev + \') left 15% no-repeat\' });\r\n
\t\t\t\t\t},function() {\r\n
\t\t\t\t\t\t$(this).css({ \'background\' : \'transparent url(\' + settings.imageBlank + \') no-repeat\' });\r\n
\t\t\t\t\t}).show().bind(\'click\',function() {\r\n
\t\t\t\t\t\tsettings.activeImage = settings.activeImage - 1;\r\n
\t\t\t\t\t\t_set_image_to_view();\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\t\r\n
\t\t\t// Show the next button, if not the last image in set\r\n
\t\t\tif ( settings.activeImage != ( settings.imageArray.length -1 ) ) {\r\n
\t\t\t\tif ( settings.fixedNavigation ) {\r\n
\t\t\t\t\t$(\'#lightbox-nav-btnNext\').css({ \'background\' : \'url(\' + settings.imageBtnNext + \') right 15% no-repeat\' })\r\n
\t\t\t\t\t\t.unbind()\r\n
\t\t\t\t\t\t.bind(\'click\',function() {\r\n
\t\t\t\t\t\t\tsettings.activeImage = settings.activeImage + 1;\r\n
\t\t\t\t\t\t\t_set_image_to_view();\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t// Show the images button for Next buttons\r\n
\t\t\t\t\t$(\'#lightbox-nav-btnNext\').unbind().hover(function() {\r\n
\t\t\t\t\t\t$(this).css({ \'background\' : \'url(\' + settings.imageBtnNext + \') right 15% no-repeat\' });\r\n
\t\t\t\t\t},function() {\r\n
\t\t\t\t\t\t$(this).css({ \'background\' : \'transparent url(\' + settings.imageBlank + \') no-repeat\' });\r\n
\t\t\t\t\t}).show().bind(\'click\',function() {\r\n
\t\t\t\t\t\tsettings.activeImage = settings.activeImage + 1;\r\n
\t\t\t\t\t\t_set_image_to_view();\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\t// Enable keyboard navigation\r\n
\t\t\t_enable_keyboard_navigation();\r\n
\t\t}\r\n
\t\t/**\r\n
\t\t * Enable a support to keyboard navigation\r\n
\t\t *\r\n
\t\t */\r\n
\t\tfunction _enable_keyboard_navigation() {\r\n
\t\t\t$(document).keydown(function(objEvent) {\r\n
\t\t\t\t_keyboard_action(objEvent);\r\n
\t\t\t});\r\n
\t\t}\r\n
\t\t/**\r\n
\t\t * Disable the support to keyboard navigation\r\n
\t\t *\r\n
\t\t */\r\n
\t\tfunction _disable_keyboard_navigation() {\r\n
\t\t\t$(document).unbind();\r\n
\t\t}\r\n
\t\t/**\r\n
\t\t * Perform the keyboard actions\r\n
\t\t *\r\n
\t\t */\r\n
\t\tfunction _keyboard_action(objEvent) {\r\n
\t\t\t// To ie\r\n
\t\t\tif ( objEvent == null ) {\r\n
\t\t\t\tkeycode = event.keyCode;\r\n
\t\t\t\tescapeKey = 27;\r\n
\t\t\t// To Mozilla\r\n
\t\t\t} else {\r\n
\t\t\t\tkeycode = objEvent.keyCode;\r\n
\t\t\t\tescapeKey = objEvent.DOM_VK_ESCAPE;\r\n
\t\t\t}\r\n
\t\t\t// Get the key in lower case form\r\n
\t\t\tkey = String.fromCharCode(keycode).toLowerCase();\r\n
\t\t\t// Verify the keys to close the ligthBox\r\n
\t\t\tif ( ( key == settings.keyToClose ) || ( key == \'x\' ) || ( keycode == escapeKey ) ) {\r\n
\t\t\t\t_finish();\r\n
\t\t\t}\r\n
\t\t\t// Verify the key to show the previous image\r\n
\t\t\tif ( ( key == settings.keyToPrev ) || ( keycode == 37 ) ) {\r\n
\t\t\t\t// If we\xb4re not showing the first image, call the previous\r\n
\t\t\t\tif ( settings.activeImage != 0 ) {\r\n
\t\t\t\t\tsettings.activeImage = settings.activeImage - 1;\r\n
\t\t\t\t\t_set_image_to_view();\r\n
\t\t\t\t\t_disable_keyboard_navigation();\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\t// Verify the key to show the next image\r\n
\t\t\tif ( ( key == settings.keyToNext ) || ( keycode == 39 ) ) {\r\n
\t\t\t\t// If we\xb4re not showing the last image, call the next\r\n
\t\t\t\tif ( settings.activeImage != ( settings.imageArray.length - 1 ) ) {\r\n
\t\t\t\t\tsettings.activeImage = settings.activeImage + 1;\r\n
\t\t\t\t\t_set_image_to_view();\r\n
\t\t\t\t\t_disable_keyboard_navigation();\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\t/**\r\n
\t\t * Preload prev and next images being showed\r\n
\t\t *\r\n
\t\t */\r\n
\t\tfunction _preload_neighbor_images() {\r\n
\t\t\tif ( (settings.imageArray.length -1) > settings.activeImage ) {\r\n
\t\t\t\tobjNext = new Image();\r\n
\t\t\t\tobjNext.src = settings.imageArray[settings.activeImage + 1][0];\r\n
\t\t\t}\r\n
\t\t\tif ( settings.activeImage > 0 ) {\r\n
\t\t\t\tobjPrev = new Image();\r\n
\t\t\t\tobjPrev.src = settings.imageArray[settings.activeImage -1][0];\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\t/**\r\n
\t\t * Remove jQuery lightBox plugin HTML markup\r\n
\t\t *\r\n
\t\t */\r\n
\t\tfunction _finish() {\r\n
\t\t\t$(\'#jquery-lightbox\').remove();\r\n
\t\t\t$(\'#jquery-overlay\').fadeOut(function() { $(\'#jquery-overlay\').remove(); });\r\n
\t\t\t// Show some elements to avoid conflict with overlay in IE. These elements appear above the overlay.\r\n
\t\t\t$(\'embed, object, select\').css({ \'visibility\' : \'visible\' });\r\n
\t\t}\r\n
\t\t/**\r\n
\t\t / THIRD FUNCTION\r\n
\t\t * getPageSize() by quirksmode.com\r\n
\t\t *\r\n
\t\t * @return Array Return an array with page width, height and window width, height\r\n
\t\t */\r\n
\t\tfunction ___getPageSize() {\r\n
\t\t\tvar xScroll, yScroll;\r\n
\t\t\tif (window.innerHeight && window.scrollMaxY) {\t\r\n
\t\t\t\txScroll = window.innerWidth + window.scrollMaxX;\r\n
\t\t\t\tyScroll = window.innerHeight + window.scrollMaxY;\r\n
\t\t\t} else if (document.body.scrollHeight > document.body.offsetHeight){ // all but Explorer Mac\r\n
\t\t\t\txScroll = document.body.scrollWidth;\r\n
\t\t\t\tyScroll = document.body.scrollHeight;\r\n
\t\t\t} else { // Explorer Mac...would also work in Explorer 6 Strict, Mozilla and Safari\r\n
\t\t\t\txScroll = document.body.offsetWidth;\r\n
\t\t\t\tyScroll = document.body.offsetHeight;\r\n
\t\t\t}\r\n
\t\t\tvar windowWidth, windowHeight;\r\n
\t\t\tif (self.innerHeight) {\t// all except Explorer\r\n
\t\t\t\tif(document.documentElement.clientWidth){\r\n
\t\t\t\t\twindowWidth = document.documentElement.clientWidth; \r\n
\t\t\t\t} else {\r\n
\t\t\t\t\twindowWidth = self.innerWidth;\r\n
\t\t\t\t}\r\n
\t\t\t\twindowHeight = self.innerHeight;\r\n
\t\t\t} else if (document.documentElement && document.documentElement.clientHeight) { // Explorer 6 Strict Mode\r\n
\t\t\t\twindowWidth = document.documentElement.clientWidth;\r\n
\t\t\t\twindowHeight = document.documentElement.clientHeight;\r\n
\t\t\t} else if (document.body) { // other Explorers\r\n
\t\t\t\twindowWidth = document.body.clientWidth;\r\n
\t\t\t\twindowHeight = document.body.clientHeight;\r\n
\t\t\t}\t\r\n
\t\t\t// for small pages with total height less then height of the viewport\r\n
\t\t\tif(yScroll < windowHeight){\r\n
\t\t\t\tpageHeight = windowHeight;\r\n
\t\t\t} else { \r\n
\t\t\t\tpageHeight = yScroll;\r\n
\t\t\t}\r\n
\t\t\t// for small pages with total width less then width of the viewport\r\n
\t\t\tif(xScroll < windowWidth){\t\r\n
\t\t\t\tpageWidth = xScroll;\t\t\r\n
\t\t\t} else {\r\n
\t\t\t\tpageWidth = windowWidth;\r\n
\t\t\t}\r\n
\t\t\tarrayPageSize = new Array(pageWidth,pageHeight,windowWidth,windowHeight);\r\n
\t\t\treturn arrayPageSize;\r\n
\t\t};\r\n
\t\t/**\r\n
\t\t / THIRD FUNCTION\r\n
\t\t * getPageScroll() by quirksmode.com\r\n
\t\t *\r\n
\t\t * @return Array Return an array with x,y page scroll values.\r\n
\t\t */\r\n
\t\tfunction ___getPageScroll() {\r\n
\t\t\tvar xScroll, yScroll;\r\n
\t\t\tif (self.pageYOffset) {\r\n
\t\t\t\tyScroll = self.pageYOffset;\r\n
\t\t\t\txScroll = self.pageXOffset;\r\n
\t\t\t} else if (document.documentElement && document.documentElement.scrollTop) {\t // Explorer 6 Strict\r\n
\t\t\t\tyScroll = document.documentElement.scrollTop;\r\n
\t\t\t\txScroll = document.documentElement.scrollLeft;\r\n
\t\t\t} else if (document.body) {// all other Explorers\r\n
\t\t\t\tyScroll = document.body.scrollTop;\r\n
\t\t\t\txScroll = document.body.scrollLeft;\t\r\n
\t\t\t}\r\n
\t\t\tarrayPageScroll = new Array(xScroll,yScroll);\r\n
\t\t\treturn arrayPageScroll;\r\n
\t\t};\r\n
\t\t /**\r\n
\t\t  * Stop the code execution from a escified time in milisecond\r\n
\t\t  *\r\n
\t\t  */\r\n
\t\t function ___pause(ms) {\r\n
\t\t\tvar date = new Date(); \r\n
\t\t\tcurDate = null;\r\n
\t\t\tdo { var curDate = new Date(); }\r\n
\t\t\twhile ( curDate - date < ms);\r\n
\t\t };\r\n
\t\t// Return the jQuery object for chaining. The unbind method is used to avoid click conflict when the plugin is called more than once\r\n
\t\treturn this.unbind(\'click\').click(_initialize);\r\n
\t};\r\n
})(jQuery); // Call and execute the function immediately passing the jQuery object

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>20065</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>jquery.lightbox-0.5.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
