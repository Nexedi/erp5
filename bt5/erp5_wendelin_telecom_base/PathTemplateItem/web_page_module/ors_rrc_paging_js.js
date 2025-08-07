/*global window, document, rJS, RSVP, Plotly, URI, location, loopEventListener */
/*jslint indent: 2, maxlen: 80, nomen: true */
(function (window, document, rJS, RSVP, Plotly, URI, loopEventListener) {
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
        'autorange': true,
        'autosize': true,
        title: {
          text: 'Date'
        }
      },
      'yaxis': {
        'autorange': true,
        'autorangeoptions': {
          minallowed: 0
        },
        'fixedrange': true,
        title: {
          text: 'RRC Paging'
        }
      }
    };
  }

  function getPlotData(date, connection_request) {
    var data_list = [];

    data_list.push({
      x: date,
      marker: {
        size: 4
      },
      mode: 'lines+markers',
      y: connection_request,
      type: 'scatter',
      line: {'color': '#1f77b4'},
      opacity: 0.3,
      fill: 'tonexty',
      name: 'RCC Paging',
      legendgroup: 'legendgroup0',
      hovertemplate: 'Date: %{x}<br>RRC Paging: %{y}'
    });
    return data_list;
  }

  function plotFromData(data, element, label) {
    var date = [];

    if (Object.keys(data).length === 0 ||
        data.utc.length === 0) {
      element.innerHTML = "";
      Plotly.react(
        element,
        [],
        getNoDataPlotLayout('No data found')
      );
      return;
    }

    data.utc.forEach(function (element) {
      date.push(new Date(element * 1000));
    });

    return Plotly.react(
      element,
      getPlotData(date, data.rrc_paging),
      getDataPlotLayout(label)
    );
  }

  function plotFromResponse(response, base_element) {
    var label,
      plotContainer,
      plotContainerList = [];
    if (Object.keys(response).length === 0) {
      Plotly.react(
        base_element,
        [],
        getNoDataPlotLayout('No data found')
      );
      return;
    }

    // There is only once cell to plot
    label = "RRC Paging";
    plotContainer = document.createElement('div');
    plotContainer.classList.add('graph-item');
    plotContainer.setAttribute('data-id', 'base');

    plotFromData(response.base, plotContainer, label);
    plotContainerList.push(plotContainer);

    base_element.innerHTML = "";
    plotContainerList.forEach(function (div) {
      base_element.appendChild(div);
    });
    return plotContainerList;
  }

  gadget_klass
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod('jio_getAttachment', 'jio_getAttachment')
    .declareService(function () {
      var gadget = this;
      return loopEventListener(window, 'resize', false, function () {
        var div_list = gadget.element.querySelectorAll('.graph-item');
        if (div_list.length > 0) {
          div_list.forEach(function (element) {
            Plotly.Plots.resize(element);
          });
        }
        return;
      });
    })
    .declareMethod('render', function (option_dict) {
      var gadget = this,
        data_url,
        chart_element = gadget.element.querySelector('.graph-base');

      return gadget.getSetting('hateoas_url')
        .push(function (hateoas_url) {
          data_url =
            (new URI(hateoas_url)).absoluteTo(location.href).toString() +
            'Base_getDataArrayForDataTypeAsJSON?data_array_url=' +
            option_dict.data_array_url +
            '&data_type=' + option_dict.data_type;
          return gadget.jio_getAttachment('erp5', data_url, {
            format: 'json'
          });
        })
        .push(function (response) {
          var plotContainerList = plotFromResponse(response, chart_element);
          gadget.element.querySelector('.ui-icon-spinner').hidden = true;

          return new RSVP.Queue().push(function () {
            plotContainerList.forEach(function (el) {
              return new RSVP.Queue().push(function () {
                return Plotly.Plots.resize(el);
              })
                .push(function () {
                  return el.on(
                    'plotly_relayout',
                    function (eventdata) {
                      var st = new Date(eventdata['xaxis.range[0]']).getTime(),
                        end = new Date(eventdata['xaxis.range[1]']).getTime(),
                        update_data_url = data_url + '&time_start=' +
                          st / 1000 + '&time_end=' + end  / 1000;

                      return new RSVP.Queue().push(function () {
                        return gadget.jio_getAttachment('erp5',
                          update_data_url, {format: 'json' });
                      })
                        .push(function (response) {
                          var key = el.getAttribute('data-id'),
                            label = "RRC Paging",
                            data = response[key];

                          return plotFromData(data, el, label);
                        });
                    }
                  );
                });
            });
            return plotContainerList;
          });
        });
    });
}(window, document, rJS, RSVP, Plotly, URI, loopEventListener));
