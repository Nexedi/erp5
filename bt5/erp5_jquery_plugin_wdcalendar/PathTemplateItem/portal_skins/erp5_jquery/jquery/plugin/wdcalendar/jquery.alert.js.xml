<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts96050261.59</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.alert.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

(function(a) {\r\n
    a.alerts = {\r\n
        verticalOffset: -75,\r\n
        horizontalOffset: 0,\r\n
        repositionOnResize: true,\r\n
        overlayOpacity: 0.50,\r\n
        overlayColor: "#FFF",\r\n
        draggable: true,\r\n
        okButton: "OK",\r\n
        cancelButton: "Cancel",\r\n
        dialogClass: null,\r\n
        alert: function(b, c, d) {\r\n
            if (c == null) {\r\n
                c = "OK"\r\n
            }\r\n
            a.alerts._show(c, b, null, "alert",\r\n
      function(e) {\r\n
          if (d) {\r\n
              d(e)\r\n
          }\r\n
      },\r\n
      null, null, null, null)\r\n
        },\r\n
        confirm: function(b, c, d) {\r\n
            if (c == null) {\r\n
                c = "Are you sure"\r\n
            }\r\n
            a.alerts._show(c, b, null, "confirm",\r\n
      function(e) {\r\n
          if (d) {\r\n
              d(e)\r\n
          }\r\n
      },\r\n
      null, null, null, null)\r\n
        },\r\n
        prompt: function(b, c, d, e) {\r\n
            if (d == null) {\r\n
                d = "Please enter something"\r\n
            }\r\n
            a.alerts._show(d, b, c, "prompt",\r\n
      function(f) {\r\n
          if (e) {\r\n
              e(f)\r\n
          }\r\n
      },\r\n
      null, null, null, null)\r\n
        },\r\n
        openBox: function(f, g, b, c, e, d, i) {\r\n
            if (g == null) {\r\n
                g = "Information"\r\n
            }\r\n
            a.alerts._show(g, f, null, "openBox",\r\n
      function(h) {\r\n
          if (i) {\r\n
              i(h)\r\n
          }\r\n
      },\r\n
      b, c, e, d)\r\n
        },\r\n
        overAlert: function(c, b) {\r\n
            a.alerts._overShow(c, b)\r\n
        },\r\n
        _overShow: function(d, c) {\r\n
            if (c == null) {\r\n
                c = 3000\r\n
            }\r\n
            var b = c + 600;\r\n
            a("body").append(\'<div id="over_container" style="display:none"><div id="over_message"></div></div>\');\r\n
            a("#over_message").text(d).html(a("#over_message").text().replace(/\\n/g, "<br />"));\r\n
            if (a.alerts.dialogClass) {\r\n
                a("#over_container").addClass(a.alerts.dialogClass)\r\n
            }\r\n
            var e = (a.browser.msie && parseInt(a.browser.version) <= 6) ? "absolute" : "fixed";\r\n
            a("#over_container").css({\r\n
                position: e,\r\n
                zIndex: 99999,\r\n
                width: 350,\r\n
                padding: 0,\r\n
                margin: 0\r\n
            }).show("fast");\r\n
            a("#over_container").css({\r\n
                minWidth: a("#over_container").outerWidth(),\r\n
                maxWidth: a("#over_container").outerWidth()\r\n
            });\r\n
            a.alerts._overReposition();\r\n
            setTimeout(function() {\r\n
                a("#over_container").hide("fast")\r\n
            },\r\n
      c);\r\n
            setTimeout(function() {\r\n
                a("#over_container").remove()\r\n
            },\r\n
      b)\r\n
        },\r\n
        _overReposition: function() {\r\n
            var c = 4;\r\n
            var b = ((a(window).width() / 2) - (a("#over_container").outerWidth() / 2)) + a.alerts.horizontalOffset;\r\n
            if (c < 0) {\r\n
                c = 0\r\n
            }\r\n
            if (b < 0) {\r\n
                b = 0\r\n
            }\r\n
            if (a.browser.msie && parseInt(a.browser.version) <= 6) {\r\n
                c = c + a(window).scrollTop()\r\n
            }\r\n
            if (a.browser.msie && parseInt(a.browser.version) <= 6) {\r\n
                b = b - 175\r\n
            }\r\n
            a("#over_container").css({\r\n
                top: c + "px",\r\n
                left: b + "px"\r\n
            });\r\n
            a("#popup_overlay").height(a(document).height())\r\n
        },\r\n
        _show: function(j, b, k, g, m, l, c, f, n) {\r\n
            a.alerts._hide();\r\n
            a.alerts._overlay("show");\r\n
            a("body").append(\'<div id="popup_container" style="display:none"><h1 id="popup_title"></h1><em id="ctl"></em><em id="cbl"></em><em id="ctr"></em><em id="cbr"></em><span id="popup_close"></span><div id="popup_content"><div id="popup_message"></div></div></div>\');\r\n
            if (a.alerts.dialogClass) {\r\n
                a("#popup_container").addClass(a.alerts.dialogClass)\r\n
            }\r\n
            var i = (a.browser.msie && parseInt(a.browser.version) <= 6) ? "absolute" : "fixed";\r\n
            a("#popup_container").css({\r\n
                position: i,\r\n
                zIndex: 99999,\r\n
                padding: 0,\r\n
                margin: 0\r\n
            }).show();\r\n
            a("#popup_title").text(j);\r\n
            a("#popup_content").addClass(g);\r\n
            if (g != "openBox") {\r\n
                a("#popup_message").text(b).html(a("#popup_message").text().replace(/\\n/g, "<br />"))\r\n
            }\r\n
            a("#popup_container").css({});\r\n
            a.alerts._reposition();\r\n
            a.alerts._maintainPosition(true);\r\n
            switch (g) {\r\n
                case "alert":\r\n
                    a("#popup_message").after(\'<div id="popup_panel"><input type="button" value="\' + a.alerts.okButton + \'" id="popup_ok" /></div>\');\r\n
                    a("#popup_ok").click(function() {\r\n
                        a.alerts._hide();\r\n
                        m(true)\r\n
                    });\r\n
                    a("#popup_ok").focus().keypress(function(h) {\r\n
                        if (h.keyCode == 13 || h.keyCode == 27) {\r\n
                            a("#popup_ok").trigger("click")\r\n
                        }\r\n
                    });\r\n
                    break;\r\n
                case "confirm":\r\n
                    a("#popup_message").after(\'<div id="popup_panel"><input type="button" value="\' + a.alerts.okButton + \'" id="popup_ok" /> <input type="button" value="\' + a.alerts.cancelButton + \'" id="popup_cancel" /></div>\');\r\n
                    a("#popup_ok").click(function() {\r\n
                        a.alerts._hide();\r\n
                        if (m) {\r\n
                            m(true)\r\n
                        }\r\n
                    });\r\n
                    a("#popup_cancel").click(function() {\r\n
                        a.alerts._hide();\r\n
                        if (m) {\r\n
                            m(false)\r\n
                        }\r\n
                    });\r\n
                    a("#popup_ok").focus();\r\n
                    a("#popup_ok, #popup_cancel").keypress(function(h) {\r\n
                        if (h.keyCode == 13) {\r\n
                            a("#popup_ok").trigger("click")\r\n
                        }\r\n
                        if (h.keyCode == 27) {\r\n
                            a("#popup_cancel").trigger("click")\r\n
                        }\r\n
                    });\r\n
                    break;\r\n
                case "prompt":\r\n
                    a("#popup_message").append(\'<br /><input type="text" size="30" id="popup_prompt" />\').after(\'<div id="popup_panel"><input type="button" value="\' + a.alerts.okButton + \'" id="popup_ok" /> <input type="button" value="\' + a.alerts.cancelButton + \'" id="popup_cancel" /></div>\');\r\n
                    a("#popup_prompt").width(a("#popup_message").width() - 10);\r\n
                    a("#popup_ok").click(function() {\r\n
                        var e = a("#popup_prompt").val();\r\n
                        a.alerts._hide();\r\n
                        if (m) {\r\n
                            m(e)\r\n
                        }\r\n
                    });\r\n
                    a("#popup_cancel").click(function() {\r\n
                        a.alerts._hide();\r\n
                        if (m) {\r\n
                            m(null)\r\n
                        }\r\n
                    });\r\n
                    a("#popup_prompt, #popup_ok, #popup_cancel").keypress(function(h) {\r\n
                        if (h.keyCode == 13) {\r\n
                            a("#popup_ok").trigger("click")\r\n
                        }\r\n
                        if (h.keyCode == 27) {\r\n
                            a("#popup_cancel").trigger("click")\r\n
                        }\r\n
                    });\r\n
                    if (k) {\r\n
                        a("#popup_prompt").val(k)\r\n
                    }\r\n
                    a("#popup_prompt").focus().select();\r\n
                    break;\r\n
                case "openBox":\r\n
                    a("#popup_message").append(a(b).html());\r\n
                    if (l) {\r\n
                        a("#popup_container").css({\r\n
                            width:\r\n
            l + "px"\r\n
                        })\r\n
                    }\r\n
                    if (c) {\r\n
                        a("#popup_container").css({\r\n
                            height: c + "px"\r\n
                        });\r\n
                        a("#popup_message").css({\r\n
                            height: (c - 48) + "px"\r\n
                        })\r\n
                    }\r\n
                    a.alerts._reposition();\r\n
                    if (f) {\r\n
                        a(f).click(function() {\r\n
                            a.alerts._hide();\r\n
                            if (m) {\r\n
                                m(true)\r\n
                            }\r\n
                        })\r\n
                    }\r\n
                    if (n) {\r\n
                        a(n).click(function() {\r\n
                            a.alerts._hide();\r\n
                            return false;\r\n
                            if (m) {\r\n
                                m(false)\r\n
                            }\r\n
                        })\r\n
                    }\r\n
                    break\r\n
            }\r\n
            a("#popup_close").click(function() {\r\n
                a.alerts._hide();\r\n
                if (m) {\r\n
                    m()\r\n
                }\r\n
            });\r\n
            if (a.alerts.draggable) {\r\n
                try {\r\n
                    a("#popup_container").draggable({\r\n
                        handle: a("#popup_title")\r\n
                    });\r\n
                    a("#popup_title").css({\r\n
                        cursor: "move"\r\n
                    })\r\n
                } catch (d) { }\r\n
            }\r\n
        },\r\n
        _hide: function() {\r\n
            a("#popup_container").remove();\r\n
            a.alerts._overlay("hide");\r\n
            a.alerts._maintainPosition(false)\r\n
        },\r\n
        _overlay: function(b) {\r\n
            switch (b) {\r\n
                case "show":\r\n
                    a.alerts._overlay("hide");\r\n
                    a("BODY").append(\'<div id="popup_overlay"></div>\');\r\n
                    a("#popup_overlay").css({\r\n
                        position:\r\n
          "absolute",\r\n
                        zIndex: 99998,\r\n
                        top: "0px",\r\n
                        left: "0px",\r\n
                        width: "100%",\r\n
                        height: a(document).height(),\r\n
                        background: a.alerts.overlayColor,\r\n
                        opacity: a.alerts.overlayOpacity\r\n
                    });\r\n
                    break;\r\n
                case "hide":\r\n
                    a("#popup_overlay").remove();\r\n
                    break\r\n
            }\r\n
        },\r\n
        _reposition: function() {\r\n
            var c = ((a(window).height() / 2) - (a("#popup_container").height() / 2)) + a.alerts.verticalOffset;\r\n
            var b = ((a(window).width() / 2) - (a("#popup_container").width() / 2)) + a.alerts.horizontalOffset;\r\n
            if (c < 0) {\r\n
                c = 0\r\n
            }\r\n
            if (b < 0) {\r\n
                b = 0\r\n
            }\r\n
            if (a.browser.msie && parseInt(a.browser.version) <= 6) {\r\n
                c = c + a(window).scrollTop()\r\n
            }\r\n
            a("#popup_container").css({\r\n
                top: c + "px",\r\n
                left: b + "px"\r\n
            });\r\n
            a("#popup_overlay").height(a(document).height())\r\n
        },\r\n
        _maintainPosition: function(b) {\r\n
            if (a.alerts.repositionOnResize) {\r\n
                switch (b) {\r\n
                    case true:\r\n
                        a(window).bind("resize", a.alerts._reposition);\r\n
                        break;\r\n
                    case false:\r\n
                        a(window).unbind("resize", a.alerts._reposition);\r\n
                        break\r\n
                }\r\n
            }\r\n
        }\r\n
    };\r\n
    hiAlert = function(b, c, d) {\r\n
        a.alerts.alert(b, c, d)\r\n
    };\r\n
    hiConfirm = function(b, c, d) {\r\n
        a.alerts.confirm(b, c, d)\r\n
    };\r\n
    hiPrompt = function(b, c, d, e) {\r\n
        a.alerts.prompt(b, c, d, e)\r\n
    };\r\n
    hiBox = function(f, g, b, c, e, d, i) {\r\n
        a.alerts.openBox(f, g, b, c, e, d, i)\r\n
    };\r\n
    hiOverAlert = function(c, b) {\r\n
        a.alerts.overAlert(c, b)\r\n
    }\r\n
})(jQuery);\r\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>12480</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>jquery.alert.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
