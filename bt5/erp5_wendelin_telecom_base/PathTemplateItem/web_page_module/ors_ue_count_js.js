/*global window, rJS, RSVP, console, Plotly, location, URI, loopEventListener */
/*jslint indent: 2, maxlen: 80, nomen: true */
(function (window, rJS, RSVP, Plotly, URI, loopEventListener) {
  'use strict';

  var gadget_klass = rJS(window);

  function getNoDataPlotLayout(title, annotation) {
    return {
      'title' : {
        'text': title
      },
      'xaxis': {
        'fixedrange': true
      },
      'yaxis': {
        'fixedrange': true
      },
      'annotations': [
        {
          'text': annotation,
          'xref': 'paper',
          'yref': 'paper',
          'showarrow': false,
          'font': {
            'size': 28
          }
        }
      ]
    };
  }

  function getDataPlotLayout(title) {
    var yaxis_clipmax;

    //if (title == 'UE Count') {
    //  yaxis_clipmax = 400;
    //}

    return {
      'title' : {
        'text': title
      },
      'xaxis': {
        'autorange': true,
        'autosize': true,
        title: {
          text: 'Date'
        }
      },
      'yaxis': {
        'autorange': true,
        'autorangeoptions': {
          clipmax: yaxis_clipmax,
          minallowed: 0
        },
        'fixedrange': true,
        title: {
          text: 'UE Count'
        }
      }
    };
  }

  function getPlotData(date, lo, av, hi) {
    var color,
      color_array = [
        {'color': '#1f77b4'},
        {'color': '#ff7f0e'},
        {'color': '#2ca02c'}
      ],
      data_list = [];

    data_list.push({
      x: date,
      marker: {
        size: 4
      },
      mode: 'lines+markers',
      y: lo,
      type: 'scatter',
      line: color_array[3],
      name: 'Min',
      legendgroup: 'legendgroup0',
      hovertemplate: 'Date: %{x}<br>UE Count Min: %{y}'
    });
    data_list.push({
      x: date,
      marker: {
        size: 4
      },
      mode: 'lines+markers',
      y: av,
      type: 'scatter',
      line: color_array[1],
      opacity: 0.3,
      fill: 'tonexty',
      name: 'Avg',
      legendgroup: 'legendgroup0',
      hovertemplate: 'Date: %{x}<br>UE Count Average: %{y}'
    });
    data_list.push({
      x: date,
      marker: {
        size: 4
      },
      mode: 'lines+markers',
      y: hi,
      type: 'scatter',
      line: color_array[0],
      opacity: 0.3,
      fill: 'tonexty',
      name: 'Max',
      legendgroup: 'legendgroup0',
      hovertemplate: 'Date: %{x}<br>UE Count Max: %{y}'
    });
    return data_list;
  }

  function plotFromResponse(response, element, data_type) {
    var rafael_test_data_dict,
      date = [],
      cell_id = [],
      ue_count_min = [],
      ue_count_avg = [],
      ue_count_max = [],
      link_data = [];

    rafael_test_data_dict = response;

    if (Object.keys(rafael_test_data_dict).length === 0 ||
        rafael_test_data_dict.utc.length === 0) {
      Plotly.react(
        element,
        [],
        getNoDataPlotLayout(data_type, 'No data found')
      );
      return;
    }

    rafael_test_data_dict.utc.forEach(function (element) {
      date.push(new Date(element * 1000));
    });

    if (data_type === 'UE Count vs Time') {
      cell_id = rafael_test_data_dict.cell_id;
      ue_count_max = rafael_test_data_dict.ue_count_max;
      ue_count_avg = rafael_test_data_dict.ue_count_avg;
      ue_count_min = rafael_test_data_dict.ue_count_min;
    }

    link_data = getPlotData(date, ue_count_min, ue_count_avg, ue_count_max);
    Plotly.react(
      element,
      link_data,
      getDataPlotLayout(data_type)
    );
  }

  gadget_klass
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod('jio_getAttachment', 'jio_getAttachment')
    .declareService(function () {
      var gadget = this;
      return loopEventListener(window, 'resize', false, function () {
        return Plotly.Plots.resize(
          gadget.element.querySelector('.graph-ue-count'));
      });
    })
    .declareMethod('render', function (option_dict) {
      var gadget = this,
        ue_count_url,
        chart_element = gadget.element.querySelector('.graph-ue-count');

      return new RSVP.Queue().push(function () {
        return gadget.getSetting('hateoas_url');
      })
        .push(function (hateoas_url) {
          ue_count_url =
            (new URI(hateoas_url)).absoluteTo(location.href).toString() +
            'Base_getOrsEnbUeCount?data_array_url=' +
            option_dict.data_array_url +
            '&kpi_type=' + option_dict.kpi_type;
          return gadget.jio_getAttachment('erp5', ue_count_url, {
            format: 'json'
          });
        })
        .push(function (response) {
          plotFromResponse(response, chart_element, 'UE Count vs Time');
          gadget.element.querySelector('.ui-icon-spinner').hidden = true;

          chart_element.on(
            'plotly_relayout',
            function (eventdata) {
              var xrange_0 = eventdata['xaxis.range[0]'],
                xrange_1 = eventdata['xaxis.range[1]'],
                x_start = new Date(xrange_0).getTime() / 1000,
                x_end = new Date(xrange_1).getTime() / 1000,
                update_ue_count_url = ue_count_url + '&time_start=' + x_start +
                  '&time_end=' + x_end;

              return new RSVP.Queue().push(function () {
                return gadget.jio_getAttachment('erp5', update_ue_count_url, {
                  format: 'json'
                });
              })
                .push(function (response) {
                  plotFromResponse(
                    response,
                    chart_element,
                    'UE Count vs Time'
                  );
                });
            }
          );
        }, function () {
          // On request error, show empty plots
          plotFromResponse(
            {},
            chart_element,
            'UE Count vs Time'
          );
          gadget.element.querySelector('.ui-icon-spinner').hidden = true;
        });
    });
}(window, rJS, RSVP, Plotly, URI, loopEventListener));
