/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global document, window, rJS, Handlebars, RSVP, Node */
(function (document, window, rJS, Handlebars, RSVP, loopEventListener, Node) {
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
    .setState({
      visible: false,
      desktop: false
    })

    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('toggle', function () {
      return this.changeState({
        visible: !this.state.visible
      });
    })
    .declareMethod('close', function () {
      return this.changeState({
        visible: false
      });
    })

    .declareMethod('render', function () {
      var g = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            g.getUrlFor({command: 'display', options: {page: "eci_directory"}}),
            g.getUrlFor({command: 'display', options: {page: "eci_provider_list"}}),
            g.getUrlFor({command: 'display', options: {page: "eci_solution_list"}}),
            g.getUrlFor({command: 'display', options: {page: "eci_success_case_list"}}),
            g.getUrlFor({command: 'display', options: {page: "eci_financial_list"}})
          ]);
        })
        .push(function (all_result) {

          // XXX: Customize panel header!
          var tmp = panel_template_header() +
            panel_template_body({
              "directory_href": all_result[0],
              "provider_href": all_result[1],
              "financial_href": all_result[4],
              "solution_href": all_result[2],
              "success_case_href": all_result[3]
            });
          g.element.querySelector("div").innerHTML = tmp;
        });
    })


    .onStateChange(function (modification_dict) {
      if (modification_dict.hasOwnProperty("visible")) {
        if (this.state.visible) {
          if (!this.element.classList.contains('visible')) {
            this.element.classList.toggle('visible');
          }
        } else {
          if (this.element.classList.contains('visible')) {
            this.element.classList.remove('visible');
          }
        }
      }
    })

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .onEvent('click', function (evt) {
      if ((evt.target.nodeType === Node.ELEMENT_NODE) &&
          (evt.target.tagName === 'BUTTON')) {
        return this.toggle();
      }
    }, false, false)

    .declareJob('listenResize', function () {
      // resize should be only trigger after the render method
      // as displaying the panel rely on external gadget (for translation for example)
      var result,
        event,
        context = this;
      function extractSizeAndDispatch() {
        if (window.matchMedia("(min-width: 85em)").matches) {
          return context.changeState({
            desktop: true
          });
        }
        return context.changeState({
          desktop: false
        });
      }
      result = loopEventListener(window, 'resize', false,
                                 extractSizeAndDispatch);
      event = document.createEvent("Event");
      event.initEvent('resize', true, true);
      window.dispatchEvent(event);
      return result;
    });
}(document, window, rJS, Handlebars, RSVP, rJS.loopEventListener, Node));





