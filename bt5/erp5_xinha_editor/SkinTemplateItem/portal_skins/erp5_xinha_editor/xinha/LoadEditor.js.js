var xinha_plugins = ["UnsavedChanges"];

var xinha_editors =
[
  'my_text_content',
];

function xinha_init()
{
  if(!Xinha.loadPlugins(xinha_plugins, xinha_init)) return;
  var xinha_config = new Xinha.Config();
  xinha_config.pageStyleSheets = ["xinha_custom.css"];
  xinha_editors = Xinha.makeEditors(xinha_editors, xinha_config, xinha_plugins);
  Xinha.startEditors(xinha_editors);
}
Xinha.addOnloadHandler(xinha_init);