<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts31928229.99</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>test.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*global window, document, rJS, JSON, QUnit, jQuery, RSVP, console, setTimeout\n
\n
*/\n
(function(rJS, JSON, QUnit, RSVP, $) {\n
    "use strict";\n
    var start = QUnit.start,\n
        stop = QUnit.stop,\n
        test = QUnit.test,\n
        equal = QUnit.equal,\n
        ok = QUnit.ok,\n
        error_handler = function(e) {\n
          window.console.error(e);\n
          ok(false, e);\n
        },\n
        sample_class_definition = {\n
        edge: {\n
            description: "Base definition for edge",\n
            properties: {\n
                _class: {\n
                    type: "string"\n
                },\n
                destination: {\n
                    type: "string"\n
                },\n
                name: {\n
                    type: "string"\n
                },\n
                required: [ "name", "_class", "source", "destination" ],\n
                source: {\n
                    type: "string"\n
                }\n
            },\n
            type: "object"\n
        },\n
        "Example.Edge": {\n
            _class: "edge",\n
            allOf: [ {\n
                $ref: "#/edge"\n
            }, {\n
                properties: {\n
                    color: {\n
                        "enum": [ "red", "green", "blue" ]\n
                    }\n
                }\n
            } ],\n
            description: "An example edge with a color property"\n
        },\n
        "Example.Node": {\n
            _class: "node",\n
            allOf: [ {\n
                $ref: "#/node"\n
            }, {\n
                properties: {\n
                    shape: {\n
                        type: "string"\n
                    }\n
                }\n
            } ],\n
            description: "An example node with a shape property"\n
        },\n
        node: {\n
            description: "Base definition for node",\n
            properties: {\n
                _class: {\n
                    type: "string"\n
                },\n
                coordinate: {\n
                    properties: {\n
                        left: "number",\n
                        top: "number"\n
                    },\n
                    type: "object"\n
                },\n
                name: {\n
                    type: "string"\n
                },\n
                required: [ "name", "_class" ]\n
            },\n
            type: "object"\n
        }\n
    }, sample_graph = {\n
        edge: {\n
            edge1: {\n
                _class: "Example.Edge",\n
                source: "N1",\n
                destination: "N2",\n
                color: "blue"\n
            }\n
        },\n
        node: {\n
            N1: {\n
                _class: "Example.Node",\n
                name: "Node 1",\n
                coordinate: {\n
                    top: 0,\n
                    left: 0\n
                },\n
                shape: "square"\n
            },\n
            N2: {\n
                _class: "Example.Node",\n
                name: "Node 2",\n
                shape: "circle",\n
                coordinate: {\n
                    top: 0.3,\n
                    left: 0.4\n
                }\n
            }\n
        }\n
    }, sample_graph_not_connected = {\n
        edge: {},\n
        node: {\n
            N1: {\n
                _class: "Example.Node",\n
                name: "Node 1",\n
                shape: "square"\n
            },\n
            N2: {\n
                _class: "Example.Node",\n
                name: "Node 2",\n
                shape: "circle"\n
            }\n
        }\n
    }, sample_data_graph = JSON.stringify({\n
        class_definition: sample_class_definition,\n
        graph: sample_graph\n
    }), sample_data_graph_not_connected = JSON.stringify({\n
        class_definition: sample_class_definition,\n
        graph: sample_graph_not_connected\n
    }), sample_data_empty_graph = JSON.stringify({\n
        class_definition: sample_class_definition,\n
        graph: {\n
            node: {},\n
            edge: {}\n
        }\n
    });\n
    QUnit.config.testTimeout = 60000;\n
    rJS(window).ready(function(g) {\n
        test("Sample graph can be loaded and output is equal to input", function() {\n
            var jsplumb_gadget;\n
            stop();\n
            g.declareGadget("./index.html", {\n
                element: document.querySelector("#qunit-fixture")\n
            }).then(function(new_gadget) {\n
                jsplumb_gadget = new_gadget;\n
                return jsplumb_gadget.render(sample_data_graph);\n
            }).then(function() {\n
                return jsplumb_gadget.getContent();\n
            }).then(function(content) {\n
                equal(content, sample_data_graph);\n
            }).fail(error_handler).always(start);\n
        });\n
        test("New node can be drag & dropped", function() {\n
            var jsplumb_gadget;\n
            stop();\n
            function runTest() {\n
                // XXX here I used getContent to have a promise, but there must be a\n
                // more elegant way.\n
                return jsplumb_gadget.getContent().then(function() {\n
                    // fake a drop event\n
                    var e = new window.Event("drop");\n
                    e.dataTransfer = {\n
                        getData: function(type) {\n
                            // make sure we are called properly\n
                            equal("application/json", type, "The drag&dropped element must have data type application/json");\n
                            return JSON.stringify("Example.Node");\n
                        }\n
                    };\n
                    jsplumb_gadget.props.main.dispatchEvent(e);\n
                }).then(function() {\n
                    return jsplumb_gadget.getContent();\n
                }).then(function(content) {\n
                    var node, graph = JSON.parse(content).graph;\n
                    equal(1, Object.keys(graph.node).length, "There is one new node class");\n
                    node = graph.node[Object.keys(graph.node)[0]];\n
                    equal("Example.Node", node._class, "Node class is set to Example.?ode");\n
                });\n
            }\n
            g.declareGadget("./index.html", {\n
                element: document.querySelector("#qunit-fixture")\n
            }).then(function(new_gadget) {\n
                jsplumb_gadget = new_gadget;\n
                jsplumb_gadget.render(sample_data_empty_graph);\n
            }).then(runTest).fail(error_handler).always(start);\n
        });\n
        test("Node can be dragged", function() {\n
            var jsplumb_gadget;\n
            stop();\n
            function runTest() {\n
                return jsplumb_gadget.getContent().then(function() {\n
                    // 100 and 60 are about 10% of the .graph_container div ( set by css, so this\n
                    // might change )\n
                    $("div[title=\'Node 1\']").simulate("drag", {\n
                        dx: 100,\n
                        dy: 60\n
                    });\n
                }).then(function() {\n
                    return jsplumb_gadget.getContent();\n
                }).then(function(content) {\n
                    var graph = JSON.parse(content).graph, node_coordinate = graph.node.N1.coordinate;\n
                    // Since original coordinates where 0,0 we are now about 0.1,0.1\n
                    // as we moved 10%\n
                    ok(node_coordinate.top - .1 < .1, "Top is ok");\n
                    ok(node_coordinate.left - .1 < .1, "Left is ok");\n
                });\n
            }\n
            g.declareGadget("./index.html", {\n
                element: document.querySelector("#qunit-fixture")\n
            }).then(function(new_gadget) {\n
                jsplumb_gadget = new_gadget;\n
                jsplumb_gadget.render(sample_data_graph);\n
            }).then(runTest).fail(error_handler).always(start);\n
        });\n
        test("Node properties can be edited", function() {\n
            var jsplumb_gadget;\n
            stop();\n
            function runTest() {\n
                return jsplumb_gadget.getContent().then(function() {\n
                    // click on a node to see display the popup\n
                    $("div[title=\'Node 1\']").simulate("dblclick");\n
                    // Promises that handle the dialog actions are not available\n
                    // immediately after clicking.\n
                    var promise = RSVP.Promise(function(resolve) {\n
                        var fillDialog = function() {\n
                            if (!jsplumb_gadget.props.dialog_promise) {\n
                                // Dialog not ready. Let\'s retry later.\n
                                // XXX this condition is actually incorrect. We need to wait\n
                                // for the event listener to have been registered for the\n
                                // dialog buttons. This setTimeout is good enough for now.\n
                                return setTimeout(fillDialog, 1e3);\n
                            }\n
                            // check displayed values\n
                            equal($("input[name=\'id\']").val(), "N1");\n
                            equal($("input[name=\'name\']").val(), "Node 1");\n
                            equal($("input[name=\'shape\']").val(), "square");\n
                            // change the name\n
                            $("input[name=\'name\']").val("Modified Name");\n
                            equal(1, $("input[value=\'Validate\']").length, "There should be one validate button");\n
                            // and save\n
                            $("input[value=\'Validate\']").click();\n
                            // resolve our test promise once the dialog handling promise is\n
                            // finished.\n
                            jsplumb_gadget.props.dialog_promise.then(resolve);\n
                        };\n
                        fillDialog();\n
                    });\n
                    return promise.then(function() {\n
                        return jsplumb_gadget.getContent().then(function(content) {\n
                            var graph = JSON.parse(content).graph, node = graph.node.N1;\n
                            equal("Modified Name", node.name, "Data is modified");\n
                            equal("Modified Name", $("div#" + jsplumb_gadget.props.node_id_to_dom_element_id.N1).text(), "DOM is modified");\n
                            equal(1, $("div[title=\'Modified Name\']").length, "DOM title attribute is modified");\n
                        });\n
                    });\n
                });\n
            }\n
            g.declareGadget("./index.html", {\n
                element: document.querySelector("#qunit-fixture")\n
            }).then(function(new_gadget) {\n
                jsplumb_gadget = new_gadget;\n
                jsplumb_gadget.render(sample_data_graph);\n
            }).then(runTest).fail(error_handler).always(start);\n
        });\n
        test("Node can be connected", function() {\n
            var jsplumb_gadget;\n
            stop();\n
            function runTest() {\n
                return jsplumb_gadget.getContent().then(function(content) {\n
                    var node1 = jsplumb_gadget.props.main.querySelector("div[title=\'Node 1\']"), node2 = jsplumb_gadget.props.main.querySelector("div[title=\'Node 2\']");\n
                    equal(0, Object.keys(JSON.parse(content).graph.edge).length, "There are no edge at the beginning");\n
                    jsplumb_gadget.props.jsplumb_instance.connect({\n
                        source: node1.id,\n
                        target: node2.id\n
                    });\n
                }).then(function() {\n
                    return jsplumb_gadget.getContent();\n
                }).then(function(content) {\n
                    var edge, graph = JSON.parse(content).graph;\n
                    equal(2, Object.keys(graph.node).length, "We still have 2 nodes");\n
                    equal(1, Object.keys(graph.edge).length, "We have 1 edge");\n
                    edge = graph.edge[Object.keys(graph.edge)[0]];\n
                    // XXX how edge class would be set ? the first one from schema ? Yes ! TODO: update test\n
                    //equal("Example.Edge", edge._class, "Edge class is correct");\n
                    equal("N1", edge.source, "edge source is correct");\n
                    equal("N2", edge.destination, "edge destination is correct");\n
                });\n
            }\n
            g.declareGadget("./index.html", {\n
                element: document.querySelector("#qunit-fixture")\n
            }).then(function(new_gadget) {\n
                jsplumb_gadget = new_gadget;\n
                jsplumb_gadget.render(sample_data_graph_not_connected);\n
            }).then(runTest).fail(error_handler).always(start);\n
        });\n
        test("Node can be deleted", function() {\n
            var jsplumb_gadget;\n
            stop();\n
            function runTest() {\n
                return jsplumb_gadget.getContent().then(function() {\n
                    equal(1, $("div[title=\'Node 1\']").length, "node 1 is visible");\n
                    equal(1, $("._jsPlumb_connector").length, "there is 1 connection");\n
                    // click on node 1 to see display the popup\n
                    $("div[title=\'Node 1\']").simulate("dblclick");\n
                    // Promises that handle the dialog actions are not available\n
                    // immediately after clicking.\n
                    var promise = RSVP.Promise(function(resolve) {\n
                        var waitForDialogAndDelete = function() {\n
                            if (!jsplumb_gadget.props.dialog_promise) {\n
                                // Dialog not ready. Let\'s retry later.\n
                                // XXX this condition is actually incorrect. We need to wait\n
                                // for the event listener to have been registered for the\n
                                // dialog buttons. This setTimeout is good enough for now.\n
                                return setTimeout(waitForDialogAndDelete, 1e3);\n
                            }\n
                            equal(1, $("input[value=\'Delete\']").length, "There should be one delete button");\n
                            $("input[value=\'Delete\']").click();\n
                            // resolve our test promise once the dialog handling promise is\n
                            // finished.\n
                            jsplumb_gadget.props.dialog_promise.then(resolve);\n
                        };\n
                        waitForDialogAndDelete();\n
                    });\n
                    return promise.then(function() {\n
                        return jsplumb_gadget.getContent().then(function(content) {\n
                            var graph = JSON.parse(content).graph;\n
                            equal(1, Object.keys(graph.node).length, "node is removed from data");\n
                            equal(0, Object.keys(graph.edge).length, "edge referencing this node is also removed");\n
                            equal(0, $("div[title=\'Node 1\']").length, "DOM element for node is removed");\n
                            equal(0, $("._jsPlumb_connector").length, "DOM element for edge is removed");\n
                        });\n
                    });\n
                });\n
            }\n
            g.declareGadget("./index.html", {\n
                element: document.querySelector("#qunit-fixture")\n
            }).then(function(new_gadget) {\n
                jsplumb_gadget = new_gadget;\n
                jsplumb_gadget.render(sample_data_graph);\n
            }).then(runTest).fail(error_handler).always(start);\n
        });\n
        test("Node id can be changed (connections are updated and node can be edited afterwards)", function() {\n
            var jsplumb_gadget;\n
            stop();\n
            function runTest() {\n
                return jsplumb_gadget.getContent().then(function() {\n
                    // click on a node to see display the popup\n
                    $("div[title=\'Node 1\']").simulate("dblclick");\n
                    // Promises that handle the dialog actions are not available\n
                    // immediately after clicking.\n
                    var promise = RSVP.Promise(function(resolve) {\n
                        var fillDialog = function() {\n
                            if (!jsplumb_gadget.props.dialog_promise) {\n
                                // Dialog not ready. Let\'s retry later.\n
                                // XXX this condition is actually incorrect. We need to wait\n
                                // for the event listener to have been registered for the\n
                                // dialog buttons. This setTimeout is good enough for now.\n
                                return setTimeout(fillDialog, 1e3);\n
                            }\n
                            equal($("input[name=\'id\']").val(), "N1");\n
                            // change the id\n
                            $("input[name=\'id\']").val("N1b");\n
                            equal(1, $("input[value=\'Validate\']").length, "There should be one validate button");\n
                            $("input[value=\'Validate\']").click();\n
                            // resolve our test promise once the dialog handling promise is\n
                            // finished.\n
                            jsplumb_gadget.props.dialog_promise.then(resolve);\n
                        };\n
                        fillDialog();\n
                    });\n
                    return promise.then(function() {\n
                        return jsplumb_gadget.getContent().then(function(content) {\n
                            var graph = JSON.parse(content).graph;\n
                            equal(2, Object.keys(graph.node).length, "We still have two nodes");\n
                            ok(graph.node.N1b !== undefined, "Node Id changed");\n
                            equal(1, Object.keys(graph.edge).length, "We still have one connection");\n
                            equal("N1b", graph.edge.edge1.source, "Connection source has been updated");\n
                        });\n
                    });\n
                });\n
            }\n
            g.declareGadget("./index.html", {\n
                element: document.querySelector("#qunit-fixture")\n
            }).then(function(new_gadget) {\n
                jsplumb_gadget = new_gadget;\n
                jsplumb_gadget.render(sample_data_graph);\n
            }).then(runTest).fail(error_handler).always(start);\n
        });\n
        test("New node can be edited", function() {\n
            var jsplumb_gadget, node_id;\n
            stop();\n
            function runTest() {\n
                // XXX here I used getContent to have a promise, but there must be a\n
                // more elegant way.\n
                return jsplumb_gadget.getContent().then(function() {\n
                    // fake a drop event\n
                    var e = new window.Event("drop");\n
                    e.dataTransfer = {\n
                        getData: function(type) {\n
                            // make sure we are called properly\n
                            equal("application/json", type, "The drag&dropped element must have data type application/json");\n
                            return JSON.stringify("Example.Node");\n
                        }\n
                    };\n
                    jsplumb_gadget.props.main.dispatchEvent(e);\n
                }).then(function() {\n
                    return jsplumb_gadget.getContent();\n
                }).then(function(content) {\n
                    var node, graph = JSON.parse(content).graph;\n
                    equal(1, Object.keys(graph.node).length);\n
                    node_id = Object.keys(graph.node)[0];\n
                    node = graph.node[node_id];\n
                    equal("Example.Node", node._class);\n
                }).then(function() {\n
                    // click the new node to see display the popup\n
                    // XXX at the moment nodes have class window\n
                    equal(1, $("div.window").length, "We have a new node");\n
                    $("div.window").simulate("dblclick");\n
                    // Promises that handle the dialog actions are not available\n
                    // immediately after clicking.\n
                    var promise = RSVP.Promise(function(resolve) {\n
                        var fillDialog = function() {\n
                            if (!jsplumb_gadget.props.dialog_promise) {\n
                                // Dialog not ready. Let\'s retry later.\n
                                // XXX this condition is actually incorrect. We need to wait\n
                                // for the event listener to have been registered for the\n
                                // dialog buttons. This setTimeout is good enough for now.\n
                                return setTimeout(fillDialog, 1e3);\n
                            }\n
                            // check displayed values\n
                            equal($("input[name=\'id\']").val(), node_id);\n
                            equal($("input[name=\'name\']").val(), "");\n
                            equal($("input[name=\'shape\']").val(), "");\n
                            // change the name\n
                            $("input[name=\'name\']").val("Modified Name");\n
                            equal(1, $("input[value=\'Validate\']").length, "There should be one validate button");\n
                            // and save\n
                            $("input[value=\'Validate\']").click();\n
                            // resolve our test promise once the dialog handling promise is\n
                            // finished.\n
                            jsplumb_gadget.props.dialog_promise.then(resolve);\n
                        };\n
                        fillDialog();\n
                    });\n
                    return promise.then(function() {\n
                        return jsplumb_gadget.getContent().then(function(content) {\n
                            var graph = JSON.parse(content).graph, node = graph.node[node_id];\n
                            equal("Modified Name", node.name, "Data is modified");\n
                            equal("Modified Name", $("div.window").text(), "DOM is modified");\n
                        });\n
                    });\n
                });\n
            }\n
            g.declareGadget("./index.html", {\n
                element: document.querySelector("#qunit-fixture")\n
            }).then(function(new_gadget) {\n
                jsplumb_gadget = new_gadget;\n
                jsplumb_gadget.render(sample_data_empty_graph);\n
            }).then(runTest).fail(error_handler).always(start);\n
        });\n
        test("New node can be deleted", function() {\n
            var jsplumb_gadget, node_id;\n
            stop();\n
            function runTest() {\n
                // XXX here I used getContent to have a promise, but there must be a\n
                // more elegant way.\n
                return jsplumb_gadget.getContent().then(function() {\n
                    // fake a drop event\n
                    var e = new window.Event("drop");\n
                    e.dataTransfer = {\n
                        getData: function(type) {\n
                            // make sure we are called properly\n
                            equal("application/json", type, "The drag&dropped element must have data type application/json");\n
                            return JSON.stringify("Example.Node");\n
                        }\n
                    };\n
                    jsplumb_gadget.props.main.dispatchEvent(e);\n
                }).then(function() {\n
                    return jsplumb_gadget.getContent();\n
                }).then(function(content) {\n
                    var node, graph = JSON.parse(content).graph;\n
                    equal(1, Object.keys(graph.node).length);\n
                    node_id = Object.keys(graph.node)[0];\n
                    node = graph.node[node_id];\n
                    equal("Example.Node", node._class);\n
                }).then(function() {\n
                    // click the new node to see display the popup\n
                    // XXX at the moment nodes have class window\n
                    equal(1, $("div.window").length, "We have a new node");\n
                    $("div.window").simulate("dblclick");\n
                    // Promises that handle the dialog actions are not available\n
                    // immediately after clicking.\n
                    var promise = RSVP.Promise(function(resolve) {\n
                        var waitForDialogAndDelete = function() {\n
                            if (!jsplumb_gadget.props.dialog_promise) {\n
                                // Dialog not ready. Let\'s retry later.\n
                                // XXX this condition is actually incorrect. We need to wait\n
                                // for the event listener to have been registered for the\n
                                // dialog buttons. This setTimeout is good enough for now.\n
                                return setTimeout(waitForDialogAndDelete, 1e3);\n
                            }\n
                            equal(1, $("input[value=\'Delete\']").length, "There should be one delete button");\n
                            $("input[value=\'Delete\']").click();\n
                            // resolve our test promise once the dialog handling promise is\n
                            // finished.\n
                            jsplumb_gadget.props.dialog_promise.then(resolve);\n
                        };\n
                        waitForDialogAndDelete();\n
                    });\n
                    return promise.then(function() {\n
                        return jsplumb_gadget.getContent().then(function(content) {\n
                            var graph = JSON.parse(content).graph;\n
                            equal(0, Object.keys(graph.node).length, "node is removed from data");\n
                            equal(0, $("div.window").length, "DOM is modified");\n
                        });\n
                    });\n
                });\n
            }\n
            g.declareGadget("./index.html", {\n
                element: document.querySelector("#qunit-fixture")\n
            }).then(function(new_gadget) {\n
                jsplumb_gadget = new_gadget;\n
                jsplumb_gadget.render(sample_data_empty_graph);\n
            }).then(runTest).fail(error_handler).always(start);\n
        });\n
    });\n
})(rJS, JSON, QUnit, RSVP, jQuery);

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>26016</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
