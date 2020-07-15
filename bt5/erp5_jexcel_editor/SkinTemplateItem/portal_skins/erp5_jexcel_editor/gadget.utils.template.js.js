/*jslint nomen: true, indent: 2, maxlen: 80 */
/*global window, rJS, RSVP, jexcel*/
(function (window, rJS, jexcel) {
  "use strict";

  function numberToLetter(i) {
    return (i >= 26 ? numberToLetter((i / 26 >> 0) - 1) : '') +
      'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i % 26 >> 0];
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

  rJS(window)

    .declareMethod("getConfigListFromTables", function (list) {
      var gadget = this, configs = [], dict;
      list.forEach(function (table, i) {
        dict = {};
        if (table.classList.contains("jSheet") || !table.dataset.config) {
          dict = Object.assign(jexcel.createFromTable(table),
                               gadget.state.template);
        } else {
          dict = JSON.parse(table.dataset.config);
          Object.assign(dict, gadget.state.template);
        }
        dict.sheetName = table.dataset.sheetName !== undefined ?
            table.dataset.sheetName : "Sheet " + (i + 1);
        configs.push(dict);
      });
      return configs;
    })

    .declareMethod("getToolbarList",
                 function (parent_gadget,
                          options) {
        var gadget = this, list = [], dict;
        dict = {
          template: {
            minDimensions: [26, 50],
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
          },
          undo: {
            type: 'i',
            content: 'undo',
            onclick: function (a, b) {
              b.undo();
            }
          },
          redo: {
            type: 'i',
            content: 'redo',
            onclick: function (a, b) {
              b.redo();
            }
          },
          merge: {
            type: 'i',
            content: 'table_chart',
            onclick: function (a, b) {
              var cell = a.querySelector("td.highlight"),
                selected = b.getJson(true),
                colspan = Object.keys(selected[0]).length,
                rowspan = selected.length,
                coor = getCoordsFromCell(cell);
              if (confirm("Only top left selected cell's content will be kept")) {
                b.setMerge(coor, colspan, rowspan);
              }
            }
          },
          unmerge: {
            type: 'i',
            content: 'close',
            onclick: function (a, b) {
              var cell = document.querySelector("td.highlight-selected"),
                coor = getCoordsFromCell(cell);
              b.removeMerge(coor);
            }
          },
          destroy_merge: {
            type: 'i',
            content: 'cancel',
            onclick: function (a, b) {
              b.destroyMerged();
            }
          },
          font_style: {
            type: 'select',
            k: 'font-family',
            v: ['Arial', 'Comic Sans MS', 'Verdana', 'Calibri', 'Tahoma',
                'Helvetica', 'DejaVu Sans', 'Times New Roman', 'Georgia',
                'Antiqua']
          },
          font_size: {
            type: 'select',
            k: 'font-size',
            v: ['8px', '10px', '12px', '14px', '16px', '18px', '20px',
                '22px', '24px', '26px', '28px', '30px', '34px', '38px',
                '42px', '46px', '50px']
          },
          text_align_left: {
            type: 'i',
            content: 'format_align_left',
            k: 'text-align',
            v: 'left'
          },
          text_align_center: {
            type: 'i',
            content: 'format_align_center',
            k: 'text-align',
            v: 'center'
          },
          text_align_right: {
            type: 'i',
            content: 'format_align_right',
            k: 'text-align',
            v: 'right'
          },
          text_align_justify: {
            type: 'i',
            content: 'format_align_justify',
            k: 'text-align',
            v: 'justify'
          },
          vertical_align_top: {
            type: 'i',
            content: 'vertical_align_top',
            k: 'vertical-align',
            v: 'top'
          },
          vertical_align_middle: {
            type: 'i',
            content: 'vertical_align_center',
            k: 'vertical-align',
            v: 'middle'
          },
          vertical_align_bottom: {
            type: 'i',
            content: 'vertical_align_bottom',
            k: 'vertical-align',
            v: 'bottom'
          },
          style_bold: {
            type: 'i',
            content: 'format_bold',
            k: 'font-weight',
            v: 'bold'
          },
          style_underlined: {
            type: 'i',
            content: 'format_underlined',
            k: 'text-decoration',
            v: 'underline'
          },
          style_italic: {
            type: 'i',
            content: 'format_italic',
            k: 'font-style',
            v: 'italic'
          },
          text_color: {
            type: 'color',
            content: 'format_color_text',
            k: 'color'
          },
          background_color: {
            type: 'color',
            content: 'format_color_fill',
            k: 'background-color'
          },
          image: {
            type: "i",
            content: "image",
            onclick: function (a) {
              var cell = a.querySelector("td.highlight-selected"),
                worksheet,
                instance;
              if (cell && confirm("Data in this column will be erased.")) {
                worksheet = document.querySelector('.selected')
                  .getAttribute('data-spreadsheet');
                instance = document.querySelector('.spreadsheet')
                  .jexcel[worksheet];
                instance.options.columns[Number(cell.dataset.x)].type = "image";
                fireDblClick(cell);
              }
            }
          },
          checkbox: {
            type: "i",
            content: "checkbox",
            onclick: function (a) {
              var cell = a.querySelector("td.highlight-selected"),
                worksheet,
                instance,
                column,
                array;
              if (cell && confirm("Data in this column will be erased.")) {
                worksheet = document.querySelector('.selected')
                  .getAttribute('data-spreadsheet');
                instance = document.querySelector('.spreadsheet')
                  .jexcel[worksheet];
                column = instance.el
                  .querySelectorAll("td[data-x='" + cell.dataset.x + "']");
                array = [...column];
                array.shift();
                array.forEach(function (cell) {
                  instance.setValue(getCoordsFromCell(cell), "");
                  cell.innerHTML = "<input type='checkbox' name='c" +
                    cell.dataset.x + "'>";
                });
                instance.options.columns[Number(cell.dataset.x)]
                  .type = "checkbox";
              }
            }
          },
          text: {
            type: "i",
            content: "title",
            onclick: function (a) {
              var cell = a.querySelector("td.highlight-selected"),
                worksheet,
                instance,
                column,
                array;
              if (cell && confirm("Data in this column will be erased.")) {
                worksheet = document.querySelector('.selected')
                  .getAttribute('data-spreadsheet');
                instance = document.querySelector('.spreadsheet')
                  .jexcel[worksheet];
                column = instance.el
                  .querySelectorAll("td[data-x='" + cell.dataset.x + "']");
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
          },
          html: {
            type: "i",
            content: "list",
            onclick: function (a) {
              var cell = a.querySelector("td.highlight-selected"),
               worksheet,
                instance,
                column,
                array;
              if (cell && confirm("Data in this column will be erased.")) {
                worksheet = document.querySelector('.selected')
                  .getAttribute('data-spreadsheet');
                instance = document.querySelector('.spreadsheet')
                  .jexcel[worksheet];
                column = instance.el
                  .querySelectorAll("td[data-x='" + cell.dataset.x + "']");
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
          },
          calendar: {
            type: "i",
            content: "calendar_today",
            onclick: function (a) {
              var cell = a.querySelector("td.highlight-selected"),
                worksheet,
                instance,
                column,
                array;
              if (cell && confirm("Data in this column will be erased.")) {
                worksheet = document.querySelector('.selected')
                  .getAttribute('data-spreadsheet');
                instance = document.querySelector('.spreadsheet')
                  .jexcel[worksheet];
                column = instance.el
                  .querySelectorAll("td[data-x='" + cell.dataset.x + "']");
                array = [...column];
                instance.options.columns[Number(cell.dataset.x)]
                  .type = "calendar";
                array.shift();
                array.forEach(function (cell) {
                  cell.innerHTML = "";
                  instance.setValue(getCoordsFromCell(cell), "");
                });
                fireDblClick(cell);
              }
            }
          },
          color: {
            type: "i",
            content: "color_lens",
            onclick: function (a) {
              var cell = a.querySelector("td.highlight-selected"),
                worksheet,
                instance,
                column,
                array;
              if (cell && confirm("Data in this column will be erased.")) {
                worksheet = document.querySelector('.selected')
                  .getAttribute('data-spreadsheet');
                instance = document.querySelector('.spreadsheet')
                  .jexcel[worksheet];
                column = instance.el
                  .querySelectorAll("td[data-x='" + cell.dataset.x + "']");
                array = [...column];
                array.shift();
                array.forEach(function (cell) {
                  instance.setValue(getCoordsFromCell(cell), "");
                  cell.innerHTML = "";
                });
                instance.options.columns[Number(cell.dataset.x)].type = "color";
                instance.options.columns[Number(cell.dataset.x)]
                  .render = "square";
                fireDblClick(cell);
              }
            }
          },
          add: {
            type: "i",
            content: "add",
            onclick: function () {
              var tabs = parent_gadget.element
                .querySelectorAll(".jexcel_tab_link");
              if (tabs.length === 18) {
                alert("Can't add sheets anymore.");
              } else {
                return gadget.getToolbarList(
                    parent_gadget,
                    options
                  )
                      .push(function (dict1) {
                      dict1.sheetName = "Sheet " +
                        (parent_gadget.element.querySelector('.spreadsheet')
                           .jexcel.length + 1);
                      return parent_gadget.bindEvents(dict1)
                      .push(function (dict2) {
                        jexcel.tabs(parent_gadget.element
                                    .querySelector(".spreadsheet"), [dict2]);
                        parent_gadget.element
                          .querySelectorAll('.jexcel_container')[parent_gadget.element.querySelector('.spreadsheet').jexcel.length - 1]
                          .querySelectorAll("td[data-x][data-y]")
                          .forEach(function (td) {
                            td.style.textAlign = "left";
                          });
                        parent_gadget.deferNotifyChangeBinded();
                        return parent_gadget.changeState({newSheet: true});
                      });
                    });
              }
            }
          },
          remove: {
            type: "i",
            content: "remove",
            onclick: function (a, b) {
              var tab_link = parent_gadget.element
                .querySelector('.jexcel_tab_link.selected'),
                index = tab_link.getAttribute("data-spreadsheet"),
                to_remove,
                sheets;
              if (confirm("Delete this sheet ?")) {
                if (parent_gadget.element
                    .querySelector('.spreadsheet').jexcel.length > 1) {
                  tab_link.remove();
                  parent_gadget.element.querySelectorAll(".jexcel_container")
                      .forEach(function (tab) {
                        if (tab.style.display === "block") {
                          to_remove = tab;
                        }
                      });
                  to_remove.remove();
                  parent_gadget.element.querySelector('.spreadsheet')
                    .jexcel.splice(index, 1);
                  sheets = parent_gadget.element
                    .querySelectorAll('.jexcel_container');
                  sheets[sheets.length - 1].style.display = "block";
                  parent_gadget.element.querySelectorAll('.jexcel_tab_link')
                      .forEach(function (tab, i) {
                        if (i === sheets.length - 1) {
                          tab.classList.add("selected");
                        }
                        tab.dataset.spreadsheet = i;
                        tab.textContent = tab.textContent.substring(0, 5) ===
                          "Sheet" ?
                            "Sheet " + (i + 1) : tab.textContent;
                      });
                } else {
                  parent_gadget.element.querySelector('.jexcel_tab_link')
                    .textContent = "Sheet 1";
                  a.querySelector("input.jexcel_formula").value = "";
                  b.setData(new Array(50).fill(0, 49, new Array(26).fill(0, 26, "")));
                }
                parent_gadget.deferNotifyChangeBinded();
              }
            }
          }
        };
        if (options.hasOwnProperty("undo_redo") && options.undo_redo) {
          list.push(dict.undo, dict.redo);
        }
        if (options.hasOwnProperty("add") && options.add) {
          list.push(dict.add, dict.remove);
        }
        if (options.hasOwnProperty("merge") && options.merge) {
          list.push(dict.merge, dict.unmerge, dict.destroy_merge);
        }
        if (options.hasOwnProperty("text_font") && options.text_font) {
          list.push(dict.font_style, dict.font_size, dict.style_bold,
                  dict.style_italic, dict.style_underlined);
        }
        if (options.hasOwnProperty("text_position") && options.text_position) {
          list.push(dict.text_align_left, dict.text_align_center,
                  dict.text_align_right, dict.text_align_justify,
                  dict.vertical_align_top, dict.vertical_align_middle,
                  dict.vertical_align_bottom);
        }
        if (options.hasOwnProperty("color_picker") && options.color_picker) {
          list.push(dict.text_color, dict.background_color);
        }
        if (options.hasOwnProperty("type") && options.type) {
          list.push(dict.text, dict.image, dict.checkbox, dict.html,
                  dict.calendar, dict.color);
        }
        var res = Object.assign({}, dict.template);
        res.toolbar = list;
        return res;
      })

    .declareMethod("buildOptions", function () {
      var str = "",
        formulas;
      formulas = ["SUM", "MIN", "MAX", "COUNT", "AVERAGE", "FLOOR", "ABS",
                "SQRT", "ISEVEN", "ISODD", "TODAY", "UPPER", "LOWER", "TRUNC",
                "TYPE", "TRIM", "SIN", "COS", "TAN", "ARCSIN", "ARCCOS",
                "ARCTAN", "ROUND", "RAND", "RANDBETWEEN", "RADIANS", "POWER",
                "PI", "PHI", "MOD", "LEN", "LN", "LOG", "LOG10", "FACT", "TRUE",
                "FALSE", "AND", "OR", "XOR", "EVEN", "ODD", "EXP",
                "CONCATENATE", "BITAND", "BITOR", "BIN2DEC", "BIN2HEX",
                "BIN2OCT", "DEC2BIN", "DEC2HEX", "DEC2OCT", "HEX2BIN",
                "HEX2DEC", "HEX2OCT", "NOT", "OCT2BIN", "OCT2DEC", "OCT2HEX",
                "PRODUCT", "QUOTIENT", "COLUMN", "ROW", "CELL"].sort();
      formulas.forEach(function (value) {
        str += "<option class='formula_option' value=" + value + ">" + value +
          "()" + "</option>";
      });
      str = "<option class='formula_option'>FORMULA</option>" + str;
      return str;
    });

}(window, rJS, jexcel));
