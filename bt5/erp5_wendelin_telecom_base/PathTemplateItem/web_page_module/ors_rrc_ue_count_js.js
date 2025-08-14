/*global window, document, Math, rJS, RSVP, console, Plotly, location, URI, loopEventListener */
/*jslint indent: 2, maxlen: 80, nomen: true */
(function (window, document, Math, rJS, RSVP, Plotly, URI, loopEventListener) {
  'use strict';

  var gadget_klass = rJS(window);

  function getNoDataPlotLayout(annotation) {
    return {
      'title' : {
        'text': 'RRC Connection Request + UE Count vs Time'
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
      getPlotData(date,
        data.rrc_con_req,
        data.ue_count_max,
        data.ue_count_avg,
        data.ue_count_min),
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
      return;
    }

    // Add base before
    label = "UE Count vs Time (all cells)";
    plotContainer = document.createElement('div');
    plotContainer.classList.add('graph-item');
    plotContainer.setAttribute('data-id', 'base');

    plotFromData(response.base, plotContainer, label);
    plotContainerList.push(plotContainer);

    // Include cell list after
    Object.entries(response).forEach(function (entry) {
      key = entry[0];
      data = entry[1];
      label = "RRC Connection Requests + UE Count vs Time";
      plotContainer = document.createElement('div');

      if (key !== 'base') {
        label += " CELL " + Math.floor(key).toString();
        plotContainer.classList.add('graph-item');
        plotContainer.setAttribute('data-id', key);
        plotFromData(data, plotContainer, label);
        plotContainerList.push(plotContainer);
      }
    });
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
        var div_list = gadget.element.querySelectorAll('.graph-ue-count');
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

      return new RSVP.Queue().push(function () {
        return gadget.getSetting('hateoas_url');
      })
        .push(function (hateoas_url) {
          data_url =
            (new URI(hateoas_url)).absoluteTo(location.href).toString() +
            'Base_getMergedDataArrayForDataTypeAsJSON?first_data_array_url=' +
            option_dict.first_data_array_url + '&second_data_array_url=' +
            option_dict.second_data_array_url +
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
                            label = "RRC Connection Request + UE Count" +
                              " vs Time CELL " +
                              Math.floor(key).toString(),
                            data = response[key];

                          return plotFromData(data, el, label);
                        });
                    }
                  );
                });
            });
            return plotContainerList;
          });
        }, function () {
          // On request error, show empty plots
          var plot = plotFromResponse(
            {},
            chart_element
          );
          gadget.element.querySelector('.ui-icon-spinner').hidden = true;
          return plot;
        });
    });
}(window, document, Math, rJS, RSVP, Plotly, URI, loopEventListener));

