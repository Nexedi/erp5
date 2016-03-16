/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // api
  /////////////////////////////////////////////////////////////////

  //  gadget_href         [string]  url of gadget to load into a cell
  //  gadget_portal_link  [string]  portal type url (to avoid fetching)
  //  gadget_query        [object]  query parameters for data to display
  //  gadegt_title        [string]  title for listbox
  //  gadget_portal       [string]  portal type to link to

  var HARDCODED_GRID_LIST = [
    [{
      "gadget_href": "gadget_e5g_ecommerce_field_shopbox_widget.html",
      "gadget_portal_link": "#jio_key=product_module&view=view",
      "gadget_title": "Products",
      "gadget_portal": "Product",
      "gadget_query": {
        "query": 'portal_type: "Product"',
        "select_list": ["title", "description", "uid"],
        "limit": [0, 20]
      }
    }]
  ];

  /////////////////////////////////////////////////////////////////
  // some methods
  /////////////////////////////////////////////////////////////////

  /////////////////////////////////////////////////////////////////
  // RJS
  /////////////////////////////////////////////////////////////////

  rJS(window)

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

    /////////////////////////////////////////////////////////////////
    // published methods
    /////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////
    // declared service
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.declareGadget("gadget_erp5_grid.html", {
            "scope": "grid"
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget("grid");
        })
        .push(function (my_grid_gadget) {
          return my_grid_gadget.render({"layout": HARDCODED_GRID_LIST});
        })
        .push(function (my_content_gadget) {
          gadget.property_dict.element.appendChild(
            my_content_gadget.property_dict.element
          );
        });
    });

}(window, rJS, RSVP));
