/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, jexcel*/
(function (window, rJS, jexcel) {
  "use strict";

  rJS(window)

    .setState({saveConfig: false})

    .declareAcquiredMethod("notifyChange", "notifyChange")

    .declareJob("deferNotifyChange", function () {
      // Ensure error will be correctly handled
      return this.notifyChange();
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.getDeclaredGadget("toolbar_gadget")
      .push(function (toolbar_gadget) {
        gadget.toolbar_gadget = toolbar_gadget;
      })
      .push(function () {
        return gadget.changeState(options);
      });
    })

    .declareMethod('getContent', function () {
      var gadget = this, form_data = {};
      if (this.state.editable || true) {
        form_data[this.state.key] = JSON.stringify(gadget.table.getConfig());
        this.state.value = form_data[this.state.key];
      }
      return form_data;
    })

    .onStateChange(function (modification_dict) {
      var template = {
        minDimensions: [52, 300],
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
        parseFormulas: true
      },
      gadget = this, tmp = Object.assign({}, template), table, toolbar_list;
      gadget.deferNotifyChangeBinded = gadget.deferNotifyChange.bind(gadget);
      if (modification_dict.hasOwnProperty('value')) {
        gadget.state.value = gadget.state.value === "" ? gadget.state.value : JSON.parse(gadget.state.value);
        Object.assign(tmp, template);
        Object.assign(tmp, gadget.state.value);
        return gadget.toolbar_gadget.getToolbarList({
            text_font: true,
            text_position: true,
            color_picker: true
          })
        .push(function (list) {
            toolbar_list = list;
          })
        .push(function () {
            table = jexcel(gadget.element.querySelector(".spreadsheet"), Object.assign(tmp, {
              onevent: function (ev) {
                var exluded_events = ["onload", "onfocus", "onblur", "onselection"];
                if (!exluded_events.includes(ev)) {
                  if ((ev === "onchangestyle" && gadget.state.saveConfig) || ev !== "onchangestyle") {
                    gadget.deferNotifyChangeBinded();
                  } else {
                    gadget.state.saveConfig = true;
                  }
                }
              },
              onselection: function (ev) {
                var cell = gadget.element.querySelector("td.highlight-selected");
                var formula = gadget.element.querySelector("input.jexcel_formula");
                formula.value = cell.textContent;
              },
              toolbar: [
                //undo
                {
                  type: 'i',
                  content: 'undo',
                  onclick: function () {
                    table.undo();
                  }
                },
                //redo
                {
                  type: 'i',
                  content: 'redo',
                  onclick: function () {
                    table.redo();
                  }
                },
                //merge cells
                {
                  type: 'i',
                  content: 'table_chart',
                  onclick: function () {
                    var cell = gadget.element.querySelector("td.highlight-selected");
                    var x = Number(cell.dataset.x);
                    var selected = table.getJson(true);
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
                    table.setMerge(coor, colspan, rowspan);
                  }
                },
                //unmerge cell
                {
                  type: 'i',
                  content: 'close',
                  onclick: function () {
                    var cell = gadget.element.querySelector("td.highlight-selected");
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
                    table.removeMerge(coor);
                  }
                },
                //destroy all merged cells
                {
                  type: 'i',
                  content: 'cancel',
                  onclick: function () {
                    table.destroyMerged();
                  }
                }
              ].concat(toolbar_list)
            }));
            gadget.table = table;
            var filter = gadget.element.querySelector(".jexcel_filter");
            gadget.element.querySelector(".jexcel_toolbar").appendChild(filter);
            var formula_div = document.createElement("div");
            formula_div.classList.add("jexcel_formula");
            var img = document.createElement("img");
            img.src = "fx.png";
            var formula_input = document.createElement("input");
            formula_input.classList.add("jexcel_formula");
            formula_div.appendChild(img);
            formula_div.appendChild(formula_input);
            gadget.element.querySelector("div.jexcel_toolbar").parentNode.insertBefore(formula_div, gadget.element.querySelector("div.jexcel_toolbar").nextSibling);
            console.log(gadget.element.querySelectorAll("i"));
            var icon_title = {
              "undo": "Undo",
              "redo": "Redo",
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
            }
            gadget.element.querySelectorAll("i").forEach(i => {
              if (i.dataset.k === "color") {i.title = "Color"}
              else if (i.dataset.k === "background-color") {i.title = "Background color"}
              else {i.title = icon_title[i.textContent]}
            });
          });
      }
    })

    .onEvent("input", function (ev) {
        var gadget = this;
        var formula = gadget.element.querySelector("input.jexcel_formula");
        if (ev.target == gadget.element.querySelector("td.highlight-selected input")) {
          formula.value = ev.target.value;
        }
      }, false, false)

}(window, rJS, jexcel));
