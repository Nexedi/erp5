/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, jexcel*/
(function (window, rJS, jexcel) {
  "use strict";

  rJS(window)

    .setState({
      saveConfig: false,
      newSheet: false
    })

    .declareAcquiredMethod("notifyChange", "notifyChange")

    .declareJob("deferNotifyChange", function () {
      return this.notifyChange();
    })

    .declareMethod("render", function (options) {
      var gadget = this;
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

    .declareMethod("addSheet", function () {
      var gadget = this;
      return gadget.template_gadget.getToolbarList(() => gadget.addSheet(), {
        undo_redo: true,
        add: true,
        merge: true,
        text_font: true,
        text_position: true,
        color_picker: true
      })
      .push(function (dict) {
        dict.sheetName = "Sheet " + (gadget.element.querySelector('.spreadsheet').jexcel.length + 1);
        return gadget.bindEvents(dict);
      })
      .push(function (dict) {
        jexcel.tabs(gadget.element.querySelector(".spreadsheet"), [dict]);
        return gadget.changeState({newSheet: true});
      });
    })

    .declareMethod("setupTable", function (element) {
      var filter = element.querySelector(".jexcel_filter");
      element.querySelector(".jexcel_toolbar").appendChild(filter);
      var formula_div = document.createElement("div");
      formula_div.classList.add("jexcel_formula");
      var img = document.createElement("img");
      img.src = "fx.png";
      var formula_input = document.createElement("input");
      formula_input.classList.add("jexcel_formula");
      formula_div.appendChild(img);
      formula_div.appendChild(formula_input);
      element.querySelector("div.jexcel_toolbar").parentNode.insertBefore(formula_div, element.querySelector("div.jexcel_toolbar").nextSibling);
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
      }
      element.querySelectorAll("i").forEach(i => {
        if (i.dataset.k === "color") {i.title = "Color"}
        else if (i.dataset.k === "background-color") {i.title = "Background color"}
        else {i.title = icon_title[i.textContent]}
      });
      gadget.state.newSheet = false;
    })

    .declareMethod("bindEvents", function (sheet) {
      var gadget = this;
      gadget.deferNotifyChangeBinded = gadget.deferNotifyChange.bind(gadget);
      sheet.onevent = function (ev) {
        var exluded_events = ["onload", "onfocus", "onblur", "onselection"];
        if (!exluded_events.includes(ev)) {
          if ((ev === "onchangestyle" && gadget.state.saveConfig) || ev !== "onchangestyle") {
            gadget.deferNotifyChangeBinded();
          }
        }
      };
      sheet.onselection = function (ev) {
        gadget.state.saveConfig = true;
        var tab = gadget.element.querySelectorAll(".jexcel_container")[gadget.element.querySelector("div.jexcel_tab_link.selected").getAttribute("data-spreadsheet")];
        var cell = tab.querySelector("td.highlight-selected");
        var formula = tab.querySelector("input.jexcel_formula");
        formula.value = cell.textContent;
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
        return gadget.template_gadget.getToolbarList(() => gadget.addSheet(), {
            undo_redo: true,
            add: true,
            merge: true,
            text_font: true,
            text_position: true,
            color_picker: true
        })
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
        var tab = gadget.element.querySelectorAll(".jexcel_container")[gadget.element.querySelector("div.jexcel_tab_link.selected").getAttribute("data-spreadsheet")];
        var formula = tab.querySelector("input.jexcel_formula");
        if (ev.target == tab.querySelector("textarea")) {
          formula.value = ev.target.value;
        }
      }, false, false)

     .onEvent("dblclick", function (ev) {
        var gadget = this;
        gadget.deferNotifyChangeBinded = gadget.deferNotifyChange.bind(gadget);
        if (ev.target.classList[0] === "jexcel_tab_link") {
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
      }, true, false);

}(window, rJS, jexcel));
