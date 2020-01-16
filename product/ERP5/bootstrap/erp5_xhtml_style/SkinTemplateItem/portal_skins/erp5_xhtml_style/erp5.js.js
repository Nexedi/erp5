/*
Copyright (c) 20xx-2006 Nexedi SARL and Contributors. All Rights Reserved.

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

function submitAction(form_or_submit, act) {
  if ($(form_or_submit).is('form')) {
    form = form_or_submit;
    form.action = act;
    form.submit();
  } else {
    form_or_submit.click();
  }
}

// This function will be called when the user click the save button. As 
// submitAction function may have changed the action before, it's better to
// reset the form action to it's original behaviour. This is actually
// usefull when the user click the back button.
function clickSaveButton(act) {
  changed = false;
  document.forms[0].action = act;
}

// The first input element with an "autofocus" class will get the focus,
// else if no element have autofocus class, the first element which is not the
// search field will get the focus. This is generally the title input text of
// a view
function autoFocus() {
  var first_autofocus_expr = ".//input[@class='autofocus']";
  var FIRST_RESULT = XPathResult.FIRST_ORDERED_NODE_TYPE;

  var input = document.evaluate(first_autofocus_expr, document, null, FIRST_RESULT, null).singleNodeValue;
  if (input) {
    input.focus();
  }else{
    // The following is disabled, because it is too annoying to have an auto focus at everywhere.
    //var first_text_input_expr = ".//input[@type='text'][@name != 'field_your_search_text']"
    //var first_text_input = document.evaluate(first_text_input_expr, document, null, FIRST_RESULT, null).singleNodeValue;
    //if (first_text_input){
    //  first_text_input.focus();
    //}
   true;
  }
}

function buildTables(element_list, rowPredicate, columnPredicate,
                    tableClassName) {
  /* Generic code to build a table from elements in element_list.
   * XXX: not used anymore ?
   * rowPredicate(element) -> bool
   *   When it returns a true value, a new line is started with element.
   *   When is returns a false value, element is skipped.
   * columnPredicate(element, initial_element) -> bitfield
   *   bit 3: end_table (if true, imlies end_row)
   *     End current table.
   *   bit 2: end_row
   *     End current row.
   *   bit 1: use_element
   *     Element passed to columnPredicate will be put in current row.
   * Hardcoded:
   *  - items in a table line must be siblings in existing DOM
   *  - table is put in place of first element of the first row
   */
  var element_index = 0;
  while (element_index < element_list.length) {
    var row_list = [];
    var end_table = false;
    while ((!end_table) && element_index < element_list.length) {
      var row_begin = element_list[element_index];
      if (rowPredicate(row_begin)) {
        var item_list = [row_begin];
        var row_item = row_begin;
        var end_line = false;
        while ((!end_line) && (row_item = row_item.nextSibling) !== null) {
          var predicate_result = columnPredicate(row_item, row_begin);
          if ((predicate_result & 1) !== 0)
            item_list.push(row_item);
          end_table = ((predicate_result & 4) !== 0);
          end_line = ((predicate_result & 6) !== 0);
        }
        row_list.push(item_list);
      }
      element_index++;
    }
    /* Do not create a table with just one cell. */
    if ((row_list.length > 1) ||
        (row_list.length == 1 && row_list[0].length > 1)) {
      var first_element = row_list[0][0];
      var fake_table = $("<table>");
      fake_table.addClass(tableClassName);
      fake_table.insertBefore(first_element);
      $.each(row_list, function() {
        var fake_row = $("<tr>");
        $.each(this, function() {
          var fake_cell = $("<td>");
          fake_cell.append(this);
          fake_row.append(fake_cell[0]);
        });
        fake_table.append(fake_row[0]);
      });
    }
  }
}

function matchLeftFieldset(element) {
// XXX: not used anymore ?
  return (element.tagName == "FIELDSET" &&
       element.className.toLowerCase().indexOf('left') != -1);
}

function matchRightFieldset(element, ignored) {
// XXX: not used anymore ?
  if (element.tagName == "FIELDSET" &&
       element.className.toLowerCase().indexOf('right') != -1)
    return 7; /* End row, table and use element */
  return 0;
}

function fixLeftRightHeightAndFocus(fix_height) {
  if (fix_height == 1) {
    var right_xpath = "following-sibling::fieldset[contains(@class, 'right')]";
    var matched_left_element_list = document.evaluate("//fieldset[contains(@class, 'left') and " + right_xpath + "]", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
    var element_index;
    for (element_index = 0; element_index < matched_left_element_list.snapshotLength; element_index++) {
      var element = matched_left_element_list.snapshotItem(element_index);
      var right = document.evaluate(right_xpath, element, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
      var table = $('<table class="fake">').insertBefore(element);
      table.append($("<tr>").append($("<td>").append(element)).append($("<td>").append(right)));
    }
  }
  autoFocus();
}

// This function can be used to catch ENTER pressed in an input
// and modify respective main form action
// if clear_changed_flag is set to true, changed will be set to false, so no
// warning message about unsaved changes will be displayed
function submitFormOnEnter(event, form_or_submit, method_name, clear_changed_flag, element){
  if (clear_changed_flag === null){ clear_changed_flag = false; }
  if(event.keyCode == 13){
    if (clear_changed_flag === true) {
      changed = false;
    }
    if ($(form_or_submit).is('form')) {
      form = form_or_submit;
      if (form == "main_form") {
        form = document.forms[form]; // backward compatibility
      }
      form.action = method_name;
      form.submit();
    } else {
      form_or_submit.click();
    }
    event.preventDefault();
    return false;
  }
}

var old_index = 0;
function shiftCheck(evt) {
  /*Uncheck all checkboxes from last unchecked one in 
    business template Install / Update / Reinstall dialog.
  */
  evt = (evt)?evt:event;
  var target=(evt.target)?evt.target:evt.srcElement;
  // remove "checkbox" part from ID
  // This part can be reused easilly by usual left column
  var target_index= target.id.substr(8);
  if(!evt.shiftKey) {
    old_index = target_index;
    check_option = target.checked;
    return false;
    }
  target.checked=1;
  var low=Math.min(target_index , old_index);
  var high=Math.max(target_index , old_index);
  for(var i=low;i<=high;i++) {
    $("#checkbox" + i).attr("checked", false);
   }
  return true;
  }

var indexAllCheckBoxesAtBTInstallationOnLoad = function() {
    // This Part is used basically for Business Template Installation.
    $("input.shift_check_support").each(
      function(index){$(this).attr("id",  "checkbox"+index);});
    //var inputs = window.getElementsByTagAndClassName("input", "shift_check_support");
    //for(i=0;i<=inputs.length-1;i++) {inputs[i].id = "checkbox" + i; }
};

var resizeIFrameOnLoad = function() {
  /* Resize all frames in document in order to remove sliders  */
  $("object.auto_height").each(function(){
    var inner_frame = this.contentDocument;
    if (inner_frame){
      $(this).css("height", inner_frame.documentElement.offsetHeight + 'px');
    }
  });
};

var changed = false;
function installUnsavedChangesWarning(warning_message) {
  window.onbeforeunload = function() {
    if ((changed)&&($("button.save")))
      // show an warning box only if save button do exists
      return warning_message;
  };
}

var addOnChangeEventHandler = function() {
  /* Add a onchange event handler for all fields inputs.
  This event handler set a dirty flag which cause a warning
  while leaving the page, unless leaving by:
      - saving (see clickSaveButton function from this file)
      - clicking a relation field wheel
      - clicking on a input with type submit
  */
  $("#main_form").each(function(i) {
    $(this).submit(function() {changed = false; return true;});
  });
  $("#master div").each(function(i) {
    if ($(this).attr("class") == "input") {
        $(this).children().each(function() {
          if ($(this).prop("tagName") == "INPUT" ||
              $(this).prop("tagName") == "SELECT" ||
              $(this).prop("tagName") == "TEXTAREA") {
              if ($(this).val() == "update..." ||
                  ($(this).prop("tagName") == "INPUT" &&
                  $(this).attr("type") == 'submit')) {
               // this is a relation field wheel or a submit form button
             this.onclick = function() { changed = false;};
            } else {
              if (!this.onchange) {
                this.onchange = function() { changed = true; };
              }
            }
          } 
          /* Listbox or MatrixBox */
          if ($(this).prop("tagName") == "DIV" && (
              $(this).attr("class") == "listbox-container" ||
              $(this).attr("class") == "MatrixContent")) {
            $(this).find('td').each(function(){
              if ($(this).attr("class") == "listbox-search-line") {
                return non-false;
              }
              $(this).find('input,textarea').each(function(){
                if ($(this).attr("type") != "hidden" &&
                    !this.onchange) {
                  this.onchange = function() { changed = true; };
                }
              });
              return true;
            });
          }
        });
    }
  });
};

var rewriteIndentedSelect = function() {
  /*
   Under firefox, rewrite indented title categories using style definition.
   This way we can select items by pressing the first letter of their name. */

    $("#master select").each(function() {
      $(this).children().each(function() {
        if ($(this).prop("tagName") != "OPTION") {
          return non-false;
        }
        text = $(this).html();
        if (text.substring(0, 1) == '\n') {
          text = text.substring(1, text.length);
        }
        level = 0;
        if (text.substring(0, 6) == '&nbsp;') {
          for (idx=0; idx <= text.length; idx+=6) {
            if (text.substring(idx, idx+6) == '&nbsp;') {
              level += 1;
            } else {
              break;
            }
          }
        }
        if (level >= 1) {
          level = level / 4.0;
          $(this).html(text.replace(/^(&nbsp;)+/, ""));
          $(this).css("paddingLeft", level+"em");
        }
        return true;
      });
    });
};

function queryStringToArray(query_string){
  /*
    Turn a query string into a "dictionary"
  */
  var final_dict = {};
  var b = query_string.split('&');
  $.each(b, function(x, y){
    var temp = y.split('=');
    final_dict[temp[0]] = temp[1];});
  return final_dict;
}

function submitLinkAsHtmlForm(event){
  /*
  Parse link into form arguments and pass everything as a 
  form (together with rest of page's input elements).
  */
  var url = $(this).attr("href");
  var form = $("form");
  var method = url.substring(0, url.indexOf('?'));
  var query_string = url.substring(url.indexOf('?')+1);
  var params = queryStringToArray(query_string);
  $.each(params, function(key, value) {
    if (!$('*[name="' + key + '"]').length){
      // key not part of HTML namespace
      form.append('<input type="hidden" name="' + key+ '" value="' + value + '">');
    }});
  // submit form  
  form.attr("action", method);
  form.submit();
  event.stopPropagation();
  return false;
}

function redirectPDFPage(event, element){
  /*
    Used in PDF thumbnail preview mode
  */
  if(event.keyCode == 13){
    selection_index = parseInt($(element).val(), 10) - 1;
    window.location.href = "PDF_viewHTMLPreviewAsImage?selection_index=" + selection_index;
    return false;    
  }
}

if (navigator.userAgent.toLowerCase().indexOf('firefox') != -1)
  $(document).ready(rewriteIndentedSelect);
$(document).ready(resizeIFrameOnLoad);
$(document).ready(addOnChangeEventHandler);
$(document).ready(indexAllCheckBoxesAtBTInstallationOnLoad);



function installDoubleSubmitDialogPrevention(confirmation_message) {
  /* Install an handler to prevent submitting a dialog twice. */
  $(document).ready( function() {
    $(".dialog_submit_button").on("click", function(e){
      if ($(this).val() != "Next") {
        $(this).on("click.confirm", function(event) {
          $(this).off(".confirm");
          if (! confirm(confirmation_message) ) {
            event.preventDefault();
          }
        });
      }
    });
  });
}
