/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, jexcel*/
(function (window, rJS, jexcel) {
  "use strict";

  var numberToLetter = function (i) {
    return (i >= 26 ? numberToLetter((i / 26 >> 0) - 1) : '') + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i % 26 >> 0];
  };

  var getCoordsFromCell = function (cell) {
    var x = Number(cell.dataset.x);
    var y = Number(cell.dataset.y) + 1;
    return numberToLetter(x) + y.toString();
  };

  var fireDblClick = function (el) {
    var clickEvent  = document.createEvent('MouseEvents');
    clickEvent.initEvent('dblclick', true, true);
    el.dispatchEvent(clickEvent);
  };

  var template = {
    minDimensions: [26, 200],
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
      var cell = a.querySelector("td.highlight");
      var selected = b.getJson(true);
      var colspan = Object.keys(selected[0]).length;
      var rowspan = selected.length;
      var coor = getCoordsFromCell(cell);
      confirm("Top left selected cell's content will be kept, other will be erased.") ? b.setMerge(coor, colspan, rowspan) : null;
    }
  };

  var unmerge = {
    type: 'i',
    content: 'close',
    onclick: function (a, b, c) {
      var cell = document.querySelector("td.highlight-selected");
      var x = Number(cell.dataset.x);
      var coor = getCoordsFromCell(cell);
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

  var image = {
    type: "i",
    content: "image",
    onclick: function (a, b, c) {
      var cell = a.querySelector("td.highlight-selected");
      if (cell && confirm("Data in this column will be erased.")) {
        var worksheet = document.querySelector('.selected').getAttribute('data-spreadsheet');
        var instance = document.querySelector('.spreadsheet').jexcel[worksheet];
        instance.options.columns[Number(cell.dataset.x)].type = "image";
        fireDblClick(cell);
      }
    }
  };

  var checkbox = {
    type: "i",
    content: "checkbox",
    onclick: function (a, b, c) {
      var cell = a.querySelector("td.highlight-selected");
      if (cell && confirm("Data in this column will be erased.")) {
        var worksheet = document.querySelector('.selected').getAttribute('data-spreadsheet');
        var instance = document.querySelector('.spreadsheet').jexcel[worksheet];
        var column = instance.el.querySelectorAll("td[data-x='" + cell.dataset.x + "']");
        var array = [...column];
        array.shift();
        array.forEach(function (cell) {
          instance.setValue(getCoordsFromCell(cell), "");
          cell.innerHTML = "<input type='checkbox' name='c" + cell.dataset.x + "'>";
        });
        instance.options.columns[Number(cell.dataset.x)].type = "checkbox";
      }
    }
  };

  var radio = {
    type: "i",
    content: "radio",
    onclick: function (a, b, c) {
      var cell = a.querySelector("td.highlight-selected");
      if (cell) {
        var worksheet = document.querySelector('.selected').getAttribute('data-spreadsheet');
        var instance = document.querySelector('.spreadsheet').jexcel[worksheet];
        var column = instance.el.querySelectorAll("td[data-x='" + cell.dataset.x + "']");
        var array = [...column];
        array.shift();
        array.forEach(function (cell) {
          instance.setValue(getCoordsFromCell(cell), "");
          cell.innerHTML = "<input type='radio'>";
        });
        instance.options.columns[Number(cell.dataset.x)].type = "radio";
      }
    }
  };

  var text = {
    type: "i",
    content: "title",
    onclick: function (a, b, c) {
      var cell = a.querySelector("td.highlight-selected");
      if (cell && confirm("Data in this column will be erased.")) {
        var worksheet = document.querySelector('.selected').getAttribute('data-spreadsheet');
        var instance = document.querySelector('.spreadsheet').jexcel[worksheet];
        var column = instance.el.querySelectorAll("td[data-x='" + cell.dataset.x + "']");
        var array = [...column];
        instance.options.columns[Number(cell.dataset.x)].type = "text";
        array.shift();
        array.forEach(function (cell) {
          cell.innerHTML = "";
          instance.setValue(getCoordsFromCell(cell), "");
        });
        fireDblClick(cell);
      }
    }
  };

  var html = {
    type: "i",
    content: "list",
    onclick: function (a, b, c) {
      var cell = a.querySelector("td.highlight-selected");
      if (cell && confirm("Data in this column will be erased.")) {
        var worksheet = document.querySelector('.selected').getAttribute('data-spreadsheet');
        var instance = document.querySelector('.spreadsheet').jexcel[worksheet];
        var column = instance.el.querySelectorAll("td[data-x='" + cell.dataset.x + "']");
        var array = [...column];
        instance.options.columns[Number(cell.dataset.x)].type = "html";
        array.shift();
        array.forEach(function (cell) {
          cell.innerHTML = "";
          instance.setValue(getCoordsFromCell(cell), "");
        });
        fireDblClick(cell);
      }
    }
  };

  var calendar = {
    type: "i",
    content: "calendar_today",
    onclick: function (a, b, c) {
      var cell = a.querySelector("td.highlight-selected");
      if (cell && confirm("Data in this column will be erased.")) {
        var worksheet = document.querySelector('.selected').getAttribute('data-spreadsheet');
        var instance = document.querySelector('.spreadsheet').jexcel[worksheet];
        var column = instance.el.querySelectorAll("td[data-x='" + cell.dataset.x + "']");
        var array = [...column];
        instance.options.columns[Number(cell.dataset.x)].type = "calendar";
        array.shift();
        array.forEach(function (cell) {
          cell.innerHTML = "";
          instance.setValue(getCoordsFromCell(cell), "");
        });
        fireDblClick(cell);
      }
    }
  };

  var color = {
    type: "i",
    content: "color_lens",
    onclick: function (a, b, c) {
      var cell = a.querySelector("td.highlight-selected");
      if (cell && confirm("Data in this column will be erased.")) {
        var worksheet = document.querySelector('.selected').getAttribute('data-spreadsheet');
        var instance = document.querySelector('.spreadsheet').jexcel[worksheet];
        var column = instance.el.querySelectorAll("td[data-x='" + cell.dataset.x + "']");
        var array = [...column];
        array.shift();
        array.forEach(function (cell) {
          instance.setValue(getCoordsFromCell(cell), "");
          cell.innerHTML = "<div class='color' style='background-color: rgb(0,0,0);'></div>";
        });
        instance.options.columns[Number(cell.dataset.x)].type = "color";
        fireDblClick(cell);
      }
    }
  };

  rJS(window)

    .declareMethod("getToolbarList", function (add_function, remove_function, dict) {
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
        var remove = {
          type: 'i',
          content: 'delete',
          onclick: remove_function
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
      if (dict.hasOwnProperty("type") && dict.type) {
        list.push(text, image, checkbox, html, calendar, color);
      }
      var res = Object.assign({}, template);
      res.toolbar = list;
      return res;
    })

    .declareMethod("buildOptions", function () {
      var str = "";
      var formulas = ["SUM", "MIN", "MAX", "COUNT", "AVERAGE", "FLOOR", "ABS", "SQRT", "ISEVEN", "ISODD", "TODAY", "UPPER", "LOWER", "TRUNC", "TYPE", "TRIM",
                     "SIN", "COS", "TAN", "ARCSIN", "ARCCOS", "ARCTAN", "ROUND", "RAND", "RANDBETWEEN", "RADIANS", "POWER", "PI", "PHI", "MOD", "LEN", "LN",
                      "LOG", "LOG10", "FACT", "TRUE", "FALSE", "AND", "OR", "XOR", "EVEN", "ODD", "EXP", "CONCATENATE", "BITAND", "BITOR", "BIN2DEC", "BIN2HEX",
                     "BIN2OCT", "DEC2BIN", "DEC2HEX", "DEC2OCT", "HEX2BIN", "HEX2DEC", "HEX2OCT", "NOT", "OCT2BIN", "OCT2DEC", "OCT2HEX", "PRODUCT", "QUOTIENT",
                     "COLUMN", "ROW", "CELL"].sort();
      formulas.forEach(function (value) {
        str += "<option class='formula_option' value=" + value + ">" + value + "()" + "</option>";
      });
      str = "<option class='formula_option'>FORMULA</option>" + str;
      return str;
    });

}(window, rJS, jexcel));
