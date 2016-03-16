(function(a) {
    a.alerts = {
        verticalOffset: -75,
        horizontalOffset: 0,
        repositionOnResize: true,
        overlayOpacity: 0.50,
        overlayColor: "#FFF",
        draggable: true,
        okButton: "OK",
        cancelButton: "Cancel",
        dialogClass: null,
        alert: function(b, c, d) {
            if (c == null) {
                c = "OK"
            }
            a.alerts._show(c, b, null, "alert",
      function(e) {
          if (d) {
              d(e)
          }
      },
      null, null, null, null)
        },
        confirm: function(b, c, d) {
            if (c == null) {
                c = "Are you sure"
            }
            a.alerts._show(c, b, null, "confirm",
      function(e) {
          if (d) {
              d(e)
          }
      },
      null, null, null, null)
        },
        prompt: function(b, c, d, e) {
            if (d == null) {
                d = "Please enter something"
            }
            a.alerts._show(d, b, c, "prompt",
      function(f) {
          if (e) {
              e(f)
          }
      },
      null, null, null, null)
        },
        openBox: function(f, g, b, c, e, d, i) {
            if (g == null) {
                g = "Information"
            }
            a.alerts._show(g, f, null, "openBox",
      function(h) {
          if (i) {
              i(h)
          }
      },
      b, c, e, d)
        },
        overAlert: function(c, b) {
            a.alerts._overShow(c, b)
        },
        _overShow: function(d, c) {
            if (c == null) {
                c = 3000
            }
            var b = c + 600;
            a("body").append('<div id="over_container" style="display:none"><div id="over_message"></div></div>');
            a("#over_message").text(d).html(a("#over_message").text().replace(/\n/g, "<br />"));
            if (a.alerts.dialogClass) {
                a("#over_container").addClass(a.alerts.dialogClass)
            }
            var e = (a.browser.msie && parseInt(a.browser.version) <= 6) ? "absolute" : "fixed";
            a("#over_container").css({
                position: e,
                zIndex: 99999,
                width: 350,
                padding: 0,
                margin: 0
            }).show("fast");
            a("#over_container").css({
                minWidth: a("#over_container").outerWidth(),
                maxWidth: a("#over_container").outerWidth()
            });
            a.alerts._overReposition();
            setTimeout(function() {
                a("#over_container").hide("fast")
            },
      c);
            setTimeout(function() {
                a("#over_container").remove()
            },
      b)
        },
        _overReposition: function() {
            var c = 4;
            var b = ((a(window).width() / 2) - (a("#over_container").outerWidth() / 2)) + a.alerts.horizontalOffset;
            if (c < 0) {
                c = 0
            }
            if (b < 0) {
                b = 0
            }
            if (a.browser.msie && parseInt(a.browser.version) <= 6) {
                c = c + a(window).scrollTop()
            }
            if (a.browser.msie && parseInt(a.browser.version) <= 6) {
                b = b - 175
            }
            a("#over_container").css({
                top: c + "px",
                left: b + "px"
            });
            a("#popup_overlay").height(a(document).height())
        },
        _show: function(j, b, k, g, m, l, c, f, n) {
            a.alerts._hide();
            a.alerts._overlay("show");
            a("body").append('<div id="popup_container" style="display:none"><h1 id="popup_title"></h1><em id="ctl"></em><em id="cbl"></em><em id="ctr"></em><em id="cbr"></em><span id="popup_close"></span><div id="popup_content"><div id="popup_message"></div></div></div>');
            if (a.alerts.dialogClass) {
                a("#popup_container").addClass(a.alerts.dialogClass)
            }
            var i = (a.browser.msie && parseInt(a.browser.version) <= 6) ? "absolute" : "fixed";
            a("#popup_container").css({
                position: i,
                zIndex: 99999,
                padding: 0,
                margin: 0
            }).show();
            a("#popup_title").text(j);
            a("#popup_content").addClass(g);
            if (g != "openBox") {
                a("#popup_message").text(b).html(a("#popup_message").text().replace(/\n/g, "<br />"))
            }
            a("#popup_container").css({});
            a.alerts._reposition();
            a.alerts._maintainPosition(true);
            switch (g) {
                case "alert":
                    a("#popup_message").after('<div id="popup_panel"><input type="button" value="' + a.alerts.okButton + '" id="popup_ok" /></div>');
                    a("#popup_ok").click(function() {
                        a.alerts._hide();
                        m(true)
                    });
                    a("#popup_ok").focus().keypress(function(h) {
                        if (h.keyCode == 13 || h.keyCode == 27) {
                            a("#popup_ok").trigger("click")
                        }
                    });
                    break;
                case "confirm":
                    a("#popup_message").after('<div id="popup_panel"><input type="button" value="' + a.alerts.okButton + '" id="popup_ok" /> <input type="button" value="' + a.alerts.cancelButton + '" id="popup_cancel" /></div>');
                    a("#popup_ok").click(function() {
                        a.alerts._hide();
                        if (m) {
                            m(true)
                        }
                    });
                    a("#popup_cancel").click(function() {
                        a.alerts._hide();
                        if (m) {
                            m(false)
                        }
                    });
                    a("#popup_ok").focus();
                    a("#popup_ok, #popup_cancel").keypress(function(h) {
                        if (h.keyCode == 13) {
                            a("#popup_ok").trigger("click")
                        }
                        if (h.keyCode == 27) {
                            a("#popup_cancel").trigger("click")
                        }
                    });
                    break;
                case "prompt":
                    a("#popup_message").append('<br /><input type="text" size="30" id="popup_prompt" />').after('<div id="popup_panel"><input type="button" value="' + a.alerts.okButton + '" id="popup_ok" /> <input type="button" value="' + a.alerts.cancelButton + '" id="popup_cancel" /></div>');
                    a("#popup_prompt").width(a("#popup_message").width() - 10);
                    a("#popup_ok").click(function() {
                        var e = a("#popup_prompt").val();
                        a.alerts._hide();
                        if (m) {
                            m(e)
                        }
                    });
                    a("#popup_cancel").click(function() {
                        a.alerts._hide();
                        if (m) {
                            m(null)
                        }
                    });
                    a("#popup_prompt, #popup_ok, #popup_cancel").keypress(function(h) {
                        if (h.keyCode == 13) {
                            a("#popup_ok").trigger("click")
                        }
                        if (h.keyCode == 27) {
                            a("#popup_cancel").trigger("click")
                        }
                    });
                    if (k) {
                        a("#popup_prompt").val(k)
                    }
                    a("#popup_prompt").focus().select();
                    break;
                case "openBox":
                    a("#popup_message").append(a(b).html());
                    if (l) {
                        a("#popup_container").css({
                            width:
            l + "px"
                        })
                    }
                    if (c) {
                        a("#popup_container").css({
                            height: c + "px"
                        });
                        a("#popup_message").css({
                            height: (c - 48) + "px"
                        })
                    }
                    a.alerts._reposition();
                    if (f) {
                        a(f).click(function() {
                            a.alerts._hide();
                            if (m) {
                                m(true)
                            }
                        })
                    }
                    if (n) {
                        a(n).click(function() {
                            a.alerts._hide();
                            return false;
                            if (m) {
                                m(false)
                            }
                        })
                    }
                    break
            }
            a("#popup_close").click(function() {
                a.alerts._hide();
                if (m) {
                    m()
                }
            });
            if (a.alerts.draggable) {
                try {
                    a("#popup_container").draggable({
                        handle: a("#popup_title")
                    });
                    a("#popup_title").css({
                        cursor: "move"
                    })
                } catch (d) { }
            }
        },
        _hide: function() {
            a("#popup_container").remove();
            a.alerts._overlay("hide");
            a.alerts._maintainPosition(false)
        },
        _overlay: function(b) {
            switch (b) {
                case "show":
                    a.alerts._overlay("hide");
                    a("BODY").append('<div id="popup_overlay"></div>');
                    a("#popup_overlay").css({
                        position:
          "absolute",
                        zIndex: 99998,
                        top: "0px",
                        left: "0px",
                        width: "100%",
                        height: a(document).height(),
                        background: a.alerts.overlayColor,
                        opacity: a.alerts.overlayOpacity
                    });
                    break;
                case "hide":
                    a("#popup_overlay").remove();
                    break
            }
        },
        _reposition: function() {
            var c = ((a(window).height() / 2) - (a("#popup_container").height() / 2)) + a.alerts.verticalOffset;
            var b = ((a(window).width() / 2) - (a("#popup_container").width() / 2)) + a.alerts.horizontalOffset;
            if (c < 0) {
                c = 0
            }
            if (b < 0) {
                b = 0
            }
            if (a.browser.msie && parseInt(a.browser.version) <= 6) {
                c = c + a(window).scrollTop()
            }
            a("#popup_container").css({
                top: c + "px",
                left: b + "px"
            });
            a("#popup_overlay").height(a(document).height())
        },
        _maintainPosition: function(b) {
            if (a.alerts.repositionOnResize) {
                switch (b) {
                    case true:
                        a(window).bind("resize", a.alerts._reposition);
                        break;
                    case false:
                        a(window).unbind("resize", a.alerts._reposition);
                        break
                }
            }
        }
    };
    hiAlert = function(b, c, d) {
        a.alerts.alert(b, c, d)
    };
    hiConfirm = function(b, c, d) {
        a.alerts.confirm(b, c, d)
    };
    hiPrompt = function(b, c, d, e) {
        a.alerts.prompt(b, c, d, e)
    };
    hiBox = function(f, g, b, c, e, d, i) {
        a.alerts.openBox(f, g, b, c, e, d, i)
    };
    hiOverAlert = function(c, b) {
        a.alerts.overAlert(c, b)
    }
})(jQuery);
