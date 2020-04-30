/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, jexcel*/
(function (window, rJS, RSVP, jexcel) {
  "use strict";

  var template = {editable: this.state.editable,
                  minDimensions: [26, 200],
                  defaultColWidth: 100,
                  fullscreen: true,
                  allowComments: true,
                  search: true,
                  rowResize: true,
                  tableOverflow: true,
                  lazyLoading: true,
                  loadingSpin: true,
                  parseFormulas: false};

  rJS(window)

    //// Acquired methods /////////////////////////////////////

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

    // call changeState to render the gadget
    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.changeState(options);
    })

    // Initialize the jexcel sheet, didn't find the way to not duplicate the sheet config
    // because jexcel need the "table" var fot the toolbar config that is initializing
    .onStateChange(function (modification_dict) {
      var gadget = this;
      var table;
      gadget.deferNotifyChangeBinded = gadget.deferNotifyChange.bind(gadget);
      // if the value key is set in the options dict of render method
      if (modification_dict.hasOwnProperty('value')) {
        var tmp = Object.assign({}, template);
        Object.assign(tmp, gadget.state.value);
        Object.assign(template, this.state.value);
        table = jexcel(gadget.element.querySelector(".spreadsheet"), Object.assign(tmp, {
          editable: gadget.state.editable,
          onchange: gadget.deferNotifyChangeBinded,
          toolbar: [
            {
              type: 'i',
              content: 'undo',
              id: "undo",
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
        }));
        this.table = table;
      }
    })

    .declareMethod('getContent', function () {
      var form_data = {};
      if (this.state.editable) {
        form_data[this.state.key] = JSON.stringify(this.table.getConfig());
        this.state.value = form_data[this.state.key];
      }
      return form_data;
    });

}(window, rJS, RSVP, jexcel));