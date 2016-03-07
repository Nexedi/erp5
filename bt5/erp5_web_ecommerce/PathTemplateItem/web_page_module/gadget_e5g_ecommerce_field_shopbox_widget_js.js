/*global window, rJS, RSVP, Handlebars */
/*jslint nomen: true, indent: 2 */
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  // XXX quick hack!

  /////////////////////////////////////////////////////////////////
  // api handlebars
  /////////////////////////////////////////////////////////////////

  // shopbbox_widget_header = {
  //   item_list: [
  //     item_link: [string],
  //     item_default_src: [string],
  //     item_title: [string],
  //     item_description: [string],
  //     item_price: [string]
  //   ]
  // }
  // shopbox_widget_search = {}
  // shopbox_widget_paginate = {}

  /////////////////////////////////////////////////////////////////
  // templates
  /////////////////////////////////////////////////////////////////
  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,

    shopbox_widget_list = Handlebars.compile(
      templater.getElementById("shopbox-widget-list").innerHTML
    );

  /////////////////////////////////////////////////////////////////
  // some methods
  /////////////////////////////////////////////////////////////////
  function digForProperty(my_property, my_document_list) {
    var list = my_document_list || [],
      property,
      j_len,
      j;

    for (j = 0, j_len = list.length; j < j_len; j += 1) {
      property = list[j][my_property];
      if (property) {
        return property;
      }
    }
  }

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
        element = gadget.property_dict.element,
        container = element.querySelector(".custom-grid .ui-body-c"),
        content = '',
        search_gadget,
        result,
        sub_document_list;

      // store initial configuration and query
      gadget.property_dict.initial_query
        = gadget.property_dict.initial_query || my_option_dict.gadget_query;
      gadget.property_dict.option_dict =
        gadget.property_dict.option_dict || my_option_dict;

      return new RSVP.Queue()
        .push(function () {
          return gadget.declareGadget("gadget_erp5_searchfield.html", {
            "scope": "shopbox-search"
          });
        })
        .push(function (my_search_gadget) {
          return my_search_gadget.render({});
        })
        .push(function (my_rendered_gadget) {
          search_gadget = my_rendered_gadget;
          return gadget.jio_allDocs(my_option_dict.gadget_query);
        })
        .push(function (my_result) {
          var subdocument_list = [],
            item,
            i_len,
            i;

          result = my_result;

          for (i = 0, i_len = result.data.total_rows; i < i_len; i += 1) {
            item = result.data.rows[i];
            subdocument_list.push(gadget.jio_getAttachment({
              "_id": "erp5",
              "_attachment": window.location.href + "hateoas/" +
                item.id + "/shopbox_getRelatedDocumentList"
            }));
          }
          return RSVP.all(subdocument_list);
        })
        .push(function (my_related_document_list) {
          var link_list = [],
            image_dict = {},
            image_url,
            item,
            sub_document,
            i_len,
            i;

          sub_document_list = my_related_document_list;

          for (i = 0, i_len = result.data.total_rows; i < i_len; i += 1) {
            item = result.data.rows[i];
            sub_document = sub_document_list[i].data.related_document_list;
            link_list.push(gadget.whoWantToDisplayThis(item.id));

            // XXX:
            image_url = digForProperty("default_image_url", sub_document);
            if (image_url) {
              image_dict[item.id] = window.location.protocol + "//" +
                window.location.host + "/" +
                  image_url + "?quality=75&display=thumbnail";
            }
          }

          return RSVP.all([
            RSVP.all(link_list),
            RSVP.hash(image_dict)
          ]);
        })
        .push(function (my_link_list) {
          var data = result.data.rows,
            href_list = my_link_list[0],
            src_dict = my_link_list[1],
            item_list = [],
            item,
            price,
            sub_document,
            price_formatted,
            i_len,
            i;

          for (i = 0, i_len = href_list.length; i < i_len; i += 1) {
            item = data[i];
            sub_document = sub_document_list[i].data.related_document_list;
            price = digForProperty("price", sub_document);
            if (price) {
              price_formatted = price.toFixed(2);
            }
            item_list.push({
              item_link: href_list[i],
              item_default_src: src_dict[item.id],
              item_title: item.value.title,
              item_description: item.value.description,
              item_price: price_formatted + " \u20AC"
            });
          }

          content += shopbox_widget_list({"item_list": item_list});
          return gadget.translateHtml(content);
        })
        .push(function (my_translated_html) {
          var wrapper,
            first_element;

          container.innerHTML = my_translated_html;
          wrapper = container.querySelector(".ui-shopbox-wrapper");
          first_element = wrapper.firstChild;
          wrapper.insertBefore(search_gadget.__element, first_element);

          return gadget;
        });
    });

    /////////////////////////////////////////////////////////////////
    // declared service
    /////////////////////////////////////////////////////////////////

}(window, rJS, RSVP, Handlebars));
