/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, document, rJS, URI, RSVP, isEmpty, console, domsugar*/
(function () {
  "use strict";

  var variable = {},
    loading_class_list = ['ui-icon-spinner', 'ui-btn-icon-left'],
    disabled_class = 'ui-disabled';

  function getRelativeTimeString(language, current_date, date) {
    var diff,
      abs,
      second = 1000,
      minute = second * 60,
      hour = minute * 60,
      day = hour * 24,
      week = day * 7,
      time_format = new Intl.RelativeTimeFormat(language);

    diff = date.getFullYear() - current_date.getFullYear();
    if (diff !== 0) {
      return time_format.format(diff, 'year');
    }

    diff = date - current_date;
    abs = Math.abs(diff);
    // "year", "quarter", "month", "week", "day", "hour", "minute", "second"
    console.log(current_date, date, abs, week, day);
    if (abs > (week * 2)) {
      return time_format.format(Math.floor(diff / week), 'week');
    } else if (abs > (day * 2)) {
      return time_format.format(Math.floor(diff / day), 'day');
    } else if (abs > (hour * 2)) {
      return time_format.format(Math.floor(diff / hour), 'hour');
    } else {
      return time_format.format(Math.floor(diff / minute), 'minute');
    }
    return date;
  }

  function buildFieldGadgetParam(value) {
    var field_gadget_param;

    if ((value !== undefined) && (value !== null) && (value.constructor === Object)) {
      if (value.field_gadget_param) {
        field_gadget_param = value.field_gadget_param;
      } else {
        field_gadget_param = {
          'editable': 0,
          'default': value.default
        };
      }
    } else {
      field_gadget_param = {
        'editable': 0,
        'default': value
      };
    }

    return field_gadget_param;
  }

  function setPaginationElement(gadget, count, url_list) {
    var disabled_suffix = ' ui-disabled',
      span_dict,
      first_dict = {
        class: "ui-btn ui-icon-angle-double-left ui-btn-icon-left responsive ui-first-child",
        text: "First"
      },
      previous_dict = {
        class: "ui-btn ui-icon-angle-left ui-btn-icon-left responsive",
        text: "Previous"
      },
      next_dict = {
        class: "ui-btn ui-icon-angle-right ui-btn-icon-right responsive ui-last-child",
        text: "Next"
      };

    if (url_list.length === 0) {
      span_dict = {
        class: "ui-icon-spinner ui-btn-icon-left"
      };
    } else {
      span_dict = {
        text: 'Page ' + Math.floor((gadget.state.begin_from + count) / gadget.state.lines)
      };
    }

    console.warn(gadget.state);
    if (gadget.state.begin_from === 0) {
      first_dict.class += disabled_suffix;
      previous_dict.class += disabled_suffix;
    } else {
      first_dict.href = url_list[0];
      previous_dict.href = url_list[1];
    }

    if (gadget.state.lines < count) {
      next_dict.href = url_list[2];
    } else {
      next_dict.class += disabled_suffix;
    }

    // Set the pagination elements
    domsugar(gadget.element.querySelector(':scope > nav'), [
      domsugar('a', first_dict),
      domsugar('a', previous_dict),
      domsugar('a', next_dict),
      domsugar('span', span_dict)
    ]);
  }

  rJS(window)
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod('getSelectedLanguage', 'getSelectedLanguage')

    //////////////////////////////////////////////
    // initialize the gadget content
    //////////////////////////////////////////////
    .declareMethod('render', function render(options) {
      console.log(options);
      var gadget = this;

      // Cancel previous line rendering to not conflict with the asynchronous render for now
      gadget.fetchLineContent(true);

      return new RSVP.Queue(RSVP.hash({
        language: gadget.getSelectedLanguage(),
        begin_from: gadget.getUrlParameter(options.key + '_begin_from')
      }))
        .push(function (result_dict) {
          return gadget.changeState({
            key: options.key,
            language: result_dict.language,
            query_string: new URI(options.query).query(true).query || '',
            begin_from: parseInt(result_dict.begin_from || '0', 10) || 0,
            lines: options.lines || 1,
            // Force line calculation in any case
            render_timestamp: new Date().getTime(),
            first_render: true,
            allDocs_result: undefined
          });
        });
    })

    .onStateChange(function onStateChange(modification_dict) {
      var gadget = this,
        allDocs_result,
        first_param,
        prev_param,
        next_param,
        pagination_key;
      console.log(gadget.state, modification_dict);

      if (modification_dict.hasOwnProperty('first_render')) {
        setPaginationElement(gadget, 0, []);
      }

      if (modification_dict.hasOwnProperty('render_timestamp')) {
        domsugar(gadget.element.querySelector(':scope > nav > span'), {
          class: "ui-icon-spinner ui-btn-icon-left",
          text: ''
        })
        return gadget.fetchLineContent(false);
      }

      if (modification_dict.hasOwnProperty('allDocs_result')) {
        allDocs_result = JSON.parse(gadget.state.allDocs_result);
        pagination_key = gadget.state.key + '_begin_from';
        first_param = {};
        first_param[pagination_key] = undefined;
        prev_param = {};
        prev_param[pagination_key] = Math.max(0, gadget.state.begin_from - gadget.state.lines) || undefined;
        next_param = {};
        next_param[pagination_key] = gadget.state.begin_from + gadget.state.lines;

        return new RSVP.Queue(RSVP.hash({
          viewer_list: RSVP.all(allDocs_result.data.rows.map(function (entry, i) {
            if (i === gadget.state.lines) {
              return;
            }
            return gadget.declareGadget('gadget_html_viewer.html')
              .push(function (viewer) {
                return viewer.render({value: entry.value.asStrippedHTML})
                  .push(function () {
                    return viewer;
                  });
              });
          })),
          url_list: gadget.getUrlForList([
            {command: 'change', options: first_param},
            {command: 'change', options: prev_param},
            {command: 'change', options: next_param}
          ])
        }))
          .push(function (result_dict) {
            console.log(result_dict);
            var now = new Date();
            domsugar(gadget.element.querySelector(':scope > ol'),
                     allDocs_result.data.rows.map(function (entry, i) {
                if (i === gadget.state.lines) {
                  return '';
                }
                var source_title = entry.value.source_title || '',
                  word_list = source_title.split(' '),
                  source_short_title;
                if (word_list.length === 1) {
                  source_short_title = (word_list[0][0] || '?') + (word_list[0][1] || '');
                } else {
                  source_short_title = word_list[0][0] + word_list[1][0];
                }
                return domsugar('li', [
                  domsugar('div', {
                    class: 'post_avatar',
                    text: source_short_title
                  }),
                  domsugar('div', {
                    class: 'post_content',
                  }, [
                    domsugar('strong', {text: source_title}),
                    " ",
                    domsugar('time', {
                      datetime: entry.value.modification_date,
                      title: entry.value.modification_date,
                      text: getRelativeTimeString(
                        gadget.state.language, now, new Date(entry.value.modification_date)
                      )
                    }),
                    domsugar('br'),
                    result_dict.viewer_list[i].element,
                    // domsugar('hr')
                  ])
                ]);
              }));
            setPaginationElement(gadget, allDocs_result.data.total_rows, result_dict.url_list);
          });
        return;
      }
    })

    .onLoop(function () {
      // update relative time
      var now = new Date(),
        gadget = this;
      this.element.querySelectorAll("div.post_content > time").forEach(
        function (element) {
          element.textContent = getRelativeTimeString(
            gadget.state.language, now, new Date(element.getAttribute('datetime'))
          );
        }
      );
      // Loop every minute
    }, 1000 * 60)

    //////////////////////////////////////////////
    // render the listbox in an asynchronous way
    //////////////////////////////////////////////
    .declareJob('fetchLineContent', function fetchLineContent(only_cancel) {
      if (only_cancel) {
        return;
      }

      var gadget = this,
        limit_options = [],
        i;

      if (gadget.state.lines === 0) {
        limit_options = undefined;
      } else {
        limit_options = [gadget.state.begin_from, gadget.state.lines + 1];
      }

      return gadget.jio_allDocs({
        query: gadget.state.query_string,
        limit: limit_options,
        select_list: ['asStrippedHTML', 'modification_date',
                      'source_title'],
        sort_on: [['modification_date', 'ASC'], ['uid', 'ASC']]
      })
        .push(function (result) {
          return gadget.changeState({
            allDocs_result: JSON.stringify(result)
          });
        });
    })

    .declareMethod("getContent", function getContent() {
      return {};
    })

    .declareMethod("checkValidity", function checkValidity() {
      return true;
    });

}());
