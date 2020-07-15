/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, jexcel*/
(function (window, rJS, jexcel) {
  "use strict";

  function numberToLetter(i) {
    return (i >= 26 ? numberToLetter((i / 26 >> 0) - 1) : '') + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i % 26 >> 0];
  }

  function getCoordsFromCell(cell) {
    var x = Number(cell.dataset.x), y = Number(cell.dataset.y) + 1;
    return numberToLetter(x) + y.toString();
  }

  function fireDblClick(el) {
    var clickEvent  = document.createEvent('MouseEvents');
    clickEvent.initEvent('dblclick', true, true);
    el.dispatchEvent(clickEvent);
  }

  var template, undo, redo, merge, unmerge, destroy_merge, font_style, font_size, text_align_left, text_align_center, text_align_right, text_align_justify, vertical_align_top, vertical_align_middle, vertical_align_bottom, style_bold, style_underlined, style_italic, text_color, background_color, image, checkbox, radio, text, html, calendar, color;

  template = {
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

  undo = {
    type: 'i',
    content: 'undo',
    onclick: function (a, b) {
      b.undo();
    }
  };

  redo = {
    type: 'i',
    content: 'redo',
    onclick: function (a, b) {
      b.redo();
    }
  };

  merge = {
    type: 'i',
    content: 'table_chart',
    onclick: function (a, b) {
      var cell = a.querySelector("td.highlight"), selected = b.getJson(true), colspan = Object.keys(selected[0]).length, rowspan = selected.length, coor = getCoordsFromCell(cell);
      if (confirm("Top left selected cell's content will be kept, other will be erased.")) {
        b.setMerge(coor, colspan, rowspan);
      }
    }
  };

  unmerge = {
    type: 'i',
    content: 'close',
    onclick: function (a, b) {
      var cell = document.querySelector("td.highlight-selected"), coor = getCoordsFromCell(cell);
      b.removeMerge(coor);
    }
  };

  destroy_merge = {
    type: 'i',
    content: 'cancel',
    onclick: function (a, b) {
      b.destroyMerged();
    }
  };

  font_style = {
    type: 'select',
    k: 'font-family',
    v: ['Arial', 'Comic Sans MS', 'Verdana', 'Calibri', 'Tahoma', 'Helvetica', 'DejaVu Sans', 'Times New Roman', 'Georgia', 'Antiqua']
  };

  font_size = {
    type: 'select',
    k: 'font-size',
    v: ['8px', '10px', '12px', '14px', '16px', '18px', '20px', '22px', '24px', '26px', '28px', '30px', '34px', '38px', '42px', '46px', '50px']
  };

  text_align_left = {
    type: 'i',
    content: 'format_align_left',
    k: 'text-align',
    v: 'left'
  };

  text_align_center = {
    type: 'i',
    content: 'format_align_center',
    k: 'text-align',
    v: 'center'
  };

  text_align_right = {
    type: 'i',
    content: 'format_align_right',
    k: 'text-align',
    v: 'right'
  };

  text_align_justify = {
    type: 'i',
    content: 'format_align_justify',
    k: 'text-align',
    v: 'justify'
  };

  vertical_align_top = {
    type: 'i',
    content: 'vertical_align_top',
    k: 'vertical-align',
    v: 'top'
  };

  vertical_align_middle = {
    type: 'i',
    content: 'vertical_align_center',
    k: 'vertical-align',
    v: 'middle'
  };

  vertical_align_bottom = {
    type: 'i',
    content: 'vertical_align_bottom',
    k: 'vertical-align',
    v: 'bottom'
  };

  style_bold = {
    type: 'i',
    content: 'format_bold',
    k: 'font-weight',
    v: 'bold'
  };

  style_underlined = {
    type: 'i',
    content: 'format_underlined',
    k: 'text-decoration',
    v: 'underline'
  };

  style_italic = {
    type: 'i',
    content: 'format_italic',
    k: 'font-style',
    v: 'italic'
  };
  text_color = {
    type: 'color',
    content: 'format_color_text',
    k: 'color'
  };
  background_color = {
    type: 'color',
    content: 'format_color_fill',
    k: 'background-color'
  };

  image = {
    type: "i",
    content: "image",
    onclick: function (a) {
      var cell = a.querySelector("td.highlight-selected"), worksheet, instance;
      if (cell && confirm("Data in this column will be erased.")) {
        worksheet = document.querySelector('.selected').getAttribute('data-spreadsheet');
        instance = document.querySelector('.spreadsheet').jexcel[worksheet];
        instance.options.columns[Number(cell.dataset.x)].type = "image";
        fireDblClick(cell);
      }
    }
  };

  checkbox = {
    type: "i",
    content: "checkbox",
    onclick: function (a) {
      var cell = a.querySelector("td.highlight-selected"), worksheet, instance, column, array;
      if (cell && confirm("Data in this column will be erased.")) {
        worksheet = document.querySelector('.selected').getAttribute('data-spreadsheet');
        instance = document.querySelector('.spreadsheet').jexcel[worksheet];
        column = instance.el.querySelectorAll("td[data-x='" + cell.dataset.x + "']");
        array = [...column];
        array.shift();
        array.forEach(function (cell) {
          instance.setValue(getCoordsFromCell(cell), "");
          cell.innerHTML = "<input type='checkbox' name='c" + cell.dataset.x + "'>";
        });
        instance.options.columns[Number(cell.dataset.x)].type = "checkbox";
      }
    }
  };

  text = {
    type: "i",
    content: "title",
    onclick: function (a) {
      var cell = a.querySelector("td.highlight-selected"), worksheet, instance, column, array;
      if (cell && confirm("Data in this column will be erased.")) {
        var worksheet = document.querySelector('.selected').getAttribute('data-spreadsheet');
        instance = document.querySelector('.spreadsheet').jexcel[worksheet];
        column = instance.el.querySelectorAll("td[data-x='" + cell.dataset.x + "']");
        array = [...column];
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

  html = {
    type: "i",
    content: "list",
    onclick: function (a) {
      var cell = a.querySelector("td.highlight-selected"), worksheet, instance, column, array;
      if (cell && confirm("Data in this column will be erased.")) {
        var worksheet = document.querySelector('.selected').getAttribute('data-spreadsheet');
        instance = document.querySelector('.spreadsheet').jexcel[worksheet];
        column = instance.el.querySelectorAll("td[data-x='" + cell.dataset.x + "']");
        array = [...column];
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

  calendar = {
    type: "i",
    content: "calendar_today",
    onclick: function (a) {
      var cell = a.querySelector("td.highlight-selected"), worksheet, instance, column, array;
      if (cell && confirm("Data in this column will be erased.")) {
        var worksheet = document.querySelector('.selected').getAttribute('data-spreadsheet');
        instance = document.querySelector('.spreadsheet').jexcel[worksheet];
        column = instance.el.querySelectorAll("td[data-x='" + cell.dataset.x + "']");
        array = [...column];
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

  color = {
    type: "i",
    content: "color_lens",
    onclick: function (a) {
      var cell = a.querySelector("td.highlight-selected"), worksheet, instance, column, array;
      if (cell && confirm("Data in this column will be erased.")) {
        var worksheet = document.querySelector('.selected').getAttribute('data-spreadsheet');
        instance = document.querySelector('.spreadsheet').jexcel[worksheet];
        column = instance.el.querySelectorAll("td[data-x='" + cell.dataset.x + "']");
        array = [...column];
        array.shift();
        array.forEach(function (cell) {
          instance.setValue(getCoordsFromCell(cell), "");
          cell.innerHTML = "";
        });
        instance.options.columns[Number(cell.dataset.x)].type = "color";
        instance.options.columns[Number(cell.dataset.x)].render = "square";
        fireDblClick(cell);
      }
    }
  };

  rJS(window)

    .declareMethod("getConfigListFromTables", function (list) {
        var gadget = this, configs = [], dict;
        list.forEach(function (table, i) {
          dict = {};
          if (table.classList.contains("jSheet") || !table.dataset.config) {
            dict = Object.assign(jexcel.createFromTable(table), template);
          }
          else {
            dict = JSON.parse(table.dataset.config);
            Object.assign(dict, template);
          }
          dict.sheetName = table.dataset.sheetName !== undefined ? table.dataset.sheetName : "Sheet " + (i + 1);
          configs.push(dict);
        });
        return configs;
      })

    .declareMethod("getToolbarList", function (add_function, remove_function, dict) {
      var list = [], add, remove;
      if (dict.hasOwnProperty("undo_redo") && dict.undo_redo) {
        list.push(undo, redo);
      }
      if (dict.hasOwnProperty("add") && dict.add) {
        add = {
          type: 'i',
          content: 'add',
          onclick : add_function
        };
        remove = {
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
      var str = "", formulas;
      formulas = ["SUM", "MIN", "MAX", "COUNT", "AVERAGE", "FLOOR", "ABS", "SQRT", "ISEVEN", "ISODD", "TODAY", "UPPER", "LOWER", "TRUNC", "TYPE", "TRIM",
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
