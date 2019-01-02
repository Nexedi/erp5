/*global window, rJS, RSVP, console, jQuery, $, JSON, Handlebars,
  loopEventListener, RegExp, alert, promiseEventListener */
/*jslint maxlen:180, nomen: true, regexp: true */
(function(window, rJS, $, Handlebars, loopEventListener) {
    "use strict";
    var gk = rJS(window), network_source = gk.__template_element.getElementById("network").innerHTML, network = Handlebars.compile(network_source);
    function endWith(str, end) {
        return str.indexOf(end, str.length - end.length) !== -1;
    }
    function contain(str, s) {
        return str.indexOf(s) !== -1;
    }
    function checkUrl(url) {
        return contain(url, ".com") || contain(url, ".net") || contain(url, ".fr");
    }
    function checkIp(ip) {
        var re = /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;
        return re.test(ip);
    }
    function check(value) {
        var g = this, info = g.__element.getElementsByClassName("info")[0], http, port, portEnd, tmp, ipValue = value;
        g.__element.getElementsByTagName("ul")[0].innerHTML = " ";
        http = ipValue.indexOf("http");
        tmp = ipValue.charAt(0);
        if (ipValue.indexOf("www.") !== -1) {
            if (http === -1) {
                info.innerHTML = "please start with http:// or https://";
                return;
            }
            if (!checkUrl(ipValue)) {
                info.innerHTML = "url invalide";
                return;
            }
        } else {
            ipValue = ipValue.substring(ipValue.indexOf("//") + 2);
            tmp = ipValue.charAt(0);
            if (tmp >= "0" && tmp <= "9") {
                port = ipValue.indexOf(":");
                portEnd = ipValue.indexOf(":/");
                if (port !== -1) {
                    ipValue = ipValue.substring(0, port);
                }
                if (http === -1) {
                    info.innerHTML = "please start ip with http:// or https://";
                    return;
                }
                if (port === -1 || portEnd !== -1) {
                    info.innerHTML = "input port number";
                    return;
                }
                if (checkIp(ipValue) === false) {
                    info.innerHTML = "invalide ip: ip should like xxx.xxx.xxx.xxx(xxx is between 0 ~ 255)";
                    return;
                }
                if (!endWith(value, "/")) {
                    info.innerHTML = "not end with /";
                    return;
                }
            }
        }
        return new RSVP.Queue().push(function() {
            return g.plSave({
                ip: value
            });
        }).push(function() {
            return g.displayThisPage({
                page: "playlist",
                action: value
            });
        }).push(function(url) {
            window.location = url;
        });
    }
    gk.declareAcquiredMethod("allDocs", "allDocs").declareAcquiredMethod("plSave", "plSave").declareAcquiredMethod("plGive", "plGive").declareAcquiredMethod("displayThisPage", "displayThisPage").declareAcquiredMethod("displayThisTitle", "displayThisTitle").declareAcquiredMethod("plCreateDavStorage", "plCreateDavStorage").declareAcquiredMethod("plEnablePage", "plEnablePage").declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash").declareMethod("render", function(options) {
        var gadget = this, ipValue, ip_context = gadget.__element.getElementsByClassName("inputIp")[0], list = gadget.__element.getElementsByTagName("ul")[0];
        return new RSVP.Queue().push(function() {
            return RSVP.all([ gadget.displayThisPage({
                page: "playlist",
                id: "offline"
            }), gadget.displayThisPage({
                page: "playlist",
                id: "localhost"
            }) ]);
        }).push(function(param_list) {
            gadget.__element.getElementsByClassName("offline")[0].href = param_list[0];
            gadget.__element.getElementsByClassName("localhost")[0].href = param_list[1];
        }).push(function() {
            if (options.action) {
                return options.action;
            }
            return gadget.plGive("ip");
        }).push(function(value) {
            if (value !== undefined) {
                ipValue = value;
                ip_context.value = value;
                if (options.action) {
                    return gadget.plCreateDavStorage(value);
                }
            }
        }).push(function() {
            return RSVP.any([ gadget.allDocs({
                include_docs: true
            }), promiseEventListener(ip_context, "change", false) ]);
        }).push(function(e) {
            if (e.data) {
                var tmp = e.data.rows, i, j, exp;
                Handlebars.registerHelper("compare", function(v1, options) {
                    if (v1 === "audio/mp3" || v1 === "audio/mpeg") {
                        return options.fn(this);
                    }
                    return options.inverse(this);
                });
                if (options.id !== undefined && options.id !== "online") {
                    tmp = [];
                    for (i = 0, j = 0; i < e.data.rows.length; i += 1) {
                        exp = new RegExp(options.id, "i");
                        if (e.data.rows[i].doc.title.search(exp) !== -1) {
                            tmp[j] = e.data.rows[i];
                            j += 1;
                        }
                    }
                    gadget.id = options.id;
                }
                list.innerHTML = network({
                    rows: tmp
                });
                $(list).listview("refresh");
                return gadget.displayThisTitle("online playlist: " + tmp.length + " media");
            }
            return check.call(gadget, ip_context.value);
        }).fail(function(error) {
            if (ipValue) {
                gadget.__element.getElementsByClassName("info")[0].innerHTML = "network error";
            }
            return gadget.displayThisTitle("online playlist: " + "0 media");
        });
    }).declareMethod("startService", function() {
        var g = this, research = g.__element.getElementsByClassName("research")[0], ip = g.__element.getElementsByClassName("inputIp")[0];
        if (g.id !== undefined) {
            research.value = g.id;
        }
        return new RSVP.Queue().push(function() {
            return g.plEnablePage();
        }).push(function() {
            return RSVP.any([ loopEventListener(research, "change", false, function() {
                return new RSVP.Queue().push(function() {
                    return g.displayThisPage({
                        page: "playlist",
                        id: research.value
                    });
                }).push(function(url) {
                    window.location = url;
                });
            }), loopEventListener(ip, "change", false, function() {
                return check.call(g, ip.value);
            }) ]);
        });
    });
})(window, rJS, jQuery, Handlebars, loopEventListener);