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
            <value> <string>ts44321418.04</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>About.js</string> </value>
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
 define(["common/main/lib/component/BaseView", "common/main/lib/component/Scroller"], function () {\r\n
    Common.Views.About = Common.UI.BaseView.extend(_.extend({\r\n
        menu: undefined,\r\n
        options: {\r\n
            alias: "Common.Views.About"\r\n
        },\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, arguments);\r\n
            this.txtVersionNum = "3.0";\r\n
            this.txtAscMail = "support@onlyoffice.com";\r\n
            this.txtAscTelNum = "+371 660-16425";\r\n
            this.txtAscUrl = "www.onlyoffice.com";\r\n
            this.txtAscName = "Ascensio System SIA";\r\n
            this.template = _.template([\'<table id="id-about-licensor-logo" cols="1" style="width: 100%; margin-top: 20px;">\', "<tr>", \'<td align="center"><div class="asc-about-office"/></td>\', "</tr>", "<tr>", \'<td align="center"><label class="asc-about-version">\' + options.appName.toUpperCase() + "</label></td>", "</tr>", "<tr>", \'<td align="center"><label class="asc-about-version">\' + this.txtVersion + this.txtVersionNum + "</label></td>", "</tr>", "</table>", \'<table id="id-about-licensor-info" cols="3" style="width: 100%;" class="margin-bottom">\', "<tr>", \'<td colspan="3" align="center" style="padding: 20px 0 10px 0;"><label class="asc-about-companyname">\' + this.txtAscName + "</label></td>", "</tr>", "<tr>", \'<td colspan="3" align="center" class="padding-small">\', \'<label class="asc-about-desc-name">\' + this.txtAddress + "</label>", \'<label class="asc-about-desc">\' + this.txtAscAddress + "</label>", "</td>", "</tr>", "<tr>", \'<td colspan="3" align="center" class="padding-small">\', \'<label class="asc-about-desc-name">\' + this.txtMail + "</label>", \'<a href="mailto:\' + this.txtAscMail + \'">\' + this.txtAscMail + "</a>", "</td>", "</tr>", "<tr>", \'<td colspan="3" align="center" class="padding-small">\', \'<label class="asc-about-desc-name">\' + this.txtTel + "</label>", \'<label class="asc-about-desc">\' + this.txtAscTelNum + "</label>", "</td>", "</tr>", "<tr>", \'<td colspan="3" align="center">\', \'<a href="http://\' + this.txtAscUrl + \'" target="_blank">\' + this.txtAscUrl + "</a>", "</td>", "</tr>", "</table>", \'<table id="id-about-licensee-info" cols="1" style="width: 100%; margin-top: 20px;" class="hidden margin-bottom"><tbody>\', "<tr>", \'<td align="center" class="padding-small"><div id="id-about-company-logo"/></td>\', "</tr>", "<tr>", \'<td align="center"><label class="asc-about-version">\' + options.appName.toUpperCase() + "</label></td>", "</tr>", "<tr>", \'<td align="center"><label style="padding-bottom: 29px;" class="asc-about-version">\' + this.txtVersion + this.txtVersionNum + "</label></td>", "</tr>", "<tr>", \'<td align="center" class="padding-small">\', \'<label class="asc-about-companyname" id="id-about-company-name"></label>\', "</td>", "</tr>", "<tr>", \'<td align="center" class="padding-small">\', \'<label class="asc-about-desc-name">\' + this.txtAddress + "</label>", \'<label class="asc-about-desc" id="id-about-company-address"></label>\', "</td>", "</tr>", "<tr>", \'<td align="center" class="padding-small">\', \'<label class="asc-about-desc-name">\' + this.txtMail + "</label>", \'<a href="mailto:" id="id-about-company-mail"></a>\', "</td>", "</tr>", "<tr>", \'<td align="center" class="padding-small">\', \'<a href="" target="_blank" id="id-about-company-url"></a>\', "</td>", "</tr>", "<tr>", \'<td align="center">\', \'<label class="asc-about-lic" id="id-about-company-lic"></label>\', "</td>", "</tr>", "</table>", \'<table id="id-about-licensor-short" cols="1" style="width: 100%; margin-top: 31px;" class="hidden"><tbody>\', "<tr>", \'<td style="width:50%;"><div class="separator horizontal short left"/></td>\', \'<td align="center"><label class="asc-about-header">\' + this.txtPoweredBy + "</label></td>", \'<td style="width:50%;"><div class="separator horizontal short"/></td>\', "</tr>", "<tr>", \'<td colspan="3" align="center" style="padding: 9px 0 10px;"><label class="asc-about-companyname">\' + this.txtAscName + "</label></td>", "</tr>", "<tr>", \'<td colspan="3" align="center">\', \'<a href="http://\' + this.txtAscUrl + \'" target="_blank">\' + this.txtAscUrl + "</a>", "</td>", "</tr>", "</table>"].join(""));\r\n
            this.menu = options.menu;\r\n
        },\r\n
        render: function () {\r\n
            var el = $(this.el);\r\n
            el.html(this.template({\r\n
                scope: this\r\n
            }));\r\n
            el.addClass("about-dlg");\r\n
            this.cntLicenseeInfo = $("#id-about-licensee-info");\r\n
            this.cntLicensorInfo = $("#id-about-licensor-info");\r\n
            this.divCompanyLogo = $("#id-about-company-logo");\r\n
            this.lblCompanyName = $("#id-about-company-name");\r\n
            this.lblCompanyAddress = $("#id-about-company-address");\r\n
            this.lblCompanyMail = $("#id-about-company-mail");\r\n
            this.lblCompanyUrl = $("#id-about-company-url");\r\n
            this.lblCompanyLic = $("#id-about-company-lic");\r\n
            if (_.isUndefined(this.scroller)) {\r\n
                this.scroller = new Common.UI.Scroller({\r\n
                    el: $(this.el),\r\n
                    suppressScrollX: true\r\n
                });\r\n
            }\r\n
            return this;\r\n
        },\r\n
        setLicInfo: function (data) {\r\n
            if (data && typeof(data) == "object" && typeof(data.customer) == "object") {\r\n
                var customer = data.customer;\r\n
                $("#id-about-licensor-logo").addClass("hidden");\r\n
                $("#id-about-licensor-short").removeClass("hidden");\r\n
                this.cntLicensorInfo.addClass("hidden");\r\n
                this.cntLicenseeInfo.removeClass("hidden");\r\n
                this.cntLicensorInfo.removeClass("margin-bottom");\r\n
                var value = customer.name;\r\n
                value && value.length ? this.lblCompanyName.text(value) : this.lblCompanyName.parents("tr").addClass("hidden");\r\n
                value = customer.address;\r\n
                value && value.length ? this.lblCompanyAddress.text(value) : this.lblCompanyAddress.parents("tr").addClass("hidden");\r\n
                (value = customer.mail) && value.length ? this.lblCompanyMail.attr("href", "mailto:" + value).text(value) : this.lblCompanyMail.parents("tr").addClass("hidden");\r\n
                if ((value = customer.www) && value.length) {\r\n
                    var http = !/^https?:\\/{2}/i.test(value) ? "http://": "";\r\n
                    this.lblCompanyUrl.attr("href", http + value).text(value);\r\n
                } else {\r\n
                    this.lblCompanyUrl.parents("tr").addClass("hidden");\r\n
                } (value = customer.info) && value.length ? this.lblCompanyLic.text(value) : this.lblCompanyLic.parents("tr").addClass("hidden");\r\n
                (value = customer.logo) && value.length ? this.divCompanyLogo.html(\'<img src="\' + value + \'" />\') : this.divCompanyLogo.parents("tr").addClass("hidden");\r\n
            } else {\r\n
                this.cntLicenseeInfo.addClass("hidden");\r\n
                this.cntLicensorInfo.addClass("margin-bottom");\r\n
            }\r\n
        },\r\n
        show: function () {\r\n
            Common.UI.BaseView.prototype.show.call(this, arguments);\r\n
            this.fireEvent("show", this);\r\n
        },\r\n
        hide: function () {\r\n
            Common.UI.BaseView.prototype.hide.call(this, arguments);\r\n
            this.fireEvent("hide", this);\r\n
        },\r\n
        txtPoweredBy: "Powered by",\r\n
        txtVersion: "Version ",\r\n
        txtLicensor: "LICENSOR",\r\n
        txtLicensee: "LICENSEE",\r\n
        txtAddress: "address: ",\r\n
        txtAscAddress: "Lubanas st. 125a-25, Riga, Latvia, EU, LV-1021",\r\n
        txtMail: "email: ",\r\n
        txtTel: "tel.: "\r\n
    },\r\n
    Common.Views.About || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>9269</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
