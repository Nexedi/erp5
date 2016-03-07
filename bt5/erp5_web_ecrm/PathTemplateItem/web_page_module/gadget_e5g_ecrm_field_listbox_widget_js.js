/*global window, rJS, RSVP, Handlebars */
/*jslint nomen: true, indent: 2 */
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // api handlebars
  /////////////////////////////////////////////////////////////////

  // listbox_widget_header = {
  //   "left_link_list": [
  //     {"link_title": [string], "link_href": [string]}
  //   ],
  //   "listbox_title": [string],
  //   "right_link_list": [
  //     {"link_title": [string], "link_href": [string]}
  //   ]
  // }
  // listbox_widget_search = {
  //   "search_title": [string]
  // }
  // listbox_widget_table = {
  //   "column_list": [
  //     {"column_title": [string]}
  //   ]
  // }
  // listbox_widget_table_partial = {
  //   "table_row_list": [{
  //     "table_cell_list": [
  //       {{"cell_title": [string], "cell_href": [string]}
  //     ]
  //   }]
  // }

  /////////////////////////////////////////////////////////////////
  // templates
  /////////////////////////////////////////////////////////////////
  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,

    listbox_widget_header = Handlebars.compile(
      templater.getElementById("listbox-widget-header").innerHTML
    ),
    listbox_widget_table = Handlebars.compile(
      templater.getElementById("listbox-widget-table").innerHTML
    ),
    listbox_widget_table_partial = Handlebars.registerPartial(
      "listbox-widget-table-partial",
      templater.getElementById("listbox-widget-table-partial").innerHTML
    );

  /////////////////////////////////////////////////////////////////
  // some methods
  /////////////////////////////////////////////////////////////////

  gadget_klass

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    .ready(function (my_gadget) {
      my_gadget.property_dict = {};
    })

    .ready(function (my_gadget) {
      return my_gadget.getElement()
        .push(function (my_element) {
          my_gadget.property_dict.element = my_element;
        });
    })

    /////////////////////////////////////////////////////////////////
    // published methods
    /////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("whoWantToDisplayThis", "whoWantToDisplayThis")
    .declareAcquiredMethod("translateHtml", "translateHtml")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (my_option_dict) {
      var gadget = this,
        content = '',
        result;

      // store initial configuration and query
      gadget.property_dict.initial_query
        = gadget.property_dict.initial_query || my_option_dict.gadget_query;
      gadget.property_dict.option_dict =
        gadget.property_dict.option_dict || my_option_dict;

      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_allDocs(my_option_dict.gadget_query);
        })
        .push(function (my_result) {
          var link_list = [],
            i_len,
            i;

          result = my_result;

          for (i = 0, i_len = result.data.total_rows; i < i_len; i += 1) {
            link_list.push(gadget.whoWantToDisplayThis(result.data.rows[i].id));
          }

          return RSVP.all(link_list);
        })
        .push(function (my_link_list) {
          var query = gadget.property_dict.option_dict.gadget_query,
            column_list = [],
            table_row_list = [],
            table_cell_list,
            i_len,
            i,
            j_len,
            j;

          // build handlebars object

          // loop select_list to build columns
          for (i = 0, i_len = query.select_list.length; i < i_len; i += 1) {
            column_list.push({"column_title": query.select_list[i]});
          }

          for (j = 0, j_len = result.data.total_rows; j < j_len; j += 1) {
            table_cell_list = [];
            for (i = 0, i_len = query.select_list.length; i < i_len; i += 1) {
              table_cell_list.push({
                "cell_href": my_link_list[j],
                "cell_title": result.data.rows[j].value[query.select_list[i]]
              });
            }
            table_row_list.push({"table_cell_list": table_cell_list});
          }
          content += listbox_widget_header({
            "listbox_title": my_option_dict.gadget_title,
            "right_link_list": [{
              "link_title": "All",
              "link_href": gadget.property_dict.option_dict.gadget_portal_link
            }]
          });
          content += listbox_widget_table({
            "column_list": column_list,
            "table_row_list": table_row_list
          });

          return gadget.translateHtml(content);
        })
        .push(function (my_translated_html) {
          gadget.property_dict.element.querySelector(".custom-grid .ui-body-c")
            .innerHTML = my_translated_html;
          return gadget;
        });
    });

    /////////////////////////////////////////////////////////////////
    // declared service
    /////////////////////////////////////////////////////////////////

}(window, rJS, RSVP, Handlebars));
