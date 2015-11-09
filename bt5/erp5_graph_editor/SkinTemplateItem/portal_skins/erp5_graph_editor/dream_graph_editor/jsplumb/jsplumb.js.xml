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
            <value> <string>ts47067792.54</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jsplumb.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

 /* ===========================================================================\n
  * Copyright 2013-2015 Nexedi SA and Contributors\n
  *\n
  * This file is part of DREAM.\n
  *\n
  * DREAM is free software: you can redistribute it and/or modify\n
  * it under the terms of the GNU Lesser General Public License as published by\n
  * the Free Software Foundation, either version 3 of the License, or\n
  * (at your option) any later version.\n
  *\n
  * DREAM is distributed in the hope that it will be useful,\n
  * but WITHOUT ANY WARRANTY; without even the implied warranty of\n
  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n
  * GNU Lesser General Public License for more details.\n
  *\n
  * You should have received a copy of the GNU Lesser General Public License\n
  * along with DREAM.  If not, see <http://www.gnu.org/licenses/>.\n
  * ==========================================================================*/\n
 /*global console, window, RSVP, rJS, $, jsPlumb, Handlebars,\n
     loopEventListener, promiseEventListener, DOMParser, Springy */\n
 /*jslint unparam: true todo: true */\n
 (function(RSVP, rJS, $, jsPlumb, Handlebars, loopEventListener, promiseEventListener, DOMParser, Springy) {\n
   "use strict";\n
   /* TODO:\n
    * less dependancies ( promise event listner ? )\n
    * no more handlebars\n
    * id should not always be modifiable\n
    * drop zoom level\n
    * rename draggable()\n
    * factorize node & edge popup edition\n
    */\n
   /*jslint nomen: true */\n
   var gadget_klass = rJS(window),\n
     domParser = new DOMParser(),\n
     node_template_source = gadget_klass.__template_element.getElementById("node-template").innerHTML,\n
     node_template = Handlebars.compile(node_template_source),\n
     popup_edit_template = gadget_klass.__template_element.getElementById("popup-edit-template").innerHTML;\n
\n
   function layoutGraph(graph_data) {\n
     // Promise returning the graph once springy calculated the layout.\n
     // If the graph already contain layout, return it as is.\n
     function resolver(resolve, reject) {\n
       try {\n
         var springy_graph = new Springy.Graph(),\n
             max_iterations = 100, // we stop layout after 100 iterations.\n
             loop = 0,\n
             springy_nodes = {},\n
             drawn_nodes = {},\n
             min_x=100, max_x=0, min_y=100, max_y=0;\n
         // make a Springy graph with our graph\n
         $.each(graph_data.node, function(key, value) {\n
           if (value.coordinate) {\n
             // graph already has a layout, no need to layout again\n
             return resolve(graph_data);\n
           }\n
           springy_nodes[key] = springy_graph.newNode({node_id: key});\n
         });\n
         $.each(graph_data.edge, function(key, value) {\n
           springy_graph.newEdge(springy_nodes[value.source], springy_nodes[value.destination]);\n
         });\n
\n
         var layout = new Springy.Layout.ForceDirected(springy_graph, 400.0, 400.0, 0.5);\n
         var renderer = new Springy.Renderer(\n
           layout,\n
           function clear() {},\n
           function drawEdge(edge, p1, p2) {},\n
           function drawNode(node, p) {\n
             drawn_nodes[node.data.node_id] = p;\n
             if ( ++loop > max_iterations) {\n
               renderer.stop();\n
             }\n
           },\n
           function onRenderStop() {\n
             // calculate the min and max of x and y\n
             $.each(graph_data.node, function(key, value) {\n
               if (drawn_nodes[key].x > max_x) {\n
                 max_x = drawn_nodes[key].x;\n
               }\n
               if (drawn_nodes[key].x < min_x) {\n
                 min_x = drawn_nodes[key].x;\n
               }\n
               if (drawn_nodes[key].y > max_y) {\n
                 max_y = drawn_nodes[key].y;\n
               }\n
               if (drawn_nodes[key].y < min_y) {\n
                 min_y = drawn_nodes[key].y;\n
               }\n
             });\n
             // "resample" the positions from 0 to 1, the scale used by this gadget.\n
             // We keep a 5% margin\n
             $.each(graph_data.node, function(key, value) {\n
               graph_data.node[key].coordinate = {\n
                  left: 0.05 + 0.9 * (drawn_nodes[key].x - min_x) / (max_x - min_x),\n
                  top: 0.05 + 0.9 * (drawn_nodes[key].y - min_y) / (max_y - min_y)\n
               };\n
             });\n
             resolve(graph_data);\n
           }\n
         );\n
         renderer.start();\n
        } catch (e) {\n
         reject(e);\n
       }\n
     }\n
     return new RSVP.Promise(resolver);\n
   }\n
\n
   function loopJsplumbBind(gadget, type, callback) {\n
     //////////////////////////\n
     // Infinite event listener (promise is never resolved)\n
     // eventListener is removed when promise is cancelled/rejected\n
     //////////////////////////\n
     var handle_event_callback, callback_promise, jsplumb_instance = gadget.props.jsplumb_instance;\n
\n
     function cancelResolver() {\n
       if (callback_promise !== undefined && typeof callback_promise.cancel === "function") {\n
         callback_promise.cancel();\n
       }\n
     }\n
\n
     function canceller() {\n
       if (handle_event_callback !== undefined) {\n
         jsplumb_instance.unbind(type);\n
       }\n
       cancelResolver();\n
     }\n
\n
     function resolver(resolve, reject) {\n
       handle_event_callback = function() {\n
         var args = arguments;\n
         cancelResolver();\n
         callback_promise = new RSVP.Queue().push(function() {\n
           return callback.apply(jsplumb_instance, args);\n
         }).push(undefined, function(error) {\n
           if (!(error instanceof RSVP.CancellationError)) {\n
             canceller();\n
             reject(error);\n
           }\n
         });\n
       };\n
       jsplumb_instance.bind(type, handle_event_callback);\n
     }\n
     return new RSVP.Promise(resolver, canceller);\n
   }\n
\n
   function getNodeId(gadget, element_id) {\n
     // returns the ID of the node in the graph from its DOM element id\n
     var node_id;\n
     $.each(gadget.props.node_id_to_dom_element_id, function(k, v) {\n
       if (v === element_id) {\n
         node_id = k;\n
         return false;\n
       }\n
     });\n
     return node_id;\n
   }\n
\n
   function generateNodeId(gadget, element) {\n
     // Generate a node id\n
     var n = 1,\n
       class_def = gadget.props.data.class_definition[element._class],\n
       id = class_def.short_id || element._class;\n
     while (gadget.props.data.graph.node[id + n] !== undefined) {\n
       n += 1;\n
     }\n
     return id + n;\n
   }\n
\n
   function generateDomElementId(gadget_element) {\n
     // Generate a probably unique DOM element ID.\n
     var n = 1;\n
     while ($(gadget_element).find("#DreamNode_" + n).length > 0) {\n
       n += 1;\n
     }\n
     return "DreamNode_" + n;\n
   }\n
\n
   function getDefaultEdgeClass(gadget) {\n
     var class_definition = gadget.props.data.class_definition;\n
     for (var key in class_definition) {\n
       if (class_definition.hasOwnProperty(key) && class_definition[key]._class === \'edge\') {\n
         return key;\n
       }\n
     }\n
     return "Dream.Edge";\n
   }\n
\n
   function updateConnectionData(gadget, connection, remove) {\n
     if (connection.ignoreEvent) {\n
       // this hack is for edge edition. Maybe there I missed one thing and\n
       // there is a better way.\n
       return;\n
     }\n
     if (remove) {\n
       delete gadget.props.data.graph.edge[connection.id];\n
     } else {\n
       var edge_data = gadget.props.data.graph.edge[connection.id] || {\n
         _class: getDefaultEdgeClass(gadget)\n
       };\n
       edge_data.source = getNodeId(gadget, connection.sourceId);\n
       edge_data.destination = getNodeId(gadget, connection.targetId);\n
       gadget.props.data.graph.edge[connection.id] = edge_data;\n
     }\n
     gadget.notifyDataChanged();\n
   }\n
\n
   function convertToAbsolutePosition(gadget, x, y) {\n
     var zoom_level = gadget.props.zoom_level,\n
       canvas_size_x = $(gadget.props.main).width(),\n
       canvas_size_y = $(gadget.props.main).height(),\n
       size_x = $(gadget.props.element).find(".dummy_window").width() * zoom_level,\n
       size_y = $(gadget.props.element).find(".dummy_window").height() * zoom_level,\n
       top = Math.floor(y * (canvas_size_y - size_y)) + "px",\n
       left = Math.floor(x * (canvas_size_x - size_x)) + "px";\n
     return [left, top];\n
   }\n
\n
   function convertToRelativePosition(gadget, x, y) {\n
     var zoom_level = gadget.props.zoom_level,\n
       canvas_size_x = $(gadget.props.main).width(),\n
       canvas_size_y = $(gadget.props.main).height(),\n
       size_x = $(gadget.props.element).find(".dummy_window").width() * zoom_level,\n
       size_y = $(gadget.props.element).find(".dummy_window").height() * zoom_level,\n
       top = Math.max(Math.min(y.replace("px", "") / (canvas_size_y - size_y), 1), 0),\n
       left = Math.max(Math.min(x.replace("px", "") / (canvas_size_x - size_x), 1), 0);\n
     return [left, top];\n
   }\n
\n
   function updateElementCoordinate(gadget, node_id, coordinate) {\n
     var element_id = gadget.props.node_id_to_dom_element_id[node_id],\n
       element,\n
       relative_position;\n
     if (coordinate === undefined) {\n
       element = $(gadget.props.element).find("#" + element_id);\n
       relative_position = convertToRelativePosition(gadget, element.css("left"), element.css("top"));\n
       coordinate = {\n
         left: relative_position[0],\n
         top: relative_position[1]\n
       };\n
     }\n
     gadget.props.data.graph.node[node_id].coordinate = coordinate;\n
     gadget.notifyDataChanged();\n
     return coordinate;\n
   }\n
\n
   function draggable(gadget) {\n
     var jsplumb_instance = gadget.props.jsplumb_instance,\n
       stop = function(element) {\n
         updateElementCoordinate(gadget, getNodeId(gadget, element.target.id));\n
       };\n
\n
     // XXX This function should only touch the node element that we just added.\n
     jsplumb_instance.draggable(jsplumb_instance.getSelector(".window"), {\n
       containment: "parent",\n
       grid: [10, 10],\n
       stop: stop\n
     });\n
     jsplumb_instance.makeSource(jsplumb_instance.getSelector(".window"), {\n
       filter: ".ep",\n
       anchor: "Continuous",\n
       connector: ["StateMachine", {\n
         curviness: 20\n
       }],\n
       connectorStyle: {\n
         strokeStyle: "#5c96bc",\n
         lineWidth: 2,\n
         outlineColor: "transparent",\n
         outlineWidth: 4\n
       }\n
     });\n
     jsplumb_instance.makeTarget(jsplumb_instance.getSelector(".window"), {\n
       dropOptions: {\n
         hoverClass: "dragHover"\n
       },\n
       anchor: "Continuous"\n
     });\n
   }\n
\n
   function updateNodeStyle(gadget, element_id) {\n
       // Update node size according to the zoom level\n
       // XXX does nothing for now\n
       var zoom_level = gadget.props.zoom_level,\n
         element = $(gadget.props.element).find("#" + element_id),\n
         new_value;\n
       $.each(gadget.props.style_attr_list, function(i, j) {\n
         new_value = element.css(j).replace("px", "") * zoom_level + "px";\n
         element.css(j, new_value);\n
       });\n
     }\n
\n
   function removeElement(gadget, node_id) {\n
     var element_id = gadget.props.node_id_to_dom_element_id[node_id];\n
     gadget.props.jsplumb_instance.removeAllEndpoints($(gadget.props.element).find("#" + element_id));\n
     $(gadget.props.element).find("#" + element_id).remove();\n
     delete gadget.props.data.graph.node[node_id];\n
     delete gadget.props.node_id_to_dom_element_id[node_id];\n
     $.each(gadget.props.data.graph.edge, function(k, v) {\n
       if (node_id === v.source || node_id === v.destination) {\n
         delete gadget.props.data.graph.edge[k];\n
       }\n
     });\n
     gadget.notifyDataChanged();\n
   }\n
\n
  function updateElementData(gadget, node_id, data) {\n
    var element_id = gadget.props.node_id_to_dom_element_id[node_id],\n
      new_id = data.id || data.data.id;\n
    $(gadget.props.element).find("#" + element_id).text(data.data.name || new_id)\n
        .attr("title", data.data.name || new_id)\n
        .append(\'<div class="ep"></div></div>\');\n
\n
    delete data.id;\n
\n
    $.extend(gadget.props.data.graph.node[node_id], data.data);\n
    if (new_id && new_id !== node_id) {\n
      gadget.props.data.graph.node[new_id] = gadget.props.data.graph.node[node_id];\n
      delete gadget.props.data.graph.node[node_id];\n
\n
      gadget.props.node_id_to_dom_element_id[new_id] = gadget.props.node_id_to_dom_element_id[node_id];\n
      delete gadget.props.node_id_to_dom_element_id[node_id];\n
\n
      delete gadget.props.data.graph.node[new_id].id;\n
      $.each(gadget.props.data.graph.edge, function (k, v) {\n
        if (v.source === node_id) {\n
          v.source = new_id;\n
        }\n
        if (v.destination === node_id) {\n
          v.destination = new_id;\n
        }\n
      });\n
    }\n
    gadget.notifyDataChanged();\n
  }\n
\n
\n
   function addEdge(gadget, edge_id, edge_data) {\n
     var overlays = [],\n
       connection;\n
     if (edge_data.name) {\n
       overlays = [\n
         ["Label", {\n
           cssClass: "l1 component label",\n
           label: edge_data.name\n
         }]\n
       ];\n
     }\n
     if (gadget.props.data.graph.node[edge_data.source] === undefined) {\n
       throw new Error("Error adding edge " +  edge_id + " Source " + edge_data.source + " does not exist");\n
     }\n
     if (gadget.props.data.graph.node[edge_data.destination] === undefined) {\n
       throw new Error("Edge adding edge " +  edge_id + " Destination " + edge_data.destination + " does not exist");\n
     }\n
     // If an edge has this data:\n
     // { _class: \'Edge\',\n
     //   source: \'N1\',\n
     //   destination: \'N2\',\n
     //   jsplumb_source_endpoint: \'BottomCenter\',\n
     //   jsplumb_destination_endpoint: \'LeftMiddle\',\n
     //   jsplumb_connector: \'Flowchart\' }\n
     // Then it is rendered using a flowchart connector. The difficulty is that\n
     // jsplumb does not let you configure the connector type on the edge, but\n
     // on the source endpoint. One solution seem to create all types of\n
     // endpoints on nodes.\n
     if (edge_data.jsplumb_connector === "Flowchart") {\n
       connection = gadget.props.jsplumb_instance.connect({\n
         uuids: [edge_data.source + ".flowChart" + edge_data.jsplumb_source_endpoint,\n
           edge_data.destination + ".flowChart" + edge_data.jsplumb_destination_endpoint\n
         ],\n
         overlays: overlays\n
       });\n
     } else {\n
       connection = gadget.props.jsplumb_instance.connect({\n
         source: gadget.props.node_id_to_dom_element_id[edge_data.source],\n
         target: gadget.props.node_id_to_dom_element_id[edge_data.destination],\n
         Connector: ["Bezier", {\n
           curviness: 75\n
         }],\n
         overlays: overlays\n
       });\n
     }\n
     // set data for \'connection\' event that will be called "later"\n
     gadget.props.data.graph.edge[edge_id] = edge_data;\n
     // jsplumb assigned an id, but we are controlling ids ourselves.\n
     connection.id = edge_id;\n
   }\n
\n
   function expandSchema(class_definition, full_schema) {\n
     // minimal expanding of json schema, supports merging allOf and $ref\n
     // references\n
     // XXX this should probably be moved to fieldset ( and not handle\n
     // class_definition here)\n
\n
     function resolveReference(ref, schema) {\n
       // 2 here is for #/\n
       var i, ref_path = ref.substr(2, ref.length),\n
         parts = ref_path.split("/");\n
       for (i = 0; i < parts.length; i += 1) {\n
         schema = schema[parts[i]];\n
       }\n
       return schema;\n
     }\n
\n
     function clone(obj) {\n
       return JSON.parse(JSON.stringify(obj));\n
     }\n
\n
     var referenced,\n
       i,\n
       property,\n
       expanded_class_definition = clone(class_definition) || {};\n
\n
\n
     if (!expanded_class_definition.properties) {\n
       expanded_class_definition.properties = {};\n
     }\n
     // expand direct ref\n
     if (class_definition.$ref) {\n
       referenced = expandSchema(resolveReference(class_definition.$ref, full_schema.class_definition), full_schema);\n
       $.extend(expanded_class_definition, referenced);\n
       delete expanded_class_definition.$ref;\n
     }\n
     // expand ref in properties\n
     for (property in class_definition.properties) {\n
       if (class_definition.properties.hasOwnProperty(property)) {\n
         if (class_definition.properties[property].$ref) {\n
           referenced = expandSchema(resolveReference(class_definition.properties[property].$ref, full_schema.class_definition), full_schema);\n
           $.extend(expanded_class_definition.properties[property], referenced);\n
           delete expanded_class_definition.properties[property].$ref;\n
         } else {\n
           if (class_definition.properties[property].type === "object") {\n
             // no reference, but we expand anyway because we need to recurse in case there is a ref in an object property\n
             referenced = expandSchema(class_definition.properties[property], full_schema);\n
             $.extend(expanded_class_definition.properties[property], referenced);\n
           }\n
         }\n
       }\n
     }\n
     if (class_definition.oneOf) {\n
       expanded_class_definition.oneOf = [];\n
       for (i = 0; i < class_definition.oneOf.length; i += 1) {\n
         expanded_class_definition.oneOf.push(expandSchema(class_definition.oneOf[i], full_schema));\n
       }\n
     }\n
     if (class_definition.allOf) {\n
       for (i = 0; i < class_definition.allOf.length; i += 1) {\n
         referenced = expandSchema(class_definition.allOf[i], full_schema);\n
         if (referenced.properties) {\n
           $.extend(expanded_class_definition.properties, referenced.properties);\n
           delete referenced.properties;\n
         }\n
         $.extend(expanded_class_definition, referenced);\n
       }\n
       if (expanded_class_definition.allOf) {\n
         delete expanded_class_definition.allOf;\n
       }\n
     }\n
     if (expanded_class_definition.$ref) {\n
       delete expanded_class_definition.$ref;\n
     }\n
     return clone(expanded_class_definition);\n
   }\n
\n
   function openEdgeEditionDialog(gadget, connection) {\n
     var edge_id = connection.id,\n
       edge_data = gadget.props.data.graph.edge[edge_id],\n
       edit_popup = $(gadget.props.element).find("#popup-edit-template"),\n
       schema,\n
       fieldset_element,\n
       delete_promise;\n
     schema = expandSchema(gadget.props.data.class_definition[edge_data._class], gadget.props.data);\n
     // We do not edit source & destination on edge this way.\n
     delete schema.properties.source;\n
     delete schema.properties.destination;\n
     gadget.props.element.insertAdjacentHTML("beforeend", popup_edit_template);\n
     edit_popup = $(gadget.props.element).find("#edit-popup");\n
     edit_popup.find(".node_class").text(connection.name || connection._class);\n
     fieldset_element = edit_popup.find("fieldset")[0];\n
     edit_popup.dialog();\n
     edit_popup.show();\n
\n
     function save_promise(fieldset_gadget, edge_id) {\n
       return RSVP.Queue().push(function() {\n
         return promiseEventListener(edit_popup.find(".graph_editor_validate_button")[0], "click", false);\n
       }).push(function(evt) {\n
         var data = {\n
           id: $(evt.target[1]).val(),\n
           data: {}\n
         };\n
         return fieldset_gadget.getContent().then(function(r) {\n
           $.extend(data.data, gadget.props.data.graph.edge[connection.id]);\n
           $.extend(data.data, r);\n
           // to redraw, we remove the edge and add again.\n
           // but we want to disable events on connection, since event\n
           // handling promise are executed asynchronously in undefined order,\n
           // we cannot just remove and /then/ add, because the new edge is\n
           // added before the old is removed.\n
           connection.ignoreEvent = true;\n
           gadget.props.jsplumb_instance.detach(connection);\n
           addEdge(gadget, r.id, data.data);\n
         });\n
       });\n
     }\n
     delete_promise = new RSVP.Queue().push(function() {\n
       return promiseEventListener(edit_popup.find(".graph_editor_delete_button")[0], "click", false);\n
     }).push(function() {\n
       // connectionDetached event will remove the edge from data\n
       gadget.props.jsplumb_instance.detach(connection);\n
     });\n
     return gadget.declareGadget("../fieldset/index.html", {\n
       element: fieldset_element,\n
       scope: "fieldset"\n
     }).push(function(fieldset_gadget) {\n
       return RSVP.all([fieldset_gadget, fieldset_gadget.render({\n
         value: edge_data,\n
         property_definition: schema\n
       }, edge_id)]);\n
     }).push(function(fieldset_gadget) {\n
       edit_popup.dialog("open");\n
       return fieldset_gadget[0];\n
     }).push(function(fieldset_gadget) {\n
       fieldset_gadget.startService(); // XXX\n
       return fieldset_gadget;\n
     }).push(function(fieldset_gadget) {\n
       // Expose the dialog handling promise so that we can wait for it in\n
       // test.\n
       gadget.props.dialog_promise = RSVP.any([save_promise(fieldset_gadget, edge_id), delete_promise]);\n
       return gadget.props.dialog_promise;\n
     }).push(function() {\n
       edit_popup.dialog("close");\n
       edit_popup.remove();\n
       delete gadget.props.dialog_promise;\n
     });\n
   }\n
\n
   function openNodeEditionDialog(gadget, element) {\n
     var node_id = getNodeId(gadget, element.id),\n
       node_data = gadget.props.data.graph.node[node_id],\n
       node_edit_popup = $(gadget.props.element).find("#popup-edit-template"),\n
       schema,\n
       fieldset_element,\n
       delete_promise;\n
     // If we have no definition for this, we do not allow edition.\n
     // XXX incorrect, we need to display this dialog to be able\n
     // to delete a node\n
     if (gadget.props.data.class_definition[node_data._class] === undefined) {\n
       return;\n
     }\n
     schema = expandSchema(gadget.props.data.class_definition[node_data._class], gadget.props.data);\n
     if (node_edit_popup.length !== 0) {\n
       node_edit_popup.remove();\n
     }\n
     gadget.props.element.insertAdjacentHTML("beforeend", popup_edit_template);\n
     node_edit_popup = $(gadget.props.element).find("#edit-popup");\n
     // Set the name of the popup to the node class\n
     node_edit_popup.find(".node_class").text(node_data.name || node_data._class);\n
     fieldset_element = node_edit_popup.find("fieldset")[0];\n
     node_edit_popup.dialog();\n
     node_data.id = node_id;\n
\n
     function save_promise(fieldset_gadget, node_id) {\n
       return RSVP.Queue().push(function() {\n
         return promiseEventListener(node_edit_popup.find(".graph_editor_validate_button")[0], "click", false);\n
       }).push(function(evt) {\n
         var data = {\n
           // XXX id should not be handled differently ...\n
           id: $(evt.target[1]).val(),\n
           data: {}\n
         };\n
         return fieldset_gadget.getContent().then(function(r) {\n
           $.extend(data.data, r);\n
           updateElementData(gadget, node_id, data);\n
         });\n
       });\n
     }\n
     delete_promise = new RSVP.Queue().push(function() {\n
       return promiseEventListener(node_edit_popup.find(".graph_editor_delete_button")[0], "click", false);\n
     }).push(function() {\n
       return removeElement(gadget, node_id);\n
     });\n
     return gadget.declareGadget("../fieldset/index.html", {\n
       element: fieldset_element,\n
       scope: "fieldset"\n
     }).push(function(fieldset_gadget) {\n
       return RSVP.all([fieldset_gadget, fieldset_gadget.render({\n
         value: node_data,\n
         property_definition: schema\n
       }, node_id)]);\n
     }).push(function(fieldset_gadget) {\n
       node_edit_popup.dialog("open");\n
       return fieldset_gadget[0];\n
     }).push(function(fieldset_gadget) {\n
       fieldset_gadget.startService(); // XXX this should not be needed anymore.\n
       return fieldset_gadget;\n
     }).push(function(fieldset_gadget) {\n
       // Expose the dialog handling promise so that we can wait for it in\n
       // test.\n
       gadget.props.dialog_promise = RSVP.any([save_promise(fieldset_gadget, node_id), delete_promise]);\n
       return gadget.props.dialog_promise;\n
     }).push(function() {\n
       node_edit_popup.dialog("close");\n
       node_edit_popup.remove();\n
       delete gadget.props.dialog_promise;\n
     });\n
   }\n
\n
   function waitForNodeClick(gadget, node) {\n
     gadget.props.nodes_click_monitor.monitor(loopEventListener(node, "dblclick", false, openNodeEditionDialog.bind(null, gadget, node)));\n
   }\n
\n
   function waitForConnection(gadget) {\n
     return loopJsplumbBind(gadget, "connection", function(info, originalEvent) {\n
       updateConnectionData(gadget, info.connection, false);\n
     });\n
   }\n
\n
   function waitForConnectionDetached(gadget) {\n
     return loopJsplumbBind(gadget, "connectionDetached", function(info, originalEvent) {\n
       updateConnectionData(gadget, info.connection, true);\n
     });\n
   }\n
\n
   function waitForConnectionClick(gadget) {\n
     return loopJsplumbBind(gadget, "click", function(connection) {\n
       return openEdgeEditionDialog(gadget, connection);\n
     });\n
   }\n
\n
   function addNode(gadget, node_id, node_data) {\n
     var render_element = $(gadget.props.main),\n
       class_definition = gadget.props.data.class_definition[node_data._class],\n
       coordinate = node_data.coordinate,\n
       dom_element_id,\n
       box,\n
       absolute_position,\n
       domElement;\n
\n
     dom_element_id = generateDomElementId(gadget.props.element);\n
     gadget.props.node_id_to_dom_element_id[node_id] = dom_element_id;\n
     node_data.name = node_data.name || class_definition.name;\n
     gadget.props.data.graph.node[node_id] = node_data;\n
     if (coordinate === undefined) {\n
       coordinate = {\n
         top: 0,\n
         left: 0\n
       };\n
     }\n
     node_data.coordinate = updateElementCoordinate(gadget, node_id, coordinate);\n
     /*jslint nomen: true*/\n
     domElement = domParser.parseFromString(node_template({\n
       "class": node_data._class.replace(".", "-"),\n
       element_id: dom_element_id,\n
       title: node_data.name || node_data.id,\n
       name: node_data.name || node_data.id\n
     }), "text/html").querySelector(".window");\n
     render_element.append(domElement);\n
     waitForNodeClick(gadget, domElement);\n
     box = $(gadget.props.element).find("#" + dom_element_id);\n
     absolute_position = convertToAbsolutePosition(gadget, coordinate.left, coordinate.top);\n
     if (class_definition && class_definition.css) {\n
       box.css(class_definition.css);\n
     }\n
     box.css("top", absolute_position[1]);\n
     box.css("left", absolute_position[0]);\n
     updateNodeStyle(gadget, dom_element_id);\n
     draggable(gadget);\n
     // XXX make only this element draggable.\n
     // Add some flowchart endpoints\n
     // TODO: add them all !\n
     gadget.props.jsplumb_instance.addEndpoint(dom_element_id, {\n
       isSource: true,\n
       maxConnections: -1,\n
       connector: ["Flowchart", {\n
         stub: [40, 60],\n
         gap: 10,\n
         cornerRadius: 5,\n
         alwaysRespectStubs: true\n
       }]\n
     }, {\n
       anchor: "BottomCenter",\n
       uuid: node_id + ".flowchartBottomCenter"\n
     });\n
     gadget.props.jsplumb_instance.addEndpoint(dom_element_id, {\n
       isTarget: true,\n
       maxConnections: -1\n
     }, {\n
       anchor: "LeftMiddle",\n
       uuid: node_id + ".flowChartLeftMiddle"\n
     });\n
     gadget.notifyDataChanged();\n
   }\n
\n
   function waitForDrop(gadget) {\n
     var callback;\n
\n
     function canceller() {\n
         if (callback !== undefined) {\n
           gadget.props.main.removeEventListener("drop", callback, false);\n
         }\n
       }\n
       /*jslint unparam: true*/\n
     function resolver(resolve, reject) {\n
       callback = function(evt) {\n
         try {\n
           var class_name, offset = $(gadget.props.main).offset(),\n
             relative_position = convertToRelativePosition(gadget, evt.clientX - offset.left + "px", evt.clientY - offset.top + "px");\n
           try {\n
             // html5 compliant browser\n
             class_name = JSON.parse(evt.dataTransfer.getData("application/json"));\n
           } catch (e) {\n
             // internet explorer\n
             class_name = JSON.parse(evt.dataTransfer.getData("text"));\n
           }\n
           addNode(gadget, generateNodeId(gadget, {\n
             _class: class_name\n
           }), {\n
             coordinate: {\n
               left: relative_position[0],\n
               top: relative_position[1]\n
             },\n
             _class: class_name\n
           });\n
         } catch (e) {\n
           reject(e);\n
         }\n
       };\n
       gadget.props.main.addEventListener("drop", callback, false);\n
     }\n
     return new RSVP.all([ // loopEventListener adds an event listener that will prevent default for\n
       // dragover\n
       loopEventListener(gadget.props.main, "dragover", false, function() {\n
         return undefined;\n
       }), RSVP.Promise(resolver, canceller)\n
     ]);\n
   }\n
\n
   gadget_klass.ready(function (g) {\n
      g.props = {};\n
    })\n
    .ready(function (g) {\n
      return g.getElement().push(function (element) {\n
        g.props.element = element;\n
      });\n
    })\n
   .ready(function(g) {\n
     g.props.node_id_to_dom_element_id = {};\n
     g.props.zoom_level = 1;\n
     g.props.style_attr_list = ["width", "height", "padding-top", "line-height"];\n
     g.getElement().then(function(element) {\n
       g.props.element = element;\n
     });\n
   })\n
   .declareAcquiredMethod("notifyDataChanged", "notifyDataChanged")\n
   .declareMethod("render", function(data) {\n
     var gadget = this, jsplumb_instance;\n
\n
     this.props.data = {};\n
     if (data.key) {\n
       // Gadget embedded in ERP5\n
       this.props.erp5_key = data.key;\n
       data = data.value;\n
     }\n
\n
     this.props.main = this.props.element.querySelector(".graph_container");\n
/*\n
     $(this.props.main).resizable({\n
        resize : function(event, ui) {\n
          jsplumb_instance.repaint(ui.helper);\n
       }\n
     });\n
*/\n
     if (data) {\n
       this.props.data = JSON.parse(data);\n
\n
// XXX how to make queue ??\n
       return layoutGraph(this.props.data.graph).then(function(graph_data) {\n
         gadget.props.data.graph = graph_data;\n
         // load the data\n
         $.each(gadget.props.data.graph.node, function(key, value) {\n
           addNode(gadget, key, value);\n
         });\n
         $.each(gadget.props.data.graph.edge, function(key, value) {\n
           addEdge(gadget, key, value);\n
         });\n
       });\n
     }\n
   })\n
   .declareMethod("getContent", function() {\n
     var ret = {};\n
     if (this.props.erp5_key) {\n
       // ERP5\n
       ret[this.props.erp5_key] = JSON.stringify(this.props.data);\n
       return ret;\n
     }\n
     return JSON.stringify(this.props.data);\n
   })\n
   .declareService(function() {\n
     var gadget = this, jsplumb_instance;\n
     this.props.main = this.props.element.querySelector(".graph_container");\n
     this.props.jsplumb_instance = jsplumb_instance = jsPlumb.getInstance();\n
     if (this.props.data) {\n
       // load the data\n
       $.each(this.props.data.graph.node, function(key, value) {\n
         addNode(gadget, key, value);\n
       });\n
       $.each(this.props.data.graph.edge, function(key, value) {\n
         addEdge(gadget, key, value);\n
       });\n
     }\n
     jsplumb_instance.setRenderMode(jsplumb_instance.SVG);\n
     jsplumb_instance.importDefaults({\n
       HoverPaintStyle: {\n
         strokeStyle: "#1e8151",\n
         lineWidth: 2\n
       },\n
       Endpoint: ["Dot", {\n
         radius: 2\n
       }],\n
       ConnectionOverlays: [\n
         ["Arrow", {\n
           location: 1,\n
           id: "arrow",\n
           length: 14,\n
           foldback: 0.8\n
         }]\n
       ],\n
       Container: this.props.main\n
     });\n
     draggable(gadget);\n
     \n
     this.props.nodes_click_monitor = RSVP.Monitor();\n
     return RSVP.all([waitForDrop(gadget),\n
       waitForConnection(gadget),\n
       waitForConnectionDetached(gadget),\n
       waitForConnectionClick(gadget),\n
       gadget.props.nodes_click_monitor\n
     ]);\n
   });\n
\n
 })(RSVP, rJS, $, jsPlumb, Handlebars, loopEventListener, promiseEventListener, DOMParser, Springy);

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>31544</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
