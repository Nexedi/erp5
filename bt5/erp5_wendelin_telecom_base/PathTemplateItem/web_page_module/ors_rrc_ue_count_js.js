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
          text: 'RRC Connection Request + UE Count'
        }
      }
    };
  }

  function getPlotData(date, rrc, hi, avg, lo) {
    var data_list = [];

    data_list.push({
      x: date,
      marker: {
        size: 4
      },
      mode: 'lines+markers',
      y: rrc,
      type: 'scatter',
      line: {'color': '#d62728'},
      opacity: 0.3,
      fill: 'tonexty',
      name: 'RCC Connection Requests',
      legendgroup: 'legendgroup0',
      hovertemplate: 'Date: %{x}<br>RRC Connection Requests: %{y}'
    });
    data_list.push({
      x: date,
      marker: {
        size: 4
      },
      mode: 'lines+markers',
      y: hi,
      type: 'scatter',
      line: {'color': '#ff7f0e'},
      opacity: 0.3,
      fill: 'tonexty',
      name: 'Ue Count Max',
      legendgroup: 'legendgroup0',
      hovertemplate: 'Date: %{x}<br>Ue Count Max: %{y}'
    });
    data_list.push({
      x: date,
      marker: {
        size: 4
      },
      mode: 'lines+markers',
      y: avg,
      type: 'scatter',
      line: {'color': '#1f77b4'},
      opacity: 0.3,
      fill: 'tonexty',
      name: 'Ue Count Avg',
      legendgroup: 'legendgroup0',
      hovertemplate: 'Date: %{x}<br>Ue Count Avg: %{y}'
    });
    data_list.push({
      x: date,
      marker: {
        size: 4
      },
      mode: 'lines+markers',
      y: lo,
      type: 'scatter',
      line: {'color': '#2ca02c'},
      opacity: 0.3,
      fill: 'tonexty',
      name: 'Ue Count Min',
      legendgroup: 'legendgroup0',
      hovertemplate: 'Date: %{x}<br>Ue Count Min: %{y}'
    });
    return data_list;
  }

  function plotFromResponse(response, element, data_type) {
    var rafael_test_data_dict,
      date = [],
      cell_id = [],
      rcc = [],
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

    link_data = getPlotData(
      date,
      rafael_test_data_dict.rrc_con_req,
      rafael_test_data_dict.ue_count_max,
      rafael_test_data_dict.ue_count_avg,
      rafael_test_data_dict.ue_count_min
    );
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
          gadget.element.querySelector('.graph-rrc-con-req'));
      });
    })
    .declareMethod('render', function (option_dict) {
      var gadget = this,
        ue_count_url,
        chart_element = gadget.element.querySelector('.graph-rrc-con-req');

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
          plotFromResponse(
            response, chart_element, 'RRC Connection Requests + UE Count');
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
                    'RRC Connection Requests + UE Count'
                  );
                });
            }
          );
        }, function () {
          // On request error, show empty plots
          plotFromResponse(
            {},
            chart_element,
            'RRC Connection Requests + UE Count'
          );
          gadget.element.querySelector('.ui-icon-spinner').hidden = true;
        });
    });
}(window, rJS, RSVP, Plotly, URI, loopEventListener));
