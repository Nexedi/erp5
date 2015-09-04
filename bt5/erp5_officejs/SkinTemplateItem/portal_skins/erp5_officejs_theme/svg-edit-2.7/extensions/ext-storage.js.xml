<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts40515059.47</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ext-storage.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals svgEditor, svgCanvas, $, widget*/\n
/*jslint vars: true, eqeq: true, regexp: true, continue: true*/\n
/*\n
 * ext-storage.js\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Brett Zamir\n
 *\n
 */\n
/**\n
* This extension allows automatic saving of the SVG canvas contents upon\n
*  page unload (which can later be automatically retrieved upon future\n
*  editor loads).\n
*\n
*  The functionality was originally part of the SVG Editor, but moved to a\n
*  separate extension to make the setting behavior optional, and adapted\n
*  to inform the user of its setting of local data.\n
*/\n
\n
/*\n
TODOS\n
1. Revisit on whether to use $.pref over directly setting curConfig in all\n
\textensions for a more public API (not only for extPath and imagePath,\n
\tbut other currently used config in the extensions)\n
2. We might provide control of storage settings through the UI besides the\n
    initial (or URL-forced) dialog.\n
*/\n
svgEditor.addExtension(\'storage\', function() {\n
\t// We could empty any already-set data for users when they decline storage,\n
\t//  but it would be a risk for users who wanted to store but accidentally\n
\t// said "no"; instead, we\'ll let those who already set it, delete it themselves;\n
\t// to change, set the "emptyStorageOnDecline" config setting to true\n
\t// in config.js.\n
\tvar emptyStorageOnDecline = svgEditor.curConfig.emptyStorageOnDecline,\n
\t\t// When the code in svg-editor.js prevents local storage on load per\n
\t\t//  user request, we also prevent storing on unload here so as to\n
\t\t//  avoid third-party sites making XSRF requests or providing links\n
\t\t// which would cause the user\'s local storage not to load and then\n
\t\t// upon page unload (such as the user closing the window), the storage\n
\t\t//  would thereby be set with an empty value, erasing any of the\n
\t\t// user\'s prior work. To change this behavior so that no use of storage\n
\t\t// or adding of new storage takes place regardless of settings, set\n
\t\t// the "noStorageOnLoad" config setting to true in config.js.\n
\t\tnoStorageOnLoad = svgEditor.curConfig.noStorageOnLoad,\n
\t\tforceStorage = svgEditor.curConfig.forceStorage,\n
\t\tstorage = svgEditor.storage;\n
\n
\tfunction replaceStoragePrompt (val) {\n
\t\tval = val ? \'storagePrompt=\' + val : \'\';\n
\t\tvar loc = top.location; // Allow this to work with the embedded editor as well\n
\t\tif (loc.href.indexOf(\'storagePrompt=\') > -1) {\n
\t\t\tloc.href = loc.href.replace(/([&?])storagePrompt=[^&]*(&?)/, function (n0, n1, amp) {\n
\t\t\t\treturn (val ? n1 : \'\') + val + (!val && amp ? n1 : (amp || \'\'));\n
\t\t\t});\n
\t\t}\n
\t\telse {\n
\t\t\tloc.href += (loc.href.indexOf(\'?\') > -1 ? \'&\' : \'?\') + val;\n
\t\t}\n
\t}\n
\tfunction setSVGContentStorage (val) {\n
\t\tif (storage) {\n
\t\t\tvar name = \'svgedit-\' + svgEditor.curConfig.canvasName;\n
\t\t\tif (!val) {\n
\t\t\t\tstorage.removeItem(name);\n
\t\t\t}\n
\t\t\telse {\n
\t\t\t\tstorage.setItem(name, val);\n
\t\t\t}\n
\t\t}\n
\t}\n
\t\n
\tfunction expireCookie (cookie) {\n
\t\tdocument.cookie = encodeURIComponent(cookie) + \'=; expires=Thu, 01 Jan 1970 00:00:00 GMT\';\n
\t}\n
\t\n
\tfunction removeStoragePrefCookie () {\n
\t\texpireCookie(\'store\');\n
\t}\n
\t\n
\tfunction emptyStorage() {\n
\t\tsetSVGContentStorage(\'\');\n
\t\tvar name;\n
\t\tfor (name in svgEditor.curPrefs) {\n
\t\t\tif (svgEditor.curPrefs.hasOwnProperty(name)) {\n
\t\t\t\tname = \'svg-edit-\' + name;\n
\t\t\t\tif (storage) {\n
\t\t\t\t\tstorage.removeItem(name);\n
\t\t\t\t}\n
\t\t\t\texpireCookie(name);\n
\t\t\t}\n
\t\t}\n
\t}\n
\t\n
//\temptyStorage();\n
\n
\t/**\n
\t* Listen for unloading: If and only if opted in by the user, set the content\n
\t*   document and preferences into storage:\n
\t* 1. Prevent save warnings (since we\'re automatically saving unsaved\n
\t*       content into storage)\n
\t* 2. Use localStorage to set SVG contents (potentially too large to allow in cookies)\n
\t* 3. Use localStorage (where available) or cookies to set preferences.\n
\t*/\n
\tfunction setupBeforeUnloadListener () {\n
\t\twindow.addEventListener(\'beforeunload\', function(e) {\n
\t\t\t// Don\'t save anything unless the user opted in to storage\n
\t\t\tif (!document.cookie.match(/(?:^|;\\s*)store=(?:prefsAndContent|prefsOnly)/)) {\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\tvar key;\n
\t\t\tif (document.cookie.match(/(?:^|;\\s*)store=prefsAndContent/)) {\n
\t\t\t\tsetSVGContentStorage(svgCanvas.getSvgString());\t\t\t\n
\t\t\t}\n
\n
\t\t\tsvgEditor.setConfig({no_save_warning: true}); // No need for explicit saving at all once storage is on\n
\t\t\t// svgEditor.showSaveWarning = false;\n
\n
\t\t\tvar curPrefs = svgEditor.curPrefs;\n
\n
\t\t\tfor (key in curPrefs) {\n
\t\t\t\tif (curPrefs.hasOwnProperty(key)) { // It\'s our own config, so we don\'t need to iterate up the prototype chain\n
\t\t\t\t\tvar val = curPrefs[key],\n
\t\t\t\t\t\tstore = (val != undefined);\n
\t\t\t\t\tkey = \'svg-edit-\' + key;\n
\t\t\t\t\tif (!store) {\n
\t\t\t\t\t\tcontinue;\n
\t\t\t\t\t}\n
\t\t\t\t\tif (storage) {\n
\t\t\t\t\t\tstorage.setItem(key, val);\n
\t\t\t\t\t}\n
\t\t\t\t\telse if (window.widget) {\n
\t\t\t\t\t\twidget.setPreferenceForKey(val, key);\n
\t\t\t\t\t}\n
\t\t\t\t\telse {\n
\t\t\t\t\t\tval = encodeURIComponent(val);\n
\t\t\t\t\t\tdocument.cookie = encodeURIComponent(key) + \'=\' + val + \'; expires=Fri, 31 Dec 9999 23:59:59 GMT\';\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}, false);\n
\t}\n
\n
\t/*\n
\t// We could add locales here instead (and also thereby avoid the need\n
\t// to keep our content within "langReady"), but this would be less\n
\t// convenient for translators.\n
\t$.extend(uiStrings, {confirmSetStorage: {\n
\t\tmessage: "By default and where supported, SVG-Edit can store your editor "+\n
\t\t"preferences and SVG content locally on your machine so you do not "+\n
\t\t"need to add these back each time you load SVG-Edit. If, for privacy "+\n
\t\t"reasons, you do not wish to store this information on your machine, "+\n
\t\t"you can change away from the default option below.",\n
\t\tstoragePrefsAndContent: "Store preferences and SVG content locally",\n
\t\tstoragePrefsOnly: "Only store preferences locally",\n
\t\tstoragePrefs: "Store preferences locally",\n
\t\tstorageNoPrefsOrContent: "Do not store my preferences or SVG content locally",\n
\t\tstorageNoPrefs: "Do not store my preferences locally",\n
\t\trememberLabel: "Remember this choice?",\n
\t\trememberTooltip: "If you choose to opt out of storage while remembering this choice, the URL will change so as to avoid asking again."\n
\t}});\n
\t*/\n
\tvar loaded = false;\n
\treturn {\n
\t\tname: \'storage\',\n
\t\tlangReady: function (data) {\n
\t\t\tvar // lang = data.lang,\n
\t\t\t\tuiStrings = data.uiStrings, // No need to store as dialog should only run once\n
\t\t\t\tstoragePrompt = $.deparam.querystring(true).storagePrompt;\n
\n
\t\t\t// No need to run this one-time dialog again just because the user\n
\t\t\t//   changes the language\n
\t\t\tif (loaded) {\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\tloaded = true;\n
\n
\t\t\t// Note that the following can load even if "noStorageOnLoad" is\n
\t\t\t//   set to false; to avoid any chance of storage, avoid this\n
\t\t\t//   extension! (and to avoid using any prior storage, set the\n
\t\t\t//   config option "noStorageOnLoad" to true).\n
\t\t\tif (!forceStorage && (\n
\t\t\t\t// If the URL has been explicitly set to always prompt the\n
\t\t\t\t//  user (e.g., so one can be pointed to a URL where one\n
\t\t\t\t// can alter one\'s settings, say to prevent future storage)...\n
\t\t\t\tstoragePrompt === true ||\n
\t\t\t\t(\n
\t\t\t\t\t// ...or...if the URL at least doesn\'t explicitly prevent a\n
\t\t\t\t\t//  storage prompt (as we use for users who\n
\t\t\t\t\t// don\'t want to set cookies at all but who don\'t want\n
\t\t\t\t\t// continual prompts about it)...\n
\t\t\t\t\tstoragePrompt !== false &&\n
\t\t\t\t\t// ...and this user hasn\'t previously indicated a desire for storage\n
\t\t\t\t\t!document.cookie.match(/(?:^|;\\s*)store=(?:prefsAndContent|prefsOnly)/)\n
\t\t\t\t)\n
\t\t\t\t// ...then show the storage prompt.\n
\t\t\t)) {\n
\n
\t\t\t\tvar options = [];\n
\t\t\t\tif (storage) {\n
\t\t\t\t\toptions.unshift(\n
\t\t\t\t\t\t{value: \'prefsAndContent\', text: uiStrings.confirmSetStorage.storagePrefsAndContent},\n
\t\t\t\t\t\t{value: \'prefsOnly\', text: uiStrings.confirmSetStorage.storagePrefsOnly},\n
\t\t\t\t\t\t{value: \'noPrefsOrContent\', text: uiStrings.confirmSetStorage.storageNoPrefsOrContent}\n
\t\t\t\t\t);\n
\t\t\t\t}\n
\t\t\t\telse {\n
\t\t\t\t\toptions.unshift(\n
\t\t\t\t\t\t{value: \'prefsOnly\', text: uiStrings.confirmSetStorage.storagePrefs},\n
\t\t\t\t\t\t{value: \'noPrefsOrContent\', text: uiStrings.confirmSetStorage.storageNoPrefs}\n
\t\t\t\t\t);\n
\t\t\t\t}\n
\n
\t\t\t\t// Hack to temporarily provide a wide and high enough dialog\n
\t\t\t\tvar oldContainerWidth = $(\'#dialog_container\')[0].style.width,\n
\t\t\t\t\toldContainerMarginLeft = $(\'#dialog_container\')[0].style.marginLeft,\n
\t\t\t\t\toldContentHeight = $(\'#dialog_content\')[0].style.height,\n
\t\t\t\t\toldContainerHeight = $(\'#dialog_container\')[0].style.height;\n
\t\t\t\t$(\'#dialog_content\')[0].style.height = \'120px\';\n
\t\t\t\t$(\'#dialog_container\')[0].style.height = \'170px\';\n
\t\t\t\t$(\'#dialog_container\')[0].style.width = \'800px\';\n
\t\t\t\t$(\'#dialog_container\')[0].style.marginLeft = \'-400px\';\n
\n
\t\t\t\t// Open select-with-checkbox dialog\n
\t\t\t\t$.select(\n
\t\t\t\t\tuiStrings.confirmSetStorage.message,\n
\t\t\t\t\toptions,\n
\t\t\t\t\tfunction (pref, checked) {\n
\t\t\t\t\t\tif (pref && pref !== \'noPrefsOrContent\') {\n
\t\t\t\t\t\t\t// Regardless of whether the user opted\n
\t\t\t\t\t\t\t// to remember the choice (and move to a URL which won\'t\n
\t\t\t\t\t\t\t// ask them again), we have to assume the user\n
\t\t\t\t\t\t\t// doesn\'t even want to remember their not wanting\n
\t\t\t\t\t\t\t// storage, so we don\'t set the cookie or continue on with\n
\t\t\t\t\t\t\t//  setting storage on beforeunload\n
\t\t\t\t\t\t\tdocument.cookie = \'store=\' + encodeURIComponent(pref) + \'; expires=Fri, 31 Dec 9999 23:59:59 GMT\'; // \'prefsAndContent\' | \'prefsOnly\'\n
\t\t\t\t\t\t\t// If the URL was configured to always insist on a prompt, if\n
\t\t\t\t\t\t\t//    the user does indicate a wish to store their info, we\n
\t\t\t\t\t\t\t//    don\'t want ask them again upon page refresh so move\n
\t\t\t\t\t\t\t//    them instead to a URL which does not always prompt\n
\t\t\t\t\t\t\tif (storagePrompt === true && checked) {\n
\t\t\t\t\t\t\t\treplaceStoragePrompt();\n
\t\t\t\t\t\t\t\treturn;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\telse { // The user does not wish storage (or cancelled, which we treat equivalently)\n
\t\t\t\t\t\t\tremoveStoragePrefCookie();\n
\t\t\t\t\t\t\tif (pref && // If the user explicitly expresses wish for no storage\n
\t\t\t\t\t\t\t\temptyStorageOnDecline\n
\t\t\t\t\t\t\t) {\n
\t\t\t\t\t\t\t\temptyStorage();\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tif (pref && checked) {\n
\t\t\t\t\t\t\t\t// Open a URL which won\'t set storage and won\'t prompt user about storage\n
\t\t\t\t\t\t\t\treplaceStoragePrompt(\'false\');\n
\t\t\t\t\t\t\t\treturn;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t// Reset width/height of dialog (e.g., for use by Export)\n
\t\t\t\t\t\t$(\'#dialog_container\')[0].style.width = oldContainerWidth;\n
\t\t\t\t\t\t$(\'#dialog_container\')[0].style.marginLeft = oldContainerMarginLeft;\t\t\t\t\n
\t\t\t\t\t\t$(\'#dialog_content\')[0].style.height = oldContentHeight;\n
\t\t\t\t\t\t$(\'#dialog_container\')[0].style.height = oldContainerHeight;\n
\t\t\t\t\t\t\n
\t\t\t\t\t\t// It should be enough to (conditionally) add to storage on\n
\t\t\t\t\t\t//   beforeunload, but if we wished to update immediately,\n
\t\t\t\t\t\t//   we might wish to try setting:\n
\t\t\t\t\t\t//       svgEditor.setConfig({noStorageOnLoad: true});\n
\t\t\t\t\t\t//   and then call:\n
\t\t\t\t\t\t//       svgEditor.loadContentAndPrefs();\n
\t\t\t\t\t\t\n
\t\t\t\t\t\t// We don\'t check for noStorageOnLoad here because\n
\t\t\t\t\t\t//   the prompt gives the user the option to store data\n
\t\t\t\t\t\tsetupBeforeUnloadListener();\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tsvgEditor.storagePromptClosed = true;\n
\t\t\t\t\t},\n
\t\t\t\t\tnull,\n
\t\t\t\t\tnull,\n
\t\t\t\t\t{\n
\t\t\t\t\t\tlabel: uiStrings.confirmSetStorage.rememberLabel,\n
\t\t\t\t\t\tchecked: false,\n
\t\t\t\t\t\ttooltip: uiStrings.confirmSetStorage.rememberTooltip\n
\t\t\t\t\t}\n
\t\t\t\t);\n
\t\t\t}\n
\t\t\telse if (!noStorageOnLoad || forceStorage) {\n
\t\t\t\tsetupBeforeUnloadListener();\n
\t\t\t}\n
\t\t}\n
\t};\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>11064</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
