/*global window, rJS*/
/*jslint maxlen:80*/
(function (rJS, RSVP) {
  "use strict";

  var wickedGrid = function (el, settings) {
    settings = settings || {};

    for (var p in WickedGrid.defaults) {
      if (WickedGrid.defaults.hasOwnProperty(p)) {
        settings[p] = settings.hasOwnProperty(p) ? settings[p] : WickedGrid.defaults[p];
      }
    }


    var element = el,
      $element = $(el),
      instance = $element.getWickedGrid();

    settings.useStack = (window.thaw === undefined ? false : settings.useStack);
    settings.useMultiThreads = (window.operative === undefined ? 
                                false : settings.useMultiThreads);

    //destroy already existing spreadsheet
    if (instance) {
      var tables = $element.children().detach();
      instance.kill();
      $element.html(tables);

      WickedGrid.events.forEach($element.unbind);
    }

    settings.element = element;
    settings.$element = $element;

    WickedGrid.events.forEach(function(event) {
      $element.bind(event, settings[event]);
    });

    $element.children().each(function(i) {
      // override frozenAt settings with table's data-frozenatrow 
      // and data-frozenatcol
      var frozenAtRow = el.getAttribute('data-frozenatrow') * 1,
          frozenAtCol = el.getAttribute('data-frozenatcol') * 1;

      if (!settings.frozenAt[i]) {
        settings.frozenAt[i] = {row:0, col:0};
      }
      if (frozenAtRow) {
        settings.frozenAt[wickedGrid.i].row = frozenAtRow;
      }
      if (frozenAtCol) {
        settings.frozenAt[wickedGrid.i].col = frozenAtCol;
      }
    });

    var wickedGrid = new WickedGrid(settings);

    return wickedGrid;
  };
  
  function tablify (rows, cols) {
		var table = document.createElement('table'),
			tr,
			td,
			rowIndex=0,
			colIndex=0,
			tbody = table.appendChild(document.createElement('tbody'));

		while (rowIndex < rows ) {
			tr = document.createElement('tr');
			tbody.appendChild(tr);
			while (colIndex < cols) {
				td = document.createElement('td');
				tr.appendChild(td);
				colIndex++;
			}
			colIndex = 0;
			rowIndex++;
		}
		return table;
  }

  function parseHtml (gadget, html, selector) {
		var parent = document.createElement('div');
		if (html === '') {
      html = tablify(10,6);
      parent.innerHTML = html.outerHTML;
		} else {
      parent.innerHTML = html;
		}

		if (selector) {
      gadget.props.element.querySelector(selector).innerHTML = parent.outerHTML;
      return parent.children;
		}
		return parent.children;
	}

  function initiate (gadget, sheetGet) {
    var url = 'jquery-sheets/menu.html';
    $.when($.get(url))
      .always(function(nav_menu) {
        if (!nav_menu.status) {
          //clearTimeout(noResponseTimer);
          localStorage[url] = nav_menu;
        }
        else {
          if (!!localStorage[url]) {
            nav_menu = localStorage[url];
          }
        }

        var jS = $('#jquery_sheet_gadget')
						.html(parseHtml(gadget, sheetGet, 'div#sheetParent'));
					var wg = wickedGrid(jS[0], {
							theme: WickedGrid.bootstrapTheme,
							title: '',
							height: '600px',
							headerMenu: function(wg) {
								var menu = $(nav_menu);
								wg.saveSheet = function () {
                  return gadget.submitContent();
                }
                menu.find('a').each(function() {
									this.wickedGrid = wg;
								});
								if (menu.is('ul')) {
									menu
										.find("ul").hide()
										.addClass(wg.theme.menuUl);

									menu.find("li")
										.addClass(wg.theme.menuLi)
										.hover(function () {
											$(this).find('ul:first')
												.hide()
												.show();
											}, function () {
											$(this).find('ul:first')
														.hide();
										});
								}

								return menu;
							}
					});
					gadget.props.wickedGrid = wg;
      });

    $('td').click(function() {
      window.focus();
    });

		return;
	}

  rJS(window)
    .ready(function (g) {
      g.props = {};
    })
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          var textarea = element.querySelector('textarea');
          g.props.element = element;
        });
    })
    .declareAcquiredMethod("submitContent", "triggerSubmit")
    .declareAcquiredMethod("maximize", "triggerMaximize")
    .declareMethod('render', function (options) {
      var gadget = this;
      this.props.key = options.key || "text_content";
      return new RSVP.Queue()
        .push(function(nav_menu) {
          initiate(gadget, options.value || '');
          return {};
        });
    })
    .declareMethod('getContent', function () {
      var result = {},
          value,
          tables = this.props.wickedGrid.loader.toTables();
      for (var table in tables) {
        if (tables[table].textContent) {
          value = result[this.props.key] || '';
          result[this.props.key] = value + tables[table].outerHTML;
        }
      }
      return result;
    });

}(rJS, RSVP));