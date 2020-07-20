/*jslint nomen: true, indent: 2, maxlen: 80 */
/*global window, rJS, RSVP, jexcel*/
(function (window, rJS, jexcel) {
  "use strict";

  function createElementFromHTML(htmlString) {
    var div = document.createElement('div');
    div.innerHTML = htmlString.trim();
    return div.children;
  }

  function letterToNumber(str) {
    var out = 0, len = str.length, pos = len;
    while (--pos > -1) {
      out += (str.charCodeAt(pos) - 64) * Math.pow(26, len - 1 - pos);
    }
    return out - 1;
  }

  function numberToLetter(i) {
    return (i >= 26 ? numberToLetter((i / 26 >> 0) - 1) : '') +
      'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i % 26 >> 0];
  }

  function getCoordsFromCell(cell) {
    var x = Number(cell.dataset.x), y = Number(cell.dataset.y) + 1;
    return numberToLetter(x) + y.toString();
  }

  function getCurrentSheet(gadget) {
    var worksheet = gadget.element.querySelector('.selected')
          .getAttribute('data-spreadsheet');
    return gadget.element.querySelector('.spreadsheet').jexcel[worksheet];
  }

  function setupTable(gadget, element) {
    var filter = element.querySelector(".jexcel_filter"),
      formula_div = document.createElement("div"),
      img = document.createElement("img"),
      formula_input = document.createElement("input"),
      cell_input = document.createElement("input");
    element.querySelector(".jexcel_toolbar").appendChild(filter);
    element.querySelector("select.jexcel_toolbar_item")
      .classList.add("minimize");
    formula_div.classList.add("jexcel_formula");
    img.src = "fx.png";
    formula_input.classList.add("jexcel_formula");
    formula_div.appendChild(img);
    formula_div.appendChild(formula_input);
    element.querySelector("div.jexcel_toolbar").parentNode
      .insertBefore(formula_div,
                    element.querySelector("div.jexcel_toolbar").nextSibling
                   );
    cell_input.classList.add("cell_input");
    formula_input.onfocus = function () {
      var worksheet = gadget.element.querySelector('.selected')
          .getAttribute('data-spreadsheet');
      gadget.element.querySelector('.spreadsheet').jexcel[worksheet]
          .resetSelection(true);
    };
    formula_input.oninput = function () {
      var worksheet = gadget.element.querySelector('.selected')
            .getAttribute('data-spreadsheet'),
        instance = gadget.element.querySelector('.spreadsheet')
            .jexcel[worksheet],
        e = this.value,
        numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
      if (e[0] === "=" && e[e.length - 1] !== ")") {
        if (numbers.includes(e[e.length - 1])) {
          instance.setValue(cell_input.value, e);
        }
      } else {
        instance.setValue(cell_input.value, e);
      }
    };
    cell_input.onfocus = function () {
      var worksheet = gadget.element.querySelector('.selected')
          .getAttribute('data-spreadsheet');
      gadget.element.querySelector('.spreadsheet').jexcel[worksheet]
          .resetSelection(true);
    };
    cell_input.onkeypress = function (ev) {
      if (ev.keyCode === 13) {
        var worksheet = gadget.element.querySelector('.selected')
            .getAttribute('data-spreadsheet'),
          y = this.value.match(/(\d+)/)[0],
          x = letterToNumber(this.value
                               .substring(0, this.value.length - y.length)
                              ),
          ys = parseInt(y, 10) - 1;
        gadget.element.querySelector('.spreadsheet').jexcel[worksheet]
          .updateSelectionFromCoords(x, ys, x, ys);
      }
    };
    formula_div.insertBefore(cell_input, img);
    return gadget.state.template_gadget.buildOptions()
      .push(function (options) {
        var select = document.createElement("select"), icon_title;
        select.innerHTML = options;
        select.classList.add("minimize");
        select.onchange = function () {
          var dropdown = this,
            sheet = getCurrentSheet(gadget),
            cell = sheet.el.querySelector("td.highlight-selected"),
            x,
            y,
            value,
            currentValue;
          if (cell && sheet.options.columns[Number(cell.dataset.x)]
              .type === "text") {
            x = Number(cell.dataset.x);
            y = Number(cell.dataset.y);
            currentValue = sheet.getValueFromCoords(x, y);
            if (currentValue === "" || currentValue[0] !== "=") {
              value = "=" +
                dropdown.options[dropdown.selectedIndex].value +
                "(" + currentValue + ")";
            } else {
              value = "=" +
                dropdown.options[dropdown.selectedIndex].value +
                "(" + currentValue.substring(1, currentValue.length) +
                ")";
            }
            sheet.setValueFromCoords(x, y, value);
            formula_input.value = value;
          }
          dropdown.selectedIndex = 0;
        };
        element.querySelector(".jexcel_toolbar").insertBefore(select, filter);
        icon_title = {
          "undo": "Undo",
          "redo": "Redo",
          "add": "Add sheet",
          "delete": "Delete sheet",
          "table_chart": "Merge cells",
          "close": "Destroy merge",
          "cancel": "Destroy all merges",
          "format_bold": "Bold",
          "format_italic": "Italic",
          "format_underlined": "Underline",
          "format_align_left": "Align left",
          "format_align_center": "Align center",
          "format_align_right": "Align right",
          "format_align_justify": "Align justify",
          "vertical_align_top": "Align top",
          "vertical_align_center": "Align middle",
          "vertical_align_bottom": "Align bottom",
          "image": "Set column type : Image",
          "checkbox": "Set column type: Checkbox",
          "title": "Set column type: Text",
          "list": "Set column type: HTML",
          "calendar_today": "Set column type: Calendar",
          "color_lens": "Set column type: Color"
        };
        element.querySelectorAll("i").forEach(function (i) {
          if (i.dataset.k === "color") {
            i.title = "Color";
          } else if (i.dataset.k === "background-color") {
            i.title = "Background color";
          } else {
            i.title = icon_title[i.textContent];
          }
        });
        gadget.element.querySelectorAll(".jexcel_tab_link")
          .forEach(function (tab) { tab.title = "Right click to rename"; });
        gadget.state.newSheet = false;
      });
  }

  rJS(window)

    .setState({
      saveConfig: false,
      newSheet: false,
      updateSelection: true,
      toolbar_dict: {
        undo_redo: true,
        add: true,
        merge: true,
        text_font: true,
        text_position: true,
        color_picker: true,
        type: true
      }
    })

    .declareAcquiredMethod("notifyChange", "notifyChange")

    .declareJob("deferNotifyChange", function () {
      return this.notifyChange();
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.deferNotifyChangeBinded = gadget.deferNotifyChange.bind(gadget);
      return gadget.getDeclaredGadget("template_gadget")
        .push(function (template_gadget) {
          options.template_gadget = template_gadget;
          gadget.changeState(options);
        });
    })

    .declareMethod('getContent', function () {
      var gadget = this, form_data = {},
        res = "",
        sheets = gadget.element.querySelector('.spreadsheet').jexcel,
        tab_links = gadget.element.querySelectorAll('.jexcel_tab_link');
      if (this.state.editable) {
        sheets.forEach(function (sheet, i) {
          var table = sheet.el.querySelector("table.jexcel").cloneNode(true),
            config = sheet.getConfig(),
            pair_style = Object.entries(config.style).filter(function (pair) {
              return pair[1] !== "text-align: center; white-space: pre-wrap;" &&
                pair[1] !==
                "text-align: center; white-space: pre-wrap; overflow: hidden;";
            }),
            style = {},
            dict;
          pair_style.forEach(function (pair) {
            style[pair[0]] = pair[1];
          });
          dict = {
            colWidths: config.colWidths,
            columns: config.columns,
            data: config.data,
            mergeCells: config.mergeCells,
            style: style,
            rows: config.rows
          };
          table.dataset.config = JSON.stringify(dict);
          table.dataset.sheetName = tab_links[i].textContent;
          table.querySelector("colgroup col").remove();
          table.querySelector("tr").remove();
          table.querySelectorAll("td.jexcel_row").forEach(function (td) {
            td.remove();
          });
          table.querySelectorAll('tr').forEach(function (tr, y) {
            tr.childNodes.forEach(function (td, x) {
              if (td.textContent !== "") {
                var value = sheet.getValueFromCoords(x, y);
                if (value[0] === "=") {
                  td.dataset.formula = value;
                  td.setAttribute('formula', value);
                }
              }
            });
          });
          res += table.outerHTML;
        });
        form_data[this.state.key] = res;
      }
      return form_data;
    })

    .declareMethod("bindEvents", function (sheet) {
      var gadget = this;
      sheet.onevent = function (ev) {
        var exluded_events = ["onload", "onfocus", "onblur", "onselection"];
        if (!exluded_events.includes(ev)) {
          if ((["onchangestyle", "onchange", "onbeforechange"].includes(ev) &&
               gadget.state.saveConfig) ||
              !["onchangestyle", "onchange", "onbeforechange"].includes(ev)) {
            gadget.deferNotifyChangeBinded();
          }
        }
      };
      sheet.onselection = function () {
        var instance = getCurrentSheet(gadget),
          tab = gadget.element
                .querySelectorAll(".jexcel_container")[gadget.element
                                                   .querySelector("div.jexcel_tab_link.selected")
                                                   .getAttribute("data-spreadsheet")],
          cell = tab.querySelector("td.highlight-selected"),
          cell_input = tab.querySelector("input.cell_input"),
          formula = tab.querySelector("input.jexcel_formula"),
          x,
          y;
        cell_input.value = getCoordsFromCell(cell);
        x = Number(cell.dataset.x);
        y = Number(cell.dataset.y);
        formula.value = ["text", "calendar", "checkbox", "color"]
          .includes(instance.options.columns[x].type) ?
              instance.getValueFromCoords(x, y) : "";
        if (instance.options.columns[x].type === "text") {
          formula.readOnly = false;
          formula.classList.remove("readonly");
        } else {
          formula.readOnly = true;
          formula.classList.add("readonly");
        }
      };
      sheet.oneditionend = function (table, cell, x, y, value) {
        if (value) {
          if (value[0] === "=" && value[value.length - 1] !== ")") {
            var numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
              worksheet,
              tab;
            if (numbers.includes(value[value.length - 1])) {
              worksheet = gadget.element.querySelector('.selected')
                .getAttribute('data-spreadsheet');
              tab = gadget.element.querySelector('.spreadsheet')
                .jexcel[worksheet];
              tab.setValueFromCoords(x, y, value);
            } else {
              cell.textContent = value;
            }
          }
        }
      };
      return sheet;
    })

    .onStateChange(function (modification_dict) {
      var gadget = this, tabs, i;
      if (modification_dict.hasOwnProperty('newSheet') &&
          modification_dict.newSheet) {
        tabs = (gadget.element.querySelectorAll(".jexcel_container"));
        return setupTable(gadget, tabs[tabs.length - 1]);
      }
      if (modification_dict.hasOwnProperty('value')) {
        return gadget.state.template_gadget
          .getToolbarList(gadget,
                          gadget.state.toolbar_dict
                         )
          .push(function (toolbar_config) {
            return gadget.bindEvents(toolbar_config)
              .push(function (toolbar_events_config) {
                if (gadget.state.value === "") {
                  toolbar_events_config.sheetName = "Sheet 1";
                  jexcel.tabs(gadget.element.querySelector(".spreadsheet"),
                              [toolbar_events_config]
                             );
                  gadget.element.querySelectorAll("td[data-x][data-y]")
                    .forEach(function (td) {
                      td.style.textAlign = "left";
                    });
                  gadget.state.tables =
                     [gadget.element
                      .querySelector("div.spreadsheet.jexcel_tabs > div:nth-child(2) > div > div.jexcel_content > table")];
                  gadget.element
                    .querySelectorAll(".jexcel_container")
                    .forEach(function (tab) {
                      return setupTable(gadget, tab);
                    });
                } else {
                  gadget.state.tables = [];
                  var nodes = createElementFromHTML(gadget.state.value);
                  for (i = 0; i < nodes.length; i++) {
                    gadget.state.tables[i] = nodes[i];
                  }
                  return gadget.state.template_gadget
                    .getConfigListFromTables(gadget.state.tables)
                    .push(function (data_list) {
                      data_list.forEach(function (dict) {
                        Object.assign(dict, toolbar_events_config);
                      });
                      jexcel.tabs(gadget.element.querySelector(".spreadsheet"),
                                  data_list
                                 );
                      setTimeout(function () {gadget.state.saveConfig = true; },
                                 5000
                                );
                      gadget.element.querySelectorAll(".jexcel_container")
                        .forEach(function (tab) {
                          return setupTable(gadget, tab);
                        });
                      var selected = gadget.element
                        .querySelector('.jexcel_tab_link.selected');
                      selected.classList.remove("selected");
                      gadget.element.querySelector('.jexcel_tab_link')
                        .classList.add("selected");
                      gadget.element.querySelectorAll(".jexcel_container")
                        .forEach(function (tab, i) {
                          if (i === 0) {
                            tab.style.display = "block";
                          } else {
                            tab.style.display = "none";
                          }
                        });
                    });
                }
              });
          });
      }
    })

    .onEvent("input", function (ev) {
      var gadget = this, sheet, formula, td;
      sheet = getCurrentSheet(gadget);
      formula = sheet.el.querySelector("input.jexcel_formula");
      td = sheet.el.querySelector("td.highlight-selected");
      if (td && ev.target === td.childNodes[0]) {
        formula.value = ev.target.value;
      }
    }, false, false)

    .onEvent("contextmenu", function (ev) {
      var gadget = this, name;
      if (ev.target.classList[0] === "jexcel_tab_link") {
        ev.preventDefault();
        name = prompt("Sheet name :", ev.target.textContent);
        ev.target.textContent = name !== null ? name : ev.target.textContent;
        gadget.deferNotifyChangeBinded();
      }
    }, false, false);

}(window, rJS, jexcel));