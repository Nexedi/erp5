/*global window, rJS, document, RSVP, isEmpty, ensureArray, console */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 200, unparam: true */
(function (window, rJS, document, RSVP, isEmpty, ensureArray, getFirstNonEmpty) {
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
          field_list: field_json.couscous,
          previous_field_length: this.state.field_list.length,
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
        };
      return this.changeState(state_dict)/*
        .push(undefined, function (error) {
          console.warn(error);
          throw error;
        })*/;
    })

    .onStateChange(function () {
      console.log(this.state);
      var gadget = this,
        promise_list = [],
        element = gadget.element,
        i,
        div;

      // First update/create needed gadgets
      for (i = 0; i < gadget.state.field_list.length; i += 1) {
        if (i < gadget.state.previous_field_length) {
          console.log('get', i);
          // Only need to get the existing gadget
          promise_list.push(gadget.getDeclaredGadget(SCOPE_PREFIX + i));
        } else {
          console.log('declare', i);
          div = document.createElement('div');
          gadget.element.appendChild(div);
          promise_list.push(gadget.declareGadget('gadget_erp5_label_field.html',
                            {element: div, scope: SCOPE_PREFIX + i}));
        }
      }

      // And remove all subgadgets not requested anymore
      for (i = gadget.state.previous_field_length - 1; i >= gadget.state.field_list.length; i -= 1) {
        console.log('drop', i);
        promise_list.push(gadget.dropGadget(SCOPE_PREFIX + i));
        element.removeChild(element.lastChild);
      }
      console.log(promise_list);
      return new RSVP.Queue(RSVP.all(promise_list))
        .push(function (gadget_list) {
          console.log(gadget_list, gadget.state.field_list);
          var sub_state;
          promise_list = [];
          for (i = 0; i < gadget.state.field_list.length; i += 1) {
            console.log('render', i);
            sub_state = gadget.state.field_list[i];

            // Compatibility
            if (!sub_state.hasOwnProperty('items')) {
              sub_state.items = sub_state.item_list;
            }
            promise_list.push(gadget_list[i].render({
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
          console.log('contnent', content_list);
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
          console.log('result', result);
          return result;
        });

    }, {mutex: 'changestate'})

    .allowPublicAcquisition('notifyValid', function () {
      return;
    })

    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")

    .declareMethod('checkValidity', function () {
      return true;

      var gadget = this,
        empty = true;
      if (this.state.editable && this.state.required) {
        return new RSVP.Queue()
          .push(function () {
            return RSVP.all([
              gadget.getContent(),
              gadget.translate("Input is required but no input given.")
            ]);
          })
          .push(function (all_result) {
            var value_list = all_result[0][gadget.state.sub_select_key],
              error_message = all_result[1],
              i;
            for (i = 0; i < value_list.length; i += 1) {
              if (value_list[i]) {
                empty = false;
              }
            }
            if (empty) {
              return gadget.notifyInvalid(error_message);
            }
            return gadget.notifyValid();
          })
          .push(function () {
            return !empty;
          });
      }
      return true;
    }, {mutex: 'changestate'});

}(window, rJS, document, RSVP, isEmpty, ensureArray, getFirstNonEmpty));