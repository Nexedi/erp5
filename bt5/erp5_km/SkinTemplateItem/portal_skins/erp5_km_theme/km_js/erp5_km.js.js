/*
Copyright (c) 2011-2012 Nexedi SARL and Contributors. All Rights Reserved.

This program is Free Software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
*/

function toggleSection(section_id, image_id){
  /* Browser gadget toggle section */
  section_obj = $("#" + section_id);
  image_obj = $("#" + image_id);
  if(section_obj.is(":hidden")){
    section_obj.show();
    image_obj.attr("src", "images/tree_open.png");}
  else{
    section_obj.hide();
    image_obj.attr("src", "images/tree_closed.png");}
  } 



function toggleHiddenFormatDialogSelection(){
  /* Expand more download formats widget */
  $("div.download-document-format-list-menu-hidden").toggle();
  $("li.toggle-hidden-format-dialog-selection-link").remove();
}

function requestPasswordReset(script_name){
  $("#reference").attr("value", $("#__ac_name").val());
  // reset __ac_name & __ac_password in case they have been filled by browser
  $("#__ac_name").attr("value", "");
  $("#__ac_password").attr("value", "");
  // Submit request password
  main_form = $("#main_form");
  main_form.attr("action", script_name);
  main_form.submit();
}

//enable or disable right side search result preview
var show_preview=false;
var popup_local_dict={};
var popup_request_dict={};

function togglePreview(dom_id,path){
  /* 
  Enable or disable right preview in search mode listbox style. 
  */
  listbox_container = $("#"+dom_id).parents("div.listbox-container");
  if(!$("#listbox-preview").length){
    // init only once per listbox
    listbox_container.append('<div id="listbox-preview"><img src="ajax-loader.gif" title="Loading" alt="Loading" /><p>Loading...</p> </div>');
    show_preview=true;
    showPopik(dom_id, path);
  }
  else{
    // we can switch it off
    $("#listbox-preview").remove();
    show_preview=false;}
}

function formatPreview(dom_id, path){
  /*
    Format visually the popup preview.
  */
  popup = $("#listbox-preview");
  dom_object = $("#"+dom_id);
  parent_row = dom_object.parents("tr").first();
  row_object = dom_object.parents("tr").first();
  class_name = row_object.attr("class"); 
  class_name = class_name.replace("listbox-data-line-","");
  class_name = class_name.replace("DataA","");
  class_name = class_name.replace("DataB","");
  row_index = parseInt(class_name, 10);
  //calculate current row offset relative to listbox's table.tbody
  offset = parent_row.position("tbody").top - $("tr.listbox-data-line-0").position("tbody").top;
  popup.css("top", offset + "px");
}

function requestPopupInfo(dom_id, path){
  /*
    Get popup infor from server and cache it locally for page's lifetime.
  */
  var popup = $("#listbox-preview");
  popup_request_dict[dom_id] = popup_request_dict;
  $.ajax({url: path + "/Document_getPopupInfo", 
          success: function(popup_html){
                           formatPreview(dom_id, path);
                           popup.html(popup_html);
                           popup.show();
                           popup_local_dict[dom_id] = popup_html;}});
  }
  

function showPopik(dom_id, path){
  /* 
    Show / Hide popup details window up in search mode. 
  */
  if(!show_preview) return;
  popup = $("#listbox-preview");
  if($("#hidden_popup_listbox_"+dom_id).length){
    // popup info is inline just copy it
    formatPreview(dom_id, path);
    popup_html = $("#hidden_popup_listbox_"+dom_id).html();
    popup.html(popup_html);
    popup.show();
    return;
  }
  // we must request popup info with another request
  popup_html = popup_local_dict[dom_id];
  popup_request = popup_request_dict[dom_id];
  if (popup_html==undefined&&popup_request==undefined){
    // still not cached for page's lifetime not any pending requests to server
    requestPopupInfo(dom_id, path);
  }
  else{
    // cached for page's lifetime
    formatPreview(dom_id, path);
    popup.html(popup_html);
    popup.show();
  }
}

function initialize_form(){
  /* 
    Pressing enter in an input field in editable_mode must called default form submit button.
    Due to different browser implementations in regard to determing which is the *right*
    form's submit button (in KM case we can have many) we explicitly catch events and call it.
  */
   if($("#input-save-edit")){
     $('#main_form').each(function() {
          $('input').keypress(function(e) {
            if(e.which == 10 || e.which == 13) {$("#input-save-edit").click();}
          });
      });
   }
 }

jQuery.fn.highlight = function (str, className) {
  /*
    Highlight search word in HTML content.
  */
  var regex = new RegExp(str, "gi");
  return this.each(function () {
      this.innerHTML = this.innerHTML.replace(regex, function(matched) {return "<span class=\"" + className + "\">" + matched + "</span>";});
    });
};

function highlight_search_word(){
  /*
    Use referer to get search text (if coming from GET search page) and highlight found words.
  */
  query_array = queryStringToArray(document.referrer);
  search_text = query_array["search_text"];
  if (search_text!=undefined){
    document_body = $("#main_content div.document div.page");
    headline = $("#main_content div.document span.headline");
    title = $("#wrapper_headline div.header_title");
    // multiple words
    search_word_list = search_text.split("%20");
    for(var i=0; i<search_word_list.length; i++) {
      if (search_word_list[i] !== '') {
        document_body.highlight(search_word_list[i], "highlight");
        headline.highlight(search_word_list[i], "highlight");
        title.highlight(search_word_list[i], "highlight");
      }
      
    }
  }
}

$(document).ready(highlight_search_word);
$(document).ready(initialize_form);
