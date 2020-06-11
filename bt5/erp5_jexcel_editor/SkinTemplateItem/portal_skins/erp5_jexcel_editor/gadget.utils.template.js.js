/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, jexcel*/
(function (window, rJS, jexcel) {
  "use strict";

  var template = {
    minDimensions: [26, 100],
    defaultColWidth: 100,
    allowExport: true,
    columnSorting: true,
    columnDrag: true,
    columnResize: true,
    rowResize: true,
    rowDrag: true,
    editable: true,
    allowInsertRow: true,
    allowManualInsertRow: true,
    allowInsertColumn: true,
    allowManualInsertColumn: true,
    allowDeleteRow: true,
    allowRenameColumn: true,
    allowComments: true,
    selectionCopy: true,
    search: true,
    fullscreen: true,
    autoIncrement: true,
    parseFormulas: true,
    wordWrap: true
  };

  var undo = {
    type: 'i',
    content: 'undo',
    onclick: function (a, b, c) {
      b.undo();
    }
  };

  var redo = {
    type: 'i',
    content: 'redo',
    onclick: function (a, b, c) {
      b.redo();
    }
  };

  var merge = {
    type: 'i',
    content: 'table_chart',
    onclick: function (a, b, c) {
      var cell = document.querySelector("td.highlight");
      var x = Number(cell.dataset.x);
      var selected = b.getJson(true);
      var colspan = Object.keys(selected[0]).length;
      var rowspan = selected.length;
      var letter = "";
      if (x <= 25) {
        letter += String.fromCharCode(97 + x).toUpperCase();
      }
      else {
        letter += String.fromCharCode(97 + Math.trunc(x / 25) - 1).toUpperCase();
        letter += String.fromCharCode(97 + (x % 26)).toUpperCase();
      }
      var coor = letter + (Number(cell.dataset.y) + 1).toString();
      b.setMerge(coor, colspan, rowspan);
    }
  };

  var unmerge = {
    type: 'i',
    content: 'close',
    onclick: function (a, b, c) {
      var cell = document.querySelector("td.highlight-selected");
      var x = Number(cell.dataset.x);
      var letter = "";
      if (x <= 25) {
        letter += String.fromCharCode(97 + x).toUpperCase();
      }
      else {
        letter += String.fromCharCode(97 + Math.trunc(x / 25) - 1).toUpperCase();
        letter += String.fromCharCode(97 + (x % 26)).toUpperCase();
      }
      var coor = letter + (Number(cell.dataset.y) + 1).toString();
      b.removeMerge(coor);
    }
  };

  var destroy_merge = {
    type: 'i',
    content: 'cancel',
    onclick: function (a, b, c) {
      b.destroyMerged();
    }
  };

  var remove = {
    type: 'i',
    content: 'delete',
    onclick: function (a, b, c) {
      var tab_link = document.querySelector('.jexcel_tab_link.selected');
      var index = tab_link.getAttribute("data-spreadsheet");
      if (document.querySelector('.spreadsheet').jexcel.length > 1) {
        tab_link.remove();
        var to_remove;
        document.querySelectorAll(".jexcel_container").forEach(tab => {tab.style.display === "block" ? to_remove = tab : null});
        to_remove.remove();
        document.querySelector('.spreadsheet').jexcel.splice(index, 1);
        document.querySelector('.jexcel_container').style.display = "block";
        document.querySelectorAll('.jexcel_tab_link').forEach((tab, i) => {
          i == 0 ? tab.classList.add("selected") : null;
          tab.dataset.spreadsheet = i;
          tab.textContent = tab.textContent.substring(0, 5) === "Sheet" ? "Sheet " + (i + 1) : tab.textContent;
        });
      }
      else {
        document.querySelector('.jexcel_tab_link').textContent = "Sheet 1"
        document.querySelector('.spreadsheet').jexcel[0].setData(Array(100).fill(0, 99, Array(26).fill(0, 26, "")));
      }
    }
  };

  var font_style = {
    type: 'select',
    k: 'font-family',
    v: ['Arial', 'Comic Sans MS', 'Verdana', 'Calibri', 'Tahoma', 'Helvetica', 'DejaVu Sans', 'Times New Roman', 'Georgia', 'Antiqua']
  };
  var font_size = {
    type: 'select',
    k: 'font-size',
    v: ['8px', '10px', '12px', '14px', '16px', '18px', '20px', '22px', '24px', '26px', '28px', '30px', '34px', '38px', '42px', '46px', '50px']
  };

  var text_align_left = {
    type: 'i',
    content: 'format_align_left',
    k: 'text-align',
    v: 'left'
  };

  var text_align_center = {
    type: 'i',
    content: 'format_align_center',
    k: 'text-align',
    v: 'center'
  };

  var text_align_right = {
    type: 'i',
    content: 'format_align_right',
    k: 'text-align',
    v: 'right'
  };

  var text_align_justify = {
    type: 'i',
    content: 'format_align_justify',
    k: 'text-align',
    v: 'justify'
  };

  var vertical_align_top = {
    type: 'i',
    content: 'vertical_align_top',
    k: 'vertical-align',
    v: 'top'
  };

  var vertical_align_middle = {
    type: 'i',
    content: 'vertical_align_center',
    k: 'vertical-align',
    v: 'middle'
  };

  var vertical_align_bottom = {
    type: 'i',
    content: 'vertical_align_bottom',
    k: 'vertical-align',
    v: 'bottom'
  };

  var style_bold = {
    type: 'i',
    content: 'format_bold',
    k: 'font-weight',
    v: 'bold'
  };

  var style_underlined = {
    type: 'i',
    content: 'format_underlined',
    k: 'text-decoration',
    v: 'underline'
  };

  var style_italic = {
    type: 'i',
    content: 'format_italic',
    k: 'font-style',
    v: 'italic'
  };
  var text_color = {
    type: 'color',
    content: 'format_color_text',
    k: 'color'
  };
  var background_color = {
    type: 'color',
    content: 'format_color_fill',
    k: 'background-color'
  };

  rJS(window)

    .declareMethod("getToolbarList", function (add_function, dict) {
      var list = [];
      if (dict.hasOwnProperty("undo_redo") && dict.undo_redo) {
        list.push(undo, redo);
      }
      if (dict.hasOwnProperty("add") && dict.add) {
        var add = {
          type: 'i',
          content: 'add',
          onclick : add_function
        };
        list.push(add, remove);
      }
      if (dict.hasOwnProperty("merge") && dict.merge) {
        list.push(merge, unmerge, destroy_merge);
      }
      if (dict.hasOwnProperty("text_font") && dict.text_font) {
        list.push(font_style, font_size, style_bold, style_italic, style_underlined);
      }
      if (dict.hasOwnProperty("text_position") && dict.text_position) {
        list.push(text_align_left, text_align_center, text_align_right, text_align_justify, vertical_align_top, vertical_align_middle, vertical_align_bottom);
      }
      if (dict.hasOwnProperty("color_picker") && dict.color_picker) {
        list.push(text_color, background_color);
      }
      var res = Object.assign({}, template);
      res.toolbar = list;
      return res;
    });

}(window, rJS, jexcel));
