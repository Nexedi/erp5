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
            <value> <string>ts44308425.21</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>FormulaDialog.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

﻿/*\r\n
 * (c) Copyright Ascensio System SIA 2010-2015\r\n
 *\r\n
 * This program is a free software product. You can redistribute it and/or \r\n
 * modify it under the terms of the GNU Affero General Public License (AGPL) \r\n
 * version 3 as published by the Free Software Foundation. In accordance with \r\n
 * Section 7(a) of the GNU AGPL its Section 15 shall be amended to the effect \r\n
 * that Ascensio System SIA expressly excludes the warranty of non-infringement\r\n
 * of any third-party rights.\r\n
 *\r\n
 * This program is distributed WITHOUT ANY WARRANTY; without even the implied \r\n
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR  PURPOSE. For \r\n
 * details, see the GNU AGPL at: http://www.gnu.org/licenses/agpl-3.0.html\r\n
 *\r\n
 * You can contact Ascensio System SIA at Lubanas st. 125a-25, Riga, Latvia,\r\n
 * EU, LV-1021.\r\n
 *\r\n
 * The  interactive user interfaces in modified source and object code versions\r\n
 * of the Program must display Appropriate Legal Notices, as required under \r\n
 * Section 5 of the GNU AGPL version 3.\r\n
 *\r\n
 * Pursuant to Section 7(b) of the License you must retain the original Product\r\n
 * logo when distributing the program. Pursuant to Section 7(e) we decline to\r\n
 * grant you any rights under trademark law for use of our trademarks.\r\n
 *\r\n
 * All the Product\'s GUI elements, including illustrations and icon sets, as\r\n
 * well as technical writing content are licensed under the terms of the\r\n
 * Creative Commons Attribution-ShareAlike 4.0 International. See the License\r\n
 * terms at http://creativecommons.org/licenses/by-sa/4.0/legalcode\r\n
 *\r\n
 */\r\n
 define(["core", "spreadsheeteditor/main/app/collection/FormulaGroups", "spreadsheeteditor/main/app/view/FormulaDialog"], function () {\r\n
    SSE.Controllers = SSE.Controllers || {};\r\n
    SSE.Controllers.FormulaDialog = Backbone.Controller.extend({\r\n
        models: [],\r\n
        views: ["FormulaDialog"],\r\n
        collections: ["FormulaGroups"],\r\n
        initialize: function () {},\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
            if (this.formulasGroups && this.api) {\r\n
                this.loadingFormulas();\r\n
                var me = this;\r\n
                this.formulas = new SSE.Views.FormulaDialog({\r\n
                    api: this.api,\r\n
                    toolclose: "hide",\r\n
                    formulasGroups: this.formulasGroups,\r\n
                    handler: function (func) {\r\n
                        if (func && me.api) {\r\n
                            me.api.asc_insertFormula(func);\r\n
                        }\r\n
                    }\r\n
                });\r\n
                this.formulas.on({\r\n
                    "hide": function () {\r\n
                        if (me.api) {\r\n
                            me.api.asc_enableKeyEvents(true);\r\n
                        }\r\n
                    }\r\n
                });\r\n
            }\r\n
            return this;\r\n
        },\r\n
        onLaunch: function () {\r\n
            this.formulasGroups = this.getApplication().getCollection("FormulaGroups");\r\n
        },\r\n
        showDialog: function () {\r\n
            if (this.formulas) {\r\n
                this.formulas.show();\r\n
            }\r\n
        },\r\n
        hideDialog: function () {\r\n
            if (this.formulas && this.formulas.isVisible()) {\r\n
                this.formulas.hide();\r\n
            }\r\n
        },\r\n
        loadingFormulas: function () {\r\n
            var i = 0,\r\n
            j = 0,\r\n
            ascGroupName, ascFunctions, functions, store = this.formulasGroups,\r\n
            formulaGroup = null,\r\n
            index = 0,\r\n
            funcInd = 0,\r\n
            info = null,\r\n
            allFunctions = [],\r\n
            allFunctionsGroup = null;\r\n
            if (store) {\r\n
                allFunctionsGroup = new SSE.Models.FormulaGroup({\r\n
                    name: "All",\r\n
                    index: index,\r\n
                    store: store\r\n
                });\r\n
                if (allFunctionsGroup) {\r\n
                    index += 1;\r\n
                    store.push(allFunctionsGroup);\r\n
                    info = this.api.asc_getFormulasInfo();\r\n
                    for (i = 0; i < info.length; i += 1) {\r\n
                        ascGroupName = info[i].asc_getGroupName();\r\n
                        ascFunctions = info[i].asc_getFormulasArray();\r\n
                        formulaGroup = new SSE.Models.FormulaGroup({\r\n
                            name: ascGroupName,\r\n
                            index: index,\r\n
                            store: store\r\n
                        });\r\n
                        index += 1;\r\n
                        functions = [];\r\n
                        for (j = 0; j < ascFunctions.length; j += 1) {\r\n
                            var func = new SSE.Models.FormulaModel({\r\n
                                index: funcInd,\r\n
                                group: ascGroupName,\r\n
                                name: ascFunctions[j].asc_getName(),\r\n
                                args: ascFunctions[j].asc_getArguments()\r\n
                            });\r\n
                            funcInd += 1;\r\n
                            functions.push(func);\r\n
                            allFunctions.push(func);\r\n
                        }\r\n
                        formulaGroup.set("functions", functions);\r\n
                        store.push(formulaGroup);\r\n
                    }\r\n
                    allFunctionsGroup.set("functions", _.sortBy(allFunctions, function (model) {\r\n
                        return model.get("name");\r\n
                    }));\r\n
                }\r\n
            }\r\n
        }\r\n
    });\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>5538</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
