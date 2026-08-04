/*global window */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window) {
  "use strict";



  var CANVAS_NOTE = "Canvas origin (0,0) is top-left, x grows right, y grows down.";

  function createToolList(canvas) {
    var ctx = canvas.getContext("2d");

    return [
      {
        definition: {
          name: "clear_canvas",
          description: "Clear the drawing canvas. " + CANVAS_NOTE + " Call this before starting a new drawing.",
          parameters: { type: "object", properties: {} }
        },
        execute: function () {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          return { cleared: true };
        }
      },
      {
        definition: {
          name: "draw_rectangle",
          description: "Draw a rectangle on the canvas. " + CANVAS_NOTE,
          parameters: {
            type: "object",
            properties: {
              x: { type: "number", description: "left edge x" },
              y: { type: "number", description: "top edge y" },
              width: { type: "number" },
              height: { type: "number" },
              color: { type: "string", description: "CSS color, default 'black'" },
              fill: { type: "boolean", description: "fill (true) or outline only (false), default true" }
            },
            required: ["x", "y", "width", "height"]
          }
        },
        execute: function (args) {
          var color = args.color || "black",
            fill = args.fill !== false;
          if (fill) {
            ctx.fillStyle = color;
            ctx.fillRect(args.x, args.y, args.width, args.height);
          } else {
            ctx.strokeStyle = color;
            ctx.strokeRect(args.x, args.y, args.width, args.height);
          }
          return { drawn: "rectangle", x: args.x, y: args.y, width: args.width, height: args.height, color: color, fill: fill };
        }
      },
      {
        definition: {
          name: "draw_circle",
          description: "Draw a circle on the canvas. " + CANVAS_NOTE,
          parameters: {
            type: "object",
            properties: {
              x: { type: "number", description: "center x" },
              y: { type: "number", description: "center y" },
              radius: { type: "number" },
              color: { type: "string", description: "CSS color, default 'black'" },
              fill: { type: "boolean", description: "fill (true) or outline only (false), default true" }
            },
            required: ["x", "y", "radius"]
          }
        },
        execute: function (args) {
          var color = args.color || "black",
            fill = args.fill !== false;
          ctx.beginPath();
          ctx.arc(args.x, args.y, args.radius, 0, Math.PI * 2);
          if (fill) {
            ctx.fillStyle = color;
            ctx.fill();
          } else {
            ctx.strokeStyle = color;
            ctx.stroke();
          }
          return { drawn: "circle", x: args.x, y: args.y, radius: args.radius, color: color, fill: fill };
        }
      },
      {
        definition: {
          name: "draw_line",
          description: "Draw a straight line segment on the canvas. " + CANVAS_NOTE,
          parameters: {
            type: "object",
            properties: {
              x1: { type: "number" },
              y1: { type: "number" },
              x2: { type: "number" },
              y2: { type: "number" },
              color: { type: "string", description: "CSS color, default 'black'" },
              lineWidth: { type: "number", description: "stroke width in px, default 1" }
            },
            required: ["x1", "y1", "x2", "y2"]
          }
        },
        execute: function (args) {
          var color = args.color || "black",
            lineWidth = args.lineWidth || 1;
          ctx.beginPath();
          ctx.moveTo(args.x1, args.y1);
          ctx.lineTo(args.x2, args.y2);
          ctx.strokeStyle = color;
          ctx.lineWidth = lineWidth;
          ctx.stroke();
          return { drawn: "line", x1: args.x1, y1: args.y1, x2: args.x2, y2: args.y2, color: color, lineWidth: lineWidth };
        }
      },
      {
        definition: {
          name: "draw_polygon",
          description: "Draw a closed polygon (e.g. a triangle, or any custom shape/'form') on the canvas from a list of points. " + CANVAS_NOTE,
          parameters: {
            type: "object",
            properties: {
              points: {
                type: "array",
                description: "ordered vertices, e.g. [{x:10,y:10},{x:50,y:10},{x:30,y:60}] for a triangle",
                items: {
                  type: "object",
                  properties: {
                    x: { type: "number" },
                    y: { type: "number" }
                  },
                  required: ["x", "y"]
                }
              },
              color: { type: "string", description: "CSS color, default 'black'" },
              fill: { type: "boolean", description: "fill (true) or outline only (false), default true" }
            },
            required: ["points"]
          }
        },
        execute: function (args) {
          var color = args.color || "black",
            fill = args.fill !== false,
            points = args.points,
            i;
          if (!points || points.length < 3) {
            throw new Error("points must be an array of at least 3 {x,y} vertices");
          }
          ctx.beginPath();
          ctx.moveTo(points[0].x, points[0].y);
          for (i = 1; i < points.length; i += 1) {
            ctx.lineTo(points[i].x, points[i].y);
          }
          ctx.closePath();
          if (fill) {
            ctx.fillStyle = color;
            ctx.fill();
          } else {
            ctx.strokeStyle = color;
            ctx.stroke();
          }
          return { drawn: "polygon", points: points, color: color, fill: fill };
        }
      },
      {
        definition: {
          name: "draw_text",
          description: "Draw text on the canvas. " + CANVAS_NOTE,
          parameters: {
            type: "object",
            properties: {
              x: { type: "number" },
              y: { type: "number" },
              text: { type: "string" },
              color: { type: "string", description: "CSS color, default 'black'" },
              fontSize: { type: "number", description: "px, default 16" }
            },
            required: ["x", "y", "text"]
          }
        },
        execute: function (args) {
          var color = args.color || "black",
            fontSize = args.fontSize || 16;
          ctx.fillStyle = color;
          ctx.font = fontSize + "px sans-serif";
          ctx.fillText(args.text, args.x, args.y);
          return { drawn: "text", x: args.x, y: args.y, text: args.text, color: color, fontSize: fontSize };
        }
      }
    ];
  }

  window.ChatTools = { createToolList: createToolList };
}(window));
