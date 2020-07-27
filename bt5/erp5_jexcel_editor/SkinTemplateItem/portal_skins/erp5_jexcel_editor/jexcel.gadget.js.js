/*jslint nomen: true, indent: 2, maxlen: 80 */
/*global window, rJS, RSVP, jexcel, domsugar, document, alert, prompt, confirm*/
(function (window, rJS, jexcel, domsugar, document, alert, prompt, confirm) {
  "use strict";

  function format(node, level) {
    var indentBefore = new Array(level + 2).join('  '),
      indentAfter,
      textNode,
      i;
    level += 1;
    indentAfter = new Array(level - 1).join('  ');
    for (i = 0; i < node.children.length; i++) {
      textNode = document.createTextNode('\n' + indentBefore);
      node.insertBefore(textNode, node.children[i]);
      format(node.children[i], level);
      if (node.lastElementChild === node.children[i]) {
        textNode = document.createTextNode('\n' + indentAfter);
        node.appendChild(textNode);
      }
    }
    return node;
  }

  function beautifyHTMLString(str) {
    var div = domsugar("div", {html: str.trim()});
    return format(div, 0).innerHTML;
  }

  function createElementFromHTML(html_string) {
    var div = domsugar("div", {html: html_string.trim()});
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

  function getCoordinatesFromCell(cell) {
    var x = Number(cell.dataset.x),
      y = Number(cell.dataset.y) + 1;
    return numberToLetter(x) + y.toString();
  }

  function fireDoubleClick(element) {
    var clickEvent  = document.createEvent('MouseEvents');
    clickEvent.initEvent('dblclick', true, true);
    element.dispatchEvent(clickEvent);
  }

  function getCurrentSheet(gadget) {
    var worksheet = gadget.element.querySelector('.selected')
          .getAttribute('data-spreadsheet');
    return gadget.element.querySelector('.spreadsheet').jexcel[worksheet];
  }

  function buildSelectOptions() {
    var frag = document.createDocumentFragment(),
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
    frag.appendChild(
      domsugar("option", {text: "FORMULA", "class": "formula_option"})
    );
    formulas.forEach(function (value) {
      frag.appendChild(
        domsugar("option",
                 {"class": "formula_option", text: value + "()", value: value}
                )
      );
    });
    return frag;
  }

  function setupTable(gadget, element) {
    var filter = element.querySelector(".jexcel_filter"),
      formula_div = domsugar("div", {"class": "jexcel_formula"}),
      img = domsugar("img", {src: "fx.png"}),
      formula_input = domsugar("input", {"class": "jexcel_formula"}),
      cell_input = domsugar("input", {"class": "cell_input"}),
      options = buildSelectOptions(),
      select = domsugar("select", {"class": "minimize"}),
      icon_title;
    element.querySelector("table.jexcel tr").childNodes.forEach(function (td) {
      td.style.textAlign = "center";
    });
    element.querySelector(".jexcel_toolbar").appendChild(filter);
    element.querySelector("select.jexcel_toolbar_item")
      .classList.add("minimize");
    formula_div.appendChild(img);
    formula_div.appendChild(formula_input);
    element.querySelector("div.jexcel_toolbar").parentNode
      .insertBefore(formula_div,
                    element.querySelector("div.jexcel_toolbar").nextSibling);
    formula_input.onfocus = gadget.triggerOnFocusFormulaInput.bind(gadget);
    formula_input.oninput = function () {
      return gadget.triggerOnInputFormulaInput(cell_input, this);
    };
    cell_input.onfocus = gadget.triggerOnFocusCellInput.bind(gadget);
    cell_input.onkeypress = function (event) {
      return gadget.triggerOnKeyPressCellInput(event, cell_input);
    };
    formula_div.insertBefore(cell_input, img);
    select.appendChild(options);
    select.onchange = function () {
      var dropdown = this;
      return gadget.triggerOnChangeSelect(dropdown, formula_input);
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
      "vertical_align_bottom": "Align bottom"
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
      .forEach(function (tab, i) {
        if (i === 0) {
          gadget.state.selectedTabLink = tab;
        }
        tab.title = "Click to rename when selected";
      });
    gadget.state.newSheet = false;
  }

  function bindEvents(gadget, sheet) {
    sheet.onevent = function (event) {
      return gadget.triggerOnEventSheet(event);
    };
    sheet.onselection = gadget.triggerOnSelectionSheet.bind(gadget);
    sheet.oneditionend = function (table, cell, x, y, value) {
      return gadget.triggerOnEditionEndSheet(cell, x, y, value);
    };
    return sheet;
  }

  function getConfigListFromTables(gadget, list) {
    var configs = [],
      dict,
      tmp;
    list.forEach(function (table, i) {
      dict = {};
      dict = Object.assign(jexcel.createFromTable(table),
                           gadget.state.template);
      if (!table.classList.contains("jSheet")) {
        tmp = JSON.parse(table.dataset.config);
        dict.columns = tmp.columns;
        dict.data = tmp.data;
      }
      dict.sheetName = table.title ? table.title : "Sheet " + (i + 1);
      configs.push(dict);
    });
    return configs;
  }

  function getTemplate(gadget) {
    var toolbar_dict = gadget.state.toolbar_dict,
      list = [],
      dict,
      res;
    dict = {
      options: gadget.state.options,
      undo: {
        type: 'i',
        content: 'undo',
        onclick: function (a, b) {
          return gadget.triggerUndo(b);
        }
      },
      redo: {
        type: 'i',
        content: 'redo',
        onclick: function (a, b) {
          return gadget.triggerRedo(b);
        }
      },
      merge: {
        type: 'i',
        content: 'table_chart',
        onclick: function (a, b) {
          return gadget.triggerMerge(a, b);
        }
      },
      unmerge: {
        type: 'i',
        content: 'close',
        onclick: function (a, b) {
          return gadget.triggerUnmerge(b);
        }
      },
      destroy_merge: {
        type: 'i',
        content: 'cancel',
        onclick: function (a, b) {
          return gadget.triggerDestroyMerge(b);
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
      add: {
        type: "i",
        content: "add",
        onclick: gadget.triggerAddSheet.bind(gadget)
      },
      remove: {
        type: "i",
        content: "delete",
        onclick: function (a, b) {
          return gadget.triggerDeleteSheet(a, b);
        }
      },
      contextMenu: function (obj, x, y) {
        var items = [];
        if (y !== null) {
           // Insert a new column
          items.push({
            title: obj.options.text.insertANewColumnBefore,
            onclick: function () {
              obj.insertColumn(1, parseInt(x, 10), 1);
            }
          });
          items.push({
            title: obj.options.text.insertANewColumnAfter,
            onclick: function () {
              obj.insertColumn(1, parseInt(x, 10), 0);
            }
          });
          // Delete a column
          items.push({
            title: obj.options.text.deleteSelectedColumns,
            onclick: function () {
              obj.deleteColumn(obj.getSelectedColumns().length ? undefined : parseInt(x, 10));
            }
          });
          // Rename column
          items.push({
            title: obj.options.text.renameThisColumn,
            onclick: function () {
              obj.setHeader(x);
            }
          });
          // Sorting
          items.push({ type: 'line' });
          items.push({
            title: obj.options.text.orderAscending,
            onclick: function () {
              obj.orderBy(x, 0);
            }
          });
          items.push({
            title: obj.options.text.orderDescending,
            onclick: function () {
              obj.orderBy(x, 1);
            }
          });
        } else {
          // Insert new row
          items.push({
            title: obj.options.text.insertANewRowBefore,
            onclick: function () {
              obj.insertRow(1, parseInt(y, 10), 1);
            }
          });
          items.push({
            title: obj.options.text.insertANewRowAfter,
            onclick: function () {
              obj.insertRow(1, parseInt(y, 10));
            }
          });
          items.push({
            title: obj.options.text.deleteSelectedRows,
            onclick: function () {
              obj.deleteRow(obj.getSelectedRows().length ? undefined : parseInt(y, 10));
            }
          });
        }
        if (x) {
          items.push({type: 'line'});
          items.push({
            title: "Set column type: Text",
            onclick: function () {
              return gadget.triggerTextType(obj, x, y);
            }
          });
          items.push({
            title: "Set column type: Image",
            onclick: function () {
              return gadget.triggerImageType(obj, x, y);
            }
          });
          items.push({
            title: "Set column type: HTML",
            onclick: function () {
              return gadget.triggerHTMLType(obj, x, y);
            }
          });
          items.push({
            title: "Set column type: Checkbox",
            onclick: function () {
              return gadget.triggerCheckboxType(obj, x, y);
            }
          });
          items.push({
            title: "Set column type: Color",
            onclick: function () {
              return gadget.triggerColorType(obj, x, y);
            }
          });
        }
        return items;
      }
    };
    if (toolbar_dict.hasOwnProperty("undo_redo") && toolbar_dict.undo_redo) {
      list.push(dict.undo, dict.redo);
    }
    if (toolbar_dict.hasOwnProperty("add") && toolbar_dict.add) {
      list.push(dict.add, dict.remove);
    }
    if (toolbar_dict.hasOwnProperty("merge") && toolbar_dict.merge) {
      list.push(dict.merge, dict.unmerge, dict.destroy_merge);
    }
    if (toolbar_dict.hasOwnProperty("text_font") && toolbar_dict.text_font) {
      list.push(dict.font_style, dict.font_size, dict.style_bold,
              dict.style_italic, dict.style_underlined);
    }
    if (toolbar_dict.hasOwnProperty("text_position") &&
        toolbar_dict.text_position) {
      list.push(dict.text_align_left, dict.text_align_center,
              dict.text_align_right, dict.text_align_justify,
              dict.vertical_align_top, dict.vertical_align_middle,
              dict.vertical_align_bottom);
    }
    if (toolbar_dict.hasOwnProperty("color_picker") &&
        toolbar_dict.color_picker) {
      list.push(dict.text_color, dict.background_color);
    }
    res = Object.assign({}, dict.options);
    res.toolbar = list;
    res.contextMenu = dict.contextMenu;
    return res;
  }

  function setHistoryType(instance, action, column, old_type, new_type) {
    instance.setHistory({
      action: action,
      column: column,
      oldType: old_type,
      newType: new_type
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
        color_picker: true
      },
      options: {
        minDimensions: [26, 50],
        defaultColWidth: 100,
        defaultColAlign: "left",
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
        selectionCopy: true,
        search: true,
        fullscreen: true,
        autoIncrement: true,
        parseFormulas: true,
        wordWrap: true
      }
    })

    .declareAcquiredMethod("notifyChange", "notifyChange")

    .declareMethod("render", function (options) {
      return this.changeState(options);
    })

    .declareMethod('getContent', function () {
      var gadget = this,
        form_data = {},
        res = "",
        sheets = gadget.element.querySelector('.spreadsheet').jexcel,
        tab_links = gadget.element.querySelectorAll('.jexcel_tab_link');
      if (this.state.editable) {
        sheets.forEach(function (sheet, i) {
          var table = sheet.el.querySelector("table.jexcel").cloneNode(true),
            config = sheet.getConfig(),
            dict;
          dict = {
            columns: config.columns,
            data: config.data
          };
          table.dataset.config = JSON.stringify(dict);
          table.title = tab_links[i].textContent;
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
        form_data[this.state.key] = beautifyHTMLString(res);
      }
      return form_data;
    })

    .onStateChange(function (modification_dict) {
      var gadget = this, tabs, i,
        toolbar_config,
        toolbar_events_config,
        nodes,
        data_list,
        selected;
      if (modification_dict.hasOwnProperty('newSheet') &&
          modification_dict.newSheet) {
        tabs = (gadget.element.querySelectorAll(".jexcel_container"));
        return setupTable(gadget, tabs[tabs.length - 1]);
      }
      if (modification_dict.hasOwnProperty('value')) {
        toolbar_config = getTemplate(gadget);
        toolbar_events_config = bindEvents(gadget, toolbar_config);
        if (gadget.state.value === "") {
          toolbar_events_config.sheetName = "Sheet 1";
          jexcel.tabs(gadget.element.querySelector(".spreadsheet"),
                      [toolbar_events_config]
                     );
          gadget.state.tables =
             [gadget.element.querySelector("div.jexcel_content > table")];
          gadget.element
            .querySelectorAll(".jexcel_container")
            .forEach(function (tab) {
              return setupTable(gadget, tab);
            });
        } else {
          gadget.state.tables = [];
          nodes = createElementFromHTML(gadget.state.value);
          for (i = 0; i < nodes.length; i++) {
            gadget.state.tables[i] = nodes[i];
          }
          data_list = getConfigListFromTables(gadget, gadget.state.tables);
          data_list.forEach(function (dict) {
            Object.assign(dict, toolbar_events_config);
          });
          jexcel.tabs(gadget.element.querySelector(".spreadsheet"), data_list);
          gadget.element.querySelectorAll(".jexcel_container")
            .forEach(function (tab) {
              return setupTable(gadget, tab);
            });
          selected = gadget.element
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
        }
      }
    })

    .declareJob("deferNotifyChange", function () {
      return this.notifyChange();
    })

    .declareJob("triggerUndo", function (instance) {
      instance.undo();
    })

    .declareJob("triggerRedo", function (instance) {
      instance.redo();
    })

    .declareJob("triggerMerge", function (sheet, instance) {
      var cell = sheet.querySelector("td.highlight"),
        selected = instance.getJson(true),
        colspan = Object.keys(selected[0]).length,
        rowspan = selected.length,
        coor = getCoordinatesFromCell(cell);
      instance.setMerge(coor, colspan, rowspan);
    })

    .declareJob("triggerUnmerge", function (instance) {
      var cell = document.querySelector("td.highlight-selected"),
        coor = getCoordinatesFromCell(cell);
      instance.removeMerge(coor);
    })

    .declareJob("triggerDestroyMerge", function (instance) {
      instance.destroyMerged();
    })

    .declareJob("triggerImageType", function (obj, cx, cy) {
      var x = parseInt(cx, 10),
        y = cy !== null ? parseInt(cy, 10) : 0,
        cell,
        column,
        array;
      obj.updateSelectionFromCoords(x, y, x, y);
      cell = obj.el.querySelector("td.highlight-selected");
      if (obj.options.columns[x].type !== "image") {
        column = obj.el
          .querySelectorAll("td[data-x='" + x + "']");
        array = [...column];
        array.shift();
        setHistoryType(obj, "beginChangeType",
                       x,
                       obj.options.columns[x].type,
                       "image");
        array.forEach(function (cell) {
          obj.setValue(getCoordinatesFromCell(cell), "");
        });
        setHistoryType(obj, "endChangeType",
                       Number(x),
                       obj.options.columns[x].type,
                       "image");
        obj.options.columns[x].type = "image";
        fireDoubleClick(cell);
      }
    })

    .declareJob("triggerCheckboxType", function (obj, cx, cy) {
      var x = parseInt(cx, 10),
        y = cy !== null ? parseInt(cy, 10) : 0,
        cell,
        column,
        array;
      obj.updateSelectionFromCoords(x, y, x, y);
      cell = obj.el.querySelector("td.highlight-selected");
      if (obj.options.columns[x].type !== "checkbox") {
        column = obj.el
          .querySelectorAll("td[data-x='" + x + "']");
        array = [...column];
        array.shift();
        setHistoryType(obj,
                       "beginChangeType",
                       x,
                       obj.options.columns[x].type,
                       "checkbox");
        array.forEach(function (cell) {
          obj.setValue(getCoordinatesFromCell(cell), "");
          cell.innerHTML = "";
          cell.appendChild(domsugar("input", {
            type: "checkbox",
            name: "c" + x
          }));
        });
        setHistoryType(obj,
                       "endChangeType",
                       x,
                       obj.options.columns[x].type,
                       "checkbox");
        obj.options.columns[x].type = "checkbox";
      }
    })

    .declareJob("triggerTextType", function (obj, cx, cy) {
      var x = parseInt(cx, 10),
        y = cy !== null ? parseInt(cy, 10) : 0,
        cell,
        column,
        array;
      obj.updateSelectionFromCoords(x, y, x, y);
      cell = obj.el.querySelector("td.highlight-selected");
      if (obj.options.columns[x].type !== "text") {
        column = obj.el
          .querySelectorAll("td[data-x='" + x + "']");
        array = [...column];
        array.shift();
        setHistoryType(obj,
                       "beginChangeType",
                       x,
                       obj.options.columns[x].type,
                       "text");
        array.forEach(function (cell) {
          cell.innerHTML = "";
          obj.setValue(getCoordinatesFromCell(cell), "");
        });
        setHistoryType(obj,
                       "endChangeType",
                       x,
                       obj.options.columns[x].type,
                       "text");
        obj.options.columns[x].type = "text";
        fireDoubleClick(cell);
      }
    })

    .declareJob("triggerHTMLType", function (obj, cx, cy) {
      var x = parseInt(cx, 10),
        y = cy !== null ? parseInt(cy, 10) : 0,
        cell,
        column,
        array;
      obj.updateSelectionFromCoords(x, y, x, y);
      cell = obj.el.querySelector("td.highlight-selected");
      if (obj.options.columns[x].type !== "html") {
        column = obj.el
          .querySelectorAll("td[data-x='" + x + "']");
        array = [...column];
        array.shift();
        setHistoryType(obj,
                       "beginChangeType",
                       x,
                       obj.options.columns[x].type,
                       "html");
        array.forEach(function (cell) {
          cell.innerHTML = "";
          obj.setValue(getCoordinatesFromCell(cell), "");
        });
        setHistoryType(obj,
                       "endChangeType",
                       x,
                       obj.options.columns[x].type,
                       "html");
        obj.options.columns[x].type = "html";
        fireDoubleClick(cell);
      }
    })

    .declareJob("triggerColorType", function (obj, cx, cy) {
      var x = parseInt(cx, 10),
        y = cy !== null ? parseInt(cy, 10) : 0,
        cell,
        column,
        array;
      obj.updateSelectionFromCoords(x, y, x, y);
      cell = obj.el.querySelector("td.highlight-selected");
      if (obj.options.columns[x].type !== "color") {
        column = obj.el
          .querySelectorAll("td[data-x='" + x + "']");
        array = [...column];
        array.shift();
        setHistoryType(obj,
                       "beginChangeType",
                       x,
                       obj.options.columns[x].type,
                       "color");
        array.forEach(function (cell) {
          obj.setValue(getCoordinatesFromCell(cell), "");
          cell.innerHTML = "";
        });
        setHistoryType(obj,
                       "endChangeType",
                       x,
                       obj.options.columns[x].type,
                       "color");
        obj.options.columns[x].type = "color";
        obj.options.columns[x].render = "square";
        fireDoubleClick(cell);
      }
    })

    .declareJob("triggerCalendarType", function (obj, cx, cy) {
      var x = parseInt(cx, 10),
        y = cy !== null ? parseInt(cy, 10) : 0,
        cell,
        column,
        array;
      obj.updateSelectionFromCoords(x, y, x, y);
      cell = obj.el.querySelector("td.highlight-selected");
      if (obj.options.columns[x].type !== "calendar") {
        column = obj.el
          .querySelectorAll("td[data-x='" + x + "']");
        array = [...column];
        array.shift();
        setHistoryType(obj,
                       "beginChangeType",
                       x,
                       obj.options.columns[x].type,
                       "calendar");
        array.forEach(function (cell) {
          cell.innerHTML = "";
          obj.setValue(getCoordinatesFromCell(cell), "");
        });
        setHistoryType(obj,
                       "endChangeType",
                       x,
                       obj.options.columns[x].type,
                       "calendar");
        obj.options.columns[x].type = "calendar";
        fireDoubleClick(cell);
      }
    })

    .declareJob("triggerAddSheet", function () {
      var gadget = this;
      var tabs = gadget.element.querySelectorAll(".jexcel_tab_link");
      if (tabs.length === 18) {
        alert("Can't add sheets anymore.");
      } else {
        var dict1 = getTemplate(gadget);
        dict1.sheetName = "Sheet " +
          (gadget.element.querySelector('.spreadsheet').jexcel.length + 1);
        var dict2 = bindEvents(gadget, dict1);
        jexcel.tabs(gadget.element.querySelector(".spreadsheet"), [dict2]);
        gadget.element
          .querySelectorAll('.jexcel_container')[gadget.element.querySelector('.spreadsheet').jexcel.length - 1]
          .querySelectorAll("td[data-x][data-y]")
          .forEach(function (td) {
            td.style.textAlign = "left";
          });
        gadget.state.selectedTabLink = gadget.element.querySelector(".jexcel_tab_link.selected");
        gadget.deferNotifyChange();
        return gadget.changeState({newSheet: true});
      }
    })

    .declareJob("triggerDeleteSheet", function (sheet, instance) {
      var gadget = this;
      var tab_link = gadget.element
        .querySelector('.jexcel_tab_link.selected'),
        index = tab_link.getAttribute("data-spreadsheet"),
        to_remove,
        sheets;
      if (confirm("Delete this sheet ?")) {
        if (gadget.element.querySelector('.spreadsheet').jexcel.length > 1) {
          tab_link.remove();
          gadget.element.querySelectorAll(".jexcel_container")
            .forEach(function (tab) {
              if (tab.style.display === "block") {
                to_remove = tab;
              }
            });
          to_remove.remove();
          gadget.element.querySelector('.spreadsheet').jexcel.splice(index, 1);
          sheets = gadget.element.querySelectorAll('.jexcel_container');
          sheets[sheets.length - 1].style.display = "block";
          gadget.element.querySelectorAll('.jexcel_tab_link')
              .forEach(function (tab, i) {
                if (i === sheets.length - 1) {
                  tab.classList.add("selected");
                }
                tab.dataset.spreadsheet = i;
                tab.textContent = tab.textContent.substring(0, 5) === "Sheet" ?
                    "Sheet " + (i + 1) : tab.textContent;
              });
        } else {
          gadget.element.querySelector('.jexcel_tab_link')
            .textContent = "Sheet 1";
          sheet.querySelector("input.jexcel_formula").value = "";
          instance.setData(new Array(instance.options.columns.length)
            .fill(0, instance.options.columns.length - 1,
                  new Array(instance.options.data.length)
                    .fill(0, instance.options.data.length - 1, "")));
          instance.options.columns.forEach(function (column) {
            column.type = "text";
          });
        }
        gadget.deferNotifyChange();
      }
    })

    .declareJob("triggerOnFocusFormulaInput", function () {
      var gadget = this;
      var worksheet = gadget.element.querySelector('.selected')
        .getAttribute('data-spreadsheet');
      gadget.element.querySelector('.spreadsheet').jexcel[worksheet]
        .resetSelection(true);
    })

    .declareJob("triggerOnInputFormulaInput", function (cell_input, formula_input) {
      var gadget = this;
      var worksheet = gadget.element.querySelector('.selected')
          .getAttribute('data-spreadsheet'),
        instance = gadget.element.querySelector('.spreadsheet')
          .jexcel[worksheet],
        e = formula_input.value,
        numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
      if (e[0] === "=" && e[e.length - 1] !== ")") {
        if (numbers.includes(e[e.length - 1])) {
          instance.setValue(cell_input.value, e);
        }
      } else {
        instance.setValue(cell_input.value, e);
      }
    })

    .declareJob("triggerOnFocusCellInput", function () {
      var gadget = this;
      var worksheet = gadget.element.querySelector('.selected')
          .getAttribute('data-spreadsheet');
      gadget.element.querySelector('.spreadsheet').jexcel[worksheet]
          .resetSelection(true);
    })

    .declareJob("triggerOnKeyPressCellInput", function (event, input) {
      var gadget = this;
      if (event.keyCode === 13) {
        var worksheet = gadget.element.querySelector('.selected')
            .getAttribute('data-spreadsheet'),
          y = input.value.match(/(\d+)/)[0],
          x = letterToNumber(input.value
                               .substring(0, input.value.length - y.length)
                              ),
          ys = parseInt(y, 10) - 1;
        gadget.element.querySelector('.spreadsheet').jexcel[worksheet]
          .updateSelectionFromCoords(x, ys, x, ys);
      }
    })

    .declareJob("triggerOnChangeSelect", function (dropdown, formula_input) {
      var gadget = this,
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
            "(" + currentValue.substring(1, currentValue.length) + ")";
        }
        sheet.setValueFromCoords(x, y, value);
        formula_input.value = value;
      }
      dropdown.selectedIndex = 0;
    })

    .declareJob("triggerOnEventSheet", function (event) {
      var gadget = this,
        exluded_events = ["onload", "onfocus", "onblur", "onselection"];
      if (!exluded_events.includes(event)) {
        if ((["onchangestyle", "onchange", "onbeforechange"].includes(event) &&
             gadget.state.saveConfig) ||
             !["onchangestyle", "onchange", "onbeforechange"].includes(event)) {
          gadget.deferNotifyChange();
        }
      }
    })

    .declareJob("triggerOnSelectionSheet", function () {
      var gadget = this,
        instance = getCurrentSheet(gadget),
        tab = gadget.element
             .querySelectorAll(".jexcel_container")[gadget.element
                                                 .querySelector("div.jexcel_tab_link.selected")
                                                 .getAttribute("data-spreadsheet")],
        cell = tab.querySelector("td.highlight-selected"),
        cell_input = tab.querySelector("input.cell_input"),
        formula = tab.querySelector("input.jexcel_formula"),
        x,
        y;
      cell_input.value = getCoordinatesFromCell(cell);
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
    })

    .declareJob("triggerOnEditionEndSheet", function (cell, x, y, value) {
      var gadget = this;
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
    })

    .onEvent("input", function (ev) {
      var gadget = this, sheet, formula, td;
      sheet = getCurrentSheet(gadget);
      td = sheet.el.querySelector("td.highlight-selected");
      if (td && ev.target === td.childNodes[0]) {
        formula = sheet.el.querySelector("input.jexcel_formula");
        formula.value = ev.target.value;
      }
    }, false, false)

    .onEvent("click", function (ev) {
      var gadget = this, name;
      gadget.state.saveConfig = true;
      if (ev.target.classList.contains("jexcel_tab_link")) {
        if (ev.target === gadget.state.selectedTabLink) {
          name = prompt("Sheet name :", ev.target.textContent);
          gadget.state.selectedTabLink.textContent = name !== null ?
            name : gadget.state.selectedTabLink.textContent;
        }
        gadget.state.selectedTabLink = ev.target;
        gadget.deferNotifyChange();
      }
    }, false, false);

}(window, rJS, jexcel, domsugar, document, prompt, alert, confirm));