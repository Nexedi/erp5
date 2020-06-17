/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, jexcel*/
(function (window, rJS, jexcel) {
  "use strict";

  var toolbar_dict = {
    undo_redo: true,
    add: true,
    merge: true,
    text_font: true,
    text_position: true,
    color_picker: true,
    type: true
  };

  var getCoordsFromCell = function (cell) {
    var x = Number(cell.dataset.x);
    var y = Number(cell.dataset.y) + 1;
    return (x >= 26 ? numberToLetter((x / 26 >> 0) - 1) : '') + 'ABCDEFGHIJKLMNOPQRSTWXYZ'[x % 26 >> 0] + y.toString();
  };

  rJS(window)

    .setState({
      saveConfig: false,
      newSheet: false,
      updateSelection: true
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
        gadget.template_gadget = template_gadget;
      })
      .push(function () {
        return gadget.changeState(options);
      });
    })

    .declareMethod('getContent', function () {
      var gadget = this, form_data = {};
      if (this.state.editable) {
        var sheets = [];
        gadget.element.querySelector('.spreadsheet').jexcel.forEach(function (sheet) {
          sheets.push(sheet.getConfig());
        });
        form_data[this.state.key] = JSON.stringify(sheets);
        this.state.value = sheets;
      }
      return form_data;
    })

    .declareMethod("getCurrentSheet", function () {
      var gadget = this;
      var worksheet = gadget.element.querySelector('.selected').getAttribute('data-spreadsheet');
      return gadget.element.querySelector('.spreadsheet').jexcel[worksheet];
    })

    .declareMethod("addSheet", function () {
      var gadget = this;
      return gadget.template_gadget.getToolbarList(() => gadget.addSheet(), toolbar_dict)
      .push(function (dict) {
        dict.sheetName = "Sheet " + (gadget.element.querySelector('.spreadsheet').jexcel.length + 1);
        return gadget.bindEvents(dict);
      })
      .push(function (dict) {
        jexcel.tabs(gadget.element.querySelector(".spreadsheet"), [dict]);
        gadget.deferNotifyChangeBinded()
        return gadget.changeState({newSheet: true});
      });
    })

    .declareMethod("setupTable", function (element) {
      var gadget = this;
      var filter = element.querySelector(".jexcel_filter");
      element.querySelector(".jexcel_toolbar").appendChild(filter);
      document.querySelector("select.jexcel_toolbar_item").classList.add("minimize");
      var formula_div = document.createElement("div");
      formula_div.classList.add("jexcel_formula");
      var img = document.createElement("img");
      img.src = "fx.png";
      var formula_input = document.createElement("input");
      formula_input.classList.add("jexcel_formula");
      formula_div.appendChild(img);
      formula_div.appendChild(formula_input);
      element.querySelector("div.jexcel_toolbar").parentNode.insertBefore(formula_div, element.querySelector("div.jexcel_toolbar").nextSibling);
      var cell_input = document.createElement("input");
      cell_input.classList.add("cell_input");
      formula_div.insertBefore(cell_input, img);
      return gadget.template_gadget.buildOptions()
      .push(function (options) {
        var select = document.createElement("select");
        select.innerHTML = options;
        select.classList.add("minimize");
        select.onclick = function () {
          var select = this;
          var cell = gadget.element.querySelector("td.highlight-selected");
          return gadget.getCurrentSheet()
          .push(function (sheet) {
            var cell = sheet.el.querySelector("td.highlight-selected");
            if (cell) {
              var x = Number(cell.dataset.x);
              var y = Number(cell.dataset.y);
              var currentValue = sheet.getValueFromCoords(x, y);
              var value;
              if (currentValue === "" || currentValue[0] !== "="){
                value = "=" + select.options[select.selectedIndex].value + "(" + currentValue + ")";
              }
              else {
                value = "=" + select.options[select.selectedIndex].value + "(" + currentValue.substring(1, currentValue.length) + ")";
              }
              sheet.setValueFromCoords(x, y, value);
              formula_input.value = value;
            }
          })
        }
        element.querySelector(".jexcel_toolbar").insertBefore(select, filter);
        var icon_title = {
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
          "radio": "Set column type: Radio button",
          "checkbox": "Set column type: Checkbox",
          "title": "Set column type: Text",
          "list": "Set column type: HTML",
          "calendar_today": "Set column type: Calendar",
          "color_lens": "Set column type: Color"
      }
      element.querySelectorAll("i").forEach(i => {
        if (i.dataset.k === "color") {i.title = "Color"}
        else if (i.dataset.k === "background-color") {i.title = "Background color"}
        else {i.title = icon_title[i.textContent]}
      });
      gadget.element.querySelectorAll(".jexcel_tab_link").forEach(tab => tab.title = "Right click to rename");
      gadget.state.newSheet = false;
      });
    })

    .declareMethod("bindEvents", function (sheet) {
      var gadget = this;
      sheet.onevent = function (ev) {
        var exluded_events = ["onload", "onfocus", "onblur", "onselection"];
        if (!exluded_events.includes(ev)) {
          if ((ev === "onchangestyle" && gadget.state.saveConfig) || ev !== "onchangestyle") {
            gadget.deferNotifyChangeBinded();
          }
        }
      };
      sheet.onselection = function (ev) {
        return gadget.getCurrentSheet()
        .push(function (instance) {
          var tab = gadget.element.querySelectorAll(".jexcel_container")[gadget.element.querySelector("div.jexcel_tab_link.selected").getAttribute("data-spreadsheet")];
          var cell = tab.querySelector("td.highlight-selected");
          var cell_input = tab.querySelector("input.cell_input");
          var formula = tab.querySelector("input.jexcel_formula");
          cell_input.value = getCoordsFromCell(cell);
          var x = Number(cell.dataset.x);
          var y = Number(cell.dataset.y);
          formula.value = ["text", "calendar", "checkbox", "color"].includes(instance.options.columns[x].type) ? instance.getValueFromCoords(x, y) : "";
        })
      };
      sheet.oneditionend = function (a, b, c, d, e) {
        if (e[0] === "=" && e[e.length - 1] !== ")") {
          var numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
          if (numbers.includes(e[e.length - 1])){
            var worksheet = gadget.element.querySelector('.selected').getAttribute('data-spreadsheet');
            var tab = gadget.element.querySelector('.spreadsheet').jexcel[worksheet];
            tab.setValueFromCoords(c, d, e);
          }
          else {
            b.textContent = e;
          }
        }
      };
      return sheet;
    })

    .onStateChange(function (modification_dict) {
      var gadget = this, tmp;
      if (modification_dict.hasOwnProperty('newSheet') && modification_dict.newSheet) {
        var tabs = (gadget.element.querySelectorAll(".jexcel_container"));
        return gadget.setupTable(tabs[tabs.length - 1]);
      }
      if (modification_dict.hasOwnProperty('value')) {
        return gadget.template_gadget.getToolbarList(() => gadget.addSheet(), toolbar_dict)
        .push(function (config) {
            tmp = Object.assign({}, config);
            if (gadget.state.value === "") {
              gadget.state.value = [tmp];
            }
            else {
              gadget.state.value = JSON.parse(gadget.state.value);
              gadget.state.value.map(sheet => {
                var res = Object.assign(sheet, tmp);
                return res;
              });
            }
            gadget.state.value.map((sheet, i) => {
              if (!sheet.hasOwnProperty("sheetName")) {sheet.sheetName = "Sheet " + (i + 1)};
              return gadget.bindEvents(sheet);
          });
          return gadget.state.value;
        })
        .push(function (sheets) {
            jexcel.tabs(gadget.element.querySelector(".spreadsheet"), sheets);
            gadget.element.querySelectorAll(".jexcel_container").forEach(tab => {
              return gadget.setupTable(tab);
            })
        });
      }
    })

    .onEvent("input", function (ev) {
        var gadget = this;
        return gadget.getCurrentSheet()
        .push(function (sheet) {
          var formula = sheet.el.querySelector("input.jexcel_formula");
          var td = sheet.el.querySelector("td.highlight-selected");
          if (td && ev.target == td.childNodes[0]) {
            formula.value = ev.target.value;
          }
        })
      }, false, false)

     .onEvent("contextmenu", function (ev) {
        var gadget = this;
        if (ev.target.classList[0] === "jexcel_tab_link") {
          ev.preventDefault();
          var name = prompt("Sheet name :", ev.target.textContent);
          ev.target.textContent = name !== null ? name : ev.target.textContent;
          return gadget.getContent()
          .push(function () {
            var tabs = gadget.element.querySelectorAll(".jexcel_tab_link");
            gadget.state.value.forEach((sheet, i) => {
              sheet.sheetName = tabs[i].textContent;
            });
            gadget.deferNotifyChangeBinded();
          })
        }
      }, false, false)

    .onEvent("click", function (ev) {
      var gadget = this;
      if (ev.target.title === "Delete sheet") {
        gadget.deferNotifyChangeBinded();
      }
    }, false, false);

}(window, rJS, jexcel));
