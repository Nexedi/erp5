/*global window, rJS, RSVP, Handlebars, URI */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars, URI) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("table-template")
                         .innerHTML,
    table_template = Handlebars.compile(source);

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
        });
    })

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translateHtml", "translateHtml")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        erp5_document,
        header_options = {},
        parent_queue,
        parent_list = [];

      function handleParent(parent_link) {
        parent_queue.push(function () {
          var uri,
            jio_key;
          if (parent_link !== undefined) {
            uri = new URI(parent_link.href);
            jio_key = uri.segment(2);

            if ((uri.protocol() !== 'urn') || (uri.segment(0) !== 'jio') || (uri.segment(1) !== "get")) {
              // Parent is the ERP5 site
              parent_list.unshift({
                title: "ERP5",
                link: "#"
              });
            } else {
              // Parent is an ERP5 document
              return gadget.getUrlFor({command: 'display_stored_state', options: {jio_key: jio_key}})
                .push(function (parent_href) {
                  parent_list.unshift({
                    title: parent_link.name,
                    link: parent_href
                  });
                  return gadget.jio_getAttachment(jio_key, "links");
                })
                .push(function (result) {
                  handleParent(result._links.parent || "#");
                });
            }

          }
        });
      }

      return gadget.getUrlFor({command: 'change', options: {page: undefined}})
        .push(function (back_url) {
          header_options.back_url = back_url;
          return gadget.jio_getAttachment(options.jio_key, "links");
        })
        .push(function (result) {
          erp5_document = result;
          header_options.page_title = erp5_document.title;
          parent_queue = new RSVP.Queue();

          handleParent(erp5_document._links.parent || "#");

          return parent_queue;
        })
        .push(function () {
          return gadget.translateHtml(table_template({
            definition_title: "Breadcrumb",
            documentlist: parent_list
          }));
        })
        .push(function (my_translated_html) {
          gadget.props.element.innerHTML = my_translated_html;
          return gadget.updateHeader(header_options);
        });
    });

}(window, rJS, RSVP, Handlebars, URI));