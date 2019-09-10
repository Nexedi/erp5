/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global document, window, rJS, Handlebars, RSVP, loopEventListener, Node */
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
            g.getUrlFor({command: 'display', options: {page: "afs_directory"}}),
            g.getUrlFor({command: 'display', options: {page: "afs_publisher_statistic"}}),
            g.getUrlFor({command: 'display', options: {page: "afs_publisher_list"}}),
            g.getUrlFor({command: 'display', options: {page: "afs_software_list"}}),
            g.getUrlFor({command: 'display', options: {page: "afs_success_case_list"}}),
            g.getUrlFor({command: 'display', options: {page: "afs_financial_list"}})
          ]);
        })
        .push(function (all_result) {

          // XXX: Customize panel header!
          var tmp = panel_template_header() +
            panel_template_body({
              "directory_href": all_result[0],
              "publisher_statistic_href": all_result[1],
              "publisher_href": all_result[2],
              "financial_href": all_result[5],
              "software_href": all_result[3],
              "success_case_href": all_result[4]
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
    })

    .onEvent('blur', function (evt) {
      // XXX Horrible hack to clear the search when focus is lost
      // This does not follow renderJS design, as a gadget should not touch
      // another gadget content
      if (evt.target.type === 'search') {
        evt.target.value = "";
      }
    }, true, false);

}(document, window, rJS, Handlebars, RSVP, loopEventListener, Node));





