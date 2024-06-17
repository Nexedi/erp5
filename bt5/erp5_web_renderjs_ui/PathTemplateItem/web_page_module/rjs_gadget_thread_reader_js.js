/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS, RSVP, console, domsugar, Intl, Query, SimpleQuery,
         ComplexQuery*/
(function (window, rJS, RSVP, console, domsugar, Intl, Query, SimpleQuery,
           ComplexQuery) {
  "use strict";

  function createMultipleSimpleOrQuery(key, value_list) {
    var i,
      query_list = [];
    if (!Array.isArray(value_list)) {
      value_list = [value_list];
    }
    for (i = 0; i < value_list.length; i += 1) {
      query_list.push(new SimpleQuery({
        key: key,
        operator: "=",
        type: "simple",
        value: value_list[i]
      }));
    }
    if (value_list.len === 1) {
      return query_list[0];
    }
    return new ComplexQuery({
      operator: "OR",
      query_list: query_list,
      type: "complex"
    });
  }

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
    if (abs > (week * 2)) {
      return time_format.format(Math.floor(diff / week), 'week');
    }
    if (abs > (day * 2)) {
      return time_format.format(Math.floor(diff / day), 'day');
    }
    if (abs > (hour * 2)) {
      return time_format.format(Math.floor(diff / hour), 'hour');
    }
    return time_format.format(Math.floor(diff / minute), 'minute');
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
        text: 'Page ' + Math.ceil((gadget.state.begin_from + count) / gadget.state.lines)
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
            query_string: Query.objectToSearchText(
              new ComplexQuery({
                operator: "AND",
                type: "complex",
                query_list: Object.entries(options.query_dict)
                                  .map(function (tuple) {
                    return createMultipleSimpleOrQuery(tuple[0], tuple[1]);
                  })
              })
            ),
            begin_from: parseInt(result_dict.begin_from || '0', 10) || 0,
            lines: options.lines || 1,
            date_column: options.date_column || 'modification_date',
            source_column: options.source_column || 'source_title',
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

      if (!gadget.state.query_string) {
        throw new Error('No "query_dict" defined for ' + gadget.state.key);
      }

      if (modification_dict.hasOwnProperty('first_render')) {
        setPaginationElement(gadget, 0, []);
      }

      if (modification_dict.hasOwnProperty('render_timestamp')) {
        domsugar(gadget.element.querySelector(':scope > nav > span'), {
          class: "ui-icon-spinner ui-btn-icon-left",
          text: ''
        });
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
            var now = new Date();
            domsugar(gadget.element.querySelector(':scope > ol'),
                     allDocs_result.data.rows.map(function (entry, i) {
                if (i === gadget.state.lines) {
                  // Drop the last lines, in case we reached the +1 post value
                  // from allDocs, used to activate the pagination
                  return '';
                }
                var source_title = entry.value[gadget.state.source_column] || '',
                  attachment_list = entry.value
                                         .Event_getAttachmentList || [],
                  attachment_element_list = [],
                  j,
                  word_list = source_title.split(' '),
                  source_short_title;

                if (word_list.length === 1) {
                  source_short_title = (word_list[0][0] || '?') + (word_list[0][1] || '');
                } else {
                  source_short_title = word_list[0][0] + word_list[1][0];
                }

                for (j = 0; j < attachment_list.length; j += 1) {
                  attachment_element_list.push(
                    domsugar('li', [
                      domsugar('a', {
                        text: attachment_list[j].title,
                        href: attachment_list[j].url,
                        download: attachment_list[j].title
                      }),
                      ' (',
                      attachment_list[j].content_type || 'attachment/octet-stream',
                      ')'
                    ])
                  );
                }

                return domsugar('li', [
                  domsugar('div', {
                    class: 'post_avatar',
                    text: source_short_title
                  }),
                  domsugar('div', {
                    class: 'post_content'
                  }, [
                    domsugar('strong', {text: source_title}),
                    " ",
                    domsugar('time', {
                      datetime: entry.value[gadget.state.date_column],
                      title: entry.value[gadget.state.date_column],
                      text: getRelativeTimeString(
                        gadget.state.language,
                        now,
                        new Date(entry.value[gadget.state.date_column])
                      )
                    }),
                    domsugar('br'),
                    result_dict.viewer_list[i].element,
                    domsugar('br'),
                    domsugar('ul', attachment_element_list)
                    // domsugar('hr')
                  ])
                ]);
              }));
            setPaginationElement(gadget, allDocs_result.data.total_rows,
                                 result_dict.url_list);
          });
      }
    })

    .onLoop(function () {
      // update relative time
      var now = new Date(),
        gadget = this;
      this.element.querySelectorAll("div.post_content > time").forEach(
        function (element) {
          element.textContent = getRelativeTimeString(
            gadget.state.language,
            now,
            new Date(element.getAttribute('datetime'))
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
        limit_options = [];

      if (gadget.state.lines === 0) {
        limit_options = undefined;
      } else {
        limit_options = [gadget.state.begin_from, gadget.state.lines + 1];
      }

      return gadget.jio_allDocs({
        query: gadget.state.query_string,
        limit: limit_options,
        select_list: ['asStrippedHTML', gadget.state.date_column,
                      gadget.state.source_column,
                      'Event_getAttachmentList'],
        sort_on: [[gadget.state.date_column, 'ASC'], ['uid', 'ASC']]
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

}(window, rJS, RSVP, console, domsugar, Intl, Query, SimpleQuery,
  ComplexQuery));
