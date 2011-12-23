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
            <value> <string>ts86919638.22</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>panel-dialog.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

\n
Xinha.PanelDialog = function(editor, side, html, localizer)\n
{\n
  this.id    = { };\n
  this.r_id  = { }; // reverse lookup id\n
  this.editor   = editor;\n
  this.document = document;\n
  this.rootElem = editor.addPanel(side);\n
\n
  var dialog = this;\n
  if(typeof localizer == \'function\')\n
  {\n
    this._lc = localizer;\n
  }\n
  else if(localizer)\n
  {\n
    this._lc = function(string)\n
    {\n
      return Xinha._lc(string,localizer);\n
    };\n
  }\n
  else\n
  {\n
    this._lc = function(string)\n
    {\n
      return string;\n
    };\n
  }\n
\n
  html = html.replace(/\\[([a-z0-9_]+)\\]/ig,\n
                      function(fullString, id)\n
                      {\n
                        if(typeof dialog.id[id] == \'undefined\')\n
                        {\n
                          dialog.id[id] = Xinha.uniq(\'Dialog\');\n
                          dialog.r_id[dialog.id[id]] = id;\n
                        }\n
                        return dialog.id[id];\n
                      }\n
             ).replace(/<l10n>(.*?)<\\/l10n>/ig,\n
                       function(fullString,translate)\n
                       {\n
                         return dialog._lc(translate) ;\n
                       }\n
             ).replace(/="_\\((.*?)\\)"/g,\n
                       function(fullString, translate)\n
                       {\n
                         return \'="\' + dialog._lc(translate) + \'"\';\n
                       }\n
             );\n
\n
  this.rootElem.innerHTML = html;\n
};\n
\n
Xinha.PanelDialog.prototype.show = function(values)\n
{\n
  this.setValues(values);\n
  this.editor.showPanel(this.rootElem);\n
};\n
\n
Xinha.PanelDialog.prototype.hide = function()\n
{\n
  this.editor.hidePanel(this.rootElem);\n
  return this.getValues();\n
};\n
\n
Xinha.PanelDialog.prototype.onresize   = Xinha.Dialog.prototype.onresize;\n
\n
Xinha.PanelDialog.prototype.toggle     = Xinha.Dialog.prototype.toggle;\n
\n
Xinha.PanelDialog.prototype.setValues  = Xinha.Dialog.prototype.setValues;\n
\n
Xinha.PanelDialog.prototype.getValues  = Xinha.Dialog.prototype.getValues;\n
\n
Xinha.PanelDialog.prototype.getElementById    = Xinha.Dialog.prototype.getElementById;\n
\n
Xinha.PanelDialog.prototype.getElementsByName = Xinha.Dialog.prototype.getElementsByName;

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2131</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>panel-dialog.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
