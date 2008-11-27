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

function submitAction(form, act) {
  form.action = act;
  form.submit();
}

// This function will be called when the user click the save button. As 
// submitAction function may have changed the action before, it's better to
// reset the form action to it's original behaviour. This is actually
// usefull when the user click the back button.
function clickSaveButton(act) {
  document.forms[0].action = act;
}


// The first input element with an "autofocus" class will get the focus,
// else if no element have autofocus class, the first element which is not the
// search field will get the focus. This is generally the title input text of
// a view
function autoFocus() {
  var first_autofocus_expr = ".//input[@class='autofocus']"
  var FIRST_RESULT = XPathResult.FIRST_ORDERED_NODE_TYPE

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
  }
}

function buildTables(element_list, rowPredicate, columnPredicate,
                    tableClassName) {
  /* Generic code to build a table from elements in element_list.
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
        while ((!end_line) && (row_item = row_item.nextSibling) != null) {
          var predicate_result = columnPredicate(row_item, row_begin)
          if ((predicate_result & 1) != 0)
            item_list.push(row_item);
          end_table = ((predicate_result & 4) != 0);
          end_line = ((predicate_result & 6) != 0);
        }
        row_list.push(item_list);
      }
      element_index++;
    }
    /* Do not create a table with just one cell. */
    if ((row_list.length > 1) ||
        (row_list.length == 1 && row_list[0].length > 1)) {
      var first_element = row_list[0][0];
      var container = first_element.parentNode;
      var fake_table = document.createElement("table");
      var i;
      var j;
      fake_table.className = tableClassName;
      container.insertBefore(fake_table, first_element);
      for (i = 0; i < row_list.length; i++) {
        var fake_row = document.createElement("tr");
        var row_element_list = row_list[i];
        for (j = 0; j < row_element_list.length; j++) {
          var fake_cell = document.createElement("td");
          fake_cell.appendChild(row_element_list[j]);
          fake_row.appendChild(fake_cell);
        }
        fake_table.appendChild(fake_row);
      }
    }
  }
}

function matchChunk(string, separator, chunk_value) {
  if (string != null) {
    var id_chunks = string.split(separator);
    var i;
    for (i = 0; i < id_chunks.length; i++) {
      if (id_chunks[i] == chunk_value)
        return true;
    }
  }
  return false;
}

function matchLeftFieldset(element) {
  return (element.tagName == "FIELDSET") &&
          matchChunk(element.id, '_', "left");
}

function matchRightFieldset(element, ignored) {
  if ((element.tagName == "FIELDSET") &&
       matchChunk(element.id, '_', "right"))
    return 7; /* End row, table and use element */
  return 0;
}

function fixLeftRightHeightAndFocus(fix_height) {
  if (fix_height == 1) {
    buildTables(document.getElementsByTagName('fieldset'),
                matchLeftFieldset, matchRightFieldset,
                "fake");
  }
  autoFocus();
}

// This function can be used to catch ENTER pressed in an input 
// and modify respective main form action
function submitFormOnEnter(event, main_form_id, method_name){
  var key_code = event.keyCode;
  if(key_code == 13){
    var main_form = getElement(main_form_id)
    main_form.action=method_name;};
}

var old_index=0;
function shiftCheck(evt) {
  evt=(evt)?evt:event;
  var target=(evt.target)?evt.target:evt.srcElement;
  // remove "checkbox" part from ID
  // This part can be reused easilly by usual left column
  var target_index= target.id.substr(8);
  if(!evt.shiftKey) {
    old_index= target_index
    check_option = target.checked;
    return false;
    }
  target.checked=1;
  var low=Math.min(target_index , old_index);
  var high=Math.max(target_index , old_index);
  for(var i=low;i<=high;i++) {
    document.getElementById("checkbox" + i ).checked = check_option;
   }
  return true;
  }

var indexAllCheckBoxesAtBTInstallationOnLoad = function() {
    // This Part is used basically for Business Template Installation.
    var inputs = window.getElementsByTagAndClassName("input", "shift_check_support");
    for(i=0;i<=inputs.length-1;i++) { inputs[i].id = "checkbox" + i; }
}

addLoadEvent(indexAllCheckBoxesAtBTInstallationOnLoad)

