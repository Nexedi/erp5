/*globals window, document, RSVP, rJS, jIO, Handlebars, LZString*/
/*jslint indent: 2, maxlen: 80*/
/*jslint nomen: true*/
(function (window, document, RSVP, rJS, jIO, Handlebars, LZString) {
  "use strict";

  /////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////
  var day_list_template = Handlebars.compile(
    document.getElementById('day_list_template').innerHTML
  ), day_form_template = Handlebars.compile(
    document.getElementById('day_form_template').innerHTML
  ), share_template = Handlebars.compile(
    document.getElementById('share_template').innerHTML
  ), import_form_template = Handlebars.compile(
    document.getElementById('import_form_template').innerHTML
  ), result_template = Handlebars.compile(
    document.getElementById('result_template').innerHTML
  ),
    MY_BET_ID = 'my_wc2018_bet',
    CODE_DICT_ID = 'wc2018_code_dict';

  /////////////////////////////////////////////////////////////
  // JSON Parser
  /////////////////////////////////////////////////////////////
  function WorldCup2018Parser(txt) {
    this._parser = JSON.parse(txt);
  }

  WorldCup2018Parser.prototype.getDocumentList = function () {
    var result_list = [],
      i,
      key,
      tmp,
      team_dict = {};

    // Parse teams
    for (i = this._parser.teams.length; i > 0; i -= 1) {
      tmp = this._parser.teams[i - 1];
      result_list.push({
        id: 'team_' + tmp.id,
        value: {},
        doc: {
          portal_type: 'World Cup 2018 Team',
          title: tmp.name,
          short_title: tmp.emojiString
        }
      });
      team_dict[tmp.id] = tmp.name;
    }

    // Parse groups
    for (key in this._parser.groups) {
      if (this._parser.groups.hasOwnProperty(key)) {
        // Group document
        result_list.push({
          id: 'group_' + this._parser.groups[key].name.slice(-1),
          value: {},
          doc: {
            portal_type: 'World Cup 2018 Group',
            title: this._parser.groups[key].name
          }
        });
        // Match documents
        for (i = this._parser.groups[key].matches.length; i > 0; i -= 1) {
          tmp = this._parser.groups[key].matches[i - 1];
          result_list.push({
            id: 'match_' + tmp.name,
            value: {},
            doc: {
              portal_type: 'World Cup 2018 Match',
              group_match: true,
              start_date: tmp.date,
              home_team: tmp.home_team,
              home_team_title: team_dict[tmp.home_team],
              home_result: tmp.home_result,
              away_team: tmp.away_team,
              away_team_title: team_dict[tmp.away_team],
              away_result: tmp.away_result,
              finished: tmp.finished,
              title: team_dict[tmp.home_team] + ' / ' + team_dict[tmp.away_team]
            }
          });
        }
      }
    }

/*
    // Parse knockout
    for (key in this._parser.knockout) {
      if (this._parser.knockout.hasOwnProperty(key)) {
        // Group document
        result_list.push({
          id: 'knockout_' + this._parser.knockout[key],
          value: {},
          doc: {
            portal_type: 'World Cup 2018 Knockout',
            title: this._parser.knockout[key].name
          }
        });
        // Match documents
        for (i = this._parser.knockout[key].matches.length; i > 0; i -= 1) {
          tmp = this._parser.knockout[key].matches[i - 1];
          result_list.push({
            id: 'match_' + tmp.name,
            value: {},
            doc: {
              portal_type: 'World Cup 2018 Match',
              start_date: tmp.date,
              title: tmp.name
            }
          });
        }
      }
    }
*/
    return result_list;
  };

  /////////////////////////////////////////////////////////////
  // Helpers
  /////////////////////////////////////////////////////////////
  function getParser(storage) {
    if (storage._parser === undefined) {
      return storage._sub_storage.getAttachment(storage._document_id,
                                                storage._attachment_id,
                                                {format: 'text'})
        .push(function (txt) {
          storage._parser = new WorldCup2018Parser(txt);
          return storage._parser;
        });
    }
    return new RSVP.Queue()
      .push(function () {
        return storage._parser;
      });
  }

  /////////////////////////////////////////////////////////////
  // Storage (ParserStorage clone)
  /////////////////////////////////////////////////////////////
  function WorldCupStorage(spec) {
    this._attachment_id = spec.attachment_id;
    this._document_id = spec.document_id;
    this._parser_name = 'world_cup_2018';
    this._sub_storage = jIO.createJIO(spec.sub_storage);
  }

  WorldCupStorage.prototype.hasCapacity = function (capacity) {
    return (capacity === "list") || (capacity === 'include');
  };

  WorldCupStorage.prototype.buildQuery = function (options) {
    if (options === undefined) {
      options = {};
    }
    return getParser(this)
      .push(function (parser) {
        return parser.getDocumentList((options.include_docs || false));
      });
  };

  WorldCupStorage.prototype.get = function (id) {
    return getParser(this)
      .push(function (parser) {
        var result_list = parser.getDocumentList(),
          i;
        for (i = result_list.length; i > 0; i -= 1) {
          if (id === result_list[i - 1].id) {
            return result_list[i - 1].doc;
          }
        }
        throw new jIO.util.jIOError(
          "Cannot find parsed document: " + id,
          404
        );
      });
  };

  jIO.addStorage('world_cup_data', WorldCupStorage);

  /////////////////////////////////////////////////////////////
  // Gadget helpers
  /////////////////////////////////////////////////////////////
  function isSameDay(d1, d2) {
    return d1.getFullYear() === d2.getFullYear() &&
      d1.getMonth() === d2.getMonth() &&
      d1.getDate() === d2.getDate();
  }

  function parseForm(form) {
    var form_data = {},
      i,
      len = form.elements.length;
    for (i = 0; i < len; i += 1) {
      if (form.elements[i].hasAttribute('name')) {
        form_data[form.elements[i].name] = form.elements[i].value;
      }
    }
    return form_data;
  }

  /////////////////////////////////////////////////////////////
  // Gadget
  /////////////////////////////////////////////////////////////
  rJS(window)
    .ready(function initJio() {
      this._storage = jIO.createJIO({
        type: 'replicate',
        check_local_modification: false,
        check_local_creation: false,
        check_local_deletion: false,
        local_sub_storage: {
          type: 'query',
          sub_storage: {
            // type: 'memory'
            type: "indexeddb",
            database: "world_cup_2018"
          }
        },
        signature_sub_storage: {
          type: 'query',
          sub_storage: {
            // type: 'memory'
            type: "indexeddb",
            database: "world_cup_2018_hash"
          }
        },
        remote_sub_storage: {
          type: 'world_cup_data',
          // document_id: 'world_cup_2018_data.json',
          document_id: 'https://raw.githubusercontent.com/lsv/' +
                       'fifa-worldcup-2018/master/data.json',
          attachment_id: 'enclosure',
          sub_storage: {
            type: 'http'
          }
        }
      });
    })

    .declareMethod('getBet', function getBet() {
      var gadget = this;
      return gadget._storage.get(MY_BET_ID)
        .push(undefined, function (error) {
          if ((error instanceof jIO.util.jIOError) &&
              (error.status_code === 404)) {
            return {
              portal_type: 'World Cup 2018 Bet'
            };
          }
          throw error;
        });
    })

    .declareMethod('updateBet', function updateBet(new_doc) {
      var gadget = this;
      return gadget.getBet()
        .push(function (doc) {
          var key;
          for (key in new_doc) {
            if (new_doc.hasOwnProperty(key)) {
              doc[key] = new_doc[key];
            }
          }
          return gadget._storage.put(MY_BET_ID, doc);
        });
    })

    .declareMethod('getCodeDict', function getCodeDict() {
      var gadget = this;
      return gadget._storage.get(CODE_DICT_ID)
        .push(function (doc) {
          return doc.code_dict;
        }, function (error) {
          if ((error instanceof jIO.util.jIOError) &&
              (error.status_code === 404)) {
            return {};
          }
          throw error;
        });
    })

    .declareMethod('updateCodeDict', function updateBet(new_code_dict) {
      var gadget = this;
      return gadget._storage.put(CODE_DICT_ID, {
        portal_type: 'World Cup 2018 Code Dict',
        code_dict: new_code_dict
      });
    })

    .declareService(function startApplication() {
      var gadget = this;
      // First, copy all JSON data into memory
      return gadget._storage.repair()
        .push(function () {
          return gadget.renderCalendar();
        });
    })

    .declareMethod('renderCalendar', function renderLauncher() {
      var gadget = this;
      return gadget._storage.allDocs({
        query: 'portal_type:"World Cup 2018 Match"',
        select_list: ['portal_type', 'start_date', 'home_team', 'title'],
        sort_on: [['start_date', 'ascending'], ['title', 'ascending']]
      })
        .push(function (result) {
          var i,
            length = result.data.rows.length,
            match,
            date,
            day_count,
            previous_date = null,
            calendar_list = [];
          for (i = 0; i < length; i += 1) {
            match = result.data.rows[i].value;
            date = new Date(match.start_date);

            if (previous_date === null) {
              day_count = 1;
              calendar_list = [{
                day_string: date.toLocaleDateString(),
                day_count: day_count,
                day_query: match.start_date.substr(0, 10),
                match_list: [match]
              }];
            } else if (!isSameDay(date, previous_date)) {
              day_count += 1;
              // XXX check day diff?
              calendar_list.push({
                day_string: date.toLocaleDateString(),
                day_query: match.start_date.substr(0, 10),
                day_count: day_count,
                match_list: [match]
              });
            } else {
              calendar_list[calendar_list.length - 1].match_list.push(match);
            }
            previous_date = date;
          }
          gadget.element.querySelector('main').innerHTML = day_list_template({
            day_list: calendar_list
          });
        });
    })


    .declareMethod('renderCard', function renderLauncher(day_query) {
      var gadget = this,
        date = new Date(day_query),
        bet;
      return gadget.getBet()
        .push(function (result) {
          bet = result;
          return gadget._storage.allDocs({
            query: 'portal_type:"World Cup 2018 Match" AND ' +
                   'start_date:"' + day_query + '%"',
            select_list: ['portal_type', 'start_date', 'title',
                          'home_team_title', 'away_team_title'],
            sort_on: [['start_date', 'ascending'], ['title', 'ascending']]
          });
        })
        .push(function (result) {
          var i,
            length = result.data.rows.length,
            match_list = [],
            match;
          for (i = 0; i < length; i += 1) {
            match = result.data.rows[i].value;
            match.home_bet_reference = result.data.rows[i].id + '_A';
            match.away_bet_reference = result.data.rows[i].id + '_B';
            // init to 0
            match.home_bet = bet[match.home_bet_reference] || 0;
            match.away_bet = bet[match.away_bet_reference] || 0;
            match.home_bet_title = match.home_team_title;
            match.away_bet_title = match.away_team_title;
            match_list.push(result.data.rows[i].value);
          }
          gadget.element.querySelector('main').innerHTML = day_form_template({
            day_string: date.toLocaleDateString(),
            match_list: match_list
          });
        });
    })

    .declareMethod('renderExport', function renderExport() {
      var gadget = this,
        match_list;
      return gadget._storage.allDocs({
        query: 'portal_type:"World Cup 2018 Match" AND ' +
               'group_match: true',
        select_list: ['start_date'],
        sort_on: [['start_date', 'ascending'], ['title', 'ascending']]
      })
        .push(function (result) {
          match_list = result.data.rows;
          return gadget.getBet();
        })
        .push(function (doc) {
          var i,
            j,
            result = '',
            key,
            suffix_list = ['_A', '_B'];
          for (i = 0; i < match_list.length; i += 1) {
            for (j = 0; j < suffix_list.length; j += 1) {
              key = 'match_' + (i + 1) + suffix_list[j];
              if ((!doc.hasOwnProperty(key)) ||
                  (parseInt(doc[key], 10) > 15)) {
                // Bet between 0 and 15
                return gadget.renderCard(match_list[i].value
                                           .start_date.substr(0, 10));
              }
              result += parseInt(doc[key], 10).toString(16);
            }
          }
          gadget.element.querySelector('main').innerHTML = share_template({
            code: LZString.compressToBase64(result)
          });
        });
    })


    .declareMethod('renderImport', function renderExport() {
      var gadget = this;
      return gadget.getCodeDict()
        .push(function (code_dict) {
          var key,
            import_string = '';
          for (key in code_dict) {
            if (code_dict.hasOwnProperty(key)) {
              import_string += '\n' + key + ' | ' + code_dict[key];
            }
          }
          gadget.element.querySelector('main').innerHTML =
            import_form_template({password_text: import_string});
        });
    })

    .declareMethod('renderResult', function renderExport() {
      var gadget = this,
        match_list;
      return gadget._storage.allDocs({
        query: 'portal_type:"World Cup 2018 Match" AND finished:true AND ' +
               'group_match: true',
        select_list: ['start_date', 'home_result', 'away_result',
                      'home_team_title', 'away_team_title', 'title'],
        sort_on: [['start_date', 'ascending'], ['title', 'ascending']]
      })
        .push(function (result) {
          match_list = result.data.rows;
          return gadget.getCodeDict();
        })
        .push(function (code_dict) {
          // First, decode all codes
          var key,
            i,
            result_list,
            player_list = [],
            score_list = [],
            score,
            home_result,
            away_result,
            home_bet,
            away_bet,
            key_count = 0,
            decoded;
          for (key in code_dict) {
            if (code_dict.hasOwnProperty(key)) {
              key_count += 1;
              result_list = [];
              decoded = LZString.decompressFromBase64(code_dict[key]);
              for (i = 0; i < decoded.length; i += 1) {
                result_list.push(parseInt(decoded[i], 16));
              }
              code_dict[key] = {
                result_list: result_list,
                score: 0
              };
            }
          }
          if (!key_count) {
            return gadget.renderImport();
          }

          // Check match result
          for (i = 0; i < match_list.length; i += 1) {
            home_result = match_list[i].value.home_result;
            away_result = match_list[i].value.away_result;
            for (key in code_dict) {
              if (code_dict.hasOwnProperty(key)) {
                // console.log(match_list[i]);
                home_bet = code_dict[key].result_list[2 * (parseInt(match_list[i].id.slice(6), 10) - 1)];
                away_bet = code_dict[key].result_list[2 * (parseInt(match_list[i].id.slice(6), 10) - 1) + 1];
                if ((home_result === home_bet) &&
                    (away_result === away_bet)) {
                  // Correct score!
                  console.log('score', home_bet, away_bet, match_list[i].value.title, home_result, away_result);
                  score = 4;
                } else if (((home_result > away_result) &&
                            (home_bet > away_bet)) ||
                           ((home_result === away_result) &&
                            (home_bet === away_bet)) ||
                           ((home_result < away_result) &&
                            (home_bet < away_bet))) {
                  // Found correct winner
                  console.log('guess', home_bet, away_bet, match_list[i].value.title, home_result, away_result);
                  score = 2;
                } else {
                  // Be nice, and always give a point
                  console.log('loser', home_bet, away_bet, match_list[i].value.title, home_result, away_result);

                  score = 1;
                }
                code_dict[key].score += score;
                /*
                if (i === 0) {
                  player_list.push({
                    name: key,
                    score: score
                  });
                }
                */

              }
            }
          }

          // Render player list
          for (key in code_dict) {
            if (code_dict.hasOwnProperty(key)) {
              player_list.push({
                name: key,
                score: code_dict[key].score
              });
            }
          }
          player_list.sort(function (a, b) {
            return b.score - a.score;
          });
          for (i = 0; i < player_list.length; i += 1) {
            if ((i === 0) ||
                (player_list[i].score !== player_list[i - 1].score)) {
              score_list.push({
                name: player_list[i].name,
                score: player_list[i].score
              });
            } else {
              score_list[score_list.length - 1].name +=
                ', ' + player_list[i].name;
            }
          }
          // console.log(code_dict);
          gadget.element.querySelector('main').innerHTML = result_template({
            player_list: score_list,
            match_count: match_list.length
          });
        });
    })

    .onEvent('click', function trapClickEvent(evt) {
      // Use click bubble
      var button_parent = evt.target.closest('button[data-wc2018]');
      if (button_parent !== null) {
        evt.preventDefault();
        return this[button_parent.getAttribute('data-wc2018')](
          button_parent.getAttribute('data-wc2018-param')
        );
      }
    }, false, false)

    .declareMethod('submitBet', function submitBet(evt) {
      var gadget = this;
      return gadget.updateBet(parseForm(evt.target))
        .push(function () {
          return gadget.renderExport();
        });
    })

    .declareMethod('submitNewCode', function submitNewCode(evt) {
      var gadget = this;
      return gadget.getCodeDict()
        .push(function (code_dict) {
          var parsed_form = parseForm(evt.target),
            // Ensure code can be decoded/parsed
            decoded = LZString.decompressFromBase64(parsed_form.code);
          if (decoded) {
            code_dict[parsed_form.player] = parsed_form.code;
            return gadget.updateCodeDict(code_dict)
              .push(function () {
                return gadget.renderImport();
              });
          }
        });
    })

    .declareMethod('submitImport', function submitImport(evt) {
      var parsed_form = parseForm(evt.target),
        password_text = parsed_form.password_text,
        line_list = password_text.split('\n'),
        sub_list,
        code_dict = {},
        i,
        gadget = this;
      for (i = 0; i < line_list.length; i += 1) {
        sub_list = line_list[i].split(' | ');
        code_dict[sub_list[0]] = sub_list[1];
      }
      return gadget.updateCodeDict(code_dict)
        .push(function () {
          return gadget.renderResult();
        });
    })

    .onEvent('submit', function trapSubmitEvent(evt) {
      evt.preventDefault();
      var form_parent = evt.target.closest('form[data-wc2018]');
      if (form_parent !== null) {
        return this[form_parent.getAttribute('data-wc2018')](evt);
      }
    });


}(window, document, RSVP, rJS, jIO, Handlebars, LZString));