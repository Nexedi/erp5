/*global window, rJS, RSVP, console, Plotly */
/*jslint indent: 2, maxlen: 80, nomen: true */
(function (window, rJS, RSVP, Plotly, loopEventListener) {
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
    return {
      'title' : {
        'text': title
      },
      'xaxis': {
        'title': {
          'text': 'Date'
        },
        'autorange': true,
        'autosize': true
      },
      'yaxis': {
        'fixedrange': true,
        'title': {
          'text': '%'
        }
      }
    };
  }

  function plotFromResponse(response, element, data_type) {
    var kpi_data_dict,
      date = [],
      epsb_estab_sr_lo = [],
      epsb_estab_sr_hi = [],
      success_rate_data = [],
      data_name = '';

    kpi_data_dict = response;

    if (Object.keys(kpi_data_dict).length === 0 ||
        kpi_data_dict.vt.length === 0) {
      Plotly.react(
        element,
        [],
        getNoDataPlotLayout(data_type, 'No data found')
      );
      return;
    }

    kpi_data_dict.vt.forEach(function (element) {
      date.push(new Date(element * 1000));
    });

    if (data_type === 'Initial E-RAB establishment success rate') {
      epsb_estab_sr_lo = kpi_data_dict.v_initial_epsb_estab_sr_lo;
      epsb_estab_sr_hi = kpi_data_dict.v_initial_epsb_estab_sr_hi;
      data_name = 'InitialEPSBEstabSR';
    } else if (data_type === 'Added E-RAB establishment success rate') {
      epsb_estab_sr_lo = kpi_data_dict.v_added_epsb_estab_sr_lo;
      epsb_estab_sr_hi = kpi_data_dict.v_added_epsb_estab_sr_hi;
      data_name = 'AddedEPSBEstabSR';
    }

    success_rate_data = [
      {
        x: date,
        mode: 'lines+markers',
        y: epsb_estab_sr_lo,
        type: 'scatter',
        line: {shape: 'hv'},
        hovertemplate: 'Date: %{x}<br>Rate: %{y}%',
        name: data_name
      },
      {
        x: date,
        mode: 'lines+markers',
        fill: 'tonexty',
        y: epsb_estab_sr_hi,
        type: 'scatter',
        line: {
          color: '#6cb9e5',
          shape: 'hv'
        },
        hovertemplate: 'Date: %{x}<br>Rate: %{y}%',
        name: data_name + ' uncertainty'
      }
    ];
    Plotly.react(
      element,
      success_rate_data,
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
        Plotly.Plots.resize(
          gadget.element.querySelector('.graph-initial-success-rate')
        );
        Plotly.Plots.resize(
          gadget.element.querySelector('.graph-added-success-rate')
        );
      });
    })
    .declareMethod('render', function (option_dict) {
      var gadget = this,
        kpi_url,
        initial_success_rate_element =
          gadget.element.querySelector('.graph-initial-success-rate'),
        added_success_rate_element =
          gadget.element.querySelector('.graph-added-success-rate');

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
          plotFromResponse(
            response,
            initial_success_rate_element,
            'Initial E-RAB establishment success rate'
          );
          plotFromResponse(
            response,
            added_success_rate_element,
            'Added E-RAB establishment success rate'
          );
          gadget.element.querySelector('.ui-icon-spinner').hidden = true;

          initial_success_rate_element.on(
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
                    initial_success_rate_element,
                    'Initial E-RAB establishment success rate'
                  );
                });
            }
          );
          added_success_rate_element.on(
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
                    added_success_rate_element,
                    'Added E-RAB establishment success rate'
                  );
                });
            }
          );
        }, function () {
          // On request error, show empty plots
          plotFromResponse(
            {},
            initial_success_rate_element,
            'Initial E-RAB establishment success rate'
          );
          plotFromResponse(
            {},
            added_success_rate_element,
            'Added E-RAB establishment success rate'
          );
          gadget.element.querySelector('.ui-icon-spinner').hidden = true;
        });
    });

}(window, rJS, RSVP, Plotly, loopEventListener));
