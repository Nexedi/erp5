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
            <value> <string>ts86919702.49</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>pluginMethods.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* This compressed file is part of Xinha. For uncompressed sources, forum, and bug reports, go to xinha.org */\n
CreateLink.prototype.show=function(b){if(!this.dialog){this.prepareDialog()}var c=this.editor;this.a=b;if(!b&&this.editor.selectionEmpty(this.editor.getSelection())){alert(this._lc("You need to select some text before creating a link"));return false}var d={f_href:"",f_title:"",f_target:"",f_other_target:""};if(b&&b.tagName.toLowerCase()=="a"){d.f_href=this.editor.fixRelativeLinks(b.getAttribute("href"));d.f_title=b.title;if(b.target){if(!/_self|_top|_blank/.test(b.target)){d.f_target="_other";d.f_other_target=b.target}else{d.f_target=b.target;d.f_other_target=""}}}this.dialog.show(d)};CreateLink.prototype.apply=function(){var m=this.dialog.hide();var k=this.a;var c=this.editor;var l={href:"",target:"",title:""};if(m.f_href){l.href=m.f_href;l.title=m.f_title;if(m.f_target.value){if(m.f_target.value=="other"){l.target=m.f_other_target}else{l.target=m.f_target.value}}}if(m.f_target.value){if(m.f_target.value!="_other"){l.target=m.f_target.value}else{l.target=m.f_other_target}}if(k&&k.tagName.toLowerCase()=="a"){if(!l.href){if(confirm(this._lc("Are you sure you wish to remove this link?"))){var b=k.parentNode;while(k.hasChildNodes()){b.insertBefore(k.removeChild(k.childNodes[0]),k)}b.removeChild(k);c.updateToolbar();return}}else{for(var g in l){k.setAttribute(g,l[g])}if(Xinha.is_ie){if(/mailto:([^?<>]*)(\\?[^<]*)?$/i.test(k.innerHTML)){k.innerHTML=RegExp.$1}}}}else{if(!l.href){return true}var f=Xinha.uniq("http://www.example.com/Link");c._doc.execCommand("createlink",false,f);var h=c._doc.getElementsByTagName("a");for(var g=0;g<h.length;g++){var d=h[g];if(d.href==f){if(!k){k=d}for(var e in l){d.setAttribute(e,l[e])}}}}c.selectNodeContents(k);c.updateToolbar()};CreateLink.prototype._getSelectedAnchor=function(){var d=this.editor.getSelection();var c=this.editor.createRange(d);var b=this.editor.activeElement(d);if(b!=null&&b.tagName.toLowerCase()=="a"){return b}else{b=this.editor._getFirstAncestor(d,"a");if(b!=null){return b}}return null};

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2077</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>pluginMethods.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
