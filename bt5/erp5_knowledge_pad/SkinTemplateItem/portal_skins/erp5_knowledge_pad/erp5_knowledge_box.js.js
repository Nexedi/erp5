// global layout is saved here
var last_layout = '';

// current active pad relative url
var active_knowledge_pad_relative_url = '';
var active_knowledge_pad_title_dom_id = '';

// enable or disable integration with server
var is_knowledge_template_used = 0;

// dictionary of invisible gadgets
var invisible_gadgets={};

var create_default_knowledge_pad_script_id = "ERP5Site_createDefaultKnowledgePadListForUser";
var knowledge_box_edit_script_id = "KnowledgeBox_baseEdit";
var knowledge_pad_save_layout_script_id = "KnowledgePad_saveBoxColumnLayout";
var knowledge_pad_delete_box_script_id = "KnowledgePad_deleteBox";
var knowledge_box_toggle_script_id = "KnowledgeBox_toggleVisibility";
var knowledge_pad_rename_script_id = "ERP5Site_renameKnowledgePad";
var knowledge_pad_delete_script_id = "ERP5Site_deleteKnowledgePad";
var add_new_knowledge_pad_script_id = "ERP5Site_addNewKnowledgePad";
var knowledge_pad_as_json_script_id = "KnowledgePad_getPadAsJSON";
var add_new_gadget_form_id = "Base_viewGadgetListDialog";

function createCustomKnowledgePadOnServer(){
  $.ajax({url:create_default_knowledge_pad_script_id, 
          data:{mode: mode,
                default_pad_group: default_pad_group},
          success:function(data){window.location=cancel_url;}});
}

function showCreateDefaultKnowledgePadWarningMessage(){
  user_choice = confirm("In order to complete operation you must have your own tab on server instead of the default one which you are currently using and which you can not change.Is it OK to create new one for you now?");
  if (user_choice===true){
    createCustomKnowledgePadOnServer();}
}

function createCookie(name, value, days, path) {
  var expires = "";
  if (days){
    var date = new Date();
    date.setTime(date.getTime()+(days*24*60*60*1000));
    expires = "; expires="+date.toGMTString();}
  if (!path){path='/';}
  document.cookie = name+"="+value+expires+"; path="+path;
}

function updater(url, box_relative_url, dom_id, 
                 editable_mode, additionnal_request_params, field_prefix){
  /* Get content from server */
  request_params = {};
  additionnal_request_params = typeof(additionnal_request_params) != 'undefined' ? additionnal_request_params : [];

  // getting parameters for the request in the form's hidden inputs
  input_list = $("#" + dom_id).find("input");

  function extractHiddenInputs(index){
    element = $(this);
    type = element.attr("type");
    name = element.attr("name");
    value = element.val();
    is_list = name.substring(name.length, name.length - 5) == ":list";
    if(type == "hidden"){
      if(name == "gadget_form_id"){
        // turn 'gadget_form_id' into 'form_id'
        request_params["form_id"] = value;}
      else if(is_list){
        if(typeof(request_params[name]) == "undefined"){
          request_params[name] = new Array();}
        request_params[name].push(value);}
      else{
        // not list input
        request_params[name] = value;}
    }}
  
  input_list.each(extractHiddenInputs);

  // we can have a field_prefix which allows multiple gadgets within same HTML form
  if (field_prefix){
    $.each(request_params,  
         function (key, value){
           if (key.match("^"+field_prefix)){
             delete request_params[key];
             request_params[key.replace(field_prefix,'')] = value;
           }});
  }
  
  // getting parameters for request from the parameter additionnal_request_params
  $.each(additionnal_request_params,  
         function (key, value){request_params[key] = additionnal_request_params[key];});
         
  request_params["box_relative_url"] = box_relative_url;
  request_params["is_gadget_mode:int"] = 1; 
  request_params["editable_mode:int"] = editable_mode; 

  // set transperancy to show an activity is going on
  $("#" + dom_id).css("opacity", 0.5);
  $.ajax({url:url,
          data: request_params,
          success: handleServerSuccess,
          error: handleServerError,
          // it's important for Zope to have traditional way of encoding an URL
          traditional: 1});
      
  function handleServerSuccess(data, text_status, xhr){
    content_type = xhr.getResponseHeader('Content-Type');
    if(content_type.search("application/json")!=-1){
      // server returned JSON which may contain HTML & JavaScript
      html = data['body'];
      eval(data['javascript']);}
    else{
      /* server returned HTML */
      html = data;}
    $("#" + dom_id).html(html);
    $("#" + dom_id).css("opacity", 1.0);
  }
      
  function handleServerError(res){
    $("#" + dom_id).html("Server side error.");
    $("#" + dom_id).css("opacity", 1.0);
  }
}

function submitGadgetPreferenceFormOnEnter(event, 
                                           form_fields_main_prefix, 
                                           box_relative_url, 
                                           edit_form_id){
  /* This function can be used to submit gadget preferences form whenever
  an enter is pressed in form */
  if(event.keyCode == 13){submitSynchronousGadgetPreferenceForm(form_fields_main_prefix, 
                                                                box_relative_url, 
                                                                edit_form_id);}
}

function addHiddenInput(name, value){
  $("form").find('input[name="' + name + '"]').remove();
  $("form").append('<input type="hidden" name="' + name + '" value="' + value + '">');
}

function submitSynchronousGadgetPreferenceForm(
                                form_fields_main_prefix, 
                                box_relative_url,
                                edit_form_id){
  /* this will add respective gadget knowledge box relative url and
     gadget ERP5 preference form field_prefix (so multiple gadgets can 
     safely coexist in one HTML page with one HTML form */
  redirect_url = window.location.protocol + "//" + window.location.host + window.location.pathname;
  addHiddenInput("box_relative_url", box_relative_url);
  addHiddenInput("form_fields_main_prefix", form_fields_main_prefix);
  addHiddenInput("gadget_redirect_url", redirect_url);
  addHiddenInput("form_id", edit_form_id);
  clickSaveButton(knowledge_box_edit_script_id);
}

function submitAsynchronousGadgetPreferenceForm(
                                 form_dom_id, 
                                 view_form_url, 
                                 box_relative_url, 
                                 visual_block_dom_id, 
                                 form_fields_main_prefix,
                                 edit_form_id){
  /* Iterate over all possible form elements within edit form,
    collect them and send to server*/
  var request_str = "synchronous_mode:int=0&" + "box_relative_url=" + box_relative_url+ "&form_fields_main_prefix=" + form_fields_main_prefix + "&form_id="+edit_form_id + "&";
  
  //input tags
  $("#" + form_dom_id).find("input").each(
    function (index) {
      element = $(this);
      type = element.attr("type");
      name = element.attr("name");
      is_checked = element.attr("checked");
      value = element.val();
      if (type == "checkbox"){
        if (is_checked){request_str+=name + ":boolean=True&";}
        else {request_str+=name + ":boolean=False&";}}
      if (type == "radio" && is_checked){request_str+=name + "="+value+"&";}
      if (type == "text" || type == "password"){request_str+=name + "=" + value + "&";}
    } );
  
  // select tags
  $("#" + form_dom_id).find("select").each(
    function (index) {
      element = $(this);
      name = element.attr("name");
      is_multiple = element.attr("multiple");
      value = element.val();
      if (is_multiple){
        //support multifield selects in gadget edit form
        element.children("option").each(
          function (index) {
            option = $(this);
            if(option.attr("selected")){request_str+=element.attr("name") + '=' + option.val() + '&';}
          }); }
       else{request_str+=name + '=' + value + '&';} });
  
  // save form preferences to remote server
  $.ajax({url: knowledge_box_edit_script_id + "?" + request_str,
          dataType: "json",
          success: function (data){
                     if (data.validation_status){
                       // server side validation passed
                       updater(view_form_url, box_relative_url, visual_block_dom_id);
                       $("#" + form_dom_id).toggle();
                       // clean error messages
                       $("#" + form_dom_id + " span.error").remove();
                     }
                     else{
                       // server side validation failed show error message
                       $("#" + form_dom_id + " div.edit-form-content").html(data.content);
                     }
          } });
}

function updateServerBoxColumnLayout(event, ui){
  /* read columns structure from DOM  and save it to server */
  var columns_arr = new Array;
  var columns = $("div.portal-column");
  // sort alphabetically as it's required to get proper layout from DOM
  columns.sort(function(a, b) {
                 var compA = $(a).attr("id").toUpperCase();
                 var compB = $(b).attr("id").toUpperCase();
                return (compA < compB) ? -1 : (compA > compB) ? 1 : 0;});

  columns.each(function(column_index, column){
    column = $(this);
    var items_arr = new Array;
    column_items = column.find("div.block");
    column_items.each(function(box_index, box){
      items_arr[box_index] = column_items[box_index].id;});           
    columns_arr[column_index] = items_arr.join('|');});
  
  var layout = columns_arr.join("##");
  // .. and send it to server only if it's different
  if (layout!=last_layout){
    last_layout = layout;
    $.ajax({url: knowledge_pad_save_layout_script_id, 
            data: {user_layout: layout}});}
}

function showAddNewPadPopup(){
  $("#add_new_tab_dialog").toggle();
  // set focus on new Pad title after toggle effect is over 
  setTimeout("$('#new_pad_title').focus()", 500 );
}

function showRenamePadPopup(knowledge_pad_relative_url, knowledge_pad_title_dom_id){
  // set current active pad' url & title dom element id
  active_knowledge_pad_relative_url = knowledge_pad_relative_url;
  active_knowledge_pad_title_dom_id = knowledge_pad_title_dom_id;
  // init rename dialog input field to current active pad
  $("#new_knowledge_pad_title")[0].value = $("#"+knowledge_pad_title_dom_id)[0].innerHTML;
  // show rename dialog
  $("#rename_tab_dialog").toggle();
  // set focus on new Pad title after toggle effect is over 
  setTimeout("$('#new_knowledge_pad_title').focus()", 500);
}

function loadPadFromServer(pad_relative_url, selected_pad_dom_id, mode){
  /* Load Pad from server */
  //  show some animation
  $("#loading-wrapper").first().show();
  $.ajax({url: knowledge_pad_as_json_script_id, 
          data: {pad_relative_url: pad_relative_url,
                 mode: mode},
          dataType: "json",
          success: handleServerSuccess});
  // set old pad to not selected
  old_selected_pad = $("#tabs ul").children("li.tab_selected").first();
  old_selected_pad.removeClass("tab_selected");
  old_selected_pad.addClass("tab");
  
  pad_actions = old_selected_pad.children("div.pad-actions").first();
  pad_actions.hide();
   
  // set new selected pad class 
  new_selected_pad = $("#" + selected_pad_dom_id).first();
  new_selected_pad.addClass("tab_selected");
  
  // enable "settings" for this pad and hide instant switch
  pad_actions = new_selected_pad.children("div.pad-actions").first();
  pad_actions.show();
  
  // set new active pad
  active_knowledge_pad_relative_url = pad_relative_url;
  
  // update "Add Gadget" link
  current_url = $("#add-gadgets").attr("href");
  new_url = current_url.substring(0, current_url.indexOf("active_pad_relative_url=")+24)+active_knowledge_pad_relative_url;
  $("#add-gadgets").attr("href", new_url);
  
  //function metadataFetchFailed(meta){}
  function handleServerSuccess(data){
    body = data.body;
    javascript = data.javascript;
    body_element = $("#pad-body-wrapper")[0];
    body_element.innerHTML = body;
    // init new Pad
    initialize();
    // execute JS code provided by server
    eval(javascript);
    // give some timeout as we can be sometimes two fast loading a tab
    setTimeout("$('#loading-wrapper').first().hide();", 250 );}
}

function addPadOnServerOnEnter(event, mode, cancel_url){
  /* Catch and submit form when ENTER is pressed */
  if(event.keyCode == 13){
    addPadOnServer(mode, cancel_url);
    return false;}
}

function addPadOnServer(mode,
                        cancel_url){
  /* add pad on server */
  pad_title_value = $("#new_pad_title").first().val();
  window.location = add_new_knowledge_pad_script_id + "?redirect_url=" + cancel_url + "&mode=" + mode + "&pad_title=" + pad_title_value;
}

function removeKnowledgePadFromServer(knowledge_pad_relative_url, mode){
  /* remove pad from server*/
  if (is_knowledge_template_used){
    showCreateDefaultKnowledgePadWarningMessage();}
  else{
    var user_choice = true;
    user_choice = confirm("Are you sure you want to remove this pad from your home?");
    if (user_choice===true){
      location.href=knowledge_pad_delete_script_id + "?knowledge_pad_relative_url=" + knowledge_pad_relative_url+"&mode="+mode;} }
}

function renameKnowledgePadToServerOnEnter(event){
  if(event.keyCode == 13){
    renameKnowledgePadToServer();
    return false;}
  return true;
}

function renameKnowledgePadToServer(){
  if (is_knowledge_template_used){
    showCreateDefaultKnowledgePadWarningMessage();}
  else{
    // rename it locally and update server asynchonously
    title_element = $("#"+active_knowledge_pad_title_dom_id).first();
    input_element = $("#new_knowledge_pad_title");
    var knowledge_pad_title = input_element.val();
    title_element.html(knowledge_pad_title);
    $.ajax({url: knowledge_pad_rename_script_id, 
            data: {knowledge_pad_relative_url: active_knowledge_pad_relative_url,
                   knowledge_pad_title: knowledge_pad_title}});                                           
  }
  $("#rename_tab_dialog").toggle();
}

function initialize(){
  // initialize sortable columns
  if (is_knowledge_template_used===0){
    // allow drag and drop only if we are dealing with a pad we can modify
    sortable_list = $("div.portal-column");
    function makeSortables(index){
      element = $(this);
      if (element.attr("class") == "portal-column"){
        // eliminate undraggable columns by checking exact match
        element.sortable({handle: "h3.handle",
                          connectWith: sortable_list,
                          placeholder: "block-hover",
                          forcePlaceholderSize: 1,
                          opacity: 0.8,
                          containment: "document",
                          delay: 100,
                          stop: updateServerBoxColumnLayout});} }
    if (sortable_list!==null) sortable_list.each(makeSortables);
  }

  // enable show/hide tabs
  gadgets_tabs = $("#tabs");
  gadgets_tabs_switcher = $("#tabs_switcher");  
  add_gadget = $("#add_new_gadget_link");
  
  function toggleTabNavigation(){
    /* Toggle tabs navigation */
    var is_tabs_visible=0;
    if($("#tabs").css("display")!="block"){
      is_tabs_visible=1;
      $("#tab_switcher_visible").show();
      $("#tab_switcher_hidden").hide();}
    else{
      $("#tab_switcher_visible").hide();
      $("#tab_switcher_hidden").show();}
    $("#tabs").toggle();
    createCookie("is_tabs_visible", is_tabs_visible, 365); }
 
  function bindGadgetHandlers(index, box){
    /* Bind all gadgets handlers */
    box = $(this);
    var edit = box.find("a.block-edit-form").first();
    var edit_form = box.find("div.edit-form").first();
    var remove = box.find("a.block-remove").first();   
    var minimize = box.find("a.block-minimize").first(); 
    var minimize_wrapper = box.find("div.minimize_wrapper").first(); 
    if(minimize){
      minimize.unbind("click");
      minimize.bind("click", function (){
        if (is_knowledge_template_used){showCreateDefaultKnowledgePadWarningMessage();}
        else{
          minimize_wrapper.toggle();
          box_id = box.attr("id");
          js_dom_id = box_id + "_content";
          js_code = invisible_gadgets[js_dom_id];
          if (js_code!=undefined){
            eval(js_code);
            // gadget is now visible, i.e. no need to query server just toggle locally dom
            delete invisible_gadgets[js_dom_id];}
           $.ajax({url: knowledge_box_toggle_script_id, 
                   data: {box_relative_url: box_id}});
           }
        });}

    if(edit){
      edit.unbind("click");
      edit.bind("click", function (){
        if (is_knowledge_template_used){showCreateDefaultKnowledgePadWarningMessage();}
        else{edit_form.toggle();}});}
        
    if(remove){
      remove.unbind("click");
      remove.bind("click", function (){
        if (is_knowledge_template_used){showCreateDefaultKnowledgePadWarningMessage();}
        else{
          user_choice = confirm("Are you sure you want to remove this gadget from your personalized page?");
          if (user_choice===true){
            box_id = box.attr("id");
            box.toggle();
            $.ajax({url: knowledge_pad_delete_box_script_id, 
                    data: {box_relative_url: box_id}});}
        }});}
  }
  
  // tabs navigation
  if(gadgets_tabs_switcher){
    gadgets_tabs_switcher.unbind("click");
    gadgets_tabs_switcher.bind("click", toggleTabNavigation);}
  
  // for each box (gadget) add respective event handlers
  gadget_list = $("div.block");
  if (gadget_list!==null){
    gadget_list.each(bindGadgetHandlers);
    // when dom is loaded we need to remove all gadget's scripts otherwise currently when a gadget is moved
    // its HTML is getting executed again, thus making unecessary calls to server, etc ...
    gadget_list.each(
      function (index, box){  $(this).find("script").remove();});
  }
}

// call function after load of document
$(document).ready(initialize);