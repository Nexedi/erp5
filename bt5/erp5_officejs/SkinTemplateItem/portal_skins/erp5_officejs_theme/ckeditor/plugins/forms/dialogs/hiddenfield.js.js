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
            <value> <string>hiddenfield.js</string> </value>
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
CKEDITOR.dialog.add("hiddenfield",function(d){return{title:d.lang.forms.hidden.title,hiddenField:null,minWidth:350,minHeight:110,onShow:function(){delete this.hiddenField;var a=this.getParentEditor(),b=a.getSelection(),c=b.getSelectedElement();c&&(c.data("cke-real-element-type")&&"hiddenfield"==c.data("cke-real-element-type"))&&(this.hiddenField=c,c=a.restoreRealElement(this.hiddenField),this.setupContent(c),b.selectElement(this.hiddenField))},onOk:function(){var a=this.getValueOf("info","_cke_saved_name"),\n
b=this.getParentEditor(),a=CKEDITOR.env.ie&&8>CKEDITOR.document.$.documentMode?b.document.createElement(\'<input name="\'+CKEDITOR.tools.htmlEncode(a)+\'">\'):b.document.createElement("input");a.setAttribute("type","hidden");this.commitContent(a);a=b.createFakeElement(a,"cke_hidden","hiddenfield");this.hiddenField?(a.replace(this.hiddenField),b.getSelection().selectElement(a)):b.insertElement(a);return!0},contents:[{id:"info",label:d.lang.forms.hidden.title,title:d.lang.forms.hidden.title,elements:[{id:"_cke_saved_name",\n
type:"text",label:d.lang.forms.hidden.name,"default":"",accessKey:"N",setup:function(a){this.setValue(a.data("cke-saved-name")||a.getAttribute("name")||"")},commit:function(a){this.getValue()?a.setAttribute("name",this.getValue()):a.removeAttribute("name")}},{id:"value",type:"text",label:d.lang.forms.hidden.value,"default":"",accessKey:"V",setup:function(a){this.setValue(a.getAttribute("value")||"")},commit:function(a){this.getValue()?a.setAttribute("value",this.getValue()):a.removeAttribute("value")}}]}]}});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1698</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
