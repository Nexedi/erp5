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
            <value> <string>ts39831393.83</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>textfield.js</string> </value>
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
CKEDITOR.dialog.add("textfield",function(b){function e(a){var a=a.element,b=this.getValue();b?a.setAttribute(this.id,b):a.removeAttribute(this.id)}function f(a){this.setValue(a.hasAttribute(this.id)&&a.getAttribute(this.id)||"")}var g={email:1,password:1,search:1,tel:1,text:1,url:1};return{title:b.lang.forms.textfield.title,minWidth:350,minHeight:150,onShow:function(){delete this.textField;var a=this.getParentEditor().getSelection().getSelectedElement();if(a&&"input"==a.getName()&&(g[a.getAttribute("type")]||\n
!a.getAttribute("type")))this.textField=a,this.setupContent(a)},onOk:function(){var a=this.getParentEditor(),b=this.textField,c=!b;c&&(b=a.document.createElement("input"),b.setAttribute("type","text"));b={element:b};c&&a.insertElement(b.element);this.commitContent(b);c||a.getSelection().selectElement(b.element)},onLoad:function(){this.foreach(function(a){if(a.getValue&&(a.setup||(a.setup=f),!a.commit))a.commit=e})},contents:[{id:"info",label:b.lang.forms.textfield.title,title:b.lang.forms.textfield.title,\n
elements:[{type:"hbox",widths:["50%","50%"],children:[{id:"_cke_saved_name",type:"text",label:b.lang.forms.textfield.name,"default":"",accessKey:"N",setup:function(a){this.setValue(a.data("cke-saved-name")||a.getAttribute("name")||"")},commit:function(a){a=a.element;this.getValue()?a.data("cke-saved-name",this.getValue()):(a.data("cke-saved-name",!1),a.removeAttribute("name"))}},{id:"value",type:"text",label:b.lang.forms.textfield.value,"default":"",accessKey:"V",commit:function(a){if(CKEDITOR.env.ie&&\n
!this.getValue()){var d=a.element,c=new CKEDITOR.dom.element("input",b.document);d.copyAttributes(c,{value:1});c.replace(d);a.element=c}else e.call(this,a)}}]},{type:"hbox",widths:["50%","50%"],children:[{id:"size",type:"text",label:b.lang.forms.textfield.charWidth,"default":"",accessKey:"C",style:"width:50px",validate:CKEDITOR.dialog.validate.integer(b.lang.common.validateNumberFailed)},{id:"maxLength",type:"text",label:b.lang.forms.textfield.maxChars,"default":"",accessKey:"M",style:"width:50px",\n
validate:CKEDITOR.dialog.validate.integer(b.lang.common.validateNumberFailed)}],onLoad:function(){CKEDITOR.env.ie7Compat&&this.getElement().setStyle("zoom","100%")}},{id:"type",type:"select",label:b.lang.forms.textfield.type,"default":"text",accessKey:"M",items:[[b.lang.forms.textfield.typeEmail,"email"],[b.lang.forms.textfield.typePass,"password"],[b.lang.forms.textfield.typeSearch,"search"],[b.lang.forms.textfield.typeTel,"tel"],[b.lang.forms.textfield.typeText,"text"],[b.lang.forms.textfield.typeUrl,\n
"url"]],setup:function(a){this.setValue(a.getAttribute("type"))},commit:function(a){var d=a.element;if(CKEDITOR.env.ie){var c=d.getAttribute("type"),e=this.getValue();c!=e&&(c=CKEDITOR.dom.element.createFromHtml(\'<input type="\'+e+\'"></input>\',b.document),d.copyAttributes(c,{type:1}),c.replace(d),a.element=c)}else d.setAttribute("type",this.getValue())}},{id:"required",type:"checkbox",label:b.lang.forms.textfield.required,"default":"",accessKey:"Q",value:"required",setup:function(a){this.setValue(a.getAttribute("required"))},\n
commit:function(a){a=a.element;this.getValue()?a.setAttribute("required","required"):a.removeAttribute("required")}}]}]}});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3349</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
