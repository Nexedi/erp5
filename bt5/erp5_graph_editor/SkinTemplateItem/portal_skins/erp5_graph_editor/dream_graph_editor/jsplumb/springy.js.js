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
            <value> <string>ts46849116.54</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>springy.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/**\n
 * Springy v2.7.1\n
 *\n
 * Copyright (c) 2010-2013 Dennis Hotson\n
 *\n
 * Permission is hereby granted, free of charge, to any person\n
 * obtaining a copy of this software and associated documentation\n
 * files (the "Software"), to deal in the Software without\n
 * restriction, including without limitation the rights to use,\n
 * copy, modify, merge, publish, distribute, sublicense, and/or sell\n
 * copies of the Software, and to permit persons to whom the\n
 * Software is furnished to do so, subject to the following\n
 * conditions:\n
 *\n
 * The above copyright notice and this permission notice shall be\n
 * included in all copies or substantial portions of the Software.\n
 *\n
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,\n
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES\n
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND\n
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT\n
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,\n
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING\n
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR\n
 * OTHER DEALINGS IN THE SOFTWARE.\n
 */\n
(function (root, factory) {\n
    if (typeof define === \'function\' && define.amd) {\n
        // AMD. Register as an anonymous module.\n
        define(function () {\n
            return (root.returnExportsGlobal = factory());\n
        });\n
    } else if (typeof exports === \'object\') {\n
        // Node. Does not work with strict CommonJS, but\n
        // only CommonJS-like enviroments that support module.exports,\n
        // like Node.\n
        module.exports = factory();\n
    } else {\n
        // Browser globals\n
        root.Springy = factory();\n
    }\n
}(this, function() {\n
\n
\tvar Springy = {};\n
\n
\tvar Graph = Springy.Graph = function() {\n
\t\tthis.nodeSet = {};\n
\t\tthis.nodes = [];\n
\t\tthis.edges = [];\n
\t\tthis.adjacency = {};\n
\n
\t\tthis.nextNodeId = 0;\n
\t\tthis.nextEdgeId = 0;\n
\t\tthis.eventListeners = [];\n
\t};\n
\n
\tvar Node = Springy.Node = function(id, data) {\n
\t\tthis.id = id;\n
\t\tthis.data = (data !== undefined) ? data : {};\n
\n
\t// Data fields used by layout algorithm in this file:\n
\t// this.data.mass\n
\t// Data used by default renderer in springyui.js\n
\t// this.data.label\n
\t};\n
\n
\tvar Edge = Springy.Edge = function(id, source, target, data) {\n
\t\tthis.id = id;\n
\t\tthis.source = source;\n
\t\tthis.target = target;\n
\t\tthis.data = (data !== undefined) ? data : {};\n
\n
\t// Edge data field used by layout alorithm\n
\t// this.data.length\n
\t// this.data.type\n
\t};\n
\n
\tGraph.prototype.addNode = function(node) {\n
\t\tif (!(node.id in this.nodeSet)) {\n
\t\t\tthis.nodes.push(node);\n
\t\t}\n
\n
\t\tthis.nodeSet[node.id] = node;\n
\n
\t\tthis.notify();\n
\t\treturn node;\n
\t};\n
\n
\tGraph.prototype.addNodes = function() {\n
\t\t// accepts variable number of arguments, where each argument\n
\t\t// is a string that becomes both node identifier and label\n
\t\tfor (var i = 0; i < arguments.length; i++) {\n
\t\t\tvar name = arguments[i];\n
\t\t\tvar node = new Node(name, {label:name});\n
\t\t\tthis.addNode(node);\n
\t\t}\n
\t};\n
\n
\tGraph.prototype.addEdge = function(edge) {\n
\t\tvar exists = false;\n
\t\tthis.edges.forEach(function(e) {\n
\t\t\tif (edge.id === e.id) { exists = true; }\n
\t\t});\n
\n
\t\tif (!exists) {\n
\t\t\tthis.edges.push(edge);\n
\t\t}\n
\n
\t\tif (!(edge.source.id in this.adjacency)) {\n
\t\t\tthis.adjacency[edge.source.id] = {};\n
\t\t}\n
\t\tif (!(edge.target.id in this.adjacency[edge.source.id])) {\n
\t\t\tthis.adjacency[edge.source.id][edge.target.id] = [];\n
\t\t}\n
\n
\t\texists = false;\n
\t\tthis.adjacency[edge.source.id][edge.target.id].forEach(function(e) {\n
\t\t\t\tif (edge.id === e.id) { exists = true; }\n
\t\t});\n
\n
\t\tif (!exists) {\n
\t\t\tthis.adjacency[edge.source.id][edge.target.id].push(edge);\n
\t\t}\n
\n
\t\tthis.notify();\n
\t\treturn edge;\n
\t};\n
\n
\tGraph.prototype.addEdges = function() {\n
\t\t// accepts variable number of arguments, where each argument\n
\t\t// is a triple [nodeid1, nodeid2, attributes]\n
\t\tfor (var i = 0; i < arguments.length; i++) {\n
\t\t\tvar e = arguments[i];\n
\t\t\tvar node1 = this.nodeSet[e[0]];\n
\t\t\tif (node1 == undefined) {\n
\t\t\t\tthrow new TypeError("invalid node name: " + e[0]);\n
\t\t\t}\n
\t\t\tvar node2 = this.nodeSet[e[1]];\n
\t\t\tif (node2 == undefined) {\n
\t\t\t\tthrow new TypeError("invalid node name: " + e[1]);\n
\t\t\t}\n
\t\t\tvar attr = e[2];\n
\n
\t\t\tthis.newEdge(node1, node2, attr);\n
\t\t}\n
\t};\n
\n
\tGraph.prototype.newNode = function(data) {\n
\t\tvar node = new Node(this.nextNodeId++, data);\n
\t\tthis.addNode(node);\n
\t\treturn node;\n
\t};\n
\n
\tGraph.prototype.newEdge = function(source, target, data) {\n
\t\tvar edge = new Edge(this.nextEdgeId++, source, target, data);\n
\t\tthis.addEdge(edge);\n
\t\treturn edge;\n
\t};\n
\n
\n
\t// add nodes and edges from JSON object\n
\tGraph.prototype.loadJSON = function(json) {\n
\t/**\n
\tSpringy\'s simple JSON format for graphs.\n
\n
\thistorically, Springy uses separate lists\n
\tof nodes and edges:\n
\n
\t\t{\n
\t\t\t"nodes": [\n
\t\t\t\t"center",\n
\t\t\t\t"left",\n
\t\t\t\t"right",\n
\t\t\t\t"up",\n
\t\t\t\t"satellite"\n
\t\t\t],\n
\t\t\t"edges": [\n
\t\t\t\t["center", "left"],\n
\t\t\t\t["center", "right"],\n
\t\t\t\t["center", "up"]\n
\t\t\t]\n
\t\t}\n
\n
\t**/\n
\t\t// parse if a string is passed (EC5+ browsers)\n
\t\tif (typeof json == \'string\' || json instanceof String) {\n
\t\t\tjson = JSON.parse( json );\n
\t\t}\n
\n
\t\tif (\'nodes\' in json || \'edges\' in json) {\n
\t\t\tthis.addNodes.apply(this, json[\'nodes\']);\n
\t\t\tthis.addEdges.apply(this, json[\'edges\']);\n
\t\t}\n
\t}\n
\n
\n
\t// find the edges from node1 to node2\n
\tGraph.prototype.getEdges = function(node1, node2) {\n
\t\tif (node1.id in this.adjacency\n
\t\t\t&& node2.id in this.adjacency[node1.id]) {\n
\t\t\treturn this.adjacency[node1.id][node2.id];\n
\t\t}\n
\n
\t\treturn [];\n
\t};\n
\n
\t// remove a node and it\'s associated edges from the graph\n
\tGraph.prototype.removeNode = function(node) {\n
\t\tif (node.id in this.nodeSet) {\n
\t\t\tdelete this.nodeSet[node.id];\n
\t\t}\n
\n
\t\tfor (var i = this.nodes.length - 1; i >= 0; i--) {\n
\t\t\tif (this.nodes[i].id === node.id) {\n
\t\t\t\tthis.nodes.splice(i, 1);\n
\t\t\t}\n
\t\t}\n
\n
\t\tthis.detachNode(node);\n
\t};\n
\n
\t// removes edges associated with a given node\n
\tGraph.prototype.detachNode = function(node) {\n
\t\tvar tmpEdges = this.edges.slice();\n
\t\ttmpEdges.forEach(function(e) {\n
\t\t\tif (e.source.id === node.id || e.target.id === node.id) {\n
\t\t\t\tthis.removeEdge(e);\n
\t\t\t}\n
\t\t}, this);\n
\n
\t\tthis.notify();\n
\t};\n
\n
\t// remove a node and it\'s associated edges from the graph\n
\tGraph.prototype.removeEdge = function(edge) {\n
\t\tfor (var i = this.edges.length - 1; i >= 0; i--) {\n
\t\t\tif (this.edges[i].id === edge.id) {\n
\t\t\t\tthis.edges.splice(i, 1);\n
\t\t\t}\n
\t\t}\n
\n
\t\tfor (var x in this.adjacency) {\n
\t\t\tfor (var y in this.adjacency[x]) {\n
\t\t\t\tvar edges = this.adjacency[x][y];\n
\n
\t\t\t\tfor (var j=edges.length - 1; j>=0; j--) {\n
\t\t\t\t\tif (this.adjacency[x][y][j].id === edge.id) {\n
\t\t\t\t\t\tthis.adjacency[x][y].splice(j, 1);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\t// Clean up empty edge arrays\n
\t\t\t\tif (this.adjacency[x][y].length == 0) {\n
\t\t\t\t\tdelete this.adjacency[x][y];\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t// Clean up empty objects\n
\t\t\tif (isEmpty(this.adjacency[x])) {\n
\t\t\t\tdelete this.adjacency[x];\n
\t\t\t}\n
\t\t}\n
\n
\t\tthis.notify();\n
\t};\n
\n
\t/* Merge a list of nodes and edges into the current graph. eg.\n
\tvar o = {\n
\t\tnodes: [\n
\t\t\t{id: 123, data: {type: \'user\', userid: 123, displayname: \'aaa\'}},\n
\t\t\t{id: 234, data: {type: \'user\', userid: 234, displayname: \'bbb\'}}\n
\t\t],\n
\t\tedges: [\n
\t\t\t{from: 0, to: 1, type: \'submitted_design\', directed: true, data: {weight: }}\n
\t\t]\n
\t}\n
\t*/\n
\tGraph.prototype.merge = function(data) {\n
\t\tvar nodes = [];\n
\t\tdata.nodes.forEach(function(n) {\n
\t\t\tnodes.push(this.addNode(new Node(n.id, n.data)));\n
\t\t}, this);\n
\n
\t\tdata.edges.forEach(function(e) {\n
\t\t\tvar from = nodes[e.from];\n
\t\t\tvar to = nodes[e.to];\n
\n
\t\t\tvar id = (e.directed)\n
\t\t\t\t? (id = e.type + "-" + from.id + "-" + to.id)\n
\t\t\t\t: (from.id < to.id) // normalise id for non-directed edges\n
\t\t\t\t\t? e.type + "-" + from.id + "-" + to.id\n
\t\t\t\t\t: e.type + "-" + to.id + "-" + from.id;\n
\n
\t\t\tvar edge = this.addEdge(new Edge(id, from, to, e.data));\n
\t\t\tedge.data.type = e.type;\n
\t\t}, this);\n
\t};\n
\n
\tGraph.prototype.filterNodes = function(fn) {\n
\t\tvar tmpNodes = this.nodes.slice();\n
\t\ttmpNodes.forEach(function(n) {\n
\t\t\tif (!fn(n)) {\n
\t\t\t\tthis.removeNode(n);\n
\t\t\t}\n
\t\t}, this);\n
\t};\n
\n
\tGraph.prototype.filterEdges = function(fn) {\n
\t\tvar tmpEdges = this.edges.slice();\n
\t\ttmpEdges.forEach(function(e) {\n
\t\t\tif (!fn(e)) {\n
\t\t\t\tthis.removeEdge(e);\n
\t\t\t}\n
\t\t}, this);\n
\t};\n
\n
\n
\tGraph.prototype.addGraphListener = function(obj) {\n
\t\tthis.eventListeners.push(obj);\n
\t};\n
\n
\tGraph.prototype.notify = function() {\n
\t\tthis.eventListeners.forEach(function(obj){\n
\t\t\tobj.graphChanged();\n
\t\t});\n
\t};\n
\n
\t// -----------\n
\tvar Layout = Springy.Layout = {};\n
\tLayout.ForceDirected = function(graph, stiffness, repulsion, damping, minEnergyThreshold) {\n
\t\tthis.graph = graph;\n
\t\tthis.stiffness = stiffness; // spring stiffness constant\n
\t\tthis.repulsion = repulsion; // repulsion constant\n
\t\tthis.damping = damping; // velocity damping factor\n
\t\tthis.minEnergyThreshold = minEnergyThreshold || 0.01; //threshold used to determine render stop\n
\n
\t\tthis.nodePoints = {}; // keep track of points associated with nodes\n
\t\tthis.edgeSprings = {}; // keep track of springs associated with edges\n
\t};\n
\n
\tLayout.ForceDirected.prototype.point = function(node) {\n
\t\tif (!(node.id in this.nodePoints)) {\n
\t\t\tvar mass = (node.data.mass !== undefined) ? node.data.mass : 1.0;\n
\t\t\tthis.nodePoints[node.id] = new Layout.ForceDirected.Point(Vector.random(), mass);\n
\t\t}\n
\n
\t\treturn this.nodePoints[node.id];\n
\t};\n
\n
\tLayout.ForceDirected.prototype.spring = function(edge) {\n
\t\tif (!(edge.id in this.edgeSprings)) {\n
\t\t\tvar length = (edge.data.length !== undefined) ? edge.data.length : 1.0;\n
\n
\t\t\tvar existingSpring = false;\n
\n
\t\t\tvar from = this.graph.getEdges(edge.source, edge.target);\n
\t\t\tfrom.forEach(function(e) {\n
\t\t\t\tif (existingSpring === false && e.id in this.edgeSprings) {\n
\t\t\t\t\texistingSpring = this.edgeSprings[e.id];\n
\t\t\t\t}\n
\t\t\t}, this);\n
\n
\t\t\tif (existingSpring !== false) {\n
\t\t\t\treturn new Layout.ForceDirected.Spring(existingSpring.point1, existingSpring.point2, 0.0, 0.0);\n
\t\t\t}\n
\n
\t\t\tvar to = this.graph.getEdges(edge.target, edge.source);\n
\t\t\tfrom.forEach(function(e){\n
\t\t\t\tif (existingSpring === false && e.id in this.edgeSprings) {\n
\t\t\t\t\texistingSpring = this.edgeSprings[e.id];\n
\t\t\t\t}\n
\t\t\t}, this);\n
\n
\t\t\tif (existingSpring !== false) {\n
\t\t\t\treturn new Layout.ForceDirected.Spring(existingSpring.point2, existingSpring.point1, 0.0, 0.0);\n
\t\t\t}\n
\n
\t\t\tthis.edgeSprings[edge.id] = new Layout.ForceDirected.Spring(\n
\t\t\t\tthis.point(edge.source), this.point(edge.target), length, this.stiffness\n
\t\t\t);\n
\t\t}\n
\n
\t\treturn this.edgeSprings[edge.id];\n
\t};\n
\n
\t// callback should accept two arguments: Node, Point\n
\tLayout.ForceDirected.prototype.eachNode = function(callback) {\n
\t\tvar t = this;\n
\t\tthis.graph.nodes.forEach(function(n){\n
\t\t\tcallback.call(t, n, t.point(n));\n
\t\t});\n
\t};\n
\n
\t// callback should accept two arguments: Edge, Spring\n
\tLayout.ForceDirected.prototype.eachEdge = function(callback) {\n
\t\tvar t = this;\n
\t\tthis.graph.edges.forEach(function(e){\n
\t\t\tcallback.call(t, e, t.spring(e));\n
\t\t});\n
\t};\n
\n
\t// callback should accept one argument: Spring\n
\tLayout.ForceDirected.prototype.eachSpring = function(callback) {\n
\t\tvar t = this;\n
\t\tthis.graph.edges.forEach(function(e){\n
\t\t\tcallback.call(t, t.spring(e));\n
\t\t});\n
\t};\n
\n
\n
\t// Physics stuff\n
\tLayout.ForceDirected.prototype.applyCoulombsLaw = function() {\n
\t\tthis.eachNode(function(n1, point1) {\n
\t\t\tthis.eachNode(function(n2, point2) {\n
\t\t\t\tif (point1 !== point2)\n
\t\t\t\t{\n
\t\t\t\t\tvar d = point1.p.subtract(point2.p);\n
\t\t\t\t\tvar distance = d.magnitude() + 0.1; // avoid massive forces at small distances (and divide by zero)\n
\t\t\t\t\tvar direction = d.normalise();\n
\n
\t\t\t\t\t// apply force to each end point\n
\t\t\t\t\tpoint1.applyForce(direction.multiply(this.repulsion).divide(distance * distance * 0.5));\n
\t\t\t\t\tpoint2.applyForce(direction.multiply(this.repulsion).divide(distance * distance * -0.5));\n
\t\t\t\t}\n
\t\t\t});\n
\t\t});\n
\t};\n
\n
\tLayout.ForceDirected.prototype.applyHookesLaw = function() {\n
\t\tthis.eachSpring(function(spring){\n
\t\t\tvar d = spring.point2.p.subtract(spring.point1.p); // the direction of the spring\n
\t\t\tvar displacement = spring.length - d.magnitude();\n
\t\t\tvar direction = d.normalise();\n
\n
\t\t\t// apply force to each end point\n
\t\t\tspring.point1.applyForce(direction.multiply(spring.k * displacement * -0.5));\n
\t\t\tspring.point2.applyForce(direction.multiply(spring.k * displacement * 0.5));\n
\t\t});\n
\t};\n
\n
\tLayout.ForceDirected.prototype.attractToCentre = function() {\n
\t\tthis.eachNode(function(node, point) {\n
\t\t\tvar direction = point.p.multiply(-1.0);\n
\t\t\tpoint.applyForce(direction.multiply(this.repulsion / 50.0));\n
\t\t});\n
\t};\n
\n
\n
\tLayout.ForceDirected.prototype.updateVelocity = function(timestep) {\n
\t\tthis.eachNode(function(node, point) {\n
\t\t\t// Is this, along with updatePosition below, the only places that your\n
\t\t\t// integration code exist?\n
\t\t\tpoint.v = point.v.add(point.a.multiply(timestep)).multiply(this.damping);\n
\t\t\tpoint.a = new Vector(0,0);\n
\t\t});\n
\t};\n
\n
\tLayout.ForceDirected.prototype.updatePosition = function(timestep) {\n
\t\tthis.eachNode(function(node, point) {\n
\t\t\t// Same question as above; along with updateVelocity, is this all of\n
\t\t\t// your integration code?\n
\t\t\tpoint.p = point.p.add(point.v.multiply(timestep));\n
\t\t});\n
\t};\n
\n
\t// Calculate the total kinetic energy of the system\n
\tLayout.ForceDirected.prototype.totalEnergy = function(timestep) {\n
\t\tvar energy = 0.0;\n
\t\tthis.eachNode(function(node, point) {\n
\t\t\tvar speed = point.v.magnitude();\n
\t\t\tenergy += 0.5 * point.m * speed * speed;\n
\t\t});\n
\n
\t\treturn energy;\n
\t};\n
\n
\tvar __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }; // stolen from coffeescript, thanks jashkenas! ;-)\n
\n
\tSpringy.requestAnimationFrame = __bind(this.requestAnimationFrame ||\n
\t\tthis.webkitRequestAnimationFrame ||\n
\t\tthis.mozRequestAnimationFrame ||\n
\t\tthis.oRequestAnimationFrame ||\n
\t\tthis.msRequestAnimationFrame ||\n
\t\t(function(callback, element) {\n
\t\t\tthis.setTimeout(callback, 10);\n
\t\t}), this);\n
\n
\n
\t/**\n
\t * Start simulation if it\'s not running already.\n
\t * In case it\'s running then the call is ignored, and none of the callbacks passed is ever executed.\n
\t */\n
\tLayout.ForceDirected.prototype.start = function(render, onRenderStop, onRenderStart) {\n
\t\tvar t = this;\n
\n
\t\tif (this._started) return;\n
\t\tthis._started = true;\n
\t\tthis._stop = false;\n
\n
\t\tif (onRenderStart !== undefined) { onRenderStart(); }\n
\n
\t\tSpringy.requestAnimationFrame(function step() {\n
\t\t\tt.tick(0.03);\n
\n
\t\t\tif (render !== undefined) {\n
\t\t\t\trender();\n
\t\t\t}\n
\n
\t\t\t// stop simulation when energy of the system goes below a threshold\n
\t\t\tif (t._stop || t.totalEnergy() < t.minEnergyThreshold) {\n
\t\t\t\tt._started = false;\n
\t\t\t\tif (onRenderStop !== undefined) { onRenderStop(); }\n
\t\t\t} else {\n
\t\t\t\tSpringy.requestAnimationFrame(step);\n
\t\t\t}\n
\t\t});\n
\t};\n
\n
\tLayout.ForceDirected.prototype.stop = function() {\n
\t\tthis._stop = true;\n
\t}\n
\n
\tLayout.ForceDirected.prototype.tick = function(timestep) {\n
\t\tthis.applyCoulombsLaw();\n
\t\tthis.applyHookesLaw();\n
\t\tthis.attractToCentre();\n
\t\tthis.updateVelocity(timestep);\n
\t\tthis.updatePosition(timestep);\n
\t};\n
\n
\t// Find the nearest point to a particular position\n
\tLayout.ForceDirected.prototype.nearest = function(pos) {\n
\t\tvar min = {node: null, point: null, distance: null};\n
\t\tvar t = this;\n
\t\tthis.graph.nodes.forEach(function(n){\n
\t\t\tvar point = t.point(n);\n
\t\t\tvar distance = point.p.subtract(pos).magnitude();\n
\n
\t\t\tif (min.distance === null || distance < min.distance) {\n
\t\t\t\tmin = {node: n, point: point, distance: distance};\n
\t\t\t}\n
\t\t});\n
\n
\t\treturn min;\n
\t};\n
\n
\t// returns [bottomleft, topright]\n
\tLayout.ForceDirected.prototype.getBoundingBox = function() {\n
\t\tvar bottomleft = new Vector(-2,-2);\n
\t\tvar topright = new Vector(2,2);\n
\n
\t\tthis.eachNode(function(n, point) {\n
\t\t\tif (point.p.x < bottomleft.x) {\n
\t\t\t\tbottomleft.x = point.p.x;\n
\t\t\t}\n
\t\t\tif (point.p.y < bottomleft.y) {\n
\t\t\t\tbottomleft.y = point.p.y;\n
\t\t\t}\n
\t\t\tif (point.p.x > topright.x) {\n
\t\t\t\ttopright.x = point.p.x;\n
\t\t\t}\n
\t\t\tif (point.p.y > topright.y) {\n
\t\t\t\ttopright.y = point.p.y;\n
\t\t\t}\n
\t\t});\n
\n
\t\tvar padding = topright.subtract(bottomleft).multiply(0.07); // ~5% padding\n
\n
\t\treturn {bottomleft: bottomleft.subtract(padding), topright: topright.add(padding)};\n
\t};\n
\n
\n
\t// Vector\n
\tvar Vector = Springy.Vector = function(x, y) {\n
\t\tthis.x = x;\n
\t\tthis.y = y;\n
\t};\n
\n
\tVector.random = function() {\n
\t\treturn new Vector(10.0 * (Math.random() - 0.5), 10.0 * (Math.random() - 0.5));\n
\t};\n
\n
\tVector.prototype.add = function(v2) {\n
\t\treturn new Vector(this.x + v2.x, this.y + v2.y);\n
\t};\n
\n
\tVector.prototype.subtract = function(v2) {\n
\t\treturn new Vector(this.x - v2.x, this.y - v2.y);\n
\t};\n
\n
\tVector.prototype.multiply = function(n) {\n
\t\treturn new Vector(this.x * n, this.y * n);\n
\t};\n
\n
\tVector.prototype.divide = function(n) {\n
\t\treturn new Vector((this.x / n) || 0, (this.y / n) || 0); // Avoid divide by zero errors..\n
\t};\n
\n
\tVector.prototype.magnitude = function() {\n
\t\treturn Math.sqrt(this.x*this.x + this.y*this.y);\n
\t};\n
\n
\tVector.prototype.normal = function() {\n
\t\treturn new Vector(-this.y, this.x);\n
\t};\n
\n
\tVector.prototype.normalise = function() {\n
\t\treturn this.divide(this.magnitude());\n
\t};\n
\n
\t// Point\n
\tLayout.ForceDirected.Point = function(position, mass) {\n
\t\tthis.p = position; // position\n
\t\tthis.m = mass; // mass\n
\t\tthis.v = new Vector(0, 0); // velocity\n
\t\tthis.a = new Vector(0, 0); // acceleration\n
\t};\n
\n
\tLayout.ForceDirected.Point.prototype.applyForce = function(force) {\n
\t\tthis.a = this.a.add(force.divide(this.m));\n
\t};\n
\n
\t// Spring\n
\tLayout.ForceDirected.Spring = function(point1, point2, length, k) {\n
\t\tthis.point1 = point1;\n
\t\tthis.point2 = point2;\n
\t\tthis.length = length; // spring length at rest\n
\t\tthis.k = k; // spring constant (See Hooke\'s law) .. how stiff the spring is\n
\t};\n
\n
\t// Layout.ForceDirected.Spring.prototype.distanceToPoint = function(point)\n
\t// {\n
\t// \t// hardcore vector arithmetic.. ohh yeah!\n
\t// \t// .. see http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment/865080#865080\n
\t// \tvar n = this.point2.p.subtract(this.point1.p).normalise().normal();\n
\t// \tvar ac = point.p.subtract(this.point1.p);\n
\t// \treturn Math.abs(ac.x * n.x + ac.y * n.y);\n
\t// };\n
\n
\t/**\n
\t * Renderer handles the layout rendering loop\n
\t * @param onRenderStop optional callback function that gets executed whenever rendering stops.\n
\t * @param onRenderStart optional callback function that gets executed whenever rendering starts.\n
\t */\n
\tvar Renderer = Springy.Renderer = function(layout, clear, drawEdge, drawNode, onRenderStop, onRenderStart) {\n
\t\tthis.layout = layout;\n
\t\tthis.clear = clear;\n
\t\tthis.drawEdge = drawEdge;\n
\t\tthis.drawNode = drawNode;\n
\t\tthis.onRenderStop = onRenderStop;\n
\t\tthis.onRenderStart = onRenderStart;\n
\n
\t\tthis.layout.graph.addGraphListener(this);\n
\t}\n
\n
\tRenderer.prototype.graphChanged = function(e) {\n
\t\tthis.start();\n
\t};\n
\n
\t/**\n
\t * Starts the simulation of the layout in use.\n
\t *\n
\t * Note that in case the algorithm is still or already running then the layout that\'s in use\n
\t * might silently ignore the call, and your optional <code>done</code> callback is never executed.\n
\t * At least the built-in ForceDirected layout behaves in this way.\n
\t *\n
\t * @param done An optional callback function that gets executed when the springy algorithm stops,\n
\t * either because it ended or because stop() was called.\n
\t */\n
\tRenderer.prototype.start = function(done) {\n
\t\tvar t = this;\n
\t\tthis.layout.start(function render() {\n
\t\t\tt.clear();\n
\n
\t\t\tt.layout.eachEdge(function(edge, spring) {\n
\t\t\t\tt.drawEdge(edge, spring.point1.p, spring.point2.p);\n
\t\t\t});\n
\n
\t\t\tt.layout.eachNode(function(node, point) {\n
\t\t\t\tt.drawNode(node, point.p);\n
\t\t\t});\n
\t\t}, this.onRenderStop, this.onRenderStart);\n
\t};\n
\n
\tRenderer.prototype.stop = function() {\n
\t\tthis.layout.stop();\n
\t};\n
\n
\t// Array.forEach implementation for IE support..\n
\t//https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/Array/forEach\n
\tif ( !Array.prototype.forEach ) {\n
\t\tArray.prototype.forEach = function( callback, thisArg ) {\n
\t\t\tvar T, k;\n
\t\t\tif ( this == null ) {\n
\t\t\t\tthrow new TypeError( " this is null or not defined" );\n
\t\t\t}\n
\t\t\tvar O = Object(this);\n
\t\t\tvar len = O.length >>> 0; // Hack to convert O.length to a UInt32\n
\t\t\tif ( {}.toString.call(callback) != "[object Function]" ) {\n
\t\t\t\tthrow new TypeError( callback + " is not a function" );\n
\t\t\t}\n
\t\t\tif ( thisArg ) {\n
\t\t\t\tT = thisArg;\n
\t\t\t}\n
\t\t\tk = 0;\n
\t\t\twhile( k < len ) {\n
\t\t\t\tvar kValue;\n
\t\t\t\tif ( k in O ) {\n
\t\t\t\t\tkValue = O[ k ];\n
\t\t\t\t\tcallback.call( T, kValue, k, O );\n
\t\t\t\t}\n
\t\t\t\tk++;\n
\t\t\t}\n
\t\t};\n
\t}\n
\n
\tvar isEmpty = function(obj) {\n
\t\tfor (var k in obj) {\n
\t\t\tif (obj.hasOwnProperty(k)) {\n
\t\t\t\treturn false;\n
\t\t\t}\n
\t\t}\n
\t\treturn true;\n
\t};\n
\n
  return Springy;\n
}));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>20157</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>springy.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
