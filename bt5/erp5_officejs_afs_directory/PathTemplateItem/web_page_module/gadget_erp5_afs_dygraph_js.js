/*globals window, RSVP, rJS, Dygraph, Date, Object, Intl*/
/*jslint indent: 2, nomen: true, maxlen: 80*/

(function (window, RSVP, rJS, Dygraph, Date, Object, Intl) {
  "use strict";

  // Darken a color
  function darkenColor(colorStr) {
    // Defined in dygraph-utils.js
    var color = Dygraph.toRGB_(colorStr);
    color.r = Math.floor((255 + color.r) / 2);
    color.g = Math.floor((255 + color.g) / 2);
    color.b = Math.floor((255 + color.b) / 2);
    return 'rgb(' + color.r + ',' + color.g + ',' + color.b + ')';
  }

  function multiColumnBarPlotter(e) {
    var g,
      ctx,
      set,
      y_bottom,
      min_sep,
      j,
      points,
      sep,
      sets,
      bar_width,
      fillColors,
      strokeColors,
      i,
      k,
      l,
      m,
      p,
      center_x,
      x_left;

    if (e.seriesIndex !== 0) {
      return;
    }
    g = e.dygraph;
    ctx = e.drawingContext;
    sets = e.allSeriesPoints;
    y_bottom = e.dygraph.toDomYCoord(0);
    min_sep = Infinity;

    // Find the minimum separation between x-values.
    // This determines the bar width.
    for (j = 0; j < sets.length; j += 1) {
      points = sets[j];
      for (i = 1; i < points.length; i++) {
        sep = points[i].canvasx - points[i - 1].canvasx;
        if (sep < min_sep) {
          min_sep = sep;
        }
      }
    }
    bar_width = Math.floor(2.0 / 3 * min_sep);
    fillColors = [];
    strokeColors = g.getColors();
    for (m = 0; m < strokeColors.length; m += 1) {
      fillColors.push(darkenColor(strokeColors[m]));
    }
    for (k = 0; k < sets.length; k += 1) {
      ctx.fillStyle = fillColors[k];
      ctx.strokeStyle = strokeColors[k];
      for (l = 0; l < sets[k].length; l += 1) {
        p = sets[k][l];
        center_x = p.canvasx;
        x_left = center_x - (bar_width / 2) * (1 - k / (sets.length - 1));

        ctx.fillRect(
          x_left,
          p.canvasy,
          bar_width / sets.length,
          y_bottom - p.canvasy
        );

        ctx.strokeRect(
          x_left,
          p.canvasy,
          bar_width / sets.length,
          y_bottom - p.canvasy
        );
      }
    }
  }

  function prepDataSet(my_data) {
    return Object.keys(my_data).map(function (year) {
      var reported_year = my_data[year];
      return [
        new Date(year + "/6/30"),
        reported_year.total_assets.value,
        reported_year.revenues.value,
        reported_year.earnings.value,
        reported_year.staff.value
      ];
    });
  }

  function getElem(my_element, my_selector) {
    return my_element.querySelector(my_selector);
  }

  rJS(window)

    .ready(function (gadget) {
      gadget.property_dict = {
        "graph_wrapper": getElem(gadget.element, ".dygraph-multibar"),
        "graph": null,
        "deferred": new RSVP.defer()
      };

      // disable zoom
      Dygraph.prototype.doZoomY_ = function () {
        return;
      };
      Dygraph.prototype.doZoomX_ = function () {
        return;
      };
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        dict = gadget.property_dict;
      return dict.deferred.resolve(options.data);
    })

    .declareMethod("renderGraph", function (my_data) {
      var gadget = this;
      var dict = gadget.property_dict;

      dict.graph = new Dygraph(
        dict.graph_wrapper,
        prepDataSet(my_data),
        {
          dateWindow: [ Date.parse("2016/01/01"), Date.parse("2019/01/01")],
          legend: 'always',
          drawPoints: true,
          title: 'Aggregate Financial Performance',
          width: "auto",
          height: 720,
          maxNumberWidth: 20,
          includeZero: true,
          plotter: multiColumnBarPlotter,
          axes : {
            x : {
              axisLabelFormatter: function (d) {
                return d.getFullYear();
              },
              valueFormatter: function (ms) {
                return new Date(ms).getFullYear();
              }
            },
            y: {
              axisLabelWidth: 100,
              valueFormatter: function (value) {
                return new Intl.NumberFormat('en-EN', {
                  style: 'currency',
                  currency: 'EUR',
                  minimumFractionDigits: "0"
                }).format(value);
              }
            },
            y2: {
              labelsKMB: true,
              axisLabelWidth: 100,
              independentTicks: true
            }
          },
          labels: ["Year", "Total Assets", "Revenues", "Earnings", "Staff"],
          series: {
            "Staff": {
              axis: "y2"
            }
          }
        }
      );
    })

    .declareService(function () {
      var gadget = this,
        dict = gadget.property_dict;

      return new RSVP.Queue()
        .push(function () {
          return dict.deferred.promise;
        })
        .push(function (my_data) {
          return gadget.renderGraph(my_data);
        });
    });

}(window, RSVP, rJS, Dygraph, Date, Object, Intl));