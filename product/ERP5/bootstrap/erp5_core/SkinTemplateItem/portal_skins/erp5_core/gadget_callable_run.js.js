/*global window, rJS, RSVP, jIO, Handlebars, document, FormData */
/*jslint nomen: true, maxlen:150, indent:2*/
(function (rJS, jIO, RSVP, window, Handlebars) {
  "use strict";
  var gk = rJS(window),
    run_source = gk.__template_element.getElementById('run').innerHTML,
    run_template = Handlebars.compile(run_source);

  function loopEventListener(target, type, useCapture, callback,
                                       prevent_default) {
    //////////////////////////
    // Infinite event listener (promise is never resolved)
    // eventListener is removed when promise is cancelled/rejected
    //////////////////////////
    var handle_event_callback,
      callback_promise;

    if (prevent_default === undefined) {
      prevent_default = true;
    }

    function cancelResolver() {
      if ((callback_promise !== undefined) &&
          (typeof callback_promise.cancel === "function")) {
        callback_promise.cancel();
      }
    }

    function canceller() {
      if (handle_event_callback !== undefined) {
        target.removeEventListener(type, handle_event_callback, useCapture);
      }
      cancelResolver();
    }
    function itsANonResolvableTrap(resolve, reject) {
      var result;
      handle_event_callback = function (evt) {
        if (prevent_default) {
          evt.stopPropagation();
          evt.preventDefault();
        }

        cancelResolver();

        try {
          result = callback(evt);
        } catch (e) {
          result = RSVP.reject(e);
        }

        callback_promise = result;
        new RSVP.Queue()
          .push(function () {
            return result;
          })
          .push(undefined, function (error) {
            if (!(error instanceof RSVP.CancellationError)) {
              canceller();
              reject(error);
            }
          });
      };

      target.addEventListener(type, handle_event_callback, useCapture);
    }
    return new RSVP.Promise(itsANonResolvableTrap, canceller);
  }

  function getLog(gadget) {
    return jIO.util.ajax(
      {
        "type": "POST",
        "url":  gadget.props.value_list.log_url,
        "xhrFields": {
          withCredentials: true
        }
      }
    );
  }

  rJS(window)
    .ready(function (g) {
      g.props = {};
      g.props.deferred = new RSVP.defer();
    })
    .declareMethod("render", function (options) {
      var param_list,
        value_list,
        gadget = this;
      value_list = options.value.replace(/\'/gi, "\"");
      value_list = JSON.parse(value_list);
      if (value_list.param_list) {
        param_list = value_list.param_list.split(',');
        value_list.param_list = param_list;
      }
      gadget.props.value_list = value_list;
      gadget.element.querySelector('form').innerHTML = run_template({param_list: param_list});
      return gadget.props.deferred.resolve();
    })
    .declareService(function () {
      var gadget = this,
        test_output,
        test_error;
      function run(data) {
        gadget.props.output = "";
        test_error.innerHTML = "";
        test_output.value = "";
        return RSVP.Queue()
          .push(function () {
            return getLog(gadget);
          })
          .push(function (result) {
            gadget.props.last_result = result.target.response.split("\n");
            gadget.props.last_result = gadget.props.last_result[gadget.props.last_result.length - 2];
            return jIO.util.ajax(
              {
                "type": "POST",
                "url":  gadget.props.value_list.output_url,
                "xhrFields": {
                  withCredentials: true
                },
                "data": data
              }
            );
          })
          .push(function (result) {
            gadget.props.output = result.target.response;
            return getLog(gadget);
          }, function (error) {
            var tmp = document.createElement('div');
            tmp.innerHTML = error.target.response;
            tmp = tmp.querySelector('.master');
            test_error.appendChild(tmp);
            return getLog(gadget);
          })
          .push(function (result) {
            var currentLogValue = result.target.response.split("\n"),
              i,
              log = "";
            i = currentLogValue.lastIndexOf(gadget.props.last_result) + 1;
            for (; i < currentLogValue.length; i += 1) {
              log += currentLogValue[i] + "\n";
            }
            test_output.value = log + gadget.props.output;
            test_output.scrollTop = test_output.scrollHeight;
          });
      }
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          test_output = gadget.element.querySelector('.test_output');
          test_error = gadget.element.querySelector('.test_error');
          if (!gadget.props.value_list.param_list) {
            return run();
          }
        })
        .push(function () {
          return loopEventListener(
            gadget.element.querySelector('form'),
            'submit',
            false,
            function () {
              var data_list = new FormData(),
                input,
                i;
              if (gadget.props.value_list.param_list) {
                for (i = 0; i < gadget.props.value_list.param_list.length; i += 1) {
                  input = gadget.element.querySelector('.' + gadget.props.value_list.param_list[i]);
                  if (input.value) {
                    data_list.append(input.className, input.value);
                  }
                }
              }
              return run(data_list);
            }
          );
        });
    });
}(rJS, jIO, RSVP, window, Handlebars));