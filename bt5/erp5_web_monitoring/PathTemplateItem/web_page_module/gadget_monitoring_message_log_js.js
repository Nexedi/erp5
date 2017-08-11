/*global window, rJS, btoa */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,

    error_log_template = Handlebars.compile(
      templater.getElementById("template-error-list").innerHTML
    );

  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
        });
    })
    .ready(function (g) {
      return g.getDeclaredGadget("log_gadget")
      .push(function (log_gadget) {
        g.props.log_gadget = log_gadget;
      });
    })
    .declareAcquiredMethod("redirect", "redirect")
    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.props.log_gadget.getMessageList(150)
        .push(function (error_list) {

          var content = error_log_template({error_list: error_list});
          gadget.props.element.querySelector('.logbox table tbody')
            .innerHTML = content;
        });
    })
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          $('.tooltip').tooltipster({
            animation: 'fade',
            delay: 200,
            theme: 'tooltipster-shadow',
            touchDevices: true,
            interactive: true,
            trigger: 'click',
            contentAsHTML: true,
            minWidth: 300
          });
        })
        .push(function () {
          var promise_list = [];
          promise_list.push(loopEventListener(
            gadget.props.element.querySelector('.commands a'),
            'click',
            false,
            function (evt) {
              return gadget.props.log_gadget.getMessageList(150)
                .push(function (error_list) {
                  var content = error_log_template({error_list: error_list});
                  gadget.props.element.querySelector('.logbox table tbody')
                    .innerHTML = content;
                  $('.tooltip').tooltipster({
                    animation: 'fade',
                    delay: 200,
                    theme: 'tooltipster-shadow',
                    touchDevices: true,
                    interactive: true,
                    trigger: 'click',
                    contentAsHTML: true,
                    minWidth: 300
                  });
                });
            }
          ));

          return RSVP.all(promise_list);
        });

    });

}(window, rJS));