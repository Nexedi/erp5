/*global window, rJS, RSVP, console, Plotly, location */
/*jslint indent: 2, maxlen: 80, nomen: true */
(function (window, rJS, RSVP, Plotly) {
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

    if (title == 'Downlink') {
      yaxis_clipmax = 400;
    } else if (title == 'Uplink') {
      yaxis_clipmax = 150;
    }

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
          minallowed: -3
        },
        'fixedrange': true,
        title: {
          text: 'Mbit/s'
        }
      }
    };
  }

  function getPlotData(active_qci, date, lo, hi) {
    var color,
      color_array = [
        {'color': '#1f77b4'},
        {'color': '#ff7f0e'},
        {'color': '#2ca02c'},
        {'color': '#d62728'},
        {'color': '#9467bd'},
        {'color': '#8c564b'},
        {'color': '#e377c2'},
        {'color': '#7f7f7f'},
        {'color': '#bcbd22'},
        {'color': '#17becf'}
      ],
      data_list = [];

    active_qci.forEach(function (qci, i) {
      color = color_array[i % color_array.length];

      lo[i].forEach(function (value, j) {
        lo[i][j] = value / 1e6;
      });
      hi[i].forEach(function (value, j) {
        hi[i][j] = value / 1e6;
      });

      data_list.push({
        x: date,
        marker: {
          size: 4
        },
        mode: 'lines+markers',
        y: lo[i],
        type: 'scatter',
        line: color,
        name: 'IPThp.' + qci,
        legendgroup: 'legendgroup' + qci,
        hovertemplate: 'Date: %{x}<br>Minimum Link Speed: %{y} Mbit/s'
      });
      data_list.push({
        x: date,
        marker: {
          size: 4
        },
        mode: 'lines+markers',
        y: hi[i],
        type: 'scatter',
        line: color,
        opacity: 0.3,
        fill: 'tonexty',
        name: 'IpThp.' + qci,
        legendgroup: 'legendgroup' + qci,
        showlegend: false,
        hovertemplate: 'Date: %{x}<br>Maximum Link Speed: %{y} Mbit/s'
      });
    });
    return data_list;
  }

  function plotFromResponse(response, element, data_type) {
    var kpi_data_dict,
      active_qci = [],
      date = [],
      l_lo = [],
      l_hi = [],
      link_data = [];

    kpi_data_dict = response;

    if (Object.keys(kpi_data_dict).length === 0 ||
        kpi_data_dict.evt.length === 0) {
      Plotly.react(
        element,
        [],
        getNoDataPlotLayout(data_type, 'No data found')
      );
      return;
    }

    kpi_data_dict.evt.forEach(function (element) {
      date.push(new Date(element * 1000));
    });

    active_qci = kpi_data_dict.active_qci;
    if (data_type === 'Downlink') {
      l_lo = kpi_data_dict.dl_lo;
      l_hi = kpi_data_dict.dl_hi;
    } else if (data_type === 'Uplink') {
      l_lo = kpi_data_dict.ul_lo;
      l_hi = kpi_data_dict.ul_hi;
    }

    link_data = getPlotData(active_qci, date, l_lo, l_hi);
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
        Plotly.Plots.resize(gadget.element.querySelector('.graph-downlink'));
        Plotly.Plots.resize(gadget.element.querySelector('.graph-uplink'));
      });
    })
    .declareMethod('render', function (option_dict) {
      var gadget = this,
        kpi_url,
        downlink_element = gadget.element.querySelector('.graph-downlink'),
        uplink_element = gadget.element.querySelector('.graph-uplink');

      return new RSVP.Queue().push(function () {
        return gadget.getSetting('hateoas_url');
      })
        .push(function (hateoas_url) {
          kpi_url =
            (new URI(hateoas_url)).absoluteTo(location.href).toString() +
            'Base_getOrsEnbKpi?data_array_url=' +
            option_dict.data_array_url +
            '&kpi_type=' + option_dict.kpi_type;
          return gadget.jio_getAttachment('erp5', kpi_url, {
            format: 'json'
          });
        })
        .push(function (response) {
          plotFromResponse(response, downlink_element, 'Downlink');
          plotFromResponse(response, uplink_element, 'Uplink');
          gadget.element.querySelector('.ui-icon-spinner').hidden = true;

          downlink_element.on(
            'plotly_relayout',
            function (eventdata) {
              var x_start = new Date(eventdata['xaxis.range[0]']).getTime()
                / 1000,
                x_end = new Date(eventdata['xaxis.range[1]']).getTime()
                / 1000,
                update_kpi_url = kpi_url +
                '&time_start=' + x_start +
                '&time_end=' + x_end;

              return new RSVP.Queue().push(function () {
                return gadget.jio_getAttachment('erp5', update_kpi_url, {
                  format: 'json'
                });
              })
                .push(function (response) {
                  plotFromResponse(
                    response,
                    downlink_element,
                    'Downlink'
                  );
                });
            }
          );
          uplink_element.on(
            'plotly_relayout',
            function (eventdata) {
              var x_start = new Date(eventdata['xaxis.range[0]']).getTime()
                / 1000,
                x_end = new Date(eventdata['xaxis.range[1]']).getTime()
                / 1000,
                update_kpi_url = kpi_url +
                '&time_start=' + x_start +
                '&time_end=' + x_end;

              return new RSVP.Queue().push(function () {
                return gadget.jio_getAttachment('erp5', update_kpi_url, {
                  format: 'json'
                });
              })
                .push(function (response) {
                  plotFromResponse(
                    response,
                    uplink_element,
                    'Uplink'
                  );
                });
            }
          );
        }, function () {
          // On request error, show empty plots
          plotFromResponse(
            {},
            downlink_element,
            'Downlink'
          );
          plotFromResponse(
            {},
            uplink_element,
            'Uplink'
          );
          gadget.element.querySelector('.ui-icon-spinner').hidden = true;
        });
    });
}(window, rJS, RSVP, Plotly));
