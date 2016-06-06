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
            <value> <string>ts86919644.58</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>popupwin.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* This compressed file is part of Xinha. For uncompressed sources, forum, and bug reports, go to xinha.org */\n
function PopupWin(c,g,j,a){this.editor=c;this.handler=j;var f=window.open("","__ha_dialog","toolbar=no,menubar=no,personalbar=no,width=600,height=600,left=20,top=40,scrollbars=no,resizable=yes");this.window=f;var h=f.document;this.doc=h;var i=this;var b=document.baseURI||document.URL;if(b&&b.match(/(.*)\\/([^\\/]+)/)){b=RegExp.$1+"/"}if(typeof _editor_url!="undefined"&&!(/^\\//.test(_editor_url))&&!(/http:\\/\\//.test(_editor_url))){b+=_editor_url}else{b=_editor_url}if(!(/\\/$/.test(b))){b+="/"}this.baseURL=b;h.open();var e="<html><head><title>"+g+"</title>\\n";e+=\'<style type="text/css">@import url(\'+_editor_url+"Xinha.css);</style>\\n";if(_editor_skin!=""){e+=\'<style type="text/css">@import url(\'+_editor_url+"skins/"+_editor_skin+"/skin.css);</style>\\n"}e+="</head>\\n";e+=\'<body class="dialog popupwin" id="--HA-body"></body></html>\';h.write(e);h.close();function d(){var k=h.body;if(!k){setTimeout(d,25);return false}f.title=g;h.documentElement.style.padding="0px";h.documentElement.style.margin="0px";var l=h.createElement("div");l.className="content";i.content=l;k.appendChild(l);i.element=k;a(i);f.focus()}d()}PopupWin.prototype.callHandler=function(){var c=["input","textarea","select"];var h={};for(var f=c.length;--f>=0;){var a=c[f];var d=this.content.getElementsByTagName(a);for(var b=0;b<d.length;++b){var e=d[b];var g=e.value;if(e.tagName.toLowerCase()=="input"){if(e.type=="checkbox"){g=e.checked}}h[e.name]=g}}this.handler(this,h);return false};PopupWin.prototype.close=function(){this.window.close()};PopupWin.prototype.addButtons=function(){var a=this;var e=this.doc.createElement("div");this.content.appendChild(e);e.id="buttons";e.className="buttons";for(var d=0;d<arguments.length;++d){var c=arguments[d];var b=this.doc.createElement("button");e.appendChild(b);b.innerHTML=Xinha._lc(c,"Xinha");switch(c.toLowerCase()){case"ok":Xinha.addDom0Event(b,"click",function(){a.callHandler();a.close();return false});break;case"cancel":Xinha.addDom0Event(b,"click",function(){a.close();return false});break}}};PopupWin.prototype.showAtElement=function(){var a=this;setTimeout(function(){var b=a.content.offsetWidth+4;var e=a.content.offsetHeight+4;var d=a.content;var c=d.style;c.position="absolute";c.left=parseInt((b-d.offsetWidth)/2,10)+"px";c.top=parseInt((e-d.offsetHeight)/2,10)+"px";if(Xinha.is_gecko){a.window.innerWidth=b;a.window.innerHeight=e}else{a.window.resizeTo(b+8,e+70)}},25)};

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2517</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>popupwin.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
