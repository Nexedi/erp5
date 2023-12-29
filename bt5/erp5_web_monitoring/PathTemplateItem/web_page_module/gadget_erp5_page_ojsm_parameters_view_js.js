/*global window, rJS, document, RSVP, escape */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, document, RSVP, escape) {
  "use strict";

  var gadget_klass = rJS(window);

  gadget_klass
    .setState({
      ouline_list: "",
      instance_tree: ""
    })
    .ready(function (g) {
      g.props = {};
      g.props.parameter_form_list = [];
    })
    .declareAcquiredMethod('jio_allDocs', 'jio_allDocs')
    .declareAcquiredMethod('jio_get', 'jio_get')

    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_get(options.opml_url);
        })
        .push(function (opml_doc) {
          return gadget.changeState({opml: opml_doc, options: options});
        })
        .push(function () {
          return gadget.jio_allDocs({
            query: '(portal_type:"Software Instance") AND (specialise_title:"' +
            options.title + '")',
            sort_on: [["title", "ascending"]],
            select_list: ["_links", "title", "parameters", "aggregate_reference"]
          });
        })
        .push(function (result) {
          return gadget.changeState({instance_dict: result});
        });
    })
    .onStateChange(function (modification_dict) {
      var gadget = this;
      if (gadget.state.options.instance_amount === 0) {
        gadget.element.querySelector('.hosting-title').textContent =
          gadget.state.options.title + " -  Not synchronized!";
      }
      gadget.element.querySelector('.hosting-title').textContent =
        gadget.state.options.title;
      if (modification_dict.hasOwnProperty('instance_dict')) {
        // render parameter form
        return new RSVP.Queue()
          .push(function () {
            var promise_list = [],
              i,
              element = gadget.element.querySelector('.parameters-box'),
              gadget_element;

            //cleanup
            while (element.hasChildNodes()) {
              element.removeChild(element.lastChild);
            }

            for (i = 0; i < gadget.state.instance_dict.data.total_rows; i += 1) {
              if (gadget.state.instance_dict.data.rows[i]
                  .value.aggregate_reference === undefined) {
                // Instance is not Synchronized!
                promise_list.push(false);
                continue;
              }
              gadget_element = document.createElement("div");
              element.appendChild(gadget_element);
              promise_list.push(
                gadget.declareGadget("gadget_officejs_monitoring_parameter_view.html",
                  {element: gadget_element,
                    scope: 'p_' + gadget.state.instance_dict.data.rows[i].id,
                    sandbox: "public"}
                  )
              );
            }
            return RSVP.all(promise_list);
          })
          .push(function (parameter_gadget_list) {
            var i,
              promise_list = [];
            gadget.props.parameter_form_list = parameter_gadget_list;
            for (i = 0; i < parameter_gadget_list.length; i += 1) {
              if (parameter_gadget_list[i]) {
                promise_list.push(
                  parameter_gadget_list[i].render({
                    url: gadget.state.instance_dict.data.rows[i].value._links.private_url.href
                      .replace('jio_private', 'private') + '/config',
                    basic_login: gadget.state.opml.basic_login,
                    title: "Parameters " + gadget.state.instance_dict.data.rows[i].value.title,
                    parameters: gadget.state.instance_dict.data.rows[i].value.parameters
                  })
                );
              }
            }
            return RSVP.all(promise_list);
          });
      }
    });

}(window, rJS, document, RSVP, escape));