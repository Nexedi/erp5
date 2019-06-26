/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, Handlebars, RSVP, Node */
(function (window, rJS, Handlebars, RSVP, Node) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // temlates
  /////////////////////////////////////////////////////////////////
  // Precompile templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    template_element = gadget_klass.__template_element,
    panel_template_header = Handlebars.compile(template_element
                         .getElementById("panel-template-header")
                         .innerHTML),
    panel_template_body = Handlebars.compile(template_element
                         .getElementById("panel-template-body")
                         .innerHTML);

  gadget_klass
    .setState({
      visible: false
    })
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("translateHtml", "translateHtml")

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
          //return g.getUrlFor({command: 'display', options: {page: "logout"}});
          return RSVP.all([
            g.getUrlFor({command: 'display', options: {page: "preference"}}),
            g.getUrlFor({command: 'display', options: {page: "download"}}),
            g.getUrlFor({command: 'display', options: {page: "ebulk_doc"}}),
            g.getUrlFor({command: 'display', options: {page: "contact"}}),
            g.getUrlFor({command: 'display', options: {page: "logout"}}),
            g.getUrlFor({command: 'display', options: {page: "fifdata"}}),
            g.getUrlFor({command: 'display', options: {page: "register"}})
          ]);
        })
        .push(function (all_result) {
          // XXX: Customize panel header!
          return g.translateHtml(
            panel_template_header() +
            panel_template_body({
              "preference_href": all_result[0],
              "download_href": all_result[1],
              "documentation_href": all_result[2],
              "contact_info_href": all_result[3],
              "logout_href": all_result[4],
              "data_download_href": all_result[5],
              "register_href": all_result[6]
            })
          );
        })
        .push(function (my_translated_or_plain_html) {
          g.element.querySelector("div").innerHTML = my_translated_or_plain_html;
        });
    })

    .onStateChange(function () {
      if (this.state.visible) {
        if (!this.element.classList.contains('visible')) {
          this.element.classList.toggle('visible');
        }
      } else {
        if (this.element.classList.contains('visible')) {
          this.element.classList.remove('visible');
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
    }, false, false);

}(window, rJS, Handlebars, RSVP, Node));
