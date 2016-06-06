$(document).ready(function() {
  generateLink("a.document_bookmark",$("title").html(), $("a.document_link").attr("href"));

  $("span.headline").click(function(){
    if ($("#content").hasClass("twocolumns"))
      contentMaximise();
    else
      contentMinimise();
  });
  
  $("span.headline").css("cursor","pointer");
  
});