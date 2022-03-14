/*jslint vars:true nomen:true */ /* these two options are for compatibility with jslint 2014-04-21 . We'll remove them once we switch to more recent jslint */
/*global window, document, rJS, JSON, QUnit, jQuery, RSVP, console, setTimeout */
(function (rJS, JSON, QUnit, RSVP, $) {
    "use strict";
    var start = QUnit.start;
    var stop = QUnit.stop;
    var test = QUnit.test;
    var equal = QUnit.equal;
    var ok = QUnit.ok;
    var error_handler = function (e) {
        window.console.error(e);
        ok(false, e);
    };
    var sample_class_definition = {
        edge: {
            description: "Base definition for edge",
            properties: {
                "_class": {
                    type: "string"
                },
                destination: {
                    type: "string"
                },
                name: {
                    type: "string"
                },
                required: ["name", "_class", "source", "destination"],
                source: {
                    type: "string"
                }
            },
            type: "object"
        },
        "Example.Edge": {
            "_class": "edge",
            allOf: [{
                "$ref": "#/edge"
            }, {
                properties: {
                    color: {
                        "enum": ["red", "green", "blue"]
                    }
                }
            }],
            description: "An example edge with a color property"
        },
        "Example.Node": {
            "_class": "node",
            allOf: [{
                "$ref": "#/node"
            }, {
                properties: {
                    shape: {
                        type: "string"
                    }
                }
            }],
            description: "An example node with a shape property"
        },
        node: {
            description: "Base definition for node",
            properties: {
                "_class": {
                    type: "string"
                },
                coordinate: {
                    properties: {
                        left: "number",
                        top: "number"
                    },
                    type: "object"
                },
                name: {
                    type: "string"
                },
                required: ["name", "_class"]
            },
            type: "object"
        }
    };
    var sample_graph = {
        edge: {
            edge1: {
                "_class": "Example.Edge",
                source: "N1",
                destination: "N2",
                color: "blue"
            }
        },
        node: {
            N1: {
                "_class": "Example.Node",
                name: "Node 1",
                coordinate: {
                    top: 0,
                    left: 0
                },
                shape: "square"
            },
            N2: {
                "_class": "Example.Node",
                name: "Node 2",
                shape: "circle",
                coordinate: {
                    top: 0.3,
                    left: 0.4
                }
            }
        }
    };
    var sample_graph_no_node_coodinate = {
        edge: {
            edge1: {
                "_class": "Example.Edge",
                source: "N1",
                destination: "N2",
                color: "blue"
            }
        },
        node: {
            N1: {
                "_class": "Example.Node",
                name: "Node 1",
                shape: "square"
            },
            N2: {
                "_class": "Example.Node",
                name: "Node 2",
                shape: "circle"
            }
        }
    };
    var sample_graph_not_connected = {
        edge: {},
        node: {
            N1: {
                "_class": "Example.Node",
                name: "Node 1",
                shape: "square"
            },
            N2: {
                "_class": "Example.Node",
                name: "Node 2",
                shape: "circle"
            }
        }
    };
    var sample_data_graph = JSON.stringify({
        class_definition: sample_class_definition,
        graph: sample_graph
    });
    var sample_data_graph_no_node_coordinate = JSON.stringify({
        class_definition: sample_class_definition,
        graph: sample_graph_no_node_coodinate
    });
    var sample_data_graph_not_connected = JSON.stringify({
        class_definition: sample_class_definition,
        graph: sample_graph_not_connected
    });
    var sample_data_empty_graph = JSON.stringify({
        class_definition: sample_class_definition,
        graph: {
            node: {},
            edge: {}
        }
    });

    QUnit.config.testTimeout = 60000;
    rJS(window).ready(function (g) {
        test("Sample graph can be loaded and output is equal to input", function () {
            var jsplumb_gadget;
            stop();
            g.declareGadget("./index.html", {
                element: document.querySelector("#test-element")
            }).then(function (new_gadget) {
                jsplumb_gadget = new_gadget;
                return jsplumb_gadget.render(sample_data_graph);
            }).then(function () {
                return jsplumb_gadget.getContent();
            }).then(function (content) {
                equal(content, sample_data_graph);
            }).fail(error_handler).always(start);
        });
        test("New node can be drag & dropped", function () {
            var jsplumb_gadget;
            stop();
            function runTest() {
                // XXX here I used getContent to have a promise, but there must be a
                // more elegant way.
                return jsplumb_gadget.getContent().then(function () {
                    // fake a drop event
                    var e = new window.Event("drop");
                    e.dataTransfer = {
                        getData: function (type) {
                            // make sure we are called properly
                            equal("application/json", type, "The drag&dropped element must have data type application/json");
                            return JSON.stringify("Example.Node");
                        }
                    };
                    jsplumb_gadget.props.main.dispatchEvent(e);
                }).then(function () {
                    return jsplumb_gadget.getContent();
                }).then(function (content) {
                    var node;
                    var graph = JSON.parse(content).graph;
                    equal(1, Object.keys(graph.node).length, "There is one new node class");
                    node = graph.node[Object.keys(graph.node)[0]];
                    equal("Example.Node", node._class, "Node class is set to Example.Node");
                });
            }
            g.declareGadget("./index.html", {
                element: document.querySelector("#test-element")
            }).then(function (new_gadget) {
                jsplumb_gadget = new_gadget;
                jsplumb_gadget.render(sample_data_empty_graph);
            }).then(runTest).fail(error_handler).always(start);
        });
        test("Node can be dragged", function () {
            var jsplumb_gadget;
            stop();
            function runTest() {
                return jsplumb_gadget.getContent().then(function () {
                    // 100 and 60 are about 10% of the .graph_container div ( set by css, so this
                    // might change )
                    $("div[title='Node 1']").simulate("drag", {
                        dx: 100,
                        dy: 60
                    });
                }).then(function () {
                    return jsplumb_gadget.getContent();
                }).then(function (content) {
                    var graph = JSON.parse(content).graph;
                    var node_coordinate = graph.node.N1.coordinate;
                    // Since original coordinates where 0,0 we are now about 0.1,0.1
                    // as we moved 10%
                    ok(node_coordinate.top - 0.1 < 0.1, "Top is ok");
                    ok(node_coordinate.left - 0.1 < 0.1, "Left is ok");
                });
            }
            g.declareGadget("./index.html", {
                element: document.querySelector("#test-element")
            }).then(function (new_gadget) {
                jsplumb_gadget = new_gadget;
                jsplumb_gadget.render(sample_data_graph);
            }).then(runTest).fail(error_handler).always(start);
        });
        test("Node properties can be edited", function () {
            var jsplumb_gadget;
            stop();
            function runTest() {
                return jsplumb_gadget.getContent().then(function () {
                    // click on a node to see display the popup
                    $("div[title='Node 1']").simulate("dblclick");
                    // Promises that handle the dialog actions are not available
                    // immediately after clicking.
                    var promise = new RSVP.Promise(function (resolve) {
                        function fillDialog() {
                            if (!jsplumb_gadget.props.dialog_promise) {
                                // Dialog not ready. Let's retry later.
                                // XXX this condition is actually incorrect. We need to wait
                                // for the event listener to have been registered for the
                                // dialog buttons. This setTimeout is good enough for now.
                                setTimeout(fillDialog, 1e3);
                                return;
                            }
                            // check displayed values
                            equal($("input[name='id']").val(), "N1");
                            equal($("input[name='name']").val(), "Node 1");
                            equal($("input[name='shape']").val(), "square");
                            // change the name
                            $("input[name='name']").val("Modified Name");
                            equal(1, $("input[value='Validate']").length, "There should be one validate button");
                            // and save
                            $("input[value='Validate']").click();
                            // resolve our test promise once the dialog handling promise is
                            // finished.
                            jsplumb_gadget.props.dialog_promise.then(resolve);
                        }
                        fillDialog();
                    });
                    return promise.then(function () {
                        return jsplumb_gadget.getContent().then(function (content) {
                            var graph = JSON.parse(content).graph;
                            var node = graph.node.N1;
                            equal("Modified Name", node.name, "Data is modified");
                            equal("Modified Name", $("div#" + jsplumb_gadget.props.node_id_to_dom_element_id.N1).text(), "DOM is modified");
                            equal(1, $("div[title='Modified Name']").length, "DOM title attribute is modified");
                        });
                    });
                });
            }
            g.declareGadget("./index.html", {
                element: document.querySelector("#test-element")
            }).then(function (new_gadget) {
                jsplumb_gadget = new_gadget;
                jsplumb_gadget.render(sample_data_graph);
            }).then(runTest).fail(error_handler).always(start);
        });
        test("Nodes can be connected", function () {
            var jsplumb_gadget;
            stop();
            function runTest() {
                return jsplumb_gadget.getContent().then(function (content) {
                    var node1 = jsplumb_gadget.props.main.querySelector("div[title='Node 1']");
                    var node2 = jsplumb_gadget.props.main.querySelector("div[title='Node 2']");
                    equal(0, Object.keys(JSON.parse(content).graph.edge).length, "There are no edge at the beginning");
                    jsplumb_gadget.props.jsplumb_instance.connect({
                        source: node1.id,
                        target: node2.id
                    });
                    // .connect insternal API is asynchronous, but there's no way to wait for the event to be processed.
                    // for now we just wait for a short delay
                    return RSVP.delay(1e3);
                }).then(function () {
                    return jsplumb_gadget.getContent();
                }).then(function (content) {
                    var edge;
                    var graph = JSON.parse(content).graph;
                    equal(2, Object.keys(graph.node).length, "We still have 2 nodes");
                    equal(1, Object.keys(graph.edge).length, "We have 1 edge");
                    edge = graph.edge[Object.keys(graph.edge)[0]];
                    // XXX how edge class would be set ? the first one from schema ? Yes ! TODO: update test
                    //equal("Example.Edge", edge._class, "Edge class is correct");
                    equal("N1", edge.source, "edge source is correct");
                    equal("N2", edge.destination, "edge destination is correct");
                });
            }
            g.declareGadget("./index.html", {
                element: document.querySelector("#test-element")
            }).then(function (new_gadget) {
                jsplumb_gadget = new_gadget;
                jsplumb_gadget.render(sample_data_graph_not_connected);
            }).then(runTest).fail(error_handler).always(start);
        });
        test("Node can be deleted", function () {
            var jsplumb_gadget;
            stop();
            function runTest() {
                return jsplumb_gadget.getContent().then(function () {
                    equal(1, $("div[title='Node 1']").length, "node 1 is visible");
                    equal(1, $("._jsPlumb_connector").length, "there is 1 connection");
                    // click on node 1 to see display the popup
                    $("div[title='Node 1']").simulate("dblclick");
                    // Promises that handle the dialog actions are not available
                    // immediately after clicking.
                    var promise = new RSVP.Promise(function (resolve) {
                        function waitForDialogAndDelete() {
                            if (!jsplumb_gadget.props.dialog_promise) {
                                // Dialog not ready. Let's retry later.
                                // XXX this condition is actually incorrect. We need to wait
                                // for the event listener to have been registered for the
                                // dialog buttons. This setTimeout is good enough for now.
                                setTimeout(waitForDialogAndDelete, 1e3);
                                return;
                            }
                            equal(1, $("input[value='Delete']").length, "There should be one delete button");
                            $("input[value='Delete']").click();
                            // resolve our test promise once the dialog handling promise is
                            // finished.
                            jsplumb_gadget.props.dialog_promise.then(resolve);
                        }
                        waitForDialogAndDelete();
                    });
                    return promise.then(function () {
                        return jsplumb_gadget.getContent().then(function (content) {
                            var graph = JSON.parse(content).graph;
                            equal(1, Object.keys(graph.node).length, "node is removed from data");
                            equal(0, Object.keys(graph.edge).length, "edge referencing this node is also removed");
                            equal(0, $("div[title='Node 1']").length, "DOM element for node is removed");
                            equal(0, $("._jsPlumb_connector").length, "DOM element for edge is removed");
                        });
                    });
                });
            }
            g.declareGadget("./index.html", {
                element: document.querySelector("#test-element")
            }).then(function (new_gadget) {
                jsplumb_gadget = new_gadget;
                jsplumb_gadget.render(sample_data_graph);
            }).then(runTest).fail(error_handler).always(start);
        });
        test("Node id can be changed (connections are updated and node can be edited afterwards)", function () {
            var jsplumb_gadget;
            stop();
            function runTest() {
                return jsplumb_gadget.getContent().then(function () {
                    // click on a node to see display the popup
                    $("div[title='Node 1']").simulate("dblclick");
                    // Promises that handle the dialog actions are not available
                    // immediately after clicking.
                    var promise = new RSVP.Promise(function (resolve) {
                        function fillDialog() {
                            if (!jsplumb_gadget.props.dialog_promise) {
                                // Dialog not ready. Let's retry later.
                                // XXX this condition is actually incorrect. We need to wait
                                // for the event listener to have been registered for the
                                // dialog buttons. This setTimeout is good enough for now.
                                setTimeout(fillDialog, 1e3);
                                return;
                            }
                            equal($("input[name='id']").val(), "N1");
                            // change the id
                            $("input[name='id']").val("N1b");
                            equal(1, $("input[value='Validate']").length, "There should be one validate button");
                            $("input[value='Validate']").click();
                            // resolve our test promise once the dialog handling promise is
                            // finished.
                            jsplumb_gadget.props.dialog_promise.then(resolve);
                        }
                        fillDialog();
                    });
                    return promise.then(function () {
                        return jsplumb_gadget.getContent().then(function (content) {
                            var graph = JSON.parse(content).graph;
                            equal(2, Object.keys(graph.node).length, "We still have two nodes");
                            ok(graph.node.N1b !== undefined, "Node Id changed");
                            equal(1, Object.keys(graph.edge).length, "We still have one connection");
                            equal("N1b", graph.edge.edge1.source, "Connection source has been updated");
                        });
                    });
                });
            }
            g.declareGadget("./index.html", {
                element: document.querySelector("#test-element")
            }).then(function (new_gadget) {
                jsplumb_gadget = new_gadget;
                jsplumb_gadget.render(sample_data_graph);
            }).then(runTest).fail(error_handler).always(start);
        });
        test("New node can be edited", function () {
            var jsplumb_gadget;
            var node_id;
            stop();
            function runTest() {
                // XXX here I used getContent to have a promise, but there must be a
                // more elegant way.
                return jsplumb_gadget.getContent().then(function () {
                    // fake a drop event
                    var e = new window.Event("drop");
                    e.dataTransfer = {
                        getData: function (type) {
                            // make sure we are called properly
                            equal("application/json", type, "The drag&dropped element must have data type application/json");
                            return JSON.stringify("Example.Node");
                        }
                    };
                    jsplumb_gadget.props.main.dispatchEvent(e);
                }).then(function () {
                    return jsplumb_gadget.getContent();
                }).then(function (content) {
                    var node;
                    var graph = JSON.parse(content).graph;
                    equal(1, Object.keys(graph.node).length);
                    node_id = Object.keys(graph.node)[0];
                    node = graph.node[node_id];
                    equal("Example.Node", node._class);
                }).then(function () {
                    // click the new node to see display the popup
                    // XXX at the moment nodes have class window
                    equal(1, $("div.window").length, "We have a new node");
                    $("div.window").simulate("dblclick");
                    // Promises that handle the dialog actions are not available
                    // immediately after clicking.
                    var promise = new RSVP.Promise(function (resolve) {
                        function fillDialog() {
                            if (!jsplumb_gadget.props.dialog_promise) {
                                // Dialog not ready. Let's retry later.
                                // XXX this condition is actually incorrect. We need to wait
                                // for the event listener to have been registered for the
                                // dialog buttons. This setTimeout is good enough for now.
                                setTimeout(fillDialog, 1e3);
                                return;
                            }
                            // check displayed values
                            equal($("input[name='id']").val(), node_id);
                            equal($("input[name='name']").val(), "");
                            equal($("input[name='shape']").val(), "");
                            // change the name
                            $("input[name='name']").val("Modified Name");
                            equal(1, $("input[value='Validate']").length, "There should be one validate button");
                            // and save
                            $("input[value='Validate']").click();
                            // resolve our test promise once the dialog handling promise is
                            // finished.
                            jsplumb_gadget.props.dialog_promise.then(resolve);
                        }
                        fillDialog();
                    });
                    return promise.then(function () {
                        return jsplumb_gadget.getContent().then(function (content) {
                            var graph = JSON.parse(content).graph;
                            var node = graph.node[node_id];
                            equal("Modified Name", node.name, "Data is modified");
                            equal("Modified Name", $("div.window").text(), "DOM is modified");
                        });
                    });
                });
            }
            g.declareGadget("./index.html", {
                element: document.querySelector("#test-element")
            }).then(function (new_gadget) {
                jsplumb_gadget = new_gadget;
                jsplumb_gadget.render(sample_data_empty_graph);
            }).then(runTest).fail(error_handler).always(start);
        });
        test("New node can be deleted", function () {
            var jsplumb_gadget;
            var node_id;
            stop();
            function runTest() {
                // XXX here I used getContent to have a promise, but there must be a
                // more elegant way.
                return jsplumb_gadget.getContent().then(function () {
                    // fake a drop event
                    var e = new window.Event("drop");
                    e.dataTransfer = {
                        getData: function (type) {
                            // make sure we are called properly
                            equal("application/json", type, "The drag&dropped element must have data type application/json");
                            return JSON.stringify("Example.Node");
                        }
                    };
                    jsplumb_gadget.props.main.dispatchEvent(e);
                }).then(function () {
                    return jsplumb_gadget.getContent();
                }).then(function (content) {
                    var node;
                    var graph = JSON.parse(content).graph;
                    equal(1, Object.keys(graph.node).length);
                    node_id = Object.keys(graph.node)[0];
                    node = graph.node[node_id];
                    equal("Example.Node", node._class);
                }).then(function () {
                    // click the new node to see display the popup
                    // XXX at the moment nodes have class window
                    equal(1, $("div.window").length, "We have a new node");
                    $("div.window").simulate("dblclick");
                    // Promises that handle the dialog actions are not available
                    // immediately after clicking.
                    var promise = new RSVP.Promise(function (resolve) {
                        function waitForDialogAndDelete() {
                            if (!jsplumb_gadget.props.dialog_promise) {
                                // Dialog not ready. Let's retry later.
                                // XXX this condition is actually incorrect. We need to wait
                                // for the event listener to have been registered for the
                                // dialog buttons. This setTimeout is good enough for now.
                                setTimeout(waitForDialogAndDelete, 1e3);
                                return;
                            }
                            equal(1, $("input[value='Delete']").length, "There should be one delete button");
                            $("input[value='Delete']").click();
                            // resolve our test promise once the dialog handling promise is
                            // finished.
                            jsplumb_gadget.props.dialog_promise.then(resolve);
                        }
                        waitForDialogAndDelete();
                    });
                    return promise.then(function () {
                        return jsplumb_gadget.getContent().then(function (content) {
                            var graph = JSON.parse(content).graph;
                            equal(0, Object.keys(graph.node).length, "node is removed from data");
                            equal(0, $("div.window").length, "DOM is modified");
                        });
                    });
                });
            }
            g.declareGadget("./index.html", {
                element: document.querySelector("#test-element")
            }).then(function (new_gadget) {
                jsplumb_gadget = new_gadget;
                jsplumb_gadget.render(sample_data_empty_graph);
            }).then(runTest).fail(error_handler).always(start);
        });
        test("Graph is automatically layout", function () {
            var jsplumb_gadget;
            stop();
            g.declareGadget("./index.html", {
                element: document.querySelector("#test-element")
            }).then(function (new_gadget) {
                jsplumb_gadget = new_gadget;
                return jsplumb_gadget.render(sample_data_graph_no_node_coordinate);
            }).then(function () {
                return jsplumb_gadget.getContent();
            }).then(function (content) {
                /*jslint unparam: true */
                $.each(JSON.parse(content).graph.node, function (ignore, node) {
                    ok(node.coordinate.top !== undefined, "Node have top coordinate");
                    ok((0 <= node.coordinate.top) && (node.coordinate.top <= 1), "Node top coordinate is between [0..1]");
                    ok(node.coordinate.left !== undefined, "Node have left coordinate");
                    ok((0 <= node.coordinate.left) && (node.coordinate.left <= 1), "Node left coordinate is between [0..1]");
                });
            }).fail(error_handler).always(start);
        });
        test("Gadget can be rendered multiple times", function () {
            var jsplumb_gadget;
            stop();
            g.declareGadget("./index.html", {
                element: document.querySelector("#test-element")
            }).then(function (new_gadget) {
                jsplumb_gadget = new_gadget;
                return jsplumb_gadget.render(sample_data_graph);
            }).then(function () {
                return jsplumb_gadget.getContent();
            }).then(function () {
                return jsplumb_gadget.render(sample_data_graph);
            }).then(function () {
                return jsplumb_gadget.getContent();
            }).then(function (content) {
                equal(sample_data_graph, content);
                equal($(".window", document.querySelector("#test-element")).length, 2, "Graph is rendered only once");
            }).fail(error_handler).always(start);
        });
    });
}(rJS, JSON, QUnit, RSVP, jQuery));