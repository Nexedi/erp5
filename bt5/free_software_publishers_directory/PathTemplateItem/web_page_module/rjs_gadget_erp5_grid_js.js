/*global window, rJS, RSVP, document */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, rJS, RSVP) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // some methods
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
    // acquired methods
    /////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////
    // published methods
    /////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (my_option_dict) {
      var gadget = this,
        props = gadget.property_dict,
        content_container;

      // declare or load a cell gadget
      function fetchAndRenderGadget(my_config_dict) {
        return new RSVP.Queue()
          .push(function () {
            return gadget.declareGadget(
              my_config_dict.gadget_href,
              {"scope": "grid_" + my_config_dict.grid_location}
            );
          })
          .push(function (my_gadget_instance) {
            return my_gadget_instance.render(my_config_dict);
          });
      }

      // generate requests to load data. On first call, also create html
      function setFragment() {
        var row_dict,
          row_container,
          cell_dict,
          i_len,
          i,
          j_len,
          j;

        content_container = document.createDocumentFragment();

        for (i = 0, i_len = props.layout.length; i < i_len; i += 1) {
          row_dict = props.layout[i];
          row_container = document.createElement("ul");
          row_container.className = 'grid-items line-' + row_dict.length;

          for (j = 0, j_len = row_dict.length; j < j_len; j += 1) {
            cell_dict = row_dict[j];
            row_container.appendChild(document.createElement("li"));
            cell_dict.grid_location = String(i) + String(j);
          }
          content_container.appendChild(row_container);
        }
      }

      // START:
      props.layout = props.layout || my_option_dict.layout || [];
      my_option_dict.parameter_dict = my_option_dict.parameter_dict || {};

      // set HTML frame
      setFragment();

      // build HTML and assemble cell content once returned
      return new RSVP.Queue()
        .push(function () {
          var render_list = [],
            cell_dict,
            row,
            i_len,
            i,
            j_len,
            j;

          for (i = 0, i_len = props.layout.length; i < i_len; i += 1) {
            row = props.layout[i];
            for (j = 0, j_len = row.length; j < j_len; j += 1) {
              cell_dict = row[j];
              cell_dict.grid_location = String(i) + String(j);
              render_list.push(fetchAndRenderGadget(cell_dict));
            }
          }
          return RSVP.all(render_list);
        })
        .push(function (my_content_list) {
          return new RSVP.Queue()
            .push(function () {
              var element_list = [],
                i_len,
                i;

              for (i = 0, i_len = my_content_list.length; i < i_len; i += 1) {
                element_list.push(my_content_list[i].getElement());
              }
              return RSVP.all(element_list);
            })
            .push(function (my_element_list) {
              var grid_container,
                i,
                i_len;

              for (i = 0, i_len = my_element_list.length; i < i_len; i += 1) {
                content_container.querySelectorAll(".grid-items > li")[i]
                  .appendChild(my_element_list[i]);
              }

              grid_container = document.createElement("div");
              grid_container.className = "ui-grid-container ui-responsive";
              grid_container.appendChild(content_container);
              props.element.appendChild(grid_container);
              return gadget;
            });
        });
    });

    /////////////////////////////////////////////////////////////////
    // declared service
    /////////////////////////////////////////////////////////////////

}(window, document, rJS, RSVP));
