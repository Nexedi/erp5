/*jslint nomen: true, indent: 2, maxerr: 3 */
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
            g.getUrlFor({command: 'display', options: {page: "afs_directory"}}),
            g.getUrlFor({command: 'display', options: {page: "afs_publisher_list"}}),
            g.getUrlFor({command: 'display', options: {page: "afs_software_list"}}),
            g.getUrlFor({command: 'display', options: {page: "afs_success_case_list"}})
          ]);
        })
        .push(function (all_result) {
          // XXX: Customize panel header!
          var tmp = panel_template_header();
          tmp += panel_template_body({
            "directory_href": all_result[0],
            "publisher_href": all_result[1],
            "software_href": all_result[2],
            "success_case_href": all_result[3]
          });
          return tmp;
        })
        .push(function (my_translated_or_plain_html) {
          g.props.element.querySelector("div").innerHTML = my_translated_or_plain_html;
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