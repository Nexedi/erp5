/*global window, rJS, document, RSVP, ensureArray */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
(function (window, rJS, document, RSVP, ensureArray) {
  'use strict';

  var SCOPE_PREFIX = 'PARALLEL_SUB_FIELD_';

  function endsWith(str, suffix) {
    // http://simonwillison.net/2006/Jan/20/escape/
    suffix = suffix.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g, "\\$&");
    return (new RegExp(suffix + '$', 'i')).test(str);
  }

  rJS(window)
    .setState({
      previous_field_length: 0,
      field_list: []
    })
    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        state_dict = {
          field_list: field_json.subfield_list,
          previous_field_length: this.state.field_list.length,
          editable: field_json.editable,
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var gadget = this,
        promise_list = [],
        element = gadget.element,
        i,
        div;

      // First update/create needed gadgets
      for (i = 0; i < gadget.state.field_list.length; i += 1) {
        if (i < gadget.state.previous_field_length) {
          // Only need to get the existing gadget
          promise_list.push(gadget.getDeclaredGadget(SCOPE_PREFIX + i));
        } else {
          div = document.createElement('div');
          gadget.element.appendChild(div);
          promise_list.push(gadget.declareGadget('gadget_erp5_label_field.html',
                            {element: div, scope: SCOPE_PREFIX + i}));
        }
      }

      // And remove all subgadgets not requested anymore
      for (i = gadget.state.previous_field_length - 1;
           i >= gadget.state.field_list.length; i -= 1) {
        promise_list.push(gadget.dropGadget(SCOPE_PREFIX + i));
        element.removeChild(element.lastChild);
      }
      return new RSVP.Queue(RSVP.all(promise_list))
        .push(function (gadget_list) {
          var sub_state;
          promise_list = [];
          for (i = 0; i < gadget.state.field_list.length; i += 1) {
            sub_state = JSON.parse(JSON.stringify(gadget.state.field_list[i]));
            sub_state.editable = gadget.state.editable;
            promise_list.push(gadget_list[i].render({
              development_link: false,
              field_json: sub_state,
              field_type: sub_state.field_type
            }));
          }
          return RSVP.all(promise_list);
        });
    })

    .declareMethod('getContent', function () {
      var gadget = this,
        i,
        promise_list = [];

      for (i = 0; i < gadget.state.field_list.length; i += 1) {
        promise_list.push(gadget.getDeclaredGadget(SCOPE_PREFIX + i));
      }

      return new RSVP.Queue(RSVP.all(promise_list))
        .push(function (gadget_list) {
          promise_list = [];
          for (i = 0; i < gadget_list.length; i += 1) {
            promise_list.push(gadget_list[i].getContent());
          }
          return RSVP.all(promise_list);
        })
        .push(function (content_list) {
          var result = {},
            key,
            j,
            concat_list;
          for (i = 0; i < content_list.length; i += 1) {
            for (key in content_list[i]) {
              if (content_list[i].hasOwnProperty(key)) {
                if (result.hasOwnProperty(key) && endsWith(key, ':list')) {
                  result[key] = ensureArray(result[key]);
                  concat_list = ensureArray(content_list[i][key]);
                  for (j = 0; j < concat_list.length; j += 1) {
                    result[key].push(concat_list[j]);
                  }
                  // XXX
                } else {
                  result[key] = content_list[i][key];
                }
              }
            }
          }
          return result;
        });

    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, document, RSVP, ensureArray));