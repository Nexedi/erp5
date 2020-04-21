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
      var context = this;
      context.deferNotifyChangeBinded = context.deferNotifyChange.bind(context);
      var table = jexcel(this.element.querySelector(".spreadsheet"), {
          minDimensions: [20, 20],
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
              v: ['Arial', 'Verdana']
            },
            {
              type: 'select',
              k: 'font-size',
              v: ['9px', '10px', '11px', '12px', '13px', '14px', '15px', '16px', '17px', '18px', '19px', '20px']
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
    .declareMethod("render", function (option_dict) {
      var gadget = this;
    })
  
    ;

}(window, rJS, RSVP, jexcel));