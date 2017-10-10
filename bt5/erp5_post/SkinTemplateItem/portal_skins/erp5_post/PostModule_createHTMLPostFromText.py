return context.PostModule_createHTMLPost(
  follow_up,
  predecessor,
  "<p>" + data.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("  ", " &nbsp;").replace("\n", "<br/>") + "</p>",
  file,
)
