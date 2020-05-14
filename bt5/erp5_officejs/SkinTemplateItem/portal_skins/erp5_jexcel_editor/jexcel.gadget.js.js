/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, jexcel*/
(function (window, rJS, jexcel) {
  "use strict";

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
    lazyLoading: true,
    loadingSpin: true,
    tableOverflow: true,
    autoIncrement: true,
    parseFormulas: true
  };

  rJS(window)

    .setState({saveStyle: false})

    .declareAcquiredMethod("notifySubmit", "notifySubmit")
    .declareJob("deferNotifySubmit", function () {
      // Ensure error will be correctly handled
      return this.notifySubmit();
    })

    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareJob("deferNotifyChange", function () {
      // Ensure error will be correctly handled
      return this.notifyChange();
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.changeState(options);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this, tmp = Object.assign({}, template), table;
      gadget.deferNotifyChangeBinded = gadget.deferNotifyChange.bind(gadget);
      if (modification_dict.hasOwnProperty('value')) {
        gadget.state.value = gadget.state.value === "" ? gadget.state.value : JSON.parse(gadget.state.value);
        Object.assign(tmp, template);
        Object.assign(tmp, gadget.state.value);
        table = jexcel(gadget.element.querySelector(".spreadsheet"), Object.assign(tmp, {
          onevent: function (ev) {
            var exluded_events = ["onload", "onfocus", "onblur", "onselection"];
            if (!exluded_events.includes(ev)) {
              if ((ev === "onchangestyle" && gadget.state.saveStyle) || ev !== "onchangestyle") {
                gadget.deferNotifyChangeBinded();
              } else {
                gadget.state.saveStyle = true;
              }
            }
          },
          toolbar: [
            {
              type: 'i',
              content: 'undo',
              onclick: function () {
                table.undo();
              }
            },
            {
              type: 'i',
              content: 'redo',
              onclick: function () {
                table.redo();
              }
            },
            {
              type: 'select',
              k: 'font-family',
              v: ['Arial', 'Comic Sans MS', 'Verdana', 'Calibri', 'Tahoma', 'Helvetica', 'DejaVu Sans', 'Times New Roman', 'Georgia', 'Antiqua']
            },
            {
              type: 'select',
              k: 'font-size',
              v: ['9px', '10px', '11px', '12px', '13px', '14px', '15px', '16px', '17px', '18px', '19px', '20px', '22px', '24px', '26px', '28px', '30px']
            },
            {
              type: 'i',
              content: 'format_align_left',
              k: 'text-align',
              v: 'left'
            },
            {
              type: 'i',
              content: 'format_align_center',
              k: 'text-align',
              v: 'center'
            },
            {
              type: 'i',
              content: 'format_align_right',
              k: 'text-align',
              v: 'right'
            },
            {
              type: 'i',
              content: 'format_bold',
              k: 'font-weight',
              v: 'bold'
            },
            {
              type: 'i',
              content: 'format_italic',
              k: 'font-style',
              v: 'italic'
            },
            {
              type: 'color',
              content: 'format_color_text',
              k: 'color'
            },
            {
              type: 'color',
              content: 'format_color_fill',
              k: 'background-color'
            }
          ]
        }));
        this.table = table;
      }
    })

    .declareMethod('getContent', function () {
      var gadget = this, form_data = {};
      if (this.state.editable || true) {
        form_data[this.state.key] = JSON.stringify(gadget.table.getConfig());
        this.state.value = form_data[this.state.key];
      }
      return form_data;
    });

}(window, rJS, jexcel));