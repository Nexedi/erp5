/*global window, rJS, jIO, RSVP, location, FormData, console */
/*jslint indent: 2, maxlen: 80, nomen: true */
(function (rJS, jIO, RSVP, window, FormData) {
  "use strict";

  rJS(window)
    .declareMethod('render', function (options) {
      return this.changeState({
        test_list: options.test_list,
        run_only: options.run_only,
        debug: options.debug,
        verbose: options.verbose,
        run_test_url: options.run_test_url,
        read_test_url: options.read_test_url,
        // Reset everything on render
        render_timestamp: new Date().getTime(),
        last_call: false,
        data_size: 0,
        test_running: false,
        continue_loop: true,
        paused: false
      });
    })

    .onStateChange(function (modification_dict) {
      if (modification_dict.hasOwnProperty('render_timestamp')) {
        return this.triggerLiveTest();
      }
    })

    .declareJob('triggerLiveTest', function () {
      var form_data = new FormData(),
        gadget = this;

      form_data.append("test_list", gadget.state.test_list);
      form_data.append("run_only", gadget.state.run_only);
      form_data.append("debug", gadget.state.debug);
      form_data.append("verbose", gadget.state.verbose);

      // Reset textarea content
      gadget.element.querySelector('textarea').value = '';

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            // Trigger the test.
            // It is considered as running while the ajax query is not over
            jIO.util.ajax({
              type: "POST",
              url: gadget.state.run_test_url,
              data: form_data
            }),
            // a delay of 2 seconds so the test can be launched
            // before results are read
            RSVP.Queue()
              .push(function () {
                return RSVP.delay(2000);
              })
              .push(function () {
                return gadget.changeState({test_running: true});
              })
          ]);
        }).push(function () {
          var state_dict = {test_running: false};
          // set continue_loop to false ONLY IF the test is not paused.
          // Otherwise it will be set when user scrolls to the end
          if (!gadget.state.paused) {
            state_dict.continue_loop = false;
          }
          return gadget.changeState(state_dict);
        })
        .push(undefined, function (error) {
          console.warn("Error launching live tests", error);
          throw error;
        });
    })

    .onLoop(function () {
      var data_textarea = this.element.querySelector('textarea'),
        gadget = this,
        state_dict = {},
        queue = new RSVP.Queue();

      if (gadget.state.paused) {
        return queue;
      }
      if (!gadget.state.continue_loop) {
        if (gadget.state.last_call) {
          // Stop reading test output
          return queue;
        }
        state_dict.last_call = true;
      }

      return queue
        .push(function () {
          return jIO.util.ajax({
            type: "GET",
            url: gadget.state.read_test_url
          });
        }).push(function (evt) {
          var data = evt.target.response;
          // cut the characters that are already presented
          data = data.substring(gadget.state.data_size);
          if ((!gadget.state.paused) && data.length !== undefined) {
            // to put the data in the correct place
            state_dict.data_size = gadget.state.data_size + data.length;
            // add the new data
            data_textarea.value = data_textarea.value + data;
            data_textarea.scrollTop = data_textarea.scrollHeight;
          }
        }, function (error) {
          // If last call failed, retry
          state_dict.last_call = false;
          console.warn("Error refreshing live test output", error);
        })
        .push(function () {
          return gadget.changeState(state_dict);
        });

    }, 1000)

    .onEvent('scroll', function scrollFunction() {
      var data_textarea = this.element.querySelector('textarea'),
        state_dict = {},
        gadget = this;

      // if the user scrolls in the window we do not want it to be updated.
      // so set paused flag to false
      state_dict.paused =
        (data_textarea.scrollHeight - data_textarea.scrollTop) >
        (data_textarea.clientHeight + 1);
      // if the service was paused when the tests are finished,
      // set continue_loop to false
      if (!gadget.state.paused && !gadget.state.test_running) {
        state_dict.continue_loop = false;
      }
      return gadget.changeState(state_dict);

    });
}(rJS, jIO, RSVP, window, FormData));