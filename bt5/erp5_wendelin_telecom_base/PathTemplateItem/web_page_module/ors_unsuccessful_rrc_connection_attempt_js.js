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
          text: 'Unsuccessful RRC Connection Attempt'
        }
      }
    };
  }

  function getPlotData(date, rrc) {
    var data_list = [];

    data_list.push({
      x: date,
      marker: {
        size: 4
      },
      mode: 'lines+markers',
      y: rrc,
      type: 'scatter',
      line: {'color': '#1f77b4'},
      opacity: 0.3,
      fill: 'tonexty',
      name: 'Unsuccessful Attempts',
      legendgroup: 'legendgroup0',
      hovertemplate: 'Date: %{x}<br>Unsuccessful RRC Connection Attempt: %{y}'
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

    rcc = rafael_test_data_dict.unsucessful_rrc_recon;

    link_data = getPlotData(date, rcc);
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
          gadget.element.querySelector('.graph-rrc'));
      });
    })
    .declareMethod('render', function (option_dict) {
      var gadget = this,
        ue_count_url,
        chart_element = gadget.element.querySelector('.graph-rrc');

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
            response, chart_element, 'Unsuccessful RRC Connection Attempt');
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
                    'Unsuccessful RRC Connection Attempt'
                  );
                });
            }
          );
        }, function () {
          // On request error, show empty plots
          plotFromResponse(
            {},
            chart_element,
            'Unsuccessful RRC Connection Attempt'
          );
          gadget.element.querySelector('.ui-icon-spinner').hidden = true;
        });
    });
}(window, rJS, RSVP, Plotly, URI, loopEventListener));
