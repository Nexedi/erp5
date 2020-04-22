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

    .declareMethod("render", function (options) {
      var gadget = this;
      var state_dict = {
          key: options.key,
          editable: options.editable === undefined ? true : options.editable,
          value: options.value === undefined ? "" : options.value
        };
      return this.changeState(state_dict);
    })

    .declareMethod("updateValue", function () {
      this.state.value = this.table.getConfig();
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;
      var table;
      gadget.deferNotifyChangeBinded = gadget.deferNotifyChange.bind(gadget);
      if (modification_dict.hasOwnProperty('value') && modification_dict.value !== "") {
        modification_dict.value.editable = this.state.editable;
        this.state.value.onchange = gadget.deferNotifyChangeBinded;
        this.state.value.onafterchanges = gadget.updateValue;
        this.state.value.toolbar = null;
        table = jexcel(gadget.element.querySelector(".spreadsheet"), this.state.value);
        jexcel(gadget.element.querySelector(".spreadsheet"), this.state.value);
        this.table = table;
      }
      else {
        table = jexcel(this.element.querySelector(".spreadsheet"), {
          editable: this.state.editable,
          minDimensions: [26, 200],
          defaultColWidth: 100,
          fullscreen: true,
          allowComments: true,
          search: true,
          rowResize: true,
          tableOverflow: true,
          lazyLoading: true,
          loadingSpin: true,
          parseFormulas: false,
          onchange: gadget.deferNotifyChangeBinded,
          onafterchanges: gadget.updateValue,
          toolbar: [
            {
              type: 'i',
              content: 'undo',
              id: "undo"
              //onclick: table.undo
            },
            {
              type: 'i',
              content: 'redo',
              //onclick: table.redo
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
      }
    })
  
    .onEvent("click", function (event) {
      var gadget = this;
      var element = event.target;
      if (element == gadget.element.querySelector(".jexcel_toolbar").childNodes[0]) {
        this.table.undo();
      }
      else if (element == gadget.element.querySelector(".jexcel_toolbar").childNodes[1]) {
        this.table.redo();
      }
    })

    .declareMethod('getContent', function () {
      var form_data = {};
      if (this.state.editable) {
        form_data[this.state.key] = this.table.getConfig();
        this.state.value = form_data[this.state.key];
      }
      return form_data;
    })
  
    ;

}(window, rJS, RSVP, jexcel));