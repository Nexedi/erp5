/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, jexcel*/
(function (window, rJS, RSVP, jexcel) {
  "use strict";
  
  rJS(window)
    
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
    
    .ready(function () {
      var gadget = this;
      gadget.deferNotifyChangeBinded = gadget.deferNotifyChange.bind(gadget);
      var table = jexcel(this.element.querySelector(".spreadsheet"), {
          minDimensions: [26, 200],
          defaultColWidth: 100,
          fullscreen: true,
          allowComments: true,
          //search: true,
          tableOverflow: true,
          lazyLoading: true,
          loadingSpin: true,
          parseFormulas: false,
          onchange: gadget.deferNotifyChangeBinded,
          toolbar: [
            {
              type: 'i',
              content: 'add',
              onclick: function () {
                gadget.addSheet();
              }
            },
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
              v: ['Arial', 'Arial Black', 'Verdana', 'Impact', 'Comic Sans MS', 'Tahoma', 'Trebuchet MS']
            },
            {
              type: 'select',
              k: 'font-size',
              v: ['20px', '21px', '22px', '23px', '24px', '25px', '26px', '27px', '28px', '29px', '30px', '32px', '34px', '36px', '38px', '40px']
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
        });
      this.table = table;
    })
    
    .declareMethod("render", function (options) {
      var gadget = this;
      var state_dict = {
          key: options.key,
          editable: options.editable === undefined ? true : options.editable
        };
      state_dict.value = options.value || "";
      return this.changeState(state_dict);
    })
  
    .declareMethod("addSheet", function () {
      var gadget = this;
      var sheets = [];
      sheets.push({
          sheetName: 'New tab ' + gadget.element.querySelector('.spreadsheet').jexcel.length,
          minDimensions: [26, 200]
        });
      jexcel.tabs(gadget.element.querySelector('.spreadsheet'), sheets);
    })
  
    .onStateChange(function (modification_dict) {
      if (modification_dict.hasOwnProperty('value')) {
        this.table.setData(this.state.value);
      }
    })
    
    .declareMethod('getContent', function () {
      var form_data = {};
      if (this.state.editable) {
        form_data[this.state.key] = this.table.getData();
        this.state.value = form_data[this.state.key];
      }
      return form_data;
    })
  
    ;

}(window, rJS, RSVP, jexcel));