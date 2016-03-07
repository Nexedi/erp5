/**
 * NEXEDI
 * Author: Thomas Lechauve
 * Date: 4/18/12
 */


// Hash parser utility
$.parseHash = function(hashTag) {
	var tokenized = $.extractAuth(hashTag);
	if (tokenized) {
		$.publish('auth', tokenized);
	}
	var splitted = hashTag.substr(1).split('/');
	return {
		route : splitted[0],
		id : splitted[1],
		method : splitted[2]
	}
};

$.extractAuth = function (hashTag) {
	var del = hashTag.indexOf('&');
	if (del != -1) {
		var splitted = hashTag.substring(del+1).split('&');
		var result = {};
		for (p in splitted) {
			var s = splitted[p].split('=');
			result[s[0]] = s[1];
		}
		return result;
	}
	return false;
};

$.genHash = function(url) {
	if ('id' in url) {
		url['id'] = '/' + url['id'];
	}
	if ('method' in url) {
		url['method'] = '/' + url['method'];
	}
	return '/' + url['route'] + (url['id'] || '') + (url['method'] || '');
};

/* Pub / Sub Pattern
	WARNING
	What's happening when we destroy a DOM object subscribed ?
 */
var o = $({});
$.subscribe = function() {
	o.on.apply(o, arguments);
};
$.unsubscribe = function() {
	o.off.apply(o, arguments);
};
$.publish = function() {
	o.trigger.apply(o, arguments);
};

// Event Handlers
$.hashHandler = function(){ $.publish("urlChange", window.location.hash.substr(1)); };
$.redirectHandler = function(event, url){ window.location.hash = $.genHash(url); };

// redirections manager
$.redirect = function(url){ $.publish('redirect', url); };
$.subscribe('redirect', $.redirectHandler)

$(window).bind('hashchange', $.hashHandler);
$(window).bind('load', $.hashHandler);
