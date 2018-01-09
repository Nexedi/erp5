return context.PostModule_createHTMLPost(
  follow_up_value=follow_up_value,
  predecessor=predecessor,
  data="<p>" + data.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("  ", " &nbsp;").replace("\n", "<br/>") + "</p>",
)
