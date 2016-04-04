/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, Handlebars, jQuery, RSVP, loopEventListener */
(function (window, rJS, Handlebars, $, RSVP, loopEventListener) {
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
          g.props.jelement = $(element.querySelector("div"));
          g.props.render_deferred = RSVP.defer();
        });
    })

    .ready(function (g) {
      g.props.jelement.panel({
        display: "overlay",
        position: "left",
        theme: "d"
        // animate: false
      });
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('toggle', function () {
      this.props.jelement.panel("toggle");
    })
    .declareMethod('close', function () {
      this.props.jelement.panel("close");
    })

    .declareMethod('render', function () {
      var g = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            g.getUrlFor({command: 'display', options: {page: "front"}}),
            g.getUrlFor({command: 'display', options: {page: "history"}}),
            g.getUrlFor({command: 'display', options: {page: "preference"}}),
            g.getUrlFor({command: 'display', options: {page: "logout"}}),
            g.getUrlFor({command: 'display', options: {page: "search"}}),
            g.getUrlFor({command: 'display', options: {page: "worklist"}}),
            
            g.getUrlFor({command: 'display', options: {page: "Purchase Price Record"}}),
            g.getUrlFor({command: 'display', options: {page: "Purchase Record"}}),
            g.getUrlFor({command: 'display', options: {page: "Products"}}),
            g.getUrlFor({command: 'display', options: {page: "Organisations"}}),
            g.getUrlFor({command: 'display', options: {page: "Inventory Move Record"}}),
            g.getUrlFor({command: 'display', options: {page: "Production Record"}}),
            
            
            g.getUrlFor({command: 'display', options: {page: "Sale Price Record"}}),
            g.getUrlFor({command: 'display', options: {page: "Sale Record"}}),
            g.getUrlFor({command: 'display', options: {page: "Daily Statement Record"}}),
            g.getUrlFor({command: 'display', options: {page: "Report"}}),
            g.getUrlFor({command: 'display', options: {page: "Synchronisation"}}),
            g.getUrlFor({command: 'display', options: {page: "Setting"}})
            
          ]);
        })
        .push(function (all_result) {
          // XXX: Customize panel header!
          var tmp = panel_template_header();
          tmp += panel_template_body({
            "module_href": all_result[0],
            "history_href": all_result[1],
            "preference_href": all_result[2],
            // "language_list": language_list,
            "logout_href": all_result[3],
            "search_href": all_result[4],
            "worklist_href": all_result[5],
            "purchase_price_record_module_href": all_result[6]
          });
          return tmp;
        })
        .push(function (my_translated_or_plain_html) {
          g.props.jelement.html(my_translated_or_plain_html);
          g.props.jelement.trigger("create");
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
            panel_gadget.props.element.querySelector('form'),
            'submit',
            false,
            formSubmit
          );
        });

    });

}(window, rJS, Handlebars, jQuery, RSVP, loopEventListener));