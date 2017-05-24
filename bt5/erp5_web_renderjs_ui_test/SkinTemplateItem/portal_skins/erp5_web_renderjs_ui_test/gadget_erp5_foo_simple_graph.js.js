/*jslint indent: 2, nomen: true */
/*global window, rJS, RSVP, console */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .ready(function (gadget) {
      gadget.property_dict = {};
      return gadget.getElement()
        .push(function (element) {
          gadget.property_dict.element = element;
          gadget.property_dict.deferred = RSVP.defer();
        });
    })

    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////

    //////////////////////////////////////////////
    // initialize the gadget content
    //////////////////////////////////////////////
    .declareMethod("render", function (option_dict) {
      console.log("foo_simple_graph, render, options", option_dict);
      var gadget = this;
      gadget.property_dict.option_dict = option_dict.value;
      gadget.renderGraph(); //Launched as service, not blocking
    })
    .declareJob("renderGraph", function () {
      var gadget = this,
          option_dict = gadget.property_dict.option_dict;
      return gadget.declareGadget(
        option_dict.graph_gadget,
        {scope: "graph",
         sandbox: "iframe",
         element: gadget.property_dict.element.querySelector(".document-content")
      })
      .push(function (graph_gadget) {
        gadget.property_dict.graph_widget = graph_gadget;
        return graph_gadget.render(
            {data: [{ value_dict: {0: [new Date("2016-02-01"), new Date("2016-02-02"), new Date("2016-02-03"), new Date("2016-02-04")],
                                   1: [0, 1, 3, 2]},
                      type: "line",
                      title: "Value"
                   },
                   { value_dict: {0: [new Date("2016-02-01"), new Date("2016-02-02"), new Date("2016-02-03"), new Date("2016-02-04")],
                                   1: [1, 2, 4, 3]},
                      type: "line",
                      title: "Value2"
                   }],
             layout: {axis_dict : {0: {"title": "date"},
                              1: {"title": "value"}
                             },
                     title: "Simple Graph"}
            });
      });

    });
}(window, rJS, RSVP));
