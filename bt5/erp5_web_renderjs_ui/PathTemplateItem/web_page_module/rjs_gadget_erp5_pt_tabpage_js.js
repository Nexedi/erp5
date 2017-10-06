/*global window, rJS, RSVP, Handlebars, URI, calculatePageTitle */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars, URI, calculatePageTitle) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    table_template = Handlebars.compile(gadget_klass.__template_element
                         .getElementById("table-template")
                         .innerHTML);

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var view_list,
        tab_list = [],
        jump_action_list = [],
        breadcrumb_action_list = [],
        parent_queue,
        gadget = this,
        erp5_document,
        tab_title = "Views",
        tab_icon = "eye",
        jump_list;

      function handleParent(parent_link) {
        parent_queue.push(function () {
          var uri,
            jio_key;
          if (parent_link !== undefined) {
            uri = new URI(parent_link.href);
            jio_key = uri.segment(2);

            if ((uri.protocol() !== 'urn') || (uri.segment(0) !== 'jio') || (uri.segment(1) !== "get")) {
              // Parent is the ERP5 site
              breadcrumb_action_list.unshift({
                title: "ERP5",
                link: "#"
              });
            } else {
              // Parent is an ERP5 document
              return gadget.getUrlFor({command: 'display_stored_state', options: {jio_key: jio_key}})
                .push(function (parent_href) {
                  breadcrumb_action_list.unshift({
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

      return gadget.jio_getAttachment(options.jio_key, "links")
        .push(function (result) {
          var i,
            promise_list = [];
          erp5_document = result;
          view_list = erp5_document._links.view || [];
          jump_list = erp5_document._links.action_object_jump || [];

          // All ERP5 document should at least have one view.
          // So, no need normally to test undefined
          if (view_list.constructor !== Array) {
            view_list = [view_list];
          }
          if (jump_list.constructor !== Array) {
            jump_list = [jump_list];
          }
          for (i = 0; i < view_list.length; i += 1) {
            promise_list.push(gadget.getUrlFor({command: 'change', options: {
              view: view_list[i].href,
              page: undefined
            }}));
          }
          for (i = 0; i < jump_list.length; i += 1) {
            promise_list.push(gadget.getUrlFor({command: 'push_history', options: {
              extended_search: new URI(jump_list[i].href).query(true).query,
              page: 'search'
            }}));
          }
          parent_queue = new RSVP.Queue();
          handleParent(erp5_document._links.parent || "#");
          promise_list.push(parent_queue);
          return RSVP.all(promise_list);
        })
        .push(function (all_result) {
          var i, j;
          j = 0;
          for (i = 0; i < view_list.length; i += 1) {
            tab_list.push({
              title: view_list[i].title,
              i18n: view_list[i].title,
              link: all_result[j]
            });
            j += 1;
          }
          for (i = 0; i < jump_list.length; i += 1) {
            jump_action_list.push({
              title: jump_list[i].title,
              link: all_result[j],
              i18n: jump_list[i].title
            });
            j += 1;
          }

          return gadget.translateHtml(table_template({
            definition_title: tab_title,
            definition_i18n: tab_title,
            definition_icon: tab_icon,
            documentlist: tab_list
          }) + table_template({
            definition_title: "Jumps",
            documentlist: jump_action_list,
            definition_icon: "plane",
            definition_i18n: "Jumps"
          }) + table_template({
            definition_title: "Breadcrumb",
            documentlist: breadcrumb_action_list,
            definition_icon: "ellipsis-v",
            definition_i18n: "Breadcrumb"
          }));
        })
        .push(function (my_translated_html) {
          gadget.element.innerHTML = my_translated_html;

          return RSVP.all([
            gadget.getUrlFor({command: 'change', options: {
              page: undefined
            }}),
            calculatePageTitle(gadget, erp5_document)
          ]);
        })
        .push(function (url_list) {
          var dict = {
            back_url: url_list[0],
            page_title: url_list[1]
          };
          return gadget.updateHeader(dict);
        });
    });

}(window, rJS, RSVP, Handlebars, URI, calculatePageTitle));