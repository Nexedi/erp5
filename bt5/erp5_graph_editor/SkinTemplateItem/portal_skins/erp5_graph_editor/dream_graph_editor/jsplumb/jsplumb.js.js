 /* ===========================================================================
  * Copyright 2013-2015 Nexedi SA and Contributors
  *
  * This file is part of DREAM.
  *
  * DREAM is free software: you can redistribute it and/or modify
  * it under the terms of the GNU Lesser General Public License as published by
  * the Free Software Foundation, either version 3 of the License, or
  * (at your option) any later version.
  *
  * DREAM is distributed in the hope that it will be useful,
  * but WITHOUT ANY WARRANTY; without even the implied warranty of
  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  * GNU Lesser General Public License for more details.
  *
  * You should have received a copy of the GNU Lesser General Public License
  * along with DREAM.  If not, see <http://www.gnu.org/licenses/>.
  * ==========================================================================*/
 /*global console, window, RSVP, rJS, $, jsPlumb, Handlebars,
     loopEventListener, promiseEventListener, DOMParser, Springy */
 /*jslint unparam: true todo: true */
 (function(RSVP, rJS, $, jsPlumb, Handlebars, loopEventListener, promiseEventListener, DOMParser, Springy) {
   "use strict";
   /* TODO:
    * less dependancies ( promise event listner ? )
    * no more handlebars
    * id should not always be modifiable
    * drop zoom level
    * rename draggable()
    * factorize node & edge popup edition
    */
   /*jslint nomen: true */
   var gadget_klass = rJS(window),
     domParser = new DOMParser(),
     node_template_source = gadget_klass.__template_element.getElementById("node-template").innerHTML,
     node_template = Handlebars.compile(node_template_source),
     popup_edit_template = gadget_klass.__template_element.getElementById("popup-edit-template").innerHTML;

   function layoutGraph(graph_data) {
     // Promise returning the graph once springy calculated the layout.
     // If the graph already contain layout, return it as is.
     function resolver(resolve, reject) {
       try {
         var springy_graph = new Springy.Graph(),
             max_iterations = 100, // we stop layout after 100 iterations.
             loop = 0,
             springy_nodes = {},
             drawn_nodes = {},
             min_x=100, max_x=0, min_y=100, max_y=0;
         // make a Springy graph with our graph
         $.each(graph_data.node, function(key, value) {
           if (value.coordinate) {
             // graph already has a layout, no need to layout again
             return resolve(graph_data);
           }
           springy_nodes[key] = springy_graph.newNode({node_id: key});
         });
         $.each(graph_data.edge, function(key, value) {
           springy_graph.newEdge(springy_nodes[value.source], springy_nodes[value.destination]);
         });

         var layout = new Springy.Layout.ForceDirected(springy_graph, 400.0, 400.0, 0.5);
         var renderer = new Springy.Renderer(
           layout,
           function clear() {},
           function drawEdge(edge, p1, p2) {},
           function drawNode(node, p) {
             drawn_nodes[node.data.node_id] = p;
             if ( ++loop > max_iterations) {
               renderer.stop();
             }
           },
           function onRenderStop() {
             // calculate the min and max of x and y
             $.each(graph_data.node, function(key, value) {
               if (drawn_nodes[key].x > max_x) {
                 max_x = drawn_nodes[key].x;
               }
               if (drawn_nodes[key].x < min_x) {
                 min_x = drawn_nodes[key].x;
               }
               if (drawn_nodes[key].y > max_y) {
                 max_y = drawn_nodes[key].y;
               }
               if (drawn_nodes[key].y < min_y) {
                 min_y = drawn_nodes[key].y;
               }
             });
             // "resample" the positions from 0 to 1, the scale used by this gadget.
             // We keep a 5% margin
             $.each(graph_data.node, function(key, value) {
               graph_data.node[key].coordinate = {
                  left: 0.05 + 0.9 * (drawn_nodes[key].x - min_x) / (max_x - min_x),
                  top: 0.05 + 0.9 * (drawn_nodes[key].y - min_y) / (max_y - min_y)
               };
             });
             resolve(graph_data);
           }
         );
         renderer.start();
        } catch (e) {
         reject(e);
       }
     }
     return new RSVP.Promise(resolver);
   }

   function loopJsplumbBind(gadget, type, callback) {
     //////////////////////////
     // Infinite event listener (promise is never resolved)
     // eventListener is removed when promise is cancelled/rejected
     //////////////////////////
     var handle_event_callback, callback_promise, jsplumb_instance = gadget.props.jsplumb_instance;

     function cancelResolver() {
       if (callback_promise !== undefined && typeof callback_promise.cancel === "function") {
         callback_promise.cancel();
       }
     }

     function canceller() {
       if (handle_event_callback !== undefined) {
         jsplumb_instance.unbind(type);
       }
       cancelResolver();
     }

     function resolver(resolve, reject) {
       handle_event_callback = function() {
         var args = arguments;
         cancelResolver();
         callback_promise = new RSVP.Queue().push(function() {
           return callback.apply(jsplumb_instance, args);
         }).push(undefined, function(error) {
           if (!(error instanceof RSVP.CancellationError)) {
             canceller();
             reject(error);
           }
         });
       };
       jsplumb_instance.bind(type, handle_event_callback);
     }
     return new RSVP.Promise(resolver, canceller);
   }

   function getNodeId(gadget, element_id) {
     // returns the ID of the node in the graph from its DOM element id
     var node_id;
     $.each(gadget.props.node_id_to_dom_element_id, function(k, v) {
       if (v === element_id) {
         node_id = k;
         return false;
       }
     });
     return node_id;
   }

   function generateNodeId(gadget, element) {
     // Generate a node id
     var n = 1,
       class_def = gadget.props.data.class_definition[element._class],
       id = class_def.short_id || element._class;
     while (gadget.props.data.graph.node[id + n] !== undefined) {
       n += 1;
     }
     return id + n;
   }

   function generateDomElementId(gadget_element) {
     // Generate a probably unique DOM element ID.
     var n = 1;
     while ($(gadget_element).find("#DreamNode_" + n).length > 0) {
       n += 1;
     }
     return "DreamNode_" + n;
   }

   function getDefaultEdgeClass(gadget) {
     var class_definition = gadget.props.data.class_definition;
     for (var key in class_definition) {
       if (class_definition.hasOwnProperty(key) && class_definition[key]._class === 'edge') {
         return key;
       }
     }
     return "Dream.Edge";
   }

   function updateConnectionData(gadget, connection, remove) {
     if (connection.ignoreEvent) {
       // this hack is for edge edition. Maybe there I missed one thing and
       // there is a better way.
       return;
     }
     if (remove) {
       delete gadget.props.data.graph.edge[connection.id];
     } else {
       var edge_data = gadget.props.data.graph.edge[connection.id] || {
         _class: getDefaultEdgeClass(gadget)
       };
       edge_data.source = getNodeId(gadget, connection.sourceId);
       edge_data.destination = getNodeId(gadget, connection.targetId);
       gadget.props.data.graph.edge[connection.id] = edge_data;
     }
     gadget.notifyDataChanged();
   }

   function convertToAbsolutePosition(gadget, x, y) {
     var zoom_level = gadget.props.zoom_level,
       canvas_size_x = $(gadget.props.main).width(),
       canvas_size_y = $(gadget.props.main).height(),
       size_x = $(gadget.props.element).find(".dummy_window").width() * zoom_level,
       size_y = $(gadget.props.element).find(".dummy_window").height() * zoom_level,
       top = Math.floor(y * (canvas_size_y - size_y)) + "px",
       left = Math.floor(x * (canvas_size_x - size_x)) + "px";
     return [left, top];
   }

   function convertToRelativePosition(gadget, x, y) {
     var zoom_level = gadget.props.zoom_level,
       canvas_size_x = $(gadget.props.main).width(),
       canvas_size_y = $(gadget.props.main).height(),
       size_x = $(gadget.props.element).find(".dummy_window").width() * zoom_level,
       size_y = $(gadget.props.element).find(".dummy_window").height() * zoom_level,
       top = Math.max(Math.min(y.replace("px", "") / (canvas_size_y - size_y), 1), 0),
       left = Math.max(Math.min(x.replace("px", "") / (canvas_size_x - size_x), 1), 0);
     return [left, top];
   }

   function updateElementCoordinate(gadget, node_id, coordinate) {
     var element_id = gadget.props.node_id_to_dom_element_id[node_id],
       element,
       relative_position;
     if (coordinate === undefined) {
       element = $(gadget.props.element).find("#" + element_id);
       relative_position = convertToRelativePosition(gadget, element.css("left"), element.css("top"));
       coordinate = {
         left: relative_position[0],
         top: relative_position[1]
       };
     }
     gadget.props.data.graph.node[node_id].coordinate = coordinate;
     gadget.notifyDataChanged();
     return coordinate;
   }

   function draggable(gadget) {
     var jsplumb_instance = gadget.props.jsplumb_instance,
       stop = function(element) {
         updateElementCoordinate(gadget, getNodeId(gadget, element.target.id));
       };

     // XXX This function should only touch the node element that we just added.
     jsplumb_instance.draggable(jsplumb_instance.getSelector(".window"), {
       containment: "parent",
       grid: [10, 10],
       stop: stop
     });
     jsplumb_instance.makeSource(jsplumb_instance.getSelector(".window"), {
       filter: ".ep",
       anchor: "Continuous",
       connector: ["StateMachine", {
         curviness: 20
       }],
       connectorStyle: {
         strokeStyle: "#5c96bc",
         lineWidth: 2,
         outlineColor: "transparent",
         outlineWidth: 4
       }
     });
     jsplumb_instance.makeTarget(jsplumb_instance.getSelector(".window"), {
       dropOptions: {
         hoverClass: "dragHover"
       },
       anchor: "Continuous"
     });
   }

   function updateNodeStyle(gadget, element_id) {
       // Update node size according to the zoom level
       // XXX does nothing for now
       var zoom_level = gadget.props.zoom_level,
         element = $(gadget.props.element).find("#" + element_id),
         new_value;
       $.each(gadget.props.style_attr_list, function(i, j) {
         new_value = element.css(j).replace("px", "") * zoom_level + "px";
         element.css(j, new_value);
       });
     }

   function removeElement(gadget, node_id) {
     var element_id = gadget.props.node_id_to_dom_element_id[node_id];
     gadget.props.jsplumb_instance.removeAllEndpoints($(gadget.props.element).find("#" + element_id));
     $(gadget.props.element).find("#" + element_id).remove();
     delete gadget.props.data.graph.node[node_id];
     delete gadget.props.node_id_to_dom_element_id[node_id];
     $.each(gadget.props.data.graph.edge, function(k, v) {
       if (node_id === v.source || node_id === v.destination) {
         delete gadget.props.data.graph.edge[k];
       }
     });
     gadget.notifyDataChanged();
   }

  function updateElementData(gadget, node_id, data) {
    var element_id = gadget.props.node_id_to_dom_element_id[node_id],
      new_id = data.id || data.data.id;
    $(gadget.props.element).find("#" + element_id).text(data.data.name || new_id)
        .attr("title", data.data.name || new_id)
        .append('<div class="ep"></div></div>');

    delete data.id;

    $.extend(gadget.props.data.graph.node[node_id], data.data);
    if (new_id && new_id !== node_id) {
      gadget.props.data.graph.node[new_id] = gadget.props.data.graph.node[node_id];
      delete gadget.props.data.graph.node[node_id];

      gadget.props.node_id_to_dom_element_id[new_id] = gadget.props.node_id_to_dom_element_id[node_id];
      delete gadget.props.node_id_to_dom_element_id[node_id];

      delete gadget.props.data.graph.node[new_id].id;
      $.each(gadget.props.data.graph.edge, function (k, v) {
        if (v.source === node_id) {
          v.source = new_id;
        }
        if (v.destination === node_id) {
          v.destination = new_id;
        }
      });
    }
    gadget.notifyDataChanged();
  }


   function addEdge(gadget, edge_id, edge_data) {
     var overlays = [],
       connection,
       label = '';
     if (edge_data.name) {
       label = edge_data.name;
       if (edge_data.path) {
         label = label.link(edge_data.path)
       }
     }
     if (edge_data.name_path_dict) {
       var linked_name_list = []
       for (var name in edge_data.name_path_dict) {
         linked_name_list.push(name.link(edge_data.name_path_dict[name]));
       }
       label = linked_name_list.join(', ');
     }
     if (label) {
       overlays = [
         ["Label", {
           cssClass: "l1 component label",
           label: label
         }]
       ];
     }
     if (gadget.props.data.graph.node[edge_data.source] === undefined) {
       throw new Error("Error adding edge " +  edge_id + " Source " + edge_data.source + " does not exist");
     }
     if (gadget.props.data.graph.node[edge_data.destination] === undefined) {
       throw new Error("Edge adding edge " +  edge_id + " Destination " + edge_data.destination + " does not exist");
     }
     // If an edge has this data:
     // { _class: 'Edge',
     //   source: 'N1',
     //   destination: 'N2',
     //   jsplumb_source_endpoint: 'BottomCenter',
     //   jsplumb_destination_endpoint: 'LeftMiddle',
     //   jsplumb_connector: 'Flowchart' }
     // Then it is rendered using a flowchart connector. The difficulty is that
     // jsplumb does not let you configure the connector type on the edge, but
     // on the source endpoint. One solution seem to create all types of
     // endpoints on nodes.
     if (edge_data.jsplumb_connector === "Flowchart") {
       connection = gadget.props.jsplumb_instance.connect({
         uuids: [edge_data.source + ".flowChart" + edge_data.jsplumb_source_endpoint,
           edge_data.destination + ".flowChart" + edge_data.jsplumb_destination_endpoint
         ],
         overlays: overlays
       });
     } else {
       connection = gadget.props.jsplumb_instance.connect({
         source: gadget.props.node_id_to_dom_element_id[edge_data.source],
         target: gadget.props.node_id_to_dom_element_id[edge_data.destination],
         Connector: ["Bezier", {
           curviness: 75
         }],
         overlays: overlays
       });
     }
     // set data for 'connection' event that will be called "later"
     gadget.props.data.graph.edge[edge_id] = edge_data;
     // jsplumb assigned an id, but we are controlling ids ourselves.
     connection.id = edge_id;
   }

   function expandSchema(class_definition, full_schema) {
     // minimal expanding of json schema, supports merging allOf and $ref
     // references
     // XXX this should probably be moved to fieldset ( and not handle
     // class_definition here)

     function resolveReference(ref, schema) {
       // 2 here is for #/
       var i, ref_path = ref.substr(2, ref.length),
         parts = ref_path.split("/");
       for (i = 0; i < parts.length; i += 1) {
         schema = schema[parts[i]];
       }
       return schema;
     }

     function clone(obj) {
       return JSON.parse(JSON.stringify(obj));
     }

     var referenced,
       i,
       property,
       expanded_class_definition = clone(class_definition) || {};


     if (!expanded_class_definition.properties) {
       expanded_class_definition.properties = {};
     }
     // expand direct ref
     if (class_definition.$ref) {
       referenced = expandSchema(resolveReference(class_definition.$ref, full_schema.class_definition), full_schema);
       $.extend(expanded_class_definition, referenced);
       delete expanded_class_definition.$ref;
     }
     // expand ref in properties
     for (property in class_definition.properties) {
       if (class_definition.properties.hasOwnProperty(property)) {
         if (class_definition.properties[property].$ref) {
           referenced = expandSchema(resolveReference(class_definition.properties[property].$ref, full_schema.class_definition), full_schema);
           $.extend(expanded_class_definition.properties[property], referenced);
           delete expanded_class_definition.properties[property].$ref;
         } else {
           if (class_definition.properties[property].type === "object") {
             // no reference, but we expand anyway because we need to recurse in case there is a ref in an object property
             referenced = expandSchema(class_definition.properties[property], full_schema);
             $.extend(expanded_class_definition.properties[property], referenced);
           }
         }
       }
     }
     if (class_definition.oneOf) {
       expanded_class_definition.oneOf = [];
       for (i = 0; i < class_definition.oneOf.length; i += 1) {
         expanded_class_definition.oneOf.push(expandSchema(class_definition.oneOf[i], full_schema));
       }
     }
     if (class_definition.allOf) {
       for (i = 0; i < class_definition.allOf.length; i += 1) {
         referenced = expandSchema(class_definition.allOf[i], full_schema);
         if (referenced.properties) {
           $.extend(expanded_class_definition.properties, referenced.properties);
           delete referenced.properties;
         }
         $.extend(expanded_class_definition, referenced);
       }
       if (expanded_class_definition.allOf) {
         delete expanded_class_definition.allOf;
       }
     }
     if (expanded_class_definition.$ref) {
       delete expanded_class_definition.$ref;
     }
     return clone(expanded_class_definition);
   }

   function waitForConnection(gadget) {
     return loopJsplumbBind(gadget, "connection", function(info, originalEvent) {
       updateConnectionData(gadget, info.connection, false);
     });
   }

   function waitForConnectionDetached(gadget) {
     return loopJsplumbBind(gadget, "connectionDetached", function(info, originalEvent) {
       updateConnectionData(gadget, info.connection, true);
     });
   }

   function addNode(gadget, node_id, node_data) {
     var render_element = $(gadget.props.main),
       class_definition = gadget.props.data.class_definition[node_data._class],
       coordinate = node_data.coordinate,
       dom_element_id,
       box,
       absolute_position,
       domElement;

     dom_element_id = generateDomElementId(gadget.props.element);
     gadget.props.node_id_to_dom_element_id[node_id] = dom_element_id;
     node_data.name = node_data.name || class_definition.name;
     gadget.props.data.graph.node[node_id] = node_data;
     if (coordinate === undefined) {
       coordinate = {
         top: 0,
         left: 0
       };
     }
     node_data.coordinate = updateElementCoordinate(gadget, node_id, coordinate);
     /*jslint nomen: true*/
     domElement = domParser.parseFromString(node_template({
       "class": node_data._class.replace(".", "-"),
       element_id: dom_element_id,
       title: node_data.name || node_data.id,
       name: node_data.name || node_data.id,
       name_href: node_data.path
     }), "text/html").querySelector(".window");
     render_element.append(domElement);
     box = $(gadget.props.element).find("#" + dom_element_id);
     absolute_position = convertToAbsolutePosition(gadget, coordinate.left, coordinate.top);
     if (class_definition && class_definition.css) {
       box.css(class_definition.css);
     }
     box.css("top", absolute_position[1]);
     box.css("left", absolute_position[0]);
     if (node_data.is_initial_state) {
       box.css("border", "double #000000");
       box.css("font-weight", "bold");

     }
     updateNodeStyle(gadget, dom_element_id);
     draggable(gadget);
     // XXX make only this element draggable.
     // Add some flowchart endpoints
     // TODO: add them all !
     gadget.props.jsplumb_instance.addEndpoint(dom_element_id, {
       isSource: true,
       maxConnections: -1,
       connector: ["Flowchart", {
         stub: [40, 60],
         gap: 10,
         cornerRadius: 5,
         alwaysRespectStubs: true
       }]
     }, {
       anchor: "BottomCenter",
       uuid: node_id + ".flowchartBottomCenter"
     });
     gadget.props.jsplumb_instance.addEndpoint(dom_element_id, {
       isTarget: true,
       maxConnections: -1
     }, {
       anchor: "LeftMiddle",
       uuid: node_id + ".flowChartLeftMiddle"
     });
     gadget.notifyDataChanged();
   }

   function waitForDrop(gadget) {
     var callback;

     function canceller() {
         if (callback !== undefined) {
           gadget.props.main.removeEventListener("drop", callback, false);
         }
       }
       /*jslint unparam: true*/
     function resolver(resolve, reject) {
       callback = function(evt) {
         try {
           var class_name, offset = $(gadget.props.main).offset(),
             relative_position = convertToRelativePosition(gadget, evt.clientX - offset.left + "px", evt.clientY - offset.top + "px");
           try {
             // html5 compliant browser
             class_name = JSON.parse(evt.dataTransfer.getData("application/json"));
           } catch (e) {
             // internet explorer
             class_name = JSON.parse(evt.dataTransfer.getData("text"));
           }
           addNode(gadget, generateNodeId(gadget, {
             _class: class_name
           }), {
             coordinate: {
               left: relative_position[0],
               top: relative_position[1]
             },
             _class: class_name
           });
         } catch (e) {
           reject(e);
         }
       };
       gadget.props.main.addEventListener("drop", callback, false);
     }
     return new RSVP.all([ // loopEventListener adds an event listener that will prevent default for
       // dragover
       loopEventListener(gadget.props.main, "dragover", false, function() {
         return undefined;
       }), RSVP.Promise(resolver, canceller)
     ]);
   }

   gadget_klass.ready(function (g) {
      g.props = {};
    })
    .ready(function (g) {
      return g.getElement().push(function (element) {
        g.props.element = element;
      });
    })
   .ready(function(g) {
     g.props.node_id_to_dom_element_id = {};
     g.props.zoom_level = 1;
     g.props.style_attr_list = ["width", "height", "padding-top", "line-height"];
     g.getElement().then(function(element) {
       g.props.element = element;
     });
   })
   .declareAcquiredMethod("notifyDataChanged", "notifyDataChanged")
   .declareMethod("render", function(data) {
     var gadget = this, jsplumb_instance;

     this.props.data = {};
     if (data.key) {
       // Gadget embedded in ERP5
       this.props.erp5_key = data.key;
       data = data.value;
     }

     this.props.main = this.props.element.querySelector(".graph_container");

     if (data) {
       this.props.data = JSON.parse(data);

// XXX how to make queue ??
       return layoutGraph(this.props.data.graph).then(function(graph_data) {
         gadget.props.data.graph = graph_data;
         // load the data
         $.each(gadget.props.data.graph.node, function(key, value) {
           addNode(gadget, key, value);
         });
         $.each(gadget.props.data.graph.edge, function(key, value) {
           addEdge(gadget, key, value);
         });
       });
     }
   })
   .declareMethod("getContent", function() {
     var ret = {};
     if (this.props.erp5_key) {
       // ERP5
       ret[this.props.erp5_key] = JSON.stringify(this.props.data);
       return ret;
     }
     return JSON.stringify(this.props.data);
   })
   .declareService(function() {
     var gadget = this, jsplumb_instance;
     this.props.main = this.props.element.querySelector(".graph_container");
     this.props.jsplumb_instance = jsplumb_instance = jsPlumb.getInstance();
     if (this.props.data) {
       // load the data
       $.each(this.props.data.graph.node, function(key, value) {
         addNode(gadget, key, value);
       });
       $.each(this.props.data.graph.edge, function(key, value) {
         addEdge(gadget, key, value);
       });
     }
     jsplumb_instance.setRenderMode(jsplumb_instance.SVG);
     jsplumb_instance.importDefaults({
       HoverPaintStyle: {
         strokeStyle: "#1e8151",
         lineWidth: 2
       },
       Endpoint: ["Dot", {
         radius: 2
       }],
       ConnectionOverlays: [
         ["Arrow", {
           location: 1,
           id: "arrow",
           length: 14,
           foldback: 0.8
         }]
       ],
       Container: this.props.main
     });
     draggable(gadget);

     this.props.nodes_click_monitor = this.__monitor;
     return RSVP.all([waitForDrop(gadget),
       waitForConnection(gadget),
       waitForConnectionDetached(gadget),
       gadget.props.nodes_click_monitor
     ]);
   });

 })(RSVP, rJS, $, jsPlumb, Handlebars, loopEventListener, promiseEventListener, DOMParser, Springy);