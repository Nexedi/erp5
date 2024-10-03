/*jslint indent: 2, nomen: true, maxlen: 80*/
/*global window, rJS, Handlebars, RSVP, loopEventListener */
(function (window, rJS, Handlebars, RSVP, loopEventListener) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // temlates
  /////////////////////////////////////////////////////////////////
  // Precompile templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    source_header = gadget_klass.__template_element
                         .getElementById("panel-template-header")
                         .innerHTML,
    panel_template_header = Handlebars.compile(source_header),
    source_body = gadget_klass.__template_element
                         .getElementById("panel-template-body")
                         .innerHTML,
    panel_template_body = Handlebars.compile(source_body);

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.render_deferred = RSVP.defer();
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('toggle', function () {
      this.props.element.classList.toggle('visible');
    })
    .declareMethod('close', function () {
      if (this.props.element.classList.contains('visible')) {
        this.props.element.classList.remove('visible');
      }
    })

    .declareMethod('render', function () {
      var g = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            g.getUrlFor({command: 'display', options:
              {jio_key: "purchase_price_record_module", page: "view"}}),
            g.getUrlFor({command: 'display', options:
              {jio_key: "purchase_record_module", page: "view"}}),
            g.getUrlFor({command: 'display', options:
              {jio_key: "product_module", page: "view"}}),
            g.getUrlFor({command: 'display', options:
              {jio_key: "organisation_module", page: "view"}}),
            g.getUrlFor({command: 'display', options:
              {jio_key: "sale_price_record_module", page: "view"}}),
            g.getUrlFor({command: 'display', options:
              {jio_key: "sale_record_module", page: "view"}}),
            g.getUrlFor({command: 'display', options:
              {jio_key: "daily_statement_record_module", page: "view"}})
          ]);
        })
        .push(function (all_result) {
          // XXX: Customize panel header!
          var tmp = panel_template_header();
          tmp += panel_template_body({
            "purchase_price_record_module_href": all_result[0],
            "purchase_record_module_href": all_result[1],
            "product_module_href": all_result[2],
            "organisation_module_href": all_result[3],
            "sale_price_record_module_href": all_result[4],
            "sale_record_module_href": all_result[5],
            "daily_statement_record_module_href": all_result[6]
          });
          return tmp;
        })
        .push(function (my_translated_or_plain_html) {
          g.props.element.querySelector("div").innerHTML
            = my_translated_or_plain_html;
          g.props.render_deferred.resolve();
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var panel_gadget = this;

      function formSubmit() {
        panel_gadget.toggle();
      }
      return new RSVP.Queue()
        .push(function () {
          return panel_gadget.props.render_deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            panel_gadget.props.element.querySelector('button'),
            'click',
            false,
            formSubmit
          );
        });

    });

}(window, rJS, Handlebars, RSVP, loopEventListener));