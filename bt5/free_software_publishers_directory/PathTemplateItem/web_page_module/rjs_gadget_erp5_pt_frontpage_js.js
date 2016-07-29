/*global window, rJS, RSVP, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars) {
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
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;

      return gadget.jio_allDocs({
        "query": 'meta_type:"ERP5 Folder" AND id:"%_module"',
        "select_list": ["title", "business_application_title"],
        "limit": 1000
      })
        .push(function (result) {
          var result_list = [],
            i;
          for (i = 0; i < result.data.rows.length; i += 1) {
            result_list.push(RSVP.all([
              gadget.getUrlFor({command: 'display_stored_state', options: {jio_key: result.data.rows[i].id}}),
              result.data.rows[i].value.title || result.data.rows[i].id,
              result.data.rows[i].value.business_application_title
            ]));
          }
          return RSVP.all(result_list);
        })
        .push(function (document_list) {
          var i,
            business_application_dict = {},
            business_application_list = [],
            business_application,
            module_info,
            result_html = '<div data-role="collapsible-set" data-theme="c">',
            doc;
          for (i = 0; i < document_list.length; i += 1) {
            doc = document_list[i];
            if (doc[2] === undefined) {
              doc[2] = "Other";
            }
            module_info = {
              link: doc[0],
              title: doc[1]
            };
            if (business_application_dict[doc[2]] === undefined) {
              business_application_dict[doc[2]] = [module_info];
              business_application_list.push(doc[2]);
            } else {
              business_application_dict[doc[2]].push(module_info);
            }
          }

          business_application_list.sort(function (a, b) {
            // Push the "Other" value at the end
            var result = 0;
            if (a === "Other") {
              result = 1;
            } else if (b === "Other") {
              result = -1;
            } else if (a < b) {
              result = -1;
            } else if (a > b) {
              result = 1;
            }
            return result;
          });

          function sort_module(a, b) {
            var result = 0;
            if (a.title < b.title) {
              result = -1;
            } else if (a.title > b.title) {
              result = 1;
            }
            return result;
          }

          for (i = 0; i < business_application_list.length; i += 1) {
            business_application = business_application_list[i];
            business_application_dict[business_application].sort(sort_module);

            result_html += table_template({
              definition_title: business_application,
              documentlist: business_application_dict[business_application]
            });
          }

          result_html += '</div>';

          return gadget.translateHtml(result_html);
        })
        .push(function (my_translated_html) {
          gadget.props.element.querySelector('.document_list').innerHTML =
            my_translated_html;
          return gadget.updateHeader({
            page_title: 'Modules'
          });
        });
    });
}(window, rJS, RSVP, Handlebars));