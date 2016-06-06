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
            <value> <string>ts86919896.69</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>insert_image.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* This compressed file is part of Xinha. For uncompressed sources, forum, and bug reports, go to xinha.org */\n
InsertImage._pluginInfo={name:"InsertImage",origin:"Xinha Core",version:"$LastChangedRevision: 1239 $".replace(/^[^:]*:\\s*(.*)\\s*\\$$/,"$1"),developer:"The Xinha Core Developer Team",developer_url:"$HeadURL: http://svn.xinha.org/trunk/modules/InsertImage/insert_image.js $".replace(/^[^:]*:\\s*(.*)\\s*\\$$/,"$1"),sponsor:"",sponsor_url:"",license:"htmlArea"};function InsertImage(c){this.editor=c;var a=c.config;var b=this;if(typeof c._insertImage=="undefined"){c._insertImage=function(){b.show()}}}InsertImage.prototype._lc=function(a){return Xinha._lc(a,"Xinha")};InsertImage.prototype.onGenerateOnce=function(){InsertImage.loadAssets()};InsertImage.loadAssets=function(){var self=InsertImage;if(self.loading){return}self.loading=true;Xinha._getback(_editor_url+"modules/InsertImage/dialog.html",function(getback){self.html=getback;self.dialogReady=true});Xinha._getback(_editor_url+"modules/InsertImage/pluginMethods.js",function(getback){eval(getback);self.methodsReady=true})};InsertImage.prototype.onUpdateToolbar=function(){if(!(InsertImage.dialogReady&&InsertImage.methodsReady)){this.editor._toolbarObjects.insertimage.state("enabled",false)}else{this.onUpdateToolbar=null}};InsertImage.prototype.prepareDialog=function(){var b=this;var a=this.editor;var c=this.dialog=new Xinha.Dialog(a,InsertImage.html,"Xinha",{width:410});c.getElementById("ok").onclick=function(){b.apply()};c.getElementById("cancel").onclick=function(){b.dialog.hide()};c.getElementById("preview").onclick=function(){var d=c.getElementById("f_url");var e=d.value;if(!e){alert(c._lc("You must enter the URL"));d.focus();return false}c.getElementById("ipreview").src=e;return false};this.dialog.onresize=function(){var d=parseInt(this.height,10)-this.getElementById("h1").offsetHeight-this.getElementById("buttons").offsetHeight-this.getElementById("inputs").offsetHeight-parseInt(this.rootElem.style.paddingBottom,10);this.getElementById("ipreview").style.height=((d>0)?d:0)+"px";this.getElementById("ipreview").style.width=this.width-2+"px"};this.dialogReady=true};

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2154</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>insert_image.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
