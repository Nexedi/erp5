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
            <value> <string>ts39831393.88</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>specialchar.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

﻿/*\n
 Copyright (c) 2003-2015, CKSource - Frederico Knabben. All rights reserved.\n
 For licensing, see LICENSE.md or http://ckeditor.com/license\n
*/\n
CKEDITOR.dialog.add("specialchar",function(i){var e,l=i.lang.specialchar,k=function(c){var b,c=c.data?c.data.getTarget():new CKEDITOR.dom.element(c);if("a"==c.getName()&&(b=c.getChild(0).getHtml()))c.removeClass("cke_light_background"),e.hide(),c=i.document.createElement("span"),c.setHtml(b),i.insertText(c.getText())},m=CKEDITOR.tools.addFunction(k),j,g=function(c,b){var a,b=b||c.data.getTarget();"span"==b.getName()&&(b=b.getParent());if("a"==b.getName()&&(a=b.getChild(0).getHtml())){j&&d(null,j);\n
var f=e.getContentElement("info","htmlPreview").getElement();e.getContentElement("info","charPreview").getElement().setHtml(a);f.setHtml(CKEDITOR.tools.htmlEncode(a));b.getParent().addClass("cke_light_background");j=b}},d=function(c,b){b=b||c.data.getTarget();"span"==b.getName()&&(b=b.getParent());"a"==b.getName()&&(e.getContentElement("info","charPreview").getElement().setHtml("&nbsp;"),e.getContentElement("info","htmlPreview").getElement().setHtml("&nbsp;"),b.getParent().removeClass("cke_light_background"),\n
j=void 0)},n=CKEDITOR.tools.addFunction(function(c){var c=new CKEDITOR.dom.event(c),b=c.getTarget(),a;a=c.getKeystroke();var f="rtl"==i.lang.dir;switch(a){case 38:if(a=b.getParent().getParent().getPrevious())a=a.getChild([b.getParent().getIndex(),0]),a.focus(),d(null,b),g(null,a);c.preventDefault();break;case 40:if(a=b.getParent().getParent().getNext())if((a=a.getChild([b.getParent().getIndex(),0]))&&1==a.type)a.focus(),d(null,b),g(null,a);c.preventDefault();break;case 32:k({data:c});c.preventDefault();\n
break;case f?37:39:if(a=b.getParent().getNext())a=a.getChild(0),1==a.type?(a.focus(),d(null,b),g(null,a),c.preventDefault(!0)):d(null,b);else if(a=b.getParent().getParent().getNext())(a=a.getChild([0,0]))&&1==a.type?(a.focus(),d(null,b),g(null,a),c.preventDefault(!0)):d(null,b);break;case f?39:37:(a=b.getParent().getPrevious())?(a=a.getChild(0),a.focus(),d(null,b),g(null,a),c.preventDefault(!0)):(a=b.getParent().getParent().getPrevious())?(a=a.getLast().getChild(0),a.focus(),d(null,b),g(null,a),c.preventDefault(!0)):\n
d(null,b)}});return{title:l.title,minWidth:430,minHeight:280,buttons:[CKEDITOR.dialog.cancelButton],charColumns:17,onLoad:function(){for(var c=this.definition.charColumns,b=i.config.specialChars,a=CKEDITOR.tools.getNextId()+"_specialchar_table_label",f=[\'<table role="listbox" aria-labelledby="\'+a+\'" style="width: 320px; height: 100%; border-collapse: separate;" align="center" cellspacing="2" cellpadding="2" border="0">\'],d=0,g=b.length,h,e;d<g;){f.push(\'<tr role="presentation">\');for(var j=0;j<c;j++,\n
d++){if(h=b[d]){h instanceof Array?(e=h[1],h=h[0]):(e=h.replace("&","").replace(";","").replace("#",""),e=l[e]||h);var k="cke_specialchar_label_"+d+"_"+CKEDITOR.tools.getNextNumber();f.push(\'<td class="cke_dark_background" style="cursor: default" role="presentation"><a href="javascript: void(0);" role="option" aria-posinset="\'+(d+1)+\'"\',\' aria-setsize="\'+g+\'"\',\' aria-labelledby="\'+k+\'"\',\' class="cke_specialchar" title="\',CKEDITOR.tools.htmlEncode(e),\'" onkeydown="CKEDITOR.tools.callFunction( \'+n+\n
\', event, this )" onclick="CKEDITOR.tools.callFunction(\'+m+\', this); return false;" tabindex="-1"><span style="margin: 0 auto;cursor: inherit">\'+h+\'</span><span class="cke_voice_label" id="\'+k+\'">\'+e+"</span></a>")}else f.push(\'<td class="cke_dark_background">&nbsp;\');f.push("</td>")}f.push("</tr>")}f.push("</tbody></table>",\'<span id="\'+a+\'" class="cke_voice_label">\'+l.options+"</span>");this.getContentElement("info","charContainer").getElement().setHtml(f.join(""))},contents:[{id:"info",label:i.lang.common.generalTab,\n
title:i.lang.common.generalTab,padding:0,align:"top",elements:[{type:"hbox",align:"top",widths:["320px","90px"],children:[{type:"html",id:"charContainer",html:"",onMouseover:g,onMouseout:d,focus:function(){var c=this.getElement().getElementsByTag("a").getItem(0);setTimeout(function(){c.focus();g(null,c)},0)},onShow:function(){var c=this.getElement().getChild([0,0,0,0,0]);setTimeout(function(){c.focus();g(null,c)},0)},onLoad:function(c){e=c.sender}},{type:"hbox",align:"top",widths:["100%"],children:[{type:"vbox",\n
align:"top",children:[{type:"html",html:"<div></div>"},{type:"html",id:"charPreview",className:"cke_dark_background",style:"border:1px solid #eeeeee;font-size:28px;height:40px;width:70px;padding-top:9px;font-family:\'Microsoft Sans Serif\',Arial,Helvetica,Verdana;text-align:center;",html:"<div>&nbsp;</div>"},{type:"html",id:"htmlPreview",className:"cke_dark_background",style:"border:1px solid #eeeeee;font-size:14px;height:20px;width:70px;padding-top:2px;font-family:\'Microsoft Sans Serif\',Arial,Helvetica,Verdana;text-align:center;",\n
html:"<div>&nbsp;</div>"}]}]}]}]}]}});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>4824</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
