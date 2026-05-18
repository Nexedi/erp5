/*global window, document, Math, rJS, RSVP, console, Plotly, location, URI, loopEventListener */
/*jslint indent: 2, maxlen: 80, nomen: true */
(function (window, document, Math, rJS, RSVP, Plotly, URI, loopEventListener) {
  'use strict';

  var gadget_klass = rJS(window);

  function getNoDataPlotLayout(annotation) {
    return {
      'title' : {
        'text': annotation
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
          text: 'Bytes'
        }
      }
    };
  }

  function getPlotData(date, bytes) {
    var color_array = [
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
      y: bytes,
      type: 'scatter',
      line: color_array[3],
      name: 'Bytes',
      legendgroup: 'legendgroup0',
      hovertemplate: 'Date: %{x}<br>Bytes: %{y}'
    });
    return data_list;
  }

  function plotFromData(data, element, label, prop) {
    var date = [],
      value = [];

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

    value = data[prop];

    return Plotly.react(
      element,
      getPlotData(date, value),
      getDataPlotLayout(label)
    );
  }

  function plotFromResponse(response, base_element) {
    var key,
      data,
      label,
      plotContainer,
      plotContainerList = [];
    if (Object.keys(response).length === 0) {
      Plotly.react(
        base_element,
        [],
        getNoDataPlotLayout('No data found')
      );
      return plotContainerList;
    }

    label = "Throughout over Time";
    plotContainer = document.createElement('div');
    plotContainer.classList.add('graph-item');
    plotContainer.setAttribute('data-id', 'bytes');
    plotContainer.setAttribute('data-label', label);

    plotFromData(response.bytes, plotContainer, label, 'bytes');
    plotContainerList.push(plotContainer);

    label = "Requests per Second";
    plotContainer = document.createElement('div');
    plotContainer.classList.add('graph-item');
    plotContainer.setAttribute('data-id', 'rps');
    plotContainer.setAttribute('data-label', label);

    plotFromData(response.rps, plotContainer, label, 'rps');
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

      if (option_dict.data_array_url === null) {
        gadget.element.querySelector('.ui-icon-spinner').hidden = true;
        Plotly.react(
          chart_element,
          [],
          getNoDataPlotLayout('No data found')
        );
        return;
      }

      return gadget.getSetting('hateoas_url')
        .push(function (hateoas_url) {
          data_url =
            (new URI(hateoas_url)).absoluteTo(location.href).toString() +
            'Base_getDataArrayForCDNDataTypeAsJSON?data_array_url=' +
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
                            label = el.getAttribute('data-label'),
                            data = response[key];

                          return plotFromData(data, el, label, key);
                        });
                    }
                  );
                });
            });
            return plotContainerList;
          });
        });
    });
}(window, document, Math, rJS, RSVP, Plotly, URI, loopEventListener));
