/*jslint nomen: true, indent: 2, maxlen: 80, unparam: true */
/*global window, rJS, RSVP, jexcel, domsugar, document, alert,
prompt, confirm, navigator*/
(function (window, rJS, jexcel, domsugar, document, alert,
            prompt, confirm, navigator) {
  "use strict";

  function isMobileDevice() {
    return (window.orientation !== undefined) ||
      (navigator.userAgent.indexOf('IEMobile') !== -1);
  }

  function format(node, level) {
    var indentBefore = new Array(level + 2).join('  '),
      indentAfter,
      textNode,
      i;
    level += 1;
    indentAfter = new Array(level - 1).join('  ');
    for (i = 0; i < node.children.length; i += 1) {
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

  function columnLetterToNumber(str) {
    // convert a column letter to its corresponding column number :
    // A -> 0, B -> 1, AA -> 26, AB -> 27 ...
    var out = 0, len = str.length, pos = len;
    while (--pos > -1) {
      out += (str.charCodeAt(pos) - 64) * Math.pow(26, len - 1 - pos);
    }
    return out - 1;
  }

  function numberToColumnLetter(i) {
    // convert a column number to its corresponding column letter :
    // 0 -> A, 1 -> B, 26 -> AA, 27 -> AB ...
    return (i >= 26 ? numberToColumnLetter((i / 26 >> 0) - 1) : '') +
      'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i % 26 >> 0];
  }

  function getCoordinatesFromCell(cell) {
    var x = Number(cell.dataset.x),
      y = Number(cell.dataset.y) + 1;
    return numberToColumnLetter(x) + y.toString();
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
      buttons;
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
    gadget.element.querySelectorAll(".jexcel_tab_link")
      .forEach(function (tab, i) {
        if (i === 0) {
          gadget.state.selectedTabLink = tab;
        }
        tab.title = "Click to rename when selected";
      });
    buttons = domsugar("div", {"class": "add_delete"});
    buttons.appendChild(element.querySelector("i[title='Add table']"));
    buttons.appendChild(element.querySelector("i[title='Delete table']"));
    gadget.element.querySelector(".spreadsheet.jexcel_tabs")
      .appendChild(buttons);
    gadget.state.newSheet = false;
  }

  function bindEvents(gadget, sheet) {
    sheet.onevent = gadget.triggerOnEventSheet.bind(gadget);
    sheet.onselection = gadget.triggerOnSelectionSheet.bind(gadget);
    sheet.oneditionend = gadget.triggerOnEditionEndSheet.bind(gadget);
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
      if (table.classList.contains("jexcel") &&
          !table.classList.contains("jSheet")) {
        if (Array.from(table.querySelectorAll("td")).filter(function (td) {
            return td.hasAttribute("cache");
          }).length === 0) {
          tmp = JSON.parse(table.dataset.config);
          dict.columns = tmp.columns;
          dict.data = tmp.data;
        }
      }
      dict.sheetName = table.title || "Sheet " + (i + 1);
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
        onclick: gadget.triggerUndo.bind(gadget),
        tooltip: "Undo"
      },
      redo: {
        type: 'i',
        content: 'redo',
        onclick: gadget.triggerRedo.bind(gadget),
        tooltip: "Redo"
      },
      merge: {
        type: 'i',
        content: 'table_chart',
        onclick: gadget.triggerMerge.bind(gadget),
        tooltip: "Merge"
      },
      unmerge: {
        type: 'i',
        content: 'close',
        onclick: gadget.triggerUnmerge.bind(gadget),
        tooltip: "Unmerge"
      },
      destroy_merge: {
        type: 'i',
        content: 'cancel',
        onclick: gadget.triggerDestroyMerge.bind(gadget),
        tooltip: "Unmerge all"
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
        v: 'left',
        tooltip: "Align left"
      },
      text_align_center: {
        type: 'i',
        content: 'format_align_center',
        k: 'text-align',
        v: 'center',
        tooltip: "Align center"
      },
      text_align_right: {
        type: 'i',
        content: 'format_align_right',
        k: 'text-align',
        v: 'right',
        tooltip: "Align right"
      },
      text_align_justify: {
        type: 'i',
        content: 'format_align_justify',
        k: 'text-align',
        v: 'justify',
        tooltip: "Align justify"
      },
      vertical_align_top: {
        type: 'i',
        content: 'vertical_align_top',
        k: 'vertical-align',
        v: 'top',
        tooltip: "Align top"
      },
      vertical_align_middle: {
        type: 'i',
        content: 'vertical_align_center',
        k: 'vertical-align',
        v: 'middle',
        tooltip: "Align center"
      },
      vertical_align_bottom: {
        type: 'i',
        content: 'vertical_align_bottom',
        k: 'vertical-align',
        v: 'bottom',
        tooltip: "Align bottom"
      },
      style_bold: {
        type: 'i',
        content: 'format_bold',
        k: 'font-weight',
        v: 'bold',
        tooltip: "Bold"
      },
      style_underlined: {
        type: 'i',
        content: 'format_underlined',
        k: 'text-decoration',
        v: 'underline',
        tooltip: "Underline"
      },
      style_italic: {
        type: 'i',
        content: 'format_italic',
        k: 'font-style',
        v: 'italic',
        tooltip: "Italic"
      },
      text_color: {
        type: 'color',
        content: 'format_color_text',
        k: 'color',
        tooltip: "Text color"
      },
      background_color: {
        type: 'color',
        content: 'format_color_fill',
        k: 'background-color',
        tooltip: "Background color"
      },
      add: {
        type: "i",
        content: "add",
        onclick: gadget.triggerAddSheet.bind(gadget),
        tooltip: "Add table"
      },
      remove: {
        type: "i",
        content: "delete",
        onclick: gadget.triggerDeleteSheet.bind(gadget),
        tooltip: "Delete table"
      },
      add_row: {
        type: "i",
        content: "playlist_add",
        onclick: gadget.triggerAddRow.bind(gadget),
        tooltip: "Add row at the end"
      },
      delete_row: {
        type: "i",
        content: "delete_sweep",
        onclick: gadget.triggerDeleteRow.bind(gadget),
        tooltip: "Delete last row"
      },
      add_column: {
        type: "i",
        content: "exposure_plus_1",
        onclick: gadget.triggerAddColumn.bind(gadget),
        tooltip: "Add column at the end"
      },
      delete_column: {
        type: "i",
        content: "exposure_neg_1",
        onclick: gadget.triggerDeleteColumn.bind(gadget),
        tooltip: "Delete last column"
      },
      dimensions: {
        type: "i",
        content: "photo_size_select_small",
        onclick: gadget.triggerNewDimensions.bind(gadget),
        tooltip: "Resize table"
      },
      contextMenu: function (obj, x, y) {
        var items = [];
        gadget.state.obj = obj;
        gadget.state.x = x;
        gadget.state.y = y;
        if (y === null) {
           // Insert a new column
          items.push({
            title: obj.options.text.insertANewColumnBefore,
            onclick: gadget.triggerInsertNewColumnBefore.bind(gadget)
          });
          items.push({
            title: obj.options.text.insertANewColumnAfter,
            onclick: gadget.triggerInsertNewColumnAfter.bind(gadget)
          });
          // Delete a column
          items.push({
            title: obj.options.text.deleteSelectedColumns,
            onclick: gadget.triggerDeleteSelectedColumns.bind(gadget)
          });
          // Rename column
          items.push({
            title: obj.options.text.renameThisColumn,
            onclick: gadget.triggerRenameColumn.bind(gadget)
          });
          // Sorting
          items.push({ type: 'line' });
          items.push({
            title: obj.options.text.orderAscending,
            onclick: gadget.triggerOrderAscending.bind(gadget)
          });
          items.push({
            title: obj.options.text.orderDescending,
            onclick: gadget.triggerOrderDescending.bind(gadget)
          });
        } else {
          // Insert new row
          items.push({
            title: obj.options.text.insertANewRowBefore,
            onclick: gadget.triggerInsertNewRowBefore.bind(gadget)
          });
          items.push({
            title: obj.options.text.insertANewRowAfter,
            onclick: gadget.triggerInsertNewRowAfter.bind(gadget)
          });
          items.push({
            title: obj.options.text.deleteSelectedRows,
            onclick: gadget.triggerDeleteSelectedRows.bind(gadget)
          });
        }
        if (x) {
          items.push({type: 'line'});
          items.push({
            title: "Set column type: Text",
            onclick: function () {
              return gadget.triggerChangeType("text");
            }
          });
          items.push({
            title: "Set column type: Image",
            onclick: function () {
              return gadget.triggerChangeType("image");
            }
          });
          items.push({
            title: "Set column type: HTML",
            onclick: function () {
              return gadget.triggerChangeType("html");
            }
          });
          items.push({
            title: "Set column type: Checkbox",
            onclick: function () {
              var child = domsugar("input", {type: "checkbox", name: "c" + x});
              return gadget.triggerChangeType("checkbox", child);
            }
          });
          items.push({
            title: "Set column type: Calendar",
            onclick: function () {
              return gadget.triggerChangeType("calendar");
            }
          });
          items.push({
            title: "Set column type: Color",
            onclick: function () {
              return gadget.triggerChangeType("color", null, "square");
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
    if (isMobileDevice()) {
      list.push({
        type: "i",
        content: "photo_library",
        onclick: function (sheet, instance) {
          return gadget.triggerChangeTypeInToolbar(sheet, instance, "image");
        }
      });
      list.push({
        type: "i",
        content: "format_size",
        onclick: function (sheet, instance) {
          return gadget.triggerChangeTypeInToolbar(sheet, instance, "text");
        }
      });
      list.push({
        type: "i",
        content: "format_paint",
        onclick: function (sheet, instance) {
          return gadget.triggerChangeTypeInToolbar(sheet, instance,
                                                   "color", null, "square");
        }
      });
      list.push({
        type: "i",
        content: "format_list_bulleted",
        onclick: function (sheet, instance) {
          return gadget.triggerChangeTypeInToolbar(sheet, instance, "html");
        }
      });
      list.push({
        type: "i",
        content: "calendar_today",
        onclick: function (sheet, instance) {
          return gadget.triggerChangeTypeInToolbar(sheet, instance, "calendar");
        }
      });
      list.push({
        type: "i",
        content: "check_box",
        onclick: function (sheet, instance) {
          var child = domsugar("input", {type: "checkbox"});
          return gadget.triggerChangeTypeInToolbar(sheet, instance,
                                                   "checkbox", child);
        }
      });
    }
    if (toolbar_dict.hasOwnProperty("add_delete_row_column") &&
        toolbar_dict.add_delete_row_column) {
      list.push(dict.add_row, dict.delete_row,
              dict.add_column, dict.delete_column, dict.dimensions);
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
        color_picker: true,
        add_delete_row_column: true
      },
      options: {
        minDimensions: [26, 100],
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
          table.border = "1px";
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
          toolbar_events_config.sheetName = "Table 1";
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
          for (i = 0; i < nodes.length; i += 1) {
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

    .declareJob("triggerAddRow", function (sheet, instance) {
      instance.insertRow();
    })

    .declareJob("triggerDeleteRow", function (sheet, instance) {
      instance.deleteRow(instance.options.data.length - 1, 1);
    })

    .declareJob("triggerInsertNewColumnBefore", function () {
      var state = this.state;
      state.obj.insertColumn(1, parseInt(state.x, 10), 1);
    })

    .declareJob("triggerInsertNewColumnAfter", function () {
      var state = this.state;
      state.obj.insertColumn(1, parseInt(state.x, 10), 0);
    })

    .declareJob("triggerDeleteSelectedColumns", function () {
      var state = this.state;
      state.obj.deleteColumn(state.obj.getSelectedColumns().length ?
                           undefined : parseInt(state.x, 10));
    })

    .declareJob("triggerRenameColumn", function () {
      var state = this.state;
      state.obj.setHeader(state.x);
    })

    .declareJob("triggerOrderAscending", function () {
      var state = this.state;
      state.obj.orderBy(state.x, 0);
    })

    .declareJob("triggerOrderDescending", function () {
      var state = this.state;
      state.obj.orderBy(state.x, 1);
    })

    .declareJob("triggerInsertNewRowBefore", function () {
      var state = this.state;
      state.obj.insertRow(1, parseInt(state.y, 10), 1);
    })

    .declareJob("triggerInsertNewRowAfter", function () {
      var state = this.state;
      state.obj.insertRow(1, parseInt(state.y, 10));
    })

    .declareJob("triggerDeleteSelectedRows", function () {
      var state = this.state;
      state.obj.deleteRow(state.obj.getSelectedRows().length ?
                        undefined : parseInt(state.y, 10));
    })

    .declareJob("triggerAddColumn", function (sheet, instance) {
      instance.insertColumn();
    })

    .declareJob("triggerDeleteColumn", function (sheet, instance) {
      instance.deleteColumn(instance.options.columns.length - 1, 1);
    })

    .declareJob("triggerUndo", function (sheet, instance) {
      instance.undo();
    })

    .declareJob("triggerRedo", function (sheet, instance) {
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

    .declareJob("triggerUnmerge", function (sheet, instance) {
      var cell = document.querySelector("td.highlight-selected"),
        coor = getCoordinatesFromCell(cell);
      instance.removeMerge(coor);
    })

    .declareJob("triggerDestroyMerge", function (sheet, instance) {
      instance.destroyMerged();
    })

    .declareJob("triggerChangeType", function (type, child, render) {
      var state = this.state,
        x = parseInt(state.x, 10),
        y = state.y !== null ? parseInt(state.y, 10) : 0,
        cell,
        column,
        array;
      state.obj.updateSelectionFromCoords(x, y, x, y);
      cell = state.obj.el.querySelector("td.highlight-selected");
      if (state.obj.options.columns[x].type !== type) {
        column = state.obj.el
          .querySelectorAll("td[data-x='" + x + "']");
        array = Array.from(column);
        array.shift();
        setHistoryType(state.obj, "beginChangeType",
                       x,
                       state.obj.options.columns[x].type,
                       type);
        array.forEach(function (cell) {
          state.obj.setValue(getCoordinatesFromCell(cell), "");
          cell.innerHTML = "";
          if (child) {
            cell.appendChild(child.cloneNode());
          }
        });
        setHistoryType(state.obj, "endChangeType",
                       x,
                       state.obj.options.columns[x].type,
                       type);
        state.obj.options.columns[x].type = type;
        if (render) {
          state.obj.options.columns[x].render = render;
        }
        fireDoubleClick(cell);
      }
    })

    .declareJob("triggerChangeTypeInToolbar",
                function (sheet, instance, type, child, render) {
        var cell = sheet.querySelector("td.highlight-selected"),
          x,
          column,
          array;
        x = cell ? parseInt(cell.dataset.x, 10) : null;
        if (cell && instance.options.columns[x].type !== type) {
          column = sheet.querySelectorAll("td[data-x='" + x + "']");
          array = Array.from(column);
          array.shift();
          setHistoryType(instance, "beginChangeType",
                         x,
                         instance.options.columns[x].type,
                         type);
          array.forEach(function (cell) {
            instance.setValue(getCoordinatesFromCell(cell), "");
            cell.innerHTML = "";
            if (child) {
              cell.appendChild(child.cloneNode());
            }
          });
          setHistoryType(instance, "endChangeType",
                         x,
                         instance.options.columns[x].type,
                         type);
          instance.options.columns[x].type = type;
          if (render) {
            instance.options.columns[x].render = render;
          }
          fireDoubleClick(cell);
        }
      })

    .declareJob("triggerNewDimensions", function (sheet, instance) {
      var r = prompt("Number of rows :", instance.options.data.length),
        c = prompt("Number of columns :", instance.options.columns.length);
      if (c > 0 && r > 0) {
        instance.setHistory({action: "beginResizeTable"});
        if (c > instance.options.columns.length) {
          while (instance.options.columns.length < c) {
            instance.insertColumn();
          }
        } else {
          while (instance.options.columns.length > c) {
            instance.deleteColumn(instance.options.columns.length - 1, 1);
          }
        }
        if (r > instance.options.data.length) {
          while (instance.options.data.length < r) {
            instance.insertRow();
          }
        } else {
          while (instance.options.data.length > r) {
            instance.deleteRow(instance.options.data.length - 1, 1);
          }
        }
        instance.setHistory({action: "endResizeTable"});
      }
    })

    .declareJob("triggerAddSheet", function () {
      var gadget = this,
        tabs = gadget.element.querySelectorAll(".jexcel_tab_link"),
        dict1,
        dict2;
      if (tabs.length === 16) {
        alert("Can't add tables anymore.");
      } else {
        dict1 = getTemplate(gadget);
        dict1.sheetName = "Table " +
          (gadget.element.querySelector('.spreadsheet').jexcel.length + 1);
        dict2 = bindEvents(gadget, dict1);
        jexcel.tabs(gadget.element.querySelector(".spreadsheet"), [dict2]);
        gadget.element
          .querySelectorAll('.jexcel_container')[gadget.element.querySelector('.spreadsheet').jexcel.length - 1]
          .querySelectorAll("td[data-x][data-y]")
          .forEach(function (td) {
            td.style.textAlign = "left";
          });
        gadget.deferNotifyChange();
        return gadget.changeState({newSheet: true})
          .push(function () {
            gadget.state.selectedTabLink = gadget.element
              .querySelector(".jexcel_tab_link.selected");
          });
      }
    })

    .declareJob("triggerDeleteSheet", function (sheet, instance) {
      var gadget = this,
        tab_link = gadget.element
          .querySelector('.jexcel_tab_link.selected'),
        index = tab_link.getAttribute("data-spreadsheet"),
        to_remove,
        sheets;
      if (confirm("Delete this table ?")) {
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
              tab.textContent = tab.textContent.substring(0, 5) === "Table" ?
                  "Table " + (i + 1) : tab.textContent;
            });
        } else {
          gadget.element.querySelector('.jexcel_tab_link')
            .textContent = "Table 1";
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
        gadget.state.selectedTabLink = gadget.element
          .querySelector(".jexcel_tab_link.selected");
      }
    })

    .declareJob("triggerOnFocusFormulaInput", function () {
      var gadget = this,
        worksheet = gadget.element.querySelector('.selected')
          .getAttribute('data-spreadsheet');
      gadget.element.querySelector('.spreadsheet').jexcel[worksheet]
        .resetSelection(true);
    })

    .declareJob("triggerOnInputFormulaInput",
              function (cell_input, formula_input) {
        var gadget = this,
          worksheet = gadget.element.querySelector('.selected')
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
      var gadget = this,
        worksheet = gadget.element.querySelector('.selected')
          .getAttribute('data-spreadsheet');
      gadget.element.querySelector('.spreadsheet').jexcel[worksheet]
          .resetSelection(true);
    })

    .declareJob("triggerOnKeyPressCellInput", function (event, input) {
      var gadget = this,
        worksheet,
        x,
        y,
        ys;
      if (event.keyCode === 13) {
        worksheet = gadget.element.querySelector('.selected')
            .getAttribute('data-spreadsheet');
        y = input.value.match(/(\d+)/)[0];
        x = columnLetterToNumber(input.value
                               .substring(0, input.value.length - y.length)
                              );
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
      var gadget = this,
        numbers,
        worksheet,
        tab;
      if (value) {
        if (value[0] === "=" && value[value.length - 1] !== ")") {
          numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
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
          name = prompt("Table name :", ev.target.textContent);
          gadget.state.selectedTabLink.textContent = name !== null ?
              name : gadget.state.selectedTabLink.textContent;
          gadget.deferNotifyChange();
        }
        gadget.state.selectedTabLink = ev.target;
      }
    }, false, false);

}(window, rJS, jexcel, domsugar, document, alert, prompt, confirm, navigator));