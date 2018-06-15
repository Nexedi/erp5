/*global window, rJS, RSVP, Handlebars, $, loopEventListener */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
(function (window, rJS, RSVP, Handlebars, $, loopEventListener) {
  "use strict";

  var INTERFACE_GADGET_SCOPE = "interface_gadget",
  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
    // Precompile the templates while loading the first gadget instance
    gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("interface-validator-template")
                         .innerHTML,
    interface_validator_template = Handlebars.compile(source);

  function fetchPageType(gadget_url) {
    var page_type = '',
      key = '_page_';
    if (gadget_url.indexOf(key) > -1) {
      page_type = gadget_url.substring(gadget_url.indexOf(key) + key.length,
                                       gadget_url.lastIndexOf('.'));
    }
    return page_type;
  }

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.content_element = element.querySelector('.appcache_form');
        });
    })

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////

    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          var error_message = '';
          if (options.found !== undefined && options.found === 'false') {
            error_message = "Error: Cannot load the appcache file. " +
                            "Please check and try again.";
          }
          gadget.props.content_element.innerHTML =
            interface_validator_template({
              message: error_message
            });
          $(gadget.props.element).trigger("create");
          gadget.props.content_element.querySelector("input[type=submit]")
                                 .disabled = false;
          gadget.props.content_element.querySelector("input[type=text]")
                                 .focus();
        });

    })

    .declareService(function () {
      ////////////////////////////////////
      // Form submit listening.
      // Prevent browser to automatically handle the form submit in
      // case of a bug
      ////////////////////////////////////
      var gadget = this;
      function formSubmit(submit_event) {
        var interface_gadget,
          appcache_url;
        return new RSVP.Queue()
          .push(function () {
            gadget.props.content_element.querySelector("input[type=submit]")
                                   .disabled = true;
            return submit_event.target[0].value;
          })
          .push(function (submit_url) {
            appcache_url = submit_url;
            return gadget.getDeclaredGadget(INTERFACE_GADGET_SCOPE);
          })
          .push(function (i_gadget) {
            var required_interface =
                'gadget_interface_validator_reportpage_interface.html',
              gadget_source_url = 'gadget_interface_validator.appcache';
            interface_gadget = i_gadget;
            return interface_gadget.getGadgetListImplementingInterface(
              required_interface,
              gadget_source_url
            );
          })
          .push(function (gadget_list) {
            if (gadget_list.length > 0) {
              var page_type = fetchPageType(gadget_list[0]);
              return gadget.redirect({
                page: page_type,
                appcache_url: appcache_url
              });
            }
            return gadget.redirect({
              found: false
            });
          });
      }
      // Listen to form submit
      return loopEventListener(
        gadget.props.content_element.querySelector(
          'form.interface-validation-form'
        ),
        'submit',
        false,
        formSubmit
      );

    });
}(window, rJS, RSVP, Handlebars, $, loopEventListener));