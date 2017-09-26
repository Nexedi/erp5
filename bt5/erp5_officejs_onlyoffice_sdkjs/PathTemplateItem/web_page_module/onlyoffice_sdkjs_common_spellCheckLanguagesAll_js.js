/*
 * (c) Copyright Ascensio System SIA 2010-2017
 *
 * This program is a free software product. You can redistribute it and/or
 * modify it under the terms of the GNU Affero General Public License (AGPL)
 * version 3 as published by the Free Software Foundation. In accordance with
 * Section 7(a) of the GNU AGPL its Section 15 shall be amended to the effect
 * that Ascensio System SIA expressly excludes the warranty of non-infringement
 * of any third-party rights.
 *
 * This program is distributed WITHOUT ANY WARRANTY; without even the implied
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR  PURPOSE. For
 * details, see the GNU AGPL at: http://www.gnu.org/licenses/agpl-3.0.html
 *
 * You can contact Ascensio System SIA at Lubanas st. 125a-25, Riga, Latvia,
 * EU, LV-1021.
 *
 * The  interactive user interfaces in modified source and object code versions
 * of the Program must display Appropriate Legal Notices, as required under
 * Section 5 of the GNU AGPL version 3.
 *
 * Pursuant to Section 7(b) of the License you must retain the original Product
 * logo when distributing the program. Pursuant to Section 7(e) we decline to
 * grant you any rights under trademark law for use of our trademarks.
 *
 * All the Product's GUI elements, including illustrations and icon sets, as
 * well as technical writing content are licensed under the terms of the
 * Creative Commons Attribution-ShareAlike 4.0 International. See the License
 * terms at http://creativecommons.org/licenses/by-sa/4.0/legalcode
 *
 */

"use strict";

(	/**
 * @param {Window} window
 * @param {undefined} undefined
 */
  function (window, undefined) {
var g_spellCheckLanguages = [];
//{ "ar", 0x0001 },
//{ "bg", 0x0002 },
//{ "ca", 0x0003 },
//{ "zh-Hans", 0x0004 },
//{ "cs", 0x0005 },
//{ "da", 0x0006 },
//{ "de", 0x0007 },
//{ "el", 0x0008 },
//{ "en", 0x0009 },
//{ "es", 0x000a },
//{ "fi", 0x000b },
//{ "fr", 0x000c },
//{ "he", 0x000d },
//{ "hu", 0x000e },
//{ "is", 0x000f },
//{ "it", 0x0010 },
//{ "ja", 0x0011 },
//{ "ko", 0x0012 },
//{ "nl", 0x0013 },
//{ "no", 0x0014 },
//{ "pl", 0x0015 },
//{ "pt", 0x0016 },
//{ "rm", 0x0017 },
//{ "ro", 0x0018 },
//{ "ru", 0x0019 },
//{ "hr", 0x001a },
//{ "sk", 0x001b },
//{ "sq", 0x001c },
//{ "sv", 0x001d },
//{ "th", 0x001e },
//{ "tr", 0x001f },
//{ "ur", 0x0020 },
//{ "id", 0x0021 },
//{ "uk", 0x0022 },
//{ "be", 0x0023 },
//{ "sl", 0x0024 },
//{ "et", 0x0025 },
//{ "lv", 0x0026 },
//{ "lt", 0x0027 },
//{ "tg", 0x0028 },
//{ "fa", 0x0029 },
//{ "vi", 0x002a },
//{ "hy", 0x002b },
//{ "az", 0x002c },
//{ "eu", 0x002d },
//{ "hsb", 0x002e },
//{ "mk", 0x002f },
//{ "tn", 0x0032 },
//{ "xh", 0x0034 },
//{ "zu", 0x0035 },
//{ "af", 0x0036 },
//{ "ka", 0x0037 },
//{ "fo", 0x0038 },
//{ "hi", 0x0039 },
//{ "mt", 0x003a },
//{ "se", 0x003b },
//{ "ga", 0x003c },
//{ "ms", 0x003e },
//{ "kk", 0x003f },
//{ "ky", 0x0040 },
//{ "sw", 0x0041 },
//{ "tk", 0x0042 },
//{ "uz", 0x0043 },
//{ "tt", 0x0044 },
//{ "bn", 0x0045 },
//{ "pa", 0x0046 },
//{ "gu", 0x0047 },
//{ "or", 0x0048 },
//{ "ta", 0x0049 },
//{ "te", 0x004a },
//{ "kn", 0x004b },
//{ "ml", 0x004c },
//{ "as", 0x004d },
//{ "mr", 0x004e },
//{ "sa", 0x004f },
//{ "mn", 0x0050 },
//{ "bo", 0x0051 },
//{ "cy", 0x0052 },
//{ "km", 0x0053 },
//{ "lo", 0x0054 },
//{ "gl", 0x0056 },
//{ "kok", 0x0057 },
//{ "syr", 0x005a },
//{ "si", 0x005b },
//{ "iu", 0x005d },
//{ "am", 0x005e },
//{ "tzm", 0x005f },
//{ "ne", 0x0061 },
//{ "fy", 0x0062 },
//{ "ps", 0x0063 },
//{ "fil", 0x0064 },
//{ "dv", 0x0065 },
//{ "ha", 0x0068 },
//{ "yo", 0x006a },
//{ "quz", 0x006b },
//{ "nso", 0x006c },
//{ "ba", 0x006d },
//{ "lb", 0x006e },
//{ "kl", 0x006f },
//{ "ig", 0x0070 },
//{ "ii", 0x0078 },
//{ "arn", 0x007a },
//{ "moh", 0x007c },
//{ "br", 0x007e },
//{ "ug", 0x0080 },
//{ "mi", 0x0081 },
//{ "oc", 0x0082 },
//{ "co", 0x0083 },
//{ "gsw", 0x0084 },
//{ "sah", 0x0085 },
//{ "qut", 0x0086 },
//{ "rw", 0x0087 },
//{ "wo", 0x0088 },
//{ "prs", 0x008c },
//{ "gd", 0x0091 },
//{ "ar-SA", 0x0401 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("bg-BG", 0x0402));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("ca-ES", 0x0403));
//{ "zh-TW", 0x0404 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("cs-CZ", 0x0405));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("da-DK", 0x0406));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("de-DE", 0x0407));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("el-GR", 0x0408));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("en-US", 0x0409));
//{ "es-ES_tradnl", 0x040a },
//{ "fi-FI", 0x040b },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("fr-FR", 0x040c));
//{ "he-IL", 0x040d },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("hu-HU", 0x040e));
//{ "is-IS", 0x040f },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("it-IT", 0x0410));
//{ "ja-JP", 0x0411 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("ko-KR", 0x0412));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("nl-NL", 0x0413));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("nb-NO", 0x0414));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("pl-PL", 0x0415));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("pt-BR", 0x0416));
//{ "rm-CH", 0x0417 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("ro-RO", 0x0418));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("ru-RU", 0x0419));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("hr-HR", 0x041a));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("sk-SK", 0x041b));
//{ "sq-AL", 0x041c },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("sv-SE", 0x041d));
//{ "th-TH", 0x041e },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("tr-TR", 0x041f));
//{ "ur-PK", 0x0420 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("id-ID", 0x0421));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("uk-UA", 0x0422));
//{ "be-BY", 0x0423 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("sl-SI", 0x0424));
//{ "et-EE", 0x0425 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("lv-LV", 0x0426));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("lt-LT", 0x0427));
//{ "tg-Cyrl-TJ", 0x0428 },
//{ "fa-IR", 0x0429 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("vi-VN", 0x042a));
//{ "hy-AM", 0x042b },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("az-Latn-AZ", 0x042c));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("eu-ES", 0x042d));
//{ "wen-DE", 0x042e },
//{ "mk-MK", 0x042f },
//{ "st-ZA", 0x0430 },
//{ "ts-ZA", 0x0431 },
//{ "tn-ZA", 0x0432 },
//{ "ven-ZA", 0x0433 },
//{ "xh-ZA", 0x0434 },
//{ "zu-ZA", 0x0435 },
//{ "af-ZA", 0x0436 },
//{ "ka-GE", 0x0437 },
//{ "fo-FO", 0x0438 },
//{ "hi-IN", 0x0439 },
//{ "mt-MT", 0x043a },
//{ "se-NO", 0x043b },
//{ "ms-MY", 0x043e },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("kk-KZ", 0x043f));
//{ "ky-KG", 0x0440 },
//{ "sw-KE", 0x0441 },
//{ "tk-TM", 0x0442 },
//{ "uz-Latn-UZ", 0x0443 },
//{ "tt-RU", 0x0444 },
//{ "bn-IN", 0x0445 },
//{ "pa-IN", 0x0446 },
//{ "gu-IN", 0x0447 },
//{ "or-IN", 0x0448 },
//{ "ta-IN", 0x0449 },
//{ "te-IN", 0x044a },
//{ "kn-IN", 0x044b },
//{ "ml-IN", 0x044c },
//{ "as-IN", 0x044d },
//{ "mr-IN", 0x044e },
//{ "sa-IN", 0x044f },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("mn-MN", 0x0450));
//{ "bo-CN", 0x0451 },
//{ "cy-GB", 0x0452 },
//{ "km-KH", 0x0453 },
//{ "lo-LA", 0x0454 },
//{ "my-MM", 0x0455 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("gl-ES", 0x0456));
//{ "kok-IN", 0x0457 },
//{ "mni", 0x0458 },
//{ "sd-IN", 0x0459 },
//{ "syr-SY", 0x045a },
//{ "si-LK", 0x045b },
//{ "chr-US", 0x045c },
//{ "iu-Cans-CA", 0x045d },
//{ "am-ET", 0x045e },
//{ "tmz", 0x045f },
//{ "ne-NP", 0x0461 },
//{ "fy-NL", 0x0462 },
//{ "ps-AF", 0x0463 },
//{ "fil-PH", 0x0464 },
//{ "dv-MV", 0x0465 },
//{ "bin-NG", 0x0466 },
//{ "fuv-NG", 0x0467 },
//{ "ha-Latn-NG", 0x0468 },
//{ "ibb-NG", 0x0469 },
//{ "yo-NG", 0x046a },
//{ "quz-BO", 0x046b },
//{ "nso-ZA", 0x046c },
//{ "ba-RU", 0x046d },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("lb-LU", 0x046e));
//{ "kl-GL", 0x046f },
//{ "ig-NG", 0x0470 },
//{ "kr-NG", 0x0471 },
//{ "gaz-ET", 0x0472 },
//{ "ti-ER", 0x0473 },
//{ "gn-PY", 0x0474 },
//{ "haw-US", 0x0475 },
//{ "so-SO", 0x0477 },
//{ "ii-CN", 0x0478 },
//{ "pap-AN", 0x0479 },
//{ "arn-CL", 0x047a },
//{ "moh-CA", 0x047c },
//{ "br-FR", 0x047e },
//{ "ug-CN", 0x0480 },
//{ "mi-NZ", 0x0481 },
//{ "oc-FR", 0x0482 },
//{ "co-FR", 0x0483 },
//{ "gsw-FR", 0x0484 },
//{ "sah-RU", 0x0485 },
//{ "qut-GT", 0x0486 },
//{ "rw-RW", 0x0487 },
//{ "wo-SN", 0x0488 },
//{ "prs-AF", 0x048c },
//{ "plt-MG", 0x048d },
//{ "gd-GB", 0x0491 },
//{ "ar-IQ", 0x0801 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("ca-ES-valencia", 0x0803));
//{ "zh-CN", 0x0804 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("de-CH", 0x0807));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("en-GB", 0x0809));
//{ "es-MX", 0x080a },
//{ "fr-BE", 0x080c },
//{ "it-CH", 0x0810 },
//{ "nl-BE", 0x0813 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("nn-NO", 0x0814));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("pt-PT", 0x0816));
//{ "ro-MO", 0x0818 },
//{ "ru-MO", 0x0819 },
//{ "sr-Latn-CS", 0x081a },
//{ "sv-FI", 0x081d },
//{ "ur-IN", 0x0820 },
//{ "az-Cyrl-AZ", 0x082c },
//{ "dsb-DE", 0x082e },
//{ "se-SE", 0x083b },
//{ "ga-IE", 0x083c },
//{ "ms-BN", 0x083e },
//{ "uz-Cyrl-UZ", 0x0843 },
//{ "bn-BD", 0x0845 },
//{ "pa-PK", 0x0846 },
//{ "mn-Mong-CN", 0x0850 },
//{ "bo-BT", 0x0851 },
//{ "sd-PK", 0x0859 },
//{ "iu-Latn-CA", 0x085d },
//{ "tzm-Latn-DZ", 0x085f },
//{ "ne-IN", 0x0861 },
//{ "quz-EC", 0x086b },
//{ "ti-ET", 0x0873 },
//{ "ar-EG", 0x0c01 },
//{ "zh-HK", 0x0c04 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("de-AT", 0x0c07));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("en-AU", 0x0c09));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("es-ES", 0x0c0a));
//{ "fr-CA", 0x0c0c },
//{ "sr-Cyrl-CS", 0x0c1a },
//{ "se-FI", 0x0c3b },
//{ "tmz-MA", 0x0c5f },
//{ "quz-PE", 0x0c6b },
//{ "ar-LY", 0x1001 },
//{ "zh-SG", 0x1004 },
//{ "de-LU", 0x1007 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("en-CA", 0x1009));
//{ "es-GT", 0x100a },
//{ "fr-CH", 0x100c },
//{ "hr-BA", 0x101a },
//{ "smj-NO", 0x103b },
//{ "ar-DZ", 0x1401 },
//{ "zh-MO", 0x1404 },
//{ "de-LI", 0x1407 },
//{ "en-NZ", 0x1409 },
//{ "es-CR", 0x140a },
//{ "fr-LU", 0x140c },
//{ "bs-Latn-BA", 0x141a },
//{ "smj-SE", 0x143b },
//{ "ar-MA", 0x1801 },
//{ "en-IE", 0x1809 },
//{ "es-PA", 0x180a },
//{ "fr-MC", 0x180c },
//{ "sr-Latn-BA", 0x181a },
//{ "sma-NO", 0x183b },
//{ "ar-TN", 0x1c01 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("en-ZA", 0x1c09));
//{ "es-DO", 0x1c0a },
//{ "fr-West", 0x1c0c },
//{ "sr-Cyrl-BA", 0x1c1a },
//{ "sma-SE", 0x1c3b },
//{ "ar-OM", 0x2001 },
//{ "en-JM", 0x2009 },
//{ "es-VE", 0x200a },
//{ "fr-RE", 0x200c },
//{ "bs-Cyrl-BA", 0x201a },
//{ "sms-FI", 0x203b },
//{ "ar-YE", 0x2401 },
//{ "en-CB", 0x2409 },
//{ "es-CO", 0x240a },
//{ "fr-CG", 0x240c },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("sr-Latn-RS", 0x241a));
//{ "smn-FI", 0x243b },
//{ "ar-SY", 0x2801 },
//{ "en-BZ", 0x2809 },
//{ "es-PE", 0x280a },
//{ "fr-SN", 0x280c },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("sr-Cyrl-RS", 0x281a));
//{ "ar-JO", 0x2c01 },
//{ "en-TT", 0x2c09 },
//{ "es-AR", 0x2c0a },
//{ "fr-CM", 0x2c0c },
//{ "sr-Latn-ME", 0x2c1a },
//{ "ar-LB", 0x3001 },
//{ "en-ZW", 0x3009 },
//{ "es-EC", 0x300a },
//{ "fr-CI", 0x300c },
//{ "sr-Cyrl-ME", 0x301a },
//{ "ar-KW", 0x3401 },
//{ "en-PH", 0x3409 },
//{ "es-CL", 0x340a },
//{ "fr-ML", 0x340c },
//{ "ar-AE", 0x3801 },
//{ "en-ID", 0x3809 },
//{ "es-UY", 0x380a },
//{ "fr-MA", 0x380c },
//{ "ar-BH", 0x3c01 },
//{ "en-HK", 0x3c09 },
//{ "es-PY", 0x3c0a },
//{ "fr-HT", 0x3c0c },
//{ "ar-QA", 0x4001 },
//{ "en-IN", 0x4009 },
//{ "es-BO", 0x400a },
//{ "en-MY", 0x4409 },
//{ "es-SV", 0x440a },
//{ "en-SG", 0x4809 },
//{ "es-HN", 0x480a },
//{ "es-NI", 0x4c0a },
//{ "es-PR", 0x500a },
//{ "es-US", 0x540a },
//{ "bs-Cyrl", 0x641a },
//{ "bs-Latn", 0x681a },
//{ "sr-Cyrl", 0x6c1a },
//{ "sr-Latn", 0x701a },
//{ "smn", 0x703b },
//{ "az-Cyrl", 0x742c },
//{ "sms", 0x743b },
//{ "zh", 0x7804 },
//{ "nn", 0x7814 },
//{ "bs", 0x781a },
//{ "az-Latn", 0x782c },
//{ "sma", 0x783b },
//{ "uz-Cyrl", 0x7843 },
//{ "mn-Cyrl", 0x7850 },
//{ "iu-Cans", 0x785d },
//{ "zh-Hant", 0x7c04 },
//{ "nb", 0x7c14 },
//{ "sr", 0x7c1a },
//{ "tg-Cyrl", 0x7c28 },
//{ "dsb", 0x7c2e },
//{ "smj", 0x7c3b },
//{ "uz-Latn", 0x7c43 },
//{ "mn-Mong", 0x7c50 },
//{ "iu-Latn", 0x7c5d },
//{ "tzm-Latn", 0x7c5f },
//{ "ha-Latn", 0x7c68 },

  //-----------------------------------------------------------export---------------------------------------------------
  window['AscCommon'] = window['AscCommon'] || {};
  window["AscCommon"].g_spellCheckLanguages = g_spellCheckLanguages;
})(window);
