$.fn.outerHTML = function() {
    $t = $(this);
    if( "outerHTML" in $t[0] )
    { return $t[0].outerHTML; }
    else
    {
        var content = $t.wrap('<div></div>').parent().html();
        $t.unwrap();
        return content;
    }
};

function getCurrentObjectUrl(){
  return window.location.href.split("?")[0];
}

function toogleLoading(is_toogle, _message) {
  var loading_wrapper;
  if (is_toogle) {
    loading_wrapper = $("#loading-wrapper").first();
    toogleLoading.prototype.old_loading_message = loading_wrapper.find('p')[0].textContent;
    loading_wrapper.find('p')[0].textContent = _message;
    loading_wrapper.show();
  }
  else {
    loading_wrapper = $("#loading-wrapper").first();
    loading_wrapper.hide();
    loading_wrapper.find('p')[0].textContent = toogleLoading.prototype.old_loading_message;
  }
}

function changeLanguage(language){
  $.ajax({
     url: "WebSite_changeLanguage?language=" + language,
     async: false,
     success: function(){
       window.location.reload();
     }
  });
}

function getPortalTypeFromContext(){
  var response = $.ajax({
                    url: "getPortalType",
                    method: "GET",
                    async: false
                }).responseText;
  return response;
}

function getUrlParameterList(){
  var argumentList = {};
  var resultList = window.location.href.split("?");
  if (resultList.length > 1) {
    var parameterList = resultList[1].split("&");
    for (var i=0;i<parameterList.length;i++){
      parameter = (parameterList[i].replace(":int","")).split("=");
      argumentList[parameter[0]] = parameter[1];
    }
  }
  return argumentList;
}

function getObjectPropertyValue(method_name){
  return $.ajax({
            url: method_name,
            async: false
         }).responseText;
}

function showNotImplementedMessage(tag){
  $(tag).fadeIn(500).delay(1000).fadeOut(800);
}

function updateWebPage(){
  var parameterList = getUrlParameterList();
  url = "WebPage_updateWebDocument?document_path=" +
         parameterList.document_path;
  $.get(url, {}, function(data, textStatus, XMLHttpRequest){
    response = jQuery.parseJSON(data);
    if (response.status != 200){
      setTimeout(updateWebPage(), 1500);
    }
    else {
      clearTimeout();
      window.location = getCurrentObjectUrl() + "?editable_mode:int=1";
    }
  });
}

function checkConversion(){
  $.get("Base_getDocumentConversionState?path=" + parameterList.document_path, {},
                                               function(data, textStatus, XMLHttpRequest){
     status = jQuery.parseJSON(data);
     switch (status) {
      case "converted":
        $("a#loading_message").text("Opening your Document...");
        clearTimeout();
        setTimeout(updateWebPage(), 1000);
        break;
      case "conversion_failed":
        clearTimeout();
        $("a#loading_message").text("Problems to convert your document...");
        setTimeout(window.location.href = window.location.href.match("^http.*\/ung")[0], 3000);
        break;
      default:
        setTimeout(checkConversion(), 1500);
        break;
     }
  });
}

function setObjectPropertyValue(method_name, value, parameter){
  $.ajax({
        type: "POST",
        url: method_name,
        data: parameter + "=" + value,
        async: false
  });
  return true;
}

function changeCheckBoxValue(value){
  $("table.listbox tbody tr td.listbox-table-select-cell input").each(function(){
    this.checked = value;
  });
}

function waitCreateUNGUser(paramStr){
  $.get("ERP5Site_checkIfUserExist?" + paramStr, {}, function(data, textStatus, xhr){
     data = jQuery.parseJSON(data);
     if (data.response === true){
       clearTimeout();
       window.location.reload();
     }
     else {
       setTimeout(waitCreateUNGUser(paramStr), 3500);
     }
  });
}

function displayFormMessage(message, delay){
  $("td#form-message").text(message);
  $("td#form-message").fadeIn(300).delay(delay).fadeOut(1000);
}

function displayLoginForm(){
  var tagToHide = "a.ung_docs, img[alt='calendar_logo_box']," +
                  "table#create-new-user, img[alt='mail_logo_box']" +
                  ", div.navigation";
  $(tagToHide).hide();
  $("div.header-left div.field input, div.main-right, div.main-left").hide();
  $.get("WebSection_loginDialog", function(data){
    // set body
    $("div.header-left fieldset.widget").append("<p>" + data + "</p>");
    // fix 'ENTER' key to form submit on firefox browser
    $("//input[id='name'], //input[id='password']").bind('keyup', function(e) {
      if (e.which == 13) {
          $('form#main_form').submit();
          e.preventDefault();
      }
    });
    // set "new account form" behaviour
    $("td#new-account-form").click(function(event){
      $("table#field_table, table#new-account-table").hide();
      $("table#create-new-user input[type='text'], table#create-new-user input[type='password']").each(function(){
        $(this).attr("value", "");
      });
      $("table#field_table, table#new-account-table, table#create-new-user").css("width", "100%");
      $("table#create-new-user").show();
      $("td#back-login").click(function(event){
        reloadLoginPage(event);
      });
      $("form#create-user").submit(function(event){
        event.preventDefault();
        var formHash = {};
        var paramList = $("form#create-user").serializeArray();
        for (var i=0; i < paramList.length; i++){
          formHash[paramList[i].name] = paramList[i].value;
        }
        if (formHash.password != formHash.confirm){
          displayFormMessage("Please confirm your password correctly..", 3500);
          return false;
        }
        $.getJSON('ERPSite_createUNGUser?' + $("form#create-user").serialize(), function(response){
          if (response === null){
            displayFormMessage(formHash.login_name + " is not available, please try another...", 3500);
            return false;
          }
          else {
            displayFormMessage("The user " + formHash.login_name + " will be created in few seconds...", 8000);
            var paramStr = "reference=" + formHash.login_name;
            setTimeout(waitCreateUNGUser(paramStr), 2000);
          }
          return true;
        });
        return true;
      });
    });
  });
}

function reloadLoginPage(event){
  event.preventDefault();
  if ($("div#main-content").html() === null){
    displayLoginForm();
  }
  if ($("table#create-new-user").css("display") != "none"){
    $("table#field_table, table#new-account-table, table#create-new-user").css("width", "78%");
    $("table#create-new-user").hide();
    $("table#field_table, table#new-account-table").show();
  }
}

function displayDocumentTitle(title){
  var document_title = title;
  document_title === null ? document_title = getObjectPropertyValue("getTitle"): null;
  if (document_title.length > 30){
    $("a[name='document_title']").html(document_title.substring(0,30) + "...");
  }
  else{
    $("a[name='document_title']").html(document_title);
  }
}

// XXX: refactor to upgrade performance of 'updateListboxSelection' function
function updateListboxSelection() {
  var data_params = $('form#main_form').serializeArray();
  $('input[name="knowledge_pad_module_ung_knowledge_pad_ung_docs_listbox_content_listbox_uid:list"]').each(function() {
      data_params.push({
        'name': 'listbox_uid:list',
        'value': this.value
      });
    });
  $.ajax({
        async: false,
        type: 'POST',
        url: 'Base_updateListboxSelection',
        data: $.param(data_params)
  });
}

$().ready(function(){
  $("p.clear").remove();
  if ($("a#login").html() !== null){
    displayLoginForm();
    return 0;
  }
  if ($("div.gadget-column").length === 0) {
    parameterList = getUrlParameterList();
    if (parameterList.hasOwnProperty("upload_document") === true){
      $("a[name='document_title'], a[name='document_state'], div.header-right, div.content").hide();
      $("a#loading_message").show();
      setTimeout(checkConversion(), 1000);
    }
    else {
      switch (getPortalTypeFromContext()) {
        case "Web Page":
          $("div.content").css({"position":"fixed", "bottom": "0px",
                                "left": "0px", "right": "0px"});
          $("div.content").css({"top": "5em"});
          break;
        case "Web Table":
          $("div.content").css({"position":"fixed", "bottom": "0px",
                                "left": "0px", "right": "0px"});
          $("div.content").css({"top": "6em"});
          $.getJSON("Base_getPreferencePathList", function(data){
            var ungPreferencePath = data.preference;
            $.get(ungPreferencePath + '/getPreferredThemeSheetEditor', function(data){
              link = $("<link>");
              link.attr("id", "dynamic_css");
              link.attr({type: 'text/css', rel:'stylesheet', href:data});
              $("head").append(link);
            });
          });
          break;
        default: break;
      }
      displayDocumentTitle(null);
    }
  }
  $("input#upload").click(function(event){
    event.preventDefault();
    $("#upload_document").dialog("open");
  });
  $("tbody tr td.listbox-table-domain-tree-cell a").each(function(){
    if ($(this).text().length == 16){
      $(this).css("padding-right", "82px");
    }
    if ($(this).text().length > 16){
      $(this).css("padding-right", "24px");
    }
  });

  if ($("div.listbox-domain-tree-container").length < 1) {
    $("div.action_menu ul li a").click(function(event){
      event.preventDefault();
      herfList = this.getAttribute("href").split("?");
      action_name = herfList[herfList.length-1].split("=")[1];
      $.ajax({
             url: "Base_changeWorkflowState",
             data: "action_name=" + action_name,
             success: function(){
               window.location.reload();
             }
      });
    });
    if ($("a[name='document_state']").text() == "Draft") {
      $("div.action_menu li ul").append("<li><a id='share_document' href='#'>" +
                                        "<h6>Share this Document</h6></a></li>");
      $("div.action_menu ul li a#share_document").click(function(event){
        event.preventDefault();
        $.ajax({
               url: 'WebPage_shareDocument',
               async: false
        });
        location.reload();
      });
    }
    $("div.action_menu li ul").css("height", $("div.action_menu li ul li").length * 25.3 + "px");
  }

  $("#edit_document").dialog({
    autoOpen: false,
    height: 131,
    width: 389,
    modal: true,
    buttons: {
      "Save": function(){
        var save_button = $("button.save");
        save_button.html() == "Save" ? save_button.html("Saving...") : null;
        var new_title = $("input#name.title").attr("value");
        var new_short_title = $("input#short_title.short_title").attr("value");
        var new_language = $("input#language.language").attr("value");
        var new_version = $("input#version.version").attr("value");
        var new_int_index = $("input#sort_index.sort_index").attr("value");
        var new_subject_list = $("textarea#keyword_list").attr("value").replace(/\n+/g, ",");
        displayDocumentTitle(new_title);
        setObjectPropertyValue("setTitle", new_title, "value");
        setObjectPropertyValue("setShortTitle", new_short_title, "value");
        setObjectPropertyValue("setLanguage", new_language, "language");
        setObjectPropertyValue("setVersion", new_version, "value");
        setObjectPropertyValue("setIntIndex", new_int_index, "value");
        setObjectPropertyValue("WebPage_setSubjectList", new_subject_list, "value");
        $("#edit_document").dialog("close");
        save_button.click();
      },
      Cancel: function() {
        $(this).dialog("close");
      }
    }
  });
  $("#upload_document").dialog({
    autoOpen: false,
    height: 116,
    width: 346,
    modal: true
  });
  $("div.gadget-listbox").dialog({
    autoOpen: false,
    height: 416,
    width: 600,
    modal: true,
    buttons: {
      "Add": function(){
         var gadgetIdList = Array();
         $("table#gadget-table tbody tr td input").each(function(){
           if (this.checked){
             gadgetIdList.push($(this).attr("id"));
           }
         });
         if (gadgetIdList.length === 0){
           $(this).dialog("close");
         }
         var tabTitle = $("div#tabs ul li.tab_selected span").html();
         $.ajax({
           type: "post",
           url:"WebSection_addGadgetList",
           data: [{name:"gadget_id_list", value: gadgetIdList}],
           success: function(data) {
             window.location.reload();
           }
         });
      }
    }
  });
  $("div#preference_dialog").dialog({
    autoOpen: false,
    height: 'auto',
    width: 'auto',
    modal:true,
    show: 'drop',
    buttons: {
      "Save": function(){
        var erp5PreferenceArgument = $("form#erp5_preference").serialize();
        $.ajax({
          async: false,
          url: ungPreferencePath + "/Base_edit",
          data: erp5PreferenceArgument + "&form_id=Preference_viewHtmlStyle"
        });
        var ungPreferenceArgument = $("form#ung_preference").serialize();
        $.ajax({
          async: false,
          url: ungPreferencePath + "/Base_edit",
          data: ungPreferenceArgument + "&form_id=UNGPreference_view"
        });
        location.reload();
      },
      Cancel: function() {
        $(this).dialog("close");
      }
    }
  });
  $("p#more_properties").click(function(){
      $("div#more_property").show();
      $("p#hide_properties").show();
      $("div#edit_document fieldset").animate({"height": "186px"}, "slow");
      $("div.ui-dialog").animate({"top": "50px"}, "slow").animate({"height": "255px"}, "slow");
      $("div#edit_document").animate({"height": "183px"}, "slow");
      $("div#edit_document fieldset input").css("margin", "0").css("width", "60%");
      $("div#edit_document fieldset label").css("float", "left").css("width", "35%");
      $("div#more_property input").css("width", "47%");
      $("p#more_properties").hide();
    });
  $("p#hide_properties").click(function(){
      $("div#more_property").hide();
      $("p#more_properties").show();
      $("p#hide_properties").hide();
      $("div#edit_document fieldset input").css("width", "95%").css("margin-top", "14px");
      $("div#edit_document fieldset").animate({"height": "69px"}, "slow");
      $("div.ui-dialog").animate({"height": "148px"}, "slow");
      $("div#edit_document").animate({"height": "78px"}, "slow");
  });
  $("a#settings").click(function(event){
      event.preventDefault();
      if ($("div#preference_dialog").html() === ""){
        $.ajax({
          url: "Base_getPreferencePathList",
          async: false,
          dataType: 'json',
          success: function(data){
            ungPreferencePath = data.preference;
            $.ajax({
              url: ungPreferencePath + '/Preference_viewHtmlStyle?editable_mode:int=1',
              async: false,
              method: 'get',
              success: function(data){
                $("div#preference_dialog").append("<form id='erp5_preference'>" +
                                                  "<fieldset class='center editable'>" +
                                                  $(data).find('fieldset.center.editable').html() +
                                                  "</fieldset></form>");
                }
            });
            $.ajax({
              url: ungPreferencePath + '/UNGPreference_view?editable_mode:int=1',
              async: false,
              method: 'get',
              success: function(data){
                $("div#preference_dialog").append("<form id='ung_preference'>" +
                                                  "<fieldset class='center editable'>" +
                                                  $(data).find('fieldset.center.editable').html() +
                                                  "</fieldset></form>");
                }
            });
          }
        });
      }
      $("div#preference_dialog").dialog("open");
    });

  $("button#change_state").click(function(event){
      event.preventDefault();
      $("div#change_state_dialog").html('');
      // update portal selections
      updateListboxSelection();
      $.ajax({
        async: false,
        url: 'erp5/Folder_viewWorkflowActionDialog',
        data: {selection_name: $('input[name=list_selection_name]').val(),
               form_id: $('input[name=gadget_form_id]').val(),
               editable_mode: 1
              },
        success: function(data2) {
          folder_workflow_action_dialog_data = data2;
          $("div#change_state_dialog").append("<form id='change_state_form'>" +
                                              "<div class='change_state_dialog'>" +
                                              "<table class='listbox listbox-table'>" +
                                              "  <thead>" +
                                              "    <tr class='listbox-label-line'>" +
                                              "            <th class='listbox-table-header-cell'>Count</th>" +
                                              "            <th class='listbox-table-header-cell'>Type</th>" +
                                              "            <th class='listbox-table-header-cell'>State</th>" +
                                              "            <th class='listbox-table-header-cell'>Workflow</th>" +
                                              "            <th class='listbox-table-header-cell'>Action</th>" +
                                              "    </tr>" +
                                              "  </thead>" +
                                              "  <tbody>" +
                                              $(data2).find('div.listbox-body > table > tbody').html() +
                                              "  </tbody></table>" +
                                              "  </div>" +
                                              $(data2).find('textarea[name*="comment"]').parent().parent().html() +
                                              "</form>");
          $("div#change_state_dialog").dialog("open");
        }
      });
    });
  $("div#change_state_dialog").dialog({
    autoOpen: false,
    height: 'auto',
    width: 680,
    modal:true,
    buttons: {
      'Change State': function() {
        var folder_workflow_data = $(folder_workflow_action_dialog_data).find('input[type="hidden"]').serializeArray();
        var change_state_data = $('form#change_state_form').serializeArray();
        var merge = {};
        $.map(folder_workflow_data, function(n,i){merge[n.name] = n.value;});
        $.map(change_state_data, function(n,i){merge[n.name] = n.value;});
        merge['form_id'] = 'WebSection_viewUNGDocumentList';
        $.ajax({
          async: false,
          url: 'web_site_module' + "/Base_callDialogMethod",
          data: merge,
          success: function(result){
            var form_data = $(result).find('input[type="hidden"]').serializeArray();
            var merge2 = {};
            $.map(form_data, function(n,i){merge2[n.name] = n.value;});
            $.ajax({
              async: false,
              url: 'web_site_module' + "/Base_callDialogMethod",
              data: merge2,
              success: function(result2){
                $("div#change_state_dialog").dialog("close");
                setPortalStatusMessage("Workflow in progress. Please refresh your page to take changes.");
              }
            });
          }
        });
      },
      Cancel: function() {
        $( this ).dialog("close");
      }
    }
  });

  $("button.ui-button, span.ui-icon").click(function(){$("p#hide_properties").click();});
  $("input#submit_document").click(function(event){
    if (document.getElementById("upload-file").value === ""){
      event.preventDefault();
      $("span#no-input-file").show();
    }
  });
  $("a[name='document_title']").click(function(){
      $("div#more_property").hide();
      $("p#hide_properties").hide();
      var document_title = getObjectPropertyValue("getTitle");
      if ($("input#name.title").attr("value") != document_title) {
        displayDocumentTitle();
      }
      $("input#name.title").attr("value", document_title);
      $("input#short_title.short_title").attr("value", getObjectPropertyValue("getShortTitle"));
      $("input#reference.reference").attr("value", getObjectPropertyValue("getReference"));
      $("input#version.version").attr("value", getObjectPropertyValue("getVersion"));
      $("input#language.language").attr("value", getObjectPropertyValue("getLanguage"));
      $("input#sort_index.sort_index").attr("value", getObjectPropertyValue("getIntIndex"));
      var subjectList = jQuery.parseJSON(getObjectPropertyValue('getSubjectList').replace(/'/g,'"'));
      if (subjectList !== null) {
        $("textarea#keyword_list").attr("value", subjectList.join("\n"));
      } else {
        $("textarea#keyword_list").attr("value", "");
      }
      $("#edit_document").dialog("open");
    });
  $("a#help").click(function(event){
    event.preventDefault();
    showNotImplementedMessage("a#right_message");
  });
  $("span#knowledge_pad_module_8_titlean").text("1");
  if ($("#tab-list-container #tabs ul li").length > 2) {
    $("li#add_new_tab_dialog_link.tab").hide();
  }
  $("div#add_new_gadget_link a#add-gadgets").removeAttr("onclick");
  $("div#add_new_gadget_link a#add-gadgets").click(function(event){
    event.preventDefault();
    // fill gadget list
    $.getJSON("WebSection_getGadgetPathList", function(to_parse_data){
      gadgetList = jQuery(to_parse_data);
      gadgetList.each(function(){
        $("div.gadget-listbox table#gadget-table").append($('<tr>').append($('<td>').append($('<input>').attr('type', 'checkbox').attr('id', this.id))).append($('<td>').append($('<a>').text(this.title))).append($('<td>').append($('<img>').attr('src', this.image_url).text(this.title))));
        });
    });
    $("div.gadget-listbox").dialog("open");
  });
  $("div#page_wrapper div#portal-column-1.portal-column, div#page_wrapper div#portal-column-2.portal-column").remove();
  var jScreen = jQuery(this);
  if (jScreen.width() < 1280){
    $("div.listbox-tree, div.gadget-action div.front_pad").css("width", "79%");
    $("td.listbox-table-domain-tree-cell a").css("padding-right", "25px");
    $("div.header-right").css("width", "52.3%");
  }
  $("a.tree-open").parent().parent().css("background-color", "#BBCCFF");
  if (window.location.href.match("^http.*\/unfoldDomain") !== null){
    $("a.document").css("text-decoration", "none").css("color", "#000");
  }
  var h3Tag = $("div#page_wrapper div h3");
  if (h3Tag.text().replace(/^\s+/,'').replace(/\s+$/,'') == "Your tab is empty."){
    h3Tag.hide();
  }

  if (!$("div.gadget-column").length === 0) {
    // render main document listbox
    $.ajax({
      async: false,
      url: 'WebSection_getUNGDocumentListPadAsJSON',
      data: {pad_relative_url: 'knowledge_pad_module/ung_knowledge_pad', mode: 'web_front'},
      dataType: 'json',
      success: function(data){
        external_data = data;
        var data_html = $(data.body)[0];
        //var data_script = $(data.body)[1].text
        var data_script = data.javascript;

        ung_listbox_container = $('div#main_listbox-container');
        // fill body
        ung_listbox_container.html(data_html);
        // attach listener
        ung_listbox_container.live('DOMSubtreeModified', checkUNGListbox);
        // eval script to update listbox
        eval(data_script);
        // remove class 'portal-column' from main listbox
        // (as it should not interfere in user's box layout)
        // updateServerBoxColumnLayout method uses 'div.portal-column' as selector
        ung_listbox_container.find('div.portal-column')[0].className = '';

        configureUNGSearch(data_script);

        wrapUpdater();
      }
    });
  }
  return false;
});

function configureUNGSearch(data_script) {
  ung_listbox_updater_call = data_script;
  $('input#search_button').click(function(event){
    event.preventDefault();
    var searched_text = $('input[name="field_your_search_text"]').val();

    // keep old function to call
    var originalUpdater = updater;
    // overwrite (shadowing) to change 'params' param on the fly
    updater = function() {
      // 'params' is the fifth param, so treat it
      params = arguments[4];
      params['SearchableText'] = searched_text;
      originalUpdater.apply(this, arguments);
    };
    // eval script
    eval(data_script);

    // restore old function
    updater = originalUpdater;
  });
}

function wrapUpdater() {
  originalUpdater = updater;
  updater = wrappedUpdater;
}

function wrappedUpdater() {
  dom_id = arguments[2];
  additional_request_params = arguments[4];

  // let UNG save checked itens of main listbox under portal_selections
  enabled_checkboxes = $('#'+dom_id).find('input[type="checkbox"]:checked');
  enabled_checkboxes.each(function(key, value){
    element = $(value);
    element_name = element.attr("name");
    element_value = element.val();
    if (typeof(additional_request_params[element_name]) == "undefined") {
      additional_request_params[element_name] = new Array();
    }
    additional_request_params[element_name].push(element_value);
  });
  originalUpdater.apply(this, arguments);
}

function checkUNGListbox() {
  gadget_listbox_container = $('div#main_listbox-container div.listbox-container');
  if (gadget_listbox_container.length >= 1) {
    // XXX: the .die and .live calls are because of the call to .find function
    // that is triggered recursively without stop if parent has the .live
    // listener, like in this case
    ung_listbox_container.die('DOMSubtreeModified');

    // look if there's a listbox-tree (listbox-domain navigation) inside
    // main content of listbox. If it finds someone, then call
    // separate_script to detach fields of main content of listbox [again]
    if (gadget_listbox_container.find("div.listbox-tree").length >= 1) {
      separateUNGListboxGadgetFields();
    }

    // re-attach listener
    ung_listbox_container.live('DOMSubtreeModified', checkUNGListbox);
  }
}

function separateUNGListboxGadgetFields() {
  // get gadget listbox container
  var data = gadget_listbox_container;

  // remove menu of listbox container gadget
  ung_listbox_container.find('h3.handle').remove();

  // detach domain_selected
  $("a.domain_selected").text(data.find("button.tree-open:last").text());

  // XXX: temporaly commented while developing
  // TODO: analyze if this css is breaking layout of 'global scope'
//  $("body").css("overflow", "hidden");

  // configure Refresh button
  configureRefreshButton();

  // detach listbox-page-navigation
  var gadget_navigation = data.find("div.listbox-page-navigation");
  if (gadget_navigation) {
    ung_toolbar_navigation = $('div.toolbar').find('div.listbox-navigation');
    ung_toolbar_navigation.html(gadget_navigation.html());
    gadget_navigation.remove();
  }

  // remove 'listbox-title' from header
  $('div.listbox-title').remove();

  // detach css of listbox-tree
  var listboxTreeHeight = data.find("div.listbox-tree").css("height").replace("px", "");
  try {
    var domainTreeHeight = data.find("div.listbox-domain-tree-container").css("height").replace("px", "");
  } catch(e) {
    // this maybe categorize first access of user, needing
    // to reload page in time to create 'selection' in portal_selections
    window.location.reload();
    return false;
  }
  if (parseInt(listboxTreeHeight,10) > parseInt(domainTreeHeight,10)){
    data.find("div.listbox-tree").css("height", data.find("div.listbox-domain-tree-container").css("height"));
  }
  if (parseInt(domainTreeHeight,10) > 233) {
    data.find("div.listbox-tree").css("overflow-y", "scroll");
  }

  // detach listbox-tree
  var listbox_tree_div = data.find("div.listbox-tree").outerHTML();
  data.find("div.listbox-tree").remove();
  // XXX: improve this behaviour of replacing
  file_listbox_tree = $('div.file-quick-search').find('div.listbox-tree');
  if (file_listbox_tree.length >= 1) {
    file_listbox_tree.replaceWith(listbox_tree_div);
  } else {
    $("div.file-quick-search").append(listbox_tree_div);
  }

  // detach css of listbox-body
  var tr_length = data.find("div.listbox-body tbody tr").length;
  if (tr_length < 16){
    var height = tr_length * 1.5;
    data.find("div.listbox-body tbody").css("height", height + "em");
  }

  // hide listbox-page-navigation if doesn't need it
  if (data.find("div.listbox-page-navigation").text() == "null")
    data.find("div.listbox-page-navigation").hide();

  // update checkAll and uncheckAll buttons under listbox
  $("input.listbox-check-all").click(function(event){
    event.preventDefault();
    changeCheckBoxValue(true);
  });
  $("input.listbox-uncheck-all").click(function(event){
    event.preventDefault();
    changeCheckBoxValue(false);
  });
  return true;
}

function configureRefreshButton() {
  $('a#refresh_button').click(function(event){
    event.preventDefault();
    // keep old function to call
    var originalUpdater = updater;
    // overwrite (shadowing) to change 'params' param on the fly
    updater = function() {
      // 'params' is the fifth param, so treat it
      params = arguments[4];
      params['reset:int'] = 1;
      originalUpdater.apply(this, arguments);
    };
    // eval script
    eval(ung_listbox_updater_call);

    // restore old function
    updater = originalUpdater;
  });
}

function setPortalStatusMessage(status_message) {
    //display warning
    status_message_tag = $('div.portal_status_message');
    status_message_tag.css("font-weight", "bold");
    status_message_tag.text(status_message);
}
