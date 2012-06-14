# -*- coding: UTF-8 -*-
# Copyright (C) 2000-2007  Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2003  Roberto Quero, Eduardo Corrales
# Copyright (C) 2004  Søren Roug
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module provides the MessageCatalog base class, which
provides message catalogs for the web.
"""

# Import from the Standard Library
from base64 import encodestring, decodestring
from hashlib import md5
from re import compile
from time import gmtime, strftime, time
from urllib import quote

# Import from itools
from itools.datatypes import LanguageTag
import itools.gettext
from itools.tmx import TMXFile, Sentence, TMXUnit, TMXNote
from itools.xliff import XLFFile, XLFNote

# Import from Zope
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from App.class_init import InitializeClass
from App.Dialogs import MessageDialog
from OFS.ObjectManager import ObjectManager
from OFS.SimpleItem import SimpleItem
from Persistence import PersistentMapping
from ZPublisher import HTTPRequest
from zope.component import getSiteManager
from zope.i18n import interpolate
from zope.i18n.interfaces import ITranslationDomain
from zope.interface import implements

# Import from Localizer
from interfaces import IMessageCatalog
from LanguageManager import LanguageManager
from LocalFiles import LocalDTMLFile
from utils import charsets, lang_negotiator, _



###########################################################################
# Utility functions and constants
###########################################################################
def md5text(str):
    """Create an MD5 sum (or hash) of a text. It is guaranteed to be 32 bytes
    long.
    """
    return md5(str.encode('utf-8')).hexdigest()


def to_unicode(x):
    """In Zope the ISO-8859-1 encoding has an special status, normal strings
    are considered to be in this encoding by default.
    """
    if isinstance(x, unicode):
        return x
    encoding = HTTPRequest.default_encoding
    return unicode(x, encoding)


def message_encode(message):
    """Encodes a message to an ASCII string.

    To be used in the user interface, to avoid problems with the
    encodings, HTML entities, etc..
    """
    if isinstance(message, unicode):
        encoding = HTTPRequest.default_encoding
        message = message.encode(encoding)

    return encodestring(message)


def message_decode(message):
    """Decodes a message from an ASCII string.

    To be used in the user interface, to avoid problems with the
    encodings, HTML entities, etc..
    """
    message = decodestring(message)
    encoding = HTTPRequest.default_encoding
    return unicode(message, encoding)


def filter_sort(x, y):
    return cmp(to_unicode(x), to_unicode(y))


def get_url(url, batch_start, batch_size, regex, lang, empty, **kw):
    params = []
    for key, value in kw.items():
        if value is None:
            continue
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        params.append('%s=%s' % (key, quote(value)))

    params.extend(['batch_start:int=%d' % batch_start,
                   'batch_size:int=%d' % batch_size,
                   'regex=%s' % quote(regex),
                   'empty=%s' % (empty and 'on' or '')])

    if lang:
        params.append('lang=%s' % lang)

    return url + '?' + '&amp;'.join(params)


# Empty header information for PO files (UTF-8 is the default encoding)
empty_po_header = {'last_translator_name': '',
                   'last_translator_email': '',
                   'language_team': '',
                   'charset': 'UTF-8'}


###########################################################################
# The Message Catalog class, and ZMI constructor
###########################################################################
manage_addMessageCatalogForm = LocalDTMLFile('ui/MC_add', globals())
def manage_addMessageCatalog(self, id, title, languages, sourcelang=None,
                             REQUEST=None):
    """ """
    if sourcelang is None:
        sourcelang = languages[0]

    self._setObject(id, MessageCatalog(id, title, sourcelang, languages))

    if REQUEST is not None:
        return self.manage_main(self, REQUEST)



class MessageCatalog(LanguageManager, ObjectManager, SimpleItem):
    """Stores messages and their translations...
    """

    meta_type = 'MessageCatalog'
    implements(IMessageCatalog)


    security = ClassSecurityInfo()


    def __init__(self, id, title, sourcelang, languages):
        self.id = id

        self.title = title

        # Language Manager data
        self._languages = tuple(languages)
        self._default_language = sourcelang

        # Here the message translations are stored
        self._messages = PersistentMapping()

        # Data for the PO files headers
        self._po_headers = PersistentMapping()
        for lang in self._languages:
            self._po_headers[lang] = empty_po_header


    #######################################################################
    # ITranslationDomain interface
    # zope.i18n.interfaces.ITranslationDomain
    #######################################################################
    @property
    def domain(self):
        """ """
        return unicode(self.id)


    def translate(self, msgid, mapping=None, context=None,
                  target_language=None, default=None):
        """ """
        msgstr = self.gettext(msgid, lang=target_language, default=default)
        return interpolate(msgstr, mapping)


    #######################################################################
    # Private API
    #######################################################################
    def get_message_key(self, message):
        if message in self._messages:
            return message
        # A message may be stored as unicode or byte string
        encoding = HTTPRequest.default_encoding
        if isinstance(message, unicode):
            message = message.encode(encoding)
        else:
            message = unicode(message, encoding)
        if message in self._messages:
            return message


    def get_translations(self, message):
        message = self.get_message_key(message)
        return self._messages[message]


    def get_tabs_message(self, REQUEST):
        message = REQUEST.get('manage_tabs_message')
        if message is None:
            return None
        return unicode(message, 'utf-8')


    #######################################################################
    # Public API
    #######################################################################
    security.declarePublic('message_exists')
    def message_exists(self, message):
        """ """
        return self._messages.has_key(message)


    security.declareProtected('Manage messages', 'message_edit')
    def message_edit(self, message, language, translation, note):
        """ """
        self._messages[message][language] = translation
        self._messages[message]['note'] = note


    security.declareProtected('Manage messages', 'message_del')
    def message_del(self, message):
        """ """
        del self._messages[message]


    security.declarePublic('gettext')
    def gettext(self, message, lang=None, add=1, default=None):
        """Returns the message translation from the database if available.

        If add=1, add any unknown message to the database.
        If a default is provided, use it instead of the message id
        as a translation for unknown messages.
        """
        if not isinstance(message, (str, unicode)):
            raise TypeError, 'only strings can be translated.'

        message = message.strip()

        if default is None:
            default = message

        # Add it if it's not in the dictionary
        if add and not self._messages.has_key(message) and message:
            self._messages[message] = PersistentMapping()

        # Get the string
        if self._messages.has_key(message):
            m = self._messages[message]

            if lang is None:
                # Builds the list of available languages
                # should the empty translations be filtered?
                available_languages = list(self._languages)

                # Imagine that the default language is 'en'. There is no
                # translation from 'en' to 'en' in the message catalog
                # The user has the preferences 'en' and 'nl' in that order
                # The next two lines make certain 'en' is shown, not 'nl'
                if not self._default_language in available_languages:
                    available_languages.append(self._default_language)

                # Get the language!
                lang = lang_negotiator(available_languages)

                # Is it None? use the default
                if lang is None:
                    lang = self._default_language

            if lang is not None:
                return m.get(lang) or default

        return default


    __call__ = gettext


    #######################################################################
    # Management screens
    #######################################################################
    manage_options = (
        {'label': u'Messages', 'action': 'manage_messages',
         'help': ('Localizer', 'MC_messages.stx')},
        {'label': u'Properties', 'action': 'manage_propertiesForm'},
        {'label': u'Import', 'action': 'manage_Import_form',
         'help': ('Localizer', 'MC_importExport.stx')},
        {'label': u'Export', 'action': 'manage_Export_form',
         'help': ('Localizer', 'MC_importExport.stx')}) \
        + LanguageManager.manage_options \
        + SimpleItem.manage_options


    #######################################################################
    # Management screens -- Messages
    #######################################################################
    security.declareProtected('Manage messages', 'manage_messages')
    manage_messages = LocalDTMLFile('ui/MC_messages', globals())


    security.declarePublic('get_namespace')
    def get_namespace(self, REQUEST):
        """For the management interface, allows to filter the messages to
        show.
        """
        # Check whether there are languages or not
        languages = self.get_languages_mapping()
        if not languages:
            return {}

        # Input
        batch_start = REQUEST.get('batch_start', 0)
        batch_size = REQUEST.get('batch_size', 15)
        empty = REQUEST.get('empty', 0)
        regex = REQUEST.get('regex', '')
        message = REQUEST.get('msg', None)

        # Build the namespace
        namespace = {}
        namespace['batch_size'] = batch_size
        namespace['empty'] = empty
        namespace['regex'] = regex

        # The language
        lang = REQUEST.get('lang', None) or languages[0]['code']
        namespace['language'] = lang

        # Filter the messages
        query = regex.strip()
        try:
            query = compile(query)
        except:
            query = compile('')

        messages = []
        for m, t in self._messages.items():
            if query.search(m) and (not empty or not t.get(lang, '').strip()):
                messages.append(m)
        messages.sort(filter_sort)
        # How many messages
        n = len(messages)
        namespace['n_messages'] = n

        # Calculate the start
        while batch_start >= n:
            batch_start = batch_start - batch_size
        if batch_start < 0:
            batch_start = 0
        namespace['batch_start'] = batch_start
        # Select the batch to show
        batch_end = batch_start + batch_size
        messages = messages[batch_start:batch_end]
        # Batch links
        namespace['previous'] = get_url(REQUEST.URL, batch_start - batch_size,
            batch_size, regex, lang, empty)
        namespace['next'] = get_url(REQUEST.URL, batch_start + batch_size,
            batch_size, regex, lang, empty)

        # Get the message
        message_encoded = None
        translations = {}
        if message is None:
            if messages:
                message = messages[0]
                translations = self.get_translations(message)
                message = to_unicode(message)
                message_encoded = message_encode(message)
        else:
            message_encoded = message
            message = message_decode(message_encoded)
            translations = self.get_translations(message)
            message = to_unicode(message)
        namespace['message'] = message
        namespace['message_encoded'] = message_encoded
        namespace['translations'] = translations
        namespace['translation'] = translations.get(lang, '')
        namespace['note'] = translations.get('note', '')

        # Calculate the current message
        namespace['messages'] = []
        for x in messages:
            x = to_unicode(x)
            x_encoded = message_encode(x)
            url = get_url(
                REQUEST.URL, batch_start, batch_size, regex, lang, empty,
                msg=x_encoded)
            namespace['messages'].append({
                'message': x,
                'message_encoded': x_encoded,
                'current': x == message,
                'url': url})

        # The languages
        for language in languages:
            code = language['code']
            language['name'] = _(language['name'], language=code)
            language['url'] = get_url(REQUEST.URL, batch_start, batch_size,
                regex, code, empty, msg=message_encoded)
        namespace['languages'] = languages

        return namespace


    security.declareProtected('Manage messages', 'manage_editMessage')
    def manage_editMessage(self, message, language, translation, note,
                           REQUEST, RESPONSE):
        """Modifies a message.
        """
        message_encoded = message
        message = message_decode(message_encoded)
        message_key = self.get_message_key(message)
        self.message_edit(message_key, language, translation, note)

        url = get_url(REQUEST.URL1 + '/manage_messages',
                      REQUEST['batch_start'], REQUEST['batch_size'],
                      REQUEST['regex'], REQUEST.get('lang', ''),
                      REQUEST.get('empty', 0),
                      msg=message_encoded,
                      manage_tabs_message=_(u'Saved changes.'))
        RESPONSE.redirect(url)


    security.declareProtected('Manage messages', 'manage_delMessage')
    def manage_delMessage(self, message, REQUEST, RESPONSE):
        """ """
        message = message_decode(message)
        message_key = self.get_message_key(message)
        self.message_del(message_key)

        url = get_url(REQUEST.URL1 + '/manage_messages',
                      REQUEST['batch_start'], REQUEST['batch_size'],
                      REQUEST['regex'], REQUEST.get('lang', ''),
                      REQUEST.get('empty', 0),
                      manage_tabs_message=_(u'Saved changes.'))
        RESPONSE.redirect(url)


    #######################################################################
    # Management screens -- Properties
    # Management screens -- Import/Export
    # FTP access
    #######################################################################
    security.declareProtected('View management screens',
                              'manage_propertiesForm')
    manage_propertiesForm = LocalDTMLFile('ui/MC_properties', globals())


    security.declareProtected('View management screens', 'manage_properties')
    def manage_properties(self, title, REQUEST=None, RESPONSE=None):
        """Change the Message Catalog properties.
        """
        self.title = title

        if RESPONSE is not None:
            RESPONSE.redirect('manage_propertiesForm')


    # Properties management screen
    security.declareProtected('View management screens', 'get_po_header')
    def get_po_header(self, lang):
        """ """
        # For backwards compatibility
        if not hasattr(aq_base(self), '_po_headers'):
            self._po_headers = PersistentMapping()

        return self._po_headers.get(lang, empty_po_header)


    security.declareProtected('View management screens', 'update_po_header')
    def update_po_header(self, lang,
                         last_translator_name=None,
                         last_translator_email=None,
                         language_team=None,
                         charset=None,
                         REQUEST=None, RESPONSE=None):
        """ """
        header = self.get_po_header(lang)

        if last_translator_name is None:
            last_translator_name = header['last_translator_name']

        if last_translator_email is None:
            last_translator_email = header['last_translator_email']

        if language_team is None:
            language_team = header['language_team']

        if charset is None:
            charset = header['charset']

        header = {'last_translator_name': last_translator_name,
                  'last_translator_email': last_translator_email,
                  'language_team': language_team,
                  'charset': charset}

        self._po_headers[lang] = header

        if RESPONSE is not None:
            RESPONSE.redirect('manage_propertiesForm')



    security.declareProtected('View management screens', 'manage_Import_form')
    manage_Import_form = LocalDTMLFile('ui/MC_Import_form', globals())


    security.declarePublic('get_charsets')
    def get_charsets(self):
        """ """
        return charsets[:]


    security.declarePublic('manage_export')
    def manage_export(self, x, REQUEST=None, RESPONSE=None):
        """Exports the content of the message catalog either to a template
        file (locale.pot) or to an language specific PO file (<x>.po).
        """
        # Get the PO header info
        header = self.get_po_header(x)
        last_translator_name = header['last_translator_name']
        last_translator_email = header['last_translator_email']
        language_team = header['language_team']
        charset = header['charset']

        # PO file header, empty message.
        po_revision_date = strftime('%Y-%m-%d %H:%m+%Z', gmtime(time()))
        pot_creation_date = po_revision_date
        last_translator = '%s <%s>' % (last_translator_name,
                                       last_translator_email)

        if x == 'locale.pot':
            language_team = 'LANGUAGE <LL@li.org>'
        else:
            language_team = '%s <%s>' % (x, language_team)

        r = ['msgid ""',
             'msgstr "Project-Id-Version: %s\\n"' % self.title,
             '"POT-Creation-Date: %s\\n"' % pot_creation_date,
             '"PO-Revision-Date: %s\\n"' % po_revision_date,
             '"Last-Translator: %s\\n"' % last_translator,
             '"Language-Team: %s\\n"' % language_team,
             '"MIME-Version: 1.0\\n"',
             '"Content-Type: text/plain; charset=%s\\n"' % charset,
             '"Content-Transfer-Encoding: 8bit\\n"',
             '', '']


        # Get the messages, and perhaps its translations.
        d = {}
        if x == 'locale.pot':
            filename = x
            for k in self._messages.keys():
                d[k] = ""
        else:
            filename = '%s.po' % x
            for k, v in self._messages.items():
                try:
                    d[k] = v[x]
                except KeyError:
                    d[k] = ""

        # Generate the file
        def backslashescape(x):
            quote_esc = compile(r'"')
            x = quote_esc.sub('\\"', x)

            trans = [('\n', '\\n'), ('\r', '\\r'), ('\t', '\\t')]
            for a, b in trans:
                x = x.replace(a, b)

            return x

        # Generate sorted msgids to simplify diffs
        dkeys = d.keys()
        dkeys.sort()
        for k in dkeys:
            r.append('msgid "%s"' % backslashescape(k))
            v = d[k]
            r.append('msgstr "%s"' % backslashescape(v))
            r.append('')

        if RESPONSE is not None:
            RESPONSE.setHeader('Content-type','application/data')
            RESPONSE.setHeader('Content-Disposition',
                               'inline;filename=%s' % filename)

        r2 = []
        for x in r:
            if isinstance(x, unicode):
                r2.append(x.encode(charset))
            else:
                r2.append(x)

        return '\n'.join(r2)


    security.declareProtected('Manage messages', 'po_import')
    def po_import(self, lang, data):
        """ """
        messages = self._messages

        # Load the data
        po = itools.gettext.POFile(string=data)
        for msgid in po.get_msgids():
            # TODO Keep the context if any
            _context, msgid = msgid
            if msgid:
                msgstr = po.get_msgstr(msgid) or ''
                if not messages.has_key(msgid):
                    messages[msgid] = PersistentMapping()
                messages[msgid][lang] = msgstr

        # Set the encoding (the full header should be loaded XXX)
        self.update_po_header(lang, charset=po.get_encoding())


    security.declareProtected('Manage messages', 'manage_import')
    def manage_import(self, lang, file, REQUEST=None, RESPONSE=None):
        """ """
        # XXX For backwards compatibility only, use "po_import" instead.
        if isinstance(file, str):
            content = file
        else:
            content = file.read()

        self.po_import(lang, content)

        if RESPONSE is not None:
            RESPONSE.redirect('manage_messages')


    def objectItems(self, spec=None):
        """ """
        for lang in self._languages:
            if not hasattr(aq_base(self), lang):
                self._setObject(lang, POFile(lang))

        r = MessageCatalog.inheritedAttribute('objectItems')(self, spec)
        return r


    #######################################################################
    # TMX support
    security.declareProtected('View management screens', 'manage_Export_form')
    manage_Export_form = LocalDTMLFile('ui/MC_Export_form', globals())


    security.declareProtected('Manage messages', 'tmx_export')
    def tmx_export(self, REQUEST, RESPONSE=None):
        """Exports the content of the message catalog to a TMX file
        """
        src_lang = self._default_language

        # Get the header info
        header = self.get_po_header(src_lang)
        charset = header['charset']

        # Init the TMX handler
        tmx = TMXFile()
        tmx.header['creationtool'] = u'Localizer'
        tmx.header['creationtoolversion'] = u'1.x'
        tmx.header['datatype'] = u'plaintext'
        tmx.header['segtype'] = u'paragraph'
        tmx.header['adminlang'] = src_lang
        tmx.header['srclang'] = src_lang
        tmx.header['o-encoding'] = u'%s' % charset.lower()

        # handle messages
        for msgkey, transunit in self._messages.items():
            unit = TMXUnit({})
            for lang in transunit.keys():
                if lang != 'note':
                    sentence = Sentence({'lang': lang})
                    sentence.text = transunit[lang]
                    unit.msgstr[lang] = sentence

            if src_lang not in transunit.keys():
                sentence = Sentence({'lang': src_lang})
                sentence.text = msgkey
                unit.msgstr[src_lang] = sentence

            if transunit.has_key('note'):
                note = TMXNote(transunit.get('note'))
                unit.notes.append(note)
            tmx.messages[msgkey] = unit

        if RESPONSE is not None:
            RESPONSE.setHeader('Content-type','application/data')
            RESPONSE.setHeader('Content-Disposition',
                               'attachment; filename="%s.tmx"' % self.id)

        return tmx.to_str()



    security.declareProtected('Manage messages', 'tmx_import')
    def tmx_import(self, howmuch, file, REQUEST=None, RESPONSE=None):
        """Imports a TMX level 1 file.
        """
        try:
            data = file.read()
            tmx = TMXFile(string=data)
        except:
            return MessageDialog(title = 'Parse error',
                                 message = _('impossible to parse the file') ,
                                 action = 'manage_Import_form',)

        num_notes = 0
        num_trans = 0

        if howmuch == 'clear':
            # Clear the message catalogue prior to import
            self._messages = {}
            self._languages = ()
            self._default_language = tmx.get_srclang()

        for id, msg in tmx.messages.items():
            if not self._messages.has_key(id) and howmuch == 'existing':
                continue
            msg.msgstr.pop(self._default_language)
            if not self._messages.has_key(id):
                self._messages[id] = {}
            for lang in msg.msgstr.keys():
                # normalize the languageTag and extract the core
                (core, local) = LanguageTag.decode(lang)
                lang = LanguageTag.encode((core, local))
                if lang not in self._languages:
                    self._languages += (lang,)
                if msg.msgstr[lang].text:
                    self._messages[id][lang] = msg.msgstr[lang].text
                    if core != lang and core != self._default_language:
                        if core not in self._languages:
                            self._languages += (core,)
                        if not msg.msgstr.has_key(core):
                            self._messages[id][core] = msg.msgstr[lang].text
            if msg.notes:
                ns = [m.text for m in msg.notes]
                self._messages[id]['note'] = u' '.join(ns)
                num_notes += 1
            num_trans += 1

        if REQUEST is not None:
            message = _(u'Imported %d messages and %d notes')
            return MessageDialog(
                title = _(u'Messages imported'),
                message = message % (num_trans, num_notes),
                action = 'manage_messages')



    #######################################################################
    # Backwards compatibility (XXX)
    #######################################################################

    hasmsg = message_exists
    hasLS = message_exists  # CMFLocalizer uses it

    security.declareProtected('Manage messages', 'xliff_export')
    def xliff_export(self, dst_lang, export_all=1, REQUEST=None,
                     RESPONSE=None):
        """Exports the content of the message catalog to an XLIFF file
        """
        from DateTime import DateTime

        src_lang = self._default_language
        export_all = int(export_all)

        # Init the XLIFF handler
        xliff = XLFFile()
        # Add the translation units
        original = '/%s' % self.absolute_url(1)
        for msgkey, transunit in self._messages.items():
            target = transunit.get(dst_lang, '')
            # If 'export_all' is true export all messages, otherwise export
            # only untranslated messages
            if export_all or not target:
                unit = xliff.add_unit(original, msgkey, None)
                unit.attributes['id'] = md5text(msgkey)
                if target:
                    unit.target = target
                # Add note
                note = transunit.get('note')
                if note:
                    unit.notes.append(XLFNote(note))

        # build the data-stucture for the File tag
        file = xliff.files[original]
        attributes = file.attributes
        attributes['original'] = original
        attributes['product-name'] = u'Localizer'
        attributes['product-version'] = u'1.1.x'
        attributes['data-type'] = u'plaintext'
        attributes['source-language'] = src_lang
        attributes['target-language'] = dst_lang
        attributes['date'] = DateTime().HTML4()

        # Serialize
        xliff = xliff.to_str()
        # Set response headers
        RESPONSE.setHeader('Content-Type', 'text/xml; charset=UTF-8')
        filename = '%s_%s_%s.xlf' % (self.id, src_lang, dst_lang)
        RESPONSE.setHeader('Content-Disposition',
           'attachment; filename="%s"' % filename)
        # Ok
        return xliff


    security.declareProtected('Manage messages', 'xliff_import')
    def xliff_import(self, howmuch, file, REQUEST=None):
        """XLIFF is the XML Localization Interchange File Format designed by a
        group of software providers.  It is specified by www.oasis-open.org
        """
        try:
            data = file.read()
            xliff = XLFFile(string=data)
        except:
            return MessageDialog(title = 'Parse error',
                                 message = _('impossible to parse the file') ,
                                 action = 'manage_Import_form',)

        num_notes = 0
        num_trans = 0
        (file_ids, sources, targets) = xliff.get_languages()

        if howmuch == 'clear':
            # Clear the message catalogue prior to import
            self._messages = {}
            self._languages = ()
            self._default_language = sources[0]

        # update languages
        if len(sources) > 1 or sources[0] != self._default_language:
            return MessageDialog(title = 'Language error',
                                 message = _('incompatible language sources') ,
                                 action = 'manage_Import_form',)
        for lang in targets:
            if lang != self._default_language and lang not in self._languages:
                self._languages += (lang,)

        # get messages
        for file in xliff.files:
            cur_target = file.attributes.get('target-language', '')
            for msg in file.body.keys():
                if not self._messages.has_key(msg) and howmuch == 'existing':
                    pass
                else:
                    if not self._messages.has_key(msg):
                        self._messages[msg] = {}

                    if cur_target and file.body[msg].target:
                        self._messages[msg][cur_target] = file.body[msg].target
                        num_trans += 1
                    if file.body[msg].notes:
                        ns = [n.text for n in file.body[msg].notes]
                        comment = ' '.join(ns)
                        self._messages[msg]['note'] = comment
                        num_notes += 1

        if REQUEST is not None:
            return MessageDialog(
                title = _(u'Messages imported'),
                message = (_(u'Imported %d messages and %d notes to %s') % \
                           (num_trans, num_notes, ' '.join(targets))),
                action = 'manage_messages')



class POFile(SimpleItem):
    """ """

    security = ClassSecurityInfo()


    def __init__(self, id):
        self.id = id


    security.declareProtected('FTP access', 'manage_FTPget')
    def manage_FTPget(self):
        """ """
        return self.manage_export(self.id)


    security.declareProtected('Manage messages', 'PUT')
    def PUT(self, REQUEST, RESPONSE):
        """ """
        body = REQUEST['BODY']
        self.po_import(self.id, body)
        RESPONSE.setStatus(204)
        return RESPONSE

InitializeClass(MessageCatalog)
InitializeClass(POFile)



def MessageCatalog_moved(object, event):
    # FIXME This does not work if what we move is the folder that contains
    # the message catalog
    container = event.oldParent
    if container is not None:
        sm = getSiteManager(container)
        sm.unregisterUtility(object, ITranslationDomain, event.oldName)

    container = event.newParent
    if container is not None:
        sm = getSiteManager(container)
        sm.registerUtility(object, ITranslationDomain, event.newName)

