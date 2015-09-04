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
            <value> <string>ts40515059.47</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ext-overview_window.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals svgEditor, svgedit, $ */\n
/*jslint es5: true, vars: true*/\n
/*\n
 * ext-overview_window.js\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2013 James Sacksteder\n
 *\n
 */\n
\n
var overviewWindowGlobals = {};\n
svgEditor.addExtension("overview_window", function() {\t\'use strict\';\n
\t//define and insert the base html element\n
\tvar propsWindowHtml= "\\\n
\t\t<div id=\\"overview_window_content_pane\\" style=\\" width:100%; word-wrap:break-word;  display:inline-block; margin-top:20px;\\">\\\n
\t\t\t<div id=\\"overview_window_content\\" style=\\"position:relative; left:12px; top:0px;\\">\\\n
\t\t\t\t<div style=\\"background-color:#A0A0A0; display:inline-block; overflow:visible;\\">\\\n
\t\t\t\t\t<svg id=\\"overviewMiniView\\" width=\\"150\\" height=\\"100\\" x=\\"0\\" y=\\"0\\" viewBox=\\"0 0 4800 3600\\" xmlns=\\"http://www.w3.org/2000/svg\\" xmlns:xlink=\\"http://www.w3.org/1999/xlink\\">\\\n
\t\t\t\t\t\t<use x=\\"0\\" y=\\"0\\" xlink:href=\\"#svgroot\\"> <\\/use>\\\n
\t\t\t\t\t </svg>\\\n
\t\t\t\t\t <div id=\\"overview_window_view_box\\" style=\\"min-width:50px; min-height:50px; position:absolute; top:30px; left:30px; z-index:5; background-color:rgba(255,0,102,0.3);\\">\\\n
\t\t\t\t\t <\\/div>\\\n
\t\t\t\t <\\/div>\\\n
\t\t\t<\\/div>\\\n
\t\t<\\/div>";\n
\t$("#sidepanels").append(propsWindowHtml);\n
\n
\t//define dynamic animation of the view box.\n
\tvar updateViewBox = function(){\n
\t\tvar portHeight=parseFloat($("#workarea").css("height"));\n
\t\tvar portWidth=parseFloat($("#workarea").css("width"));\n
\t\tvar portX=$("#workarea").scrollLeft();\n
\t\tvar portY=$("#workarea").scrollTop();\n
\t\tvar windowWidth=parseFloat($("#svgcanvas").css("width"));\n
\t\tvar windowHeight=parseFloat($("#svgcanvas").css("height"));\n
\t\tvar overviewWidth=$("#overviewMiniView").attr("width");\n
\t\tvar overviewHeight=$("#overviewMiniView").attr("height");\n
\t\t\n
\t\tvar viewBoxX=portX/windowWidth*overviewWidth;\n
\t\tvar viewBoxY=portY/windowHeight*overviewHeight;\n
\t\tvar viewBoxWidth=portWidth/windowWidth*overviewWidth;\n
\t\tvar viewBoxHeight=portHeight/windowHeight*overviewHeight;\n
\t\t\n
\t\t$("#overview_window_view_box").css("min-width",viewBoxWidth+"px");\n
\t\t$("#overview_window_view_box").css("min-height",viewBoxHeight+"px");\n
\t\t$("#overview_window_view_box").css("top",viewBoxY+"px");\n
\t\t$("#overview_window_view_box").css("left",viewBoxX+"px");\n
\t};\n
\t$("#workarea").scroll(function(){\n
\t\tif(!(overviewWindowGlobals.viewBoxDragging)){\n
\t\t\tupdateViewBox();\n
\t\t}\n
\t});\n
\t$("#workarea").resize(updateViewBox);\n
\tupdateViewBox();\n
\t\n
\t//comphensate for changes in zoom and canvas size\n
\tvar updateViewDimensions= function(){\n
\t\tvar viewWidth=$("#svgroot").attr("width");\n
\t\tvar viewHeight=$("#svgroot").attr("height");\n
\t\tvar viewX=640;\n
\t\tvar viewY=480;\n
\t\t\n
\t\tif(svgedit.browser.isIE())\n
\t\t{\n
\t\t\t//This has only been tested with Firefox 10 and IE 9 (without chrome frame).\n
\t\t\t//I am not sure if if is Firefox or IE that is being non compliant here.\n
\t\t\t//Either way the one that is noncompliant may become more compliant later.\n
\t\t\t//TAG:HACK  \n
\t\t\t//TAG:VERSION_DEPENDENT\n
\t\t\t//TAG:BROWSER_SNIFFING\n
\t\t\tviewX=0;\n
\t\t\tviewY=0;\n
\t\t}\n
\t\t\n
\t\tvar svgWidth_old=$("#overviewMiniView").attr("width");\n
\t\tvar svgHeight_new=viewHeight/viewWidth*svgWidth_old;\n
\t\t$("#overviewMiniView").attr("viewBox",viewX+" "+viewY+" "+viewWidth+" "+viewHeight);\n
\t\t$("#overviewMiniView").attr("height",svgHeight_new);\n
\t\tupdateViewBox();\n
\t};\n
\tupdateViewDimensions();\n
\t\n
\t//set up the overview window as a controller for the view port.\n
\toverviewWindowGlobals.viewBoxDragging=false;\n
\tvar updateViewPortFromViewBox = function(){\n
\t\n
\t\tvar windowWidth =parseFloat($("#svgcanvas").css("width" ));\n
\t\tvar windowHeight=parseFloat($("#svgcanvas").css("height"));\n
\t\tvar overviewWidth =$("#overviewMiniView").attr("width" );\n
\t\tvar overviewHeight=$("#overviewMiniView").attr("height");\n
\t\tvar viewBoxX=parseFloat($("#overview_window_view_box").css("left"));\n
\t\tvar viewBoxY=parseFloat($("#overview_window_view_box").css("top" ));\n
\t\t\n
\t\tvar portX=viewBoxX/overviewWidth *windowWidth;\n
\t\tvar portY=viewBoxY/overviewHeight*windowHeight;\n
\n
\t\t$("#workarea").scrollLeft(portX);\n
\t\t$("#workarea").scrollTop(portY);\n
\t};\n
\t$( "#overview_window_view_box" ).draggable({  containment: "parent"\n
\t\t,drag: updateViewPortFromViewBox\n
\t\t,start:function(){overviewWindowGlobals.viewBoxDragging=true; }\n
\t\t,stop :function(){overviewWindowGlobals.viewBoxDragging=false;}\n
\t});  \n
\t$("#overviewMiniView").click(function(evt){\n
\t\t//Firefox doesn\'t support evt.offsetX and evt.offsetY\n
\t\tvar mouseX=(evt.offsetX || evt.originalEvent.layerX);\n
\t\tvar mouseY=(evt.offsetY || evt.originalEvent.layerY);\n
\t\tvar overviewWidth =$("#overviewMiniView").attr("width" );\n
\t\tvar overviewHeight=$("#overviewMiniView").attr("height");\n
\t\tvar viewBoxWidth =parseFloat($("#overview_window_view_box").css("min-width" ));\n
\t\tvar viewBoxHeight=parseFloat($("#overview_window_view_box").css("min-height"));\n
 \n
\t\tvar viewBoxX=mouseX - 0.5 * viewBoxWidth;\n
\t\tvar viewBoxY=mouseY- 0.5 * viewBoxHeight;\n
\t\t//deal with constraints\n
\t\tif(viewBoxX<0){\n
\t\t\tviewBoxX=0;\n
\t\t}\n
\t\tif(viewBoxY<0){\n
\t\t\tviewBoxY=0;\n
\t\t}\n
\t\tif(viewBoxX+viewBoxWidth>overviewWidth){\n
\t\t\tviewBoxX=overviewWidth-viewBoxWidth;\n
\t\t}\n
\t\tif(viewBoxY+viewBoxHeight>overviewHeight){\n
\t\t\tviewBoxY=overviewHeight-viewBoxHeight;\n
\t\t}\n
\t\t\n
\t\t$("#overview_window_view_box").css("top",viewBoxY+"px");\n
\t\t$("#overview_window_view_box").css("left",viewBoxX+"px");\n
\t\tupdateViewPortFromViewBox();\n
\t});\n
\t\n
\treturn{\n
\t\tname: "overview window",\n
\t\tcanvasUpdated:updateViewDimensions,\n
\t\tworkareaResized:updateViewBox\n
\t};\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>5360</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
