$.extend({
  getUrlVars: function(){
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
      hash = hashes[i].split('=');
      vars.push(hash[0]);
      vars[hash[0]] = hash[1];
    }
    return vars;
  },
  getUrlVar: function(name){
    return $.getUrlVars()[name];
  }
});

var checkState_call_count = 0
function checkState(message){
  checkState_call_count += 1
  var checkState_call_str = ["",".","..","..."]
  $("#transition-message").html(message+checkState_call_str[checkState_call_count%4])
  $.get("Document_getPropertiesAsJSON", {}, function(data, textStatus, XMLHttpRequest){
    if (textStatus == "timeout" || textStatus == "error" || textStatus == "parsererror"){
      $("title").html("Error during conversion");
      $("#transition-message").html("An error occurs during the process. Please resend your file");
    }
    else {
      //TextStatus is "notmodified","success"
      json = jQuery.parseJSON( data );
      if ((json.processing == "converted") || (json.processing == "conversion_failed") || (json.processing == "empty")){
        $("title").html("Finish");
        $("#transition-message").html("The conversion process is finish. You will be redirect in 3 seconds.");
        setTimeout("$(location).attr('href','"+json.permanent_url+"')", 3000);
      }
      else {
        if (json.processing == "process_error") {
          $("title").html("Error during conversion");
          $("#transition-message").html("An error occurs during the process. Please resend your file");
        }
        else {
          setTimeout("checkState('"+message+"')", 500);
        }
      }
    }
  });
}

function createBookmark(title,url) {
  if ($.browser.mozilla == true) {
    window.sidebar.addPanel(title, url, "");
  } 
  else {
    if($.browser.msie == true) {
      window.external.AddFavorite( url, title);
    }
    else {
      alert('Please use CTRL + D to bookmark this website.'); 
    }
  }
}
 
function generateLink(id, title, url){
  var link_title ;
  if ($.browser.msie == true) {
    link_title = "Add to Favorites";
  } else  if ($.browser.mozilla == true) {
    link_title = "Bookmark Page";
  } else if ($.browser.opera== true) { 
    link_title = "Add Bookmark" ;
  } else {
    link_title = "Add to favorites";
  }
  
  var link = $(id);
  link.attr("title",link_title);
  link.html(link_title);
  link.attr("href","javascript:createBookmark(\""+title+"\",\""+url+"\");");
}

function contentMaximise(){
  $("#content").removeClass("twocolumns");
  $("#sidebar").hide();
}

function contentMinimise(){
  $("#content").addClass("twocolumns");
  $("#sidebar").show();
}