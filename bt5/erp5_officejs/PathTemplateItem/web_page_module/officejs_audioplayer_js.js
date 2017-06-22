/*global window, rJS, RSVP, console, $, jQuery, URL, location, webkitURL */
/*jslint nomen: true*/
(function (window, rJS, $, RSVP, document) {
    "use strict";
    $.mobile.ajaxEnabled = false;
    $.mobile.linkBindingEnabled = false;
    $.mobile.hashListeningEnabled = false;
    $.mobile.pushStateEnabled = false;
    var gadget_list = {
        upload: {
            "0": "gadget_officejs_audioplayer_upload.html",
            "1": "gadget_officejs_audioplayer_playlist_local.html",
            "2": "gadget_officejs_audioplayer_upload.html"
        },
        playlist: {
            "0": "gadget_officejs_audioplayer_playlist_offline.html",
            "1": "gadget_officejs_audioplayer_playlist_local.html",
            "2": "gadget_officejs_audioplayer_playlist_online.html"
        },
        control: {
            "0": "gadget_officejs_audioplayer_control.html",
            "1": "gadget_officejs_audioplayer_control.html",
            "2": "gadget_officejs_audioplayer_control.html"
        },
        video_control: {
            "0": "gadget_officejs_audioplayer_video_control.html",
            "1": "gadget_officejs_audioplayer_video_control.html",
            "2": "gadget_officejs_audioplayer_video_control.html"
        }
    }, allStorageType = ["offline", "localhost", "online"];
    function storageType(type) {
        return allStorageType[type];
    }
    function disablePage(g) {
        var overlay = document.createElement("div"), loader = document.createElement("div"), controlPanel = g.__element.getElementsByClassName("page")[0], i = 0, circle;
        if (controlPanel.firstChild) {
            return;
        }
        overlay.className = "overlay";
        loader.className = "loader";
        while (i < 5) {
            circle = document.createElement("div");
            circle.className = "circle";
            loader.appendChild(circle);
            i += 1;
        }
        overlay.appendChild(loader);
        controlPanel.appendChild(overlay);
    }
    rJS(window)
      .declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash")
      .allowPublicAcquisition("plEnablePage", function () {
        var controlPanel = this.__element.getElementsByClassName("page")[0];
        if (controlPanel) {
            while (controlPanel.firstChild) {
                controlPanel.removeChild(controlPanel.firstChild);
            }
        }
    }).allowPublicAcquisition("plDisablePage", function() {
        disablePage(this);
    }).allowPublicAcquisition("plCreateDavStorage", function(list) {
        return this.getDeclaredGadget("online").push(function(gadget) {
            return gadget.createJio({
                type: "dav",
                url: list[0]
            });
        });
    }).allowPublicAcquisition("displayThisPage", function(param_list) {
        // Hey, I want to display this page
        return this.aq_pleasePublishMyState(param_list[0]);
    }).allowPublicAcquisition("plSave", function(param_list) {
        this.save = this.save || [];
        var key = Object.keys(param_list[0]);
        this.save[key[0]] = param_list[0][key[0]];
    }).allowPublicAcquisition("plGiveStorageType", function() {
        return this.storageType;
    }).allowPublicAcquisition("plGive", function(param_list) {
        if (this.save === undefined) {
            return this.save;
        }
        return this.save[param_list[0]];
    }).allowPublicAcquisition("allDocs", function(param_list) {
        if (this.storageType === 1) {
            param_list[0].save = true;
        } else {
            param_list[0].save = false;
        }
        return this.getDeclaredGadget(storageType(this.storageType)).push(function(jio_gadget) {
            return jio_gadget.allDocs.apply(jio_gadget, param_list);
        });
    }).allowPublicAcquisition("jio_post", function(param_list) {
        var type;
        if (param_list[1] === 0 || param_list[1] === 1) {
            type = param_list[1];
        } else {
            type = this.storageType;
        }
        return this.getDeclaredGadget(storageType(type)).push(function(jio_gadget) {
            return jio_gadget.post.apply(jio_gadget, param_list);
        });
    }).allowPublicAcquisition("jio_putAttachment", function(param_list) {
        var type;
        if (param_list[1] === 0 || param_list[1] === 1) {
            type = param_list[1];
        } else {
            type = this.storageType;
        }
        return this.getDeclaredGadget(storageType(type)).push(function(jio_gadget) {
            return jio_gadget.putAttachment.apply(jio_gadget, param_list);
        });
    }).allowPublicAcquisition("jio_getAttachment", function(param_list) {
        return this.getDeclaredGadget(storageType(this.storageType)).push(function(jio_gadget) {
            return jio_gadget.getAttachment.apply(jio_gadget, param_list);
        });
    }).allowPublicAcquisition("jio_get", function(param_list) {
        return this.getDeclaredGadget(storageType(this.storageType)).push(function(jio_gadget) {
            return jio_gadget.get.apply(jio_gadget, param_list);
        });
    }).allowPublicAcquisition("jio_remove", function(param_list) {
        return this.getDeclaredGadget(storageType(this.storageType)).push(function(jio_gadget) {
            return jio_gadget.remove.apply(jio_gadget, param_list);
        });
    }).allowPublicAcquisition("jio_removeAttachment", function(param_list) {
        return this.getDeclaredGadget(storageType(this.storageType)).push(function(jio_gadget) {
            return jio_gadget.removeAttachment.apply(jio_gadget, param_list);
        });
    }).allowPublicAcquisition("displayThisTitle", function(param_list) {
        var header = this.__element.getElementsByTagName("h1")[0];
        header.innerHTML = param_list[0];
    });
    rJS(window).ready(function(g) {
        return g.getDeclaredGadget("localhost").push(function(gadget) {
            return gadget.createJio({
                type: "http",
                database: "http://localhost:8080/"
            });
        }).push(function() {
            return g.getDeclaredGadget("offline");
        }).push(function(gadget) {
            return gadget.createJio({
                type: "indexeddb",
                database: "musicLibrary",
                _unite: 5e6
            });
        }).push(function() {
            var controlPanel = g.__element.getElementsByClassName("page")[0];
            if (controlPanel) {
                while (controlPanel.firstChild) {
                    controlPanel.removeChild(controlPanel.firstChild);
                }
            }
        });
    }).declareMethod("render", function(options) {
        var gadget = this, page_gadget, element, page_element;
        element = gadget.__element.getElementsByClassName("gadget_container")[0];
        if (options.page === undefined) {
            // Redirect to the about page
            return gadget.aq_pleasePublishMyState({
                page: "playlist"
            }).push(gadget.pleaseRedirectMyHash.bind(gadget));
        }
        gadget.__element.getElementsByClassName("console")[0].innerHTML = "";
        gadget.storageType = gadget.storageType || 0;
        if (options.page === "playlist") {
            if (options.id === "offline") {
                gadget.storageType = 0;
                gadget.__element.getElementsByClassName("addMusic")[0].style.display = "";
            } else if (options.id === "localhost") {
                gadget.storageType = 1;
                gadget.__element.getElementsByClassName("addMusic")[0].style.display = "none";
            } else if (options.id === "online") {
                gadget.storageType = 2;
                gadget.__element.getElementsByClassName("addMusic")[0].style.display = "";
            }
        }
        return gadget.declareGadget(gadget_list[options.page][gadget.storageType]).push(function(g) {
            disablePage(gadget);
            page_gadget = g;
            return page_gadget.getElement();
        }).push(function(result) {
            page_element = result;
            while (element.firstChild) {
                element.removeChild(element.firstChild);
            }
            element.appendChild(page_element);
            $(element).trigger("create");
            if (page_gadget.render !== undefined) {
                return page_gadget.render(options);
            }
        }).push(function() {
            // XXX RenderJS hack to start sub gadget services
            // Only work if this gadget has no parent.
            if (page_gadget.startService !== undefined) {
                return page_gadget.startService(options);
            }
        }).fail(function(e) {
            gadget.__element.getElementsByClassName("console")[0].innerHTML = e;
        });
    });
})(window, rJS, jQuery, RSVP, document);