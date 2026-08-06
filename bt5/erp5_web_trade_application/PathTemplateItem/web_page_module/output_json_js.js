/*global window,rJS,RSVP,URI,location */
/*jslint indent: 2, maxlen: 80*/
/*jslint nomen: true*/
(function (window, rJS, RSVP) {
  "use strict";
  var hateoas_url = "hateoas/";

  function createJio(gadget) {
    return new RSVP.Queue()
      .push(function () {
        return gadget.state_parameter_dict.jio_storage.createJio({
          type: "erp5",
          url: (new URI(hateoas_url)).absoluteTo(location.href).toString(),
          default_view_reference: "trade_jio_view"
        });
      })
      .push(function () {
        return gadget.state_parameter_dict.jio_storage.allDocs({
          query: 'portal_type:(' +
            '"Organisation Module"' +
            'OR "Purchase Price Record Module" ' +
            'OR "Product Module" ' +            
            'OR "Sale Price Record Module" ' +
            'OR "Daily Statement Record Module"' +
            'OR "Purchase Record Module" ' +
            'OR "Sale Record Module" ' +
            ') ' +
            'OR (portal_type:"Organisation" '
              + 'AND validation_state:("validated" OR "submitted")) ' +
            'OR (portal_type:"Currency"'
               + 'AND validation_state:"validated") ' +
            'OR (portal_type:"Category" AND (   relative_url:"region/%" ' +
            'OR relative_url:"quantity_unit/weight/%" ' +
            'OR relative_url:"product_line/product/%"' +
            'OR relative_url:"product_line/material/%")) ',
          limit: [0, 100000]
        });
      })
      .push(function (result) {
        function getValue(element) {
          return gadget.state_parameter_dict.jio_storage.get(element.id);
        }
        var promise_list = result.data.rows.map(getValue);
        return RSVP.all(promise_list);
      })
      .push(function (result) {
        var json_data = {}, i, url;
        for (i = 0; i < result.length; i += 1) {
          if (result[i].portal_type === "Organisation") {
            json_data.organisation = result[i];
          } else {
            json_data[result[i].relative_url] = result[i];
          }
        }
        json_data = JSON.stringify(json_data);
        url = 'data:text/json;charset=utf8,'
          + encodeURIComponent(json_data);
        window.open(url, '_blank');
        window.focus();
        return json_data;
      });
  }

  rJS(window)
    .ready(function (gadget) {
      return gadget.getDeclaredGadget('jio')
        .push(function (jio_gadget) {
          // Initialize the gadget local parameters
          gadget.state_parameter_dict = {jio_storage: jio_gadget};
        });
    })
    .ready(function (g) {
      return createJio(g);
    });


}(window, rJS, RSVP));