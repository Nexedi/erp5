function callBeforeRequest(type){
  switch(type){
    case 1:
      message = "Loading Events...";
      break;
    case 2:
      message = "Adding Event...";
      break;
    case 3:
      message = "Removing Event...";
      break;
    case 4:
      message = "The request is being processed ...";
      break;
    default: break;
  }
  $("#errorpannel").hide();
  $("#loadingpannel").html(message).show();
}

function callAfterRequest(type){
  switch(type){
    default:
      $("#loadingpannel").hide();
      break;
  }
}

function callOnError(type, data){
  $("#errorpannel").show();
}

function Edit(data){
  var url ="WebSection_newEvent";
  $("div#new_event_dialog").dialog({
    title: "Update Event",
    buttons: {
      "Save": function(){
        var data = $("form#create_new_event").serializeArray();
        var dataHash = {};
        for (var i=0; i<data.length; i++)
          dataHash[data[i].name] = data[i].value;
        start_date = dataHash.start_date_month + "/" + 
                    dataHash.start_date_day + "/" + 
                    dataHash.start_date_year + " " + 
                    dataHash.start_date_hour + ":" + 
                    dataHash.start_date_minute;
  
        stop_date = dataHash.stop_date_month + "/" + 
                    dataHash.stop_date_day + "/" + 
                    dataHash.stop_date_year + " " + 
                    dataHash.stop_date_hour + ":" + 
                    dataHash.stop_date_minute;

        var paramList = [{name : 'CalendarEndTime', 'value': stop_date},
                         {name : 'event_portal_type', 'value': dataHash.portal_type},
                         {name : 'CalendarStartTime', 'value': start_date},
                         {name : 'title', 'value': dataHash.title},
                         {name : 'request_type', 'value': 'update'},
                         {name : 'event_id', 'value': $("input#event_id").attr("value")},
                         {name : 'event_text_content', 'value': dataHash.event_text_content}];

        $.post("Base_updateCalendarEventList", paramList, function(){
                $("div#new_event_dialog").dialog("close");
                $("div#showreflashbtn.fbutton").click();
        });
      }
    }
  });
  $("div#new_event_dialog").load(url, {}, function(){
    $("form#create_new_event").append("<input type='hidden' id='event_id'/>");
    $("input#event_id").attr("value", data[9]);
    $("form#create_new_event select").val(data[10]);
    $("textarea[name='event_text_content']").val(data[11]);
    $("input[name='title']").attr("value", data[1]);
    $("input.start_date_field[name='start_date_year']").attr("value", data[2].getFullYear());
    $("input.start_date_field[name='start_date_month']").attr("value", (parseInt(data[2].getMonth(),10) + 1));
    $("input.start_date_field[name='start_date_day']").attr("value", data[2].getDate());
    $("input.start_date_field[name='start_date_hour']").attr("value", data[2].getHours());
    $("input.start_date_field[name='start_date_minute']").attr("value", data[2].getMinutes());

    $("input.stop_date_field[name='stop_date_year']").attr("value", data[3].getFullYear());
    $("input.stop_date_field[name='stop_date_month']").attr("value", (parseInt(data[3].getMonth(),10) + 1));
    $("input.stop_date_field[name='stop_date_day']").attr("value", data[3].getDate());
    $("input.stop_date_field[name='stop_date_hour']").attr("value", data[3].getHours());
    $("input.stop_date_field[name='stop_date_minute']").attr("value", data[3].getMinutes());
  });
  $("div#new_event_dialog").dialog('open');
}

function View(data){
  var str = "";
  $.each(data, function(i, item){
    str += "[" + i + "]: " + item + "\n";
  });
  alert(str);
}

function Delete(data, callback){
  hiConfirm("Are You Sure to Delete this Event", 'Confirm', function(r){ r && callback(0);});
}

function submitEventOnEvent(event){
  var keynum;
  if(window.event){
    keynum = event.keyCode;
  }
  else if(event.which){
    keynum = event.which;
  }
  if (keynum == 13){
    createNewEvent();
  }  
}

function createNewEvent(){
  $.post("EventModule_createNewEvent",
    $("form#create_new_event").serialize(), function(){
      $("div#new_event_dialog").dialog("close");
      $("div#showreflashbtn.fbutton").click();
  });
}

function createFieldToInsertOnDialog(){
  return "<th class='cb-key'>Event Type</th>" + 
         "<td class='cb-value'><select name='portal_type'>" +
         "<option>Acknowledgement</option>" +
         "<option>Fax Message</option>" + 
         "<option>Letter</option>" +
         "<option>Mail Message</option>" +
         "<option>Note</option>" + 
         "<option>Phone Call</option>" +
         "<option>Short Message</option>" +
         "<option>Site Message</option>" + 
         "<option>Visit</option>" +
         "<option>Web Message</option>" +
         "</select></td>";
}

i18n.xgcalendar.content = "Title";
i18n.xgcalendar.location = "Event Id";
i18n.xgcalendar.participant = "Event Type";
i18n.xgcalendar.repeat_event = "Description";
i18n.xgcalendar.event = "Title";

$(document).ready(function() {     
  var DATA_FEED_URL = "Base_updateCalendarEventList";
  var op = {
    view: "week",
    showday: new Date(),
    EditCmdhandler:Edit,
    DeleteCmdhandler:Delete,
    weekstartday: 0,
    ViewCmdhandler:View,
    onBeforeRequestData: callBeforeRequest,
    onAfterRequestData: callAfterRequest,
    onRequestDataError: callOnError,
    autoload:true,
    url: DATA_FEED_URL + "?request_type=list",
    quickAddUrl: DATA_FEED_URL + "?request_type=add",
    quickUpdateUrl: DATA_FEED_URL + "?request_type=update",
    quickDeleteUrl: DATA_FEED_URL + "?request_type=remove",
    loadFieldOnDialog: createFieldToInsertOnDialog 
  };
  var $dv = $("#calhead");
  var _MH = document.documentElement.clientHeight;
  var dvH = $dv.height() + 2;
  op.height = _MH - dvH;
  op.eventItems = [];
  $("#gridcontainer").bcalendar(op).BcalGetOp();
  $("#caltoolbar").noSelect();
  //to show day view
  $("#showdaybtn").click(function(e) {
    $("div.toolbar-listview, div.event-listview").remove();
    $("#caltoolbar div.fcurrent").each(function() {
      $(this).removeClass("fcurrent");
    });
    $(this).addClass("fcurrent");
    var optionList = $("#gridcontainer").swtichView("day").BcalGetOp();
    $("div#display-datetime span#text-datetime").text(optionList.datestrshow);
  });
  //to show week view
  $("#showweekbtn").click(function(e) {
    $("div.toolbar-listview, div.event-listview").remove();
    $("#caltoolbar div.fcurrent").each(function() {
      $(this).removeClass("fcurrent");
    });
    $(this).addClass("fcurrent");
    var optionList = $("#gridcontainer").swtichView("week").BcalGetOp();
    $("div#display-datetime span#text-datetime").text(optionList.datestrshow);
  });
  //to show month view
  $("#showmonthbtn").click(function(e) {
    $("div.toolbar-listview, div.event-listview").remove();
    $("#caltoolbar div.fcurrent").each(function() {
      $(this).removeClass("fcurrent");
    });
    $(this).addClass("fcurrent");
    var optionList = $("#gridcontainer").swtichView("month").BcalGetOp();
    $("div#display-datetime span#text-datetime").text(optionList.datestrshow);
  });
  $("#showreflashbtn").click(function(e){
    $("#gridcontainer").reload();
  });          
  //Add a new event
  $("span.addcal").click(function() {
    var url ="WebSection_newEvent";
    var date = new Date();
    $("div#new_event_dialog").load(url, {}, function(){
      $("input.start_date_field[name='start_date_month'], input.stop_date_field[name='stop_date_month']").attr("value", date.getMonth()+1);
      $("input.start_date_field[name='start_date_day'], input.stop_date_field[name='stop_date_day']").attr("value", date.getDate());
      $("input.start_date_field[name='start_date_hour'], input.stop_date_field[name='stop_date_hour']").attr("value", date.getHours());
      $("input.start_date_field[name='start_date_minute'], input.stop_date_field[name='stop_date_minute']").attr("value", date.getMinutes());
    });
    $("div#new_event_dialog").dialog("open");
  });
  //go to today
  $("#showtodaybtn").click(function() {
    var optionList = $("#gridcontainer").gotoDate().BcalGetOp();
    $("div#display-datetime span#text-datetime").text(optionList.datestrshow);
  });
  //previous date range
  $("#sfprevbtn").click(function() {
    var optionList = $("#gridcontainer").previousRange().BcalGetOp();
    $("div#display-datetime span#text-datetime").text(optionList.datestrshow);
  });
  //next date range
  $("#sfnextbtn").click(function() {
    var optionList = $("#gridcontainer").nextRange().BcalGetOp();
    $("div#display-datetime span#text-datetime").text(optionList.datestrshow);
  });
  $("div#new_event_dialog").dialog({
    autoOpen: false,
    height: 248,
    width: 410,
    modal: true
  });
  $("#datepicker").datepicker({
    onSelect: function(dateText, inst){
      var dateList = dateText.split("/");
      var month = dateList[0] - 1;
      var day = dateList[1];
      var year = dateList[2];
      var optionList = $("#gridcontainer").gotoDate(new Date(year, month, day)).BcalGetOp();
      $("div#display-datetime span#text-datetime").text(optionList.datestrshow);
     }
  });
  $("input#submit-search").click(function(event){
    event.preventDefault();
    if ($("input[name='searchable-text']").val() === "")
      return false;
    $("div#dvCalMain.calmain div#gridcontainer").css("background", "none repeat scroll 0 0 #FFFFFF");
    $("div#dvwkcontaienr.wktopcontainer").remove();
    $("div#gridcontainer div#dvtec.scolltimeevent").remove();
    if (document.getElementById("blank-result") !== null){
      $("div#blank-result").remove();
    }
    $("div#gridcontainer div.event-listview,div#gridcontainer div.toolbar-listview").remove();
    var tableList = Array();
    tableList.push("<div class='toolbar-listview'>",
                   "<table width='100%' cellspacing='0' cellpadding='2'>",
                   "<tbody>",
                   "<tr><td>",
                   "<a id='back-calendar' href='#'> « Back to Calendar</a>",
                   "</td><td id='resultview'>Results:</td>",
                   "</tbody></table></div>");
    tableList.push("<div class='event-listview'>");
    tableList.push("<table width='100%' cellspacing='0' cellpadding='2'><tbody>");
    text = $("input[name='searchable-text']").val();
    paramList = [{name: "request_type", value: "list"}];
    if (text !== "")
      paramList.push({name: "SearchableText", value: text});
    $.ajax({
           url:"Base_updateCalendarEventList",
           dataType: "json",
           data : paramList,
           success: function(data){
             var eventTableList = Array();
             var eventList = data.events;
             var currentDate = new Date();
             for (var i = 0; i < eventList.length; i++){
               var eventDate = new Date(eventList[i][2]);
               var hourSymbol = "am";
               if (eventDate.getMonth() == currentDate.getMonth() && eventDate.getDate() == currentDate.getDate()){
                 eventTableList.push("<tr id='today-event'>");
               }
               else {
                 eventTableList.push("<tr>");
               }
               var dateSplitted = eventList[i][2].split(" ");
               if (eventDate.getHours() >= 12)
                 hourSymbol = "pm";
               eventTableList.push("<td id='event-date'>",
                                   dateSplitted[0],
                                   "</td>");
               eventTableList.push("<td id='time-range'>", 
                                   dateSplitted[1] + hourSymbol,
                                   "</td>");
               eventTableList.push("<td>", eventList[i][1]);
               eventTableList.push("</td></tr>");
             }
             $("div.event-listview tbody").append(eventTableList.join(""));
             $("td#resultview").append("<b>" + " " +
                                       $("div.event-listview tbody tr").length + 
                                       "</b>" + " to " + 
                                       "<b>" + text + "</b>");
             $("div.event-listview tbody td#event-date").click(function(){
               op.showday = new Date($(this).text());
               op.view = "day";
               $("#gridcontainer").bcalendar(op).BcalGetOp();
             });
             if ($("div.event-listview tr").height() > 0){
               $("div#gridcontainer").css("height",
                 $("div#gridcontainer table tbody tr").length*$("div.event-listview tr").height() + "px");
             } else {
                $("div#gridcontainer").css("height", "54px").append("<div id='blank-result'>No Results</div>");
             }
           }
    });
    tableList.push("</tbody></table></div>");
    $("div#gridcontainer").append(tableList.join(""));
    return true;
  });
  $("img[alt='calendar_logo_box']").click(function(){
    window.location.reload();
  });
});

$("div#new_event_dialog").ready(function(){
  $("div#new_event_dialog").dialog({
    title: "Create New Event",
    autoOpen: false,
    buttons: {
      "Create": createNewEvent
      }
  });
});

window.onload = function(){
  $("div#dvCalMain.calmain").parent().css("padding", "0 0 0 1px");
};