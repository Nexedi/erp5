/*global window, rJS, console, RSVP, Dygraph, DataView, Float32Array,
document */
/*jslint indent: 2, maxerr: 3 */

(function (rJS) {
  "use strict";

  rJS(window)

    .ready(function (gadget) {
      gadget.property_dict = {};
    })

    .declareMethod('draw', function (data) {
      /* a generic method to call which can draw a diagram */
      var graph_gadget = this;
      return graph_gadget.getElement()
        .push(function (dom_element) {

          var data_points_per_channel, total_channels, byte_len, i,
            tmp_data, x_value, x_delta, make_shell, start_time, stop_time,
            make_series, make_graph_struct, test_a;

          // data parameters
          x_value = "time";               // must be passed from header
          x_delta = 0.00000025;           // must be passed from header
          data_points_per_channel = 4000; // must be passed from header
          total_channels = 3;             // must be passed from header

          start_time = Date.now();

          data = new DataView(data);

          byte_len = data.byteLength;

          tmp_data = new Float32Array(byte_len / Float32Array.BYTES_PER_ELEMENT);

          // Incoming data is raw floating point values with little-endian byte ordering.
          for (i = 0; i < tmp_data.length; i += 1) {
            tmp_data[i] = data.getFloat32(i * Float32Array.BYTES_PER_ELEMENT, true);
          }

          // graph shell
          make_shell = function (opts) {
            var x, shell, shell_row;

            shell = [];
            for (x = 0; x < opts.points; x += 1) {
              shell_row = [];
              shell_row.push(opts.delta * x);
              shell.push(shell_row);
            }
            return shell;
          };

          // graph data series
          make_series = function (opts) {
            var k, pos;

            pos = opts.start;
            for (k = 0; k < opts.points; k += 1) {
              opts.shell[k].push(opts.float[k + pos]);
            }
            return opts.shell;
          };

          // build a row structure for dygraph with series needed
          make_graph_struct = function (opts) {
            var j, k, channel_len, struct, series;

            for (j = 0, channel_len = opts.total_channels; j < channel_len; j += 1) {
              for (k = 0; k < opts.display.length; k += 1) {
                series = opts.display[k];
                if (series[0] === j) {
                  struct = make_series({
                    "points": opts.points,
                    "float": opts.data,
                    "shell":  make_shell({
                      "points": opts.points,
                      "delta": opts.delta
                    }),
                    "start": series[1]
                  });
                }
              }
            }
            return struct;
          };

          // dynagraph
          test_a = new Dygraph(
            dom_element.querySelector(".graph-a"),
            make_graph_struct({
              "display": [[0, 0]],
              "total_channels": total_channels,
              "points": data_points_per_channel,
              "data": tmp_data,
              "delta": x_delta
            }),
            {
              "legend": 'always',
              "title": 'Channel X',
              "showRoller": true,
              "rollPeriod": 50,
              "labels": [ x_value, "A" ]
            }
          );

          test_a = new Dygraph(
            dom_element.querySelector(".graph-b"),
            make_graph_struct({
              "display": [[1, data_points_per_channel]],
              "total_channels": total_channels,
              "points": data_points_per_channel,
              "data": tmp_data,
              "delta": x_delta
            }),
            {
              "legend": 'always',
              "title": 'Channel Y',
              "showRoller": true,
              "rollPeriod": 50,
              "labels": [ x_value, "B" ]
            }
          );

          test_a = new Dygraph(
            dom_element.querySelector(".graph-c"),
            make_graph_struct({
              "display": [[2, 2 * data_points_per_channel]],
              "total_channels": total_channels,
              "points": data_points_per_channel,
              "data": tmp_data,
              "delta": x_delta
            }),
            {
              "legend": 'always',
              "title": 'Channel Z',
              "showRoller": true,
              "rollPeriod": 50,
              "labels": [ x_value, "C" ]
            }
          );

          stop_time = Date.now();
          console.log(stop_time - start_time);
        });
    });
}(rJS));