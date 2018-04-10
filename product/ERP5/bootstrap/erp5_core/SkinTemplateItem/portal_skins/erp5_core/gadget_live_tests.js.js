/*global window, rJS, jIO, RSVP, location, document, FormData, console */
/*jslint indent: 2, maxlen: 80, nomen: true */
(function (rJS, jIO, RSVP, window, document, FormData) {
  "use strict";
  var my_url_run_test = document.baseURI + 'runLiveTest',
    my_url_read_test = document.baseURI + 'readTestOutput',
    paused = false,
    data_textarea =
      document.querySelector("[name='field_your_text_output']"),
    continue_loop = true,
    tests_still_running = true,
    last_call = false,
    data_size = 0,
    form_data = new FormData();

  data_textarea.value = "";

  form_data.append("test_list",
    document.querySelector("[name='field_your_test']").value);
  form_data.append("run_only",
    document.querySelector("[name='field_your_run_only']").value);
  form_data.append("debug",
    document.querySelector("[name='field_your_debug']").checked ===
       true ? 1 : 0);
  form_data.append("verbose",
    document.querySelector("[name='field_your_verbose']").checked ===
       true ? 1 : 0);

  // if the user scrolls in the window we do not want it to be updated.
  // so set paused flag to false
  function scrollFunction() {
    paused = (data_textarea.scrollHeight - data_textarea.scrollTop) >
      (data_textarea.clientHeight + 1);
    // if the service was paused when the tests are finished,
    // set continue_loop to false
    if (!paused && !tests_still_running) {
      continue_loop = false;
    }
  }

  data_textarea.onscroll = scrollFunction;

  rJS(window).declareService(function () {
    var queue = new RSVP.Queue();

    function launchLiveTest() {
      queue.push(function () {
        return jIO.util.ajax({
          type: "POST",
          url: my_url_run_test,
          data: form_data
        });
      }).push(function () {
        tests_still_running = false;
        // set continue_loop to false ONLY IF the test is not paused.
        // Otherwise it will be set when user scrolls to the end
        if (!paused) {
          continue_loop = false;
        }
      }, function (error) {
        console.error("Error launching live tests", error);
      });
    }
    return queue.push(function () {
      return launchLiveTest();
    });
  }).declareService(function () {
    var queue = new RSVP.Queue();

    function getLiveTestOutput() {
      queue.push(function () {
        return jIO.util.ajax({
          type: "GET",
          url: my_url_read_test
        });
      }).push(function (evt) {
        var data = evt.target.response;
        // cut the characters that are already presented
        data = data.substring(data_size);
        if ((!paused || last_call) && data.length !== undefined) {
          // to put the data in the correct place
          data_size = data_size + data.length;
          // add the new data
          data_textarea.value = data_textarea.value + data;
          data_textarea.scrollTop = data_textarea.scrollHeight;
        }
        return RSVP.delay(1000);
      }, function (error) {
        console.error("Error refreshing live test output", error);
      }).push(function () {
        if (continue_loop) {
          return getLiveTestOutput();
        }
        if (!continue_loop) {
          if (!last_call) {
            last_call = true;
            return getLiveTestOutput();
          }
        }
      });
    }
    return queue.push(function () {
      // a delay of 2 seconds so the test can be launched
      // before results are read
      return RSVP.delay(2000);
    }).push(getLiveTestOutput());
  });
}(rJS, jIO, RSVP, window, document, FormData));