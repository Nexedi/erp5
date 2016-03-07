function loadEmailFormActions(){
  $("button#discard-mail").click(function(){
    window.location.reload();
  });
  $("span#add-cc-field").click(function(){
    $(this).hide();
    $("tr#cc").show();
  });
  $("span#add-bcc-field").click(function(){
    $(this).hide();
    $("tr#bcc").show();
  });
}

function saveEmailThread(event){
  event.preventDefault();
  var formData = new Array();
  $("div.compose-mail-page textarea, div.compose-mail-page input").each(function(){
    formData.push({name: $(this).attr("id"), value: $(this).attr("value")});
  });
  formData.push({name: "action", value: event.currentTarget.id});
  var divMail = $("div.compose-mail-page");
  var eventId = divMail.data("event_uid") != undefined ? divMail.data("event_uid") : "";
  formData.push({name: "event_id", value: eventId});
  $.ajax({
     type: "post",
     url: "ERP5Site_createNewEmailThread",
     data: formData,
     mediaType: "json",
     success: function(data){
       if (event.currentTarget.id == "send-mail"){
         $("div.compose-mail-page").removeDate("event_id");
         var baseUrl = window.location.href.split("?")[0];
         window.location.href = baseUrl + "?reset:int=1";
       }
       if (event.currentTarget.id == "save-mail"){
         $("div.compose-mail-page").data("event_uid", data);
       }
     }
  });
}

$().ready(function(){
  var baseUrl = window.location.href.split("?")[0];
  $("button#compose-mail").click(function(event){
    event.preventDefault();
    $("div.main-right fieldset.widget").hide();
    $("div.main-right").css("background-color", "#BBCCFF");
    $("div.main-right").load("EmailThread_formView", {}, function(){
      loadEmailFormActions();
      $("button#save-mail, button#send-mail").click(saveEmailThread);  
    });
  });
  $("img[alt='mail_logo_box']").click(function(){
    window.location.href = baseUrl + "?reset:int=1";
  });
  $("input#submit-search").click(function(event){
    event.preventDefault();
    var text = $("input[name='searchable-text']").attr("value").replace(/\ /g,"%20");
    window.location.href = baseUrl + "?SearchableText=" + text;
  });
  $("input[name='searchable-text']").keypress(function(event){
    (event.which == 13) ? $("input#submit-search").click() : null;
  });
  $("div.listbox-body table.listbox td.listbox-table-data-cell a").click(function(event){
    event.preventDefault();
    var emailThreadUId = $(this).parent().parent().find("input").attr("value");
    var emailUid = [{name: "email_thread_uid", value: emailThreadUId}];
    $.ajax({
       type: "post",
       url: "ERP5Site_loadEmailThreadData",
       data: emailUid,
       mediaType: "json",
       success: function(data){
         data = jQuery.parseJSON(data);
         $("div.main-right fieldset.widget").hide();
         $("div.main-right").css("background-color", "#BBCCFF");
         $("div.main-right").load("EmailThread_formView", {}, function(){
           if (data.state != "draft"){
             $("button#discard-mail").hide();
           }
           $("button#save-mail, button#send-mail").click(saveEmailThread);
           $(this).ready(function(){
             (data.cc !== null) ? $("textarea#cc").attr("value", data.cc) : null;
             (data.bcc !== null) ? $("textarea#bcc").attr("value", data.bcc) : null;
             (data.to !== null) ? $("textarea#to").attr("value", data.to) : null;
             (data.text_content !== null) ? $("textarea#text-content").attr("value", data.text_content) : null;
             (data.subject !== null) ? $("input#subject").attr("value", data.subject) : null;
             (data.id !== null) ? $("div.compose-mail-page").data("event_id", data.id) : null;
             loadEmailFormActions();
           });
         });
       }
    });
    $("div.compose-mail-page").data("event_uid", emailThreadUId);
  });
});