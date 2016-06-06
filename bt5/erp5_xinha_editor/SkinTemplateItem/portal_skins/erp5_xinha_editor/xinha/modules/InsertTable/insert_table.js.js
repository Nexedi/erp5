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
            <value> <string>ts86919945.97</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>insert_table.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* This compressed file is part of Xinha. For uncompressed sources, forum, and bug reports, go to xinha.org */\n
InsertTable._pluginInfo={name:"InsertTable",origin:"Xinha Core",version:"$LastChangedRevision: 1085 $".replace(/^[^:]*:\\s*(.*)\\s*\\$$/,"$1"),developer:"The Xinha Core Developer Team",developer_url:"$HeadURL: http://svn.xinha.org/trunk/modules/InsertTable/insert_table.js $".replace(/^[^:]*:\\s*(.*)\\s*\\$$/,"$1"),sponsor:"",sponsor_url:"",license:"htmlArea"};function InsertTable(c){this.editor=c;var a=c.config;var b=this;c.config.btnList.inserttable[3]=function(){b.show()}}InsertTable.prototype._lc=function(a){return Xinha._lc(a,"Xinha")};InsertTable.prototype.onGenerateOnce=function(){InsertTable.loadAssets()};InsertTable.loadAssets=function(){var self=InsertTable;if(self.loading){return}self.loading=true;Xinha._getback(_editor_url+"modules/InsertTable/dialog.html",function(getback){self.html=getback;self.dialogReady=true});Xinha._getback(_editor_url+"modules/InsertTable/pluginMethods.js",function(getback){eval(getback);self.methodsReady=true})};InsertTable.prototype.onUpdateToolbar=function(){if(!(InsertTable.dialogReady&&InsertTable.methodsReady)){this.editor._toolbarObjects.inserttable.state("enabled",false)}else{this.onUpdateToolbar=null}};InsertTable.prototype.prepareDialog=function(){var b=this;var a=this.editor;var c=this.dialog=new Xinha.Dialog(a,InsertTable.html,"Xinha",{width:400});c.getElementById("ok").onclick=function(){b.apply()};c.getElementById("cancel").onclick=function(){b.dialog.hide()};this.borderColorPicker=new Xinha.colorPicker.InputBinding(c.getElementById("border_color"));this.dialog.onresize=function(){this.getElementById("layout_fieldset").style.width=(this.width/2)+50+"px";this.getElementById("spacing_fieldset").style.width=(this.width/2)-120+"px"};this.dialogReady=true};

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1834</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>insert_table.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
