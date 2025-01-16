/*global window, rJS, RSVP, jIO */
/*jslint nomen: true, maxlen:180, indent:2*/
(function (rJS, jIO, RSVP, window) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareMethod('render', function (options) {
      var gadget = this;
      return gadget.getSetting("hateoas_url")
        .push(function (hateoas_url) {
          options.hateoas_url = hateoas_url;
          options.submit_state = 'initial';
          options.input_value = 'Mark OK';
          return gadget.changeState(options);
        });
    })
    .onStateChange(function (modification_dict) {
      var gadget = this,
        button_container =
          gadget.element.querySelector('.dialog_button_container'),
        submit_input = button_container.querySelector('input'),
        spinner = button_container.querySelector('.ui-icon-spinner');
      if (modification_dict.hasOwnProperty('input_value')) {
        submit_input.value = modification_dict.input_value;
      }
      if (modification_dict.hasOwnProperty('submit_state')) {
        switch (gadget.state.submit_state) {
        case 'initial':
          submit_input.disabled = false;
          spinner.classList.add('ui-visibility-hidden');
          submit_input.classList.remove('success');
          submit_input.classList.remove('error');
          break;
        case 'sending':
          submit_input.disabled = true;
          spinner.classList.remove('ui-visibility-hidden');
          submit_input.classList.remove('success');
          submit_input.classList.remove('error');
          break;
        case 'success':
          submit_input.disabled = true;
          spinner.classList.add('ui-visibility-hidden');
          submit_input.classList.add('success');
          submit_input.classList.remove('error');
          break;
        case 'error':
          submit_input.disabled = true;
          spinner.classList.add('ui-visibility-hidden');
          submit_input.classList.remove('success');
          submit_input.classList.add('error');
          break;
        }
      }
    })
    .onEvent('submit', function submit() {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.changeState({
              'submit_state': 'sending',
              'input_value': 'Posting'
            }),
            gadget.jio_putAttachment(
              gadget.state.quality_control,
              // it's ugly, we should generate url in server side,
              // but it doesn't work well to get hateoas_url in server side
              // romain will check it in generic code
              gadget.state.hateoas_url + gadget.state.post_url,
              {
                'result': gadget.state.value,
                'fast_post': true
              }
            )
          ]);
        })
        .push(function (result_list) {
          return jIO.util.readBlobAsText(result_list[1].target.response);
        })
        .push(function (response) {
          var result = JSON.parse(response.target.result);
          return gadget.changeState({
            'submit_state': result.portal_status_level,
            'input_value': result.portal_status_message
          });
        });
    });


}(rJS, jIO, RSVP, window));