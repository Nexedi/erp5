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
      return gadget.changeState(options);
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
        //lazyLoading: true,
        //loadingSpin: true,
        //tableOverflow: true,
        autoIncrement: true,
        parseFormulas: true
      },
      gadget = this, tmp = Object.assign({}, template), table;
      gadget.deferNotifyChangeBinded = gadget.deferNotifyChange.bind(gadget);
      if (modification_dict.hasOwnProperty('value')) {
        gadget.state.value = gadget.state.value === "" ? gadget.state.value : JSON.parse(gadget.state.value);
        Object.assign(tmp, template);
        Object.assign(tmp, gadget.state.value);
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
            },
            //font style
            {
              type: 'select',
              k: 'font-family',
              v: ['Arial', 'Comic Sans MS', 'Verdana', 'Calibri', 'Tahoma', 'Helvetica', 'DejaVu Sans', 'Times New Roman', 'Georgia', 'Antiqua']
            },
            //font size
            {
              type: 'select',
              k: 'font-size',
              v: ['9px', '10px', '11px', '12px', '13px', '14px', '15px', '16px', '17px', '18px', '19px', '20px', '22px', '24px', '26px', '28px', '30px']
            },
            //text align left
            {
              type: 'i',
              content: 'format_align_left',
              k: 'text-align',
              v: 'left'
            },
            //text align center
            {
              type: 'i',
              content: 'format_align_center',
              k: 'text-align',
              v: 'center'
            },
            //text align right
            {
              type: 'i',
              content: 'format_align_right',
              k: 'text-align',
              v: 'right'
            },
            //text align justify
            {
              type: 'i',
              content: 'format_align_justify',
              k: 'text-align',
              v: 'justify'
            },
            //vertical align top
            {
              type: 'i',
              content: 'vertical_align_top',
              k: 'vertical-align',
              v: 'top'
            },
            //vertical align middle
            {
              type: 'i',
              content: 'vertical_align_center',
              k: 'vertical-align',
              v: 'middle'
            },
            //vertical align bottom
            {
              type: 'i',
              content: 'vertical_align_bottom',
              k: 'vertical-align',
              v: 'bottom'
            },
            //style bold
            {
              type: 'i',
              content: 'format_bold',
              k: 'font-weight',
              v: 'bold'
            },
            //style underlined
            {
              type: 'i',
              content: 'format_underlined',
              k: 'text-decoration',
              v: 'underline'
            },
            //style italic
            {
              type: 'i',
              content: 'format_italic',
              k: 'font-style',
              v: 'italic'
            },
            //text color
            {
              type: 'color',
              content: 'format_color_text',
              k: 'color'
            },
            //background color
            {
              type: 'color',
              content: 'format_color_fill',
              k: 'background-color'
            }
          ]
        }));
        gadget.table = table;
        var filter = gadget.element.querySelector(".jexcel_filter");
        gadget.element.querySelector(".jexcel_toolbar").appendChild(filter);
      }
    });

}(window, rJS, jexcel));
